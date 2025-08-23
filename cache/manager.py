import json
import os
import time
import hashlib
import pickle
from pathlib import Path

# Try to import settings, use fallback if not available
try:
    from config.settings import CACHE_DIR, CACHE_TTL, CACHE_MAX_SIZE
except ImportError:
    # Fallback configuration
    PROJECT_ROOT = Path(__file__).parent.parent
    CACHE_DIR = PROJECT_ROOT / "data" / "cache"
    CACHE_TTL = 24 * 60 * 60  # 24 hours
    CACHE_MAX_SIZE = 1000

class CacheManager:
    def __init__(self):
        """Initialize cache manager"""
        self.cache_dir = CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_cache_key(self, query):
        """Generate a cache key for a query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key):
        """Get the file path for a cache key"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def get_cached_result(self, query):
        """Retrieve cached result for a query"""
        cache_key = self._get_cache_key(query)
        cache_file = self._get_cache_file_path(cache_key)
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    
                # Check if cache is still valid
                if time.time() - cached_data['timestamp'] < CACHE_TTL:
                    return cached_data['result']
                else:
                    # Remove expired cache
                    os.remove(cache_file)
            except Exception as e:
                print(f"Error reading cache: {e}")
                
        return None
    
    def cache_result(self, query, result):
        """Cache a result for a query"""
        # Check cache size and clean if needed
        self._clean_cache_if_needed()
        
        cache_key = self._get_cache_key(query)
        cache_file = self._get_cache_file_path(cache_key)
        
        cached_data = {
            'query': query,
            'result': result,
            'timestamp': time.time()
        }
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cached_data, f)
        except Exception as e:
            print(f"Error writing cache: {e}")
    
    def _clean_cache_if_needed(self):
        """Clean cache if it exceeds maximum size"""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]
            
            if len(cache_files) >= CACHE_MAX_SIZE:
                # Remove oldest cache files
                cache_files_with_time = []
                for f in cache_files:
                    file_path = os.path.join(self.cache_dir, f)
                    cache_files_with_time.append((file_path, os.path.getmtime(file_path)))
                    
                # Sort by modification time (oldest first)
                cache_files_with_time.sort(key=lambda x: x[1])
                
                # Remove oldest files
                files_to_remove = len(cache_files) - CACHE_MAX_SIZE + 10  # Keep some buffer
                for i in range(min(files_to_remove, len(cache_files_with_time))):
                    os.remove(cache_files_with_time[i][0])
        except Exception as e:
            print(f"Error cleaning cache: {e}")
            
    def get_cache_stats(self):
        """Get cache statistics"""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]
            total_size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in cache_files)
            
            return {
                'total_items': len(cache_files),
                'total_size_bytes': total_size,
                'max_size': CACHE_MAX_SIZE,
                'ttl_hours': CACHE_TTL / 3600
            }
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {
                'total_items': 0,
                'total_size_bytes': 0,
                'max_size': CACHE_MAX_SIZE,
                'ttl_hours': CACHE_TTL / 3600
            }