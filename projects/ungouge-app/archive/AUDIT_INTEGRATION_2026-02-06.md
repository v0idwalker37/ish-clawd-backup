# Integration & Cross-Layer Analysis Report
## Ungouge.ai Full-Stack Audit

**Date:** 2026-02-06  
**Scope:** Frontend ↔ Backend integration points  
**Purpose:** Identify mismatches, architectural gaps, and coordinated fixes

---

## Executive Summary

All three audits (full-stack, backend, frontend) identified strong individual components but **critical misalignment in the auth architecture**. The backend is configured for httpOnly cookie auth with CSRF protection, but the frontend ignores this and uses localStorage tokens. This creates a split-brain system where security features exist but aren't connected.

### Integration Health Score: ⚠️ 4/10

**Why so low?**
- Auth architecture fundamentally disconnected
- API contracts inconsistent (some endpoints missing auth checks)
- Error handling formats don't align
- Payment flow has backend skeleton but no frontend implementation
- File format support mismatch (HEIC)

---

## 🚨 Critical Integration Issues

### 1. Auth Architecture Split-Brain 🧠➡️🧠

**The Problem:**
- **Backend** has `CsrfSettings` configured, expects httpOnly cookies + CSRF tokens
- **Frontend** stores tokens in `localStorage`, never sends CSRF tokens or credentials
- Result: CSRF protection is configured but not enforced, XSS vulnerability wide open

**Evidence:**
```python
# Backend: main.py:17-19
class CsrfSettings(BaseModel):
    secret_key: str = os.getenv("JWT_SECRET_KEY", "...")
    cookie_secure: bool = True
    cookie_samesite: str = "strict"
```

```typescript
// Frontend: login/page.tsx:38
localStorage.setItem('token', data.token); // ❌ Not using cookies!
```

**Impact:**
- Anyone who can inject JS (XSS) steals the token from localStorage
- Backend's CSRF middleware is loaded but never validates requests
- Logout doesn't work properly (frontend clears localStorage, backend blacklists token, but cookies never involved)

**Coordinated Fix:**

**Backend changes:**
```python
# In routers/auth.py - Login endpoint
@router.post("/auth/login")
async def login(..., response: Response):
    # ... authentication logic ...
    
    # Set httpOnly cookie instead of returning token in JSON
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="strict",
        max_age=1800  # 30 minutes
    )
    
    # Also set CSRF token in readable cookie
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,  # Frontend needs to read this
        secure=True,
        samesite="strict"
    )
    
    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
        # NO token in response body
    }
```

**Frontend changes:**
```typescript
// Remove ALL localStorage.setItem('token', ...) calls

// In login/page.tsx
const response = await fetch(`${apiUrl}/api/auth/login`, {
  method: 'POST',
  credentials: 'include',  // ⬅️ KEY: Send cookies
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ email, password }),
});

// No token storage needed - browser handles cookies automatically
if (response.ok) {
  router.push('/dashboard');
}

// For API calls:
const response = await fetch(`${apiUrl}/api/quotes`, {
  method: 'POST',
  credentials: 'include',  // ⬅️ Always include cookies
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': getCsrfTokenFromCookie(),  // ⬅️ Add CSRF header
  },
  body: JSON.stringify(data),
});

// Helper function:
function getCsrfTokenFromCookie(): string {
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  return match ? match[1] : '';
}
```

**Priority:** 🔴 **CRITICAL** - Fixes C1 (frontend) and Critical #3 (backend)

---

### 2. Missing Authorization on Report Endpoints 🔓

**The Problem:**
- Frontend calls `GET /api/quotes/{id}` without `Authorization` header
- Backend endpoint `/quotes/{quote_id}/report` doesn't require auth (calls `get_quote_report` without `current_user`)
- Result: Anyone with a report ID can view paid reports (IDOR vulnerability)

**Evidence:**
```typescript
// Frontend: report/[id]/page.tsx:31
const response = await axios.get(`${apiUrl}/api/quotes/${reportId}`);
// ❌ No Authorization header
```

```python
# Backend: routers/quotes.py:167-177
@router.get("/quotes/{quote_id}/report", response_model=ReportModel)
async def get_quote_full_report(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await get_quote_report(quote_id, db)  # ❌ Missing current_user
```

**Coordinated Fix:**

**Backend:**
```python
@router.get("/quotes/{quote_id}/report", response_model=ReportModel)
async def get_quote_full_report(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ⬅️ Add auth
):
    return await get_quote_report(quote_id, db, current_user)
```

