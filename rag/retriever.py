import numpy as np
from embeddings.model import EmbeddingModel
from embeddings.storage import FaissStorage
from config.settings import TOP_K_RESULTS

class Retriever:
    def __init__(self):
        """Initialize retriever with embedding model and FAISS storage"""
        self.embedding_model = EmbeddingModel()
        self.faiss_storage = None
        
    def initialize(self):
        """Initialize components"""
        # Load embedding model
        self.embedding_model.load_model()
        
        # Initialize FAISS storage
        dim = self.embedding_model.get_dimension()
        self.faiss_storage = FaissStorage(dim)
        self.faiss_storage.initialize_index()
        
    def search(self, query, k=TOP_K_RESULTS):
        """Search for relevant documents given a query"""
        if self.faiss_storage is None:
            self.initialize()
            
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Search in FAISS
        results, distances = self.faiss_storage.search(query_embedding, k)
        
        return results, distances
    
    def add_documents(self, documents):
        """Add documents to the retrieval system"""
        if self.faiss_storage is None:
            self.initialize()
            
        all_chunks = []
        all_metadata = []
        
        for doc in documents:
            # Chunk the document
            chunks = self.chunk_text(doc['content'])
            
            # Create embeddings for chunks
            if chunks:
                embeddings = self.embedding_model.encode(chunks)
                
                # Create metadata for each chunk
                for i, chunk in enumerate(chunks):
                    metadata = {
                        'content': chunk,
                        'source_file': doc['filename'],
                        'chunk_index': i
                    }
                    all_metadata.append(metadata)
                    
                # Add embeddings and metadata
                all_chunks.append(embeddings)
                
        if all_chunks:
            # Combine all embeddings
            combined_embeddings = np.vstack(all_chunks)
            # Add to FAISS
            self.faiss_storage.add_embeddings(combined_embeddings, all_metadata)
            
    def chunk_text(self, text, chunk_size=500, overlap=50):
        """Split text into chunks with overlap"""
        import re
        chunks = []
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) + 1 <= chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                # Add current chunk to chunks
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    
                # Start new chunk with overlap
                # Take last 'overlap' characters from current chunk as start of new chunk
                if len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:] + " " + sentence
                else:
                    current_chunk = sentence
                    
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def get_index_stats(self):
        """Get statistics about the search index"""
        if self.faiss_storage is None:
            self.initialize()
            
        return {
            'total_vectors': self.faiss_storage.get_total_vectors(),
            'embedding_dimension': self.embedding_model.get_dimension(),
            'top_k_results': TOP_K_RESULTS
        }
        
    def clear_index(self):
        """Clear the search index"""
        if self.faiss_storage is None:
            self.initialize()
        self.faiss_storage.clear_index()