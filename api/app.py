from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routers import query, documents, system
from config.settings import API_TITLE, API_DESCRIPTION, API_VERSION
import os

# Create directories if they don't exist
from config.settings import DATA_DIR, DOCUMENTS_DIR, CACHE_DIR, EMBEDDINGS_DIR, CELERY_RESULTS_DIR

for directory in [DATA_DIR, DOCUMENTS_DIR, CACHE_DIR, EMBEDDINGS_DIR, CELERY_RESULTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(query.router)
app.include_router(documents.router)
app.include_router(system.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Local RAG API with Celery job queues",
        "version": API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/system/health"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "details": {
                "path": str(request.url),
                "method": request.method
            }
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print(f"Starting {API_TITLE} v{API_VERSION}")
    print(f"API Documentation: http://localhost:8080/docs")
    print(f"Alternative Docs: http://localhost:8080/redoc")
    
    # Create a sample document if documents directory is empty
    if not os.listdir(DOCUMENTS_DIR):
        sample_doc_path = os.path.join(DOCUMENTS_DIR, "sample_document.txt")
        with open(sample_doc_path, 'w', encoding='utf-8') as f:
            f.write("""Local RAG System Documentation

This is a sample document for the Local RAG (Retrieval-Augmented Generation) system.

The system uses:
- Llama 3.2 1B model for text generation
- all-MiniLM-L6-v2 for creating embeddings
- FAISS for efficient vector similarity search
- FastAPI for the REST API interface
- Celery for asynchronous task processing

Key Features:
1. Local execution - no cloud dependencies
2. Document processing and indexing
3. Semantic search capabilities
4. Response caching for improved performance
5. Asynchronous task processing
6. RESTful API interface

To use the system:
1. Place your documents in the data/documents/ directory
2. Call the /documents/process endpoint to index them
3. Use the /query endpoint to ask questions
4. Monitor task progress using the task status endpoints

The system is optimized for CPU-only execution and provides comprehensive API documentation through Swagger UI and ReDoc interfaces.""")
        print(f"Created sample document: {sample_doc_path}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print(f"Shutting down {API_TITLE}")

if __name__ == "__main__":
    import uvicorn
    from config.settings import API_HOST, API_PORT
    
    uvicorn.run(
        "api.app:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )