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


# 定義前端會傳什麼資料過來 (只要一個網址)
class VideoRequest(BaseModel):
    url: str


@app.post("/api/download")
async def download_video(request: VideoRequest):
    try:
        # 設定 yt-dlp 下載選項
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': '%(title)s.%(ext)s',  # 先暫存到後端資料夾
            'noplaylist': True
        }

        # 1. 開始下載影片
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            # 取得剛剛下載的完整檔名
            filename = ydl.prepare_filename(info)
            # 確保副檔名是 .mp4 (因為我們上面強制轉成 mp4 了)
            filename = os.path.splitext(filename)[0] + ".mp4"

        # 2. 處理中文檔名亂碼問題
        encoded_filename = urllib.parse.quote(os.path.basename(filename))

        # 3. 把檔案回傳給前端瀏覽器，並設定為「附件下載」模式
        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }

        return FileResponse(
            path=filename,
            media_type="video/mp4",
            headers=headers
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))