# OAuth CSRF Protection - State Parameter Implementation

**Issue:** Dashboard OAuth 2.0 flow missing state parameter (CSRF vulnerability)  
**Severity:** HIGH  
**Discovered:** 2026-02-10 security audit  
**Estimated fix time:** 30 minutes

---

## Vulnerability

**Current flow:**
1. User clicks "Sign in with Google"
2. Redirect to Google OAuth with client_id + redirect_uri
3. Google redirects back with auth code
4. Backend exchanges code for ID token
5. Backend verifies email whitelist
6. Session created

**Problem:** No state parameter validation  
**Attack:** OAuth CSRF - attacker can trick user into authenticating attacker's account

**Example attack:**
1. Attacker initiates Google OAuth, captures callback URL: `?code=ABC123`
2. Attacker sends victim: `https://dashboard.ungouge.ai/auth/callback?code=ABC123`
3. Victim clicks link (while logged into Google)
4. Victim's session is now linked to attacker's Google account
5. Attacker can view victim's dashboard activity

---

## Fix: Add State Parameter

### Step 1: Generate and Store State (Backend)

**File:** `backend/main.py`

**Add before OAuth redirect:**
```python
import secrets

# OAuth login endpoint
@app.get("/auth/login")
def oauth_login(response: Response):
    """Initiate Google OAuth flow with CSRF protection"""
    # Generate random state token
    state = secrets.token_urlsafe(32)
    
    # Store state in secure httpOnly cookie (expires in 10 minutes)
    response.set_cookie(
        key="oauth_state",
        value=state,
        max_age=600,  # 10 minutes
        httponly=True,
        secure=True,  # HTTPS only
        samesite="lax"
    )
    
    # Build Google OAuth URL with state
    google_oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"state={state}"  # <-- Add state parameter
    )
    
    return RedirectResponse(google_oauth_url)
```

### Step 2: Validate State (Callback)

**File:** `backend/main.py`

**Modify callback endpoint:**
```python
@app.get("/auth/callback")
def oauth_callback(
    code: str, 
    state: str,  # <-- Google returns this
    request: Request,
    response: Response
):
    """Handle OAuth callback with state validation"""
    
    # CRITICAL: Validate state parameter (CSRF protection)
    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        # State mismatch = potential CSRF attack
        print(f"❌ OAuth state mismatch! Stored: {stored_state}, Received: {state}")
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Clear state cookie (one-time use)
    response.delete_cookie("oauth_state")
    
    # ... rest of existing code (exchange code for token, verify email, create session)
```

### Step 3: Update Frontend (Optional - if using JS OAuth button)

**File:** `frontend/login.html` (if exists)

**No changes needed** - state is handled server-side in redirect flow.

---

## Testing

### Positive Test (Valid Flow)
1. Navigate to `/auth/login`
2. Verify `oauth_state` cookie is set
3. Complete Google sign-in
4. Verify callback succeeds with matching state
5. Verify `oauth_state` cookie is deleted

### Negative Test (CSRF Attack Simulation)
1. User A initiates OAuth, captures callback URL with `code=X&state=Y`
2. User B clicks callback URL with User A's code
3. **Expected:** 400 error "Invalid state parameter" (state cookie won't match)
4. **Current behavior (without fix):** User B's session linked to User A's Google account

### Edge Cases
- State cookie expired (>10 min between login click and callback)
  - **Expected:** 400 error (no stored state)
- State parameter missing from callback
  - **Expected:** 400 error
- Multiple login attempts (parallel OAuth flows)
  - **Expected:** Only latest state is valid (cookie overwrites previous)

---

## Deployment

### 1. Update Code
- Modify `backend/main.py` per above
- Add `import secrets` if not already present

### 2. Test Locally
```bash
cd backend
uvicorn main:app --reload
# Test OAuth flow in browser
```

### 3. Deploy to Cloud Run
```bash
gcloud run deploy dashboard --region=us-central1 \
  --source=. \
  --set-env-vars $(cat .env.cloudrun | tr '\n' ',' | sed 's/,$//')
```

### 4. Verify
- Test login flow on https://dashboard.ungouge.ai
- Check browser dev tools for `oauth_state` cookie
- Confirm state parameter in Google OAuth redirect URL

---

## Security Improvements Checklist

- [x] State parameter generation (random, secure)
- [x] State stored server-side (httpOnly cookie)
- [x] State validated on callback
- [x] State cookie expires (10 min timeout)
- [x] State cookie deleted after use (one-time)
- [ ] Optional: Store state in database instead of cookie (more secure for high-value apps)

---

## Alternative: Database-Based State Storage

For **maximum security** (enterprise apps):

**backend/auth.py:**
```python
def create_oauth_state(email_hint: str = None) -> str:
    """Generate and store OAuth state in database"""
    state = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(minutes=10)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO oauth_states (state, email_hint, expires_at)
        VALUES (?, ?, ?)
    """, (state, email_hint, expires_at.isoformat()))
    conn.commit()
    conn.close()
    
    return state

def verify_oauth_state(state: str) -> bool:
    """Verify and consume OAuth state"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT expires_at FROM oauth_states
        WHERE state = ?
    """, (state,))
    
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False
    
    # Check expiration
    expires_at = datetime.fromisoformat(row[0])
    if datetime.now() > expires_at:
        cursor.execute("DELETE FROM oauth_states WHERE state = ?", (state,))
        conn.commit()
        conn.close()
        return False
    
    # State valid - delete it (one-time use)
    cursor.execute("DELETE FROM oauth_states WHERE state = ?", (state,))
    conn.commit()
    conn.close()
    
    return True
```

**Pros:** More secure (can't be stolen via XSS), works across multiple backends  
**Cons:** Adds database dependency, more complex

**Recommendation:** Cookie-based is sufficient for single-admin dashboard. Use database-based if adding multi-user support.

---

## Impact

**Before fix:** Dashboard vulnerable to OAuth CSRF attack  
**After fix:** Industry-standard CSRF protection, passes OAuth security audit  
**Audit score:** +2-3 points (59/100 → 61-62/100)

---

**Next steps:**
1. Jason approval for fix
2. Implement + test locally
3. Deploy to production
4. Add to security documentation

*Authored by Ish during 2026-02-10 autonomous security research session*
