import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.processor import DocumentProcessor
from rag.retriever import Retriever
from cache.manager import CacheManager
from llm import generate_response
import time

class RAGEngine:
    def __init__(self):
        """Initialize RAG engine"""
        self.document_processor = DocumentProcessor()
        self.retriever = Retriever()
        self.cache_manager = CacheManager()
        
        # Initialize retriever
        self.retriever.initialize()
        
    def process_documents(self):
        """Process and index all documents"""
        print("Loading documents...")
        documents = self.document_processor.load_documents()
        
        if not documents:
            print("No documents found to process")
            return {
                'status': 'completed',
                'documents_processed': 0,
                'message': 'No documents found in data/documents/ directory'
            }
            
        print(f"Processing {len(documents)} documents...")
        
        # Clear existing index before adding new documents
        self.retriever.clear_index()
        
        # Add documents to retriever
        self.retriever.add_documents(documents)
        
        print("Document processing complete")
        
        return {
            'status': 'completed',
            'documents_processed': len(documents),
            'message': f'Successfully processed {len(documents)} documents'
        }
        
    def query(self, question):
        """Process a query through the RAG pipeline"""
        start_time = time.time()
        
        # Check cache first
        cached_result = self.cache_manager.get_cached_result(question)
        if cached_result:
            print("Using cached result")
            return {
                'answer': cached_result,
                'source': 'cache',
                'processing_time': time.time() - start_time,
                'retrieved_chunks': 0
            }
            
        # Retrieve relevant documents
        print("Retrieving relevant documents...")
        results, distances = self.retriever.search(question)
        
        # Format context
        context = "\n".join([result['metadata']['content'] for result in results])
        
        # Generate prompt with context
        if context:
            prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
        else:
            prompt = f"Question: {question}\nAnswer:"
            
        # Generate response using LLM
        print("Generating response...")
        answer = generate_response(prompt)
        
        processing_time = time.time() - start_time
        print(f"Response generated in {processing_time:.2f} seconds")
        
        # Cache the result
        self.cache_manager.cache_result(question, answer)
        
        return {
            'answer': answer,
            'source': 'generated',
            'processing_time': processing_time,
            'retrieved_chunks': len(results),
            'context_used': bool(context)
        }
    
    def get_system_stats(self):
        """Get comprehensive system statistics"""
        doc_stats = self.document_processor.get_document_stats()
        index_stats = self.retriever.get_index_stats()
        cache_stats = self.cache_manager.get_cache_stats()
        
        return {
            'documents': doc_stats,
            'index': index_stats,
            'cache': cache_stats,
            'system_status': 'healthy'
        }