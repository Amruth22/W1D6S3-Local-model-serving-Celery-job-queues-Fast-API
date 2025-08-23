# 🚀 Local RAG FastAPI + Celery System

A production-ready **Retrieval-Augmented Generation (RAG) system** built with FastAPI and Celery job queues that runs entirely locally. This system transforms the original CLI-based RAG implementation into a scalable web API with asynchronous task processing.

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   FastAPI App   │────│   SQLite     │────│  Celery Worker  │
│   (Port 8080)   │    │  (Broker)    │    │ (Async Tasks)   │
└─────────────────┘    └──────────────┘    └─────────────────┘
         │                                           │
         └─────────── File-based Storage ───────────┘
              (FAISS Index, Cache, Documents)
```

## 🔧 **Technology Stack**

- **🤖 LLM**: Llama 3.2 1B GGUF model (CPU-optimized)
- **🧠 Embeddings**: all-MiniLM-L6-v2 sentence transformers
- **🔍 Vector DB**: FAISS for efficient similarity search
- **🌐 Web API**: FastAPI with automatic OpenAPI documentation
- **⚡ Task Queue**: Celery with SQLite broker (no Redis required)
- **💾 Caching**: File-based dual-layer caching system
- **📊 Monitoring**: Built-in health checks and system statistics

## ✨ **Key Features**

### 🌐 **REST API Endpoints**
- **Query Processing**: Synchronous and asynchronous query handling
- **Document Management**: Automated document processing and indexing
- **Batch Operations**: Process multiple queries simultaneously
- **Task Monitoring**: Real-time progress tracking for async operations
- **System Management**: Health checks, statistics, and cache control

### ⚡ **Asynchronous Processing**
- **Celery Integration**: Background task processing with progress tracking
- **SQLite Broker**: No external dependencies (Redis-free)
- **Task Status API**: Monitor and cancel running tasks
- **Concurrent Processing**: Handle multiple requests simultaneously

### 🧠 **Advanced RAG Pipeline**
- **Smart Chunking**: Intelligent document segmentation with overlap
- **Semantic Search**: Vector-based similarity matching
- **Context Optimization**: Retrieval of most relevant document chunks
- **Response Caching**: Intelligent caching with 24-hour TTL
- **Local Privacy**: All processing happens on your machine

### 🔧 **Production Ready**
- **Comprehensive Testing**: End-to-end API endpoint testing
- **Error Handling**: Robust error management and logging
- **Auto Documentation**: Interactive Swagger UI and ReDoc
- **Health Monitoring**: System status and performance metrics
- **Easy Deployment**: Single command startup

## Installation

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd W1D6S3-Local-model-serving-Celery-job-queues-Fast-API

# Install requirements
pip install -r requirements.txt

# Test installation
python test_installation.py

# Start the system
python main.py
```

### Alternative Installation
```bash
# Using the startup script (Linux/Mac)
chmod +x start.sh
./start.sh
```

## Usage

### Start the System
```bash
# Start both FastAPI server and Celery worker
python main.py

# Or start services separately
python main.py api     # FastAPI server only
python main.py worker  # Celery worker only
```

### Access the API
- **API Base URL**: `http://localhost:8080`
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **Health Check**: `http://localhost:8080/system/health`

### 🚀 **Quick Start Example**

```bash
# 1. Check system health
curl http://localhost:8080/system/health
# Response: {"status": "healthy", "version": "1.0.0", ...}

# 2. Process documents (sync)
curl -X POST "http://localhost:8080/documents/process" \
  -H "Content-Type: application/json" \
  -d '{"clear_existing": true, "async_processing": false}'
# Response: {"status": "completed", "documents_processed": 1, ...}

# 3. Ask a question (sync)
curl -X POST "http://localhost:8080/query/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?", "async_processing": false}'
# Response: {"answer": "Machine learning is...", "processing_time": 2.34, ...}

# 4. Async query with progress tracking
curl -X POST "http://localhost:8080/query/" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain deep learning", "async_processing": true}'
# Response: {"task_id": "abc123", "status": "PENDING", ...}

# 5. Check task status
curl "http://localhost:8080/query/abc123"
# Response: {"status": "SUCCESS", "progress": 100, "result": {...}}

# 6. Get system statistics
curl "http://localhost:8080/system/stats"
# Response: {"documents": {...}, "index": {...}, "cache": {...}}
```

