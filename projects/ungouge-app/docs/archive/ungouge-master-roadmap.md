# Ungouge.ai — Master Roadmap

## Executive Summary

**Ungouge.ai** is a consumer web tool that helps homeowners verify whether contractor quotes are fair, complete, and use quality materials. Users upload a quote (PDF, image, or text), and an AI-powered engine parses line items, benchmarks costs against market data, flags red flags, and produces a plain-English report with actionable negotiation tips.

**Market opportunity:** U.S. homeowners spend $500–600B annually on improvements. Studies show 40–50% of quotes are overpriced, with an average overcharge of ~$400. Several startups (QuoteEvaluator, Quotalyze, Savior) validate the concept but no dominant player exists yet.

**Revenue model:** Freemium — first report free, then $9.99/report or $14.99/mo subscription. Affiliate revenue from contractor referrals, financing partners, and marketplace integrations provides supplemental income.

**Key pivot from original docs:** The original documents specified Bubble.io as the tech stack. **We are replacing this with a proper code-first stack** (Next.js + FastAPI + PostgreSQL) for performance, scalability, cost control, and the ability for Ish (AI) to build and maintain it directly. This eliminates Bubble's workload-unit limitations, vendor lock-in, and scaling ceilings.

**Target launch:** 5–6 weeks from project start. Jason's time commitment: 20 hours/week (120 hours to launch). This bandwidth allows parallel workstreams — legal, marketing, and testing all run alongside the build, compressing the timeline and shipping a more polished, feature-rich MVP.

---

## Product Vision & Core Features

### The Core Loop
1. **Upload** → User drops a PDF/image/text of their contractor quote
2. **Parse** → OCR + AI extracts line items, quantities, prices, materials
3. **Analyze** → Each item benchmarked against market data; red flags detected
4. **Report** → One-page summary + detailed line-by-line breakdown
5. **Act** → Negotiation tips, alternative suggestions, next steps

### MVP Feature Set (Phase 1 — Weeks 1–6)

| Feature | Description |
|---------|-------------|
| **Quote Upload** | PDF, image (JPG/PNG), paste text. Drag-drop interface. |
| **OCR Pipeline** | GPT-4o Vision for image/scanned PDFs; direct text extraction for digital PDFs |
| **AI Parsing** | Extract line items into structured JSON: description, qty, unit price, total, category |
| **Price Benchmarking** | Compare each item against market data (Craftsman API + public sources) |
| **Red Flag Detection** | Vague items, missing scope, unusually high/low prices, no warranty info |
| **Quality/Warranty Check** | Identify brands/models, retrieve warranty info, flag unspecified materials |
| **Alternative Suggestions** | Suggest comparable but cheaper/better materials when relevant |
| **Plain-English Report** | Summary verdict + line-by-line analysis with confidence scores |
| **PDF Export** | Downloadable report for negotiation |
| **User Accounts** | Email/password auth, saved reports, usage tracking |
| **Stripe Payment** | Free first report, then $9.99/report or $14.99/mo subscription |
| **Email Delivery** | Auto-send report via email (Postmark/Resend) |
| **Mobile Responsive** | Full mobile support — upload photos from phone |

### Phase 2 Features (Weeks 7–10)

| Feature | Description |
|---------|-------------|
| **Multi-Quote Comparison** | Upload 2–3 quotes for same project, get side-by-side analysis |
| **Referral Program** | Unique codes, free report rewards for referrals |
| **Regional Adjustments** | ZIP-code-based labor rate and material cost adjustments |
| **Confidence Scoring** | High/Medium/Low confidence per line item based on data quality |
| **Content/SEO Pages** | Programmatic pages: "HVAC cost in [City]" for organic traffic |
| **Admin Dashboard** | Internal tool to review analyses, monitor quality, manage users |

### Phase 3 Features (Weeks 11–16+)

| Feature | Description |
|---------|-------------|
| **Contractor Referral Marketplace** | Connect users with vetted contractors (affiliate revenue) |
| **Financing Partner Integration** | Link to home improvement loan providers |
| **User Feedback Loop** | "Was this accurate?" → feeds back into data model |
| **Subscription Tiers** | Basic/Pro/Enterprise pricing |
| **API for Partners** | White-label analysis for home inspectors, real estate agents |
| **E-Signature Integration** | Accept/reject quotes digitally |

