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

## 🚀 直接下載使用 (免安裝環境)

如果你只是想使用這個工具，不想設定開發環境，可以直接下載已經打包好的執行檔：

1. 前往本專案的 **[Releases 頁面](../../releases)**。
2. 根據你的作業系統下載對應的版本：
   - **macOS**: 下載 `YT2MP4.app` (或 `.dmg` / `.zip`)
   - **Windows**: 下載 `YT2MP4.exe`
3. 雙擊執行即可開始使用！

*(註：下載的影片預設會存放在你電腦的 `Downloads` 資料夾中。)*

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
pip install fastapi uvicorn yt-dlp pydantic pywebview

# 啟動開發伺服器 (網頁模式)
uvicorn main:app --reload

# 或啟動桌面應用程式模式 (會開啟獨立視窗)
python desktop.py
```
> 💡 **開發提示**: 開發期間，你可以同時啟動前端的 `npm run dev` 與後端的 `uvicorn main:app --reload`，並將前端 API 請求導向後端的 `http://127.0.0.1:8000` 進行前後端分離測試。

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
專案中已經提供了 `YT2MP4.spec` 檔案。
*(⚠️ 注意：該 `.spec` 檔案中目前指定了 `ffmpeg` 的 Homebrew 路徑 `/opt/homebrew/bin/ffmpeg`。如果你的 `ffmpeg` 安裝路徑不同，請在執行打包前先修改 `YT2MP4.spec` 檔內的 `binaries` 參數。)*

執行打包指令：
```bash
pyinstaller YT2MP4.spec
```
打包完成後，你可以在 `dist/` 資料夾下找到編譯完成的 `YT2MP4.app` 應用程式。

#### 🪟 Windows 打包指南
Windows 平台可以參考以下指令進行打包，無需使用 Mac 專用的 `.spec` 檔。若要打包成單一資料夾或單一執行檔，可以使用 `--add-data` 把前端的 `dist` 目錄包進去：

```bash
pyinstaller --noconfirm --onedir --windowed --add-data "frontend/dist;frontend/dist" desktop.py
```
*(💡 提示：若要在 Windows 上免安裝 FFmpeg 即可運行，建議將下載好的 `ffmpeg.exe` 一併用 `--add-binary` 參數打包進去，並在 `main.py` 的 `get_ffmpeg_path` 函式中做好對應的 Windows 路徑處理。)*

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
└── README.md             # 本說明文件
```

## 🤝 參與貢獻
歡迎任何人提交 Pull Request 或建立 Issue 來改善這個專案！

## 📄 授權條款
本專案採用 [MIT License](LICENSE) 授權。
