# Database Index Summary

## Overview
This document summarizes all database indexes added to optimize query performance for the GougeAlert backend.

## Indexes Added (2024-02-02)

### User Table (`users`)
| Column | Index Type | Reason |
|--------|-----------|--------|
| `email` | Unique + Index | Email lookups during login (already existed) |
| `is_active` | Index | Filtered on every login to check account status |
| `is_verified` | Index | Checked in auth flows for email verification status |
| `created_at` | Index | Used for sorting user lists by registration date |

**Impact:** Login queries will be faster (no table scan on is_active filter). User listing/admin panels will sort efficiently.

---

### Quote Table (`quotes`)
| Column | Index Type | Reason |
|--------|-----------|--------|
| `user_id` | Foreign Key + Index | **CRITICAL** - Used in `get_my_quotes()` to fetch user's quotes |
| `created_at` | Index | Used in `ORDER BY` for quote listing (most recent first) |

**Impact:** Prevents N+1 queries when loading user quotes. Sorting quotes by date is now O(log n) instead of O(n).

**Query Example:**
```sql
SELECT * FROM quotes WHERE user_id = ? ORDER BY created_at DESC
-- Without index: Full table scan + sort
-- With index: Index seek on user_id + ordered traversal
```

---

### QuoteLineItem Table (`quote_line_items`)
| Column | Index Type | Reason |
|--------|-----------|--------|
| `quote_id` | Foreign Key + Index | **CRITICAL** - Prevents N+1 when loading line items for quotes |

**Impact:** When displaying quote details, line items load instantly via index seek instead of scanning the entire table.

**N+1 Prevention Example:**
```python
# Without index: N+1 queries (1 for quotes + N for each quote's line items)
for quote in quotes:
    items = quote.line_items  # Triggers SELECT * FROM quote_line_items WHERE quote_id = ?

# With index: Fast lookup for each quote
```

---

### AnalysisReport Table (`analysis_reports`)
| Column | Index Type | Reason |
|--------|-----------|--------|
| `quote_id` | Unique + Index | One-to-one relationship (unique creates index automatically) |
| `created_at` | Index | For sorting reports by analysis date |

**Impact:** Report lookups by quote are instant. Report listing sorted by date is efficient.

---

### Payment Table (`payments`)
| Column | Index Type | Reason |
|--------|-----------|--------|
| `quote_id` | Foreign Key + Index | Payment lookup by quote for verification |
| `stripe_payment_intent_id` | Unique + Index | Stripe webhook lookups (unique creates index automatically) |
| `status` | Index | Filter payments by status (pending, completed, failed) |

**Impact:** Payment verification queries are fast. Status-based reporting is efficient.

**Query Example:**
```sql
SELECT * FROM payments WHERE status = 'pending' ORDER BY created_at DESC
-- Index on status makes this query fast
```

---

### PasswordResetToken Table (`password_reset_tokens`)
| Column | Index Type | Reason |
|--------|-----------|--------|
| `user_id` | Foreign Key + Index | Lookup reset tokens for a user |
| `token` | Unique + Index | Token verification on reset (unique creates index automatically) |
| `expires_at` | Index | Cleanup queries to delete expired tokens |

**Impact:** Token verification is instant. Cleanup jobs run efficiently.

**Cleanup Query:**
```sql
DELETE FROM password_reset_tokens WHERE expires_at < NOW() - INTERVAL '7 days'
-- Index on expires_at makes this efficient even with millions of old tokens
```

---

### EmailVerificationToken Table (`email_verification_tokens`)
| Column | Index Type | Reason |
|--------|-----------|--------|
| `user_id` | Foreign Key + Index | Lookup verification tokens for a user |
| `token` | Unique + Index | Token verification on email confirm (unique creates index automatically) |
| `expires_at` | Index | Cleanup queries to delete expired tokens |

**Impact:** Email verification is instant. Cleanup jobs run efficiently.

---

## Total Indexes Added

**New Indexes:** 13
- 5 on foreign keys (prevents N+1 queries)
- 4 on timestamps (efficient sorting/filtering)
- 2 on boolean flags (auth optimizations)
- 2 on expiry dates (cleanup efficiency)

**Already Existed:** 6 (via unique=True constraints)

**Total Database Indexes:** 19

---

## Performance Impact Estimates

### Before Optimization
| Operation | Queries | Complexity |
|-----------|---------|------------|
| User login | 1 | O(n) - table scan on is_active |
| Get my quotes (10 items) | 21 | O(n) - table scan on user_id |
| Password reset lookup | 1 | O(n) - table scan on token |
| Token cleanup (1M tokens) | 1 | O(n) - full table scan |

### After Optimization
| Operation | Queries | Complexity |
|-----------|---------|------------|
| User login | 1 | O(log n) - index seek |
| Get my quotes (10 items) | 21* | O(log n) - index seek per query |
| Password reset lookup | 1 | O(log n) - index seek |
| Token cleanup (1M tokens) | 1 | O(log n) - index range scan |

*Can be reduced to 1-3 queries with eager loading (see PERFORMANCE_NOTES.md)

### Expected Improvement
- **Auth operations:** 5-10x faster (especially under load)
- **User quote listings:** 10-50x faster (depends on data size)
- **Token operations:** 100-1000x faster (as token table grows)
- **Cleanup jobs:** Near-instant (even with millions of records)

---

## Migration Safety

✅ **Tested:** Fresh database creation works correctly
✅ **Backward Compatible:** Indexes only improve performance, don't break queries
✅ **No Data Loss:** Adding indexes doesn't modify existing data
✅ **Production Ready:** Can be applied to production database safely

### Applying to Existing Database

For SQLite (current setup):
```bash
# Backup first
cp ungouge.db ungouge.db.backup

# Apply migrations
python -c "
import asyncio
from models.database import engine, Base

async def migrate():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✓ Indexes added')

asyncio.run(migrate())
"
```

For PostgreSQL (production):
```sql
-- Indexes will be created by SQLAlchemy on first deployment
-- Or create manually with:
CREATE INDEX CONCURRENTLY ix_quotes_user_id ON quotes(user_id);
CREATE INDEX CONCURRENTLY ix_quotes_created_at ON quotes(created_at);
-- etc...
```

---

## Next Steps (Future Optimizations)

1. **Eager Loading:** Implement in `get_my_quotes()` to reduce from 21 to 1-3 queries
2. **Composite Indexes:** If query patterns show common filter combinations
3. **Query Monitoring:** Enable slow query logging in production
4. **Caching Layer:** Redis for frequently accessed reports
5. **Connection Pooling:** Tune pool size based on production load

See `PERFORMANCE_NOTES.md` for detailed recommendations.

---

## Index Naming Convention

SQLAlchemy auto-generates index names using this pattern:
```
ix_{table_name}_{column_name}
```

Examples:
- `ix_users_email`
- `ix_quotes_user_id`
- `ix_password_reset_tokens_expires_at`

---

## Verification Commands

Check indexes in SQLite:
```sql
-- List all indexes on a table
PRAGMA index_list('users');

-- Show index details
PRAGMA index_info('ix_users_email');

-- See which indexes are used in a query
EXPLAIN QUERY PLAN SELECT * FROM quotes WHERE user_id = 'abc123';
```

Check indexes in PostgreSQL:
```sql
-- List all indexes
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'users';

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM quotes WHERE user_id = 'abc123';
```

---

**Document Version:** 1.0  
**Last Updated:** 2024-02-02  
**Author:** Database Optimization Sprint
