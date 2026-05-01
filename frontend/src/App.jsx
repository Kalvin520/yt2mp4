import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [url, setUrl] = useState('');
  const [videoInfo, setVideoInfo] = useState(null);
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleGetInfo = async () => {
    if (!url) {
      setStatus('請先輸入 YouTube 網址喔！');
      return;
    }

    setIsLoading(true);
    setStatus('🔍 正在解析影片畫質與大小，請稍候...');
    setVideoInfo(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/info', { url: url });
      setVideoInfo(response.data);
      setStatus('✅ 解析成功！請在下方選擇你要下載的格式：');
    } catch (error) {
      setStatus('❌ 解析失敗，請確認網址是否正確。');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (formatId, resolution, type = 'video') => {
    setIsLoading(true);
    setStatus(`📥 正在為您處理並下載 ${type === 'audio' ? 'MP3 音樂' : resolution + '影片'}，請勿關閉視窗...`);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/download',
        { url: url, format_id: formatId, type: type },
        { responseType: 'blob' }
      );

      setStatus('✅ 處理完成！正在存入您的電腦...');

      const contentDisposition = response.headers['content-disposition'];
      let fileName = type === 'audio' ? "downloaded_audio.mp3" : "downloaded_video.mp4";
      if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/);
        if (fileNameMatch && fileNameMatch.length === 2) {
          fileName = decodeURIComponent(fileNameMatch[1]);
        }
      }

      const fileUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = fileUrl;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(fileUrl);

      setStatus('🎉 檔案已成功下載完成！');

    } catch (error) {
      setStatus('❌ 下載失敗，請重試。');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '40px', fontFamily: 'sans-serif' }}>
      <h1>Easy YouTube 2 mp4 🎓 </h1>
      <p style={{ color: '#666' }}>先貼上網址，再選擇您想要的畫質或音樂下載</p>

      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://www.youtube.com/watch?v=..."
        style={{ width: '500px', padding: '15px', fontSize: '16px', borderRadius: '8px', border: '1px solid #ccc' }}
      />
      <br /><br />

      <button
        onClick={handleGetInfo}
        disabled={isLoading}
        style={{
          padding: '12px 24px', fontSize: '16px', cursor: isLoading ? 'not-allowed' : 'pointer',
          backgroundColor: isLoading && !videoInfo ? '#ccc' : '#3498db',
          color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold'
        }}
      >
        {isLoading && !videoInfo ? '解析中 ⏳' : '1. 解析影片網址 🔍'}
      </button>

      <h3 style={{ marginTop: '20px', color: isLoading ? '#f39c12' : '#2ecc71' }}>
        {status}
      </h3>

      {videoInfo && (
        <div style={{ marginTop: '20px', padding: '20px', border: '2px solid #eee', borderRadius: '15px', display: 'inline-block', textAlign: 'left', backgroundColor: '#fdfdfd' }}>
          <h2 style={{ fontSize: '20px', marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '10px', color: '#333' }}>
            🎬 {videoInfo.title}
          </h2>

          {/* 新增的純音樂 MP3 按鈕 */}
          <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#e8f4f8', borderRadius: '8px', border: '1px dashed #3498db', textAlign: 'center' }}>
            <span style={{ marginRight: '15px', fontWeight: 'bold', color: '#333' }}>只想聽音樂？</span>
            <button
              onClick={() => handleDownload('bestaudio', '音樂', 'audio')}
              disabled={isLoading}
              style={{ padding: '10px 25px', backgroundColor: '#2ecc71', color: 'white', border: 'none', borderRadius: '5px', cursor: isLoading ? 'not-allowed' : 'pointer', fontWeight: 'bold', fontSize: '16px' }}
            >
              🎵 下載為 MP3 音檔
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {videoInfo.options.map((opt, index) => (
              <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '8px', width: '450px', border: '1px solid #eee' }}>
                <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#333', width: '80px' }}>
                  {opt.resolution}
                </span>
                <span style={{ color: '#666', fontSize: '15px' }}>
                  檔案大小: {opt.size_mb === "未知" ? "未知大小" : `${opt.size_mb} MB`}
                </span>
                <button
                  onClick={() => handleDownload(opt.format_id, opt.resolution, 'video')}
                  disabled={isLoading}
                  style={{ padding: '8px 20px', backgroundColor: '#E50914', color: 'white', border: 'none', borderRadius: '5px', cursor: isLoading ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}
                >
                  下載 👇
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;