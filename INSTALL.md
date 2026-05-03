# AI File Finder - Installation Guide

## System Requirements

### Minimum:

- **RAM**: 4 GB
- **Storage**: 2 GB free space
- **OS**: Windows 10/11 or macOS 11+

### Recommended:

- **RAM**: 8 GB or more
- **Storage**: 5 GB free space
- **For best performance**: SSD storage

---

## Prerequisites

### 1. Install Ollama

**Windows:**

1. Download from: https://ollama.ai/download
2. Run installer
3. Ollama will start automatically

**macOS:**

1. Download from: https://ollama.ai/download
2. Drag to Applications folder
3. Open Ollama (it runs in menu bar)

**Verify Installation:**

```bash
ollama --version
```

### 2. Download AI Model

Open terminal/command prompt:

```bash
ollama pull llama3.2:3b
```

This downloads ~2GB. Wait for completion.

---

## Installation

### Windows

1. **Download** `AI-File-Finder-Setup.msi`
2. **Double-click** to run installer
3. Follow installation wizard
4. Click **Finish**

The app is now in Start Menu.

### macOS

1. **Download** `AI-File-Finder.dmg`
2. **Double-click** to open
3. **Drag** app to Applications folder
4. Open from Applications

**First time**: Right-click → Open (to bypass Gatekeeper)

---

## First Launch

1. **Start the application**
2. You'll see: "Backend server not running"
3. This is normal on first launch
4. The app will automatically start the backend

**If it doesn't work:**

- Make sure Ollama is running (check system tray/menu bar)
- Check if model is downloaded: `ollama list`

---

## Initial Setup

### 1. Add Folders to Index

1. Click **⚙️ Settings**
2. Go to **"Indexed Folders"**
3. Add your folders:
   - Windows: `C:\Users\YourName\Documents`
   - macOS: `/Users/yourname/Documents`
4. Click **🔄 Index** button
5. Wait for indexing to complete

**Recommended folders to index:**

- Documents
- Desktop
- Downloads
- Projects/Work folders

### 2. Configure Settings (Optional)

- **Excluded file types**: Add extensions to skip
- **Max file size**: Adjust if needed (default: 50MB)
- **LLM Model**: Change if you have more/less RAM

### 3. Start Searching!

Try these queries:

- "find my Python files"
- "show me documents from last week"
- "where is that budget spreadsheet?"

---

## Keyboard Shortcuts

- **Ctrl/Cmd + K**: Focus search
- **Ctrl/Cmd + ,**: Open settings
- **Ctrl/Cmd + H**: Show history
- **Ctrl/Cmd + N**: New conversation
- **Esc**: Clear/Close
- **?**: Show all shortcuts

---

## Troubleshooting

### Backend won't start

**Solution:**

1. Close the app
2. Open Ollama manually
3. Restart the app

### "Model not found" error

**Solution:**

```bash
ollama pull llama3.2:3b
```

### Searches return no results

**Solution:**

1. Go to Settings
2. Check if folders are added
3. Click "Index" button
4. Wait for indexing

### App is slow

**Solution:**

- Use smaller LLM model (llama3.2:1b)
- Reduce max file size in settings
- Index fewer folders
- Close other applications

---

## Uninstallation

### Windows

1. Settings → Apps → AI File Finder → Uninstall
2. Delete data folder (optional):
   - `%APPDATA%\AIFileFinder`

### macOS

1. Drag app to Trash
2. Delete data folder (optional):
   - `~/Library/Application Support/AIFileFinder`

---

## Support

**Issues?** Check:

- Ollama is running
- Model is downloaded
- Folders are indexed
- Enough disk space

**Still having issues?**
Create an issue on GitHub with:

- Your OS version
- Error messages
- What you were trying to do
