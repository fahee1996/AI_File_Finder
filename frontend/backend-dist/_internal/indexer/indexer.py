"""
Main indexer module - coordinates scanning, extraction, and storage
"""
from indexer.vector_store import VectorStore
import hashlib
from pathlib import Path
from typing import List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
import time

from utils.logger import setup_logger
from config import config
from indexer.scanner import FileScanner, FileInfo
from indexer.extractor import ContentExtractor
from indexer.database import FileDatabase

logger = setup_logger('indexer')

@dataclass
class IndexingProgress:
    """Progress information for indexing"""
    total_files: int = 0
    processed_files: int = 0
    successful: int = 0
    skipped: int = 0
    failed: int = 0
    current_file: str = ""
    started_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    @property
    def elapsed_seconds(self) -> float:
        """Calculate elapsed time"""
        if not self.started_at:
            return 0.0
        return (datetime.now() - self.started_at).total_seconds()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'successful': self.successful,
            'skipped': self.skipped,
            'failed': self.failed,
            'progress_percent': self.progress_percent,
            'elapsed_seconds': self.elapsed_seconds,
            'current_file': self.current_file
        }

class FileIndexer:
    """Main file indexing coordinator"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.scanner = FileScanner()
        self.extractor = ContentExtractor()
        self.database = FileDatabase(db_path)
        self.vector_store = VectorStore()  # ADD THIS LINE
        self.progress = IndexingProgress()
        self.is_running = False
        self.progress_callback: Optional[Callable] = None
    
    def _generate_file_id(self, file_path: str) -> str:
        return hashlib.md5(file_path.encode()).hexdigest()
    
    def index_directory(
        self,
        root_path: str | Path,
        recursive: bool = True,
        force_reindex: bool = False,
        progress_callback: Optional[Callable[[IndexingProgress], None]] = None
    ) -> IndexingProgress:
        """
        Index all files in a directory
        
        Args:
            root_path: Directory path to index
            recursive: Whether to index subdirectories
            force_reindex: Re-index files even if already indexed
            progress_callback: Optional callback for progress updates
            
        Returns:
            IndexingProgress object with results
        """
        root_path = Path(root_path)
        self.is_running = True
        self.progress_callback = progress_callback
        
        logger.info(f"Starting indexing: {root_path}")
        logger.info(f"Recursive: {recursive}, Force reindex: {force_reindex}")
        
        # Reset progress
        self.progress = IndexingProgress(started_at=datetime.now())
        
        try:
            # First pass: count files
            logger.info("Counting files...")
            file_list = list(self.scanner.scan_directory(root_path, recursive))
            self.progress.total_files = len(file_list)
            
            logger.info(f"Found {self.progress.total_files} files to process")
            
            if self.progress.total_files == 0:
                logger.warning("No files found to index")
                return self.progress
            
            # Second pass: index files
            batch_data = []
            batch_size = config.BATCH_SIZE
            
            for i, file_info in enumerate(file_list):
                if not self.is_running:
                    logger.info("Indexing cancelled by user")
                    break
                
                self.progress.current_file = file_info.name
                self.progress.processed_files = i + 1
                
                # Check if needs indexing
                if not force_reindex:
                    if not self.database.needs_reindex(
                        str(file_info.path),
                        file_info.modified_time
                    ):
                        self.progress.skipped += 1
                        self._update_progress()
                        continue
                
                # Extract content
                # Extract content
                try:
                    searchable_text = self.extractor.get_searchable_text(
                        file_info.path,
                        file_info.name
                    )
                    
                    # Add to vector store
                    file_id = self._generate_file_id(str(file_info.path))
                    self.vector_store.add_file(
                        file_id=file_id,
                        file_path=str(file_info.path),
                        searchable_text=searchable_text,
                        metadata={
                            'name': file_info.name,
                            'extension': file_info.extension,
                            'size_mb': file_info.size_mb,
                            'modified_time': file_info.modified_time.isoformat()
                        }
                    )
                    
                    # Prepare data for batch insert
                    batch_data.append((
                        str(file_info.path),
                        file_info.name,
                        file_info.extension,
                        file_info.size_bytes,
                        file_info.size_mb,
                        file_info.modified_time.isoformat(),
                        file_info.created_time.isoformat(),
                        datetime.now().isoformat(),
                        searchable_text[:config.CONTENT_PREVIEW_LENGTH],
                        1  # is_indexed
                    ))
                    
                    self.progress.successful += 1
                    
                except Exception as e:
                    logger.error(f"Error indexing {file_info.name}: {e}")
                    self.progress.failed += 1
                
                # Update progress
                self._update_progress()
            
            # Insert remaining batch
            if batch_data:
                self._insert_batch(batch_data)
            
            # Log completion
            elapsed = self.progress.elapsed_seconds
            logger.info(f"Indexing complete in {elapsed:.2f}s")
            logger.info(f"Successful: {self.progress.successful}")
            logger.info(f"Skipped: {self.progress.skipped}")
            logger.info(f"Failed: {self.progress.failed}")
            
            return self.progress
            
        except Exception as e:
            logger.error(f"Indexing error: {e}", exc_info=True)
            raise
        finally:
            self.is_running = False
    
    def _insert_batch(self, batch_data: List[tuple]):
        """Insert a batch of files into database"""
        count = self.database.add_files_batch(batch_data)
        logger.debug(f"Inserted batch of {count} files")
    
    def _update_progress(self):
        """Update progress and call callback if set"""
        if self.progress_callback:
            self.progress_callback(self.progress)
    
    def stop_indexing(self):
        """Stop the indexing process"""
        logger.info("Stopping indexing...")
        self.is_running = False
    
    def index_single_file(self, file_path: str | Path) -> bool:
        """
        Index a single file
        
        Args:
            file_path: Path to file
            
        Returns:
            True if successful
        """
        file_path = Path(file_path)
        
        if not file_path.exists() or not file_path.is_file():
            logger.error(f"File does not exist: {file_path}")
            return False
        
        try:
            # Get file info
            scanner = FileScanner()
            file_info = scanner._get_file_info(file_path)
            
            if not file_info:
                logger.warning(f"File excluded from indexing: {file_path}")
                return False
            
            # Extract content
            searchable_text = self.extractor.get_searchable_text(
                file_info.path,
                file_info.name
            )
            
            # Add to database
            success = self.database.add_file(file_info, searchable_text)
            
            if success:
                logger.info(f"Successfully indexed: {file_info.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error indexing single file: {e}")
            return False
    
    def get_indexed_count(self) -> int:
        """Get total number of indexed files"""
        stats = self.database.get_statistics()
        return stats.get('total_files', 0)
    
    def get_statistics(self) -> dict:
        """Get indexing statistics"""
        return self.database.get_statistics()

# Convenience functions
def index_directory(path: str | Path, recursive: bool = True) -> IndexingProgress:
    """Index a directory"""
    indexer = FileIndexer()
    return indexer.index_directory(path, recursive)

def index_file(path: str | Path) -> bool:
    """Index a single file"""
    indexer = FileIndexer()
    return indexer.index_single_file(path)

if __name__ == "__main__":
    # Test indexer
    import sys
    
    print(f"\n{'='*60}")
    print(f"AI File Finder - Indexer Test")
    print(f"{'='*60}\n")
    
    # Get path from command line or use current directory
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
    else:
        test_path = "."
    
    # Progress callback
    def show_progress(progress: IndexingProgress):
        """Display progress"""
        if progress.processed_files % 10 == 0:  # Update every 10 files
            print(f"Progress: {progress.progress_percent:.1f}% "
                  f"({progress.processed_files}/{progress.total_files}) "
                  f"- {progress.current_file}")
    
    # Create indexer
    indexer = FileIndexer()
    
    print(f"Indexing: {test_path}\n")
    
    # Index directory
    result = indexer.index_directory(
        test_path,
        recursive=True,
        progress_callback=show_progress
    )
    
    # Show results
    print(f"\n{'='*60}")
    print(f"Indexing Results:")
    print(f"{'='*60}")
    print(f"Total files: {result.total_files}")
    print(f"Successful: {result.successful}")
    print(f"Skipped: {result.skipped}")
    print(f"Failed: {result.failed}")
    print(f"Time taken: {result.elapsed_seconds:.2f}s")
    
    # Show statistics
    print(f"\n{'='*60}")
    print(f"Database Statistics:")
    print(f"{'='*60}")
    
    stats = indexer.get_statistics()
    print(f"Total files in DB: {stats.get('total_files', 0)}")
    print(f"Total size: {stats.get('total_size_gb', 0):.2f} GB")
    
    print(f"\nTop file types:")
    for ext_data in stats.get('by_extension', [])[:5]:
        print(f"  {ext_data['extension']}: {ext_data['count']} files")