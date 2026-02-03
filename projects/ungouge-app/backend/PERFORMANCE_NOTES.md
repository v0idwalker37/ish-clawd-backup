# Database Performance Analysis & Optimizations

## Date: 2024-02-02

## Critical Issues Found

### 1. Missing Foreign Key Indexes (N+1 Query Risk)
**Impact:** High - Will cause performance degradation under load

The following foreign keys were **not indexed**, causing potential N+1 query problems:

- `Quote.user_id` → Referenced in `get_my_quotes()` - **CRITICAL**
- `QuoteLineItem.quote_id` → Accessed when loading quote details
- `Payment.quote_id` → Used for payment verification
- `PasswordResetToken.user_id` → Token lookup by user
- `EmailVerificationToken.user_id` → Token lookup by user

**Why this matters:** SQLAlchemy relationships will generate individual queries for each parent record when these aren't indexed, causing O(N) query complexity instead of O(1).

### 2. Missing Query Optimization Indexes

**Timestamp Sorting:**
- `Quote.created_at` → Used in `ORDER BY` in `get_my_quotes()` and `list_quotes()`
- `User.created_at` → For user listing/sorting

**Filter Conditions:**
- `User.is_active` → Checked on every login
- `User.is_verified` → Checked in auth flows
- `Payment.status` → For filtering payment states

**Cleanup Operations:**
- `PasswordResetToken.expires_at` → For expired token cleanup jobs
- `EmailVerificationToken.expires_at` → For expired token cleanup jobs

### 3. N+1 Query Risks in Routers

#### `quotes.py::get_my_quotes()` (Line ~188)
```python
# Current code loads quotes but doesn't eager load relationships
result = await db.execute(
    select(Quote)
    .where(Quote.user_id == current_user.id)
    .order_by(Quote.created_at.desc())
)
```

**Risk:** If we later access `quote.line_items` or `quote.analysis_report`, it will trigger N additional queries.

**Solution (Future):** Use eager loading:
```python
from sqlalchemy.orm import selectinload

result = await db.execute(
    select(Quote)
    .options(
        selectinload(Quote.line_items),
        selectinload(Quote.analysis_report)
    )
    .where(Quote.user_id == current_user.id)
    .order_by(Quote.created_at.desc())
)
```

#### `quotes.py::get_quote_report()` (Line ~88)
Two separate queries instead of a join - minor efficiency issue but acceptable for now.

## Optimizations Implemented

### Added Indexes:

1. **Foreign Keys (Critical):**
   - `Quote.user_id` 
   - `QuoteLineItem.quote_id`
   - `Payment.quote_id`
   - `PasswordResetToken.user_id`
   - `EmailVerificationToken.user_id`

2. **Timestamp Indexes (High Volume):**
   - `Quote.created_at`
   - `User.created_at`
   - `AnalysisReport.created_at`

3. **Boolean Filter Indexes:**
   - `User.is_active`
   - `User.is_verified`

4. **Status/Cleanup Indexes:**
   - `Payment.status`
   - `PasswordResetToken.expires_at`
   - `EmailVerificationToken.expires_at`

### Composite Index Opportunities (Future)

If query patterns evolve, consider these composite indexes:

```python
# For user quote history with filtering
Index('ix_quotes_user_created', Quote.user_id, Quote.created_at.desc())

# For active verified user lookups
Index('ix_users_active_verified', User.is_active, User.is_verified)

# For token cleanup with user context
Index('ix_reset_tokens_user_expires', PasswordResetToken.user_id, PasswordResetToken.expires_at)
```

## Production Recommendations

### 1. Query Monitoring
- Enable slow query logging (>100ms threshold)
- Monitor query patterns in production
- Use `EXPLAIN ANALYZE` for optimization

### 2. Eager Loading Strategy
Review and update relationship loading as the app grows:
```python
# Good: Explicit eager loading
.options(selectinload(Quote.line_items))

# Bad: Lazy loading in loops
for quote in quotes:
    print(quote.line_items)  # N+1 query!
```

### 3. Database Connection Pool
For production with high concurrency:
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Adjust based on load
    max_overflow=10,
    pool_pre_ping=True,    # Verify connections
)
```

### 4. Caching Strategy
Consider caching for:
- User profiles (Redis, 5-10 min TTL)
- Quote reports (Redis, 1 hour TTL)
- BLS wage data (In-memory, 24 hour TTL)

### 5. Periodic Cleanup Jobs
Create cron jobs to delete expired tokens:
```python
# Delete expired password reset tokens (older than expiry + 7 days)
DELETE FROM password_reset_tokens 
WHERE expires_at < NOW() - INTERVAL '7 days';

# Delete expired email verification tokens (older than expiry + 30 days)
DELETE FROM email_verification_tokens 
WHERE expires_at < NOW() - INTERVAL '30 days';
```

## Testing

Verify migrations work:
```bash
# Backup current database
cp ungouge.db ungouge.db.backup

# Drop and recreate (dev only)
rm ungouge.db
python -c "
from models.database import engine, Base
import asyncio

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
asyncio.run(init_db())
"
```

## Impact Estimate

**Before Optimization:**
- User login → 1 query
- Get my quotes (10 items) → 1 + 10 (line items) + 10 (reports) = 21 queries
- Password reset lookup → Full table scan on unindexed token

**After Optimization:**
- User login → 1 query (indexed email, is_active)
- Get my quotes (10 items) → Still 21 queries BUT with eager loading could be 1-3 queries
- Password reset lookup → Index seek (milliseconds vs seconds)

**Expected improvement:** 5-10x faster on high-volume operations, especially user quote listings and auth flows.