---

## Target Service Categories (Launch)

1. **HVAC** — ~3M replacements/yr, $8–15K avg
2. **Roofing** — ~5M replacements/yr, $7–16K avg
3. **Plumbing** — ~9M water heater installs/yr + repairs
4. **Solar** — ~0.8M installs/yr, $15–30K avg
5. **Painting** — ~10M+ pro jobs/yr, $2–5K avg
6. **Electrical** — Panel upgrades, rewiring, EV chargers

---

## Phased Implementation Plan

> **Jason @ 20 hrs/week** runs 3 parallel tracks from Day 1. See `ungouge-labor-breakdown.md` for detailed task assignments per person.

### Phase 1: Build + Business Setup + Marketing Prep (Weeks 1–4)

**Week 1: Foundation (Ish builds / Jason sets up business)**

*Ish:*
- [ ] Set up GitHub repo with monorepo structure (frontend + backend)
- [ ] Initialize Next.js frontend with Tailwind CSS
- [ ] Initialize FastAPI backend with SQLAlchemy + Alembic
- [ ] Set up PostgreSQL database (Supabase or Railway)
- [ ] Configure environment variables, CI/CD (Vercel + Railway/Render)
- [ ] Design database schema: Users, Reports, LineItems, Benchmarks
- [ ] Implement user auth (NextAuth.js + JWT)

*Jason (Track A — Legal/Business):*
- [ ] File LLC (Wyoming or VT)
- [ ] Apply for EIN
- [ ] Open Mercury business bank account
- [ ] Set up Stripe business account
- [ ] Set up business email (hello@ungouge.com)
- [ ] Begin shopping Tech E&O insurance

**Week 2: Core Pipeline + Landing Page (Ish builds / Jason starts marketing)**

*Ish:*
- [ ] Build file upload component (react-dropzone)
- [ ] Implement OCR pipeline: PDF text extraction (PyMuPDF) + GPT-4o Vision for images
- [ ] Design and test AI parsing prompts (structured JSON output)
- [ ] Set up Stripe integration (products, prices, checkout, webhooks)
- [ ] Deploy "Coming Soon" landing page with email capture

*Jason (Track B — Marketing Prep):*
- [ ] Write/sketch "dream report" to guide Ish
- [ ] Draft landing page copy with Ish
- [ ] Set up social media profiles (Twitter/X, LinkedIn, Facebook, Instagram)
- [ ] Begin collecting sample quotes (target: 25–30 across all 6 categories)
- [ ] Review/finalize Terms of Service and Privacy Policy (Ish drafts)
- [ ] Bind E&O insurance policy

**Week 3: Analysis Engine + Content (Ish builds / Jason writes + tests)**

*Ish:*
- [ ] Build price benchmarking engine (Craftsman API + fallback data)
- [ ] Implement red flag detection rules
- [ ] Build quality/warranty lookup system
- [ ] Create report generation engine (structured data → formatted report)
- [ ] Build negotiation script generator
- [ ] Build "What's Missing" checklist engine (per-category expected items)

*Jason (Tracks B+C — Content + Testing):*
- [ ] Review/edit first 5 blog articles (Ish drafts)
- [ ] Publish blog articles to site
- [ ] Test OCR pipeline with 10+ sample quotes — report issues
- [ ] Create lead magnet PDF ("23 Red Flags in Contractor Quotes")
- [ ] Build launch contact list (20–30 press/blogger targets)
- [ ] Identify 10+ home inspectors for partnership outreach

**Week 4: Polish + Integration Testing (Both in sync)**

*Ish:*
- [ ] Build report display page (responsive, professional design)
- [ ] Implement PDF export
- [ ] Set up email delivery (Resend or Postmark)
- [ ] Build user dashboard (saved reports, account management)
- [ ] Payment flow: free first report → paywall → Stripe Checkout
- [ ] Mobile optimization pass
- [ ] Referral program system (codes, tracking, rewards)
- [ ] Analytics integration (GA4 + PostHog)

*Jason:*
- [ ] End-to-end testing: upload → parse → analyze → report → pay → email
- [ ] Test 25+ quotes across all 6 categories, document accuracy issues
- [ ] Review report tone and clarity — rewrite anything confusing
- [ ] Test referral program flow
- [ ] Test Stripe payment + subscription flows
- [ ] Review/edit 5 more blog articles
- [ ] Begin warm outreach to inspectors ("launching soon, want early access?")

