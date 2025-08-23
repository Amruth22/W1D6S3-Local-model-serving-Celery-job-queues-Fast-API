from tasks.celery_app import celery_app
from rag.engine import RAGEngine
import time

@celery_app.task(bind=True)
def process_query_async(self, question):
    """Asynchronously process a RAG query"""
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
            meta={'status': 'Searching for relevant documents...', 'progress': 30}
        )
        
        # Small delay to show progress for demo purposes
        time.sleep(0.5)
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Generating response...', 'progress': 60}
        )
        
        # Process the query
        result = rag_engine.query(question)
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Finalizing response...', 'progress': 90}
        )
        
        # Small delay
        time.sleep(0.2)
        
        # Return final result
        return {
            'status': 'completed',
            'question': question,
            'answer': result['answer'],
            'source': result['source'],
            'processing_time': result['processing_time'],
            'retrieved_chunks': result['retrieved_chunks'],
            'context_used': result['context_used'],
            'progress': 100,
            'message': 'Query processed successfully'
        }
        
    except Exception as exc:
        # Update task state with error
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Error occurred during query processing',
                'error': str(exc),
                'question': question,
                'progress': 0
            }
        )
        raise exc

@celery_app.task(bind=True)
def batch_query_async(self, questions):
    """Process multiple queries asynchronously"""
    try:
        results = []
        total_questions = len(questions)
        
        # Initialize RAG engine
        rag_engine = RAGEngine()
        
        for i, question in enumerate(questions):
            # Update progress
            progress = int((i / total_questions) * 90)  # Reserve 10% for finalization
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': f'Processing question {i+1} of {total_questions}...',
                    'progress': progress,
                    'current_question': question
                }
            )
            
            # Process the query
            result = rag_engine.query(question)
            results.append({
                'question': question,
                'answer': result['answer'],
                'source': result['source'],
                'processing_time': result['processing_time'],
                'retrieved_chunks': result['retrieved_chunks']
            })
        
        # Final update
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Finalizing batch results...', 'progress': 95}
        )
        
        return {
            'status': 'completed',
            'total_questions': total_questions,
            'results': results,
            'progress': 100,
            'message': f'Successfully processed {total_questions} questions'
        }
        
    except Exception as exc:
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Error occurred during batch query processing',
                'error': str(exc),
                'progress': 0
            }
        )
        raise exc