# ungouge.ai - MVP Master Roadmap

**Mission:** Help businesses avoid getting overcharged by providing AI-powered quote analysis and vendor comparison.

**Target Launch:** 8-12 weeks from kickoff

---

## 🎯 MVP Success Criteria

**Must Have (Launch Blockers):**
- Users can submit quotes (PDF/image upload or paste text)
- AI extracts line items, pricing, and key terms
- System flags overpriced items vs. market benchmarks
- Users receive clear "gouging score" + actionable recommendations
- Stripe payment integration (pay-per-analysis or simple subscription)
- Basic user accounts (email/password + magic link)

**Core Metric:** 
- **Primary:** % of users who return for 2nd analysis within 30 days
- **Secondary:** Average $ saved per quote (self-reported)

**Out of Scope for MVP:**
- Multi-user/team accounts
- Integrations with procurement systems
- White-label/enterprise features
- Mobile apps (web-responsive only)
- Real-time vendor negotiation

---

## 📋 Phase Breakdown

### **Phase 0: Foundation (Week 1-2)**

**Goal:** Define core architecture, stack decisions, development environment

**Deliverables:**
- [ ] Tech stack finalized (see recommendations below)
- [ ] Database schema v1 (users, quotes, line_items, analyses)
- [ ] Dev environment setup (local + staging)
- [ ] Domain purchased, DNS configured
- [ ] GitHub repo initialized with CI/CD pipeline
- [ ] Core dependencies installed

**Key Decisions:**
- **Frontend:** Next.js 14+ (App Router) + Tailwind CSS + shadcn/ui
- **Backend:** Next.js API routes OR separate FastAPI service
- **Database:** PostgreSQL (Supabase for auth + DB, or self-hosted)
- **AI:** OpenAI GPT-4o for quote parsing + Claude for analysis/recommendations
- **Storage:** S3-compatible (Cloudflare R2 or AWS S3) for uploaded files
- **Hosting:** Vercel (frontend) + Railway/Fly.io (backend if separate)
- **Payment:** Stripe

**Technical Architecture:**
```
User Upload → File Storage (R2/S3) → AI Parser (GPT-4o Vision) → 
Structured Data → Market Benchmark Comparison → AI Analysis (Claude) → 
Report Generation → User Dashboard
```

---

### **Phase 1: Core Quote Parsing (Week 2-4)**

**Goal:** Get quote data extraction working reliably

**Deliverables:**
- [ ] Upload interface (drag-drop PDF/image, paste text)
- [ ] File storage pipeline (S3/R2 integration)
- [ ] GPT-4o Vision integration for OCR + extraction
- [ ] Structured output schema:
  ```json
  {
    "vendor": "Company Name",
    "quote_date": "2026-01-15",
    "total": 45000,
    "line_items": [
      {
        "description": "Dell PowerEdge R740",
        "quantity": 2,
        "unit_price": 8500,
        "total": 17000,
        "category": "server_hardware"
      }
    ],
    "terms": {
      "payment_terms": "Net 30",
      "warranty": "3 year onsite"
    }
  }
  ```
- [ ] Manual review/edit interface (let users fix parsing errors)
- [ ] Test with 20+ real-world quotes across verticals

**Success Metric:** 85%+ accuracy on line item extraction (manual validation)

---

### **Phase 2: Market Benchmarking (Week 4-6)**

**Goal:** Build the "gouging detection" engine

**Deliverables:**
- [ ] Market price database (initial seed data)
  - Manual curation: Top 100 common IT items (servers, laptops, licenses)
  - Web scraping: Dell, CDW, Newegg, Amazon Business
  - API integrations: Google Shopping API, Stripe Pricing Tables
- [ ] Pricing normalization logic (apples-to-apples comparison)
- [ ] Markup calculation:
  ```
  Markup % = ((Quote Price - Market Price) / Market Price) × 100
  ```
- [ ] Gouging score algorithm:
  ```
  Score = weighted average of:
  - Line item markups (70%)
  - Total quote markup (20%)
  - Suspicious terms (10%, e.g., "restocking fee >20%")
  ```
- [ ] Threshold definitions:
  - 0-15%: Fair
  - 15-30%: Elevated
  - 30-50%: High
  - 50%+: Extreme

**Success Metric:** Correctly identify "bad" quotes in 90%+ of test cases

---

