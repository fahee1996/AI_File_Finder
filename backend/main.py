"""
AI File Finder - Main Application Entry Point
"""
from utils.logger import setup_logger
from config import config
import ollama
import sys

# Set up logger
logger = setup_logger('main', 'main', level=20)  # 20 = INFO

def check_ollama():
    """Verify Ollama is running and model is available"""
    logger.info("Checking Ollama connection...")
    
    try:
        # Try to list models
        models = ollama.list()
        available_models = models.get('models', [])
        logger.info(f"✓ Ollama connected. Found {len(available_models)} model(s)")
        
        # Check if our model exists
        model_names = [m['name'] for m in available_models]
        model_found = any(config.LLM_MODEL in name for name in model_names)
        
        if not model_found:
            logger.warning(f"Model '{config.LLM_MODEL}' not found")
            logger.info(f"Downloading {config.LLM_MODEL}... (this may take a few minutes)")
            
            ollama.pull(config.LLM_MODEL)
            logger.info(f"✓ Model '{config.LLM_MODEL}' downloaded successfully")
        else:
            logger.info(f"✓ Model '{config.LLM_MODEL}' is available")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to connect to Ollama: {e}")
        logger.error("Make sure Ollama is running (check system tray/menu bar)")
        logger.error("You can start it with: ollama serve")
        return False

def check_dependencies():
    """Verify all required dependencies"""
    logger.info("=" * 60)
    logger.info(f"Starting {config.APP_NAME} v{config.VERSION}")
    logger.info("=" * 60)
    
    logger.info(f"Data directory: {config.DATA_DIR}")
    logger.info(f"Vector DB: {config.CHROMA_DIR}")
    
    # Check Ollama
    if not check_ollama():
        return False
    
    # Check ChromaDB
    try:
        import chromadb
        client = chromadb.Client()
        logger.info("✓ ChromaDB initialized")
    except Exception as e:
        logger.error(f"✗ ChromaDB error: {e}")
        return False
    
    # Check embeddings model
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        model = SentenceTransformer(config.EMBEDDING_MODEL)
        logger.info("✓ Embedding model loaded")
    except Exception as e:
        logger.error(f"✗ Embedding model error: {e}")
        return False
    
    logger.info("=" * 60)
    logger.info("✓ All dependencies verified successfully!")
    logger.info("=" * 60)
    
    return True

def main():
    """Main application entry point"""
    try:
        # Check dependencies
        if not check_dependencies():
            logger.error("Dependency check failed. Please fix errors and try again.")
            sys.exit(1)
        
        logger.info("\n🚀 Backend is ready!")
        logger.info("Next steps:")
        logger.info("  - Implement file indexer (Week 2)")
        logger.info("  - Build search engine (Week 3)")
        logger.info("  - Create frontend UI (Week 4)")
        
        # TODO: Start file indexing service
        # TODO: Start search API server
        # TODO: Connect to frontend IPC
        
    except KeyboardInterrupt:
        logger.info("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()