## 📡 **API Endpoints**

### 🔍 **Query Processing**
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/query/` | POST | Process single queries (sync/async) | Query result or task ID |
| `/query/batch` | POST | Process multiple queries | Task ID for batch processing |
| `/query/{task_id}` | GET | Check task status and results | Task status with progress |
| `/query/{task_id}` | DELETE | Cancel running task | Cancellation confirmation |

### 📚 **Document Management**
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/documents/process` | POST | Process documents (sync/async) | Processing result or task ID |
| `/documents/status` | GET | Get document statistics | Document and index stats |
| `/documents/clear-index` | POST | Clear search index | Task ID for clearing |
| `/documents/task/{task_id}` | GET | Check document task status | Task progress and result |

### 🔧 **System Management**
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/system/health` | GET | System health check | Health status and components |
| `/system/stats` | GET | Comprehensive statistics | System performance metrics |
| `/system/info` | GET | System configuration | API and model information |
| `/system/cache/clear` | POST | Clear response cache | Cache clearing confirmation |

### 📖 **Interactive Documentation**
- **Swagger UI**: `http://localhost:8080/docs` - Interactive API testing
- **ReDoc**: `http://localhost:8080/redoc` - Beautiful API documentation
- **OpenAPI Schema**: `http://localhost:8080/openapi.json` - Machine-readable API spec

## 📄 **Document Management**

### Adding Documents
1. **Place Documents**: Add `.txt` files to the `data/documents/` directory
2. **Process Documents**: Call the processing endpoint
   ```bash
   curl -X POST "http://localhost:8080/documents/process" \
     -H "Content-Type: application/json" \
     -d '{"clear_existing": true, "async_processing": false}'
   ```
3. **Monitor Progress**: Check processing status
   ```bash
   curl "http://localhost:8080/documents/status"
   ```

### Document Processing Features
- **Automatic Chunking**: Documents split into 500-character chunks with 50-character overlap
- **Embedding Generation**: Each chunk converted to 384-dimensional vectors
- **FAISS Indexing**: Efficient vector storage for fast similarity search
- **Metadata Tracking**: Source file and chunk information preserved
- **Incremental Updates**: Add new documents without reprocessing existing ones

## 🏗️ **System Architecture**

### Core Components
```
📁 Project Structure
├── api/                    # FastAPI application
│   ├── models/            # Pydantic request/response schemas
│   ├── routers/           # API endpoint handlers
│   └── app.py            # Main FastAPI application
├── tasks/                 # Celery task definitions
│   ├── celery_app.py     # Celery configuration
│   ├── document_tasks.py # Document processing tasks
│   └── query_tasks.py    # Query processing tasks
├── rag/                   # RAG system core
│   ├── engine.py         # Main RAG orchestrator
│   ├── processor.py      # Document processing
│   └── retriever.py      # Semantic search
├── embeddings/            # Vector processing
├── cache/                 # Caching system
├── config/                # Configuration management
└── data/                  # Data storage
```

### Processing Pipeline
1. **Document Ingestion** → Text files loaded from `data/documents/`
2. **Chunking** → Documents split into overlapping segments
3. **Embedding** → Chunks converted to vector representations
4. **Indexing** → Vectors stored in FAISS for fast search
5. **Query Processing** → User questions matched against document chunks
6. **Response Generation** → LLM generates answers using retrieved context
7. **Caching** → Results cached for improved performance

### Deployment Architecture
- **Single Process**: Both API and worker can run together
- **Separate Services**: API and worker can be scaled independently
- **No External Dependencies**: Uses SQLite and file system
- **Local Privacy**: All data stays on your machine

