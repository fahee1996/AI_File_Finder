"""
Vector store module - manages embeddings in ChromaDB
"""
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

from utils.logger import setup_logger
from config import config

logger = setup_logger('vector_store')

class VectorStore:
    """Manages vector embeddings using ChromaDB"""
    
    def __init__(self, persist_directory: Optional[Path] = None):
        if persist_directory is None:
            persist_directory = config.CHROMA_DIR
        
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB at: {persist_directory}")
        self.client = chromadb.PersistentClient(
            path=str(persist_directory)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="file_contents",
            metadata={"description": "File content embeddings for semantic search"}
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        logger.info("Vector store initialized")
    
    def add_file(
        self,
        file_id: str,
        file_path: str,
        searchable_text: str,
        metadata: Dict
    ) -> bool:
        """
        Add a file to the vector store
        
        Args:
            file_id: Unique identifier for the file
            file_path: Path to the file
            searchable_text: Text to embed and search
            metadata: Additional metadata (name, extension, etc.)
            
        Returns:
            True if successful
        """
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(searchable_text)
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding.tolist()],
                documents=[searchable_text],
                metadatas=[{
                    'path': file_path,
                    **metadata
                }],
                ids=[file_id]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding file to vector store: {e}")
            return False
    
    def add_files_batch(
        self,
        file_ids: List[str],
        file_paths: List[str],
        searchable_texts: List[str],
        metadatas: List[Dict]
    ) -> int:
        """
        Add multiple files in batch
        
        Args:
            file_ids: List of file IDs
            file_paths: List of file paths
            searchable_texts: List of texts to embed
            metadatas: List of metadata dicts
            
        Returns:
            Number of files added
        """
        try:
            # Generate embeddings for all texts
            embeddings = self.embedding_model.encode(searchable_texts)
            
            # Add metadata paths
            full_metadatas = [
                {'path': path, **metadata}
                for path, metadata in zip(file_paths, metadatas)
            ]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=searchable_texts,
                metadatas=full_metadatas,
                ids=file_ids
            )
            
            return len(file_ids)
            
        except Exception as e:
            logger.error(f"Error adding batch to vector store: {e}")
            return 0
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar files using semantic search
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results with metadata and scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'path': results['metadatas'][0][i].get('path'),
                        'metadata': results['metadatas'][0][i],
                        'document': results['documents'][0][i] if results['documents'] else None,
                        'distance': results['distances'][0][i] if results['distances'] else None,
                        'similarity': 1 - results['distances'][0][i] if results['distances'] else None
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def update_file(
        self,
        file_id: str,
        searchable_text: str,
        metadata: Dict
    ) -> bool:
        """Update a file's embedding and metadata"""
        try:
            # Generate new embedding
            embedding = self.embedding_model.encode(searchable_text)
            
            # Update in collection
            self.collection.update(
                embeddings=[embedding.tolist()],
                documents=[searchable_text],
                metadatas=[metadata],
                ids=[file_id]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating file in vector store: {e}")
            return False
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from vector store"""
        try:
            self.collection.delete(ids=[file_id])
            return True
        except Exception as e:
            logger.error(f"Error deleting file from vector store: {e}")
            return False
    
    def get_count(self) -> int:
        """Get total number of vectors in store"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            return 0
    
    def clear(self):
        """Clear all vectors from store"""
        try:
            # Delete collection and recreate
            self.client.delete_collection(name="file_contents")
            self.collection = self.client.get_or_create_collection(
                name="file_contents",
                metadata={"description": "File content embeddings for semantic search"}
            )
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")

if __name__ == "__main__":
    # Test vector store
    print(f"\n{'='*60}")
    print(f"Testing Vector Store")
    print(f"{'='*60}\n")
    
    # Create vector store
    vector_store = VectorStore()
    
    print(f"Vector store initialized")
    print(f"Current count: {vector_store.get_count()}")
    
    # Add test files
    print(f"\nAdding test files...")
    
    test_files = [
        {
            'id': 'test_1',
            'path': '/documents/report.pdf',
            'text': 'Annual sales report for Q4 2024 showing revenue growth',
            'metadata': {'name': 'report.pdf', 'extension': '.pdf'}
        },
        {
            'id': 'test_2',
            'path': '/documents/budget.xlsx',
            'text': 'Budget spreadsheet with financial projections and expenses',
            'metadata': {'name': 'budget.xlsx', 'extension': '.xlsx'}
        },
        {
            'id': 'test_3',
            'path': '/code/main.py',
            'text': 'Python script for file processing and data analysis',
            'metadata': {'name': 'main.py', 'extension': '.py'}
        }
    ]
    
    for file in test_files:
        vector_store.add_file(
            file['id'],
            file['path'],
            file['text'],
            file['metadata']
        )
    
    print(f"Added {len(test_files)} files")
    print(f"New count: {vector_store.get_count()}")
    
    # Test search
    print(f"\n{'='*60}")
    print(f"Testing Search")
    print(f"{'='*60}\n")
    
    test_queries = [
        "financial report",
        "python code",
        "sales data"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = vector_store.search(query, n_results=2)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['metadata']['name']} "
                  f"(similarity: {result['similarity']:.2f})")