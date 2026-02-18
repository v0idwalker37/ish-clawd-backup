# Frontend Code Audit Report
## Ungouge.ai - Next.js Application

**Audit Date:** February 6, 2026  
**Auditor:** Clawd (Opus 4.6)  
**Scope:** `/Users/moltbot/clawd/projects/ungouge-app/frontend/`  
**Framework:** Next.js 14.2.3 with TypeScript

---

## Executive Summary

The Ungouge.ai frontend is a well-structured Next.js application with good UX patterns and reasonable TypeScript usage. However, **several security vulnerabilities require immediate attention**, particularly around authentication token handling and API request authorization. The codebase shows consistent patterns but lacks some production-ready hardening.

### Risk Summary
| Severity | Count |
|----------|-------|
| 🔴 Critical | 2 |
| 🟠 High | 3 |
| 🟡 Medium | 8 |
| 🔵 Low | 10 |

### Top Priorities
1. **Replace localStorage token storage with httpOnly cookies**
2. **Add authorization headers to authenticated API requests**
3. **Implement CSRF protection**

---

## Critical Issues 🔴

### C1: Auth Token Stored in localStorage (XSS Vulnerability)
**Files:** `src/app/login/page.tsx:38`, `src/app/register/page.tsx:51`

```typescript
// VULNERABLE: localStorage is accessible to any JS, including XSS payloads
localStorage.setItem('token', data.token);
```

**Risk:** If an attacker injects malicious JavaScript (via XSS), they can steal the auth token and hijack user sessions. localStorage has no same-origin isolation from scripts.

**Fix:** Use httpOnly cookies set by the backend. The frontend should not handle raw tokens.

```typescript
// Backend should set: Set-Cookie: token=xxx; HttpOnly; Secure; SameSite=Strict
// Frontend just makes credentialed requests:
const response = await fetch('/api/auth/login', {
  method: 'POST',
  credentials: 'include', // Send cookies automatically
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
});
```

---

### C2: Report API Fetched Without Authorization
**File:** `src/app/report/[id]/page.tsx:31-34`

```typescript
const response = await axios.get(`${apiUrl}/api/quotes/${reportId}`);
// No Authorization header - report accessible to anyone with ID
```

**Risk:** Paid reports may be accessible to anyone who guesses or brute-forces the report ID. This is an **IDOR vulnerability** (Insecure Direct Object Reference).

**Fix:** Include auth token in request headers (after migrating to httpOnly cookies, use credentialed requests):

```typescript
const response = await axios.get(`${apiUrl}/api/quotes/${reportId}`, {
  withCredentials: true, // For cookie-based auth
  // OR with current localStorage approach (temporary):
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});
```

---

## High Issues 🟠

### H1: No CSRF Protection on Forms
**Files:** `src/app/login/page.tsx`, `src/app/register/page.tsx`, `src/components/QuoteForm.tsx`

All POST requests lack CSRF tokens. While using `SameSite=Strict` cookies helps, explicit CSRF tokens provide defense-in-depth.

**Fix:** Implement CSRF token flow:
1. Backend generates token on session start
2. Token included in form as hidden field or header
3. Backend validates token on POST requests

---

### H2: Error Messages May Leak Internal Details
**Files:** Multiple

```typescript
// login/page.tsx:30
throw new Error(data.error || 'Login failed');

// QuoteForm.tsx:98
setError(err.response?.data?.detail || 'Failed to analyze quote...');
```

**Risk:** Backend error messages may contain stack traces, SQL errors, or internal paths that help attackers.

**Fix:** Sanitize error messages:
```typescript
// Map specific backend errors to user-friendly messages
const errorMessages: Record<string, string> = {
  'INVALID_CREDENTIALS': 'Invalid email or password',
  'RATE_LIMITED': 'Too many attempts. Please wait.',
  // ...
};
const userMessage = errorMessages[data.code] || 'An error occurred. Please try again.';
```

---

### H3: Missing Token Validation
**File:** `src/app/dashboard/layout.tsx:17-20`

```typescript
const token = localStorage.getItem('token');
if (!token) {
  router.push('/login');
  return;
}
// Token exists but not validated - could be expired or malformed
```

**Risk:** Users with expired or invalid tokens see loading state indefinitely or get unexpected errors.

**Fix:** Validate token on mount:
```typescript
useEffect(() => {
  const validateSession = async () => {
    try {
      const response = await fetch('/api/auth/validate', { credentials: 'include' });
      if (!response.ok) {
        router.push('/login');
        return;
      }
      setUser(await response.json());
    } catch {
      router.push('/login');
    }
  };
  validateSession();
}, [router]);
```

---

## Medium Issues 🟡

### M1: useEffect Dependency Warning in ChatWidget
**File:** `src/components/ChatWidget.tsx:40-51`

