import React, { useState } from 'react';
import axios from 'axios';

// 簡單的 CSS 樣式物件，我們用 JS 變數來管理，方便閱讀
const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '50px 20px',
    fontFamily: "'Inter', 'Segoe UI', sans-serif",
    background: 'linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)', // 酷炫深色漸層背景
    color: '#ffffff',
    transition: 'all 0.5s ease',
  },
  header: {
    fontSize: '3rem',
    fontWeight: '800',
    marginBottom: '10px',
    textShadow: '0 0 10px rgba(52, 152, 219, 0.5)',
    letterSpacing: '1px',
  },
  subtitle: {
    color: '#b2bec3',
    fontSize: '1.1rem',
    marginBottom: '40px',
  },
  inputCard: {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(10px)', // 毛玻璃特效
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '20px',
    padding: '30px',
    boxShadow: '0 15px 35px rgba(0,0,0,0.2)',
    width: '100%',
    maxWidth: '600px',
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  input: {
    width: '100%',
    padding: '18px 20px',
    fontSize: '16px',
    borderRadius: '12px',
    border: '2px solid rgba(255, 255, 255, 0.1)',
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    color: '#fff',
    outline: 'none',
    boxSizing: 'border-box',
    transition: 'border-color 0.3s, box-shadow 0.3s',
  },
  btnPrimary: {
    padding: '15px 30px',
    fontSize: '18px',
    fontWeight: 'bold',
    borderRadius: '12px',
    border: 'none',
    background: 'linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%)',
    color: 'white',
    cursor: 'pointer',
    boxShadow: '0 4px 15px rgba(0, 210, 255, 0.3)',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
  btnDisabled: {
    background: '#555',
    cursor: 'not-allowed',
    boxShadow: 'none',
    color: '#999',
  },
  statusText: {
    marginTop: '25px',
    fontSize: '1.1rem',
    fontWeight: '500',
    minHeight: '26px', // 避免文字跳動
  },
  resultCard: {
    marginTop: '40px',
    background: 'rgba(255, 255, 255, 0.95)', // 改為亮色毛玻璃讓列表更清楚
    backdropFilter: 'blur(15px)',
    borderRadius: '24px',
    padding: '30px',
    width: '100%',
    maxWidth: '700px',
    boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
    color: '#333',
    animation: 'fadeIn 0.5s ease-out forwards',
  },
  titleArea: {
    fontSize: '1.4rem',
    fontWeight: 'bold',
    marginBottom: '25px',
    paddingBottom: '15px',
    borderBottom: '2px solid #f0f0f0',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    color: '#2c3e50',
  },
  mp3Box: {
    background: 'linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)',
    padding: '20px',
    borderRadius: '16px',
    marginBottom: '25px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 10px 20px rgba(142, 197, 252, 0.2)',
  },
  listItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '18px 25px',
    backgroundColor: '#ffffff',
    borderRadius: '16px',
    marginBottom: '15px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.02)',
    border: '1px solid #f1f2f6',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
  btnDownload: {
    padding: '10px 24px',
    backgroundColor: '#ff4757',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontWeight: 'bold',
    fontSize: '15px',
    cursor: 'pointer',
    boxShadow: '0 4px 10px rgba(255, 71, 87, 0.3)',
    transition: 'all 0.2s',
  },
  btnMp3: {
    padding: '12px 25px',
    backgroundColor: '#6c5ce7',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    fontWeight: 'bold',
    fontSize: '16px',
    cursor: 'pointer',
    boxShadow: '0 4px 15px rgba(108, 92, 231, 0.4)',
  }
};

function App() {
  const [url, setUrl] = useState('');
  const [videoInfo, setVideoInfo] = useState(null);
  const [status, setStatus] = useState('');
  const [statusColor, setStatusColor] = useState('#00d2ff');
  const [isLoading, setIsLoading] = useState(false);

  const updateStatus = (msg, color) => {
    setStatus(msg);
    setStatusColor(color);
  };

  const handleGetInfo = async () => {
    if (!url) {
      updateStatus('⚠️ 請先輸入 YouTube 網址喔！', '#ff9f43');
      return;
    }

    setIsLoading(true);
    updateStatus('🔍 正在解析影片畫質與大小，請稍候...', '#00d2ff');
    setVideoInfo(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/info', { url: url });
      setVideoInfo(response.data);
      updateStatus('✨ 解析成功！請在下方選擇格式', '#1dd1a1');
    } catch (error) {
      updateStatus('❌ 解析失敗，請確認網址是否正確。', '#ff4757');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (formatId, resolution, type = 'video') => {
    setIsLoading(true);
    updateStatus(`📥 正在為您打包 ${type === 'audio' ? 'MP3 🎵' : resolution + ' 🎬'}，這可能需要一點時間...`, '#feca57');

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/download',
        { url: url, format_id: formatId, type: type },
        { responseType: 'blob' }
      );

      updateStatus('✅ 處理完成！正在存入您的電腦...', '#1dd1a1');

      const contentDisposition = response.headers['content-disposition'];
      let fileName = type === 'audio' ? "downloaded_audio.mp3" : "downloaded_video.mov";
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

      updateStatus('🎉 檔案已成功下載完成！', '#1dd1a1');

    } catch (error) {
      updateStatus('❌ 下載失敗，請重試。', '#ff4757');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* 簡單的全局動畫樣式 */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .hover-scale:hover { transform: scale(1.02); }
        .hover-btn:hover:not(:disabled) { transform: translateY(-2px); filter: brightness(1.1); }
        .hover-btn:active:not(:disabled) { transform: translateY(1px); }
        .input-focus:focus { border-color: #00d2ff !important; box-shadow: 0 0 15px rgba(0, 210, 255, 0.3) !important; }
      `}</style>

      <div style={styles.container}>

        {/* 標題區塊 */}
        <h1 style={styles.header}>快樂小狗 YT <span style={{ color: '#00d2ff' }}>Studio</span></h1>
        <p style={styles.subtitle}>極致流暢的影音下載體驗</p>

        {/* 輸入區塊 (毛玻璃卡片) */}
        <div style={styles.inputCard}>
          <input
            className="input-focus"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="貼上 YouTube 影片網址 (https://www...)"
            style={styles.input}
          />
          <button
            className="hover-btn"
            onClick={handleGetInfo}
            disabled={isLoading}
            style={{
              ...styles.btnPrimary,
              ...(isLoading ? styles.btnDisabled : {})
            }}
          >
            {isLoading && !videoInfo ? '🚀 正在解析中...' : '✨ 立即解析網址'}
          </button>
        </div>

        {/* 狀態提示文字 */}
        <div style={{ ...styles.statusText, color: statusColor }}>
          {status}
        </div>

        {/* 菜單結果區塊 */}
        {videoInfo && (
          <div style={styles.resultCard}>
            <div style={styles.titleArea}>
              🎬 <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{videoInfo.title}</span>
            </div>

            {/* MP3 下載專區 */}
            <div style={styles.mp3Box} className="hover-scale">
              <div>
                <h3 style={{ margin: 0, color: '#2d3436', fontSize: '1.2rem' }}>只想聽音樂？</h3>
                <p style={{ margin: '5px 0 0 0', color: '#636e72', fontSize: '0.9rem' }}>提取最高音質 MP3</p>
              </div>
              <button
                className="hover-btn"
                onClick={() => handleDownload('bestaudio', '音樂', 'audio')}
                disabled={isLoading}
                style={{ ...styles.btnMp3, ...(isLoading ? styles.btnDisabled : {}) }}
              >
                🎵 下載 MP3
              </button>
            </div>

            {/* 影片畫質列表 */}
            <div style={{ marginTop: '10px' }}>
              <h4 style={{ color: '#a4b0be', marginBottom: '15px', paddingLeft: '5px' }}>選擇影片畫質</h4>
              {videoInfo.options.map((opt, index) => (
                <div key={index} style={styles.listItem} className="hover-scale">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <span style={{ fontSize: '1.3rem', fontWeight: '900', color: '#2f3542', width: '70px' }}>
                      {opt.resolution}
                    </span>
                    <span style={{ color: '#747d8c', fontSize: '0.95rem', backgroundColor: '#f1f2f6', padding: '4px 10px', borderRadius: '6px' }}>
                      預估約 {opt.size_mb === "未知" ? "--" : opt.size_mb} MB
                    </span>
                  </div>

                  <button
                    className="hover-btn"
                    onClick={() => handleDownload(opt.format_id, opt.resolution, 'video')}
                    disabled={isLoading}
                    style={{ ...styles.btnDownload, ...(isLoading ? styles.btnDisabled : {}) }}
                  >
                    下載 ⬇️
                  </button>
                </div>
              ))}
            </div>

          </div>
        )}
      </div>
    </>
  );
}

export default App;