**Frontend:**
```typescript
// After switching to cookie auth, just add credentials:
const response = await axios.get(`${apiUrl}/api/quotes/${reportId}`, {
  withCredentials: true,  // ⬅️ Send auth cookie
});

// Or with current localStorage approach (temporary until cookie migration):
const response = await axios.get(`${apiUrl}/api/quotes/${reportId}`, {
  headers: {
    Authorization: `Bearer ${localStorage.getItem('token')}`
  }
});
```

**Priority:** 🔴 **CRITICAL** - Fixes C2 (frontend) and High #4 (backend)

---

### 3. Error Format Mismatch 📝

**The Problem:**
- Backend returns custom exception format: `{error: "...", suggestion: "...", context: {}}`
- Frontend expects FastAPI default: `{detail: "..."}` or `{detail: {error: "..."}}`
- Result: Users see "undefined" or generic messages instead of helpful errors

**Evidence:**
```python
# Backend: exceptions.py:73
return JSONResponse(
    status_code=self.status_code,
    content={
        "error": self.error,
        "suggestion": self.suggestion,
        "context": context,
    },
)
```

```typescript
// Frontend: QuoteForm.tsx:98
setError(err.response?.data?.detail || 'Failed to analyze quote');
// ❌ Looking for 'detail' but backend returns 'error'
```

**Coordinated Fix:**

**Option 1: Update Frontend (Recommended)**
```typescript
// Create error parser utility
// lib/errors.ts
export function parseApiError(error: any): string {
  const data = error.response?.data;
  
  // Backend custom exception format
  if (data?.error) {
    return data.suggestion 
      ? `${data.error}. ${data.suggestion}`
      : data.error;
  }
  
  // FastAPI default format
  if (data?.detail) {
    return typeof data.detail === 'string' 
      ? data.detail 
      : data.detail.error || 'An error occurred';
  }
  
  return 'An unexpected error occurred. Please try again.';
}

// Use everywhere:
setError(parseApiError(err));
```

**Option 2: Update Backend (Not recommended - breaks consistency)**
Return both formats during transition:
```python
return JSONResponse(
    status_code=self.status_code,
    content={
        "detail": self.error,  # FastAPI compatibility
        "error": self.error,
        "suggestion": self.suggestion,
    },
)
```

**Priority:** 🟡 **MEDIUM** - Improves UX but not a security issue

---

### 4. File Format Support Mismatch (HEIC) 📁

**The Problem:**
- Frontend allows HEIC uploads: `validTypes = ['..., 'image/heic']`
- Backend rejects HEIC: `ALLOWED_CONTENT_TYPES = {'pdf', 'png', 'jpg', 'jpeg'}`
- Result: User uploads HEIC, wastes bandwidth, gets confusing error

**Coordinated Fix:**

**Option 1: Backend adds HEIC support (Recommended)**
```python
# validators.py
ALLOWED_CONTENT_TYPES = {
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/heic',  # ⬅️ Add
}

# Also install pillow-heif for processing:
# pip install pillow-heif
from pillow_heif import register_heif_opener
register_heif_opener()
```

**Option 2: Frontend removes HEIC (Quick fix)**
```typescript
const validTypes = [
  'application/pdf',
  'image/png',
  'image/jpeg',
  'image/jpg',
  // Remove 'image/heic'
];
```

**Priority:** 🟠 **HIGH** - Bad UX, wastes upload bandwidth

---

### 5. Payment Flow Gap 💳

**The Problem:**
- Backend has `TODO: Create Stripe payment intent` in code
- Frontend has NO payment UI, NO Stripe integration
- Result: Users can't actually pay, business model broken

**Evidence:**
```python
# Backend: routers/quotes.py:46-50
# TODO: In production, create Stripe payment intent here
# payment_intent = await create_payment_intent(amount=1999, quote_id=quote_id)
```

```typescript
// Frontend: No payment components exist
// QuoteForm submission goes directly to /api/quotes
// No Stripe Elements, no payment confirmation
```

**Coordinated Fix:**

This is a **major feature gap**, not just a bug. Full implementation needed:

**Backend:**
```python
# 1. Create payment intent endpoint
@router.post("/quotes/{quote_id}/payment-intent")
async def create_payment_intent_endpoint(
    quote_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify quote ownership
    quote = await get_quote(quote_id, current_user, db)
    
    # Create Stripe payment intent
    intent = stripe.PaymentIntent.create(
        amount=1999,  # $19.99 in cents
        currency='usd',
        metadata={'quote_id': quote_id, 'user_id': current_user.id},
    )
    
    return {"client_secret": intent.client_secret}

# 2. Webhook to confirm payment
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    event = stripe.Webhook.construct_event(
        payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
    )
    
    if event.type == 'payment_intent.succeeded':
        quote_id = event.data.object.metadata['quote_id']
        # Generate report, save to DB, send email
        await generate_and_save_report(quote_id, db)
    
    return {"status": "success"}
```

