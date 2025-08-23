import os
from config.settings import DOCUMENTS_DIR, CHUNK_SIZE, CHUNK_OVERLAP
import re

class DocumentProcessor:
    def __init__(self):
        """Initialize document processor"""
        pass
    
    def load_documents(self):
        """Load all documents from the documents directory"""
        documents = []
        
        if not os.path.exists(DOCUMENTS_DIR):
            print(f"Documents directory {DOCUMENTS_DIR} does not exist")
            os.makedirs(DOCUMENTS_DIR, exist_ok=True)
            return documents
            
        for filename in os.listdir(DOCUMENTS_DIR):
            file_path = os.path.join(DOCUMENTS_DIR, filename)
            if os.path.isfile(file_path) and filename.endswith('.txt'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents.append({
                            'content': content,
                            'filename': filename,
                            'path': file_path
                        })
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    
        return documents
    
    def chunk_text(self, text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
        """Split text into chunks with overlap"""
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
    
    def get_document_stats(self):
        """Get statistics about documents in the directory"""
        documents = self.load_documents()
        total_docs = len(documents)
        total_chars = sum(len(doc['content']) for doc in documents)
        
        # Estimate total chunks
        total_chunks = 0
        for doc in documents:
            chunks = self.chunk_text(doc['content'])
            total_chunks += len(chunks)
            
        return {
            'total_documents': total_docs,
            'total_characters': total_chars,
            'estimated_chunks': total_chunks,
            'chunk_size': CHUNK_SIZE,
            'chunk_overlap': CHUNK_OVERLAP
        }