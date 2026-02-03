# ungouge.ai — Enhanced Business Plan
## From Zero to $100K: A Bootstrap SaaS Playbook
### February 2026

---

# EXECUTIVE SUMMARY

## The Problem

Every year, 37.8 million American homeowners hire contractors. Most have zero way to know if they're being overcharged. They Google cost ranges, get vague answers, and either overpay or spend weeks collecting multiple quotes. The average homeowner leaves **$1,500-$5,000 on the table per major project** simply because they lack pricing intelligence.

## The Solution

**ungouge.ai** lets homeowners upload a photo of any contractor quote and receive an instant, AI-powered, line-by-line analysis comparing every charge against authoritative cost databases adjusted for their specific location. In under 60 seconds, they know if they're getting a fair deal — or getting gouged.

## The Market

- **TAM:** $530M (26.5M annual quote events × $20 avg. price)
- **SAM:** $47.8M (digitally savvy homeowners with projects >$1K)
- **Year 1 Target:** $30K-$100K (1,500-5,000 analyses)
- **Year 3 Target:** $400K-$1M

## The Model

| Metric | Value |
|--------|-------|
| Price per analysis | $19.99 |
| COGS per analysis | ~$1.00 |
| Gross margin | 95% |
| Monthly break-even | 11 analyses |
| CAC (organic/pSEO) | ~$2-5 |
| LTV (1.5 analyses avg) | ~$30 |
| LTV:CAC ratio | 6-15x |

## The Moat

25,000+ programmatic SEO pages targeting "how much does [trade] cost in [city]" — the exact query homeowners search before and after getting a quote. First-mover advantage in a keyword space with zero competition from quote-analysis tools.

## The Ask

This is a bootstrap venture. No funding needed. Total investment to launch: **~$2,000** (LLC, domain, 3 months of tooling). Profitable from Month 2.

---

# 1. FINANCIAL MODELS

## 1.1 Revenue Projections (3 Scenarios)

### Conservative (Slow pSEO Growth)

