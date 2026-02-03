"""
Token blacklist service for logout functionality
Uses in-memory cache for development, Redis for production
"""
from typing import Optional
from datetime import datetime, timedelta
import os

# In-memory cache for development (replace with Redis in production)
_blacklist_cache = {}

class TokenBlacklist:
    """
    Manage blacklisted JWT tokens (for logout functionality)
    
    In production, use Redis:
    - redis_client = redis.Redis(host='localhost', port=6379, db=0)
    - redis_client.setex(token, expiry_seconds, "blacklisted")
    """
    
    @staticmethod
    def add(token: str, expires_in_seconds: int):
        """Add token to blacklist with expiry"""
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        _blacklist_cache[token] = expires_at
        
        # Clean up expired tokens periodically
        TokenBlacklist._cleanup()
    
    @staticmethod
    def is_blacklisted(token: str) -> bool:
        """Check if token is blacklisted"""
        if token not in _blacklist_cache:
            return False
        
        expires_at = _blacklist_cache[token]
        
        # Check if expired
        if datetime.utcnow() > expires_at:
            del _blacklist_cache[token]
            return False
        
        return True
    
    @staticmethod
    def _cleanup():
        """Remove expired tokens from cache"""
        now = datetime.utcnow()
        expired_tokens = [
            token for token, expires_at in _blacklist_cache.items()
            if now > expires_at
        ]
        for token in expired_tokens:
            del _blacklist_cache[token]


# Production Redis implementation (commented out)
"""
import redis
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=0,
    decode_responses=True
)

class TokenBlacklist:
    @staticmethod
    def add(token: str, expires_in_seconds: int):
        redis_client.setex(f"blacklist:{token}", expires_in_seconds, "true")
    
    @staticmethod
    def is_blacklisted(token: str) -> bool:
        return redis_client.exists(f"blacklist:{token}") > 0
"""
