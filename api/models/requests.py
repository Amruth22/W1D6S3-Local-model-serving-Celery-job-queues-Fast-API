from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    """Request model for single query"""
    question: str = Field(..., description="The question to ask the RAG system", min_length=1, max_length=1000)
    async_processing: bool = Field(False, description="Whether to process the query asynchronously")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is machine learning?",
                "async_processing": False
            }
        }

class BatchQueryRequest(BaseModel):
    """Request model for batch queries"""
    questions: List[str] = Field(..., description="List of questions to ask the RAG system", min_items=1, max_items=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    "What is machine learning?",
                    "How does deep learning work?",
                    "What are neural networks?"
                ]
            }
        }

class DocumentProcessRequest(BaseModel):
    """Request model for document processing"""
    clear_existing: bool = Field(True, description="Whether to clear existing index before processing")
    async_processing: bool = Field(True, description="Whether to process documents asynchronously")
    
    class Config:
        json_schema_extra = {
            "example": {
                "clear_existing": True,
                "async_processing": True
            }
        }