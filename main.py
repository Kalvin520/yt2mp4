import os
import urllib.parse
import glob  # 👇 記得要引入 glob 來大範圍掃蕩垃圾
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
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

# 定義接收的資料格式
class InfoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    format_id: str
    type: str = "video"

# ==========================================
# 🛠️ 刪除檔案小幫手 (大範圍掃蕩防爆版)
# ==========================================
def cleanup_file(path: str):
    try:
        base_name = os.path.splitext(path)[0]
        # 找出資料夾裡所有同檔名、不同副檔名的垃圾 (例如 .webm, .m4a, .temp.mp4)
        pattern = f"{glob.escape(base_name)}.*"
        temp_files = glob.glob(pattern)

        for temp_file in temp_files:
            os.remove(temp_file)
            print(f"🗑️ 已成功掃除暫存檔：{temp_file}")
    except Exception as e:
        print(f"⚠️ 刪除暫存檔失敗：{e}")

# 洗網址專用小工具
def clean_youtube_url(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    if 'v' in query_params:
        video_id = query_params['v'][0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

# ==========================================
# API 1: 解析 YouTube 網址 (Mac 智慧優化版)
# ==========================================
@app.post("/api/info")
async def get_video_info(request: InfoRequest):
    try:
        clean_url = clean_youtube_url(request.url)

        ydl_opts = {
            'skip_download': True,
            'noplaylist': True,
            'extract_flat': 'in_playlist'
        }

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

        return {
            "title": info.get('title', '未知影片'),
            "options": sorted(options, key=lambda x: int(x['resolution'].replace('p', '').replace('4K', '2160')), reverse=True)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==========================================
# API 2: 正式下載影片或 MP3 (雙軌智慧切換版)
# ==========================================
@app.post("/api/download")
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks):
    try:
        clean_url = clean_youtube_url(request.url)

        if request.type == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'noplaylist': True,
                'extract_flat': 'in_playlist',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            target_ext = ".mp3"
            media_type = "audio/mpeg"

        else:
            # 🌟 步驟一：先快速偷看這支影片的資訊，判斷畫質有多高
            target_height = 0
            with yt_dlp.YoutubeDL({'noplaylist': True, 'quiet': True}) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                video_format_id = request.format_id.split('+')[0]
                for f in info.get('formats', []):
                    if f.get('format_id') == video_format_id:
                        target_height = f.get('height', 0)
                        break

            # 🌟 步驟二：準備基礎下載設定
            ydl_opts = {
                'format': f"{request.format_id}",
                'merge_output_format': 'mp4',
                'outtmpl': '%(title)s.%(ext)s',
                'noplaylist': True,
                'keepvideo': False,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]
            }

            # 🌟 步驟三：雙軌智慧判斷！
            if target_height > 1080:
                print(f"🚀 偵測到 {target_height}p 超高畫質！啟動 H.264 強制轉檔模式 (需較長時間以相容 Mac)...")
                ydl_opts['postprocessor_args'] = [
                    '-vcodec', 'libx264',
                    '-preset', 'fast'
                ]
            else:
                print(f"⚡ 偵測到 {target_height}p (含)以下畫質！啟動極速合併模式...")

            target_ext = ".mp4"
            media_type = "video/mp4"

        # 執行正式下載
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            if info.get('_type') == 'playlist':
                raise ValueError("伺服器不支援下載整個播放清單，請提供單一影片的網址喔！")

            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + target_ext

        encoded_filename = urllib.parse.quote(os.path.basename(filename))
        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }

        # 傳送給前端後，交給 BackgroundTasks 做大範圍垃圾掃除
        background_tasks.add_task(cleanup_file, filename)

        return FileResponse(path=filename, media_type=media_type, headers=headers)

    except Exception as e:
        print(f"合併或下載發生錯誤: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))