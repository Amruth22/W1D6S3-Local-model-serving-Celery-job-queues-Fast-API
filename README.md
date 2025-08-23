# Local RAG FastAPI + Celery System

This is a FastAPI-based Retrieval-Augmented Generation (RAG) system with Celery job queues that runs entirely locally using:
- Llama 3.2 1B model for text generation
- all-MiniLM-L6-v2 for embeddings
- FAISS for vector storage
- FastAPI for REST API
- Celery for asynchronous task processing

## Features
- REST API endpoints for document processing and querying
- Asynchronous task processing with Celery
- Local document processing and indexing
- Semantic search using embeddings
- Dual-layer caching (in-memory and disk-based)
- Optimized for CPU-only execution
- SQLite-based Celery broker (no Redis required)

## Installation

1. Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

### Start the FastAPI Server
```bash
python main.py
```

The API will be available at `http://localhost:8080`

### API Documentation
Once the server is running, visit:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## API Endpoints

### Query Endpoints
- `POST /query` - Submit questions for RAG processing
- `GET /query/{job_id}` - Check async query status and retrieve results

### Document Management
- `POST /documents/process` - Trigger document processing from `data/documents/`
- `GET /documents/status` - Get document processing status

### System Information
- `GET /health` - System health check
- `GET /stats` - System statistics

## Adding Documents

To add documents for the RAG system to use:
1. Place your text documents in the `data/documents/` directory
2. Call the `POST /documents/process` endpoint
3. The documents will be automatically processed and indexed

## Architecture

The system uses:
- **FastAPI** for the REST API server
- **Celery** for background task processing
- **SQLite** as Celery message broker
- **File-based** result backend
- **Existing cache system** for response caching

## Configuration

Configuration settings can be found in `config/settings.py`:
- API settings (host, port)
- Model configurations
- Celery settings
- Cache parameters
- Task timeouts