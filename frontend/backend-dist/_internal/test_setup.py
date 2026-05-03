"""Test script to verify all dependencies are working"""
import chromadb
import ollama
from sentence_transformers import SentenceTransformer

def test_chromadb():
    print("Testing ChromaDB...")
    client = chromadb.Client()
    print("✓ ChromaDB working!")
    return True

def test_ollama():
    print("\nTesting Ollama...")
    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[{'role': 'user', 'content': 'Say "Backend setup complete!"'}]
        )
        print(f"✓ Ollama response: {response['message']['content']}")
        return True
    except Exception as e:
        print(f"✗ Ollama error: {e}")
        print("Make sure Ollama is running!")
        return False

def test_embeddings():
    print("\nTesting Sentence Transformers...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode("test")
    print(f"✓ Generated embedding with {len(embedding)} dimensions")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("AI File Finder - Dependency Check")
    print("=" * 50)
    
    all_passed = True
    all_passed &= test_chromadb()
    all_passed &= test_ollama()
    all_passed &= test_embeddings()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Backend is ready!")
    else:
        print("❌ Some tests failed. Check errors above.")
    print("=" * 50)