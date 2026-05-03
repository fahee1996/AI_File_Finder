# 🔍 AI File Finder

> Find your files using natural language. Powered by local AI.

![AI File Finder](screenshot.png)

**AI File Finder** is a desktop application that uses artificial intelligence to help you find files using natural language queries. Everything runs locally - your data never leaves your computer.

---

## ✨ Features

- 🤖 **Natural Language Search**: Ask like you would a person

  - "Find my Python files from last week"
  - "Show me that budget spreadsheet"
  - "Where's the presentation about sales?"

- 🚀 **Semantic Search**: Understands meaning, not just keywords

  - Finds files even if you don't remember exact names
  - Vector embeddings for intelligent matching

- 🔒 **100% Local & Private**:

  - No cloud services
  - No data collection
  - All processing on your device

- ⚡ **Fast & Efficient**:

  - Indexes 100,000+ files
  - Search results in < 1 second
  - Incremental indexing

- 📂 **File Operations**:

  - Open files
  - Show in folder
  - Copy path
  - Move/Rename (coming soon)

- ⌨️ **Keyboard Shortcuts**: Power-user friendly

- 📜 **Search History & Favorites**: Quick access to common searches

---

## 🎯 Use Cases

- **Developers**: Find that config file or code snippet
- **Researchers**: Locate papers and notes quickly
- **Writers**: Find documents by content
- **Everyone**: Stop digging through folders!

---

## 📸 Screenshots

### Chat Interface

![Chat](screenshots/chat.png)

### Search Results

![Results](screenshots/results.png)

### Settings

![Settings](screenshots/settings.png)

---

## 🚀 Quick Start

### Prerequisites

1. **Ollama** (AI runtime)

   - Download: https://ollama.ai/download
   - Install and run

2. **Download AI Model**:

```bash
   ollama pull llama3.2:3b
```

### Installation

**Download for your platform:**

- 🪟 [Windows (MSI)](releases/latest)
- 🍎 [macOS (DMG)](releases/latest)

See [INSTALL.md](INSTALL.md) for detailed instructions.

---

## 🏗️ Technology Stack

- **Frontend**: Tauri + React + JavaScript
- **Backend**: Python + Flask
- **AI**: Ollama (Llama 3.2 3B)
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence Transformers
- **File Operations**: Cross-platform Python libraries

---

## 📊 Performance

With 168,604 indexed files:

- **Indexing speed**: 50-100 files/second
- **Search latency**: < 500ms
- **Memory usage**: ~500MB
- **Storage**: ~200MB for index

---

## 🛠️ Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ai-file-finder
cd ai-file-finder

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install

# Download model
ollama pull llama3.2:3b
```

### Run Development

**Terminal 1 - Backend:**

```bash
cd backend
python http_server.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run tauri dev
```

### Build

```bash
# Windows
.\build.ps1

# macOS/Linux
./build.sh
```

---

## 📝 Roadmap

### ✅ MVP (v1.0) - Current

- Natural language search
- File operations
- Settings panel
- Keyboard shortcuts
- History & favorites

### 🚧 v1.1 - Next

- Advanced filters
- Date range picker
- File size filters
- Multiple file types

### 🔮 v1.2 - Future

- File preview
- Batch operations
- Cloud sync (optional)
- Mobile companion app
- Custom AI models

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **Tauri** - Desktop app framework
- **ChromaDB** - Vector database
- **Sentence Transformers** - Embeddings

---

## 📧 Contact

Questions? Feedback? Open an issue or reach out!

---

**Made with ❤️ for people who can't find their files**
