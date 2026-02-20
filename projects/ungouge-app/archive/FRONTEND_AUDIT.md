# UnGouge.ai Frontend Audit Report

**Date:** 2026-02-13  
**Auditor:** Next.js Expert (Claude Opus 4.6)  
**Framework:** Next.js 14.2.35 (App Router), React 18.3, TypeScript 5.4  
**Scope:** Full pre-launch audit — architecture, performance, SEO, security, accessibility, TypeScript, data fetching, code quality

---

## Summary

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | 5 |
| 🟠 HIGH | 12 |
| 🟡 MEDIUM | 16 |
| 🟢 LOW | 10 |
| **Total** | **43** |

---

## 🔴 CRITICAL

### C1. CSP allows `unsafe-eval` and `unsafe-inline` — defeats XSS protection

**File:** `next.config.js` (line 9)  
**Issue:** The Content-Security-Policy header includes `'unsafe-eval' 'unsafe-inline'` for `script-src`. This effectively disables CSP's XSS protection — any injected script will execute. This is a pre-launch blocker for a payment-processing site.

**Current:**
```js
value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; ..."
```

**Fix:** Use nonces with Next.js. In `next.config.js`:
```js
// next.config.js
const nextConfig = {
  reactStrictMode: true,
  // ... existing config ...
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            // Remove unsafe-eval entirely. Keep unsafe-inline for style-src only (Tailwind needs it).
            // For production, use nonce-based approach or hashes.
            value: "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.ungouge.ai https://gemini.googleapis.com;",
          },
          // ... rest of headers
        ],
      },
    ];
  },
};
```

For the nonce-based approach (best practice), see the [Next.js CSP documentation](https://nextjs.org/docs/app/building-your-application/configuring/content-security-policy) using middleware to inject nonces.

---

### C2. Landing page is entirely client-rendered — kills SEO and Core Web Vitals

**File:** `src/app/page.tsx` (line 1)  
**Issue:** The landing page has `'use client'` at the top, making the **entire page** a Client Component. This means:
- Zero server-side HTML for search engines to index
- Large JavaScript bundle shipped to client (Lucide icons, React state management)
- Worse LCP/FCP — content only appears after JS hydration
- The only interactive element is a simple FAQ accordion

The homepage is the most important page for SEO and first impressions.

**Fix:** Extract the tiny interactive part (FAQ) into its own Client Component and make the page a Server Component:

```tsx
// src/app/page.tsx — Server Component (remove 'use client')
import Link from 'next/link';
import { CheckCircle, Shield, DollarSign, FileText, Upload, Search, Award, Lock, TrendingDown, Star } from 'lucide-react';
import FaqAccordion from '@/components/FaqAccordion';

const faqs = [
  // ... move FAQ data here ...
];

export default function HomePage() {
  return (
    <div>
      {/* All existing sections remain unchanged */}
      {/* ... Hero, How It Works, Trust Badges, Testimonials, Features ... */}

      {/* FAQ Section — only this needs interactivity */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">Frequently Asked Questions</h2>
            <p className="text-xl text-gray-600">Everything you need to know</p>
          </div>
          <FaqAccordion faqs={faqs} />
        </div>
      </section>

      {/* CTA Section unchanged */}
    </div>
  );
}
```

```tsx
// src/components/FaqAccordion.tsx
'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

interface FAQ {
  question: string;
  answer: string;
}

export default function FaqAccordion({ faqs }: { faqs: FAQ[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div className="space-y-4">
      {faqs.map((faq, index) => (
        <div key={index} className="card border-2 border-gray-200 hover:border-primary-300 transition-colors">
          <button
            onClick={() => setOpenIndex(openIndex === index ? null : index)}
            className="w-full flex items-center justify-between text-left"
            aria-expanded={openIndex === index}
          >
            <h3 className="font-semibold text-lg text-gray-900 pr-4">{faq.question}</h3>
            <ChevronDown
              className={`w-5 h-5 text-primary-600 flex-shrink-0 transition-transform ${
                openIndex === index ? 'rotate-180' : ''
              }`}
            />
          </button>
          {openIndex === index && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
```

---

### C3. Report page fetches data client-side — loses SSR, SEO, and is slower

**File:** `src/app/report/[id]/page.tsx` (lines 1, 29-55)  
**Issue:** The report page uses `'use client'` + `useEffect` + `axios.get()` to fetch report data. This is an **anti-pattern** in App Router. Problems:
- No SSR — search engines see a loading spinner
- Extra round-trip (HTML → JS → hydrate → fetch → render)
- No caching/revalidation — every visit re-fetches
- Error handling doesn't use `notFound()` from Next.js

**Fix:** Convert to Server Component with async data fetching:
```tsx
// src/app/report/[id]/page.tsx
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import ReportView from '@/components/ReportView'; // Extract client interactivity here
import { api } from '@/lib/api-server'; // Server-side API client (see note)

interface PageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  // Optionally fetch report title for dynamic metadata
  return {
    title: `Quote Analysis Report #${id}`,
    robots: { index: false }, // Reports are private
  };
}

