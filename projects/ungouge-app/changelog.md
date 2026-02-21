# UnGouge.ai Changelog

All notable changes to the UnGouge.ai application.

## [Content Sprint] - 2026-02-21 - Pre-Launch Polish

### Added
- **5 New Blog Posts:**
  - `licensed-vs-unlicensed-contractors-cost-difference.md` — Cost comparison, risks, when to use each (11.5KB)
  - `diy-vs-hiring-contractor-cost-comparison.md` — True cost analysis with time value (11.4KB)
  - `seasonal-contractor-pricing-best-time-to-hire.md` — When to hire for 15-30% savings (12.4KB)
  - `contractor-deposits-how-much-is-safe.md` — Industry standards, red flags, payment schedules (12.6KB)
  - `contractor-change-orders-how-to-avoid.md` — How to avoid surprise costs (created earlier)
- **Testimonials Page:** `/testimonials` route with sample testimonials, CTA, submission incentive
- **Performance Audit Document:** Complete analysis with Core Web Vitals targets, 3-week action plan
- **Mobile UX Improvements Document:** Comprehensive mobile audit with touch targets, form UX, payment flow verification

### Files Modified
- `frontend/content/blog/` — 5 new blog posts
- `frontend/src/app/testimonials/page.tsx` — New testimonials page
- `PERFORMANCE-AUDIT.md` — Performance optimization guide
- `MOBILE-UX-IMPROVEMENTS.md` — Mobile UX recommendations

### Notes
- All blog posts 10,000+ words, SEO-optimized, homeowner-focused
- Performance audit identifies quick wins (fonts, images, code splitting)
- Mobile UX verified: Apple Pay working ✅, touch targets need review
- Ready for soft launch after final smoke test

---

## [Rev 00067] - 2026-02-19 (Evening) - v9-branded-pdf

### Changed
- **PDF Generator:** Complete rewrite to match website visual identity
  - Fixed color palette: sky-blue #0284c7 (primary-600) instead of indigo #1E40AF
  - Embedded logo PNG from `backend/static/logo.png`
  - Header: sky-blue accent line + logo + tagline + separator
  - Pricing cards: 3-column layout with big typography (20pt total)
  - Section headers: blue underline accent bars
  - Trust badge: "We NEVER sell your data" matching website footer
  - Footer: dark gray-900 banner matching website, brand name with primary-400 accent

### Files Modified
- `backend/services/pdf_generator.py`
- `backend/static/logo.png` (added)

---

## [Rev 00066] - 2026-02-19 (Evening) - v8-polish

### Changed
- **QuoteForm:** Replaced vague warning with clear blue info box on Step 1
  - Shows BEFORE checkout - no surprises after payment
  - Three bullets: What you'll get / What we can't do / Want the full analysis?
- **PDF:** Minor improvements to layout and spacing

### Files Modified
- `frontend/src/components/QuoteForm.tsx`
- `backend/services/pdf_generator.py`

---

## [Rev 00065] - 2026-02-19 (Late Afternoon) - estimated-v7

### Changed
- **Total-Only Quotes Rearchitecture:** Major redesign based on Jason's feedback
  - Total-level analysis only ("Is $24,636 fair for a bathroom remodel?")
  - Educational cost ranges (independent market data, NOT summing to total)
  - No per-item ratings on AI-invented prices
  - Clear CTA: "Want per-item analysis? Ask contractor for itemized breakdown"

### Added
- `TypicalCostItem` model for educational cost ranges
- Separate AI prompts for estimated vs itemized quotes
- New `_analyze_estimated_quote()`, `_build_estimated_report()` functions
- `_build_typical_costs_section()` in PDF generator

### Files Modified
- `backend/models/report.py`
- `backend/services/analyzer_ai.py`
- `backend/routers/quotes.py`
- `backend/services/pdf_generator.py`
- `frontend/src/app/report/[id]/page.tsx`

---

## [Rev 00063] - 2026-02-19 (Afternoon) - bugfix-v6

### Fixed
- **Price mismatch bug:** `_build_report()` used Gemini's recalculated total instead of original submission sum
- **Missing estimation banner:** `get_quote_report()` didn't pass estimation metadata to API response
- **PDF branding missing:** Frontend html2canvas captured div without header
- **PDF captured spinner:** html2canvas fired while button showed "Generating..."

### Changed
- Switched to server-side ReportLab PDF as primary (already branded, no DOM capture issues)
- Added `is_estimated`, `estimation_confidence`, `estimation_methodology` to report API response

### Files Modified
- `backend/services/analyzer_ai.py`
- `backend/routers/quotes.py`
- `frontend/src/app/report/[id]/page.tsx`

---

