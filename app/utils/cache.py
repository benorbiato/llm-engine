"""
Simple in-memory cache for verification results.
Prevents duplicate API calls for the same process.
"""
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.utils.logger import get_logger


logger = get_logger("cache")


class VerificationCache:
    """In-memory cache for verification results."""
    
    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize cache.
        
        Args:
            ttl_minutes: Time to live for cached entries (minutes)
        """
        self.ttl_minutes = ttl_minutes
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def _generate_key(self, processo_data: Dict[str, Any]) -> str:
        """
        Generate a cache key from process data.
        Uses hash of processo number and main fields.
        """
        # Use numeric process as primary identifier
        numero_processo = str(processo_data.get("numeroProcesso", ""))
        
        # Create a simple key to avoid re-processing same process
        key_data = {
            "numeroProcesso": numero_processo,
            # Include main fields that affect decision
            "esfera": processo_data.get("esfera"),
            "valorCondenacao": processo_data.get("valorCondenacao")
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        
        return f"verify_{key_hash}"
    
    def get(self, processo_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached verification result.
        
        Args:
            processo_data: Process data
        
        Returns:
            Cached result or None if not found/expired
        """
        key = self._generate_key(processo_data)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check expiration
        created_at = entry.get("created_at")
        if created_at:
            age = datetime.now() - created_at
            if age > timedelta(minutes=self.ttl_minutes):
                logger.info(
                    "Cache entry expired",
                    extra={"extra_data": {"key": key, "age_minutes": age.total_seconds() / 60}}
                )
                del self.cache[key]
                return None
        
        logger.info(
            "Cache hit for verification",
            extra={"extra_data": {
                "key": key,
                "numero_processo": processo_data.get("numeroProcesso")
            }}
        )
        
        return entry.get("result")
    
    def set(self, processo_data: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Cache a verification result.
        
        Args:
            processo_data: Process data
            result: Verification result
        """
        key = self._generate_key(processo_data)
        
        self.cache[key] = {
            "result": result,
            "created_at": datetime.now(),
            "numero_processo": processo_data.get("numeroProcesso")
        }
        
        logger.info(
            "Cached verification result",
            extra={"extra_data": {
                "key": key,
                "numero_processo": processo_data.get("numeroProcesso")
            }}
        )
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self.cache),
            "ttl_minutes": self.ttl_minutes,
            "entries": [
                {
                    "numero_processo": entry.get("numero_processo"),
                    "cached_at": entry.get("created_at").isoformat() if entry.get("created_at") else None
                }
                for entry in self.cache.values()
            ]
        }


# Global cache instance (1 hour TTL)
verification_cache = VerificationCache(ttl_minutes=60)