export default async function ReportPage({ params }: PageProps) {
  const { id } = await params;

  let report;
  try {
    // Use server-side fetch with cookie forwarding
    const { cookies } = await import('next/headers');
    const cookieStore = await cookies();
    const res = await fetch(
      `${process.env.API_URL || 'http://localhost:8000'}/api/quotes/${id}`,
      {
        headers: { Cookie: cookieStore.toString() },
        cache: 'no-store', // Reports are user-specific
      }
    );
    if (res.status === 404) notFound();
    if (res.status === 401) {
      // Redirect handled by middleware ideally
      const { redirect } = await import('next/navigation');
      redirect('/login');
    }
    if (!res.ok) throw new Error('Failed to fetch report');
    report = await res.json();
  } catch (error) {
    notFound();
  }

  return <ReportView report={report} />;
}
```

> **Note:** This requires a server-side API utility that forwards cookies from the incoming request. The current `api.ts` uses `credentials: 'include'` which only works in browser context.

---

### C4. No middleware for auth protection — dashboard routes are unprotected

**File:** (missing) `middleware.ts`  
**Issue:** There is no Next.js middleware. The dashboard layout (`src/app/dashboard/layout.tsx`) does auth checking client-side via `useEffect`, which means:
- Unauthenticated users briefly see the loading state
- The protected page HTML/JS is still shipped to the browser
- No server-side redirect — SEO bots and scrapers see the page
- Race condition: the page can flash before redirect occurs

**Fix:** Create `src/middleware.ts`:
```tsx
// src/middleware.ts
import { NextRequest, NextResponse } from 'next/server';

const PROTECTED_PATHS = ['/dashboard', '/report'];
const AUTH_PATHS = ['/login', '/register'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasAuthCookie = request.cookies.has('access_token');

  // Protect dashboard/report routes
  const isProtected = PROTECTED_PATHS.some((path) => pathname.startsWith(path));
  if (isProtected && !hasAuthCookie) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('return', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect logged-in users away from auth pages
  const isAuthPage = AUTH_PATHS.some((path) => pathname.startsWith(path));
  if (isAuthPage && hasAuthCookie) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/report/:path*', '/login', '/register'],
};
```

---

### C5. `dangerouslySetInnerHTML` for JSON-LD without sanitization of dynamic data

**File:** `src/app/layout.tsx` (lines 73-80), `src/lib/seo.ts` (line 203)  
**Issue:** The `renderJsonLd()` function uses `JSON.stringify()` into `dangerouslySetInnerHTML`. While the current data is static, this pattern is dangerous if any user-controlled data ever enters the schema (e.g., dynamic page titles from a CMS, user names, etc.). A `</script>` in the data would break out of the JSON-LD block.

**Fix:** Use the Next.js built-in JSON-LD pattern (Next.js 14.1+):
```tsx
// In layout.tsx — replace the <script> tags in <head>
<body className={inter.variable}>
  <script
    type="application/ld+json"
    dangerouslySetInnerHTML={{
      __html: JSON.stringify(organizationSchema).replace(/</g, '\\u003c'),
    }}
  />
  <script
    type="application/ld+json"
    dangerouslySetInnerHTML={{
      __html: JSON.stringify(softwareSchema).replace(/</g, '\\u003c'),
    }}
  />
  {/* ... */}
</body>
```

Update `renderJsonLd`:
```tsx
// src/lib/seo.ts
export function renderJsonLd(schema: object) {
  return {
    __html: JSON.stringify(schema).replace(/</g, '\\u003c'),
  };
}
```

Also move the `<script>` tags out of `<head>` — they should be in `<body>` or use Next.js `<Script>` component. Placing them in `<head>` alongside the Next.js-managed head content can cause hydration issues.

---

## 🟠 HIGH

### H1. No `loading.tsx` or `error.tsx` files anywhere in the app

**File:** (missing) `src/app/loading.tsx`, `src/app/error.tsx`, `src/app/not-found.tsx`, `src/app/dashboard/loading.tsx`, etc.  
**Issue:** The entire app has zero `loading.tsx`, `error.tsx`, or `not-found.tsx` files. This means:
- No Suspense boundaries for route transitions
- Unhandled errors crash the entire page (only the manual `ErrorBoundary` component catches render errors)
- No custom 404 page — users see the default Next.js 404

**Fix:** Create these files:

```tsx
// src/app/loading.tsx
export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4" />
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
```

```tsx
// src/app/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="text-center max-w-md">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Something went wrong</h2>
        <p className="text-gray-600 mb-6">{error.message || 'An unexpected error occurred.'}</p>
        <button onClick={reset} className="btn-primary">
          Try Again
        </button>
      </div>
    </div>
  );
}
```

```tsx
// src/app/not-found.tsx
import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="text-center max-w-md">
        <h1 className="text-6xl font-bold text-primary-600 mb-4">404</h1>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Page Not Found</h2>
        <p className="text-gray-600 mb-6">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <Link href="/" className="btn-primary">
          Go Home
        </Link>
      </div>
    </div>
  );
}
```

Also create `src/app/dashboard/loading.tsx` and `src/app/dashboard/error.tsx`.

---

### H2. Analyze page is a Client Component for no reason

**File:** `src/app/analyze/page.tsx` (line 1)  
**Issue:** This page has `'use client'` but contains zero interactivity — it just renders a heading and the `QuoteForm` component. The `QuoteForm` is already a Client Component. The `'use client'` on the page is unnecessary and prevents server-side rendering of the static wrapper content.

**Fix:**
```tsx
// src/app/analyze/page.tsx — remove 'use client'
import type { Metadata } from 'next';
import QuoteForm from '@/components/QuoteForm';

