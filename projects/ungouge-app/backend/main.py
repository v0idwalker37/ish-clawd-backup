from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel

from routers import quotes, health, auth, payments
from models.database import engine, Base
from middleware.dnt import DNTMiddleware
from middleware.security_logging import SecurityAuditMiddleware, setup_security_logging

# HIGH-08: Conditional HTTPS redirect for production deployments
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
if ENVIRONMENT == "production":
    from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# CSRF Protection Configuration
class CsrfSettings(BaseModel):
    secret_key: str = os.environ["CSRF_SECRET_KEY"] if "CSRF_SECRET_KEY" in os.environ else os.environ["JWT_SECRET_KEY"]  # Fail if not set
    cookie_samesite: str = "strict"
    cookie_secure: bool = os.getenv("ENVIRONMENT") == "production"
    cookie_httponly: bool = True

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

async def _daily_cleanup_loop():
    """Background loop that runs data retention cleanup once per day."""
    import asyncio
    import logging
    from middleware.data_retention import cleanup_expired_quotes, cleanup_expired_tokens
    from models.database import async_session_maker as AsyncSessionLocal

    logger = logging.getLogger("ungouge.retention")
    INTERVAL = 24 * 60 * 60  # 24 hours in seconds

    while True:
        try:
            async with AsyncSessionLocal() as db:
                quotes_deleted = await cleanup_expired_quotes(db)
                tokens_deleted = await cleanup_expired_tokens(db)
                logger.info(
                    f"Daily cleanup completed: {quotes_deleted} quotes, "
                    f"{tokens_deleted} tokens removed"
                )
        except Exception as e:
            logger.error(f"Daily cleanup failed: {e}")
        await asyncio.sleep(INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    import asyncio

    # Ensure all models are imported so create_all picks up their tables
    from services.token_blacklist import BlacklistedToken  # noqa: F401 — registers token_blacklist table

    # Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize structured security logging
    setup_security_logging()

    # Schedule daily data retention cleanup (GDPR compliance)
    cleanup_task = asyncio.create_task(_daily_cleanup_loop())

    yield

    # Cancel cleanup task on shutdown
    cleanup_task.cancel()
    # Cleanup on shutdown
    await engine.dispose()

app = FastAPI(
    title="Ungouge.ai API",
    description="Fair contractor quote analysis API",
    version="1.0.0",
    lifespan=lifespan,
)

# HIGH-08: Add HTTPS redirect middleware in production (must be added before other middleware)
if ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CSRF error handler
@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": "CSRF token validation failed"}
    )

# Global exception handler (catch-all for unhandled exceptions)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to prevent leaking internal error details.
    Logs full error server-side but returns generic message to client.
    """
    from fastapi.responses import JSONResponse
    from services.logger import log_error
    
    # Log full error details server-side
    log_error(
        error_type=type(exc).__name__,
        message=str(exc),
        details={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else None,
        }
    )
    
    # Return generic error to client (don't expose internals)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again later.",
            "error_id": None  # In production, return a traceable error ID
        }
    )

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Prevent MIME-type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Enable XSS protection (legacy browsers)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # HTTPS enforcement (only in production)
    if os.getenv("ENVIRONMENT") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    # Content Security Policy (basic policy, adjust as needed)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    
    return response

# GDPR R-15: DNT (Do Not Track) signal handling
app.add_middleware(DNTMiddleware)

# CORS middleware (hardened for production)
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# Add production origin if set
production_url = os.getenv("FRONTEND_URL")
if production_url and production_url not in cors_origins:
    cors_origins.append(production_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Explicit list, no wildcards
    allow_headers=["Content-Type", "Authorization", "Accept"],  # Explicit list, no wildcards
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],  # Rate limit headers
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(quotes.router, prefix="/api", tags=["quotes"])
app.include_router(payments.router, prefix="/api", tags=["payments"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ungouge.ai API",
        "version": "1.0.0",
        "docs": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
