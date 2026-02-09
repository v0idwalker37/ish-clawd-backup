# Ungouge.ai Fix Plan
## Prioritized Action Items from Feb 6 Audit

**Created:** 2026-02-06  
**Status:** Ready to execute

---

## 🚀 Quick Wins (Can do TODAY - ~2 hours total)

These are high-impact, low-effort fixes we can knock out immediately:

### QW-1: Remove Hardcoded JWT Secret (15 min) 🔴
**Files:** `backend/main.py:17`, `backend/services/auth.py:17`

```python
# BEFORE (vulnerable):
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")

# AFTER (secure):
SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # Fails if not set
```

**Also add to startup validation.**

---

### QW-2: Remove Token Logging (10 min) 🔴
**File:** `backend/routers/auth.py` - lines 122-127, 338-345, 390-397, 450-457

Delete or wrap in dev-only check:
```python
if os.getenv("ENVIRONMENT") != "production":
    logger.info("...", extra={"token": verification_token})
```

---

### QW-3: Add Auth to Quote List Endpoint (10 min) 🔴
**File:** `backend/routers/quotes.py:179-196`

```python
@router.get("/quotes")
async def list_quotes(
    current_user: User = Depends(get_current_user),  # ADD THIS
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),  # ADD MAX
    db: AsyncSession = Depends(get_db),
):
    # Only return current user's quotes, not all
    result = await db.execute(
        select(Quote).where(Quote.user_id == current_user.id)...
    )
```

---

### QW-4: Fix Report Endpoint Auth (5 min) 🔴
**File:** `backend/routers/quotes.py:167-177`

```python
@router.get("/quotes/{quote_id}/report", response_model=ReportModel)
async def get_quote_full_report(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ADD THIS
):
    return await get_quote_report(quote_id, db, current_user)  # PASS IT
```

---

### QW-5: Add Password Validation on Reset (5 min) 🟠
**File:** `backend/routers/auth.py:351-405`

```python
from validators import validate_password

@router.post("/auth/reset-password")
async def reset_password(request: PasswordResetVerify, ...):
    # ADD THIS before setting password:
    try:
        validate_password(request.new_password)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    user.password_hash = hash_password(request.new_password)
```

---

### QW-6: Add Pagination Limits (5 min) 🟡
**File:** `backend/routers/quotes.py:149-165`

```python
from fastapi import Query

async def get_my_quotes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),  # Max 100
    ...
):
```

---

### QW-7: Fix HEIC Mismatch (10 min) 🟠
**Option A - Remove from frontend:**
**File:** `frontend/src/components/FileUpload.tsx:61`
```typescript
const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
// Remove 'image/heic'
```

**Option B - Add to backend (requires pillow-heif):**
```bash
pip install pillow-heif
```
Then add 'image/heic' to `backend/validators.py:24-28`

---

## 📋 Phase 1: Auth Architecture Fix (4-6 hours)

This is the big one - connecting frontend to backend's cookie-based auth.

### P1-1: Backend Cookie Auth Response
**File:** `backend/routers/auth.py` - login endpoint

```python
from fastapi import Response

@router.post("/auth/login")
async def login(
    credentials: LoginCredentials,
    response: Response,  # ADD
    db: AsyncSession = Depends(get_db),
):
    # ... existing auth logic ...
    
    # Instead of returning token in JSON:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=1800,
        path="/"
    )
    
    return {
        "message": "Login successful",
        "user": {"id": user.id, "name": user.name, "email": user.email}
        # NO token in body
    }
```

### P1-2: Backend CSRF Enforcement
**File:** `backend/main.py` and protected routes

Enable CSRF validation on state-changing endpoints.

### P1-3: Frontend Remove localStorage
**Files:** `frontend/src/app/login/page.tsx`, `register/page.tsx`

```typescript
// DELETE these lines:
localStorage.setItem('token', data.token);

// ADD credentials to all fetch calls:
const response = await fetch(url, {
  credentials: 'include',
  // ...
});
```

### P1-4: Frontend Add 401 Interceptor
**File:** `frontend/src/lib/api.ts` (new)

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      window.location.href = '/login?session_expired=true';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### P1-5: Update All API Calls
Replace `axios` with the new `api` instance everywhere.

---

## 📋 Phase 2: Payment Flow (8-12 hours)

### P2-1: Backend Stripe Integration
- Create payment intent endpoint
- Implement webhook handler
- Generate report only after payment confirmed

### P2-2: Frontend Payment Page
- Install `@stripe/stripe-js`
- Create `/payment/[id]/page.tsx`
- Add Stripe Elements form
- Handle success/failure redirects

### P2-3: Update Quote Flow
- After analysis, redirect to payment
- After payment, redirect to report

---

## 📋 Phase 3: Stability (4-6 hours)

### P3-1: Error Handler Utility
Create `frontend/src/lib/errors.ts` to parse both error formats.

### P3-2: Token Blacklist Persistence
Switch from in-memory dict to Redis or database.

### P3-3: Expired Token Cleanup Job
Add background task to delete old tokens.

### P3-4: Error Boundary
Add React error boundary to layout.

---

## 🎯 Execution Order

### Today (Feb 6)
- [ ] QW-1: Remove hardcoded JWT secret
- [ ] QW-2: Remove token logging
- [ ] QW-3: Add auth to quote list
- [ ] QW-4: Fix report endpoint auth
- [ ] QW-5: Password validation on reset
- [ ] QW-6: Pagination limits
- [ ] QW-7: Fix HEIC mismatch

### This Week
- [ ] P1-1 through P1-5: Auth architecture

### Next Week
- [ ] P2-1 through P2-3: Payment flow

### Following Week
- [ ] P3-1 through P3-4: Stability

---

## 📊 Progress Tracker

| Task | Status | Time | Notes |
|------|--------|------|-------|
| QW-1 | ✅ | 15m | JWT secret now fails if not set |
| QW-2 | ✅ | 10m | Token logging wrapped in dev-only check |
| QW-3 | ✅ | 10m | /quotes endpoint now requires auth, filters by user |
| QW-4 | ✅ | 5m | /quotes/{id}/report now passes current_user |
| QW-5 | ✅ | 5m | Password reset now validates password strength |
| QW-6 | ✅ | 5m | Pagination limits enforced (max 100) |
| QW-7 | ✅ | 10m | Removed HEIC from frontend (matches backend) |
| P1-1 | ✅ | 1h | Backend sets httpOnly cookies on login/register/refresh |
| P1-2 | ✅ | 30m | Auth service reads from cookies OR Bearer |
| P1-3 | ✅ | 30m | Frontend removed localStorage, uses credentials:include |
| P1-4 | ✅ | 20m | Created /lib/api.ts with 401 interceptor |
| P1-5 | ✅ | 40m | Updated all API calls: login, register, dashboard, quotes, report |

**Quick Wins completed:** 2026-02-06 @ 9:15 AM EST

---

**Ready to start with Quick Wins?**
