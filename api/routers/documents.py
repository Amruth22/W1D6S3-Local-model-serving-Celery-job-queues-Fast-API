from fastapi import APIRouter, HTTPException
from api.models.requests import DocumentProcessRequest
from api.models.responses import DocumentProcessResponse, AsyncTaskResponse, TaskStatusResponse, SystemStats
from tasks.document_tasks import process_documents_async, clear_index_async, get_document_stats_async
from tasks.celery_app import celery_app
from rag.engine import RAGEngine
from typing import Union

router = APIRouter(prefix="/documents", tags=["Documents"])

# Initialize RAG engine
rag_engine = None

def get_rag_engine():
    """Get or initialize RAG engine"""
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
    return rag_engine

@router.post("/process", response_model=Union[DocumentProcessResponse, AsyncTaskResponse])
async def process_documents(request: DocumentProcessRequest):
    """
    Process documents from the data/documents/ directory.
    
    - **clear_existing**: Whether to clear the existing search index
    - **async_processing**: Whether to process documents asynchronously
    """
    try:
        if request.async_processing:
            # Process asynchronously
            if request.clear_existing:
                # First clear the index, then process documents
                clear_task = clear_index_async.delay()
                # Wait a moment then start processing
                task = process_documents_async.delay()
            else:
                task = process_documents_async.delay()
                
            return AsyncTaskResponse(
                task_id=task.id,
                status="PENDING",
                message="Document processing submitted for asynchronous execution"
            )
        else:
            # Process synchronously
            engine = get_rag_engine()
            
            if request.clear_existing:
                engine.retriever.clear_index()
                
            result = engine.process_documents()
            
            return DocumentProcessResponse(
                status=result['status'],
                documents_processed=result['documents_processed'],
                message=result['message']
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

@router.get("/status", response_model=SystemStats)
async def get_document_status():
    """
    Get current document processing status and statistics.
    """
    try:
        engine = get_rag_engine()
        stats = engine.get_system_stats()
        
        return SystemStats(
            documents=stats['documents'],
            index=stats['index'],
            cache=stats['cache'],
            system_status=stats['system_status']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document status: {str(e)}")

@router.post("/clear-index", response_model=AsyncTaskResponse)
async def clear_search_index():
    """
    Clear the search index (removes all indexed documents).
    """
    try:
        task = clear_index_async.delay()
        
        return AsyncTaskResponse(
            task_id=task.id,
            status="PENDING",
            message="Index clearing submitted for asynchronous execution"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing index: {str(e)}")

@router.get("/stats", response_model=SystemStats)
async def get_document_stats():
    """
    Get detailed document and system statistics.
    """
    try:
        engine = get_rag_engine()
        stats = engine.get_system_stats()
        
        return SystemStats(
            documents=stats['documents'],
            index=stats['index'],
            cache=stats['cache'],
            system_status=stats['system_status']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document statistics: {str(e)}")

@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_document_task_status(task_id: str):
    """
    Get the status of a document processing task.
    
    - **task_id**: The task identifier returned when submitting an async document operation
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