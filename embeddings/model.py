import torch
from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL_ID
import numpy as np
import os

class EmbeddingModel:
    def __init__(self):
        """Initialize the embedding model"""
        self.model = None
        self.dim = None
        
    def load_model(self):
        """Load the embedding model"""
        if self.model is None:
            print("Loading embedding model...")
            self.model = SentenceTransformer(EMBEDDING_MODEL_ID)
            self.dim = self.model.get_sentence_embedding_dimension()
            print("Embedding model loaded successfully")
        
    def encode(self, texts):
        """Encode texts into embeddings"""
        if self.model is None:
            self.load_model()
            
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
            
        # Generate embeddings
        with torch.no_grad():
            embeddings = self.model.encode(
                texts, 
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
        return embeddings
    
    def get_dimension(self):
        """Get the dimension of the embeddings"""
        if self.dim is None:
            self.load_model()
        return self.dim