```typescript
useEffect(() => {
  if (isOpen && messages.length === 0) {
    setTimeout(() => {
      addBotMessage("👋 Hi!...");
    }, 300);
  }
}, [isOpen]); // Missing: messages.length, addBotMessage
```

**Risk:** ESLint warning, potential stale closure issues. Welcome message might fire unexpectedly.

**Fix:**
```typescript
const [hasShownWelcome, setHasShownWelcome] = useState(false);

useEffect(() => {
  if (isOpen && !hasShownWelcome) {
    const timer = setTimeout(() => {
      addBotMessage("👋 Hi!...");
      setHasShownWelcome(true);
    }, 300);
    return () => clearTimeout(timer);
  }
}, [isOpen, hasShownWelcome]);
```

---

### M2: Console.error in Production
**Files:** `src/app/report/[id]/page.tsx:38`, `src/components/QuoteForm.tsx:94`, `src/components/FileUpload.tsx:77`

```typescript
console.error('Upload error:', error);
```

**Risk:** Logs may leak to users, debug info in production, browser console clutter.

**Fix:** Use proper error logging service:
```typescript
// lib/logger.ts
export const logError = (context: string, error: unknown) => {
  if (process.env.NODE_ENV === 'development') {
    console.error(context, error);
  }
  // In production: send to Sentry, LogRocket, etc.
};
```

---

### M3: Unguarded Navigation Calls
**Files:** `src/app/login/page.tsx:35`, `src/app/register/page.tsx:48`

```typescript
localStorage.setItem('token', data.token);
router.push('/dashboard');
// No await - navigation happens after synchronous code
```

**Risk:** Race conditions, potential issues with Next.js navigation state.

**Fix:**
```typescript
localStorage.setItem('token', data.token);
await router.push('/dashboard');
// Or handle navigation completion
```

---

### M4: Header Auth State Flickers
**File:** `src/components/Header.tsx:16-26`

```typescript
useEffect(() => {
  const token = localStorage.getItem('token');
  if (token) {
    setUser({ name: 'John Doe', email: 'john@example.com' });
  }
}, []);
```

**Risk:** Header renders with logged-out state, then flickers to logged-in. Poor UX.

**Fix:** Initialize with `null` explicitly and show loading or use SSR-compatible auth:
```typescript
const [user, setUser] = useState<User | null | 'loading'>('loading');
// Render null or skeleton while loading
```

---

### M5: File Upload Missing Size/Type Validation Error UX
**File:** `src/components/FileUpload.tsx:45-51`

```typescript
if (!validTypes.includes(file.type)) {
  onError('Please upload a PDF or image file...');
  return;
}
// File variable still set, causing inconsistent state
```

**Fix:** Ensure file state is cleared on error:
```typescript
if (!validTypes.includes(file.type)) {
  setFile(null);
  onError('Please upload a PDF or image file...');
  return;
}
```

---

### M6: QuoteForm Allows Bypassing Steps
**File:** `src/components/QuoteForm.tsx`

Users can theoretically bypass step validation via devtools manipulation. Form data isn't validated until final submission.

**Fix:** Add server-side validation (already implied by zod schema, but ensure backend enforces).

---

### M7: Missing Input Sanitization Display
**Files:** Dashboard, Report pages

User-provided strings (contractor names, project types) are rendered directly:
```typescript
<p className="font-semibold text-gray-900 truncate">{user.name}</p>
```

**Risk:** While React escapes by default, ensure no `dangerouslySetInnerHTML` is used with user content.

**Status:** Currently safe - React's JSX escaping handles this. But add Content-Security-Policy headers for defense-in-depth.

---

### M8: Price Gauge Division Edge Case
**File:** `src/components/PriceGauge.tsx:10`

```typescript
const maxPrice = Math.max(quotedPrice, fairHigh * 1.5);
const quotedPercent = (quotedPrice / maxPrice) * 100;
```

**Risk:** If `maxPrice` is 0 (edge case with bad data), division by zero creates NaN.

**Fix:**
```typescript
const maxPrice = Math.max(quotedPrice, fairHigh * 1.5, 1); // Ensure non-zero
```

---

## Low Issues 🔵

### L1: Missing Error Boundaries
No React Error Boundaries found. Uncaught errors crash the entire app.

**Fix:** Add error boundary wrapper:
```typescript
// components/ErrorBoundary.tsx
'use client';
import { Component, ReactNode } from 'react';

class ErrorBoundary extends Component<{children: ReactNode}, {hasError: boolean}> {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError) return <div>Something went wrong.</div>;
    return this.props.children;
  }
}
```

---

### L2: Missing `rel="noopener noreferrer"` on External Links
**File:** `src/components/Footer.tsx:46`

```typescript
<a href="mailto:support@ungouge.ai">support@ungouge.ai</a>
```

**Note:** `mailto:` links don't need `noopener`, but ensure any `target="_blank"` links include it. Currently not an issue.

---

