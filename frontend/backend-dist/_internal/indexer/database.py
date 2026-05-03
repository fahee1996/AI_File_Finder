"""
Database module - stores file metadata using SQLite
"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from contextlib import contextmanager

from utils.logger import setup_logger
from config import config
from indexer.scanner import FileInfo

logger = setup_logger('database')

class FileDatabase:
    """SQLite database for file metadata"""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = config.DATA_DIR / "files.db"
        
        self.db_path = db_path
        self._init_database()
        logger.info(f"Database initialized: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    extension TEXT,
                    size_bytes INTEGER,
                    size_mb REAL,
                    modified_time TEXT,
                    created_time TEXT,
                    indexed_time TEXT,
                    content_preview TEXT,
                    is_indexed BOOLEAN DEFAULT 0
                )
            """)
            
            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_name ON files(name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_extension ON files(extension)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_modified ON files(modified_time)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_indexed ON files(is_indexed)
            """)
            
            # Create indexing stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS indexing_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT,
                    completed_at TEXT,
                    files_scanned INTEGER,
                    files_indexed INTEGER,
                    files_failed INTEGER,
                    root_path TEXT
                )
            """)
            
            conn.commit()
            logger.debug("Database schema created")
    
    def add_file(self, file_info: FileInfo, content_preview: str = "") -> bool:
        """
        Add or update file in database
        
        Args:
            file_info: FileInfo object
            content_preview: Text preview of file content
            
        Returns:
            True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO files (
                        path, name, extension, size_bytes, size_mb,
                        modified_time, created_time, indexed_time,
                        content_preview, is_indexed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(file_info.path),
                    file_info.name,
                    file_info.extension,
                    file_info.size_bytes,
                    file_info.size_mb,
                    file_info.modified_time.isoformat(),
                    file_info.created_time.isoformat(),
                    datetime.now().isoformat(),
                    content_preview,
                    1  # is_indexed = True
                ))
                
                return True
                
        except Exception as e:
            logger.error(f"Error adding file {file_info.name}: {e}")
            return False
    
    def add_files_batch(self, files_data: List[tuple]) -> int:
        """
        Add multiple files in a batch
        
        Args:
            files_data: List of tuples matching the INSERT statement
            
        Returns:
            Number of files added
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.executemany("""
                    INSERT OR REPLACE INTO files (
                        path, name, extension, size_bytes, size_mb,
                        modified_time, created_time, indexed_time,
                        content_preview, is_indexed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, files_data)
                
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"Error adding files batch: {e}")
            return 0
    
    def get_file(self, path: str) -> Optional[Dict]:
        """Get file by path"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM files WHERE path = ?", (path,))
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Error getting file {path}: {e}")
            return None
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists in database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM files WHERE path = ? LIMIT 1", (path,))
                return cursor.fetchone() is not None
                
        except Exception as e:
            logger.error(f"Error checking file existence: {e}")
            return False
    
    def needs_reindex(self, path: str, modified_time: datetime) -> bool:
        """Check if file needs to be reindexed (modified since last index)"""
        file_data = self.get_file(path)
        
        if not file_data:
            return True  # New file
        
        # Compare modification times
        stored_modified = datetime.fromisoformat(file_data['modified_time'])
        return modified_time > stored_modified
    
    def get_all_files(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all files from database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM files ORDER BY indexed_time DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting all files: {e}")
            return []
    
    def search_by_name(self, query: str, limit: int = 50) -> List[Dict]:
        """Search files by name (simple text search)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM files 
                    WHERE name LIKE ? OR content_preview LIKE ?
                    ORDER BY modified_time DESC
                    LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total files
                cursor.execute("SELECT COUNT(*) as count FROM files")
                total = cursor.fetchone()['count']
                
                # By extension
                cursor.execute("""
                    SELECT extension, COUNT(*) as count 
                    FROM files 
                    GROUP BY extension 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                by_extension = [dict(row) for row in cursor.fetchall()]
                
                # Total size
                cursor.execute("SELECT SUM(size_bytes) as total FROM files")
                total_size = cursor.fetchone()['total'] or 0
                
                return {
                    'total_files': total,
                    'total_size_bytes': total_size,
                    'total_size_gb': total_size / (1024**3),
                    'by_extension': by_extension
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def delete_file(self, path: str) -> bool:
        """Delete file from database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM files WHERE path = ?", (path,))
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def clear_database(self):
        """Clear all files from database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM files")
                logger.info("Database cleared")
                
        except Exception as e:
            logger.error(f"Error clearing database: {e}")

if __name__ == "__main__":
    # Test database
    print(f"\n{'='*60}")
    print(f"Testing File Database")
    print(f"{'='*60}\n")
    
    # Create test database
    test_db_path = config.DATA_DIR / "test_files.db"
    db = FileDatabase(test_db_path)
    
    print(f"Database created at: {test_db_path}")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\nCurrent statistics:")
    print(f"  Total files: {stats.get('total_files', 0)}")
    print(f"  Total size: {stats.get('total_size_gb', 0):.2f} GB")
    
    print("\nDatabase test complete!")