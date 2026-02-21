# Performance Audit - February 21, 2026

## Summary

Overall performance is good for a Next.js 14 app, but there are optimization opportunities.

**Current status:** ⚠️ Not measured (need Lighthouse/WebPageTest baseline)  
**Target:** Lighthouse score 90+ on all metrics

---

## Quick Wins (Implement First)

### 1. Image Optimization ✅ Already Done (mostly)

**Status:** Using Next.js `<Image>` component (automatic optimization)

**Check:** Verify all images use `<Image>` not `<img>`

```bash
# Find any non-optimized images
grep -r "<img" ~/clawd/projects/ungouge-app/frontend/src/app --include="*.tsx"
```

**If any found:** Replace with Next.js `<Image>` component

---

### 2. Font Optimization

**Current setup:** Check if using next/font

```typescript
// Should be in app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })
```

**If not using next/font:**
- Fonts load from Google Fonts (extra DNS lookup + download)
- FOUT (Flash of Unstyled Text) possible

**Fix:** Use `next/font` for automatic font optimization

---

### 3. Bundle Size Analysis

**Run bundle analyzer:**

```bash
cd ~/clawd/projects/ungouge-app/frontend
npm install --save-dev @next/bundle-analyzer
```

**Add to next.config.js:**

```javascript
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = withBundleAnalyzer({
  // existing config
})
```

**Analyze:**

```bash
ANALYZE=true npm run build
```

**Look for:**
- Large dependencies (>100KB)
- Duplicate packages
- Unused code

---

### 4. Code Splitting

**Check:** Are heavy components lazy-loaded?

**Example: PDF viewer (if you have one):**

```typescript
// Before (loads immediately)
import PDFViewer from '@/components/PDFViewer'

// After (loads only when needed)
import dynamic from 'next/dynamic'
const PDFViewer = dynamic(() => import('@/components/PDFViewer'), {
  loading: () => <p>Loading...</p>
})
```

**Candidates for lazy loading:**
- Chart libraries (if used)
- Rich text editors
- PDF viewers
- Large modals/drawers

---

## Medium Priority (Implement Week 2)

### 5. Static Generation

**Check:** Are blog posts statically generated?

**Current:** Should be ✅ (using `generateStaticParams`)

**Verify:**

```bash
cd ~/clawd/projects/ungouge-app/frontend
npm run build
# Check .next/server/app/blog/[slug] - should have pre-rendered HTML
```

**If not static:** Blog posts regenerate on every request (slow)

---

### 6. API Route Caching

**Check:** Do API routes have caching headers?

**Example: /api/quotes/my**

```typescript
export async function GET(request: Request) {
  const data = await fetchQuotes()
  
  return Response.json(data, {
    headers: {
      'Cache-Control': 'private, max-age=60, stale-while-revalidate=300'
    }
  })
}
```

**Benefit:** Reduces database queries for frequently accessed data

---

### 7. Database Query Optimization

**Check:** Are N+1 queries happening?

**Example (bad):**

```python
# Fetches quotes
quotes = db.query(Quote).all()
# Then for each quote, fetches user (N+1 queries!)
for quote in quotes:
    user = db.query(User).where(User.id == quote.user_id).first()
```

**Example (good):**

```python
# One query with join
quotes = db.query(Quote).join(User).all()
```

**Action:** Review backend query patterns in most-used endpoints

---

### 8. Compression

**Check:** Is gzip/brotli enabled?

**Vercel:** ✅ Automatic compression  
**Cloud Run:** Check response headers

```bash
curl -I https://ungouge-backend-[...].run.app/api/health | grep -i encoding
```

**Should see:** `content-encoding: gzip` or `br`

**If not:** Add compression middleware to FastAPI

---

## Low Priority (Nice to Have)

### 9. Prefetching

**Next.js automatically prefetches visible links.**

**Check:** Are critical pages prefetched?

```typescript
// Manual prefetch for time-sensitive pages
import Link from 'next/link'

<Link href="/analyze" prefetch={true}>
  Analyze Quote
</Link>
```

**Use sparingly:** Only for pages users will likely visit next

---

### 10. Service Worker / PWA

**Not implemented:** Site is not a PWA

**Benefit:**
- Offline support
- Faster repeat visits
- "Add to Home Screen" on mobile

**Effort:** Medium-high  
**Priority:** Low (not critical for MVP)

---

### 11. Database Connection Pooling

**Check:** Is SQLAlchemy pool configured?

**backend/models/database.py:**

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600
)
```

**If not set:** Default pool might exhaust connections under load

---

### 12. CDN for Static Assets

**Vercel:** ✅ Automatic CDN for static files  
**Cloud Run:** Static assets served from backend (slower)

**Optimization:** Move static assets (logo, images) to Cloud Storage + CDN

**Benefit:** Faster asset delivery worldwide

---

## Performance Metrics to Track

### Core Web Vitals (Google)

| Metric | Target | What It Measures |
|--------|--------|------------------|
| **LCP** (Largest Contentful Paint) | <2.5s | How fast main content loads |
| **FID** (First Input Delay) | <100ms | How fast page responds to interaction |
| **CLS** (Cumulative Layout Shift) | <0.1 | How much page jumps around while loading |

**Measure:** Use Lighthouse in Chrome DevTools or PageSpeed Insights

---

### Additional Metrics

- **TTFB** (Time to First Byte): <600ms (hosting latency)
- **FCP** (First Contentful Paint): <1.8s (when something appears)
- **TTI** (Time to Interactive): <3.8s (when page is fully usable)

---

## Performance Testing

### Run Lighthouse Audit

```bash
# Install globally
npm install -g lighthouse

