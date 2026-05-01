import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleDownload = async () => {
    if (!url) {
      setStatus('請先輸入 YouTube 網址喔！');
      return;
    }

    setIsLoading(true);
    setStatus('📥 影片正在伺服器下載處理中，這可能需要幾分鐘，請耐心等候...');

    try {
      // 呼叫後端 API，非常重要的是 responseType 要設為 'blob' (二進位大型物件)
      const response = await axios.post('http://127.0.0.1:8000/api/download',
        { url: url },
        { responseType: 'blob' }
      );

      // --- 下面這是讓瀏覽器自動下載檔案的黑魔法 ---
      setStatus('✅ 處理完成！準備存入你的電腦...');

      // 取得後端傳來的檔名
      const contentDisposition = response.headers['content-disposition'];
      let fileName = "downloaded_video.mp4";
      if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/);
        if (fileNameMatch && fileNameMatch.length === 2) {
          fileName = decodeURIComponent(fileNameMatch[1]);
        }
      }

      // 建立一個虛擬的網址來打包這包檔案
      const fileUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = fileUrl;
      link.setAttribute('download', fileName); // 設定下載的檔名

      // 模擬點擊下載按鈕
      document.body.appendChild(link);
      link.click();

      // 清理垃圾
      link.remove();
      window.URL.revokeObjectURL(fileUrl);
      setStatus('🎉 影片已成功下載到你的電腦！');

    } catch (error) {
      setStatus('❌ 發生錯誤，請檢查網址是否正確。');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '100px', fontFamily: 'sans-serif' }}>
      <h1>🍿 專屬 YouTube 下載神器 🍿</h1>
      <p style={{ color: '#666' }}>貼上網址，無廣告、高畫質直接存進你的電腦</p>

      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://www.youtube.com/watch?v=..."
        style={{ width: '500px', padding: '15px', fontSize: '16px', borderRadius: '8px', border: '1px solid #ccc' }}
      />
      <br /><br />

      <button
        onClick={handleDownload}
        disabled={isLoading}
        style={{
          padding: '15px 30px',
          fontSize: '18px',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          backgroundColor: isLoading ? '#ccc' : '#E50914',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontWeight: 'bold'
        }}
      >
        {isLoading ? '' +
            '努力抓取中 ⏳' : '開始下載影片 👇'}
      </button>

      <h3 style={{ marginTop: '30px', color: isLoading ? '#f39c12' : '#2ecc71' }}>
        {status}
      </h3>
    </div>
  );
}

export default App;