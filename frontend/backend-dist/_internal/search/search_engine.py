"""
Search engine - combines traditional and semantic search
"""
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from utils.logger import setup_logger
from config import config
from indexer.database import FileDatabase
from indexer.vector_store import VectorStore

logger = setup_logger('search')

@dataclass
class SearchResult:
    """Single search result"""
    path: str
    name: str
    extension: str
    size_mb: float
    modified_time: str
    relevance_score: float
    match_type: str  # 'semantic', 'keyword', or 'hybrid'
    preview: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'path': self.path,
            'name': self.name,
            'extension': self.extension,
            'size_mb': self.size_mb,
            'modified_time': self.modified_time,
            'relevance_score': self.relevance_score,
            'match_type': self.match_type,
            'preview': self.preview
        }

class SearchEngine:
    """Main search engine combining multiple search strategies"""
    
    def __init__(self):
        self.database = FileDatabase()
        self.vector_store = VectorStore()
        logger.info("Search engine initialized")
    
    def search(
        self,
        query: str,
        max_results: int = None,
        file_type: Optional[str] = None,
        search_type: str = 'hybrid'
    ) -> List[SearchResult]:
        """
        Search for files
        
        Args:
            query: Search query
            max_results: Maximum number of results
            file_type: Filter by file extension (e.g., '.pdf')
            search_type: 'semantic', 'keyword', or 'hybrid'
            
        Returns:
            List of SearchResult objects
        """
        if max_results is None:
            max_results = config.MAX_SEARCH_RESULTS
        
        logger.info(f"Searching: '{query}' (type: {search_type})")
        
        results = []
        
        if search_type in ['semantic', 'hybrid']:
            # Semantic search using vector store
            semantic_results = self._semantic_search(query, max_results, file_type)
            results.extend(semantic_results)
        
        if search_type in ['keyword', 'hybrid']:
            # Keyword search using database
            keyword_results = self._keyword_search(query, max_results, file_type)
            results.extend(keyword_results)
        
        # Merge and rank results
        merged_results = self._merge_results(results)
        
        # Limit to max results
        final_results = merged_results[:max_results]
        
        logger.info(f"Found {len(final_results)} results")
        
        return final_results
    
    def _semantic_search(
        self,
        query: str,
        max_results: int,
        file_type: Optional[str]
    ) -> List[SearchResult]:
        """Perform semantic search using embeddings"""
        # Build metadata filter
        filter_metadata = {}
        if file_type:
            filter_metadata['extension'] = file_type
        
        # Search vector store
        vector_results = self.vector_store.search(
            query,
            n_results=max_results,
            filter_metadata=filter_metadata if filter_metadata else None
        )
        
        # Convert to SearchResult objects
        search_results = []
        for result in vector_results:
            metadata = result['metadata']
            search_results.append(SearchResult(
                path=result['path'],
                name=metadata.get('name', 'Unknown'),
                extension=metadata.get('extension', ''),
                size_mb=metadata.get('size_mb', 0),
                modified_time=metadata.get('modified_time', ''),
                relevance_score=result.get('similarity', 0),
                match_type='semantic',
                preview=result.get('document', '')[:200]
            ))
        
        return search_results
    
    def _keyword_search(
        self,
        query: str,
        max_results: int,
        file_type: Optional[str]
    ) -> List[SearchResult]:
        """Perform traditional keyword search"""
        # Search database
        db_results = self.database.search_by_name(query, limit=max_results)
        
        # Filter by file type if specified
        if file_type:
            db_results = [r for r in db_results if r['extension'] == file_type]
        
        # Convert to SearchResult objects
        search_results = []
        for result in db_results:
            search_results.append(SearchResult(
                path=result['path'],
                name=result['name'],
                extension=result['extension'],
                size_mb=result['size_mb'],
                modified_time=result['modified_time'],
                relevance_score=0.7,  # Fixed score for keyword matches
                match_type='keyword',
                preview=result.get('content_preview', '')[:200]
            ))
        
        return search_results
    
    def _merge_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Merge and deduplicate results, keeping highest scores
        
        Args:
            results: List of SearchResult objects
            
        Returns:
            Merged and sorted list
        """
        # Group by path
        results_by_path = {}
        
        for result in results:
            path = result.path
            
            if path not in results_by_path:
                results_by_path[path] = result
            else:
                # Keep result with higher score
                existing = results_by_path[path]
                if result.relevance_score > existing.relevance_score:
                    results_by_path[path] = result
                    # Mark as hybrid if from different sources
                    if existing.match_type != result.match_type:
                        results_by_path[path].match_type = 'hybrid'
        
        # Sort by relevance score
        merged = list(results_by_path.values())
        merged.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return merged
    
    def get_file_by_path(self, path: str) -> Optional[Dict]:
        """Get file details by path"""
        return self.database.get_file(path)
    
    def get_statistics(self) -> Dict:
        """Get search engine statistics"""
        db_stats = self.database.get_statistics()
        vector_count = self.vector_store.get_count()
        
        return {
            'total_files_indexed': db_stats.get('total_files', 0),
            'total_vectors': vector_count,
            'total_size_gb': db_stats.get('total_size_gb', 0),
            'file_types': db_stats.get('by_extension', [])
        }

if __name__ == "__main__":
    # Test search engine
    print(f"\n{'='*60}")
    print(f"Testing Search Engine")
    print(f"{'='*60}\n")
    
    search_engine = SearchEngine()
    
    # Show statistics
    stats = search_engine.get_statistics()
    print(f"Files indexed: {stats['total_files_indexed']}")
    print(f"Vectors stored: {stats['total_vectors']}")
    print(f"Total size: {stats['total_size_gb']:.2f} GB")
    
    # Test searches
    test_queries = [
        "python code",
        "report",
        "data analysis"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print(f"{'='*60}")
        
        results = search_engine.search(query, max_results=5)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.name}")
                print(f"   Path: {result.path}")
                print(f"   Score: {result.relevance_score:.2f} ({result.match_type})")
                print()
        else:
            print("No results found\n")