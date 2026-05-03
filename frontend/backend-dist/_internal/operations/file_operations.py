"""
File operations module - handles opening, moving, copying files
"""
import os
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Optional, Tuple
import pyperclip

from utils.logger import setup_logger

logger = setup_logger('file_operations')

class FileOperations:
    """Handles file system operations"""
    
    def __init__(self):
        self.system = platform.system()
        logger.info(f"File operations initialized for {self.system}")
    
    def open_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Open file with default application
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (success, message)
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return False, f"File not found: {file_path}"
        
        if not path.is_file():
            logger.error(f"Not a file: {file_path}")
            return False, f"Not a file: {file_path}"
        
        try:
            if self.system == "Windows":
                os.startfile(str(path))
            elif self.system == "Darwin":  # macOS
                subprocess.run(["open", str(path)], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(path)], check=True)
            
            logger.info(f"Opened file: {path.name}")
            return True, f"Opened {path.name}"
            
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return False, f"Error opening file: {str(e)}"
    
    def show_in_folder(self, file_path: str) -> Tuple[bool, str]:
        """
        Show file in folder/Finder/Explorer
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (success, message)
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return False, f"File not found: {file_path}"
        
        try:
            if self.system == "Windows":
                subprocess.run(["explorer", "/select,", str(path)], check=True)
            elif self.system == "Darwin":  # macOS
                subprocess.run(["open", "-R", str(path)], check=True)
            else:  # Linux
                # Open parent folder
                subprocess.run(["xdg-open", str(path.parent)], check=True)
            
            logger.info(f"Showed file in folder: {path.name}")
            return True, f"Opened folder containing {path.name}"
            
        except Exception as e:
            logger.error(f"Error showing file in folder: {e}")
            return False, f"Error: {str(e)}"
    
    def copy_path_to_clipboard(self, file_path: str) -> Tuple[bool, str]:
        """
        Copy file path to clipboard
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (success, message)
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return False, f"File not found: {file_path}"
        
        try:
            pyperclip.copy(str(path))
            logger.info(f"Copied path to clipboard: {file_path}")
            return True, f"Copied path to clipboard"
            
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
            return False, f"Error: {str(e)}"
    
    def move_file(
        self,
        source_path: str,
        destination: str,
        overwrite: bool = False
    ) -> Tuple[bool, str]:
        """
        Move file to destination
        
        Args:
            source_path: Source file path
            destination: Destination folder or full path
            overwrite: Whether to overwrite if file exists
            
        Returns:
            Tuple of (success, message)
        """
        source = Path(source_path)
        dest = Path(destination)
        
        if not source.exists():
            logger.error(f"Source file not found: {source_path}")
            return False, f"File not found: {source_path}"
        
        try:
            # If destination is a directory, append filename
            if dest.is_dir():
                dest = dest / source.name
            
            # Check if destination exists
            if dest.exists() and not overwrite:
                return False, f"File already exists at destination: {dest}"
            
            # Move file
            shutil.move(str(source), str(dest))
            
            logger.info(f"Moved {source.name} to {dest}")
            return True, f"Moved {source.name} to {dest.parent.name}"
            
        except Exception as e:
            logger.error(f"Error moving file: {e}")
            return False, f"Error moving file: {str(e)}"
    
    def copy_file(
        self,
        source_path: str,
        destination: str,
        overwrite: bool = False
    ) -> Tuple[bool, str]:
        """
        Copy file to destination
        
        Args:
            source_path: Source file path
            destination: Destination folder or full path
            overwrite: Whether to overwrite if file exists
            
        Returns:
            Tuple of (success, message)
        """
        source = Path(source_path)
        dest = Path(destination)
        
        if not source.exists():
            logger.error(f"Source file not found: {source_path}")
            return False, f"File not found: {source_path}"
        
        try:
            # If destination is a directory, append filename
            if dest.is_dir():
                dest = dest / source.name
            
            # Check if destination exists
            if dest.exists() and not overwrite:
                return False, f"File already exists at destination: {dest}"
            
            # Copy file
            shutil.copy2(str(source), str(dest))
            
            logger.info(f"Copied {source.name} to {dest}")
            return True, f"Copied {source.name} to {dest.parent.name}"
            
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            return False, f"Error copying file: {str(e)}"
    
    def rename_file(
        self,
        file_path: str,
        new_name: str
    ) -> Tuple[bool, str]:
        """
        Rename file
        
        Args:
            file_path: Path to file
            new_name: New filename
            
        Returns:
            Tuple of (success, message)
        """
        source = Path(file_path)
        
        if not source.exists():
            logger.error(f"File not found: {file_path}")
            return False, f"File not found: {file_path}"
        
        try:
            # Create new path with same parent
            dest = source.parent / new_name
            
            # Check if destination exists
            if dest.exists():
                return False, f"A file named '{new_name}' already exists"
            
            # Rename
            source.rename(dest)
            
            logger.info(f"Renamed {source.name} to {new_name}")
            return True, f"Renamed to {new_name}"
            
        except Exception as e:
            logger.error(f"Error renaming file: {e}")
            return False, f"Error renaming file: {str(e)}"
    
    def delete_file(self, file_path: str, permanent: bool = False) -> Tuple[bool, str]:
        """
        Delete file (move to trash or permanent delete)
        
        Args:
            file_path: Path to file
            permanent: If True, permanently delete. If False, move to trash
            
        Returns:
            Tuple of (success, message)
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return False, f"File not found: {file_path}"
        
        try:
            if permanent:
                # Permanent delete
                path.unlink()
                logger.warning(f"Permanently deleted: {path.name}")
                return True, f"Permanently deleted {path.name}"
            else:
                # Move to trash
                try:
                    from send2trash import send2trash
                    send2trash(str(path))
                    logger.info(f"Moved to trash: {path.name}")
                    return True, f"Moved {path.name} to trash"
                except ImportError:
                    logger.warning("send2trash not installed, performing permanent delete")
                    path.unlink()
                    return True, f"Deleted {path.name}"
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False, f"Error deleting file: {str(e)}"
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get detailed file information
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info or None
        """
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        try:
            stat = path.stat()
            
            return {
                'name': path.name,
                'path': str(path),
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'extension': path.suffix,
                'parent': str(path.parent),
                'is_file': path.is_file(),
                'is_dir': path.is_dir()
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None

if __name__ == "__main__":
    # Test file operations
    print("\n" + "="*70)
    print("Testing File Operations")
    print("="*70 + "\n")
    
    ops = FileOperations()
    
    # Create a test file
    test_file = Path("test_file_ops.txt")
    test_file.write_text("This is a test file for file operations.")
    print(f"✓ Created test file: {test_file.name}\n")
    
    # Test get info
    print("1. Getting file info...")
    info = ops.get_file_info(str(test_file))
    if info:
        print(f"   Name: {info['name']}")
        print(f"   Size: {info['size_mb']:.4f} MB")
        print(f"   Extension: {info['extension']}")
        print("   ✓ Success\n")
    
    # Test copy path
    print("2. Copying path to clipboard...")
    success, msg = ops.copy_path_to_clipboard(str(test_file))
    print(f"   {msg}")
    print(f"   ✓ Success\n" if success else f"   ✗ Failed\n")
    
    # Test show in folder (will actually open)
    print("3. Show in folder...")
    print("   (This will open your file explorer)")
    choice = input("   Press Enter to test, or 's' to skip: ")
    if choice.lower() != 's':
        success, msg = ops.show_in_folder(str(test_file))
        print(f"   {msg}\n")
    else:
        print("   Skipped\n")
    
    # Test open file (will actually open)
    print("4. Open file...")
    print("   (This will open the file in default app)")
    choice = input("   Press Enter to test, or 's' to skip: ")
    if choice.lower() != 's':
        success, msg = ops.open_file(str(test_file))
        print(f"   {msg}\n")
    else:
        print("   Skipped\n")
    
    # Clean up
    print("5. Cleaning up...")
    if test_file.exists():
        test_file.unlink()
        print("   ✓ Test file deleted\n")
    
    print("File operations test complete!")