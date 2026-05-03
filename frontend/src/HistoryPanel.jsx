import { useEffect, useState } from "react";
import "./HistoryPanel.css";
import storageService from "./services/storage";

function HistoryPanel({ onClose, onSearchHistoryClick, onFileClick }) {
  const [activeTab, setActiveTab] = useState("history"); // 'history', 'favorites', 'recent'
  const [searchHistory, setSearchHistory] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [recentFiles, setRecentFiles] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setSearchHistory(storageService.getSearchHistory());
    setFavorites(storageService.getFavorites());
    setRecentFiles(storageService.getRecentFiles());
  };

  const clearHistory = () => {
    if (confirm("Clear all search history?")) {
      storageService.clearSearchHistory();
      setSearchHistory([]);
    }
  };

  const clearFavorites = () => {
    if (confirm("Remove all favorites?")) {
      storageService.clearFavorites();
      setFavorites([]);
    }
  };

  const clearRecent = () => {
    if (confirm("Clear recent files?")) {
      storageService.clearRecentFiles();
      setRecentFiles([]);
    }
  };

  const removeFavorite = (filePath) => {
    const updated = storageService.removeFromFavorites(filePath);
    setFavorites(updated);
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getFileIcon = (extension) => {
    const icons = {
      ".pdf": "📄",
      ".doc": "📝",
      ".docx": "📝",
      ".xls": "📊",
      ".xlsx": "📊",
      ".ppt": "📊",
      ".pptx": "📊",
      ".txt": "📃",
      ".md": "📃",
      ".jpg": "🖼️",
      ".jpeg": "🖼️",
      ".png": "🖼️",
      ".gif": "🖼️",
      ".mp4": "🎬",
      ".avi": "🎬",
      ".mov": "🎬",
      ".mp3": "🎵",
      ".wav": "🎵",
      ".zip": "📦",
      ".rar": "📦",
      ".py": "🐍",
      ".js": "📜",
      ".jsx": "📜",
      ".ts": "📜",
      ".tsx": "📜",
      ".html": "🌐",
      ".css": "🎨",
    };
    return icons[extension?.toLowerCase()] || "📁";
  };

  return (
    <div className="history-overlay" onClick={onClose}>
      <div className="history-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="history-header">
          <h2>📜 History & Favorites</h2>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div className="history-tabs">
          <button
            className={`history-tab ${activeTab === "history" ? "active" : ""}`}
            onClick={() => setActiveTab("history")}
          >
            🔍 Search History ({searchHistory.length})
          </button>
          <button
            className={`history-tab ${
              activeTab === "favorites" ? "active" : ""
            }`}
            onClick={() => setActiveTab("favorites")}
          >
            ⭐ Favorites ({favorites.length})
          </button>
          <button
            className={`history-tab ${activeTab === "recent" ? "active" : ""}`}
            onClick={() => setActiveTab("recent")}
          >
            🕐 Recent ({recentFiles.length})
          </button>
        </div>

        {/* Content */}
        <div className="history-content">
          {/* Search History Tab */}
          {activeTab === "history" && (
            <div className="history-list">
              <div className="list-header">
                <h3>Recent Searches</h3>
                {searchHistory.length > 0 && (
                  <button className="clear-button" onClick={clearHistory}>
                    Clear All
                  </button>
                )}
              </div>

              {searchHistory.length === 0 ? (
                <div className="empty-state">
                  <p>🔍 No search history yet</p>
                  <p className="empty-subtitle">
                    Your searches will appear here
                  </p>
                </div>
              ) : (
                searchHistory.map((item, idx) => (
                  <div
                    key={idx}
                    className="history-item"
                    onClick={() => {
                      onSearchHistoryClick(item.query);
                      onClose();
                    }}
                  >
                    <span className="history-icon">🔍</span>
                    <div className="history-info">
                      <div className="history-text">{item.query}</div>
                      <div className="history-time">
                        {formatDate(item.timestamp)}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Favorites Tab */}
          {activeTab === "favorites" && (
            <div className="history-list">
              <div className="list-header">
                <h3>Favorite Files</h3>
                {favorites.length > 0 && (
                  <button className="clear-button" onClick={clearFavorites}>
                    Clear All
                  </button>
                )}
              </div>

              {favorites.length === 0 ? (
                <div className="empty-state">
                  <p>⭐ No favorites yet</p>
                  <p className="empty-subtitle">
                    Star files to quick access them
                  </p>
                </div>
              ) : (
                favorites.map((file, idx) => (
                  <div key={idx} className="history-item file-item">
                    <span className="history-icon">
                      {getFileIcon(file.extension)}
                    </span>
                    <div className="history-info">
                      <div className="history-text">{file.name}</div>
                      <div className="history-time">
                        {formatDate(file.favoritedAt)}
                      </div>
                    </div>
                    <div className="file-actions">
                      <button
                        className="icon-button"
                        onClick={() => {
                          onFileClick("open", file.path);
                          onClose();
                        }}
                        title="Open"
                      >
                        📂
                      </button>
                      <button
                        className="icon-button remove"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFavorite(file.path);
                        }}
                        title="Remove from favorites"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Recent Files Tab */}
          {activeTab === "recent" && (
            <div className="history-list">
              <div className="list-header">
                <h3>Recently Opened</h3>
                {recentFiles.length > 0 && (
                  <button className="clear-button" onClick={clearRecent}>
                    Clear All
                  </button>
                )}
              </div>

              {recentFiles.length === 0 ? (
                <div className="empty-state">
                  <p>🕐 No recent files</p>
                  <p className="empty-subtitle">
                    Files you open will appear here
                  </p>
                </div>
              ) : (
                recentFiles.map((file, idx) => (
                  <div key={idx} className="history-item file-item">
                    <span className="history-icon">
                      {getFileIcon(file.extension)}
                    </span>
                    <div className="history-info">
                      <div className="history-text">{file.name}</div>
                      <div className="history-time">
                        {formatDate(file.openedAt)}
                      </div>
                    </div>
                    <div className="file-actions">
                      <button
                        className="icon-button"
                        onClick={() => {
                          onFileClick("open", file.path);
                          onClose();
                        }}
                        title="Open again"
                      >
                        📂
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default HistoryPanel;