| Month | Analyses/Mo | Revenue | Cumulative |
|-------|-------------|---------|------------|
| 1 (Mar '26) | 20 | $400 | $400 |
| 2 | 35 | $700 | $1,100 |
| 3 | 50 | $1,000 | $2,100 |
| 6 | 120 | $2,400 | $9,000 |
| 12 | 300 | $6,000 | $33,000 |
| 18 | 500 | $10,000 | $78,000 |
| 24 | 750 | $15,000 | $138,000 |

**Year 1 total: $33,000** ✅ Hits low end of Jason's target

### Base Case (Moderate Growth + pSEO Kicks In)

| Month | Analyses/Mo | Revenue | Cumulative |
|-------|-------------|---------|------------|
| 1 | 30 | $600 | $600 |
| 2 | 60 | $1,200 | $1,800 |
| 3 | 100 | $2,000 | $3,800 |
| 6 | 300 | $6,000 | $20,000 |
| 12 | 700 | $14,000 | $80,000 |
| 18 | 1,200 | $24,000 | $185,000 |
| 24 | 1,800 | $36,000 | $320,000 |

**Year 1 total: $80,000** ✅ Middle of Jason's target range

### Optimistic (Viral Moment + Strong SEO)

| Month | Analyses/Mo | Revenue | Cumulative |
|-------|-------------|---------|------------|
| 1 | 50 | $1,000 | $1,000 |
| 3 | 200 | $4,000 | $8,000 |
| 6 | 800 | $16,000 | $52,000 |
| 12 | 2,000 | $40,000 | $220,000 |
| 24 | 5,000 | $100,000 | $900,000 |

**Year 1 total: $220,000** 🚀

### Key Assumptions

- **Conversion rate from pSEO traffic:** 0.5-2% (industry standard for transactional landing pages)
- **pSEO traffic ramp:** 3-6 months for Google indexing, hockey stick at 6-9 months
- **Average analyses per customer:** 1.5 (some buy 3-packs)
- **Churn:** N/A for per-use model; subscription churn estimated at 15%/month
- **Seasonality:** +30% spring/summer, -20% winter (matches home improvement cycle)

## 1.2 Cost Structure

### Fixed Monthly Costs

| Item | Monthly Cost | Annual Cost |
|------|-------------|-------------|
| Bubble.io Growth Plan | $119 | $1,428 |
| Craftsman Estimator Cloud | $14 | $168 |
| Domain (ungouge.ai) | ~$3 | $35 |
| Postmark (email) | $15 | $180 |
| Google Cloud (Gemini API overhead) | $10 | $120 |
| Misc tools (analytics, etc.) | $30 | $360 |
| **Total Fixed** | **$191** | **$2,291** |

### Variable Costs Per Analysis

| Item | Cost |
|------|------|
| Gemini API | $0.05 |
| Stripe processing (2.9% + $0.30) | $0.88 |
| Postmark per email | $0.001 |
| **Total Variable** | **$0.93** |

### Sensitivity Analysis: What If Gemini Costs 10x More?

Even at $0.50/analysis (10x current estimate), total COGS only rises to $1.43/analysis. Gross margin drops from 95% to 93%. The business still works at any realistic AI pricing scenario.

### Sensitivity Analysis: What If Conversion Rate is Half Expected?

At 0.25% conversion (vs. 0.5% base case), Year 1 revenue drops to ~$40K. Still profitable, still within Jason's target range. The model is robust.

## 1.3 Profit & Loss — Base Case Year 1

| Quarter | Revenue | COGS | Fixed Costs | Net Profit |
|---------|---------|------|-------------|------------|
| Q1 (Mar-May) | $3,800 | $150 | $573 | $3,077 |
| Q2 (Jun-Aug) | $18,000 | $650 | $573 | $16,777 |
| Q3 (Sep-Nov) | $30,000 | $1,080 | $573 | $28,347 |
| Q4 (Dec-Feb) | $28,000 | $1,010 | $573 | $26,417 |
| **Year 1** | **$79,800** | **$2,890** | **$2,292** | **$74,618** |

**Net margin: 93.5%.** This is the beauty of a solo-founder, AI-powered, no-employee SaaS.

---

# 2. RISK MATRIX

## 2.1 Comprehensive Risk Assessment

### 🔴 Critical Risks

**1. Craftsman Data Access**
- **Risk:** No API exists; Terms of Service prohibit commercial use of their data in a consumer product
- **Probability:** 40%
- **Impact:** Cannot build core product as designed
- **Mitigation:** 
  - Contact Craftsman THIS WEEK
  - Prepare alternative: Build cost database from BLS data + RSMeans + public cost guides
  - Alternative: Use Gemini's training data for ballpark costs (less authoritative but functional)
  - Nuclear option: Manually input cost data from published Craftsman books (legal under first-sale doctrine for reference, but verify)

**2. Analysis Accuracy / Liability**
- **Risk:** AI produces wildly wrong analysis; homeowner makes bad decision; threatens legal action
- **Probability:** 15%
- **Impact:** Reputation destruction, potential lawsuit
- **Mitigation:**
  - Strong disclaimers ("for informational purposes only")
  - Include confidence scores on each line item
  - Show data sources for every comparison
  - Carry general liability insurance ($500-1,000/year)
  - Concierge phase validates accuracy before scaling

### 🟡 Moderate Risks

**3. Google Algorithm Change**
- **Risk:** Google devalues programmatic SEO pages
- **Probability:** 30% (over 2 years)
- **Impact:** 50-70% traffic reduction
- **Mitigation:** Diversify to social, email list, paid ads, partnerships. Ensure pSEO pages have genuine unique value (real cost data, not just template text).

**4. Competitor Entry**
- **Risk:** GreatBuildz, Homewyse, or a funded startup adds quote analysis
- **Probability:** 40% (over 2 years)
- **Impact:** Market share pressure, price competition
- **Mitigation:** Build brand, accumulate proprietary data, establish SEO moat. First-mover has 12-18 month head start.

**5. Low Demand**
- **Risk:** Homeowners won't pay for quote analysis
- **Probability:** 25%
- **Impact:** Revenue below targets
- **Mitigation:** Concierge phase validates demand with <$500 investment. Pivot to freemium (ad-supported) if needed.

### 🟢 Low Risks

**6. UPPA Legal Challenge**
- **Risk:** State regulator claims ungouge.ai is practicing public adjusting
- **Probability:** 5% (if properly positioned)
- **Impact:** Cease-and-desist in specific states
- **Mitigation:** Legal review, proper disclaimers, avoid insurance claim language

**7. Gemini API Deprecation/Price Hike**
- **Risk:** Google kills Gemini 1.5 Pro or raises prices dramatically
- **Probability:** 10%
- **Impact:** Need to switch models (Claude, GPT-4o, etc.)
- **Mitigation:** Abstract the AI layer. Any modern vision model can do OCR + analysis. Not locked in.

**8. Bubble.io Limitations**
- **Risk:** Bubble can't handle the pSEO scale or API complexity
- **Probability:** 20%
- **Impact:** Need to rebuild on different platform
- **Mitigation:** Bubble handles up to ~10K dynamic pages well. Beyond that, may need to generate static pages. Start with 5,000 and test.

---

# 3. GO-TO-MARKET TIMELINE

## Gantt Chart (Text Format)

```
2026
         FEB        MAR        APR        MAY        JUN        JUL        AUG
Week:    1234       1234       1234       1234       1234       1234       1234

PHASE 0: PRE-BUILD
LLC/Legal ████
Accounts  ██
Craftsman ████
Legal Rev  ████

PHASE 1: CONCIERGE MVP
Landing    ░░████
Upload Form  ░░████
Stripe Int    ░░██
Manual Ops      ░░████████████
Feedback              ░░████

PHASE 2: AUTOMATED MVP
Gemini Int              ░░████████
OCR Pipeline               ░░████████
Auto Reports                  ░░████████
Testing                           ░░████
Launch! 🚀                            ★

PHASE 3: pSEO ENGINE
Keyword Res    ░░████
Templates              ░░████
Content Gen              ░░████████████
Deploy Pages                  ░░████████████████
Monitor/Opt                         ░░████████████████████████

PHASE 4: GROWTH (ONGOING)
A/B Testing                              ░░████████████████████
Social/Content                           ░░████████████████████
Partnerships                                   ░░████████████████

████ = Active work (Jason's time)
░░ = AI prep work (minimal Jason time)
★ = Automated MVP launch
```

**Key milestones:**
- **Feb 15:** LLC filed, all accounts created
- **Mar 1:** Concierge MVP live (manual analysis)
- **Mar 31:** 20-50 concierge analyses completed, demand validated
- **Apr 15:** Automated MVP in beta testing
- **May 1:** Automated MVP public launch 🚀
- **Jun 1:** First 5,000 pSEO pages deployed
- **Aug 1:** 25,000 pSEO pages live, organic traffic growing
- **Dec 31:** $80K annual run rate (base case)

---

# 4. COMPETITIVE MOAT ANALYSIS (EXPANDED)

## 4.1 Porter's Five Forces

### Threat of New Entrants: MODERATE
- Low technical barriers (anyone can use Gemini + cost data)
- BUT: pSEO moat takes 6-12 months to build and years to replicate
- Brand recognition in a niche market is sticky

### Bargaining Power of Suppliers: LOW
- Multiple AI providers (Gemini, Claude, GPT)
- Multiple cost data sources (Craftsman, RSMeans, BLS)
- No single supplier dependency

### Bargaining Power of Buyers: HIGH
- One-time purchase, easy to comparison shop
- Free alternatives exist (though inferior)
- Mitigated by low price point and clear value prop

### Threat of Substitutes: HIGH
- "Just get 3 quotes" (free but time-consuming)
- Ask on Reddit (free but unreliable)
- ChatGPT DIY analysis (free but no cost database)
- Mitigated by convenience and authority of cost-database-backed analysis

### Competitive Rivalry: LOW (currently)
- Near-zero direct competitors
- GreatBuildz is adjacent but differently positioned
- Window of opportunity: 12-18 months before copycats

## 4.2 Moat Deepening Strategy (Year 1-3)

**Year 1 — SEO Moat:**
- 25,000 pSEO pages indexed and ranking
- Establish "ungouge" as a verb ("I ungouged my contractor quote")
- Build email list of 5,000+ homeowners

**Year 2 — Data Moat:**
- Proprietary database of 10,000+ analyzed quotes
- Real-world pricing intelligence beyond published cost books
- "Homeowners in [city] typically pay [X] for [trade]" — data no one else has

**Year 3 — Brand Moat:**
- Media coverage, press mentions
- Partnerships with real estate agents, home inspectors
- Trusted brand in consumer home improvement

---

# 5. PRODUCT ROADMAP (18 MONTHS)

## MVP (Launch)
- Upload contractor quote (image/PDF)
- AI-powered line-by-line analysis
- Location-adjusted fair market comparison
- Email delivery of report
- Single-purchase payment ($19.99)

## V1.1 (Month 3)
- Multi-quote comparison (upload 2-3 quotes, compare)
- 3-pack pricing ($39.99)
- Shareable report link
- Customer accounts (save past analyses)

## V1.2 (Month 6)
- Subscription tier ($49.99/month unlimited)
- Negotiation talking points in report
- "Questions to ask your contractor" section
- Mobile-optimized upload experience

## V2.0 (Month 12)
- Real-time chat with AI about your quote
- Contractor rating/review integration
- "Get competing quotes" partnership (referral revenue)
- White-label for real estate agencies

## V2.5 (Month 18)
- API for third-party integrations
- Contractor-side tool ("Price your quote competitively")
- Spanish language support
- Canadian market expansion

---

# 6. MARKETING STRATEGY

## 6.1 Channel Priorities (Ranked by ROI)

### 1. Programmatic SEO (Primary — 60% of effort)
- 25,000+ pages targeting long-tail cost queries
- Content value: Real cost data, not generic advice
- CTA: "Got a quote for [trade] in [city]? Upload it for instant analysis"
- Expected: 50,000-200,000 monthly organic visits by Month 12

### 2. Reddit & Forum Marketing (20% of effort)
- r/homeimprovement (2.8M members)
- r/homeowners (500K+)
- r/RealEstate
- r/FirstTimeHomeBuyer
- Strategy: Genuinely helpful answers + link to tool when relevant
- **Never spam.** Build reputation as a helpful expert.

### 3. Content Marketing / Blog (10% of effort)
- "Is your [trade] quote fair? A guide for [city] homeowners"
- "The 5 most overcharged line items on roofing quotes"
- "How to read a contractor estimate: A homeowner's guide"
- Cross-links to pSEO pages for internal linking

### 4. Social / Viral (5% of effort)
- TikTok/Instagram: Before/after of quote analysis
- "I saved $3,000 by ungouging my contractor quote" stories
- Twitter/X: Home improvement tips thread → CTA

### 5. Partnerships (5% of effort, growing in Year 2)
- Real estate agents (recommend to clients)
- Home inspectors (bundle with inspection services)
- Insurance adjusters (careful re: UPPA)
- Home warranty companies

## 6.2 Customer Acquisition Cost Estimates

| Channel | Estimated CAC | Volume Potential |
|---------|---------------|-----------------|
| pSEO (organic) | $0-2 | High |
| Reddit (organic) | $0-5 | Medium |
| Blog/content | $2-5 | Medium |
| Paid search | $15-30 | Medium (expensive) |
| Social media | $5-15 | Low-Medium |
| Partnerships | $5-10 | Medium (Year 2+) |

**Blended CAC target: $3-5** (achievable with pSEO-dominant strategy)

---

# 7. LEGAL & COMPLIANCE CHECKLIST

- [ ] Wyoming LLC formation ($100, online)
- [ ] EIN from IRS (free, immediate online)
- [ ] Business bank account (separate from personal)
- [ ] Stripe business verification
- [ ] General liability insurance ($500-1,000/year, optional but recommended)
- [ ] Terms of Service (AI-drafted, lawyer-reviewed)
- [ ] Privacy Policy (CCPA/GDPR compliant)
- [ ] UPPA compliance review by attorney ($500-1,000)
- [ ] Disclaimer language on all reports
- [ ] Craftsman data usage rights verification
- [ ] Trademark search for "ungouge" (optional, $225-400 USPTO filing)

---

# 8. KEY METRICS TO TRACK

## North Star Metric
**Monthly analyses completed** (proxy for revenue and product-market fit)

## Supporting Metrics

| Metric | Target (Month 6) | Target (Month 12) |
|--------|-------------------|--------------------|
| Monthly analyses | 300 | 700 |
| Monthly revenue | $6,000 | $14,000 |
| pSEO pages indexed | 5,000 | 25,000 |
| Organic monthly visitors | 10,000 | 50,000 |
| Conversion rate (visit → purchase) | 1% | 1.5% |
| Customer satisfaction (NPS) | >50 | >60 |
| Report accuracy (spot-check) | >90% | >95% |
| Support tickets/month | <20 | <50 |

---

*End of Phase 3: Enhanced Business Plan*