export const metadata: Metadata = {
  title: 'Analyze Your Quote',
  description: 'Enter your contractor quote details to get instant, data-backed analysis using real BLS labor rates.',
};

export default function AnalyzePage() {
  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">Analyze Your Quote</h1>
          <p className="text-xl text-gray-600">
            Enter your contractor quote details to get instant analysis.
          </p>
        </div>
        <QuoteForm />
      </div>
    </div>
  );
}
```

**Bonus:** Now you can export static `metadata` — which is impossible from a Client Component.

---

### H3. Dashboard page is a Client Component with hardcoded mock data

**File:** `src/app/dashboard/page.tsx` (line 1)  
**Issue:** The entire dashboard page is `'use client'` with hardcoded mock data (`stats`, empty `recentQuotes`). In production this will show fake numbers to real users. Additionally, being a Client Component means:
- No per-page metadata (title shows generic "Dashboard")
- Data should come from the server, not be mocked client-side

**Fix:** Fetch real data server-side or via the dashboard layout, and pass it down. At minimum, add a clear TODO/warning:
```tsx
// If keeping client-side for now, at minimum remove mock stats or fetch them:
useEffect(() => {
  const fetchDashboardData = async () => {
    try {
      const data = await api.get('/api/dashboard/stats');
      setStats(data.stats);
      setRecentQuotes(data.recent_quotes);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };
  fetchDashboardData();
}, []);
```

---

### H4. Header makes an API call on every page render to check auth

**File:** `src/components/Header.tsx` (lines 20-38)  
**Issue:** The Header calls `fetch('/api/auth/me')` on every single mount (every page navigation). This creates:
- Unnecessary API load (N+1 for every page view)
- Visible delay before user avatar appears
- No caching — fetches even when the user hasn't changed

**Fix:** Move auth state to a React Context provider that fetches once and caches:
```tsx
// src/providers/AuthProvider.tsx
'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface User {
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/auth/me`, { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        setUser({ name: data.name, email: data.email });
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { checkAuth(); }, []);

  const logout = async () => {
    // ... logout logic
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, logout, refresh: checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
```

Wrap in `layout.tsx` and use `useAuth()` in Header and DashboardLayout.

---

### H5. Footer conditionally returns `null` after hooks — violates Rules of Hooks

**File:** `src/components/Footer.tsx` (lines 7-9)  
**Issue:** The Footer calls `usePathname()` (a hook) and then conditionally returns `null`. While this particular pattern is technically safe (the hook always runs), it's fragile — if someone adds a hook after the early return it will break. More importantly, this should be done at the layout level, not by having every component self-hide.

**Fix:** Use separate layouts via Route Groups:
```
app/
├── (marketing)/
│   ├── layout.tsx          # Has Header + Footer
│   ├── page.tsx
│   ├── about/page.tsx
│   ├── pricing/page.tsx
│   └── analyze/page.tsx
├── (dashboard)/
│   ├── layout.tsx          # Has sidebar, no Header/Footer
│   └── dashboard/
│       ├── page.tsx
│       └── settings/page.tsx
└── layout.tsx              # Root layout (html/body only)
```

This eliminates the conditional rendering pattern entirely and is the idiomatic App Router approach.

---

### H6. `process.env.NEXT_PUBLIC_API_URL` used with rewrite makes API URL leak to client

**File:** `next.config.js` (lines 3-5, 30-36)  
**Issue:** The `env` block re-exposes `NEXT_PUBLIC_API_URL`, and the rewrite proxies `/api/:path*` to the backend. However, multiple components directly reference `NEXT_PUBLIC_API_URL` in client-side `fetch` calls (Header line 23, LoginPage, RegisterPage, FileUpload, ReportPage), bypassing the proxy. This means:
- The internal API URL leaks to the client bundle
- CORS headers are needed on the backend
- The rewrite proxy is unused for most requests

**Fix:** Use the proxy consistently. All client-side API calls should go to `/api/...` (relative), which the rewrite will proxy:
```tsx
// Instead of:
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
await fetch(`${apiUrl}/api/auth/me`, { credentials: 'include' });

// Use:
await fetch('/api/auth/me', { credentials: 'include' });
```

Then remove the `env` block from `next.config.js` and the `NEXT_PUBLIC_API_URL` references from client code. Keep a non-public `API_URL` env var for server-side only calls.

---

### H7. `err: any` used everywhere for error handling — loses type safety

**Files:** Multiple  
- `src/app/report/[id]/page.tsx` line 41 (`catch (err: any)`)
- `src/components/QuoteForm.tsx` line 86 (`catch (err: any)`)
- `src/app/login/page.tsx` lines 36, 64 (`catch (err: any)`)
- `src/app/register/page.tsx` line 58 (`catch (err: any)`)
- `src/app/dashboard/settings/page.tsx` line 29 (`catch (err: any)`)

**Issue:** `any` type on caught errors bypasses TypeScript's safety. Accessing `err.response?.data?.detail` or `err.message` without type narrowing can crash.

**Fix:** Use `unknown` and narrow:
```tsx
} catch (err: unknown) {
  if (err instanceof Error) {
    setError(err.message);
  } else {
    setError('An unexpected error occurred');
  }
}

// For axios errors:
import { isAxiosError } from 'axios';

} catch (err: unknown) {
  if (isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    setError(typeof detail === 'string' ? detail : 'Request failed');
  } else if (err instanceof Error) {
    setError(err.message);
  } else {
    setError('An unexpected error occurred');
  }
}
```

---

### H8. Static sitemap.xml — won't include dynamic routes

**File:** `public/sitemap.xml`  
**Issue:** The sitemap is a static XML file in `/public`. It won't include any dynamically generated pages (e.g., blog posts, public reports if they ever exist). It also requires manual updates when new static pages are added.

**Fix:** Use Next.js dynamic sitemap generation:
```tsx
// src/app/sitemap.ts
import { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://ungouge.ai';

  return [
    { url: baseUrl, lastModified: new Date(), changeFrequency: 'weekly', priority: 1.0 },
    { url: `${baseUrl}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${baseUrl}/pricing`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${baseUrl}/analyze`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${baseUrl}/privacy`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.4 },
    { url: `${baseUrl}/terms`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.4 },
  ];
}
```

Then delete `public/sitemap.xml`. Do the same for robots.txt:
```tsx
// src/app/robots.ts
import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', allow: '/', disallow: ['/dashboard/', '/api/'] },
    sitemap: 'https://ungouge.ai/sitemap.xml',
  };
}
```

---

### H9. No `Suspense` boundaries — entire page blocks on slowest component

**File:** `src/app/layout.tsx`  
**Issue:** There are no `<Suspense>` boundaries anywhere in the app. If/when pages become Server Components with async data fetching, the entire page will block rendering until all data is fetched. Interactive components like `ChatWidget` and `CookieConsent` should also be wrapped in Suspense to prevent them from blocking the main content paint.

**Fix:**
```tsx
// src/app/layout.tsx
import { Suspense } from 'react';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.variable}>
        <div className="flex flex-col min-h-screen">
          <Header />
          <ErrorBoundary>
            <main className="flex-grow">{children}</main>
          </ErrorBoundary>
          <Footer />
          <Suspense fallback={null}>
            <CookieConsent />
          </Suspense>
          <Suspense fallback={null}>
            <ChatWidget />
          </Suspense>
        </div>
      </body>
    </html>
  );
}
```

---

### H10. Dashboard layout auth check duplicates Header auth check

**File:** `src/app/dashboard/layout.tsx` (lines 16-31)  
**Issue:** The dashboard layout independently calls `/api/auth/me` in a `useEffect`, which is the same call the Header makes. With the AuthProvider fix (H4), this duplication goes away. But there's also a deeper issue: the layout shows a loading spinner while checking auth, but the page `children` have already been sent to the client — the auth check is cosmetic only.

**Fix:** Use middleware (C4) for actual protection, and AuthProvider (H4) for UI state. The dashboard layout should not independently verify auth.

---

### H11. `ReportCard` component missing `'use client'` directive but used in client context

**File:** `src/components/ReportCard.tsx` (line 1)  
**Issue:** `ReportCard` has no `'use client'` directive. It's imported and used inside `ReportPage` which is a Client Component, so it works fine *today*. However, if the report page is converted to a Server Component (per fix C3), this will need explicit handling. Not a current bug, but a correctness issue — the component uses no hooks or browser APIs, so it should stay as a Server Component. Mark it clearly.

**Fix:** No code change needed — but when refactoring per C3, ensure `ReportCard` remains importable from both server and client contexts. Since it has no `'use client'`, it's already correctly a Server Component.

---

### H12. `connect-src` CSP doesn't include Stripe domains

**File:** `next.config.js` (line 9)  
**Issue:** The CSP `connect-src` only allows `self`, `api.ungouge.ai`, and `gemini.googleapis.com`. But the app redirects to Stripe Checkout for payments. If any Stripe.js is loaded in the future (e.g., for embedded checkout), it would be blocked. More critically, analytics/monitoring services would also be blocked.

**Fix:** Add Stripe domains to connect-src:
```
connect-src 'self' https://api.ungouge.ai https://gemini.googleapis.com https://*.stripe.com;
```

---

## 🟡 MEDIUM

### M1. No per-page metadata on most pages

**Files:**  
- `src/app/page.tsx` — no metadata export (Client Component, can't export metadata)
- `src/app/analyze/page.tsx` — no metadata export (Client Component)
- `src/app/report/[id]/page.tsx` — no metadata export (Client Component)
- `src/app/dashboard/page.tsx` — no metadata export
- `src/app/login/page.tsx` — no metadata export
- `src/app/register/page.tsx` — no metadata export

**Issue:** Only the root layout exports metadata. Individual pages can't export `metadata` because they're all Client Components. This means every page shows the same title "Ungouge.ai – Fair Contractor Quote Analysis" — poor for SEO and user orientation.

**Fix:** Converting pages to Server Components (C2, H2) unlocks per-page metadata:
```tsx
// src/app/analyze/page.tsx
export const metadata: Metadata = {
  title: 'Analyze Your Quote',
  description: 'Upload your contractor quote for instant, data-backed analysis.',
};
```

For pages that must remain Client Components, use `generateMetadata` from a parent layout or a server-side page wrapper.

---

### M2. `ChatWidget` has stale closure in `handleQuickQuestion`

**File:** `src/components/ChatWidget.tsx` (lines 112-115)  
**Issue:** `handleQuickQuestion` sets `inputText` then calls `handleSendMessage` in a `setTimeout`. But `handleSendMessage` reads `inputText` from state, which won't have updated yet due to React's batched state updates.

**Current:**
```tsx
const handleQuickQuestion = (question: string) => {
  setInputText(question);
  setTimeout(() => handleSendMessage(), 100);
};
```

**Fix:** Pass the question directly:
```tsx
const handleSendMessage = async (overrideText?: string) => {
  const userMessage = (overrideText ?? inputText).trim();
  if (!userMessage) return;
  setInputText('');
  addUserMessage(userMessage);
  // ... rest of logic
};

const handleQuickQuestion = (question: string) => {
  handleSendMessage(question);
};
```

---

### M3. `ChatWidget` welcome message has missing dependency in useEffect

**File:** `src/components/ChatWidget.tsx` (lines 45-53)  
**Issue:** The `useEffect` that sends the welcome message references `messages.length` and `isOpen` but only lists `[isOpen]` as a dependency. Also, `addBotMessage` is not in the dependency array.

**Fix:**
```tsx
useEffect(() => {
  if (isOpen && messages.length === 0) {
    const timer = setTimeout(() => {
      addBotMessage("👋 Hi! I'm here to answer questions...");
    }, 300);
    return () => clearTimeout(timer);
  }
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [isOpen]); // messages.length intentionally excluded to only trigger once
```

Add the eslint comment to document the intentional exclusion.

---

### M4. No `aria-expanded` on FAQ buttons

**File:** `src/app/page.tsx` (line ~189)  
**Issue:** The FAQ accordion buttons don't have `aria-expanded` attributes, making them inaccessible to screen readers.

**Fix:**
```tsx
<button
  onClick={() => setOpenFaqIndex(openFaqIndex === index ? null : index)}
  className="w-full flex items-center justify-between text-left"
  aria-expanded={openFaqIndex === index}
  aria-controls={`faq-answer-${index}`}
>
```
And on the answer:
```tsx
{openFaqIndex === index && (
  <div id={`faq-answer-${index}`} role="region" className="mt-4 pt-4 border-t border-gray-200">
```

---

### M5. Mobile menu lacks focus management and `Escape` key handling

**File:** `src/components/Header.tsx`  
**Issue:** The mobile menu opens/closes but:
- Focus doesn't move into the menu when opened
- Pressing Escape doesn't close it
- Focus isn't trapped within the menu
- No `aria-expanded` on the hamburger button

**Fix:**
```tsx
<button
  className="md:hidden p-2 rounded-lg hover:bg-gray-100"
  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
  aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
  aria-expanded={mobileMenuOpen}
  aria-controls="mobile-menu"
>
```

Add Escape key handler:
```tsx
useEffect(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      setMobileMenuOpen(false);
      setUserMenuOpen(false);
    }
  };
  document.addEventListener('keydown', handleEscape);
  return () => document.removeEventListener('keydown', handleEscape);
}, []);
```

---

### M6. User menu dropdown lacks keyboard navigation

**File:** `src/components/Header.tsx` (lines 71-110)  
**Issue:** The user dropdown menu can only be operated with a mouse. It has no:
- `role="menu"` / `role="menuitem"` attributes
- Arrow key navigation
- `Escape` to close
- Focus management when opened

**Fix:** Add ARIA menu attributes and keyboard handling:
```tsx
<div
  role="menu"
  aria-orientation="vertical"
  className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-xl border border-gray-200 py-2"
>
  <Link role="menuitem" href="/dashboard" /* ... */>Dashboard</Link>
  <Link role="menuitem" href="/dashboard/quotes" /* ... */>My Quotes</Link>
  {/* etc. */}
</div>
```

---

### M7. `PriceGauge` gauge labels overlap on small screens

**File:** `src/components/PriceGauge.tsx` (lines 58-73)  
**Issue:** The "Fair Low" and "Fair High" labels are absolutely positioned with `translateX(-50%)`. When the fair range is narrow, these labels will overlap and become unreadable on mobile.

**Fix:** Add responsive handling:
```tsx
{/* Labels - hidden on very small screens, shown as a legend instead */}
<div className="relative h-8 hidden sm:block">
  {/* ... existing positioned labels ... */}
</div>
<div className="sm:hidden flex justify-between text-xs text-gray-600 mt-2">
  <span>Fair: ${fairLow.toLocaleString()}</span>
  <span>— ${fairHigh.toLocaleString()}</span>
</div>
```

---

### M8. `FileUpload` response is consumed twice — `await response.json()` after progress steps

**File:** `src/components/FileUpload.tsx` (lines 78-100)  
**Issue:** The code checks `response.ok`, then does visual progress steps with `setTimeout`, then calls `response.json()`. But the response body may have already been consumed or timed out. The progress steps (uploading → extracting → analyzing) are **fake** — the response has already been received.

**Fix:** Fetch the data first, then show progress:
```tsx
const uploadAndParse = async (file: File) => {
  setUploading(true);
  setUploadStep(1);
  setUploadProgress('Uploading your quote...');

  try {
    const formData = new FormData();
    formData.append('file', file);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/quotes/parse-upload`, {
      method: 'POST',
      credentials: 'include',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Unable to process your file.');
    }

    const data = await response.json();

    // Show progress steps AFTER data is ready (cosmetic, but honest)
    setUploadStep(2);
    setUploadProgress('Extracting text...');
    await new Promise((r) => setTimeout(r, 400));

    setUploadStep(3);
    setUploadProgress('Analyzing...');
    await new Promise((r) => setTimeout(r, 400));

    setUploadStep(4);
    setUploadProgress('Complete!');
    await new Promise((r) => setTimeout(r, 300));

    onFileProcessed(data);
    // ...
```

---

### M9. Notification toggles don't persist — state is lost on reload

**File:** `src/app/dashboard/settings/page.tsx` (lines 5-9, 41)  
**Issue:** Notification preferences are local `useState` with a `// TODO: Save to backend` comment. Changes are lost on page reload. This is UX-breaking for a settings page.

**Fix:** Implement the API call:
```tsx
const handleNotificationChange = async (key: keyof typeof notifications) => {
  const newPrefs = { ...notifications, [key]: !notifications[key] };
  setNotifications(newPrefs); // Optimistic update

  try {
    await api.put('/api/auth/notifications', newPrefs);
  } catch (error) {
    // Revert on failure
    setNotifications(notifications);
    // Show error toast
  }
};
```

---

### M10. Login page "Remember me" checkbox does nothing

**File:** `src/app/login/page.tsx` (line ~136)  
**Issue:** There's a "Remember me" checkbox that isn't wired to any state or sent to the API. It's cosmetic-only.

**Fix:** Either implement it (send to backend to control cookie duration) or remove it to avoid misleading users:
```tsx
// Option A: Remove it
// Simply delete the checkbox div

// Option B: Wire it up
const [rememberMe, setRememberMe] = useState(false);

// In handleSubmit:
body: JSON.stringify({ email, password, remember_me: rememberMe }),
```

---

### M11. `axios` imported alongside native `fetch` — inconsistent HTTP client

**Files:** `src/app/report/[id]/page.tsx` (uses axios), `src/components/QuoteForm.tsx` (uses axios), all other files use native `fetch`  
**Issue:** The app uses both `axios` and native `fetch` for HTTP calls. This:
- Increases bundle size (axios is ~13KB gzipped)
- Creates inconsistent error handling patterns
- The `src/lib/api.ts` utility uses `fetch`, but some components use `axios` directly

**Fix:** Standardize on `fetch` + the `api.ts` utility. Remove `axios` from `package.json`:
```bash
npm uninstall axios
```

Replace axios usage:
```tsx
// Before (QuoteForm.tsx):
const quoteResponse = await axios.post(`${apiUrl}/api/quotes`, data, { withCredentials: true });

// After:
const quoteResponse = await api.post('/api/quotes', data);
```

---

### M12. Missing `<label>` associations on some form inputs

**File:** `src/components/ChatWidget.tsx` (line ~174)  
**Issue:** The chat input field has no associated `<label>`. Screen readers won't know what the input is for.

**Fix:**
```tsx
<label htmlFor="chat-input" className="sr-only">Ask a question</label>
<input
  id="chat-input"
  type="text"
  value={inputText}
  // ...
/>
```

---

### M13. Images in Header don't specify dimensions consistently

**File:** `src/components/Header.tsx` (line 62), `src/app/dashboard/layout.tsx` (lines 68, 117)  
**Issue:** Logo images use `next/image` correctly with `width`/`height`, but the `priority` prop is only on one of them. The dashboard layout logo doesn't have `priority`, which could delay LCP for dashboard pages.

**Fix:**
```tsx
// src/app/dashboard/layout.tsx line 68
<Image
  src="/images/logo-small.png"
  alt="Ungouge.ai"
  width={130}
  height={41}
  priority  // Add this
/>
```

---

### M14. `localStorage.clear()` on logout clears all site storage

**Files:** `src/components/Header.tsx` (line 49), `src/app/dashboard/layout.tsx` (line 41), `src/lib/api.ts` (line 35)  
**Issue:** Calling `localStorage.clear()` and `sessionStorage.clear()` nukes *everything*, including cookie consent preferences if they were stored in localStorage, any theme preferences, etc.

**Fix:** Only clear what you own:
```tsx
// Clear specific keys
localStorage.removeItem('ug_user_cache');
sessionStorage.removeItem('ug_session');
// Don't clear everything
```

---

### M15. No CSRF protection on state-changing requests

**Files:** `src/app/login/page.tsx`, `src/app/register/page.tsx`, `src/app/dashboard/settings/page.tsx`  
**Issue:** The app uses cookie-based auth (`credentials: 'include'`) but there's no CSRF token mechanism visible. Cookie-authenticated POST/PUT/DELETE requests are vulnerable to CSRF attacks.

**Fix:** Implement CSRF protection. Options:
1. **SameSite cookies** — if the backend sets `SameSite=Strict` or `SameSite=Lax` on auth cookies, this mitigates most CSRF (check backend config)
2. **CSRF token** — include a token from a meta tag or cookie in request headers
3. **Custom header** — require `X-Requested-With: XMLHttpRequest` on all mutation requests (simple but effective)

---

### M16. The `connect-src` CSP doesn't include `localhost` for development

**File:** `next.config.js` (line 9)  
**Issue:** In development, API calls go to `localhost:8000` but the CSP only allows `self`, `api.ungouge.ai`, and `gemini.googleapis.com`. This means CSP violations fire constantly in dev.

**Fix:** Conditionally adjust CSP for development:
```js
const isDev = process.env.NODE_ENV === 'development';
const connectSrc = isDev
  ? "connect-src 'self' http://localhost:8000 https://api.ungouge.ai https://gemini.googleapis.com"
  : "connect-src 'self' https://api.ungouge.ai https://gemini.googleapis.com https://*.stripe.com";
```

---

## 🟢 LOW

### L1. Testimonials use `[...Array(5)].map()` for star ratings — fragile pattern

**File:** `src/app/page.tsx` (lines ~128, 149, 170)  
**Issue:** Creating arrays with `[...Array(5)]` works but is less readable than a utility.

**Fix:**
```tsx
// Create a simple utility
function StarRating({ count = 5 }: { count?: number }) {
  return (
    <div className="flex items-center gap-1" aria-label={`${count} out of 5 stars`}>
      {Array.from({ length: count }, (_, i) => (
        <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
      ))}
    </div>
  );
}
```

---

### L2. `seo.ts` has dead page metadata entries

**File:** `src/lib/seo.ts` (lines 60-110)  
**Issue:** `PAGE_METADATA` has entries for `how_it_works`, `search`, `saved_reports`, and `blog` — pages that don't exist in the app. Dead configuration.

**Fix:** Remove unused entries or add a comment marking them as planned:
```tsx
// TODO: Future pages — uncomment when implemented
// how_it_works: { ... },
// blog: { ... },
```

---

### L3. SEO helper functions `generateOpenGraphTags` and `generateTwitterCardTags` are unused

**File:** `src/lib/seo.ts` (lines 118-142), `src/app/layout.tsx` (line 5)  
**Issue:** These functions are imported in layout.tsx but never called — the metadata export handles OG/Twitter tags natively via the Next.js Metadata API.

**Fix:** Remove the unused imports and potentially the functions if they're not needed elsewhere:
```tsx
// layout.tsx — remove unused imports
import {
  DEFAULT_METADATA,
  SITE_CONFIG,
  // Remove: generateOpenGraphTags,
  // Remove: generateTwitterCardTags,
  generateOrganizationSchema,
  generateSoftwareApplicationSchema,
  renderJsonLd,
} from '@/lib/seo';
```

---

### L4. `ChatWidget` message IDs use `Date.now()` — possible duplicates

**File:** `src/components/ChatWidget.tsx` (lines 70, 79)  
**Issue:** Message IDs are `Date.now().toString()`. If two messages are added in the same millisecond (e.g., quick question + bot response), IDs will collide.

**Fix:**
```tsx
let messageIdCounter = 0;
const generateId = () => `msg-${Date.now()}-${++messageIdCounter}`;
```

Or use `crypto.randomUUID()`:
```tsx
id: crypto.randomUUID(),
```

---

### L5. Inconsistent button styling patterns

**Files:** Various  
**Issue:** Some buttons use the `btn-primary` / `btn-secondary` CSS classes, while others use inline Tailwind classes. This creates maintenance burden and inconsistency.

Examples:
- `src/app/dashboard/settings/page.tsx` line 52: `className="btn-secondary text-sm"` ✅
- `src/app/dashboard/settings/page.tsx` line 97: inline `className="px-4 py-2 bg-red-50 text-red-600 border..."` ❌
- `src/components/CookieConsent.tsx`: all buttons use inline classes ❌

**Fix:** Create additional component classes in `globals.css`:
```css
.btn-danger {
  @apply bg-red-600 text-white px-4 py-2 rounded-lg font-semibold
         hover:bg-red-700 transition-all duration-200
         focus:outline-none focus:ring-4 focus:ring-red-200;
}

.btn-ghost {
  @apply px-4 py-2 rounded-lg font-medium text-gray-600
         hover:bg-gray-100 transition-all duration-200
         focus:outline-none focus:ring-4 focus:ring-gray-200;
}
```

---

### L6. `tailwind.config.js` not audited — custom colors may be missing

**File:** (not provided in audit scope but referenced)  
**Issue:** Classes like `text-primary-600`, `bg-primary-50`, `text-success`, `text-danger`, `text-warning` are used throughout but we can't verify the Tailwind config defines them. If any are missing, they'll silently produce no styles.

**Fix:** Verify `tailwind.config.js` includes all custom color definitions. Run `npx tailwindcss --help` or check for missing class warnings in dev.

---

### L7. Footer social links use inline SVGs — could use a component

**File:** `src/components/Footer.tsx` (lines 95-160)  
**Issue:** Four social media icons are inline SVGs with ~15 lines each. This is verbose and hard to maintain.

**Fix:** Extract to a component or use `lucide-react` icons where available:
```tsx
// For X/Twitter, Lucide doesn't have the new X logo, so inline SVG is fine.
// But extract to a shared component:
function SocialIcon({ href, label, children }: { href: string; label: string; children: React.ReactNode }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors" aria-label={label}>
      {children}
    </a>
  );
}
```

---

### L8. No TypeScript strict null checks verification

**File:** `tsconfig.json`  
**Issue:** `strict: true` is set, which is good. However, the `DEFAULT_METADATA.ogImage!` usage in `layout.tsx` (line 49) uses non-null assertion. This is a code smell — if `ogImage` is always defined, the type should reflect that.

**Fix:** Make `ogImage` required in the `PageMetadata` interface for the default:
```tsx
// Or simply check:
images: DEFAULT_METADATA.ogImage ? [DEFAULT_METADATA.ogImage] : [],
```

---

### L9. `QuoteForm` total calculation doesn't account for quantity

**File:** `src/components/QuoteForm.tsx` (line ~93)  
**Issue:** 
```tsx
const totalQuoted = lineItems.reduce((sum, item) => sum + (item.quoted_price || 0), 0);
```
This sums `quoted_price` without multiplying by `quantity`. If the quoted price is per-unit, the total will be wrong.

**Fix:** Clarify semantics. If `quoted_price` is the total for that line item:
```tsx
// Add a comment clarifying this is the total per line item, not per-unit price
const totalQuoted = lineItems.reduce((sum, item) => sum + (item.quoted_price || 0), 0);
```

If it's per-unit:
```tsx
const totalQuoted = lineItems.reduce(
  (sum, item) => sum + (item.quoted_price || 0) * (item.quantity || 1),
  0
);
```

---

### L10. `next.config.js` uses CommonJS — should use ESM or `next.config.ts`

**File:** `next.config.js`  
**Issue:** Uses `module.exports` (CommonJS). Next.js 14+ supports `next.config.ts` natively, which gives type checking.

**Fix:** Rename to `next.config.ts`:
```tsx
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // ... rest of config with full type checking
};

export default nextConfig;
```

---

## Architecture Recommendations (Non-Blocking)

### A1. Consider Route Groups for marketing vs. app layouts
The current pattern of Header/Footer self-hiding based on pathname is fragile. Route Groups would give proper layout separation.

### A2. Consider upgrading to Next.js 15
Next.js 14.2.35 is stable but Next.js 15 brings: async params (Promise-based), improved caching defaults, React 19 support, and the `after()` API. Plan the upgrade.

### A3. Add error monitoring (Sentry/LogRocket)
The `ErrorBoundary` component logs to console. In production, unhandled errors will be invisible. Add Sentry:
```bash
npx @sentry/wizard@latest -i nextjs
```

### A4. Add analytics
No analytics implementation is visible. For a pre-launch product, add at minimum privacy-respecting analytics (Plausible, Fathom) to track conversion funnel: landing → analyze → payment.

### A5. Consider `next/dynamic` for heavy client components
`ChatWidget` and `CookieConsent` are loaded on every page. Use dynamic imports to code-split:
```tsx
const ChatWidget = dynamic(() => import('@/components/ChatWidget'), { ssr: false });
const CookieConsent = dynamic(() => import('@/components/CookieConsent'), { ssr: false });
```

---

## Pre-Launch Checklist

- [ ] Fix C1: Remove `unsafe-eval` from CSP
- [ ] Fix C2: Make landing page a Server Component
- [ ] Fix C3: Server-side render report pages
- [ ] Fix C4: Add authentication middleware
- [ ] Fix C5: Sanitize JSON-LD output
- [ ] Fix H1: Add `loading.tsx`, `error.tsx`, `not-found.tsx`
- [ ] Fix H2: Make analyze page a Server Component
- [ ] Fix H6: Standardize API calls through proxy
- [ ] Fix H8: Convert sitemap/robots to Next.js dynamic generation
- [ ] Fix M1: Add per-page metadata
- [ ] Fix M10: Remove or implement "Remember me" checkbox
- [ ] Fix M15: Verify CSRF protection
- [ ] Add error monitoring (Sentry)
- [ ] Add analytics
- [ ] Run Lighthouse audit and fix any remaining issues
- [ ] Test with screen reader (VoiceOver/NVDA)
- [ ] Test payment flow end-to-end with Stripe test mode
