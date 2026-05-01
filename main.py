from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

# 允許前端 (React) 跨網域來呼叫我們
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 測試時允許所有人，上線時可改成前端網址
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定義前端傳過來的資料格式（只需要一個網址）
class VideoRequest(BaseModel):
    url: str


# 建立一個下載的接收站 API
@app.post("/api/download")
def download_video(request: VideoRequest):
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': '%(title)s.%(ext)s',  # 預設會下載到後端的資料夾
            'noplaylist': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([request.url])

        return {"status": "success", "message": "影片下載成功！"}
    except Exception as e:
        # 如果失敗，回傳錯誤訊息給前端
        raise HTTPException(status_code=400, detail=str(e))