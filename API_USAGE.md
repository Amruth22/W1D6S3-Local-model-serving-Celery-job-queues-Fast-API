# API Usage Guide

This document provides examples of how to use the Local RAG FastAPI + Celery system.

## Starting the System

### Option 1: Using the startup script (Linux/Mac)
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Using Python directly
```bash
# Install requirements
pip install -r requirements.txt

# Start both FastAPI and Celery
python main.py

# Or start services separately
python main.py api     # Start only FastAPI server
python main.py worker  # Start only Celery worker
```

## API Endpoints

### Base URL
```
http://localhost:8080
```

### 1. System Health and Information

#### Health Check
```bash
curl -X GET "http://localhost:8080/system/health"
```

#### System Statistics
```bash
curl -X GET "http://localhost:8080/system/stats"
```

#### System Information
```bash
curl -X GET "http://localhost:8080/system/info"
```

### 2. Document Management

#### Process Documents (Synchronous)
```bash
curl -X POST "http://localhost:8080/documents/process" \
  -H "Content-Type: application/json" \
  -d '{
    "clear_existing": true,
    "async_processing": false
  }'
```

#### Process Documents (Asynchronous)
```bash
curl -X POST "http://localhost:8080/documents/process" \
  -H "Content-Type: application/json" \
  -d '{
    "clear_existing": true,
    "async_processing": true
  }'
```

#### Get Document Status
```bash
curl -X GET "http://localhost:8080/documents/status"
```

#### Clear Search Index
```bash
curl -X POST "http://localhost:8080/documents/clear-index"
```

#### Check Document Task Status
```bash
curl -X GET "http://localhost:8080/documents/task/{task_id}"
```

### 3. Query Processing

#### Simple Query (Synchronous)
```bash
curl -X POST "http://localhost:8080/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "async_processing": false
  }'
```

#### Simple Query (Asynchronous)
```bash
curl -X POST "http://localhost:8080/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is deep learning and how does it work?",
    "async_processing": true
  }'
```

#### Batch Queries
```bash
curl -X POST "http://localhost:8080/query/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      "What is machine learning?",
      "How does deep learning work?",
      "What are neural networks?"
    ]
  }'
```

#### Check Query Task Status
```bash
curl -X GET "http://localhost:8080/query/{task_id}"
```

#### Cancel Task
```bash
curl -X DELETE "http://localhost:8080/query/{task_id}"
```

### 4. Cache Management

#### Clear Cache
```bash
curl -X POST "http://localhost:8080/system/cache/clear"
```

## Python Client Examples

### Using requests library

```python
import requests
import time

# Base URL
BASE_URL = "http://localhost:8080"

# 1. Check system health
response = requests.get(f"{BASE_URL}/system/health")
print("Health:", response.json())

# 2. Process documents asynchronously
doc_response = requests.post(f"{BASE_URL}/documents/process", json={
    "clear_existing": True,
    "async_processing": True
})
task_id = doc_response.json()["task_id"]
print(f"Document processing task ID: {task_id}")

# 3. Wait for document processing to complete
while True:
    status_response = requests.get(f"{BASE_URL}/documents/task/{task_id}")
    status = status_response.json()
    print(f"Status: {status['status']}, Progress: {status.get('progress', 0)}%")
    
    if status["status"] in ["SUCCESS", "FAILURE"]:
        break
    time.sleep(2)

# 4. Ask a question
query_response = requests.post(f"{BASE_URL}/query/", json={
    "question": "What topics are covered in the AI course?",
    "async_processing": False
})
print("Answer:", query_response.json()["answer"])

# 5. Get system statistics
stats_response = requests.get(f"{BASE_URL}/system/stats")
print("System Stats:", stats_response.json())
```

### Using httpx (async)

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Health check
        health = await client.get("http://localhost:8080/system/health")
        print("Health:", health.json())
        
        # Ask a question
        query = await client.post("http://localhost:8080/query/", json={
            "question": "What is machine learning?",
            "async_processing": False
        })
        print("Answer:", query.json()["answer"])

# Run the async function
asyncio.run(main())
```

## Response Examples

### Successful Query Response
```json
{
  "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task.",
  "source": "generated",
  "processing_time": 2.34,
  "retrieved_chunks": 3,
  "context_used": true
}
```

### Async Task Response
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PENDING",
  "message": "Query submitted for asynchronous processing"
}
```

### Task Status Response
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "SUCCESS",
  "progress": 100,
  "message": "Query processed successfully",
  "result": {
    "answer": "Machine learning is...",
    "processing_time": 3.45,
    "retrieved_chunks": 5
  }
}
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (invalid endpoint or task ID)
- `500`: Internal Server Error

Error responses include details:
```json
{
  "error": "Internal Server Error",
  "message": "Error description",
  "details": {
    "path": "/query/",
    "method": "POST"
  }
}
```

## Interactive API Documentation

Visit these URLs when the server is running:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

These provide interactive documentation where you can test the API endpoints directly from your browser.