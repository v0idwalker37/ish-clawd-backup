from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from models.database import get_db
import time

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint
    Returns API status and database connectivity
    """
    start_time = time.time()
    
    # Check database connection
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    response_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "response_time_ms": round(response_time, 2),
        "version": "1.0.0",
    }

@router.get("/health/ready")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    """
    return {"ready": True}

@router.get("/health/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    """
    return {"alive": True}
