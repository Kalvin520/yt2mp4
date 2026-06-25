# 🎥 YT2MP4 Downloader

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=flat&logo=vite&logoColor=FFD62E)

一個現代化、美觀且高效的 YouTube 影片與音樂下載工具。結合了 React (Vite) 前端介面與 FastAPI 後端，並透過 PyWebView 提供原生的桌面應用程式體驗。

## ✨ 核心特色

- 🎨 **現代化 UI**：流暢的 React 介面，支援即時下載進度顯示。
- ⚡ **極速下載**：底層使用強大的 `yt-dlp` 進行影片解析與下載。
- 🎬 **多重畫質**：支援從 480p 到 4K 超高畫質的 MP4 下載。
- 🎵 **純音樂提取**：一鍵下載 MP3 格式，自動轉換。
- 🖥️ **跨平台桌面端**：可打包為 Windows / macOS 獨立應用程式（無需安裝 Python 或 Node.js 即可執行）。

---

## 🚀 直接打開 APP 使用

一般使用者不需要安裝 Python、Node.js，也不需要打開終端機。只要下載已經打包好的桌面版 APP，打開後貼上 YouTube 網址就能使用：

1. 前往本專案的 **[Releases 頁面](../../releases)**。
2. 根據你的作業系統下載對應版本：
   - **macOS**：下載 `YT2MP4.app`、`.dmg` 或 `.zip`，解壓後直接打開 `YT2MP4.app`。
   - **Windows**：下載 `YT2MP4.exe`，雙擊打開即可。
3. 下載完成的影片或音樂會存放在電腦的 `Downloads` 資料夾。

打包版會內建前端介面與後端服務；如果打包時有一起包含 FFmpeg，就可以直接合併影片、轉 MP3，並輸出 Windows/macOS 都相容的 MP4。需要登入、年齡限制、私人影片、會員限定或其他受 YouTube 限制的影片，可能無法直接下載。

---

## 🛠️ 本地開發環境設置

如果你想要修改程式碼或進行二次開發，請按照以下步驟啟動專案：

### 0. 前置需求 (Prerequisites)
- [Node.js](https://nodejs.org/) (建議 v18+)
- [Python](https://www.python.org/) 3.8+
- [FFmpeg](https://ffmpeg.org/download.html) (用於影片與音軌的合併、高畫質轉檔)
  - **macOS**: `brew install ffmpeg`
  - **Windows**: 下載後請將 `ffmpeg/bin` 路徑加入到系統的環境變數 `PATH` 中。

### 1. 啟動前端 (Frontend)

前端使用 Vite + React 開發。

```bash
# 進入前端目錄
cd frontend

# 安裝依賴套件
npm install

# 啟動開發伺服器 (預設運行在 http://localhost:5173)
npm run dev
```

### 2. 啟動後端 (Backend)

後端使用 FastAPI 提供 API 服務，並依賴 `yt-dlp` 進行下載作業。

```bash
# 回到專案根目錄
cd ..

# (選擇性) 建立並啟動虛擬環境
python -m venv venv
source venv/bin/activate  # macOS / Linux
# venv\Scripts\activate   # Windows

# 安裝必備的 Python 套件
pip install -r requirements.txt

# 啟動開發伺服器 (網頁模式)
uvicorn main:app --reload

# 或啟動桌面應用程式模式 (會開啟獨立視窗)
python desktop.py
```
> 💡 **開發提示**: 開發期間，你可以同時啟動前端的 `npm run dev` 與後端的 `uvicorn main:app --reload`。Vite 已設定 `/api` proxy，預設會將前端 API 請求導向 `http://127.0.0.1:8000`。如果後端跑在其他位置，可設定 `VITE_API_BASE_URL` 覆蓋。

---

## 📦 打包成桌面應用程式 (Build Desktop App)

你可以使用 PyInstaller 將整個專案打包成單一執行檔，方便分享給其他人直接使用。

### 步驟 1：建置前端靜態檔案

在打包前，必須先將 React 前端建置為靜態網頁：
```bash
cd frontend
npm run build
cd ..
```
這會在 `frontend/dist` 產生打包好的網頁檔案，後端腳本啟動時會自動讀取並掛載。

### 步驟 2：使用 PyInstaller 打包

請確保你的環境中已安裝 `pyinstaller`：
```bash
pip install pyinstaller
```

#### 🍎 macOS 打包指南
專案中已經提供了 `YT2MP4.spec` 檔案。打包時會依序尋找：
- 環境變數 `FFMPEG_BINARY`
- 系統 `PATH` 內的 `ffmpeg`
- Homebrew 常見路徑 `/opt/homebrew/bin/ffmpeg`、`/usr/local/bin/ffmpeg`

如果你想指定 FFmpeg，可以在打包前設定：
```bash
export FFMPEG_BINARY=/opt/homebrew/bin/ffmpeg
```

執行打包指令：
```bash
pyinstaller YT2MP4.spec
```
打包完成後，你可以在 `dist/` 資料夾下找到編譯完成的 `YT2MP4.app` 應用程式。

#### 🪟 Windows 10/11 打包指南
Windows 平台使用 `YT2MP4-windows.spec`。打包時會依序尋找：
- 環境變數 `FFMPEG_BINARY`
- 系統 `PATH` 內的 `ffmpeg.exe` 或 `ffmpeg`
- 專案內的 `bin/ffmpeg.exe`

建議做法是下載 Windows 版 FFmpeg，將 `ffmpeg.exe` 放到專案的 `bin/` 資料夾，或設定：

```powershell
$env:FFMPEG_BINARY="C:\ffmpeg\bin\ffmpeg.exe"
```

執行打包指令：
```powershell
pyinstaller YT2MP4-windows.spec
```

打包完成後，你可以在 `dist/` 資料夾下找到編譯完成的 `YT2MP4.exe`。

---

## 📝 專案結構說明
```text
YT2MP4/
├── frontend/             # React 前端目錄 (Vite)
│   ├── src/              # 前端原始碼
│   ├── dist/             # npm run build 產生的靜態檔案
│   └── package.json      # 前端套件依賴
├── main.py               # FastAPI 後端核心邏輯 (API 處理、yt-dlp 下載、進度回報)
├── desktop.py            # PyWebView 桌面視窗啟動入口 (內嵌 Uvicorn)
├── YT2MP4.spec           # macOS 的 PyInstaller 打包設定檔
├── YT2MP4-windows.spec   # Windows 的 PyInstaller 打包設定檔
├── requirements.txt      # Python 依賴清單
└── README.md             # 本說明文件
```

## 🤝 參與貢獻
歡迎任何人提交 Pull Request 或建立 Issue 來改善這個專案！

## 📄 授權條款
本專案採用 [MIT License](LICENSE) 授權。
