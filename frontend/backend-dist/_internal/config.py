"""Application configuration module"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

@dataclass
class Config:
    """Application configuration settings"""
    
    # Application Info
    APP_NAME: str = "AI File Finder"
    VERSION: str = "0.1.0"
    
    # Paths
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).parent)
    DATA_DIR: Path = field(init=False)
    CHROMA_DIR: Path = field(init=False)
    CACHE_DIR: Path = field(init=False)
    
    # LLM Settings
    LLM_MODEL: str = "llama3.2:3b"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_TEMPERATURE: float = 0.7
    
    # Search Settings
    MAX_SEARCH_RESULTS: int = 10
    CONTENT_PREVIEW_LENGTH: int = 500
    MIN_SIMILARITY_SCORE: float = 0.5
    
    # Indexing Settings
    EXCLUDED_EXTENSIONS: List[str] = field(default_factory=lambda: [
        '.exe', '.dll', '.so', '.dylib',
        '.sys', '.tmp', '.log', '.cache',
        '.bin', '.dat', '.iso'
    ])
    
    EXCLUDED_FOLDERS: List[str] = field(default_factory=lambda: [
        'node_modules', '__pycache__', '.git',
        'venv', 'env', '.venv', 'target',
        '.idea', '.vscode', 'dist', 'build'
    ])
    
    SUPPORTED_EXTENSIONS: List[str] = field(default_factory=lambda: [
        # Documents
        '.txt', '.md', '.pdf', '.doc', '.docx',
        '.xls', '.xlsx', '.ppt', '.pptx',
        # Code
        '.py', '.js', '.jsx', '.ts', '.tsx',
        '.html', '.css', '.java', '.cpp', '.c',
        # Data
        '.json', '.xml', '.csv', '.yaml', '.yml',
        # Images (metadata only)
        '.jpg', '.jpeg', '.png', '.gif', '.svg'
    ])
    
    MAX_FILE_SIZE_MB: int = 50
    
    # Performance
    BATCH_SIZE: int = 100
    MAX_WORKERS: int = 4
    ENABLE_CACHE: bool = True
    
    def __post_init__(self):
        """Initialize paths after instance creation"""
        self.DATA_DIR = self.BASE_DIR / "data"
        self.CHROMA_DIR = self.DATA_DIR / "chroma_db"
        self.CACHE_DIR = self.DATA_DIR / "cache"
        
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.CHROMA_DIR.mkdir(exist_ok=True)
        self.CACHE_DIR.mkdir(exist_ok=True)
    
    def is_file_supported(self, file_path: Path) -> bool:
        """Check if file type is supported for indexing"""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def is_file_excluded(self, file_path: Path) -> bool:
        """Check if file should be excluded from indexing"""
        # Check extension
        if file_path.suffix.lower() in self.EXCLUDED_EXTENSIONS:
            return True
        
        # Check if in excluded folder
        parts = file_path.parts
        for excluded in self.EXCLUDED_FOLDERS:
            if excluded in parts:
                return True
        
        return False
    
    def is_file_too_large(self, file_path: Path) -> bool:
        """Check if file exceeds size limit"""
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            return size_mb > self.MAX_FILE_SIZE_MB
        except OSError:
            return True  # If we can't read size, exclude it

# Global config instance
config = Config()

if __name__ == "__main__":
    # Test configuration
    print(f"{config.APP_NAME} v{config.VERSION}")
    print(f"Data directory: {config.DATA_DIR}")
    print(f"Supported extensions: {len(config.SUPPORTED_EXTENSIONS)}")
    print(f"Excluded folders: {config.EXCLUDED_FOLDERS}")