import { useEffect, useState } from "react";
import "./Settings.css";

const API_URL = "http://localhost:5000/api";

function Settings({ onClose }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [indexPaths, setIndexPaths] = useState([]);
  const [newPath, setNewPath] = useState("");
  const [excludedExtensions, setExcludedExtensions] = useState([]);
  const [newExtension, setNewExtension] = useState("");
  const [excludedFolders, setExcludedFolders] = useState([]);
  const [newFolder, setNewFolder] = useState("");
  const [indexing, setIndexing] = useState(false);
  const [indexProgress, setIndexProgress] = useState(null);
  const [currentlyIndexing, setCurrentlyIndexing] = useState("");
  const [settings, setSettings] = useState({
    maxFileSize: 50,
    autoIndex: false,
    llmModel: "llama3.2:3b",
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/settings`);
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.settings) {
          setIndexPaths(data.settings.index_paths || []);
          setExcludedExtensions(data.settings.excluded_extensions || []);
          setExcludedFolders(data.settings.excluded_folders || []);
          setSettings({
            maxFileSize: data.settings.max_file_size || 50,
            autoIndex: data.settings.auto_index || false,
            llmModel: data.settings.llm_model || "llama3.2:3b",
          });
        }
      }
    } catch (error) {
      console.error("Error loading settings:", error);
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API_URL}/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          index_paths: indexPaths,
          excluded_extensions: excludedExtensions,
          excluded_folders: excludedFolders,
          max_file_size: settings.maxFileSize,
          auto_index: settings.autoIndex,
          llm_model: settings.llmModel,
        }),
      });

      const data = await response.json();
      if (data.success) {
        alert(
          "✅ Settings saved successfully!\n\nChanges will take effect immediately."
        );
      } else {
        alert(`❌ Failed to save settings: ${data.error}`);
      }
    } catch (error) {
      console.error("Error saving settings:", error);
      alert("❌ Failed to save settings. Check if backend is running.");
    } finally {
      setSaving(false);
    }
  };

  const resetSettings = async () => {
    if (
      !confirm(
        "Reset all settings to defaults? This will not delete indexed files."
      )
    ) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/settings/reset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      const data = await response.json();
      if (data.success && data.settings) {
        setIndexPaths(data.settings.index_paths || []);
        setExcludedExtensions(data.settings.excluded_extensions || []);
        setExcludedFolders(data.settings.excluded_folders || []);
        setSettings({
          maxFileSize: data.settings.max_file_size || 50,
          autoIndex: data.settings.auto_index || false,
          llmModel: data.settings.llm_model || "llama3.2:3b",
        });
        alert("✅ Settings reset to defaults!");
      }
    } catch (error) {
      console.error("Error resetting settings:", error);
      alert("❌ Failed to reset settings");
    }
  };

  const addPath = () => {
    if (!newPath.trim()) {
      alert("Please enter a valid path");
      return;
    }

    if (indexPaths.includes(newPath.trim())) {
      alert("This path is already added");
      return;
    }

    setIndexPaths([...indexPaths, newPath.trim()]);
    setNewPath("");
  };

  const removePath = (path) => {
    if (confirm(`Remove "${path}" from indexed folders?`)) {
      setIndexPaths(indexPaths.filter((p) => p !== path));
    }
  };

  const addExtension = () => {
    const ext = newExtension.trim().startsWith(".")
      ? newExtension.trim()
      : `.${newExtension.trim()}`;

    if (!ext || ext === ".") {
      alert("Please enter a valid extension");
      return;
    }

    if (excludedExtensions.includes(ext)) {
      alert("This extension is already excluded");
      return;
    }

    setExcludedExtensions([...excludedExtensions, ext]);
    setNewExtension("");
  };

  const removeExtension = (ext) => {
    setExcludedExtensions(excludedExtensions.filter((e) => e !== ext));
  };

  const addFolder = () => {
    if (!newFolder.trim()) {
      alert("Please enter a valid folder name");
      return;
    }

    if (excludedFolders.includes(newFolder.trim())) {
      alert("This folder is already excluded");
      return;
    }

    setExcludedFolders([...excludedFolders, newFolder.trim()]);
    setNewFolder("");
  };

  const removeFolder = (folder) => {
    setExcludedFolders(excludedFolders.filter((f) => f !== folder));
  };

  const startIndexing = async (path, force = false) => {
    const action = force ? "Re-index" : "Index";
    const message = force
      ? `Re-index all files in "${path}"?\n\nThis will re-process all files, even if already indexed.`
      : `Start indexing "${path}"?\n\nThis may take a while depending on the number of files.`;

    if (!confirm(message)) {
      return;
    }

    setIndexing(true);
    setCurrentlyIndexing(path);
    setIndexProgress(null);

    try {
      const response = await fetch(`${API_URL}/index`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: path,
          recursive: true,
          force: force,
        }),
      });

      const data = await response.json();

      if (data.success && data.result) {
        setIndexProgress(data.result);

        const summary = `
✅ Indexing Complete!

Path: ${path}
Total Files: ${data.result.total_files || 0}
Successfully Indexed: ${data.result.successful || 0}
Skipped: ${data.result.skipped || 0}
Failed: ${data.result.failed || 0}
Time Taken: ${(data.result.elapsed_seconds || 0).toFixed(2)}s
        `.trim();

        alert(summary);
      } else {
        alert(`❌ Indexing failed: ${data.error || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Error indexing:", error);
      alert(`❌ Failed to start indexing: ${error.message}`);
    } finally {
      setIndexing(false);
      setCurrentlyIndexing("");
    }
  };

  const indexAllPaths = async () => {
    if (indexPaths.length === 0) {
      alert("No folders to index. Please add at least one folder.");
      return;
    }

    if (
      !confirm(
        `Index all ${indexPaths.length} folder(s)?\n\nThis may take a while.`
      )
    ) {
      return;
    }

    for (const path of indexPaths) {
      await startIndexing(path, false);
    }

    alert("✅ All folders have been indexed!");
  };

  if (loading) {
    return (
      <div className="settings-overlay">
        <div className="settings-panel">
          <div className="settings-header">
            <h2>⚙️ Settings</h2>
            <button className="close-button" onClick={onClose}>
              ✕
            </button>
          </div>
          <div
            className="settings-content"
            style={{ padding: "3rem", textAlign: "center" }}
          >
            <p>Loading settings...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="settings-overlay"
      onClick={(e) => {
        if (e.target.className === "settings-overlay") onClose();
      }}
    >
      <div className="settings-panel">
        {/* Header */}
        <div className="settings-header">
          <h2>⚙️ Settings</h2>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="settings-content">
          {/* Index Paths */}
          <section className="settings-section">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <h3>📁 Indexed Folders</h3>
                <p className="section-description">
                  Add folders to scan and index for searching
                </p>
              </div>
              {indexPaths.length > 0 && (
                <button
                  onClick={indexAllPaths}
                  disabled={indexing}
                  className="action-btn index-btn"
                  style={{ marginLeft: "1rem" }}
                >
                  {indexing ? "⏳ Indexing..." : "🔄 Index All"}
                </button>
              )}
            </div>

            <div className="input-group">
              <input
                type="text"
                value={newPath}
                onChange={(e) => setNewPath(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addPath()}
                placeholder="Windows: C:\Users\YourName\Documents | Mac: /Users/name/Documents"
                className="settings-input"
              />
              <button onClick={addPath} className="add-button">
                + Add Folder
              </button>
            </div>

            <div className="items-list">
              {indexPaths.map((path, idx) => (
                <div key={idx} className="item-card">
                  <span className="item-text">{path}</span>
                  <div className="item-actions">
                    <button
                      onClick={() => startIndexing(path, false)}
                      disabled={indexing}
                      className="action-btn index-btn"
                      title="Index new and modified files"
                    >
                      {indexing && currentlyIndexing === path
                        ? "⏳ Indexing..."
                        : "🔄 Index"}
                    </button>
                    <button
                      onClick={() => startIndexing(path, true)}
                      disabled={indexing}
                      className="action-btn index-btn"
                      title="Re-index all files (slower)"
                      style={{ background: "#FF9800" }}
                    >
                      🔄 Re-index
                    </button>
                    <button
                      onClick={() => removePath(path)}
                      disabled={indexing}
                      className="action-btn remove-btn"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
              {indexPaths.length === 0 && (
                <div className="empty-message">
                  <p>📂 No folders added yet</p>
                  <p
                    style={{
                      fontSize: "0.9rem",
                      color: "#999",
                      marginTop: "0.5rem",
                    }}
                  >
                    Add a folder above to start indexing your files
                  </p>
                </div>
              )}
            </div>
          </section>

          {/* Excluded Extensions */}
          <section className="settings-section">
            <h3>🚫 Excluded File Types</h3>
            <p className="section-description">
              File extensions to ignore during indexing (e.g., temporary files,
              executables)
            </p>

            <div className="input-group">
              <input
                type="text"
                value={newExtension}
                onChange={(e) => setNewExtension(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addExtension()}
                placeholder="Enter extension (e.g., .tmp, .log, .bak)"
                className="settings-input"
              />
              <button onClick={addExtension} className="add-button">
                + Add
              </button>
            </div>

            <div className="tags-list">
              {excludedExtensions.map((ext, idx) => (
                <span key={idx} className="tag">
                  {ext}
                  <button
                    onClick={() => removeExtension(ext)}
                    className="tag-remove"
                    title="Remove this extension"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          </section>

          {/* Excluded Folders */}
          <section className="settings-section">
            <h3>📂 Excluded Folders</h3>
            <p className="section-description">
              Folder names to skip everywhere (e.g., node_modules, .git, build
              folders)
            </p>

            <div className="input-group">
              <input
                type="text"
                value={newFolder}
                onChange={(e) => setNewFolder(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addFolder()}
                placeholder="Enter folder name (e.g., node_modules, .git)"
                className="settings-input"
              />
              <button onClick={addFolder} className="add-button">
                + Add
              </button>
            </div>

            <div className="tags-list">
              {excludedFolders.map((folder, idx) => (
                <span key={idx} className="tag">
                  {folder}
                  <button
                    onClick={() => removeFolder(folder)}
                    className="tag-remove"
                    title="Remove this folder"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          </section>

          {/* General Settings */}
          <section className="settings-section">
            <h3>⚡ General Settings</h3>

            <div className="setting-row">
              <label>
                <strong>Max File Size (MB):</strong>
                <br />
                <small style={{ color: "#666" }}>
                  Files larger than this will be skipped
                </small>
              </label>
              <input
                type="number"
                value={settings.maxFileSize}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    maxFileSize: parseInt(e.target.value) || 50,
                  })
                }
                className="number-input"
                min="1"
                max="500"
              />
            </div>

            <div className="setting-row">
              <label>
                <strong>LLM Model:</strong>
                <br />
                <small style={{ color: "#666" }}>
                  AI model for understanding queries
                </small>
              </label>
              <select
                value={settings.llmModel}
                onChange={(e) =>
                  setSettings({ ...settings, llmModel: e.target.value })
                }
                className="select-input"
              >
                <option value="llama3.2:1b">
                  Llama 3.2 1B (Fastest, 2GB RAM)
                </option>
                <option value="llama3.2:3b">
                  Llama 3.2 3B (Balanced, 4GB RAM)
                </option>
                <option value="llama3.1:8b">
                  Llama 3.1 8B (Best Quality, 8GB RAM)
                </option>
              </select>
            </div>

            <div className="setting-row">
              <label
                style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
              >
                <input
                  type="checkbox"
                  checked={settings.autoIndex}
                  onChange={(e) =>
                    setSettings({ ...settings, autoIndex: e.target.checked })
                  }
                />
                <span>
                  <strong>Auto-index on startup</strong>
                  <br />
                  <small style={{ color: "#666" }}>
                    Automatically update index when app starts
                  </small>
                </span>
              </label>
            </div>
          </section>

          {/* Index Progress */}
          {indexProgress && (
            <section className="settings-section">
              <h3>📊 Last Indexing Results</h3>
              <div className="progress-stats">
                <div className="stat">
                  <span className="stat-label">Total Files</span>
                  <span className="stat-value">
                    {indexProgress.total_files || 0}
                  </span>
                </div>
                <div className="stat">
                  <span className="stat-label">Successful</span>
                  <span className="stat-value success">
                    {indexProgress.successful || 0}
                  </span>
                </div>
                <div className="stat">
                  <span className="stat-label">Skipped</span>
                  <span className="stat-value">
                    {indexProgress.skipped || 0}
                  </span>
                </div>
                <div className="stat">
                  <span className="stat-label">Failed</span>
                  <span className="stat-value error">
                    {indexProgress.failed || 0}
                  </span>
                </div>
              </div>
              <p
                style={{
                  textAlign: "center",
                  color: "#666",
                  marginTop: "1rem",
                  fontSize: "0.9rem",
                }}
              >
                Time taken: {(indexProgress.elapsed_seconds || 0).toFixed(2)}s
              </p>
            </section>
          )}
        </div>

        {/* Footer */}
        <div className="settings-footer">
          <button
            onClick={resetSettings}
            className="cancel-button"
            style={{ marginRight: "auto" }}
          >
            🔄 Reset to Defaults
          </button>
          <button onClick={onClose} className="cancel-button">
            Cancel
          </button>
          <button
            onClick={saveSettings}
            className="save-button"
            disabled={saving}
          >
            {saving ? "⏳ Saving..." : "💾 Save Settings"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Settings;
