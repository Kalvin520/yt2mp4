import { useState, useRef } from 'react';
import axios from 'axios';

// ==========================================
// 🎨 樣式設定區
// ==========================================
const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '50px 20px',
    fontFamily: "'Inter', 'Segoe UI', sans-serif",
    background: 'linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)',
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
    backdropFilter: 'blur(10px)',
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
    transition: 'all 0.3s ease',
  },
  statusText: {
    marginTop: '25px',
    fontSize: '1.1rem',
    fontWeight: '500',
    minHeight: '26px',
  },
  resultCard: {
    marginTop: '40px',
    background: 'rgba(255, 255, 255, 0.95)',
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
    transition: 'all 0.3s ease',
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
    transition: 'all 0.3s ease',
  },
  progressOverlay: {
    position: 'fixed',
    top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    color: 'white',
    animation: 'fadeIn 0.3s ease-out forwards',
  },
  progressBarContainer: {
    width: '80%',
    maxWidth: '500px',
    height: '24px',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '12px',
    overflow: 'hidden',
    marginTop: '25px',
    boxShadow: 'inset 0 2px 5px rgba(0,0,0,0.5)',
  },
  progressBar: {
    height: '100%',
    background: 'linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%)',
    transition: 'width 0.5s ease',
    boxShadow: '0 0 15px rgba(0, 210, 255, 0.5)',
  },
  progressText: {
    marginTop: '15px',
    fontSize: '1.2rem',
    fontWeight: 'bold',
    color: '#00d2ff',
  }
};

function App() {
  const [url, setUrl] = useState('');
  const [videoInfo, setVideoInfo] = useState(null);
  const [status, setStatus] = useState('');
  const [statusColor, setStatusColor] = useState('#00d2ff');

  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMsg, setProgressMsg] = useState('');

  const timerRef = useRef(null);

  const getApiBaseUrl = () => {
    return (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
  };

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
      const response = await axios.post(`${getApiBaseUrl()}/api/info`, { url: url });
      setVideoInfo(response.data);
      updateStatus('✨ 解析成功！請在下方選擇格式', '#1dd1a1');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || '無法連線伺服器';
      updateStatus(`❌ 解析失敗: ${errorMsg}`, '#ff4757');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const pollProgress = async (taskId) => {
    try {
      const res = await axios.post(`${getApiBaseUrl()}/api/progress`, { task_id: taskId });
      const data = res.data;

      if (data.status === 'completed') {
        setProgress(100);
        setProgressMsg('✅ 處理完成！');
        updateStatus(`🎉 檔案已成功儲存至您的「下載」資料夾！`, '#1dd1a1');
        clearInterval(timerRef.current);
        
        setTimeout(() => {
          setIsDownloading(false);
          if (document.activeElement instanceof HTMLElement) {
            document.activeElement.blur();
          }
        }, 2000);
        return;
      }

      if (data.status === 'error') {
        clearInterval(timerRef.current);
        updateStatus(`❌ 下載失敗: ${data.message}`, '#ff4757');
        setIsDownloading(false);
        return;
      }

      // 更新進度與訊息
      if (data.progress !== undefined) {
        setProgress(data.progress);
      }
      if (data.message) {
        setProgressMsg(data.message);
      }

    } catch (error) {
      console.error("輪詢進度失敗:", error);
    }
  };


  const handleDownload = async (formatId, resolution, type = 'video') => {
    setIsDownloading(true);
    setProgress(0);
    setProgressMsg('🚀 正在初始化下載任務...');

    try {
      // 1. 發送下載請求，後端現在會「立刻」回傳一個 task_id，而不是等下載完
      const response = await axios.post(`${getApiBaseUrl()}/api/download`,
        { 
          url: url, 
          format_id: formatId, 
          type: type,
          resolution: resolution 
        }
      );

      if (response.data.success && response.data.task_id) {
        const taskId = response.data.task_id;
        
        // 2. 開始「輪詢」：每隔 1 秒問一次後端「現在進度到哪了？」
        timerRef.current = setInterval(() => {
          pollProgress(taskId);
        }, 1000);

      } else {
        throw new Error('無法建立下載任務');
      }

    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || '伺服器發生不明錯誤';
      updateStatus(`❌ 下載失敗: ${errorMsg}`, '#ff4757');
      console.error("下載錯誤詳情:", error);
      setIsDownloading(false);
    }
  };

  return (
    <>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .hover-scale:hover { transform: scale(1.02); }
        .hover-btn:hover:not(:disabled) { transform: translateY(-2px); filter: brightness(1.1); }
        .hover-btn:active:not(:disabled) { transform: translateY(1px); }
        .hover-btn:disabled { opacity: 0.5; cursor: not-allowed; filter: grayscale(50%); transform: none; box-shadow: none; }
        .input-focus:focus { border-color: #00d2ff !important; box-shadow: 0 0 15px rgba(0, 210, 255, 0.3) !important; }
      `}</style>

      {isDownloading && (
        <div style={styles.progressOverlay}>
          <div style={{ fontSize: '4rem', marginBottom: '20px' }}>📦</div>
          <h2 style={{ margin: 0, color: '#fff', textShadow: '0 2px 4px rgba(0,0,0,0.5)' }}>
            {progressMsg}
          </h2>

          <div style={styles.progressBarContainer}>
            <div style={{ ...styles.progressBar, width: `${progress}%` }}></div>
          </div>

          <div style={styles.progressText}>
            {Math.floor(progress)}%
          </div>

          {progress >= 80 && progress < 100 && (
            <p style={{ marginTop: '15px', color: '#b2bec3', fontSize: '0.9rem' }}>
              正在進行影音合併或 H.264 轉檔，這可能需要幾分鐘...
            </p>
          )}
        </div>
      )}

      <div style={styles.container}>
        <h1 style={styles.header}>快樂小狗 YT <span style={{ color: '#00d2ff' }}>Studio</span></h1>
        <p style={styles.subtitle}>極致流暢的影音下載體驗</p>

        <div style={styles.inputCard}>
          <input
            className="input-focus"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="貼上 YouTube 影片網址 (https://www...)"
            style={styles.input}
            disabled={isLoading || isDownloading}
          />
          <button
            className="hover-btn"
            onClick={handleGetInfo}
            disabled={isLoading || isDownloading}
            style={styles.btnPrimary}
          >
            {isLoading && !videoInfo ? '🚀 正在解析中...' : '✨ 立即解析網址'}
          </button>
        </div>

        <div style={{ ...styles.statusText, color: statusColor }}>
          {status}
        </div>

        {videoInfo && !isLoading && (
          <div style={styles.resultCard}>
            <div style={styles.titleArea}>
              🎬 <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{videoInfo.title}</span>
            </div>

            <div style={styles.mp3Box} className="hover-scale">
              <div>
                <h3 style={{ margin: 0, color: '#2d3436', fontSize: '1.2rem' }}>只想聽音樂？</h3>
                <p style={{ margin: '5px 0 0 0', color: '#636e72', fontSize: '0.9rem' }}>提取最高音質 MP3</p>
              </div>
              <button
                className="hover-btn"
                onClick={() => handleDownload('bestaudio', '音樂', 'audio')}
                disabled={isDownloading}
                style={styles.btnMp3}
              >
                🎵 下載 MP3
              </button>
            </div>

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
                    disabled={isDownloading}
                    style={styles.btnDownload}
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
