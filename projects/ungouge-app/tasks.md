# Tasks (project: ungouge-app)

*Last updated: 2026-02-19 19:54 EST*

## Launch Readiness (Priority: CRITICAL)

### Testing & Validation
- [ ] **Test Total-Only Quotes with diverse inputs**
  - Handwritten quotes (poor OCR quality)
  - Different regions (Vermont, NYC, Texas, etc.)
  - Different project types (kitchen, bathroom, roof, HVAC)
  - Edge cases (very high/low totals, unusual descriptions)
  - Priority: High | Owner: Ish + Jason | Due: Feb 20

- [ ] **Real payment flow test**
  - Submit quote, pay $19.99 (no promo code)
  - Verify Stripe charge, email receipt, report delivery
  - Priority: High | Owner: Jason | Due: Before launch

- [ ] **Email delivery verification**
  - Password reset emails
  - Payment receipts
  - Report-ready notifications
  - Priority: High | Owner: Jason | Due: Before launch

### Content & SEO (Week 2)
- [ ] **Blog content refresh**
  - Update 34 existing posts with consistent branding
  - Match PDF/website visual identity
  - Ensure tone consistency
  - Priority: Medium | Owner: Ish | Due: Feb 20-21

- [ ] **Write new cost guide content**
  - Target high-intent keywords ("how much should X cost in 2026")
  - Regional guides (Vermont, NYC, Texas, California, etc.)
  - Project-specific deep dives (kitchen remodel, roof replacement)
  - Priority: Medium | Owner: Ish | Due: Week 2 (Feb 20-26)

### Community & Distribution (Week 3-4)
- [ ] **Reddit engagement**
  - r/HomeImprovement, r/Renovations, r/DIY
  - Value-first posts, not spam
  - Priority: Medium | Owner: Ish | Due: Week 3

- [ ] **Facebook groups**
  - Homeowner, renovation, contractor groups
  - Share insights, build trust
  - Priority: Medium | Owner: Ish | Due: Week 3

- [ ] **Product Hunt launch**
  - Prepare assets, description, screenshots
  - Coordinate launch day
  - Priority: Medium | Owner: Ish + Jason | Due: Week 4

## Technical Debt & Known Issues

### Active Bugs
- [ ] **Delete quote still shows "500 error" for user**
  - Quote does delete on refresh
  - Suspected Vercel proxy/caching issue
  - No DELETE requests reaching rev 00049 in logs
  - Priority: Medium | Owner: Ish | Due: This week

- [ ] **Dashboard stats accuracy**
  - Fix deployed, needs user verification
  - Priority: Medium | Owner: Jason | Due: When testing

### Features In Progress
- [ ] **Multi-file upload**
  - Backend endpoint complete
  - Need to implement `process_multiple_files()` in quote_parser_gemini.py
  - Approach: OCR each file separately, concatenate text, single Gemini analysis
  - Priority: Low | Owner: Ish | Due: Post-launch

- [ ] **"Request Re-Analysis" button**
  - Allow users to request updated analysis if quote changes
  - Priority: Low | Owner: Ish | Due: Post-launch

### Infrastructure
- [ ] **Mobile-responsive audit**
  - Full pass on all pages (report, quote form, dashboard)
  - Test on phone/tablet
  - Priority: Medium | Owner: Ish | Due: Before launch

- [ ] **Final smoke test**
  - End-to-end flow: upload → pay → report → PDF → email
  - All major browsers (Chrome, Safari, Firefox)
  - Mobile + desktop
  - Priority: High | Owner: Jason + Ish | Due: Before launch

## Post-Launch Features (Priority: LOW)

### Phase 2: Distribution & Reach
- [ ] **Mobile app (iOS + Android)**
  - PWA first or React Native
  - App store presence = credibility + push notifications
  - Priority: Low | Owner: TBD | Due: Q2 2026

- [ ] **Custom GPT**
  - "UnGouge Quote Analyzer" in ChatGPT store
  - Upload quote → get analysis
  - Funnels users to full reports on ungouge.ai
  - Priority: Low | Owner: Ish | Due: Q2 2026

- [ ] **Voice widget (OpenAI Realtime API)**
  - "Talk through your report" button
  - AI preloaded with specific quote analysis
  - Cost: ~$0.50-1.00/session
  - Priority: Low | Owner: Ish | Due: v1.1 (post-launch)

- [ ] **Email marketing**
  - Post-report follow-up sequence
  - Newsletter with pricing tips
  - Priority: Low | Owner: TBD | Due: Q2 2026

- [ ] **Partnerships**
  - Real estate agents
  - Home inspectors
  - Mortgage brokers
  - Priority: Low | Owner: Jason | Due: Q2 2026

### Long-Term Moat
- [ ] **Proprietary cost database**
  - Build from submitted quotes (with permission)
  - Aggregate data → better accuracy over time
  - Priority: Low | Owner: Ish | Due: Q3 2026

## Completed ✅

### Feb 19, 2026
- [x] Total-Only Quotes feature (revs 00057-00061, rearchitected to 00065)
- [x] PDF generator rewrite to match website branding (rev 00067)
- [x] QuoteForm UX improvements (blue info banner, clear expectations)
- [x] SEO Week 1: sitemap auto-generation, Vercel Analytics, Google Search Console
- [x] Google verification (DNS + meta tag)
- [x] Brand color fixes across codebase (#0284c7)

### Feb 18, 2026
- [x] AI-powered analyzer (Gemini 2.5 Pro + Search Grounding)
- [x] Support system (Zedd AI + human email + 16 FAQs)
- [x] Report UX overhaul (filters, PDF, savings calc)
- [x] Promo code system (LAUNCH2026, BETATESTER)
- [x] 16+ bug fixes across frontend and backend

### Feb 13, 2026
- [x] Stripe payment integration (full checkout flow)
- [x] Security audit + all critical/high fixes
- [x] Full GDPR compliance (21/21 items)
- [x] SEO optimization, blog system (34 posts)
- [x] Error boundaries, loading states
- [x] Backend test suite (46 tests)
- [x] Alembic migrations, Dockerfile
- [x] Cost model validation + critical bug fixes

---

*Use this file to track what's done, what's next, and what's blocked. Update after each major milestone.*
