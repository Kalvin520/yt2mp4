import os
import urllib.parse
from fastapi import FastAPI, HTTPException
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


# ==========================================
# API 1: 解析 YouTube 網址，回傳畫質菜單
# ==========================================
@app.post("/api/info")
async def get_video_info(request: InfoRequest):
    try:
        ydl_opts = {
            'skip_download': True,
            'noplaylist': True,  # 告訴 yt-dlp 只抓單一影片
            'extract_flat': 'in_playlist'  # 如果遇到清單，不要去解析內容
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 這裡會去抓取網址的資訊
            info = ydl.extract_info(request.url, download=False)

        # 【核心防護層】如果抓出來的資訊是一個清單，馬上阻擋！
        if info.get('_type') == 'playlist':
            raise ValueError("伺服器不支援下載整個播放清單，請提供單一影片的網址喔！")

        # 1. 抓出最好的聲音大小，等一下算總容量會用到
        audio_formats = [f for f in info.get('formats', []) if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
        best_audio = audio_formats[-1] if audio_formats else None
        audio_size = best_audio.get('filesize') or best_audio.get('filesize_approx') or 0 if best_audio else 0
        audio_id = best_audio['format_id'] if best_audio else 'bestaudio'

        # 2. 篩選出我們想要的影片畫質
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

                # 如果這個高畫質影像沒有聲音，我們要把聲音綁上去
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
        # 如果發生任何錯誤（包含我們上面自己丟出來的 ValueError），都會回傳給前端
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# API 2: 正式下載影片或 MP3
# ==========================================
@app.post("/api/download")
async def download_video(request: DownloadRequest):
    try:
        if request.type == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'noplaylist': True,  # 防護層
                'extract_flat': 'in_playlist',  # 防護層
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            target_ext = ".mp3"
            media_type = "audio/mpeg"

        else:
            ydl_opts = {
                'format': request.format_id,
                'merge_output_format': 'mp4',
                'outtmpl': '%(title)s.%(ext)s',
                'noplaylist': True,  # 防護層
                'extract_flat': 'in_playlist'  # 防護層
            }
            target_ext = ".mp4"
            media_type = "video/mp4"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 確保不會在下載時偷渡播放清單
            info = ydl.extract_info(request.url, download=True)

            if info.get('_type') == 'playlist':
                raise ValueError("伺服器不支援下載整個播放清單，請提供單一影片的網址喔！")

            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + target_ext

        encoded_filename = urllib.parse.quote(os.path.basename(filename))
        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }

        return FileResponse(path=filename, media_type=media_type, headers=headers)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))