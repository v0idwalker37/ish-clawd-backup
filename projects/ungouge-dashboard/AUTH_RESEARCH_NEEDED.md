# OAuth Authentication - Research Needed

**Status:** Taking a break to research proper implementation pattern
**Date:** 2026-02-04
**Goal:** Most secure solution that actually works

## What We've Learned

### The Problem
Google OAuth popup/iframe + HTTP-only cookies = **Cross-origin security blocks cookie**

**Symptoms:**
- ✅ Google Sign-In succeeds
- ✅ Backend verification succeeds (`/auth/verify` returns 200)
- ✅ Session created in database
- ✅ Set-Cookie header sent
- ❌ **Cookie never reaches browser** (blocked by cross-origin policy)
- ❌ Subsequent requests to `/` have no session cookie
- ❌ User stuck on login page

### What We Tried (All Failed)
1. ✅ Fixed JavaScript syntax error (missing `}`)
2. ✅ Fixed missing Python dependency (`requests`)
3. ✅ Fixed database path mismatch (`DB_PATH` vs `DATABASE_PATH`)
4. ❌ Changed `SameSite=lax` → didn't work
5. ❌ Changed `SameSite=none` + explicit domain → didn't work
6. ❌ Removed explicit domain → didn't work
7. ❌ Removed `httpOnly=True` → **still didn't work**
8. ❌ Added 500ms delay before redirect → didn't work
9. ✅ Moved sessions from memory to database (good fix, but didn't solve cookie issue)

### Root Cause
**Browser security:** Cookies set in OAuth popup/iframe context cannot be accessed by parent window, even with:
- `SameSite=none`
- `Secure=true`
- `httpOnly=false`

This is a fundamental browser cross-origin security policy.

## Research Topics for Tomorrow

### 1. **Google OAuth Best Practices for Cloud Run**
- How do production apps handle Google OAuth with cookies?
- Server-side redirect flow vs popup flow
- Token exchange patterns

### 2. **Cookie-less Auth Patterns**
- Session token in `localStorage` instead of cookies
- JWT tokens returned to frontend
- Session ID in response body, stored client-side

### 3. **Alternative Approaches**
- Use server-side redirect OAuth flow (no popup)
- Store session token in URL parameter → set cookie on redirect
- Use Firebase Auth or similar managed auth service

### 4. **Security vs Practicality**
- httpOnly cookies = most secure (XSS protection)
- localStorage = less secure but works with OAuth popups
- What do real production apps do?

## Current State

### What's Working
- ✅ Backend API (FastAPI)
- ✅ Database (SQLite with sessions table)
- ✅ Google OAuth verification
- ✅ Session creation and management
- ✅ Frontend login page
- ✅ Dashboard HTML (syntax fixed)

### What's Broken
- ❌ Cookie delivery to browser after OAuth
- ❌ Session persistence across page loads
- ❌ Login → Dashboard flow

### Current Files
- `backend/main.py` - FastAPI app with auth endpoints
- `backend/auth.py` - Google OAuth verification + session management (uses DATABASE_PATH, stores in SQLite)
- `backend/static/login.html` - Login page with Google Sign-In button
- `backend/static/dashboard.html` - Dashboard (844 lines, braces balanced)

## Recommended Solution (To Research)

**Option 1: Server-side redirect flow** (Most secure)
- Remove Google Sign-In popup button
- Redirect user to Google OAuth consent page
- Google redirects back to `/auth/callback`
- Backend sets cookie on the callback response
- Cookie works because it's same-origin (no popup)

**Option 2: Token in response body** (Practical)
- OAuth popup sends token to frontend
- Frontend stores token in localStorage
- Frontend includes token in Authorization header for all requests
- Backend validates token instead of cookie

**Option 3: Hybrid approach**
- Use popup for UX
- Backend returns session token in JSON response
- Frontend manually creates cookie via `document.cookie`
- Less secure than httpOnly but works with popups

## Next Steps (Tomorrow)
1. Research production OAuth patterns for Cloud Run
2. Find reference implementations that work
3. Choose most secure pattern that actually works
4. Implement clean solution from scratch if needed
5. Test thoroughly before showing Jason

## Deployment Info
- Service: `ungouge-dashboard`
- Region: `us-central1`
- Latest revision: `ungouge-dashboard-00009-f59`
- Current config: `SameSite=none, httpOnly=False, Secure=true`

---

**Bottom line:** Cookie-based auth with OAuth popups has fundamental browser security limitations. Need to research proper patterns used by production apps.
