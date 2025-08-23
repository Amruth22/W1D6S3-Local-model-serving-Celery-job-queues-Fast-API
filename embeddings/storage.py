import faiss
import numpy as np
import json
import os
from config.settings import FAISS_INDEX_FILE, FAISS_METADATA_FILE, EMBEDDINGS_DIR
import pickle

class FaissStorage:
    def __init__(self, dimension):
        """Initialize FAISS storage"""
        self.dimension = dimension
        self.index = None
        self.metadata = []
        
        # Create embeddings directory if it doesn't exist
        os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
        
    def initialize_index(self):
        """Initialize or load the FAISS index"""
        if os.path.exists(FAISS_INDEX_FILE):
            print("Loading existing FAISS index...")
            self.index = faiss.read_index(str(FAISS_INDEX_FILE))
            # Load metadata
            if os.path.exists(FAISS_METADATA_FILE):
                with open(FAISS_METADATA_FILE, 'r') as f:
                    self.metadata = json.load(f)
        else:
            print("Creating new FAISS index...")
            self.index = faiss.IndexFlatIP(self.dimension)
            
    def add_embeddings(self, embeddings, metadata_list):
        """Add embeddings and metadata to the index"""
        if self.index is None:
            self.initialize_index()
            
        # Normalize embeddings for inner product search
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Add metadata
        self.metadata.extend(metadata_list)
        
        # Save index and metadata
        self.save_index()
        
    def search(self, query_embedding, k=5):
        """Search for similar embeddings"""
        if self.index is None:
            self.initialize_index()
            
        if self.index.ntotal == 0:
            return [], []
            
        # Normalize query embedding
        faiss.normalize_L2(query_embedding)
        
        # Search
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        # Get metadata for results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append({
                    'metadata': self.metadata[idx],
                    'distance': float(distances[0][i])
                })
                
        return results, distances[0]
        
    def save_index(self):
        """Save the index and metadata to disk"""
        if self.index is not None:
            faiss.write_index(self.index, str(FAISS_INDEX_FILE))
            with open(FAISS_METADATA_FILE, 'w') as f:
                json.dump(self.metadata, f)
                
    def get_total_vectors(self):
        """Get the total number of vectors in the index"""
        if self.index is None:
            self.initialize_index()
        return self.index.ntotal
        
    def clear_index(self):
        """Clear the index and metadata"""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        self.save_index()
        print("Index cleared successfully")