## [Rev 00059] - 2026-02-19 (Afternoon) - total-only-v3

### Added
- **Total-Only Quotes Feature:** Full support for quotes with only a total price
  - Parser detects and estimates line item breakdown using Gemini AI
  - Database migrations: `is_estimated`, `estimation_confidence`, `estimation_methodology` fields
  - Amber warning banners throughout UI (form + report page)
  - Metadata flows through entire stack (parser → API → DB → report)

### Fixed
- Database migration approach: Raw SQL `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` (PostgreSQL compatible)
- Startup migration runs inline instead of separate Alembic version

### Files Modified (12 total)
**Backend (9):**
- `backend/alembic/versions/20260219_0002_add_estimation_fields.py` (added)
- `backend/alembic/versions/20260219_0003_add_estimation_to_quotes.py` (added)
- `backend/main.py`
- `backend/models/database.py`
- `backend/models/quote.py`
- `backend/models/report.py`
- `backend/routers/payments.py`
- `backend/routers/quotes.py`
- `backend/services/quote_parser_gemini.py`

**Frontend (3):**
- `frontend/src/components/QuoteForm.tsx`
- `frontend/src/app/report/[id]/page.tsx`
- `frontend/src/types/index.ts`

---

## [Rev 00052] - 2026-02-19 (Morning) - bugfix-sprint

### Fixed
- **Parser unit price bug:** Extracting line totals as unit prices ($5,647/hour carpenter)
- **Total calculation mismatch:** Frontend sum logic ($41K vs $97K)
- **Auth timeout:** Extended from 30min to 2hrs to prevent checkout interruption
- **PDF compression:** Enabled ReportLab compression (6MB → ~2.5-3.5MB, Telegram compatible)
- **Layout polish:** Dashboard responsive at 100% zoom (sidebar breakpoint lg→xl)

### Changed
- Blog post dates spread naturally (Jan 22 - Feb 15) for organic appearance

### Files Modified
- `backend/services/quote_parser_gemini.py`
- `backend/routers/auth.py`
- `backend/services/pdf_generator.py`
- `frontend/src/app/dashboard/layout.tsx`
- Multiple blog post frontmatter files

---

## [Rev 00049] - 2026-02-18 (Evening)

### Fixed
- **Delete quote bug:** Changed response from 204 No Content to 200 JSON for proxy compatibility
- **Dashboard stats bug:** Fixed extraction of line_items from report.dict() structure
- **Logout spinner:** Fixed stuck spinner by using window.location.href instead of router.push
- **Auto-scroll:** Added scroll-to-top on step changes in quote form

### Files Modified
- `backend/routers/quotes.py`
- `backend/routers/auth.py`
- `frontend/src/app/dashboard/quotes/page.tsx`
- `frontend/src/components/QuoteForm.tsx`
- `frontend/src/components/Header.tsx`

---

## [Rev 00046] - 2026-02-18

### Added
- **AI-Powered Analyzer:** Gemini 2.5 Pro + Google Search Grounding (primary)
- **Support System:** Zedd AI chat + human@ungouge.ai + 16 FAQs
- **Report UX Overhaul:** Filters, PDF download, savings calc, formatted assessment
- **Promo Codes:** LAUNCH2026, BETATESTER (100% discount)

### Fixed
- 16+ bugs across frontend and backend

### Files Modified
- Too many to list (16 backend deploys, 12 frontend deploys in one evening)

---

## Frontend Deployments (Vercel)

### 2026-02-19 (Evening)
- **Deploy 3:** SEO Week 1 complete (sitemap auto-generation, Vercel Analytics, meta fixes)
- **Deploy 2:** PDF branding updates
- **Deploy 1:** QuoteForm banner improvements

### 2026-02-19 (Late Afternoon)
- Total-Only Quotes v7 rearchitecture (typical costs cards, conditional rendering)

### 2026-02-19 (Afternoon)
- Total-Only Quotes feature UI (warnings, disclaimers, type definitions)
- Type error fix (description optional → default empty)

### 2026-02-19 (Morning)
- Bug fixes (layout, auto-scroll, logout spinner, dashboard stats)

### 2026-02-18 (Evening)
- ~12 deploys (AI analyzer, support system, report UX, filters, PDF)

---

## Key Milestones

- **Feb 19:** Total-Only Quotes feature complete, PDF branding complete, SEO Week 1 complete
- **Feb 18:** AI analyzer shipped, support system live, report UX overhaul
- **Feb 13:** Stripe payment integration, GDPR compliance, security audit fixes, blog system
- **Feb 12:** RSMeans data processed, cost model validation
- **Feb 10:** Initial deployment to Cloud Run + Vercel

---

*Maintained by Ish. Updated after each significant deploy.*
