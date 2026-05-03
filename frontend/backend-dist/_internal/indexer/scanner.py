"""
File scanner module - handles directory traversal and file discovery
"""
import os
from pathlib import Path
from typing import Generator, List, Set
from dataclasses import dataclass
from datetime import datetime

from utils.logger import setup_logger
from config import config

logger = setup_logger('scanner')

@dataclass
class FileInfo:
    """Basic file information"""
    path: Path
    name: str
    extension: str
    size_bytes: int
    modified_time: datetime
    created_time: datetime
    
    def __post_init__(self):
        """Calculate additional properties"""
        self.size_mb = self.size_bytes / (1024 * 1024)
        self.size_readable = self._format_size(self.size_bytes)
    
    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'path': str(self.path),
            'name': self.name,
            'extension': self.extension,
            'size_bytes': self.size_bytes,
            'size_mb': self.size_mb,
            'size_readable': self.size_readable,
            'modified_time': self.modified_time.isoformat(),
            'created_time': self.created_time.isoformat()
        }

class FileScanner:
    """Scans directories and discovers files for indexing"""
    
    def __init__(self):
        self.files_found = 0
        self.files_skipped = 0
        self.errors = 0
        self.excluded_folders: Set[str] = set(config.EXCLUDED_FOLDERS)
        self.excluded_extensions: Set[str] = set(config.EXCLUDED_EXTENSIONS)
        self.supported_extensions: Set[str] = set(config.SUPPORTED_EXTENSIONS)
    
    def scan_directory(
        self,
        root_path: str | Path,
        recursive: bool = True
    ) -> Generator[FileInfo, None, None]:
        """
        Scan directory and yield FileInfo objects
        
        Args:
            root_path: Directory path to scan
            recursive: Whether to scan subdirectories
            
        Yields:
            FileInfo objects for each valid file
        """
        root_path = Path(root_path)
        
        if not root_path.exists():
            logger.error(f"Path does not exist: {root_path}")
            return
        
        if not root_path.is_dir():
            logger.error(f"Path is not a directory: {root_path}")
            return
        
        logger.info(f"Starting scan: {root_path}")
        logger.info(f"Recursive: {recursive}")
        
        # Use os.walk for efficient traversal
        for dirpath, dirnames, filenames in os.walk(root_path):
            current_dir = Path(dirpath)
            
            # Filter out excluded directories (modifies dirnames in-place)
            dirnames[:] = [
                d for d in dirnames 
                if not self._is_directory_excluded(d)
            ]
            
            # Process files in current directory
            for filename in filenames:
                file_path = current_dir / filename
                
                # Try to get file info
                file_info = self._get_file_info(file_path)
                
                if file_info:
                    self.files_found += 1
                    yield file_info
                else:
                    self.files_skipped += 1
            
            # Stop if not recursive
            if not recursive:
                break
        
        # Log summary
        logger.info(f"Scan complete: {self.files_found} files found, "
                   f"{self.files_skipped} skipped, {self.errors} errors")
    
    def _get_file_info(self, file_path: Path) -> FileInfo | None:
        """
        Extract file information
        
        Args:
            file_path: Path to file
            
        Returns:
            FileInfo object or None if file should be skipped
        """
        try:
            # Check if file should be excluded
            if self._should_exclude_file(file_path):
                return None
            
            # Get file stats
            stat = file_path.stat()
            
            # Check file size
            if stat.st_size > config.MAX_FILE_SIZE_MB * 1024 * 1024:
                logger.debug(f"File too large, skipping: {file_path.name}")
                return None
            
            # Create FileInfo object
            return FileInfo(
                path=file_path,
                name=file_path.name,
                extension=file_path.suffix.lower(),
                size_bytes=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                created_time=datetime.fromtimestamp(stat.st_ctime)
            )
            
        except PermissionError:
            logger.debug(f"Permission denied: {file_path}")
            self.errors += 1
            return None
        except Exception as e:
            logger.debug(f"Error reading {file_path}: {e}")
            self.errors += 1
            return None
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from indexing"""
        # Check extension
        ext = file_path.suffix.lower()
        
        # Explicitly excluded
        if ext in self.excluded_extensions:
            return True
        
        # Not in supported list (and list is not empty)
        if self.supported_extensions and ext not in self.supported_extensions:
            return True
        
        # Hidden files (starts with .)
        if file_path.name.startswith('.'):
            return True
        
        return False
    
    def _is_directory_excluded(self, dirname: str) -> bool:
        """Check if directory should be excluded"""
        # Check against excluded folders
        if dirname in self.excluded_folders:
            return True
        
        # Hidden directories (start with .)
        if dirname.startswith('.'):
            return True
        
        return False
    
    def get_stats(self) -> dict:
        """Get scanning statistics"""
        return {
            'files_found': self.files_found,
            'files_skipped': self.files_skipped,
            'errors': self.errors
        }
    
    def reset_stats(self):
        """Reset scanning statistics"""
        self.files_found = 0
        self.files_skipped = 0
        self.errors = 0

# Convenience function
def scan_directory(path: str | Path, recursive: bool = True) -> List[FileInfo]:
    """
    Scan directory and return list of FileInfo objects
    
    Args:
        path: Directory to scan
        recursive: Whether to scan subdirectories
        
    Returns:
        List of FileInfo objects
    """
    scanner = FileScanner()
    return list(scanner.scan_directory(path, recursive))

if __name__ == "__main__":
    # Test scanner
    import sys
    
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
    else:
        # Default: scan current directory
        test_path = "."
    
    print(f"\n{'='*60}")
    print(f"Testing File Scanner")
    print(f"{'='*60}\n")
    
    scanner = FileScanner()
    files = list(scanner.scan_directory(test_path))
    
    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"{'='*60}")
    print(f"Files found: {len(files)}")
    
    if files:
        print(f"\nFirst 5 files:")
        for file_info in files[:5]:
            print(f"  - {file_info.name} ({file_info.size_readable})")
    
    stats = scanner.get_stats()
    print(f"\nStatistics:")
    print(f"  Found: {stats['files_found']}")
    print(f"  Skipped: {stats['files_skipped']}")
    print(f"  Errors: {stats['errors']}")