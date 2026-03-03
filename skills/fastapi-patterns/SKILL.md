---
name: fastapi-patterns
description: Production-ready FastAPI patterns for ungouge.ai backend. Covers async patterns, dependency injection, error handling, Pydantic validation, database sessions, authentication, API design, and performance optimization. Use when building API endpoints, implementing business logic, handling errors, validating data, managing database connections, securing endpoints, or optimizing FastAPI performance.
---

# FastAPI Patterns

Production-ready patterns for building robust FastAPI applications.

## Core Patterns

### Dependency Injection

**Database Session:**
```python
# app/dependencies.py
from sqlalchemy.orm import Session
from app.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoints
@app.get("/quotes")
def get_quotes(db: Session = Depends(get_db)):
    return db.query(Quote).all()
```

**Current User:**
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
```

### Error Handling

**Custom Exception Handler:**
```python
from fastapi import Request
from fastapi.responses import JSONResponse

class QuoteNotFoundError(Exception):
    def __init__(self, quote_id: int):
        self.quote_id = quote_id

@app.exception_handler(QuoteNotFoundError)
async def quote_not_found_handler(request: Request, exc: QuoteNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Quote {exc.quote_id} not found"}
    )
```

**Validation Errors:**
```python
from pydantic import BaseModel, Field, validator

class QuoteCreate(BaseModel):
    project_type: str = Field(..., min_length=3, max_length=100)
    quote_amount: float = Field(..., gt=0)
    contractor_name: str = Field(..., min_length=2, max_length=200)
    
    @validator('quote_amount')
    def validate_amount(cls, v):
        if v > 1000000:
            raise ValueError('Quote amount exceeds reasonable limit')
        return v
```

### Async Patterns

**Async Endpoint with Database:**
```python
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/quotes/{quote_id}")
async def get_quote(
    quote_id: int,
    db: AsyncSession = Depends(get_async_db)
) -> QuoteResponse:
    result = await db.execute(
        select(Quote).where(Quote.id == quote_id)
    )
    quote = result.scalar_one_or_none()
    if not quote:
        raise QuoteNotFoundError(quote_id)
    return quote
```

**Concurrent External API Calls:**
```python
import asyncio

async def analyze_quote_complete(quote_data: dict):
    # Run multiple API calls concurrently
    gemini_task = asyncio.create_task(analyze_with_gemini(quote_data))
    rsmeans_task = asyncio.create_task(get_rsmeans_data(quote_data))
    
    gemini_result, rsmeans_result = await asyncio.gather(
        gemini_task, rsmeans_task
    )
    
    return combine_analysis(gemini_result, rsmeans_result)
```

### API Design

**Consistent Response Format:**
```python
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

@app.post("/quotes", response_model=APIResponse[QuoteResponse])
async def create_quote(quote: QuoteCreate, db: Session = Depends(get_db)):
    new_quote = Quote(**quote.dict())
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    
    return APIResponse(success=True, data=new_quote)
```

**Pagination:**
```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

@app.get("/quotes", response_model=PaginatedResponse[QuoteResponse])
async def list_quotes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * page_size
    
    quotes = db.query(Quote).offset(offset).limit(page_size).all()
    total = db.query(Quote).count()
    
    return PaginatedResponse(
        items=quotes,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )
```

### Security Patterns

**Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/quotes/analyze")
@limiter.limit("10/minute")
async def analyze_quote(
    request: Request,
    quote: QuoteCreate,
    current_user: User = Depends(get_current_user)
):
    # Analysis logic
    pass
```

**Input Sanitization:**
```python
from bleach import clean

class QuoteCreate(BaseModel):
    contractor_name: str
    
    @validator('contractor_name')
    def sanitize_name(cls, v):
        # Remove HTML tags and dangerous characters
        return clean(v, tags=[], strip=True)
```

## Complete Example: Quote Analysis Endpoint

```python
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@app.post(
    "/api/v1/quotes/analyze",
    response_model=APIResponse[QuoteAnalysisResponse],
    status_code=201,
    tags=["quotes"],
    summary="Analyze a quote for potential overpricing"
)
async def analyze_quote(
    quote_data: QuoteCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> APIResponse[QuoteAnalysisResponse]:
    """
    Analyze a quote using RSMeans data and AI evaluation.
    
    - **project_type**: Type of construction project
    - **quote_amount**: Total quoted amount in USD
    - **contractor_name**: Name of the contractor
    - **line_items**: Optional itemized breakdown
    """
    try:
        # Create database record
        quote = Quote(
            user_id=current_user.id,
            **quote_data.dict()
        )
        db.add(quote)
        db.commit()
        db.refresh(quote)
        
        logger.info(f"Quote {quote.id} created by user {current_user.id}")
        
        # Perform analysis (async for speed)
        analysis_result = await perform_analysis(quote_data.dict(), db)
        
        # Update quote with analysis
        quote.analysis = analysis_result
        db.commit()
        
        # Queue background tasks (email, logging, etc.)
        background_tasks.add_task(
            send_analysis_email,
            user_email=current_user.email,
            quote_id=quote.id
        )
        
        return APIResponse(
            success=True,
            data=QuoteAnalysisResponse(
                id=quote.id,
                analysis=analysis_result,
                created_at=quote.created_at
            )
        )
        
    except ExternalServiceError as e:
        logger.error(f"External service error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Analysis service temporarily unavailable"
        )
    except Exception as e:
        logger.exception("Unexpected error during quote analysis")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred processing your quote"
        )
```

## Performance Optimization

**Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_location_factor(location: str) -> float:
    """Cache location factors to avoid repeated DB queries."""
    return db.query(LocationFactor).filter_by(location=location).first()
```

**Database Query Optimization:**
```python
# Bad: N+1 query problem
quotes = db.query(Quote).all()
for quote in quotes:
    user = quote.user  # Triggers separate query

# Good: Eager loading
quotes = db.query(Quote).options(joinedload(Quote.user)).all()
for quote in quotes:
    user = quote.user  # No additional query
```

**Connection Pooling:**
```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True  # Verify connections before use
)
```

## Best Practices

✅ **DO**:
- Use dependency injection for database sessions and auth
- Implement proper error handling and logging
- Validate all inputs with Pydantic
- Use async for I/O-bound operations
- Cache expensive computations
- Use background tasks for non-blocking operations
- Implement rate limiting
- Use structured logging

❌ **DON'T**:
- Store sessions in global variables
- Ignore validation errors
- Make external API calls synchronously
- Return raw exceptions to clients
- Hardcode secrets
- Skip input sanitization
- Use `SELECT *` in production
- Ignore connection pooling

For comprehensive FastAPI patterns, consult the [Next.js Expert skill](../nextjs-expert/) as a reference for similar architectural patterns.