**Frontend:**
```typescript
// 1. After quote analysis, redirect to payment
const { data: analysisResult } = await axios.post('/api/quotes', quoteData);
router.push(`/payment/${analysisResult.quote_id}`);

// 2. Create payment page: src/app/payment/[id]/page.tsx
'use client';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, PaymentElement } from '@stripe/react-stripe-js';

export default function PaymentPage({ params }: { params: { id: string } }) {
  const [clientSecret, setClientSecret] = useState('');
  
  useEffect(() => {
    // Fetch payment intent
    axios.post(`/api/quotes/${params.id}/payment-intent`)
      .then(res => setClientSecret(res.data.client_secret));
  }, [params.id]);
  
  return (
    <Elements stripe={stripePromise} options={{ clientSecret }}>
      <PaymentForm quoteId={params.id} />
    </Elements>
  );
}

// 3. On success, redirect to report
```

**Priority:** 🔴 **CRITICAL** - Business logic missing, revenue at risk

---

### 6. Token Lifecycle Incomplete 🔄

**The Problem:**
- Backend blacklists tokens on logout
- Frontend clears localStorage on logout
- But frontend doesn't handle 401 responses (expired/blacklisted tokens)
- Result: User with expired token sees broken UI, not redirected to login

**Coordinated Fix:**

**Frontend global axios interceptor:**
```typescript
// lib/api.ts
import axios from 'axios';
import { useRouter } from 'next/navigation';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,  // For cookie auth
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token expired or blacklisted - clear state and redirect
      localStorage.clear();  // Clear any cached data
      window.location.href = '/login?session_expired=true';
    }
    return Promise.reject(error);
  }
);

export default api;

// Use this instance everywhere instead of axios directly
```

**Priority:** 🟠 **HIGH** - Poor UX, confusing for users

---

## 📊 API Contract Audit

### Endpoints Missing Auth (Security Gap)

| Endpoint | Backend Auth | Frontend Sends Auth | Risk |
|----------|-------------|---------------------|------|
| `GET /api/quotes` | ❌ None | ❌ No | 🔴 Lists all users' quotes |
| `GET /api/quotes/{id}/report` | ❌ None | ❌ No | 🔴 Anyone can view reports |
| `GET /api/quotes/{id}` | ✅ Required | ❌ No | 🟠 IDOR if auth removed |
| `POST /api/quotes` | ✅ Required | ✅ Yes | ✅ Secure |
| `GET /api/dashboard` | ✅ Required | ✅ Yes | ✅ Secure |

**Action Items:**
1. Add auth requirement to `GET /api/quotes` (or remove endpoint)
2. Add auth to `GET /api/quotes/{id}/report`
3. Frontend: Switch to credential-based requests (cookie auth)

---

### Endpoints with Format Mismatch

| Endpoint | Backend Returns | Frontend Expects | Issue |
|----------|----------------|------------------|-------|
| `POST /api/auth/login` | `{token, user}` | ✅ Matches | None (but should return cookie) |
| `POST /api/quotes` | `{error, suggestion}` | `{detail}` | 🟡 Error not displayed properly |
| `POST /api/quotes/parse-upload` | `{error, suggestion}` | `{detail}` | 🟡 Error not displayed |

---

## 🎯 Unified Fix Priority

### Phase 1: Auth Architecture (Week 1) 🔴🔴🔴

**Why first:** Affects every authenticated endpoint, highest security impact

**Tasks:**
1. Backend: Implement httpOnly cookie auth response
2. Backend: Enable CSRF validation on protected routes
3. Frontend: Remove localStorage token storage
4. Frontend: Add `credentials: 'include'` to all API calls
5. Frontend: Implement CSRF token reading from cookie
6. Frontend: Add 401 interceptor for auto-redirect
7. Test: Full auth flow (login → dashboard → logout → expired token)

**Estimated effort:** 8-12 hours  
**Files affected:** 15+ (backend routers, frontend auth pages, all API calls)

---

### Phase 2: Payment Flow (Week 2-3) 🔴

**Why second:** Business logic gap, no revenue without this

**Tasks:**
1. Backend: Complete Stripe payment intent creation
2. Backend: Implement webhook handler
3. Frontend: Install @stripe/stripe-js
4. Frontend: Create payment page with Stripe Elements
5. Frontend: Update quote submission flow to redirect to payment
6. Frontend: Create payment success/failure pages
7. Backend: Generate report only after payment confirmation
8. Test: End-to-end payment flow with Stripe test mode