### **Phase 3: AI Analysis & Recommendations (Week 6-7)**

**Goal:** Turn data into actionable insights

**Deliverables:**
- [ ] Claude-powered analysis engine
- [ ] Report generation with:
  - Executive summary (3 bullet points)
  - Gouging score + visual gauge
  - Line-by-line breakdown (flagged items highlighted)
  - Specific negotiation tactics:
    - "Ask vendor to match $X for [item]"
    - "Remove [unnecessary item] to save $Y"
    - "Compare against [alternative vendor] pricing"
  - Estimated savings potential
- [ ] Export to PDF (clean, professional formatting)
- [ ] Email delivery option

**Success Metric:** Users rate recommendations as "actionable" (4/5+) in beta testing

---

### **Phase 4: User Accounts & Payment (Week 7-9)**

**Goal:** Make it a real business

**Deliverables:**
- [ ] Auth system (Supabase Auth or NextAuth.js)
  - Email/password
  - Magic link login
  - Google OAuth (nice-to-have)
- [ ] User dashboard:
  - Quote history
  - Saved analyses
  - Usage stats
- [ ] Stripe integration:
  - **Pricing Model Option A (Recommended for MVP):** Pay-per-analysis
    - $29 per quote analysis (single)
    - $99 for 5 analyses (bulk discount)
  - **Pricing Model Option B:** Subscription tiers
    - Free: 1 quote/month (limited report)
    - Pro: $49/mo (10 quotes, full reports, export)
    - Business: $149/mo (unlimited, priority support)
- [ ] Payment flow (checkout, success/failure handling)
- [ ] Receipt/invoice generation

**Success Metric:** <5% payment failure rate, <10% abandoned checkouts

---

### **Phase 5: Polish & Launch Prep (Week 9-11)**

**Goal:** Ship-ready product

**Deliverables:**
- [ ] Landing page (value prop, how it works, pricing, CTA)
- [ ] SEO basics (meta tags, sitemap, robots.txt)
- [ ] Legal pages (Terms, Privacy, Refund Policy)
- [ ] Analytics (PostHog or Plausible)
- [ ] Error tracking (Sentry)
- [ ] Email notifications (Resend or SendGrid):
  - Analysis complete
  - Payment receipts
  - Weekly digest (if subscription model)
- [ ] Performance optimization:
  - Quote parsing <30s for typical document
  - Dashboard loads <2s
  - Mobile-responsive design
- [ ] Security audit:
  - File upload validation (type, size limits)
  - Rate limiting on API endpoints
  - Secure file storage (private buckets)
- [ ] Beta testing with 10-20 real users
- [ ] Onboarding flow (first-time user guide)

**Success Metric:** Beta users complete first analysis with <2 support questions

---

### **Phase 6: Launch & Iteration (Week 11-12)**

**Goal:** Go live, gather feedback, iterate

**Deliverables:**
- [ ] Public launch announcement (Twitter, LinkedIn, Product Hunt)
- [ ] Support channel setup (email, optional Discord/Slack)
- [ ] Monitoring dashboard (uptime, error rates, conversion funnel)
- [ ] Feedback collection mechanism (in-app survey, NPS)
- [ ] Post-launch iteration plan:
  - Week 1: Fix critical bugs, usability issues
  - Week 2-4: Add most-requested features
  - Month 2+: Expand market benchmarks, new verticals

**Success Metric:** 
- 100 signups in first 30 days
- 20%+ conversion to paid analysis
- <1% error rate on quote parsing

---

## 🏗️ Technical Stack Recommendations

### **Core Stack**
- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **UI Components:** shadcn/ui (Radix primitives)
- **Backend:** Next.js API routes (start simple, extract to FastAPI if needed)
- **Database:** PostgreSQL via Supabase (auth + DB + storage in one)
- **AI:** 
  - OpenAI GPT-4o (quote parsing, vision for PDFs/images)
  - Anthropic Claude 3.5 Sonnet (analysis, recommendations)
- **File Storage:** Cloudflare R2 (S3-compatible, cheaper egress)
- **Auth:** Supabase Auth
- **Payment:** Stripe
- **Email:** Resend (modern, simple API)
- **Analytics:** Plausible (privacy-friendly) or PostHog (product analytics)
- **Hosting:** Vercel (Next.js) + Supabase (DB/auth)

