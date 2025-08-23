#!/usr/bin/env python3
"""
Installation test script for Local RAG FastAPI + Celery system.
This script verifies that all components can be imported and basic functionality works.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Core dependencies
        import fastapi
        import uvicorn
        import celery
        import pydantic
        print("✓ FastAPI, Uvicorn, Celery, Pydantic")
        
        # ML dependencies
        import torch
        import transformers
        import sentence_transformers
        import faiss
        import numpy as np
        print("✓ PyTorch, Transformers, Sentence-Transformers, FAISS, NumPy")
        
        # Project modules
        from config.settings import API_PORT, API_TITLE
        from cache.manager import CacheManager
        from embeddings.model import EmbeddingModel
        from embeddings.storage import FaissStorage
        from rag.processor import DocumentProcessor
        from rag.retriever import Retriever
        from rag.engine import RAGEngine
        print("✓ Project modules")
        
        # API modules
        from api.app import app
        from api.models.requests import QueryRequest
        from api.models.responses import QueryResponse
        from tasks.celery_app import celery_app
        print("✓ API and task modules")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_directories():
    """Test that required directories can be created"""
    print("\nTesting directory creation...")
    
    try:
        from config.settings import DATA_DIR, DOCUMENTS_DIR, CACHE_DIR, EMBEDDINGS_DIR, CELERY_RESULTS_DIR
        
        directories = [DATA_DIR, DOCUMENTS_DIR, CACHE_DIR, EMBEDDINGS_DIR, CELERY_RESULTS_DIR]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if os.path.exists(directory):
                print(f"✓ {directory}")
            else:
                print(f"❌ Failed to create {directory}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Directory creation error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without heavy model loading"""
    print("\nTesting basic functionality...")
    
    try:
        # Test cache manager
        from cache.manager import CacheManager
        cache_manager = CacheManager()
        cache_manager.cache_result("test", "result")
        result = cache_manager.get_cached_result("test")
        assert result == "result"
        print("✓ Cache manager")
        
        # Test document processor
        from rag.processor import DocumentProcessor
        processor = DocumentProcessor()
        chunks = processor.chunk_text("This is a test. This is another sentence. And one more.")
        assert len(chunks) > 0
        print("✓ Document processor")
        
        # Test embedding model initialization (without loading)
        from embeddings.model import EmbeddingModel
        embedding_model = EmbeddingModel()
        print("✓ Embedding model structure")
        
        # Test FAISS storage initialization
        from embeddings.storage import FaissStorage
        faiss_storage = FaissStorage(384)  # Standard dimension for all-MiniLM-L6-v2
        print("✓ FAISS storage structure")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality error: {e}")
        return False

def test_api_structure():
    """Test API structure without starting the server"""
    print("\nTesting API structure...")
    
    try:
        from api.app import app
        from fastapi.testclient import TestClient
        
        # Create test client
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        print("✓ Root endpoint")
        
        # Test health endpoint
        response = client.get("/system/health")
        assert response.status_code == 200
        print("✓ Health endpoint")
        
        # Test info endpoint
        response = client.get("/system/info")
        assert response.status_code == 200
        print("✓ Info endpoint")
        
        return True
        
    except Exception as e:
        print(f"❌ API structure error: {e}")
        return False

def test_celery_structure():
    """Test Celery task structure"""
    print("\nTesting Celery structure...")
    
    try:
        from tasks.celery_app import celery_app
        from tasks.document_tasks import process_documents_async
        from tasks.query_tasks import process_query_async
        
        # Check that tasks are registered
        registered_tasks = list(celery_app.tasks.keys())
        print(f"✓ Celery app with {len(registered_tasks)} registered tasks")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery structure error: {e}")
        return False

def main():
    """Run all installation tests"""
    print("=" * 60)
    print("Local RAG FastAPI + Celery Installation Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Directory Test", test_directories),
        ("Basic Functionality Test", test_basic_functionality),
        ("API Structure Test", test_api_structure),
        ("Celery Structure Test", test_celery_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"Installation Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Installation test completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python main.py' to start the system")
        print("2. Visit http://localhost:8080/docs for API documentation")
        print("3. Place documents in data/documents/ directory")
        print("4. Use /documents/process endpoint to index documents")
        print("5. Use /query/ endpoint to ask questions")
    else:
        print(f"❌ {total - passed} tests failed. Please check the installation.")
        print("\nTroubleshooting:")
        print("1. Make sure all requirements are installed: pip install -r requirements.txt")
        print("2. Check Python version (3.8+ recommended)")
        print("3. Ensure all dependencies are compatible")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)