"""
Health check endpoints for GougeAlert API

Provides:
  GET /health           — Basic health + DB status + version + uptime
  GET /health/ready     — Readiness probe (DB connection verified)
  GET /health/live      — Liveness probe (always responds if process is alive)
  GET /api/health/detailed — Full system status (auth optional, more detail)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from models.database import get_db
import time
import os
import platform

router = APIRouter()

# ── Uptime tracking ─────────────────────────────────────────────────────────
_START_TIME = time.time()

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def _uptime_seconds() -> float:
    return round(time.time() - _START_TIME, 2)


def _uptime_human(seconds: float) -> str:
    """Convert seconds to human-readable uptime string."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


async def _check_database(db: AsyncSession) -> dict:
    """Check database connectivity and return status dict."""
    start = time.time()
    try:
        await db.execute(text("SELECT 1"))
        latency_ms = round((time.time() - start) * 1000, 2)
        return {"status": "connected", "latency_ms": latency_ms}
    except Exception as e:
        latency_ms = round((time.time() - start) * 1000, 2)
        return {"status": "disconnected", "latency_ms": latency_ms, "error": str(e)}


# ── GET /health ──────────────────────────────────────────────────────────────

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.

    Returns API status, database connectivity, version, and uptime.
    Used by monitoring dashboards and load balancers.
    """
    db_info = await _check_database(db)
    uptime = _uptime_seconds()

    is_healthy = db_info["status"] == "connected"

    return {
        "status": "healthy" if is_healthy else "degraded",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "uptime_seconds": uptime,
        "uptime": _uptime_human(uptime),
        "database": db_info["status"],
        "response_time_ms": db_info["latency_ms"],
    }


# ── GET /health/ready ───────────────────────────────────────────────────────

@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe — reports whether the service can accept traffic.

    Checks:
      - Database connection is alive

    Returns 200 with ready=true if all checks pass.
    Returns 200 with ready=false and details if any check fails.
    Cloud Run / k8s should treat ready=false as not ready to serve.
    """
    db_info = await _check_database(db)
    is_ready = db_info["status"] == "connected"

    return {
        "ready": is_ready,
        "checks": {
            "database": db_info,
        },
    }


# ── GET /health/live ────────────────────────────────────────────────────────

@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe — confirms the process is alive and responding.

    Does NOT check dependencies (DB, external services).
    If this fails, the process should be restarted.
    """
    return {
        "alive": True,
        "uptime_seconds": _uptime_seconds(),
    }


# ── GET /api/health/detailed ────────────────────────────────────────────────

@router.get("/api/health/detailed")
async def detailed_health(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check with system info.

    Useful for debugging and operations dashboards.
    Does NOT expose secrets or sensitive config.
    """
    db_info = await _check_database(db)
    uptime = _uptime_seconds()

    # Check optional services
    checks = {
        "database": db_info,
    }

    # Redis check (if configured)
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis as redis_lib
            r = redis_lib.from_url(redis_url, socket_timeout=2)
            r.ping()
            checks["redis"] = {"status": "connected"}
        except Exception as e:
            checks["redis"] = {"status": "disconnected", "error": str(e)}
    else:
        checks["redis"] = {"status": "not_configured"}

    # Stripe connectivity
    stripe_configured = bool(os.getenv("STRIPE_SECRET_KEY"))
    checks["stripe"] = {"status": "configured" if stripe_configured else "not_configured"}

    # Email
    email_dev_mode = os.getenv("EMAIL_DEV_MODE", "true").lower() == "true"
    smtp_configured = bool(os.getenv("SMTP_USER")) and bool(os.getenv("SMTP_PASSWORD"))
    checks["email"] = {
        "status": "dev_mode" if email_dev_mode else ("configured" if smtp_configured else "not_configured"),
    }

    all_healthy = db_info["status"] == "connected"

    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "uptime_seconds": uptime,
        "uptime": _uptime_human(uptime),
        "python_version": platform.python_version(),
        "checks": checks,
    }
