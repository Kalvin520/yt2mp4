import yt_dlp


def download_best_mp4(url):
    print("\n🚀 收到網址！正在自動尋找最高畫質的影片與聲音...")

    ydl_opts = {
        # 【核心魔法】：直接告訴 yt-dlp 抓最好的影像和聲音
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',

        # 強制呼叫 FFmpeg 把它們黏在一起變成 mp4
        'merge_output_format': 'mp4',

        # 設定檔案名稱：使用原本影片的標題加上 .mp4
        'outtmpl': '%(title)s.%(ext)s',

        # （選擇性）不下載播放清單，避免不小心貼到歌單網址一口氣下載 100 首歌
        'noplaylist': True
    }

    try:
        # 開始啟動下載器
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print("\n✅ 太棒了！影片下載與合併成功！請到你的資料夾查看 MP4 檔案。")

    except Exception as e:
        print(f"\n❌ 糟糕，下載過程中發生了一點錯誤：\n{e}")
        print("💡 小提示：最常見的錯誤是沒有安裝 FFmpeg，或是網址不正確喔！")


if __name__ == "__main__":
    print("====================================")
    print("      🎬 超級極簡版影片下載器      ")
    print("====================================")

    # 讓使用者輸入網址
    target_url = input("\n🔗 請貼上你要下載的 YouTube 網址，然後按 Enter：\n> ")

    # 檢查使用者是不是不小心直接按了 Enter 沒有貼網址
    if target_url.strip() != "":
        download_best_mp4(target_url)
    else:
        print("⚠️ 你好像沒有輸入網址喔，請重新執行程式。")