## ⚙️ **Configuration**

All settings are centralized in `config/settings.py`:

### 🌐 **API Configuration**
```python
API_HOST = "0.0.0.0"          # Server host
API_PORT = 8080               # Server port
API_TITLE = "Local RAG API"   # API title
```

### 🤖 **Model Settings**
```python
LLM_MODEL_ID = "meta-llama/Llama-3.2-1B"  # Language model
EMBEDDING_MODEL_ID = "all-MiniLM-L6-v2"   # Embedding model
CHUNK_SIZE = 500                          # Document chunk size
CHUNK_OVERLAP = 50                        # Chunk overlap
TOP_K_RESULTS = 5                         # Retrieved chunks per query
```

### ⚡ **Celery Configuration**
```python
CELERY_BROKER_URL = "sqlite:///data/celery.db"  # SQLite broker
CELERY_RESULT_BACKEND = "file://data/celery_results"  # File backend
TASK_TIMEOUT = 300                               # 5-minute timeout
```

### 💾 **Cache Settings**
```python
CACHE_TTL = 24 * 60 * 60     # 24-hour cache lifetime
CACHE_MAX_SIZE = 1000        # Maximum cached items
```

## 🧪 **Testing**

### Installation Test
```bash
python test_installation.py  # Verify all components
```

### API Endpoint Tests
```bash
python unit_test.py          # End-to-end API testing
```

### Manual Testing
```bash
# Health check
curl http://localhost:8080/system/health

# Process documents
curl -X POST "http://localhost:8080/documents/process" \
  -H "Content-Type: application/json" \
  -d '{"clear_existing": true, "async_processing": false}'

# Ask a question
curl -X POST "http://localhost:8080/query/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?", "async_processing": false}'
```

## 📊 **Monitoring & Observability**

### Health Monitoring
- **System Health**: `/system/health` - Component status checks
- **Performance Stats**: `/system/stats` - Detailed system metrics
- **Cache Analytics**: Track cache hit rates and storage usage
- **Task Monitoring**: Real-time progress tracking for async operations

### Logging
- **API Requests**: Automatic request/response logging
- **Task Execution**: Celery task progress and completion logs
- **Error Tracking**: Comprehensive error logging and stack traces
- **Performance Metrics**: Response times and resource usage

## 🚀 **Production Deployment**

### Single Machine Deployment
```bash
# Start both API and worker
python main.py
```

### Separate Service Deployment
```bash
# Terminal 1: Start API server
python main.py api

# Terminal 2: Start Celery worker
python main.py worker
```

### Process Management
```bash
# Using systemd, supervisor, or PM2 for production
# Example systemd service files can be created for:
# - rag-api.service (FastAPI server)
# - rag-worker.service (Celery worker)
```

## 🔒 **Security Considerations**

- **Local Execution**: All processing happens locally (no cloud dependencies)
- **No Authentication**: Designed for local/trusted network use
- **File System Access**: Ensure proper file permissions for data directories
- **Model Security**: Models downloaded from HuggingFace Hub
- **Input Validation**: Pydantic models validate all API inputs

## 🎯 **Use Cases**

- **📚 Personal Knowledge Base**: Query your personal document collection
- **🏢 Enterprise Document Search**: Internal document retrieval without cloud
- **🎓 Educational Projects**: Learn RAG implementation and API development
- **🔒 Privacy-Sensitive Applications**: Keep sensitive data on-premises
- **🌐 Offline Environments**: No internet connectivity required after setup
- **🔬 Research & Development**: Experiment with RAG techniques locally

## 🤝 **Contributing**

Contributions are welcome! Areas for improvement:
- Additional document format support (PDF, DOCX, etc.)
- Advanced chunking strategies
- Multiple embedding model support
- Enhanced caching mechanisms
- Performance optimizations
- Additional API endpoints

## 📝 **License**

This project is open source. Please check the license file for details.

---

**🎉 Ready to get started?** Follow the installation guide above and start building your local RAG system!