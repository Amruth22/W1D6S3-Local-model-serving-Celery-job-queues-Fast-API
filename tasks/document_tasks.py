from tasks.celery_app import celery_app
from rag.engine import RAGEngine
import time

@celery_app.task(bind=True)
def process_documents_async(self):
    """Asynchronously process documents and build search index"""
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Initializing RAG engine...', 'progress': 10}
        )
        
        # Initialize RAG engine
        rag_engine = RAGEngine()
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Processing documents...', 'progress': 30}
        )
        
        # Process documents
        result = rag_engine.process_documents()
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Building search index...', 'progress': 80}
        )
        
        # Small delay to show progress
        time.sleep(1)
        
        # Final result
        return {
            'status': 'completed',
            'result': result,
            'progress': 100,
            'message': 'Document processing completed successfully'
        }
        
    except Exception as exc:
        # Update task state with error
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Error occurred during document processing',
                'error': str(exc),
                'progress': 0
            }
        )
        raise exc

@celery_app.task(bind=True)
def clear_index_async(self):
    """Asynchronously clear the search index"""
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Clearing search index...', 'progress': 50}
        )
        
        # Initialize RAG engine and clear index
        rag_engine = RAGEngine()
        rag_engine.retriever.clear_index()
        
        return {
            'status': 'completed',
            'progress': 100,
            'message': 'Search index cleared successfully'
        }
        
    except Exception as exc:
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Error occurred while clearing index',
                'error': str(exc),
                'progress': 0
            }
        )
        raise exc

@celery_app.task
def get_document_stats_async():
    """Get document statistics asynchronously"""
    try:
        rag_engine = RAGEngine()
        stats = rag_engine.get_system_stats()
        
        return {
            'status': 'completed',
            'stats': stats,
            'message': 'Document statistics retrieved successfully'
        }
        
    except Exception as exc:
        return {
            'status': 'failed',
            'error': str(exc),
            'message': 'Failed to retrieve document statistics'
        }