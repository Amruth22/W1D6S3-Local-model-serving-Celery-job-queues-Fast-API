#!/usr/bin/env python3
"""
Main entry point for the Local RAG FastAPI + Celery application.

This script starts both the FastAPI server and Celery worker in the same process
for simplified deployment and development.
"""

import sys
import os
import multiprocessing
import signal
import time
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def start_celery_worker():
    """Start Celery worker process"""
    from tasks.celery_app import celery_app
    
    print("Starting Celery worker...")
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--pool=threads'  # Use threads for better compatibility
    ])

def start_fastapi_server():
    """Start FastAPI server"""
    import uvicorn
    
    try:
        from config.settings import API_HOST, API_PORT
    except ImportError:
        API_HOST = "0.0.0.0"
        API_PORT = 8080
        print("⚠️  Using fallback API configuration")
    
    print(f"Starting FastAPI server on {API_HOST}:{API_PORT}...")
    uvicorn.run(
        "api.app:app",
        host=API_HOST,
        port=API_PORT,
        log_level="info",
        access_log=True
    )

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\nReceived signal {signum}. Shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to start both FastAPI and Celery"""
    print("=" * 60)
    print("Local RAG System with FastAPI + Celery")
    print("=" * 60)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create necessary directories
    try:
        from config.settings import DATA_DIR, DOCUMENTS_DIR, CACHE_DIR, EMBEDDINGS_DIR, CELERY_RESULTS_DIR
    except ImportError:
        # Fallback configuration if settings file is missing
        from pathlib import Path
        PROJECT_ROOT = Path(__file__).parent
        DATA_DIR = PROJECT_ROOT / "data"
        DOCUMENTS_DIR = DATA_DIR / "documents"
        CACHE_DIR = DATA_DIR / "cache"
        EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"
        CELERY_RESULTS_DIR = DATA_DIR / "celery_results"
        print("⚠️  Using fallback configuration (config/settings.py not found)")
    
    for directory in [DATA_DIR, DOCUMENTS_DIR, CACHE_DIR, EMBEDDINGS_DIR, CELERY_RESULTS_DIR]:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Directory ready: {directory}")
    
    print("\nStarting services...")
    
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == "worker":
                # Start only Celery worker
                start_celery_worker()
            elif sys.argv[1] == "api":
                # Start only FastAPI server
                start_fastapi_server()
            else:
                print("Usage: python main.py [worker|api]")
                print("  worker - Start only Celery worker")
                print("  api    - Start only FastAPI server")
                print("  (no args) - Start both services")
                sys.exit(1)
        else:
            # Start both services using multiprocessing
            print("Starting both FastAPI server and Celery worker...")
            
            # Create processes
            api_process = multiprocessing.Process(target=start_fastapi_server, name="FastAPI")
            worker_process = multiprocessing.Process(target=start_celery_worker, name="Celery")
            
            # Start processes
            api_process.start()
            time.sleep(2)  # Give FastAPI a moment to start
            worker_process.start()
            
            print("\n" + "=" * 60)
            print("🚀 Services started successfully!")
            print(f"📖 API Documentation: http://localhost:8080/docs")
            print(f"📚 Alternative Docs: http://localhost:8080/redoc")
            print(f"❤️  Health Check: http://localhost:8080/system/health")
            print("=" * 60)
            print("\nPress Ctrl+C to stop all services")
            
            try:
                # Wait for processes
                api_process.join()
                worker_process.join()
            except KeyboardInterrupt:
                print("\nShutting down services...")
                api_process.terminate()
                worker_process.terminate()
                api_process.join()
                worker_process.join()
                print("✓ All services stopped")
                
    except Exception as e:
        print(f"Error starting services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set multiprocessing start method for compatibility
    if sys.platform != "win32":
        multiprocessing.set_start_method("spawn", force=True)
    
    main()