# Run audit
lighthouse https://ungouge.ai --output html --output-path ./lighthouse-report.html --view
```

**Or:** Use Chrome DevTools > Lighthouse tab

---

### WebPageTest

**URL:** https://www.webpagetest.org

**Test:** https://ungouge.ai from multiple locations

**Look for:**
- TTFB >600ms (hosting issue)
- Large resource sizes (images, JS bundles)
- Render-blocking resources

---

### Real User Monitoring (Future)

**Option 1:** Vercel Analytics (built-in)  
**Option 2:** Google Analytics 4 (free)  
**Option 3:** Sentry Performance (paid)

**Benefit:** See actual user performance, not just lab tests

---

## Backend Performance

### API Response Times

**Target:** <200ms for most endpoints

**Measure:**

```bash
# Install httpie
pip install httpie

# Time API request
time http GET https://ungouge-backend-[...].run.app/api/health
```

**Common bottlenecks:**
- Database queries (>50ms)
- AI API calls (1-5 seconds)
- PDF generation (2-10 seconds)

**Optimization:**
- Cache frequently accessed data (Redis)
- Background jobs for slow tasks (report generation)
- Database indexes on commonly queried fields

---

### Database Indexes

**Check:** Are foreign keys indexed?

```sql
-- Should have indexes on:
- quotes.user_id
- payments.quote_id
- quote_line_items.quote_id
- analysis_reports.quote_id
```

**Add if missing:**

```sql
CREATE INDEX idx_quotes_user_id ON quotes(user_id);
CREATE INDEX idx_payments_quote_id ON payments(quote_id);
-- etc.
```

---

### Cloud Run Scaling

**Current:** Cold starts possible if instance scales to zero

**Mitigation:**
- Set min instances to 1 (costs ~$10/month, eliminates cold starts)
- Or accept 2-5 second cold start delay

**Command:**

```bash
gcloud run services update ungouge-backend \
  --region=us-central1 \
  --min-instances=1
```

---

## Mobile Performance

### Check Mobile Lighthouse Score

**Test:** Use Lighthouse mobile mode (simulated slow 4G)

**Common issues:**
- Images too large (use responsive images)
- Too much JavaScript (code splitting)
- Render-blocking resources

**Fix:** See recommendations from Lighthouse

---

### Touch Target Size

**Rule:** Interactive elements should be ≥48x48px

**Check:**

```bash
# Find small buttons
grep -r "className.*text-xs\|text-sm" ~/clawd/projects/ungouge-app/frontend/src --include="*.tsx" | grep -i button
```

**Fix:** Ensure buttons/links have enough padding for thumb taps

---

## Performance Budget

**Set limits to prevent regression:**

| Resource | Budget | Current | Status |
|----------|--------|---------|--------|
| JavaScript | <500KB | ? | ⏳ Measure |
| CSS | <100KB | ? | ⏳ Measure |
| Images | <1MB | ? | ⏳ Measure |
| Total page size | <2MB | ? | ⏳ Measure |
| Requests | <50 | ? | ⏳ Measure |

**Tool:** Use Lighthouse or bundle analyzer to measure

---

## Action Items (Prioritized)

### Week 1 (Immediate)
1. Run Lighthouse audit (baseline)
2. Check font optimization (next/font)
3. Verify image optimization (all using `<Image>`)
4. Run bundle analyzer (identify large deps)

### Week 2 (High Impact)
5. Add lazy loading to heavy components
6. Add API route caching headers
7. Review backend N+1 queries
8. Add database indexes if missing

### Week 3 (Polish)
9. Optimize bundle size (remove unused deps)
10. Add prefetching to critical pages
11. Consider Redis caching for frequently accessed data

### Future (Nice to Have)
12. Real user monitoring (Vercel Analytics)
13. Service worker / PWA
14. CDN for backend static assets

---

## Measurement Plan

**Baseline (now):**
- Run Lighthouse: https://ungouge.ai
- Run WebPageTest from 3 locations
- Measure API response times
- Measure bundle size

**Re-test (after optimizations):**
- Compare before/after scores
- Track improvement %

**Ongoing:**
- Weekly Lighthouse checks
- Monthly performance review

---

## Expected Improvements

| Optimization | Expected Gain |
|--------------|---------------|
| Font optimization | −200ms LCP |
| Image optimization | −500ms LCP |
| Code splitting | −300ms TTI |
| API caching | −100ms load time |
| Database indexes | −50ms API response |
| Bundle size reduction | −200ms TTI |

**Total estimated:** 1-2 second faster load time

---

**Performance audit complete. Next: Run baseline measurements and implement Week 1 actions.**
