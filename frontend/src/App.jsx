import { useEffect, useRef, useState } from "react";
import "./App.css";
import HistoryPanel from "./HistoryPanel";
import { useKeyboardShortcuts } from "./hooks/useKeyboard";
import KeyboardHelp from "./KeyboardHelp";
import storageService from "./services/storage";
import Settings from "./Settings";

const API_URL = "http://localhost:5000/api";

// Helper function for API calls
async function apiCall(endpoint, data = null) {
  const options = {
    method: data ? "POST" : "GET",
    headers: { "Content-Type": "application/json" },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(`${API_URL}${endpoint}`, options);
  return response.json();
}

function App() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState("chat");
  const [serverConnected, setServerConnected] = useState(false); // ADD THIS

  const [showSettings, setShowSettings] = useState(false);

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  const [showKeyboardHelp, setShowKeyboardHelp] = useState(false);

  const [showHistory, setShowHistory] = useState(false);
  const [favorites, setFavorites] = useState([]);

  // Keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: "k",
      ctrl: true,
      callback: () => {
        inputRef.current?.focus();
        inputRef.current?.select();
      },
    },
    {
      key: "h",
      ctrl: true,
      callback: () => {
        setShowHistory(true);
      },
    },
    {
      key: "Escape",
      callback: () => {
        if (showSettings) {
          setShowSettings(false);
        } else if (searchResults.length > 0) {
          setSearchResults([]);
        } else {
          setMessage("");
          inputRef.current?.blur();
        }
      },
    },
    {
      key: ",",
      ctrl: true,
      callback: () => {
        setShowSettings(true);
      },
    },
    {
      key: "n",
      ctrl: true,
      callback: () => {
        setChatHistory([]);
        setSearchResults([]);
        setMessage("");
      },
    },
    {
      key: "ArrowUp",
      alt: true,
      callback: () => {
        // Navigate up in results
        if (searchResults.length > 0) {
          setSelectedResult((prev) =>
            prev > 0 ? prev - 1 : searchResults.length - 1
          );
        }
      },
    },
    {
      key: "ArrowDown",
      alt: true,
      callback: () => {
        // Navigate down in results
        if (searchResults.length > 0) {
          setSelectedResult((prev) =>
            prev < searchResults.length - 1 ? prev + 1 : 0
          );
        }
      },
    },
    {
      key: "?",
      shift: true,
      callback: () => {
        setShowKeyboardHelp(true);
      },
    },
    {
      key: "Enter",
      alt: true,
      callback: () => {
        // Open selected result
        if (searchResults.length > 0 && selectedResult >= 0) {
          handleFileAction("open", searchResults[selectedResult].path);
        }
      },
    },
  ]);

  const [selectedResult, setSelectedResult] = useState(-1);

  // Load stats on mount
  useEffect(() => {
    checkServerConnection();
    setFavorites(storageService.getFavorites());
  }, []);

  const checkServerConnection = async () => {
    try {
      const response = await apiCall("/stats");
      if (response.success) {
        setStats(response.stats);
        setServerConnected(true);
      }
    } catch (error) {
      console.error("Server not connected:", error);
      setServerConnected(false);
      setChatHistory([
        {
          role: "error",
          content:
            "⚠️ Backend server not running. Please start it in a terminal: cd backend && python http_server.py",
          timestamp: new Date(),
        },
      ]);
    }
  };

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const loadStats = async () => {
    try {
      const response = await invoke("get_stats");
      if (response.success && response.stats) {
        setStats(response.stats);
      }
    } catch (error) {
      console.error("Error loading stats:", error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!message.trim()) return;

    const userMessage = message.trim();
    storageService.addToSearchHistory(userMessage);

    setMessage("");

    setChatHistory((prev) => [
      ...prev,
      {
        role: "user",
        content: userMessage,
        timestamp: new Date(),
      },
    ]);

    setLoading(true);

    try {
      const response = await apiCall("/chat", { message: userMessage });

      if (response.success) {
        setChatHistory((prev) => [
          ...prev,
          {
            role: "assistant",
            content: response.response,
            timestamp: new Date(),
          },
        ]);

        if (response.results && response.results.length > 0) {
          setSearchResults(response.results);
        }
      } else {
        setChatHistory((prev) => [
          ...prev,
          {
            role: "error",
            content: response.error || "An error occurred",
            timestamp: new Date(),
          },
        ]);
      }
    } catch (error) {
      console.error("Error:", error);
      setChatHistory((prev) => [
        ...prev,
        {
          role: "error",
          content:
            "Failed to connect to backend server. Make sure http_server.py is running.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleFileAction = async (action, filePath, fileData = null) => {
    try {
      let response;

      if (action === "open") {
        response = await apiCall("/file/open", { path: filePath });
        if (response.success && fileData) {
          storageService.addToRecentFiles(fileData);
        }
      } else if (action === "show") {
        response = await apiCall("/file/show", { path: filePath });
      } else if (action === "copy") {
        response = await apiCall("/file/copy-path", { path: filePath });
      } else if (action === "favorite") {
        if (storageService.isFavorite(filePath)) {
          storageService.removeFromFavorites(filePath);
          setFavorites(storageService.getFavorites());
          return { success: true, message: "Removed from favorites" };
        } else {
          storageService.addToFavorites(fileData);
          setFavorites(storageService.getFavorites());
          return { success: true, message: "Added to favorites" };
        }
      }

      if (response && response.success) {
        setChatHistory((prev) => [
          ...prev,
          {
            role: "system",
            content: response.message || "Action completed",
            timestamp: new Date(),
          },
        ]);
      } else if (response) {
        alert(response.error || "Action failed");
      }
    } catch (error) {
      console.error("File action error:", error);
      alert("Failed to connect to backend server");
    }
  };

  const formatFileSize = (mb) => {
    if (mb < 0.01) return `${(mb * 1024).toFixed(2)} KB`;
    if (mb < 1024) return `${mb.toFixed(2)} MB`;
    return `${(mb / 1024).toFixed(2)} GB`;
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🔍 AI File Finder</h1>

          {/* header-right: settings button + stats (shown only if serverConnected) */}
          <div className="header-right">
            <button
              className="settings-button"
              onClick={() => setShowSettings(true)}
              title="Settings"
            >
              ⚙️
            </button>

            <button
              className="history-button"
              onClick={() => setShowHistory(true)}
              title="History & Favorites (Ctrl+H)"
            >
              📜
            </button>

            <button
              className="help-button"
              onClick={() => setShowKeyboardHelp(true)}
              title="Keyboard shortcuts (?)"
            >
              ⌨️
            </button>

            {stats && serverConnected && (
              <div className="stats-badge">
                {stats.total_files_indexed?.toLocaleString() || 0} files indexed
              </div>
            )}
          </div>
        </div>

        <div className="tabs">
          <button
            className={`tab ${activeTab === "chat" ? "active" : ""}`}
            onClick={() => setActiveTab("chat")}
          >
            💬 Chat
          </button>
          <button
            className={`tab ${activeTab === "search" ? "active" : ""}`}
            onClick={() => setActiveTab("search")}
          >
            🔎 Search
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === "chat" ? (
          // Chat Tab
          <div className="chat-container">
            <div className="chat-messages">
              {chatHistory.length === 0 && (
                <div className="welcome-message">
                  <h2>👋 Welcome to AI File Finder!</h2>
                  <p>Ask me to find files using natural language:</p>
                  <ul>
                    <li>"Find my Python files from last week"</li>
                    <li>"Show me that budget spreadsheet"</li>
                    <li>"Open the presentation about sales"</li>
                    <li>"What files do I have?"</li>
                  </ul>
                </div>
              )}

              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`message message-${msg.role}`}>
                  <div className="message-content">{msg.content}</div>
                  <div className="message-time">
                    {msg.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message message-assistant">
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            <form onSubmit={handleSendMessage} className="chat-input-form">
              <input
                ref={inputRef}
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask me to find files..."
                className="chat-input"
                disabled={loading}
              />
              <button
                type="submit"
                className="send-button"
                disabled={loading || !message.trim()}
              >
                {loading ? "⏳" : "➤"}
              </button>
            </form>
          </div>
        ) : (
          // Search Tab (placeholder for now)
          <div className="search-container">
            <div className="coming-soon">
              <h2>Direct Search</h2>
              <p>Coming soon! For now, use the Chat tab.</p>
            </div>
          </div>
        )}

        {/* Search Results Sidebar */}
        {searchResults.length > 0 && (
          <aside className="results-sidebar">
            <div className="results-header">
              <h3>📂 Results ({searchResults.length})</h3>
              <button
                className="clear-button"
                onClick={() => setSearchResults([])}
              >
                ✕
              </button>
            </div>

            <div className="results-list">
              {searchResults.map((result, idx) => (
                <div
                  key={idx}
                  className={`result-card ${
                    selectedResult === idx ? "selected" : ""
                  }`}
                >
                  <div className="result-header">
                    <span className="result-icon">
                      {result.extension === ".pdf"
                        ? "📄"
                        : result.extension === ".xlsx" ||
                          result.extension === ".xls"
                        ? "📊"
                        : result.extension === ".docx" ||
                          result.extension === ".doc"
                        ? "📝"
                        : result.extension === ".py"
                        ? "🐍"
                        : result.extension === ".js" ||
                          result.extension === ".jsx"
                        ? "📜"
                        : "📁"}
                    </span>
                    <span className="result-name" title={result.name}>
                      {result.name}
                    </span>
                  </div>

                  <div className="result-details">
                    <span className="result-size">
                      {formatFileSize(result.size_mb)}
                    </span>
                    <span className="result-score">
                      {(result.relevance_score * 100).toFixed(0)}% match
                    </span>
                  </div>

                  {result.preview && (
                    <div className="result-preview">
                      {result.preview.substring(0, 100)}...
                    </div>
                  )}

                  <div className="result-actions">
                    <button
                      onClick={() =>
                        handleFileAction("favorite", result.path, result)
                      }
                      className={`action-button ${
                        storageService.isFavorite(result.path)
                          ? "favorited"
                          : ""
                      }`}
                      title={
                        storageService.isFavorite(result.path)
                          ? "Remove from favorites"
                          : "Add to favorites"
                      }
                    >
                      {storageService.isFavorite(result.path) ? "⭐" : "☆"}{" "}
                      Favorite
                    </button>
                    <button
                      onClick={() => handleFileAction("open", result.path)}
                      className="action-button"
                      title="Open file"
                    >
                      📂 Open
                    </button>
                    <button
                      onClick={() => handleFileAction("show", result.path)}
                      className="action-button"
                      title="Show in folder"
                    >
                      📁 Show
                    </button>
                    <button
                      onClick={() => handleFileAction("copy", result.path)}
                      className="action-button"
                      title="Copy path"
                    >
                      📋 Copy
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </aside>
        )}
      </main>
      {/* Settings Panel */}
      {showSettings && <Settings onClose={() => setShowSettings(false)} />}
      {/* Keyboard Help */}
      {showKeyboardHelp && (
        <KeyboardHelp onClose={() => setShowKeyboardHelp(false)} />
      )}
      {/* History Panel */}
      {showHistory && (
        <HistoryPanel
          onClose={() => setShowHistory(false)}
          onSearchHistoryClick={(query) => {
            setMessage(query);
            inputRef.current?.focus();
          }}
          onFileClick={handleFileAction}
        />
      )}
    </div>
  );
}

export default App;
