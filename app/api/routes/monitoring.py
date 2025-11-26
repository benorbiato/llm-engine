"""
Monitoring and status routes for API credits and cache.
"""
from fastapi import APIRouter, status
from app.utils.logger import get_logger
from app.utils.cache import verification_cache
from app.config import settings

logger = get_logger("monitoring")

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/cache-stats")
async def get_cache_stats():
    """
    Get cache statistics.
    
    Returns info about cached verifications and performance.
    """
    stats = verification_cache.get_stats()
    return {
        "status": "success",
        "cache": stats,
        "message": f"{stats['total_entries']} processos em cache"
    }


@router.post("/cache/clear")
async def clear_cache():
    """
    Clear all cache entries.
    
    Use this if you want to force fresh API calls.
    """
    verification_cache.clear()
    logger.info("Cache cleared by user request")
    return {
        "status": "success",
        "message": "Cache limpo com sucesso"
    }


@router.get("/api-status")
async def get_api_status():
    """
    Get API configuration and credit usage status.
    
    Returns information about configured API and recommendations.
    """
    api_key_configured = bool(settings.groq_api_key)
    api_key_masked = (
        settings.groq_api_key[:7] + "..." 
        if api_key_configured else "NOT_CONFIGURED"
    )
    
    cache_stats = verification_cache.get_stats()
    
    return {
        "status": "operational",
        "api": {
            "provider": "Groq",
            "model": settings.groq_model,
            "api_key_configured": api_key_configured,
            "api_key_preview": api_key_masked,
            "max_tokens_per_request": settings.max_tokens
        },
        "cache": cache_stats,
        "recommendations": [
            "✅ Use cache para evitar requisições duplicadas",
            f"📊 Atualmente {cache_stats['total_entries']} processos em cache",
            "🔄 Cache expira em 60 minutos",
            "💰 Monitore seu uso em https://console.groq.com/",
            "⚠️  Se receber erro 429, seus créditos foram esgotados"
        ]
    }


@router.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "LLM Verification API",
        "api_key_configured": bool(settings.groq_api_key)
    }

