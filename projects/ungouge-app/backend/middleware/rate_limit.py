"""
Rate Limiting Middleware
Prevents abuse and DoS attacks
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"],  # Global default
    storage_uri="memory://",  # In-memory storage (use Redis for production)
)

# Rate limit configurations
RATE_LIMITS = {
    "quote_analyze": "10/hour",      # Quote analysis endpoint
    "upload": "5/hour",               # File upload endpoint
    "login": "5/15minute",            # Login attempts
    "api_general": "30/minute",       # General API calls
    "create": "20/minute",            # Create operations
    "delete": "10/minute",            # Delete operations
}


def get_rate_limit(endpoint: str) -> str:
    """Get rate limit string for an endpoint"""
    return RATE_LIMITS.get(endpoint, "30/minute")


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom rate limit exceeded handler"""
    return Response(
        content={
            "error": "Rate limit exceeded",
            "detail": f"You have exceeded the rate limit. Please try again later.",
            "retry_after": exc.detail
        },
        status_code=429,
        headers={"Retry-After": str(exc.detail)}
    )
