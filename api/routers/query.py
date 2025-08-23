from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.models.requests import QueryRequest, BatchQueryRequest
from api.models.responses import QueryResponse, AsyncTaskResponse, TaskStatusResponse, BatchQueryResponse
from tasks.query_tasks import process_query_async, batch_query_async
from tasks.celery_app import celery_app
from rag.engine import RAGEngine
from typing import Union
import time

router = APIRouter(prefix="/query", tags=["Query"])

# Initialize RAG engine (will be reused across requests)
rag_engine = None

def get_rag_engine():
    """Get or initialize RAG engine"""
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
    return rag_engine

@router.post("/", response_model=Union[QueryResponse, AsyncTaskResponse])
async def process_query(request: QueryRequest):
    """
    Process a single query through the RAG system.
    
    - **question**: The question to ask the RAG system
    - **async_processing**: Whether to process asynchronously (for complex queries)
    """
    try:
        if request.async_processing:
            # Process asynchronously
            task = process_query_async.delay(request.question)
            return AsyncTaskResponse(
                task_id=task.id,
                status="PENDING",
                message="Query submitted for asynchronous processing"
            )
        else:
            # Process synchronously
            engine = get_rag_engine()
            result = engine.query(request.question)
            
            return QueryResponse(
                answer=result['answer'],
                source=result['source'],
                processing_time=result['processing_time'],
                retrieved_chunks=result['retrieved_chunks'],
                context_used=result['context_used']
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/batch", response_model=Union[BatchQueryResponse, AsyncTaskResponse])
async def process_batch_queries(request: BatchQueryRequest):
    """
    Process multiple queries in batch.
    
    - **questions**: List of questions to process (max 10)
    """
    try:
        # Always process batch queries asynchronously
        task = batch_query_async.delay(request.questions)
        
        return AsyncTaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"Batch of {len(request.questions)} queries submitted for processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch queries: {str(e)}")

@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of an asynchronous task.
    
    - **task_id**: The task identifier returned when submitting an async query
    """
    try:
        # Get task result
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = TaskStatusResponse(
                task_id=task_id,
                status="PENDING",
                message="Task is waiting to be processed"
            )
        elif task_result.state == 'PROGRESS':
            response = TaskStatusResponse(
                task_id=task_id,
                status="PROGRESS",
                progress=task_result.info.get('progress', 0),
                message=task_result.info.get('status', 'Processing...')
            )
        elif task_result.state == 'SUCCESS':
            result = task_result.result
            response = TaskStatusResponse(
                task_id=task_id,
                status="SUCCESS",
                progress=100,
                message=result.get('message', 'Task completed successfully'),
                result=result
            )
        elif task_result.state == 'FAILURE':
            response = TaskStatusResponse(
                task_id=task_id,
                status="FAILURE",
                progress=0,
                message="Task failed",
                error=str(task_result.info)
            )
        else:
            response = TaskStatusResponse(
                task_id=task_id,
                status=task_result.state,
                message=f"Task is in {task_result.state} state"
            )
            
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task status: {str(e)}")

@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel an asynchronous task.
    
    - **task_id**: The task identifier to cancel
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": f"Task {task_id} has been cancelled"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(e)}")