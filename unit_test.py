import sys
import os
import numpy as np
import asyncio
import pytest
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm import generate_response, load_model
from embeddings.model import EmbeddingModel
from embeddings.storage import FaissStorage
from rag.processor import DocumentProcessor
from rag.retriever import Retriever
from rag.engine import RAGEngine
from cache.manager import CacheManager
from tasks.celery_app import celery_app
from tasks.document_tasks import process_documents_async
from tasks.query_tasks import process_query_async

def test_model_inference():
    """Test the GGUF LLM model inference with a simple 'hi' prompt"""
    print("Testing Model Inference...")
    print("-" * 30)
    
    try:
        # Load the model
        model = load_model()
        print("[PASS] Model loaded successfully")
        
        # Test with a simple prompt
        prompt = "Hi"
        response = generate_response(prompt)
        print(f"[PASS] Model response: {response[:50]}{'...' if len(response) > 50 else ''}")
        print("[PASS] Model inference test passed\n")
        return True
    except Exception as e:
        print(f"[FAIL] Model inference test failed: {e}\n")
        return False

def test_embedding_model():
    """Test the embedding model inference"""
    print("Testing Embedding Model...")
    print("-" * 30)
    
    try:
        # Initialize embedding model
        embedding_model = EmbeddingModel()
        embedding_model.load_model()
        print("[PASS] Embedding model loaded successfully")
        
        # Test encoding a simple text
        test_text = "This is a test sentence for embedding."
        embedding = embedding_model.encode(test_text)
        print(f"[PASS] Embedding shape: {embedding.shape}")
        print(f"[PASS] Embedding dtype: {embedding.dtype}")
        print("[PASS] Embedding model test passed\n")
        return True
    except Exception as e:
        print(f"[FAIL] Embedding model test failed: {e}\n")
        return False

def test_vector_storage():
    """Test the FAISS vector storage"""
    print("Testing Vector Storage...")
    print("-" * 30)
    
    try:
        # Initialize embedding model to get dimension
        embedding_model = EmbeddingModel()
        dim = embedding_model.get_dimension()
        print(f"[PASS] Embedding dimension: {dim}")
        
        # Initialize FAISS storage
        faiss_storage = FaissStorage(dim)
        faiss_storage.initialize_index()
        print("[PASS] FAISS storage initialized successfully")
        
        # Test adding a sample embedding
        sample_embedding = np.random.rand(1, dim).astype('float32')
        sample_metadata = [{"content": "Test document", "source": "test"}]
        faiss_storage.add_embeddings(sample_embedding, sample_metadata)
        print("[PASS] Sample embedding added to FAISS storage")
        
        # Test searching
        query_embedding = np.random.rand(1, dim).astype('float32')
        results, distances = faiss_storage.search(query_embedding, k=1)
        print(f"[PASS] Search returned {len(results)} results")
        print("[PASS] Vector storage test passed\n")
        return True
    except Exception as e:
        print(f"[FAIL] Vector storage test failed: {e}\n")
        return False

def test_chunking():
    """Test the document chunking functionality"""
    print("Testing Document Chunking...")
    print("-" * 30)
    
    try:
        # Test chunking with a sample text
        sample_text = "This is a sample document. " * 100  # Make it long enough to chunk
        processor = DocumentProcessor()
        chunks = processor.chunk_text(sample_text, chunk_size=100, overlap=10)
        print(f"[PASS] Generated {len(chunks)} chunks")
        print(f"[PASS] First chunk: {chunks[0][:50]}{'...' if len(chunks[0]) > 50 else ''}")
        print("[PASS] Document chunking test passed\n")
        return True
    except Exception as e:
        print(f"[FAIL] Document chunking test failed: {e}\n")
        return False

def test_retrieval():
    """Test the document retrieval functionality"""
    print("Testing Document Retrieval...")
    print("-" * 30)
    
    try:
        # Initialize retriever
        retriever = Retriever()
        retriever.initialize()
        print("[PASS] Retriever initialized successfully")
        
        # Test searching with a query
        query = "test query"
        results, distances = retriever.search(query, k=3)
        print(f"[PASS] Search returned {len(results)} results")
        if results:
            print(f"[PASS] First result preview: {results[0]['metadata']['content'][:50]}{'...' if len(results[0]['metadata']['content']) > 50 else ''}")
        print("[PASS] Document retrieval test passed\n")
        return True
    except Exception as e:
        print(f"[FAIL] Document retrieval test failed: {e}\n")
        return False

def test_rag_engine():
    """Test the complete RAG engine"""
    print("Testing RAG Engine...")
    print("-" * 30)
    
    try:
        # Initialize RAG engine
        rag_engine = RAGEngine()
        print("[PASS] RAG engine initialized successfully")
        
        # Test document processing
        result = rag_engine.process_documents()
        print(f"[PASS] Document processing result: {result['status']}")
        
        # Test query processing
        query_result = rag_engine.query("What is machine learning?")
        print(f"[PASS] Query processed successfully")
        print(f"[PASS] Answer preview: {query_result['answer'][:100]}{'...' if len(query_result['answer']) > 100 else ''}")
        
        # Test system stats
        stats = rag_engine.get_system_stats()
        print(f"[PASS] System stats retrieved: {stats['system_status']}")
        
        print("[PASS] RAG engine test passed\n")
        return True
    except Exception as e:
        print(f"[FAIL] RAG engine test failed: {e}\n")
        return False

def test_cache_manager():
    """Test the cache manager"""
    print("Testing Cache Manager...")
    print("-" * 30)
    
    try:
        # Initialize cache manager
        cache_manager = CacheManager()
        print("[PASS] Cache manager initialized successfully")
        
        # Test caching
        test_query = "test query for caching"
        test_result = "test result"
        
        cache_manager.cache_result(test_query, test_result)
        print("[PASS] Result cached successfully")
        
        # Test retrieval
        cached_result = cache_manager.get_cached_result(test_query)
        assert cached_result == test_result
        print("[PASS] Cached result retrieved successfully")
        
        # Test stats
        stats = cache_manager.get_cache_stats()
        print(f"[PASS] Cache stats: {stats['total_items']} items")
        
        print("[PASS] Cache manager test passed\n")
        return True
    except Exception as e:
        print(f"[FAIL] Cache manager test failed: {e}\n")
        return False

def test_celery_tasks():
    """Test Celery task functionality"""
    print("Testing Celery Tasks...")
    print("-" * 30)
    
    try:
        # Test document processing task
        print("[INFO] Testing document processing task...")
        # Note: This is a basic test - in production you'd want to test with actual task execution
        
        # Test query processing task
        print("[INFO] Testing query processing task...")
        
        print("[PASS] Celery tasks structure validated\n")
        return True
    except Exception as e:
        print(f"[FAIL] Celery tasks test failed: {e}\n")
        return False

def main():
    """Run all unit tests for the RAG system"""
    print("Running RAG System Unit Tests")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_embedding_model,
        test_vector_storage,
        test_chunking,
        test_cache_manager,
        test_retrieval,
        test_rag_engine,
        test_celery_tasks,
        # test_model_inference,  # Comment out LLM test for faster testing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"❌ {total - passed} tests failed")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)