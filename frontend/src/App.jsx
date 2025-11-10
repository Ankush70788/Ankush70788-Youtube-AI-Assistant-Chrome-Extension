import { useState, useEffect } from 'react';
import './App.css'; // We'll create this next

function App() {
  const [videoUrl, setVideoUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]); // [{type: 'user', text: '...'}, {type: 'ai', text: '...'}]
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isProcessed, setIsProcessed] = useState(false);

  const BACKEND_URL = 'http://127.0.0.1:8000';

  // Get the current YouTube tab URL when the popup opens
  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const currentUrl = tabs[0].url;
      if (currentUrl && (currentUrl.includes('youtube.com/watch') || currentUrl.includes('youtu.be/'))) {
        setVideoUrl(currentUrl);
      } else {
        setError('Not a YouTube video page.');
      }
    });
  }, []);

  const handleProcessVideo = async () => {
    if (!videoUrl) return;
    setIsLoading(true);
    setError('');
    setChatHistory([]); // Clear chat on new video
    
    try {
      const response = await fetch(`${BACKEND_URL}/process-video`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: videoUrl }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to process video');
      }

      const data = await response.json();
      setVideoId(data.video_id);
      setIsProcessed(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question || !videoId) return;
    setIsLoading(true);
    setError('');
    
    // Add user question to chat
    setChatHistory(prev => [...prev, { type: 'user', text: question }]);
    const currentQuestion = question;
    setQuestion(''); // Clear input

    try {
      const response = await fetch(`${BACKEND_URL}/ask-question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id: videoId, question: currentQuestion }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to get answer');
      }

      const data = await response.json();
      // Add AI answer to chat
      setChatHistory(prev => [...prev, { type: 'ai', text: data.answer }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h2>YouTube Q&A</h2>
      {error && <div className="error-box">{error}</div>}

      {!isProcessed ? (
        <div className="processing-section">
          <p>Ready to process:</p>
          <span className="video-url">{videoUrl.substring(0, 40)}...</span>
          <button onClick={handleProcessVideo} disabled={isLoading || !videoUrl}>
            {isLoading ? 'Processing...' : 'Start Q&A'}
          </button>
        </div>
      ) : (
        <div className="qa-section">
          <div className="chat-window">
            {chatHistory.length === 0 && (
              <div className="chat-message ai">
                <p>Video processed! Ask me anything about it.</p>
              </div>
            )}
            {chatHistory.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.type}`}>
                <p>{msg.text}</p>
              </div>
            ))}
            {isLoading && chatHistory.length > 0 && (
              <div className="chat-message ai">
                <p><i>Thinking...</i></p>
              </div>
            )}
          </div>
          <div className="input-area">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion()}
              placeholder="Ask a question..."
              disabled={isLoading}
            />
            <button onClick={handleAskQuestion} disabled={isLoading || !question}>
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;