### **Development Tools**
- **Version Control:** GitHub
- **CI/CD:** GitHub Actions → Vercel auto-deploy
- **Error Tracking:** Sentry
- **API Testing:** Bruno or Postman
- **Database Migrations:** Prisma or Drizzle ORM

### **Why This Stack?**
- **Speed:** Next.js API routes = no separate backend initially
- **Cost:** Supabase free tier, Vercel hobby plan = $0 to start
- **Scalability:** Can extract backend to FastAPI/Python later if AI processing gets heavy
- **Developer Experience:** TypeScript + Prisma = type-safe, fast iteration

---

## 💰 Cost Estimates (Monthly, MVP Scale)

| Item | Cost |
|------|------|
| Vercel (Hobby → Pro if traffic grows) | $0-20 |
| Supabase (Free → Pro) | $0-25 |
| Cloudflare R2 (10GB storage, 100GB transfer) | ~$1 |
| OpenAI API (100 quotes @ $0.50 ea) | ~$50 |
| Anthropic API (100 analyses @ $0.30 ea) | ~$30 |
| Stripe (fees on revenue) | 2.9% + 30¢ per txn |
| Domain (.ai domain) | ~$80/year (~$7/mo) |
| Resend (email, 3k/mo free) | $0 |
| Plausible Analytics | $9 |
| **Total (low traffic):** | **~$120-150/mo** |

**Break-even (Pay-per-analysis model):**
- At $29/quote, need ~5-6 paid analyses/month to cover costs
- At 20% conversion, need ~30 signups/month

---

## 🚧 Risk Mitigation

### **Risk: Quote parsing accuracy too low**
- **Mitigation:** Manual review interface in MVP, human-in-the-loop
- **Backup plan:** Offer "premium parsing" with human QA for +$10

### **Risk: Market benchmark data insufficient**
- **Mitigation:** Start with narrow vertical (IT hardware/software), expand later
- **Backup plan:** Partner with price aggregators or industry orgs for data

### **Risk: Not enough users/demand**
- **Mitigation:** Pre-launch landing page with email capture, validate demand
- **Backup plan:** Pivot to B2B (sell to procurement teams, not individuals)

### **Risk: AI costs too high (unit economics broken)**
- **Mitigation:** Cache common item lookups, optimize prompts, batch processing
- **Backup plan:** Raise pricing, add usage caps

### **Risk: Legal liability (bad analysis leads to bad business decision)**
- **Mitigation:** Clear disclaimers ("recommendations, not guarantees"), ToS
- **Backup plan:** Require users to acknowledge "informational purposes only"

---

## 📊 Post-MVP Roadmap (Month 2-6)

**Potential Features (prioritize based on feedback):**
1. **Vendor comparison mode:** Upload multiple quotes, side-by-side analysis
2. **Negotiation templates:** Pre-written emails to send vendors
3. **Industry-specific benchmarks:** Construction, medical, legal, etc.
4. **Team accounts:** Share analyses with colleagues, approval workflows
5. **API access:** Let procurement software integrate
6. **Chrome extension:** Analyze quotes directly from email/web pages
7. **Mobile app:** Native iOS/Android (or just PWA)
8. **Historical tracking:** See how vendor pricing changes over time
9. **Vendor reputation scores:** Crowdsourced reviews + analysis
10. **White-label:** Let consultancies rebrand and resell

---

## ✅ Pre-Flight Checklist

**Before writing a single line of code:**
- [ ] Validate demand (10+ emails from landing page signups)
- [ ] Interview 3-5 target users (what quotes do they struggle with?)
- [ ] Confirm willingness to pay ($29 per analysis realistic?)
- [ ] Secure .ai domain or alternative
- [ ] Set up development environment (GitHub, Vercel, Supabase accounts)
- [ ] Define "done" criteria for MVP (ship with X features, not "perfect")

**Mindset:**
- **Imperfect action > perfect planning**
- **Ship in 8 weeks, iterate in public**
- **Talk to users every week**
- **Data > opinions (instrument everything)**

---

## 🎯 The One-Sentence MVP

**"Upload a quote, get a gouging score and specific negotiation tactics in 60 seconds."**

Everything else is nice-to-have. Ship this, learn, iterate.

---

**Last Updated:** 2026-01-31  
**Status:** Roadmap v1 - Ready for review and prioritization
