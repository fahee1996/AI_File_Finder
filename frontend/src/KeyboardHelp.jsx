import "./KeyboardHelp.css";

function KeyboardHelp({ onClose }) {
  const shortcuts = [
    { keys: ["Ctrl/Cmd", "K"], description: "Focus search box" },
    { keys: ["Ctrl/Cmd", ","], description: "Open settings" },
    { keys: ["Ctrl/Cmd", "N"], description: "New conversation" },
    { keys: ["Esc"], description: "Clear results / Close dialog" },
    { keys: ["Alt", "↑"], description: "Navigate up in results" },
    { keys: ["Alt", "↓"], description: "Navigate down in results" },
    { keys: ["Alt", "Enter"], description: "Open selected file" },
    { keys: ["?"], description: "Show this help" },
  ];

  return (
    <div className="keyboard-help-overlay" onClick={onClose}>
      <div className="keyboard-help-panel" onClick={(e) => e.stopPropagation()}>
        <div className="keyboard-help-header">
          <h2>⌨️ Keyboard Shortcuts</h2>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="shortcuts-grid">
          {shortcuts.map((shortcut, idx) => (
            <div key={idx} className="shortcut-row">
              <div className="shortcut-keys">
                {shortcut.keys.map((key, keyIdx) => (
                  <span key={keyIdx}>
                    <kbd className="key">{key}</kbd>
                    {keyIdx < shortcut.keys.length - 1 && (
                      <span className="key-separator">+</span>
                    )}
                  </span>
                ))}
              </div>
              <div className="shortcut-description">{shortcut.description}</div>
            </div>
          ))}
        </div>

        <div className="keyboard-help-footer">
          <p>
            Press <kbd className="key">?</kbd> anytime to show this help
          </p>
        </div>
      </div>
    </div>
  );
}

export default KeyboardHelp;
