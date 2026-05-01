# 1. 向雲端租借一台已經安裝好 Python 3.9 的輕量級 Linux 電腦 (廚房)
FROM python:3.14-slim

# 2. 這是最重要的一步！命令這台電腦下載並安裝 FFmpeg (轉檔神器)
# apt-get 是 Linux 的應用程式商店，我們先更新商店清單，然後下載 ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. 在電腦裡建立一個叫做 /app 的專屬工作資料夾，並走進去
WORKDIR /app

# 4. 將我們剛剛寫好的「食材採購清單 (requirements.txt)」複製到這台電腦裡
COPY requirements.txt .

# 5. 命令電腦看著清單，用 pip 把 FastAPI、yt-dlp 這些套件安裝起來
RUN pip install --no-cache-dir -r requirements.txt

# 6. 把我們寫的後端主程式 (main.py) 複製到這台電腦的工作資料夾裡
COPY . .

# 7. 告訴雲端伺服器：「當這台電腦開機時，請執行這行指令來啟動網站！」
# uvicorn 是啟動 FastAPI 的馬達，0.0.0.0 代表允許全世界連線，port 會由雲端平台自動分配
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

# 2. 這是最重要的一步！命令這台電腦下載並安裝 FFmpeg (轉檔神器)
# apt-get 是 Linux 的應用程式商店，我們先更新商店清單，然後下載 ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. 在電腦裡建立一個叫做 /app 的專屬工作資料夾，並走進去
WORKDIR /app

# 4. 將我們剛剛寫好的「食材採購清單 (requirements.txt)」複製到這台電腦裡
COPY requirements.txt .

# 5. 命令電腦看著清單，用 pip 把 FastAPI、yt-dlp 這些套件安裝起來
RUN pip install --no-cache-dir -r requirements.txt

# 6. 把我們寫的後端主程式 (main.py) 複製到這台電腦的工作資料夾裡
COPY . .

# 7. 告訴雲端伺服器：「當這台電腦開機時，請執行這行指令來啟動網站！」
# uvicorn 是啟動 FastAPI 的馬達，0.0.0.0 代表允許全世界連線，port 會由雲端平台自動分配
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

# 2. 這是最重要的一步！命令這台電腦下載並安裝 FFmpeg (轉檔神器)
# apt-get 是 Linux 的應用程式商店，我們先更新商店清單，然後下載 ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. 在電腦裡建立一個叫做 /app 的專屬工作資料夾，並走進去
WORKDIR /app

# 4. 將我們剛剛寫好的「食材採購清單 (requirements.txt)」複製到這台電腦裡
COPY requirements.txt .

# 5. 命令電腦看著清單，用 pip 把 FastAPI、yt-dlp 這些套件安裝起來
RUN pip install --no-cache-dir -r requirements.txt

# 6. 把我們寫的後端主程式 (main.py) 複製到這台電腦的工作資料夾裡
COPY . .

# 7. 告訴雲端伺服器：「當這台電腦開機時，請執行這行指令來啟動網站！」
# uvicorn 是啟動 FastAPI 的馬達，0.0.0.0 代表允許全世界連線，port 會由雲端平台自動分配
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

# 2. 這是最重要的一步！命令這台電腦下載並安裝 FFmpeg (轉檔神器)
# apt-get 是 Linux 的應用程式商店，我們先更新商店清單，然後下載 ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. 在電腦裡建立一個叫做 /app 的專屬工作資料夾，並走進去
WORKDIR /app

# 4. 將我們剛剛寫好的「食材採購清單 (requirements.txt)」複製到這台電腦裡
COPY requirements.txt .

# 5. 命令電腦看著清單，用 pip 把 FastAPI、yt-dlp 這些套件安裝起來
RUN pip install --no-cache-dir -r requirements.txt

# 6. 把我們寫的後端主程式 (main.py) 複製到這台電腦的工作資料夾裡
COPY . .

# 7. 告訴雲端伺服器：「當這台電腦開機時，請執行這行指令來啟動網站！」
# uvicorn 是啟動 FastAPI 的馬達，0.0.0.0 代表允許全世界連線，port 會由雲端平台自動分配
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]