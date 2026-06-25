import threading
import uvicorn
import webview
import socket
from main import app  # 引入我們寫好的 FastAPI App

server = None

def find_free_port():
    """自動找尋一個系統上沒人用的 Port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def run_server(port):
    """在背景執行緒中啟動 FastAPI"""
    global server
    # 關閉 uvicorn 的預設輸出，讓終端機乾淨一點
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    server.run()

class Api:
    """提供給網頁前端呼叫的桌面專用 API (非必要，但可以擴充功能)"""
    def __init__(self, window):
        self.window = window

def on_closed():
    """當使用者關閉視窗時觸發：通知背景伺服器結束"""
    print("視窗已關閉，正在結束程式...")
    if server:
        server.should_exit = True

if __name__ == '__main__':
    # 1. 取得可用 Port
    port = find_free_port()
    url = f"http://127.0.0.1:{port}"
    print(f"後端伺服器啟動於: {url}")

    # 2. 啟動背景伺服器執行緒
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    # 3. 建立並啟動桌面視窗
    window = webview.create_window(
        title='YT2MP4 Downloader', 
        url=url, 
        width=800, 
        height=600,
        min_size=(600, 500)
    )
    
    # 綁定關閉事件
    window.events.closed += on_closed

    # 啟動 WebView 視窗 (會卡在這裡直到視窗關閉)
    webview.start()
    if server_thread.is_alive():
        server_thread.join(timeout=5)
