"""
Complete system test - tests all components working together
"""
from api.server import FileFinderAPI
from utils.logger import setup_logger

logger = setup_logger('test_complete')

def main():
    print("\n" + "="*70)
    print(" AI File Finder - Complete System Test")
    print("="*70 + "\n")
    
    # Initialize API
    api = FileFinderAPI()
    
    # Show statistics
    print("System Statistics:")
    print("-" * 70)
    result = api.get_indexing_stats()
    if result['success']:
        stats = result['stats']
        print(f"Files indexed: {stats.get('total_files_indexed', 0):,}")
        print(f"Vectors stored: {stats.get('total_vectors', 0):,}")
        print(f"Total size: {stats.get('total_size_gb', 0):.2f} GB")
    print()
    
    # Interactive chat
    print("="*70)
    print(" Interactive Chat (type 'quit' to exit)")
    print("="*70)
    print()
    print("Try these:")
    print("  - 'find my python files'")
    print("  - 'show me documents from last week'")
    print("  - 'open that report'")
    print("  - 'what files do I have?'")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if user_input.lower() == 'clear':
                api.clear_context()
                print("\n[Context cleared]\n")
                continue
            
            # Send to API
            result = api.chat(user_input)
            
            if result['success']:
                print(f"\nAssistant: {result['response']}\n")
                
                # Show results if any
                if result.get('results'):
                    print(f"Found {len(result['results'])} files:")
                    for i, file in enumerate(result['results'][:5], 1):
                        print(f"  {i}. {file['name']} ({file['size_mb']:.2f} MB)")
                    print()
            else:
                print(f"\nError: {result.get('error')}\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()