### L3: Hardcoded Mock Data in Dashboard
**File:** `src/app/dashboard/page.tsx:10-17`

```typescript
const stats = {
  totalReports: 12,
  totalSavings: 8450,
  // ...
};
```

**Risk:** Confusing for development, could ship to production accidentally.

**Fix:** Clearly mark or fetch from API:
```typescript
// TODO: Replace with API call - this is mock data
const stats = process.env.NODE_ENV === 'development' ? mockStats : await fetchStats();
```

---

### L4: Missing Loading State for Dashboard Stats
**File:** `src/app/dashboard/page.tsx`

Stats are hardcoded. When real API is connected, add loading skeletons.

---

### L5: Accessibility - Missing Focus Indicators on Some Elements
**File:** `src/app/globals.css`

`.focus-visible-ring` utility exists but isn't applied everywhere.

**Fix:** Ensure all interactive elements have visible focus states for keyboard navigation.

---

### L6: Accessibility - FAQ Buttons Missing aria-expanded
**File:** `src/app/page.tsx:221-224`

```typescript
<button onClick={() => setOpenFaqIndex(...)}>
  // Missing aria-expanded attribute
```

**Fix:**
```typescript
<button
  onClick={() => setOpenFaqIndex(...)}
  aria-expanded={openFaqIndex === index}
  aria-controls={`faq-answer-${index}`}
>
```

---

### L7: Type Assertion Could Be Stricter
**File:** `src/app/report/[id]/page.tsx:29`

```typescript
const reportId = params.id as string;
```

**Fix:** Handle potential undefined:
```typescript
const reportId = params.id;
if (typeof reportId !== 'string') {
  return <NotFoundPage />;
}
```

---

### L8: ChatWidget Quick Questions Missing Keys
**File:** `src/components/ChatWidget.tsx:175-183`

```typescript
{faqs.slice(0, 3).map((faq, idx) => (
  <button key={idx}>...
```

**Risk:** Using index as key is acceptable here since list is static, but consider using faq.question for stability.

---

### L9: Missing Meta Tags for Dynamic Report Pages
**File:** `src/app/report/[id]/page.tsx`

No `generateMetadata` function for dynamic SEO.

**Fix:**
```typescript
export async function generateMetadata({ params }: { params: { id: string } }) {
  return {
    title: `Report ${params.id} | Ungouge.ai`,
    robots: { index: false } // Reports should be private
  };
}
```

---

### L10: Bundle Size - lucide-react Imports
**Files:** Multiple components

```typescript
import { Shield, Lock, Eye, Database, UserX, FileText } from 'lucide-react';
```

**Note:** Tree-shaking should handle this, but verify bundle analyzer shows minimal icon code.

---

## Quick Wins 🚀

These can be implemented quickly with high impact:

1. **Add Content-Security-Policy header** in `next.config.js`:
   ```javascript
   headers: async () => [
     {
       source: '/:path*',
       headers: [
         { key: 'Content-Security-Policy', value: "default-src 'self'; script-src 'self' 'unsafe-inline'" },
         { key: 'X-Frame-Options', value: 'DENY' },
         { key: 'X-Content-Type-Options', value: 'nosniff' },
       ],
     },
   ],
   ```

2. **Add React Error Boundary** at layout level (~15 mins)

3. **Fix FAQ aria-expanded** (~5 mins)

4. **Add loading skeleton to Header auth state** (~20 mins)

5. **Create centralized error handler** for API calls (~30 mins)

---

## Recommended Architecture Improvements

### Auth Flow Refactor
Current: localStorage tokens → Vulnerable to XSS  
Recommended: httpOnly cookies with CSRF tokens

```
┌─────────┐         ┌─────────┐         ┌─────────┐
│ Browser │ ──1──▶  │ Next.js │ ──2──▶  │ Backend │
│         │ ◀──4──  │  API    │ ◀──3──  │         │
└─────────┘         └─────────┘         └─────────┘
1. Login request with credentials
2. Forward to backend
3. Backend returns Set-Cookie: token=xxx; HttpOnly; Secure
4. Cookie automatically stored (not accessible to JS)
```

### API Request Wrapper
```typescript
// lib/api.ts
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(sanitizeError(error));
  }
);

export default api;
```

---

## Summary

The Ungouge.ai frontend is well-structured with good UX patterns. The main concerns are:

1. **Security:** Auth token handling needs immediate attention
2. **Error Handling:** Needs centralized, user-friendly error management  
3. **Accessibility:** Minor improvements needed for ARIA attributes
4. **Performance:** Current state is acceptable; monitor bundle size as app grows

**Priority Order:**
1. Fix C1 & C2 (Critical auth issues) - Coordinate with backend
2. Address H1-H3 (CSRF, error sanitization, token validation)
3. Implement Quick Wins
4. Plan Medium issues for next sprint

---

*Report generated by Clawd | Opus 4.6*