**Estimated effort:** 16-24 hours  
**Files affected:** 10+ (new payment routes, frontend pages, email templates)

---

### Phase 3: Auth Endpoints (Week 3) 🟠

**Tasks:**
1. Backend: Add auth to `GET /api/quotes` or remove endpoint
2. Backend: Fix `GET /api/quotes/{id}/report` to require auth
3. Frontend: Update all quote list/detail calls to send credentials
4. Test: Verify unauthorized access blocked

**Estimated effort:** 2-4 hours  
**Files affected:** 4 (quotes router, report page)

---

### Phase 4: Error Handling (Week 4) 🟡

**Tasks:**
1. Frontend: Create `parseApiError` utility
2. Frontend: Replace all `err.response?.data?.detail` with utility
3. Frontend: Add user-friendly error messages for common codes
4. Test: Verify all error scenarios show proper messages

**Estimated effort:** 3-5 hours  
**Files affected:** 8+ (all components with API calls)

---

### Phase 5: File Upload (Week 4) 🟠

**Tasks:**
1. Backend: Add HEIC to allowed types
2. Backend: Install pillow-heif
3. Backend: Test HEIC file parsing
4. OR Frontend: Remove HEIC from allowed types

**Estimated effort:** 1-2 hours  
**Files affected:** 2 (validators.py, FileUpload.tsx)

---

## 🔧 Development Workflow Improvements

### 1. API Contract Testing
**Recommendation:** Add contract tests to catch frontend/backend mismatches early

```typescript
// __tests__/api-contract.test.ts
describe('API Contract: Auth', () => {
  test('Login returns expected format', async () => {
    const response = await login('test@example.com', 'password');
    expect(response).toHaveProperty('user');
    expect(response).toHaveProperty('token'); // Will fail after cookie migration
  });
});
```

### 2. Shared TypeScript Types
**Recommendation:** Generate frontend types from backend Pydantic models

```bash
# Install datamodel-code-generator
pip install datamodel-code-generator

# Generate TypeScript types from Pydantic models
datamodel-codegen \
  --input backend/schemas/ \
  --output frontend/src/types/api.ts \
  --output-model-type=typescript
```

### 3. Integration Test Suite
**Recommendation:** E2E tests covering critical flows

```typescript
// e2e/quote-submission.spec.ts
test('User can submit quote and view report', async ({ page }) => {
  await page.goto('/login');
  await login(page);
  await submitQuote(page, quoteData);
  await expect(page).toHaveURL(/\/payment\/.+/);  // Redirects to payment
  await completePayment(page);
  await expect(page).toHaveURL(/\/report\/.+/);   // Redirects to report
  await expect(page.locator('.report-summary')).toBeVisible();
});
```

---

## 📈 Overall Integration Score After Fixes

| Category | Current | After Phase 1-2 | After Phase 3-5 |
|----------|---------|-----------------|-----------------|
| Auth Architecture | 2/10 | 9/10 | 9/10 |
| API Security | 3/10 | 7/10 | 9/10 |
| Error Handling | 5/10 | 5/10 | 8/10 |
| Payment Flow | 0/10 | 8/10 | 9/10 |
| File Upload | 6/10 | 6/10 | 9/10 |
| **OVERALL** | **4/10** | **7.5/10** | **9/10** |

---

## 🎬 Next Steps

1. **Review this report with team** - Discuss auth architecture approach
2. **Decide: httpOnly cookies or keep localStorage?** - I strongly recommend cookies
3. **Create GitHub issues** for each phase
4. **Start Phase 1** - Auth architecture fixes (highest impact)
5. **Set milestone dates** for each phase
6. **Schedule follow-up review** after Phase 1-2 complete

---

## 💡 Key Takeaways

### What's Working Well ✅
- Individual components (backend validators, frontend UI) are solid
- Security awareness is high (rate limiting, CORS, input validation)
- Code structure is clean and maintainable

### What Needs Immediate Attention 🚨
1. **Auth architecture is split-brain** - backend configured for cookies, frontend using localStorage
2. **Payment flow is incomplete** - no way for users to actually pay
3. **Authorization gaps** - some endpoints missing auth checks

### Long-term Architecture Recommendations 🏗️
1. **Use httpOnly cookies** for session management (not localStorage)
2. **Enforce CSRF protection** on all state-changing endpoints
3. **Generate TypeScript types** from Pydantic models for type safety
4. **Add E2E tests** for critical user flows
5. **Implement error boundary** and global error handling

---

*End of Integration Analysis Report*

**Questions?** Reference this document alongside the three individual audit reports for complete context.
