from fastapi import APIRouter, HTTPException
from api.models.responses import HealthResponse, SystemStats
from rag.engine import RAGEngine
from datetime import datetime
import sys
import os

# Try to import settings, use fallback if not available
try:
    from config.settings import API_VERSION, API_TITLE
except ImportError:
    API_VERSION = "1.0.0"
    API_TITLE = "Local RAG API"

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Get system health status.
    """
    try:
        # Check various system components
        components = {}
        
        # Check if we can initialize RAG engine
        try:
            rag_engine = RAGEngine()
            components["rag_engine"] = "healthy"
        except Exception as e:
            components["rag_engine"] = f"error: {str(e)}"
        
        # Check if directories exist
        from config.settings import DATA_DIR, DOCUMENTS_DIR, CACHE_DIR, EMBEDDINGS_DIR
        
        components["data_directory"] = "healthy" if os.path.exists(DATA_DIR) else "missing"
        components["documents_directory"] = "healthy" if os.path.exists(DOCUMENTS_DIR) else "missing"
        components["cache_directory"] = "healthy" if os.path.exists(CACHE_DIR) else "missing"
        components["embeddings_directory"] = "healthy" if os.path.exists(EMBEDDINGS_DIR) else "missing"
        
        # Check Python version
        components["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Overall status
        overall_status = "healthy" if all("error" not in status for status in components.values()) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            version=API_VERSION,
            components=components
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking system health: {str(e)}")

@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """
    Get comprehensive system statistics.
    """
    try:
        rag_engine = RAGEngine()
        stats = rag_engine.get_system_stats()
        
        return SystemStats(
            documents=stats['documents'],
            index=stats['index'],
            cache=stats['cache'],
            system_status=stats['system_status']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system statistics: {str(e)}")

@router.get("/info")
async def get_system_info():
    """
    Get general system information.
    """
    try:
        from config.settings import (
            API_TITLE, API_VERSION, API_DESCRIPTION,
            LLM_MODEL_ID, EMBEDDING_MODEL_ID,
            CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS,
            CACHE_TTL, CACHE_MAX_SIZE
        )
        
        return {
            "api": {
                "title": API_TITLE,
                "version": API_VERSION,
                "description": API_DESCRIPTION
            },
            "models": {
                "llm_model": LLM_MODEL_ID,
                "embedding_model": EMBEDDING_MODEL_ID
            },
            "configuration": {
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "top_k_results": TOP_K_RESULTS,
                "cache_ttl_hours": CACHE_TTL / 3600,
                "cache_max_size": CACHE_MAX_SIZE
            },
            "system": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")

@router.post("/cache/clear")
async def clear_cache():
    """
    Clear the response cache.
    """
    try:
        from cache.manager import CacheManager
        cache_manager = CacheManager()
        
        # Get current stats
        stats_before = cache_manager.get_cache_stats()
        
        # Clear cache by removing all cache files
        import os
        cache_files = [f for f in os.listdir(cache_manager.cache_dir) if f.endswith('.pkl')]
        for cache_file in cache_files:
            os.remove(os.path.join(cache_manager.cache_dir, cache_file))
        
        # Get stats after clearing
        stats_after = cache_manager.get_cache_stats()
        
        return {
            "message": "Cache cleared successfully",
            "items_removed": stats_before['total_items'],
            "bytes_freed": stats_before['total_size_bytes'],
            "current_items": stats_after['total_items']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")