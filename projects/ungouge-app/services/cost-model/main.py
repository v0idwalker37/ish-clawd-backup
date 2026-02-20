"""
Cost Model Service - Microservice for quote cost analysis
Extracted from monolithic quote_analyzer.py
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import redis.asyncio as redis
import json
import hashlib
import os
from datetime import datetime

app = FastAPI(
    title="Ungouge Cost Model Service",
    description="Calculates fair market pricing for contractor quotes",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client: Optional[redis.Redis] = None

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()

# Pydantic models
class LineItem(BaseModel):
    description: str
    quantity: float
    unit: str
    unit_price: float
    
    @property
    def total(self) -> float:
        return self.quantity * self.unit_price

class Location(BaseModel):
    zip_code: str
    state: Optional[str] = None
    city: Optional[str] = None

class CostAnalysisRequest(BaseModel):
    quote_id: str
    line_items: List[LineItem]
    location: Location
    project_type: str = Field(..., description="e.g., flooring, roofing, hvac")
    total_quoted: Optional[float] = None

class CostBreakdownItem(BaseModel):
    category: str
    estimated_cost: float
    quoted_cost: float
    variance: float
    variance_pct: float
    flag: Optional[str] = None  # "high", "low", "extreme", None

class CostAnalysisResponse(BaseModel):
    quote_id: str
    total_cost: float
    fair_price_range: Dict[str, float]  # min, max
    confidence_score: float  # 0-1
    fairness_score: int  # 0-100
    verdict: str  # "suspiciously_low", "fair", "slightly_high", "overpriced"
    breakdown: List[CostBreakdownItem]
    recommendations: List[str]
    flags: List[str]
    location_factor: float
    analyzed_at: str

# Health checks
@app.get("/health/live")
async def liveness():
    return {"status": "ok"}

@app.get("/health/ready")
async def readiness():
    # Check Redis connectivity
    try:
        await redis_client.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "error"
        
    is_ready = redis_status == "ok"
    
    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": {
            "redis": redis_status
        }
    }

def generate_cache_key(request: CostAnalysisRequest) -> str:
    """Generate deterministic cache key from request data"""
    # Sort line items for consistency
    items_data = sorted([
        (item.description, item.quantity, item.unit, item.unit_price)
        for item in request.line_items
    ])
    
    cache_data = {
        "line_items": items_data,
        "location": request.location.zip_code,
        "project_type": request.project_type
    }
    
    cache_str = json.dumps(cache_data, sort_keys=True)
    hash_digest = hashlib.sha256(cache_str.encode()).hexdigest()
    return f"cost:analysis:{request.quote_id}:{hash_digest[:16]}"

@app.post("/analyze", response_model=CostAnalysisResponse)
async def analyze_quote(request: CostAnalysisRequest):
    """
    Analyze quote and return cost breakdown with fairness assessment
    """
    
    # Check cache first
    cache_key = generate_cache_key(request)
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return CostAnalysisResponse(**json.loads(cached))
    except Exception:
        pass  # Cache miss, proceed with analysis
    
    # Perform cost analysis
    result = await _analyze_quote_logic(request)
    
    # Cache result (1 hour TTL)
    try:
        await redis_client.setex(
            cache_key,
            3600,  # 1 hour
            json.dumps(result.dict())
        )
    except Exception:
        pass  # Cache write failure shouldn't block response
    
    return result

async def _analyze_quote_logic(request: CostAnalysisRequest) -> CostAnalysisResponse:
    """
    Core cost analysis logic (extracted from quote_analyzer.py)
    TODO: Import actual cost model data and RSMeans factors
    """
    
    # Placeholder implementation - will import real logic from monolith
    # For now, return mock analysis
    
    total_quoted = request.total_quoted or sum(item.total for item in request.line_items)
    
    # Mock: Assume fair range is ±20% of quoted amount
    fair_min = total_quoted * 0.80
    fair_max = total_quoted * 1.20
    
    # Mock location factor (Vermont = 0.95)
    location_factor = 0.95
    
    # Mock fairness score (60 = middle of fair range)
    fairness_score = 60
    
    # Mock breakdown
    breakdown = [
        CostBreakdownItem(
            category="Labor",
            estimated_cost=total_quoted * 0.60,
            quoted_cost=total_quoted * 0.60,
            variance=0.0,
            variance_pct=0.0,
            flag=None
        ),
        CostBreakdownItem(
            category="Materials",
            estimated_cost=total_quoted * 0.35,
            quoted_cost=total_quoted * 0.35,
            variance=0.0,
            variance_pct=0.0,
            flag=None
        ),
        CostBreakdownItem(
            category="Overhead",
            estimated_cost=total_quoted * 0.05,
            quoted_cost=total_quoted * 0.05,
            variance=0.0,
            variance_pct=0.0,
            flag=None
        )
    ]
    
    return CostAnalysisResponse(
        quote_id=request.quote_id,
        total_cost=total_quoted,
        fair_price_range={"min": fair_min, "max": fair_max},
        confidence_score=0.75,
        fairness_score=fairness_score,
        verdict="fair",
        breakdown=breakdown,
        recommendations=[
            "Quote appears to be within normal market range",
            "Consider getting 2-3 additional quotes for comparison"
        ],
        flags=[],
        location_factor=location_factor,
        analyzed_at=datetime.utcnow().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
