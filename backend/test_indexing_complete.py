"""
Complete test of indexing and search system
"""
from pathlib import Path
from indexer.indexer import FileIndexer, IndexingProgress
from search.search_engine import SearchEngine
from utils.logger import setup_logger

logger = setup_logger('test')

def progress_callback(progress: IndexingProgress):
    """Display indexing progress"""
    if progress.processed_files % 5 == 0:
        logger.info(
            f"Progress: {progress.progress_percent:.1f}% "
            f"({progress.processed_files}/{progress.total_files})"
        )

def main():
    print("\n" + "="*70)
    print(" AI File Finder - Complete Indexing & Search Test")
    print("="*70 + "\n")
    
    # Get test directory
    test_dir = input("Enter directory to index (or press Enter for current): ").strip()
    if not test_dir:
        test_dir = "."
    
    test_path = Path(test_dir)
    if not test_path.exists():
        logger.error(f"Directory does not exist: {test_dir}")
        return
    
    # Step 1: Index files
    print("\n" + "="*70)
    print(" Step 1: Indexing Files")
    print("="*70 + "\n")
    
    indexer = FileIndexer()
    result = indexer.index_directory(
        test_path,
        recursive=True,
        force_reindex=False,
        progress_callback=progress_callback
    )
    
    print(f"\nIndexing Results:")
    print(f"  Total files: {result.total_files}")
    print(f"  Successful: {result.successful}")
    print(f"  Skipped: {result.skipped}")
    print(f"  Failed: {result.failed}")
    print(f"  Time taken: {result.elapsed_seconds:.2f}s")
    
    # Step 2: Show statistics
    print("\n" + "="*70)
    print(" Step 2: Database Statistics")
    print("="*70 + "\n")
    
    stats = indexer.get_statistics()
    print(f"Total files in database: {stats.get('total_files', 0)}")
    print(f"Total size: {stats.get('total_size_gb', 0):.2f} GB")
    
    print("\nTop 10 file types:")
    for ext_data in stats.get('by_extension', [])[:10]:
        print(f"  {ext_data['extension']}: {ext_data['count']} files")
    
    # Step 3: Test search
    print("\n" + "="*70)
    print(" Step 3: Testing Search")
    print("="*70 + "\n")
    
    search_engine = SearchEngine()
    
    # Interactive search
    while True:
        query = input("\nEnter search query (or 'quit' to exit): ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        print(f"\nSearching for: '{query}'")
        print("-" * 70)
        
        # Search
        results = search_engine.search(query, max_results=10)
        
        if results:
            print(f"\nFound {len(results)} results:\n")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.name}")
                print(f"   Path: {result.path}")
                print(f"   Type: {result.extension}")
                print(f"   Size: {result.size_mb:.2f} MB")
                print(f"   Score: {result.relevance_score:.3f} ({result.match_type})")
                
                if result.preview:
                    preview = result.preview[:100].replace('\n', ' ')
                    print(f"   Preview: {preview}...")
                
                print()
        else:
            print("\nNo results found.")
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()