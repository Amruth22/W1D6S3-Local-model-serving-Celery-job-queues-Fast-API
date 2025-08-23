from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "PENDING"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    COMPLETED = "completed"

class QueryResponse(BaseModel):
    """Response model for single query"""
    answer: str = Field(..., description="The generated answer")
    source: str = Field(..., description="Source of the answer (cache/generated)")
    processing_time: float = Field(..., description="Time taken to process the query in seconds")
    retrieved_chunks: int = Field(..., description="Number of document chunks retrieved")
    context_used: bool = Field(..., description="Whether context was used for generation")
    
class AsyncTaskResponse(BaseModel):
    """Response model for async task submission"""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status")
    message: str = Field(..., description="Status message")
    
class TaskStatusResponse(BaseModel):
    """Response model for task status check"""
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    progress: Optional[int] = Field(None, description="Task progress percentage (0-100)")
    message: Optional[str] = Field(None, description="Status message")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")

class DocumentStats(BaseModel):
    """Document statistics model"""
    total_documents: int = Field(..., description="Total number of documents")
    total_characters: int = Field(..., description="Total characters across all documents")
    estimated_chunks: int = Field(..., description="Estimated number of chunks")
    chunk_size: int = Field(..., description="Chunk size configuration")
    chunk_overlap: int = Field(..., description="Chunk overlap configuration")

class IndexStats(BaseModel):
    """Index statistics model"""
    total_vectors: int = Field(..., description="Total vectors in the index")
    embedding_dimension: int = Field(..., description="Embedding vector dimension")
    top_k_results: int = Field(..., description="Top-K results configuration")

class CacheStats(BaseModel):
    """Cache statistics model"""
    total_items: int = Field(..., description="Total cached items")
    total_size_bytes: int = Field(..., description="Total cache size in bytes")
    max_size: int = Field(..., description="Maximum cache size")
    ttl_hours: float = Field(..., description="Cache TTL in hours")

class SystemStats(BaseModel):
    """System statistics model"""
    documents: DocumentStats
    index: IndexStats
    cache: CacheStats
    system_status: str = Field(..., description="Overall system status")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="System health status")
    timestamp: str = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    components: Dict[str, str] = Field(..., description="Component health status")

class DocumentProcessResponse(BaseModel):
    """Document processing response model"""
    status: str = Field(..., description="Processing status")
    documents_processed: int = Field(..., description="Number of documents processed")
    message: str = Field(..., description="Processing message")
    task_id: Optional[str] = Field(None, description="Task ID if processed asynchronously")

class BatchQueryResponse(BaseModel):
    """Batch query response model"""
    total_questions: int = Field(..., description="Total number of questions processed")
    results: List[Dict[str, Any]] = Field(..., description="Results for each question")
    task_id: Optional[str] = Field(None, description="Task ID if processed asynchronously")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")