"""
API Gateway Service - Entry point for all backend requests
Handles auth, routing, rate limiting, and security
"""

from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware
import httpx
import os
from datetime import datetime
from typing import Optional

app = FastAPI(
    title="Ungouge API Gateway",
    description="Entry point for all backend API requests",
    version="2.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
COST_MODEL_SERVICE_URL = os.getenv("COST_MODEL_SERVICE_URL", "http://cost-model:8001")
QUOTE_EXTRACTOR_SERVICE_URL = os.getenv("QUOTE_EXTRACTOR_SERVICE_URL", "http://quote-extractor:8002")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", "dev-csrf-secret")

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Session middleware (for CSRF)
app.add_middleware(SessionMiddleware, secret_key=CSRF_SECRET_KEY)

# Trusted hosts (production only)
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["ungouge.ai", "*.ungouge.ai"]
    )

# HTTP client for service calls
http_client: Optional[httpx.AsyncClient] = None

@app.on_event("startup")
async def startup():
    global http_client
    http_client = httpx.AsyncClient(timeout=60.0)

@app.on_event("shutdown")
async def shutdown():
    if http_client:
        await http_client.aclose()

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    if ENVIRONMENT == "production":
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "frame-src https://js.stripe.com; "
            "connect-src 'self' https://api.stripe.com"
        )
    
    return response

# Health checks
@app.get("/health/live")
async def liveness():
    """Liveness probe"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/ready")
async def readiness():
    """Readiness probe - checks downstream services"""
    checks = {
        "cost_model": "unknown",
        "quote_extractor": "unknown",
        "database": "unknown",
    }
    
    # Check cost model service
    try:
        response = await http_client.get(f"{COST_MODEL_SERVICE_URL}/health/live", timeout=3.0)
        checks["cost_model"] = "ok" if response.status_code == 200 else "error"
    except Exception:
        checks["cost_model"] = "error"
    
    # Check quote extractor service
    try:
        response = await http_client.get(f"{QUOTE_EXTRACTOR_SERVICE_URL}/health/live", timeout=3.0)
        checks["quote_extractor"] = "ok" if response.status_code == 200 else "error"
    except Exception:
        checks["quote_extractor"] = "error"
    
    # Check database (would query actual DB in real implementation)
    checks["database"] = "ok"  # Placeholder
    
    is_ready = all(v == "ok" for v in checks.values())
    status_code = 200 if is_ready else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Proxy endpoints to downstream services

@app.post("/api/v2/quotes/analyze")
@limiter.limit("20/minute")
async def analyze_quote(request: Request):
    """
    Proxy to cost model service for quote analysis
    """
    # TODO: Add auth middleware
    # TODO: Validate request
    
    body = await request.json()
    
    try:
        response = await http_client.post(
            f"{COST_MODEL_SERVICE_URL}/analyze",
            json=body,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=getattr(e.response, 'status_code', 500),
            detail=f"Cost model service error: {str(e)}"
        )

@app.post("/api/v2/quotes/extract")
@limiter.limit("10/minute")
async def extract_quote(request: Request):
    """
    Proxy to quote extractor service
    """
    # TODO: Add auth middleware
    # TODO: Validate request
    
    body = await request.json()
    
    try:
        response = await http_client.post(
            f"{QUOTE_EXTRACTOR_SERVICE_URL}/extract",
            json=body,
            timeout=300.0  # 5 minutes for Vision API
        )
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=getattr(e.response, 'status_code', 500),
            detail=f"Quote extractor service error: {str(e)}"
        )

# Authentication endpoints (placeholder - extract from backend/routers/auth.py)

@app.post("/api/v2/auth/register")
@limiter.limit("3/hour")
async def register(request: Request):
    """
    User registration
    TODO: Extract from backend/routers/auth.py
    """
    return {"message": "Registration endpoint - TODO: implement"}

@app.post("/api/v2/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    """
    User login
    TODO: Extract from backend/routers/auth.py
    """
    return {"message": "Login endpoint - TODO: implement"}

@app.post("/api/v2/auth/refresh")
@limiter.limit("10/minute")
async def refresh_token(request: Request):
    """
    Refresh access token
    TODO: Extract from backend/routers/auth.py
    """
    return {"message": "Token refresh endpoint - TODO: implement"}

@app.get("/api/v2/auth/profile")
async def get_profile(request: Request):
    """
    Get user profile
    TODO: Extract from backend/routers/auth.py
    """
    return {"message": "Profile endpoint - TODO: implement"}

# Stripe checkout endpoint (placeholder)

@app.post("/api/v2/payments/create-checkout")
@limiter.limit("10/minute")
async def create_checkout(request: Request):
    """
    Create Stripe Checkout session
    TODO: Extract from backend/routers/stripe_checkout.py
    """
    return {"message": "Checkout endpoint - TODO: implement"}

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error (would use proper logging in production)
    print(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
