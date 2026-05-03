"""
Simple API server for frontend communication
This will be replaced with Tauri commands later
"""
from typing import Dict, Any, List
from llm.assistant import FileFinderAssistant
from search.search_engine import SearchEngine
from indexer.indexer import FileIndexer, IndexingProgress
from operations.file_operations import FileOperations
from utils.logger import setup_logger

logger = setup_logger('api')

class FileFinderAPI:
    """API interface for the file finder"""
    
    def __init__(self):
        self.assistant = FileFinderAssistant()
        self.search_engine = SearchEngine()
        self.indexer = FileIndexer()
        self.file_ops = FileOperations()
        
        logger.info("API initialized")
    
    # ===== Chat / Assistant Methods =====
    
    def chat(self, message: str) -> Dict[str, Any]:
        """
        Send message to assistant
        
        Args:
            message: User message
            
        Returns:
            Response dict with message and metadata
        """
        try:
            response = self.assistant.process_message(message)
            
            return {
                'success': True,
                'response': response,
                'results': [r.to_dict() for r in self.assistant.context.last_results] if self.assistant.context.last_results else [],
                'intent': self.assistant.context.last_intent.to_dict() if self.assistant.context.last_intent else None
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def clear_context(self) -> Dict[str, Any]:
        """Clear conversation context"""
        self.assistant.clear_context()
        return {'success': True, 'message': 'Context cleared'}
    
    # ===== Search Methods =====
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        file_type: str = None
    ) -> Dict[str, Any]:
        """
        Search for files
        
        Args:
            query: Search query
            max_results: Maximum results
            file_type: Optional file type filter
            
        Returns:
            Search results
        """
        try:
            results = self.search_engine.search(
                query,
                max_results=max_results,
                file_type=file_type
            )
            
            return {
                'success': True,
                'results': [r.to_dict() for r in results],
                'count': len(results)
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    # ===== Indexing Methods =====
    
    def start_indexing(
        self,
        path: str,
        recursive: bool = True,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Start indexing a directory
        
        Args:
            path: Directory path
            recursive: Whether to index subdirectories
            force: Force re-index
            
        Returns:
            Indexing result
        """
        try:
            result = self.indexer.index_directory(path, recursive, force)
            
            return {
                'success': True,
                'result': result.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Indexing error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_indexing_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        try:
            stats = self.search_engine.get_statistics()
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Stats error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    # ===== File Operation Methods =====
    
    def open_file(self, file_path: str) -> Dict[str, Any]:
        """Open file"""
        success, message = self.file_ops.open_file(file_path)
        return {'success': success, 'message': message}
    
    def show_in_folder(self, file_path: str) -> Dict[str, Any]:
        """Show file in folder"""
        success, message = self.file_ops.show_in_folder(file_path)
        return {'success': success, 'message': message}
    
    def copy_path(self, file_path: str) -> Dict[str, Any]:
        """Copy file path to clipboard"""
        success, message = self.file_ops.copy_path_to_clipboard(file_path)
        return {'success': success, 'message': message}
    
    def move_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """Move file"""
        success, message = self.file_ops.move_file(source, destination, overwrite)
        return {'success': success, 'message': message}
    
    def rename_file(self, file_path: str, new_name: str) -> Dict[str, Any]:
        """Rename file"""
        success, message = self.file_ops.rename_file(file_path, new_name)
        return {'success': success, 'message': message}
    
    def delete_file(self, file_path: str, permanent: bool = False) -> Dict[str, Any]:
        """Delete file"""
        success, message = self.file_ops.delete_file(file_path, permanent)
        return {'success': success, 'message': message}

if __name__ == "__main__":
    # Test API
    print("\n" + "="*70)
    print("Testing File Finder API")
    print("="*70 + "\n")
    
    api = FileFinderAPI()
    
    # Test stats
    print("1. Getting statistics...")
    result = api.get_indexing_stats()
    if result['success']:
        stats = result['stats']
        print(f"   Files indexed: {stats.get('total_files_indexed', 0):,}")
        print(f"   Total size: {stats.get('total_size_gb', 0):.2f} GB")
        print("   ✓ Success\n")
    
    # Test search
    print("2. Testing search...")
    result = api.search("python", max_results=5)
    if result['success']:
        print(f"   Found: {result['count']} results")
        if result['results']:
            print(f"   Top result: {result['results'][0]['name']}")
        print("   ✓ Success\n")
    
    # Test chat
    print("3. Testing chat...")
    result = api.chat("What files do I have?")
    if result['success']:
        print(f"   Response: {result['response'][:100]}...")
        print("   ✓ Success\n")
    
    print("API test complete!")