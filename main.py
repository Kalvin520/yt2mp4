import os
import urllib.parse
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
    type: str = "video"  # 區分是影片還是純音樂

# 刪除檔案的小幫手 (必須放在最外層獨立出來)
def cleanup_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"🗑️ 已成功刪除伺服器暫存檔：{path}")
    except Exception as e:
        print(f"⚠️ 刪除暫存檔失敗：{e}")

# 洗網址專用小工具，把 &list= 後面的東西全部切掉
def clean_youtube_url(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    # 如果網址裡有 'v' 參數 (代表單一影片 id)，我們只保留這個 'v'，丟掉其他東西 (包含 list)
    if 'v' in query_params:
        video_id = query_params['v'][0]
        return f"https://www.youtube.com/watch?v={video_id}"

    # 如果沒有 'v' 參數 (可能是 youtu.be 縮網址或其他形式)，就原封不動回傳
    return url

# ==========================================
# API 1: 解析 YouTube 網址，回傳畫質菜單
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
        options = []
        seen_resolutions = set()

        for f in reversed(info.get('formats', [])):
            height = f.get('height')
            vcodec = f.get('vcodec')

            if vcodec != 'none' and height in target_resolutions and height not in seen_resolutions:
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
                seen_resolutions.add(height)

        return {
            "title": info.get('title', '未知影片'),
            "options": sorted(options, key=lambda x: int(x['resolution'].replace('p', '').replace('4K', '2160')),
                              reverse=True)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# API 2: 正式下載影片或 MP3 (極速不轉檔版)
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
            # 極速魔法：拔除所有耗時的轉檔指令，只做最單純的「合併」
            ydl_opts = {
                'format': f"{request.format_id}",
                'merge_output_format': 'mp4',  # 只要求放進 mp4 容器，不改變內部編碼
                'outtmpl': '%(title)s.%(ext)s',
                'noplaylist': True,
                'extract_flat': 'in_playlist',
                'keepvideo': False
            }
            target_ext = ".mp4"
            media_type = "video/mp4"

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

        # 傳送檔案給前端後，在背景大掃除
        background_tasks.add_task(cleanup_file, filename)

        return FileResponse(path=filename, media_type=media_type, headers=headers)

    except Exception as e:
        print(f"合併或下載發生錯誤: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))