import os
import sys
import platform
import urllib.parse
import re
import threading
import time
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yt_dlp

TASK_TTL_SECONDS = 60 * 30
progress_lock = threading.Lock()
progress_data = {}

def safe_print(message: str):
    try:
        print(message)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(message.encode(encoding, errors="replace").decode(encoding, errors="replace"))

def get_ffmpeg_path():
    bundled_dir = getattr(sys, '_MEIPASS', None)
    if getattr(sys, 'frozen', False):
        return bundled_dir

    ffmpeg_from_env = os.environ.get("FFMPEG_PATH")
    if ffmpeg_from_env:
        return ffmpeg_from_env

    system_name = platform.system()
    if system_name == "Darwin":
        for candidate in ("/opt/homebrew/bin", "/usr/local/bin"):
            if os.path.exists(os.path.join(candidate, "ffmpeg")):
                return candidate

    return None

def get_downloads_dir():
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    return downloads_dir

def sanitize_filename(filename: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    sanitized = sanitized.rstrip(' .')
    return sanitized[:180] or "download"

def set_progress(task_id: str, **updates):
    with progress_lock:
        current = progress_data.setdefault(task_id, {})
        current.update(updates)
        current["updated_at"] = time.time()

def get_task_progress(task_id: str):
    with progress_lock:
        progress = progress_data.get(task_id)
        if not progress:
            return None
        return {key: value for key, value in progress.items() if key != "updated_at"}

def cleanup_old_tasks():
    cutoff = time.time() - TASK_TTL_SECONDS
    with progress_lock:
        expired_ids = [
            task_id
            for task_id, progress in progress_data.items()
            if progress.get("updated_at", 0) < cutoff
        ]
        for task_id in expired_ids:
            progress_data.pop(task_id, None)

def parse_resolution_height(resolution: str) -> int:
    if resolution == "4K":
        return 2160
    match = re.search(r"(\d+)", resolution)
    return int(match.group(1)) if match else 0

def get_h264_transcode_args(resolution: str) -> list[str]:
    height = parse_resolution_height(resolution)
    if platform.system() == "Darwin":
        bitrate = "24000k" if height >= 2160 else "12000k"
        return [
            "-c:v", "h264_videotoolbox",
            "-b:v", bitrate,
            "-allow_sw", "1",
            "-c:a", "aac",
            "-b:a", "192k",
        ]

    return ["-vcodec", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "192k"]

def get_aac_audio_args() -> list[str]:
    return ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k"]

def is_aac_compatible_audio(audio_format: dict) -> bool:
    ext = (audio_format.get("ext") or "").lower()
    acodec = (audio_format.get("acodec") or "").lower()
    return ext in {"m4a", "mp4"} or acodec.startswith(("mp4a", "aac"))

def audio_quality_score(audio_format: dict) -> tuple[float, int]:
    bitrate = audio_format.get("abr") or audio_format.get("tbr") or 0
    filesize = audio_format.get("filesize") or audio_format.get("filesize_approx") or 0
    return float(bitrate or 0), int(filesize or 0)

def select_best_audio_format(audio_formats: list[dict]):
    if not audio_formats:
        return None

    compatible_formats = [f for f in audio_formats if is_aac_compatible_audio(f)]
    candidates = compatible_formats or audio_formats
    return max(candidates, key=audio_quality_score)

def friendly_error_message(error: Exception) -> str:
    message = str(error)
    lowered = message.lower()

    if "ffmpeg" in lowered or "ffprobe" in lowered:
        return "找不到 FFmpeg，請確認已安裝 FFmpeg，或使用打包版內建的 ffmpeg.exe。"
    if "permission denied" in lowered or "access is denied" in lowered:
        return "沒有權限寫入下載資料夾，請確認 Downloads 資料夾可寫入，或關閉可能佔用檔案的程式。"
    if "no such file" in lowered or "cannot find the file" in lowered or "系統找不到指定的檔案" in message:
        return "找不到下載後的暫存檔，可能是防毒軟體、權限或檔名限制造成，請再試一次。"
    if "file exists" in lowered or "being used by another process" in lowered:
        return "目標檔案可能正在被其他程式使用，請關閉播放器或檔案總管預覽後再試。"
    if "unsupported url" in lowered:
        return "不支援這個網址，請貼上單一 YouTube 影片網址。"
    if "playlist" in lowered or "播放清單" in message:
        return "目前不支援下載整個播放清單，請貼上單一影片網址。"
    if "sign in" in lowered or "login" in lowered:
        return "這部影片需要登入或受到限制，目前無法直接下載。"
    if "http error" in lowered or "unable to download" in lowered or "network" in lowered:
        return "連線到 YouTube 時發生問題，請確認網路連線後再試。"

    return message or "發生未知錯誤，請稍後再試。"

FFMPEG_PATH = get_ffmpeg_path()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProgressHook:
    def __init__(self, task_id):
        self.task_id = task_id
        set_progress(self.task_id, status="downloading", progress=0, message="準備開始下載...")

    def __call__(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes')
            if total_bytes and downloaded_bytes:
                progress = (downloaded_bytes / total_bytes) * 100
                set_progress(self.task_id, progress=progress * 0.8, message=f"下載中... {int(progress)}%")
        elif d['status'] == 'finished':
            set_progress(self.task_id, progress=80, message="下載完成，準備進行最終處理...")
        elif d['status'] == 'error':
            set_progress(self.task_id, status="error", message="下載過程中發生錯誤")

def ffmpeg_progress_hook(task_id):
    progress = get_task_progress(task_id)
    if progress and progress.get("status") != "completed":
        current_progress = progress.get("progress", 80)
        if current_progress < 99:
            set_progress(task_id, progress=min(current_progress + 0.1, 99), message="影片轉檔中，這可能需要幾分鐘...")

class InfoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    format_id: str
    type: str = "video"
    resolution: str = ""

class ProgressRequest(BaseModel):
    task_id: str

def clean_youtube_url(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    if 'v' in query_params:
        video_id = query_params['v'][0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

@app.post("/api/info")
async def get_video_info(request: InfoRequest):
    try:
        clean_url = clean_youtube_url(request.url)
        ydl_opts = {'skip_download': True, 'noplaylist': True, 'extract_flat': 'in_playlist'}
        if FFMPEG_PATH:
            ydl_opts['ffmpeg_location'] = FFMPEG_PATH
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
        if info.get('_type') == 'playlist':
            raise ValueError("伺服器不支援下載整個播放清單，請提供單一影片的網址喔！")
        audio_formats = [f for f in info.get('formats', []) if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
        best_audio = select_best_audio_format(audio_formats)
        audio_size = best_audio.get('filesize') or best_audio.get('filesize_approx') or 0 if best_audio else 0
        audio_id = best_audio['format_id'] if best_audio else 'bestaudio'
        target_resolutions = [480, 720, 1080, 1440, 2160]
        options_dict = {}
        for f in info.get('formats', []):
            height = f.get('height')
            vcodec = f.get('vcodec', '')
            if vcodec != 'none' and height in target_resolutions:
                is_mac_friendly = 'avc1' in vcodec or 'h264' in vcodec
                if height not in options_dict:
                    options_dict[height] = f
                else:
                    current_f = options_dict[height]
                    current_is_mac = 'avc1' in current_f.get('vcodec', '')
                    if is_mac_friendly and not current_is_mac:
                        options_dict[height] = f
                    elif is_mac_friendly == current_is_mac:
                        options_dict[height] = f
        options = []
        for height, f in options_dict.items():
            video_size = f.get('filesize') or f.get('filesize_approx') or 0
            total_size = video_size
            format_id = f['format_id']
            if f.get('acodec') == 'none':
                total_size += audio_size
                format_id = f"{f['format_id']}+{audio_id}"
            size_mb = total_size / (1024 * 1024)
            options.append({
                "resolution": f"{height}p" if height != 2160 else "4K",
                "format_id": format_id,
                "size_mb": round(size_mb, 1) if size_mb > 0 else "未知"
            })
        return {"title": info.get('title', '未知影片'), "options": sorted(options, key=lambda x: int(x['resolution'].replace('p', '').replace('4K', '2160')), reverse=True)}
    except Exception as e:
        safe_print(f"解析影片失敗: {str(e)}")
        raise HTTPException(status_code=400, detail=friendly_error_message(e))

@app.post("/api/download")
async def start_download_task(request: DownloadRequest, background_tasks: BackgroundTasks):
    cleanup_old_tasks()
    task_id = str(uuid.uuid4())
    set_progress(task_id, status="queued", progress=0, message="等待下載任務啟動...")
    background_tasks.add_task(run_download, request, task_id)
    return {"success": True, "task_id": task_id}

def run_download(request: DownloadRequest, task_id: str):
    try:
        clean_url = clean_youtube_url(request.url)
        progress_hook = ProgressHook(task_id)

        downloads_dir = get_downloads_dir()

        ydl_opts = {
            'format': request.format_id,
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(downloads_dir, f'{task_id}_%(title).180B.%(ext)s'),
            'restrictfilenames': platform.system() == "Windows",
            'noplaylist': True,
            'keepvideo': False,
            'progress_hooks': [progress_hook],
        }
        if FFMPEG_PATH:
            ydl_opts['ffmpeg_location'] = FFMPEG_PATH

        if request.type == "audio":
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
            target_ext = ".mp3"
        else:
            ydl_opts['postprocessors'] = [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
            if "1440" in request.resolution or "4K" in request.resolution or "2160" in request.resolution:
                safe_print(f"偵測到 {request.resolution} 超高畫質，啟動 H.264 轉檔模式...")
                video_args = get_h264_transcode_args(request.resolution)
            else:
                video_args = get_aac_audio_args()
            ydl_opts['postprocessor_args'] = {'ffmpegvideoconvertor+ffmpeg_o': video_args}
            ydl_opts['postprocessor_hooks'] = [lambda d: ffmpeg_progress_hook(task_id)]
            target_ext = ".mp4"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + target_ext

        final_filename = sanitize_filename(os.path.basename(filename).replace(f'{task_id}_', ''))
        final_path = os.path.join(downloads_dir, final_filename)

        counter = 1
        base_name, ext = os.path.splitext(final_filename)
        while os.path.exists(final_path):
            final_path = os.path.join(downloads_dir, f"{base_name} ({counter}){ext}")
            counter += 1

        os.replace(filename, final_path)
        safe_print(f"檔案已儲存至: {final_path}")

        set_progress(task_id, status="completed", progress=100, message="下載完成！")

    except Exception as e:
        safe_print(f"下載任務 {task_id} 失敗: {str(e)}")
        set_progress(task_id, status="error", message=friendly_error_message(e))

@app.post("/api/progress")
async def get_progress(request: ProgressRequest):
    cleanup_old_tasks()
    progress = get_task_progress(request.task_id) or {"status": "not_found", "message": "找不到任務"}
    return JSONResponse(content=progress)

def get_frontend_dir():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "frontend", "dist")

frontend_path = get_frontend_dir()
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
else:
    @app.get("/")
    def read_root():
        return {"error": "找不到前端靜態檔案！", "solution": "請切換到 frontend 資料夾，並執行 'npm run build' 來產生 dist 資料夾。"}
