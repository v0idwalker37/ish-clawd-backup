"""
Simple in-memory rate limiter for FastAPI.
No external dependencies — uses only Python stdlib.

Usage:
    from rate_limiter import RateLimiter, rate_limit

    limiter = RateLimiter()

    @app.post("/endpoint")
    @rate_limit(limiter, "30/minute")
    async def endpoint(request: Request):
        ...
"""

import time
import functools
from collections import defaultdict
from typing import Optional
from fastapi import Request, HTTPException


class RateLimiter:
    """Thread-safe in-memory rate limiter using sliding window."""

    def __init__(self):
        # {key: [(timestamp, ...), ...]}
        self._hits = defaultdict(list)

    def _clean(self, key: str, window_seconds: float):
        """Remove expired entries."""
        cutoff = time.monotonic() - window_seconds
        self._hits[key] = [t for t in self._hits[key] if t > cutoff]

    def is_allowed(self, key: str, max_hits: int, window_seconds: float) -> bool:
        """Check if a request is allowed and record it if so."""
        self._clean(key, window_seconds)
        if len(self._hits[key]) >= max_hits:
            return False
        self._hits[key].append(time.monotonic())
        return True

    def remaining(self, key: str, max_hits: int, window_seconds: float) -> int:
        """Return remaining requests in window."""
        self._clean(key, window_seconds)
        return max(0, max_hits - len(self._hits[key]))


def _parse_limit(limit_string: str) -> tuple:
    """Parse '30/minute' into (30, 60.0)."""
    parts = limit_string.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid limit format: {limit_string}. Use 'N/period'.")

    max_hits = int(parts[0])
    period = parts[1].strip().lower()

    period_map = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
    }

    seconds = period_map.get(period)
    if seconds is None:
        raise ValueError(f"Unknown period: {period}. Use second/minute/hour/day.")

    return (max_hits, seconds)


def _get_client_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For behind proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def rate_limit(limiter: RateLimiter, limit_string: str, key_prefix: Optional[str] = None):
    """
    Decorator for FastAPI endpoints.

    Usage:
        @rate_limit(limiter, "30/minute")
        async def my_endpoint(request: Request, ...):
            ...

    The decorated function MUST accept `request: Request` as a parameter.
    """
    max_hits, window_seconds = _parse_limit(limit_string)

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request is None:
                return await func(*args, **kwargs)

            ip = _get_client_ip(request)
            prefix = key_prefix or func.__name__
            key = f"{prefix}:{ip}"

            if not limiter.is_allowed(key, max_hits, window_seconds):
                remaining = 0
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={
                        "X-RateLimit-Limit": str(max_hits),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(window_seconds)),
                        "Retry-After": str(int(window_seconds)),
                    }
                )

            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request is None:
                return func(*args, **kwargs)

            ip = _get_client_ip(request)
            prefix = key_prefix or func.__name__
            key = f"{prefix}:{ip}"

            if not limiter.is_allowed(key, max_hits, window_seconds):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={
                        "X-RateLimit-Limit": str(max_hits),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(window_seconds)),
                        "Retry-After": str(int(window_seconds)),
                    }
                )

            return func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
