import "./Settings.css";

function SettingsTest({ onClose }) {
  return (
    <div className="settings-overlay" style={{ background: "rgba(0,0,0,0.7)" }}>
      <div className="settings-panel" style={{ background: "white" }}>
        <div className="settings-header" style={{ background: "#f8f9fa" }}>
          <h2>Test Settings</h2>
          <button
            onClick={onClose}
            style={{
              background: "red",
              color: "white",
              border: "none",
              padding: "10px",
            }}
          >
            Close
          </button>
        </div>
        <div style={{ padding: "2rem", background: "white", color: "black" }}>
          <p>If you can see this text, the component is rendering!</p>
          <p>Background should be white, text should be black.</p>
        </div>
      </div>
    </div>
  );
}

export default SettingsTest;