### Phase 2: Launch + Early Growth (Weeks 5–6)

*Ish:*
- [ ] Programmatic SEO: generate 500+ city/trade landing pages
- [ ] Multi-quote comparison feature
- [ ] Regional ZIP-code adjustments (BLS data integration)
- [ ] Admin dashboard for internal quality review
- [ ] Bug fixes from beta testing
- [ ] A/B testing framework for pricing experiments

*Jason:*
- [ ] **LAUNCH DAY** — Product Hunt, Reddit, HN, IndieHackers
- [ ] Email blast to waitlist
- [ ] Press outreach (personalized pitches to 15+ bloggers/journalists)
- [ ] Social media launch campaign (daily posts for 1 week)
- [ ] Begin inspector partnership outreach (formal pitches with live demo)
- [ ] Real estate agent outreach (5–10 contacts)
- [ ] Monitor first 50 real user reports — manual QA for accuracy
- [ ] Respond to all user feedback and support inquiries
- [ ] Write/edit 5 more blog articles (total: 15 at launch)

### Phase 3: Scale & Optimize (Weeks 7–10+)

*Ish:*
- [ ] Partner API for home inspectors (co-branded reports)
- [ ] Contractor referral marketplace
- [ ] User feedback loop → data improvement pipeline
- [ ] Advanced subscription management
- [ ] Performance optimization + cost reduction
- [ ] Financing partner integrations

*Jason (20 hrs/week ongoing):*
- [ ] Customer support & community engagement (3–4 hrs/wk)
- [ ] Formalize inspector/agent partnerships (contracts, onboarding)
- [ ] Content marketing: 2 articles/week + social posts + newsletter
- [ ] Small paid ads experiments (Google Ads, $300/mo)
- [ ] Data quality spot-checks with Ish
- [ ] A/B pricing analysis and optimization
- [ ] Business admin (bookkeeping, compliance)
- [ ] Feature prioritization based on user feedback

---

## Legal & Regulatory Requirements

### Critical — Do Before Launch
| Item | Detail |
|------|--------|
| **LLC Formation** | Wyoming or Vermont LLC. ~$125 filing + $50/yr registered agent. Pass-through taxation. |
| **EIN** | IRS Form SS-4 for business banking and Stripe |
| **Business Banking** | Mercury or Wise Business account |
| **Terms of Service** | "AS IS" disclaimer, liability cap at $100 or 1 month subscription, "informational purposes only" |
| **Privacy Policy** | CCPA/GDPR compliant. Disclose OCR processing, data retention, third-party APIs |
| **UPPA Disclaimer** | "Not a Public Adjuster" — critical for states like FL, TX, IL. Never reference insurance claims |
| **Tech E&O Insurance** | ~$90/mo for $1M coverage. Covers claims of data inaccuracy causing loss |
| **Report Disclaimers** | Every report: "For informational purposes only. Not professional advice. Verify independently." |

### Insurance Claim Kill Zone
The app must **never** imply advocacy regarding insurance claims. Position strictly as a "Market Research Tool" providing informational benchmarks. The word "Insurance" should not appear in UI copy related to analysis.

---

## Marketing Strategy

### Pre-Launch (Weeks 1–4)
- [ ] Secure domains (already done: ungouge.com, ungouge.app, etc.)
- [ ] Landing page with email capture ("Get your first quote check free")
- [ ] Social media profiles (Twitter/X, LinkedIn, Facebook, Instagram)
- [ ] "Coming Soon" campaign — target 500 email signups
- [ ] Create lead magnet: "23 Red Flags in Contractor Quotes" PDF
- [ ] Begin 5 blog posts targeting high-volume cost queries

### Launch (Weeks 5–6)
- [ ] Product Hunt launch (schedule, prepare assets, first comment narrative)
- [ ] Reddit posts (r/homeimprovement, r/construction, r/personalfinance)
- [ ] Hacker News "Show HN" post
- [ ] Email blast to waitlist
- [ ] Press release to home improvement bloggers/journalists
- [ ] Personal network outreach (friends/family to generate first 50 reports)

