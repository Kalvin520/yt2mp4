import os
import sys
import shutil
import urllib.parse
import glob
import uuid
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

# 允許前端網頁來呼叫我們的後端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🌟 進度追蹤系統
# ==========================================
# 使用一個簡單的字典來儲存每個下載任務的進度
progress_data = {}

class ProgressHook:
    def __init__(self, task_id):
        self.task_id = task_id
        progress_data[self.task_id] = {"status": "downloading", "progress": 0, "message": "準備開始下載..."}

    def __call__(self, d):
        if d['status'] == 'downloading':
            # 提取下載進度
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes')
            if total_bytes and downloaded_bytes:
                progress = (downloaded_bytes / total_bytes) * 100
                # 我們將下載階段的進度限制在 0-80% 之間
                progress_data[self.task_id]["progress"] = progress * 0.8 
                progress_data[self.task_id]["message"] = f"下載中... {int(progress)}%"

        elif d['status'] == 'finished':
            # 下載完成，進入轉檔/合併階段
            progress_data[self.task_id]["progress"] = 80
            progress_data[self.task_id]["message"] = "下載完成，準備進行最終處理..."

        elif d['status'] == 'error':
            progress_data[self.task_id]["status"] = "error"
            progress_data[self.task_id]["message"] = "下載過程中發生錯誤"

def ffmpeg_progress_hook(task_id):
    """一個假的 ffmpeg 進度更新器，讓進度條在轉檔時也能慢慢動"""
    if task_id in progress_data and progress_data[task_id].get("status") != "completed":
        current_progress = progress_data[task_id].get("progress", 80)
        if current_progress < 99:
            # 轉檔階段的進度在 80-99% 之間緩慢移動
            progress_data[task_id]["progress"] = min(current_progress + 0.1, 99)
            progress_data[task_id]["message"] = "影片轉檔中，這可能需要幾分鐘..."


# 定義接收的資料格式
class InfoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    format_id: str
    type: str = "video"
    resolution: str = ""

class ProgressRequest(BaseModel):
    task_id: str

# ==========================================
# 🛠️ 刪除檔案小幫手
# ==========================================
def cleanup_file(path: str):
    try:
        base_name = os.path.splitext(path)[0]
        pattern = f"{glob.escape(base_name)}.*"
        temp_files = glob.glob(pattern)
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"🗑️ 已成功掃除暫存檔：{temp_file}")
    except Exception as e:
        print(f"⚠️ 刪除暫存檔失敗：{e}")

def clean_youtube_url(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    if 'v' in query_params:
        video_id = query_params['v'][0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

# ==========================================
# API 1: 解析 YouTube 網址 
# ==========================================
@app.post("/api/info")
async def get_video_info(request: InfoRequest):
    try:
        clean_url = clean_youtube_url(request.url)
        ydl_opts = {'skip_download': True, 'noplaylist': True, 'extract_flat': 'in_playlist'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
        if info.get('_type') == 'playlist':
            raise ValueError("伺服器不支援下載整個播放清單，請提供單一影片的網址喔！")
        audio_formats = [f for f in info.get('formats', []) if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
        best_audio = audio_formats[-1] if audio_formats else None
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
        raise HTTPException(status_code=400, detail=str(e))

# ==========================================
# API 2: 啟動下載任務 (非同步)
# ==========================================
@app.post("/api/download")
async def start_download_task(request: DownloadRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    # 將下載任務丟到背景執行
    background_tasks.add_task(run_download, request, task_id)
    return {"success": True, "task_id": task_id}

def run_download(request: DownloadRequest, task_id: str):
    """真正的下載函式，會在背景執行緒中被呼叫"""
    try:
        clean_url = clean_youtube_url(request.url)
        progress_hook = ProgressHook(task_id)

        ydl_opts = {
            'format': request.format_id,
            'merge_output_format': 'mp4',
            'outtmpl': f'{task_id}_%(title)s.%(ext)s', # 檔名加入 task_id 避免衝突
            'noplaylist': True,
            'keepvideo': False,
            'progress_hooks': [progress_hook],
            'postprocessor_hooks': [lambda d: progress_hook(d) if d['status'] == 'finished' else None],
        }

        if request.type == "audio":
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
            target_ext = ".mp3"
        else:
            ydl_opts['postprocessors'] = [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
            if "1440" in request.resolution or "4K" in request.resolution or "2160" in request.resolution:
                print(f"🚀 偵測到 {request.resolution} 超高畫質！啟動 H.264 強制轉檔模式...")
                ydl_opts['postprocessor_args'] = ['-vcodec', 'libx264', '-preset', 'fast', '-crf', '23']
                # 如果是高畫質轉檔，我們需要一個假的進度更新器
                ydl_opts['postprocessor_hooks'].append(lambda d: ffmpeg_progress_hook(task_id))
            target_ext = ".mp4"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + target_ext

        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        os.makedirs(downloads_dir, exist_ok=True)
        
        # 把檔名中的 task_id 去掉
        final_filename = os.path.basename(filename).replace(f'{task_id}_', '')
        final_path = os.path.join(downloads_dir, final_filename)
        
        counter = 1
        base_name, ext = os.path.splitext(final_filename)
        while os.path.exists(final_path):
            final_path = os.path.join(downloads_dir, f"{base_name} ({counter}){ext}")
            counter += 1
            
        shutil.move(filename, final_path)
        print(f"✅ 檔案已成功搬移至: {final_path}")
        
        progress_data[task_id] = {"status": "completed", "progress": 100, "message": "下載完成！"}
        cleanup_file(filename)

    except Exception as e:
        print(f"下載任務 {task_id} 失敗: {str(e)}")
        progress_data[task_id] = {"status": "error", "message": str(e)}

# ==========================================
# API 3: 查詢進度
# ==========================================
@app.post("/api/progress")
async def get_progress(request: ProgressRequest):
    progress = progress_data.get(request.task_id, {"status": "not_found", "message": "找不到任務"})
    return JSONResponse(content=progress)

# ==========================================
# 靜態檔案路由 
# ==========================================
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