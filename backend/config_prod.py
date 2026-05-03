"""
Production configuration
"""
from pathlib import Path
import sys
import os

# Determine if running as frozen exe (PyInstaller)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent
    APP_DIR = BASE_DIR

# Use AppData for user data
if sys.platform == 'win32':
    DATA_DIR = Path(os.getenv('APPDATA')) / 'AIFileFinder'
elif sys.platform == 'darwin':
    DATA_DIR = Path.home() / 'Library' / 'Application Support' / 'AIFileFinder'
else:
    DATA_DIR = Path.home() / '.aifilefinder'

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Production settings
CHROMA_DIR = DATA_DIR / "chroma_db"
CACHE_DIR = DATA_DIR / "cache"
LOGS_DIR = DATA_DIR / "logs"
SETTINGS_FILE = DATA_DIR / "settings.json"

# Create directories
CHROMA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# LLM Settings
LLM_MODEL = "llama3.2:3b"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Server settings
SERVER_HOST = "localhost"
SERVER_PORT = 5000

print(f"[Config] Data directory: {DATA_DIR}")
print(f"[Config] ChromaDB: {CHROMA_DIR}")
print(f"[Config] Settings: {SETTINGS_FILE}")