### Post-Launch Growth (Ongoing)
- [ ] SEO content: 2 articles/week targeting "[project] cost in [city]"
- [ ] Programmatic SEO: auto-generated city/trade pages
- [ ] Partnership outreach: home inspectors, real estate agents
- [ ] Referral program activation
- [ ] Nextdoor community engagement
- [ ] Email newsletter: monthly tips, savings stories, new features
- [ ] Social proof: collect testimonials, publish case studies
- [ ] Limited paid ads experiments ($300/mo budget): Google high-intent keywords

### Channel Priority (Ranked by CAC efficiency)
1. **SEO / Content Marketing** — CAC ~$1–2, slow but highest ROI
2. **Partnerships (Inspectors, Agents)** — CAC ~$1–2, high conversion
3. **Referral Program** — CAC ~$0–1
4. **Email Marketing** — CAC <$1 (retention/upsell)
5. **Product Hunt / Reddit** — Free, burst traffic
6. **Google Ads (targeted)** — CAC $5–10, for high-intent terms only
7. **Facebook/Nextdoor** — CAC $50+, avoid for direct acquisition

---

## Pricing Strategy

| Tier | Price | Details |
|------|-------|---------|
| **Free Trial** | $0 | First report free (full-featured) |
| **Pay-Per-Report** | $9.99 | Single detailed analysis |
| **Monthly Subscription** | $14.99/mo | Unlimited reports |
| **Annual Subscription** | $99/yr ($8.25/mo) | Best value, lock-in |

**Satisfaction Guarantee:** Full refund if dissatisfied. Budget 5–10% of sales for refunds.

**Stripe Fee Impact:** At $9.99/report, Stripe takes ~$0.59 (5.9%) vs $0.33 on $1 (33%). The higher price point dramatically improves unit economics vs. the original $1/report model.

---

## Key Metrics & Success Criteria

| Metric | Target | No-Go Threshold |
|--------|--------|-----------------|
| Parsing Accuracy | ≥85% | <60% |
| Free→Paid Conversion | ≥8% | <5% |
| Customer Acquisition Cost | ≤$6 | >$15 |
| Monthly Paid Users (Month 6) | 150+ | <30 |
| Monthly Revenue (Month 6) | $1,500+ | <$300 |
| NPS Score | ≥+30 | <0 |
| Report Generation Time | <60 seconds | >3 minutes |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| AI hallucination / wrong analysis | Medium-High | High | Confidence scoring, manual QA for first 200 reports, structured prompts with data grounding |
| Regional data gaps | High | Medium | Conservative defaults, location adjustments, user-submitted data over time |
| Low conversion / users won't pay | Medium | High | Free trial to prove value, satisfaction guarantee, A/B test pricing |
| UPPA legal exposure | Low | Critical | Strict "informational only" positioning, no insurance language, E&O insurance |
| Competitor copies approach | Medium | Medium | Data moat via user-contributed quotes, speed to market, trust building |
| High CAC / can't find users | Medium | High | Prioritize organic/SEO, partnerships, referrals over paid ads |
| Stripe fee erosion | Low | Low | $9.99 price point makes fees manageable (6% vs 33% at $1) |

---

## 12-Month Financial Projections

| Month | Traffic | Free Uploads | Paid Reports | Revenue | Costs | Profit |
|-------|---------|-------------|-------------|---------|-------|--------|
| 1–2 | 1,000 | 100 | 10 | $100 | $300 | -$200 |
| 3–4 | 3,000 | 300 | 30 | $300 | $350 | -$50 |
| 5–6 | 8,000 | 600 | 60 | $600 | $400 | $200 |
| 7–9 | 15,000 | 1,000 | 100 | $1,200 | $500 | $700 |
| 10–12 | 25,000 | 1,500 | 150 | $1,800 | $600 | $1,200 |

**Year 1 Total:** ~$12,000 revenue, ~$8,000 costs, ~$4,000 profit (base case)
**Upside (2x traffic):** ~$25,000 revenue, ~$12,000 costs, ~$13,000 profit

---

## Domains Secured
- ungouge.com ✅
- ungouge.app ✅ (redirects)
- quotarian.com ✅ (future brand option)
- quotarion.app ✅
- quotarion.com ✅

All expire Oct 5, 2026. Auto-renew enabled.
