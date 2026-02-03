# ungouge.ai — Phase 1: Market Viability Analysis
## PhD-Level Competitive Intelligence & Market Sizing
### Prepared: February 2026

---

## Table of Contents
1. [Executive Market Thesis](#1-executive-market-thesis)
2. [Competitive Landscape Deep Dive](#2-competitive-landscape-deep-dive)
3. [TAM / SAM / SOM Analysis](#3-tam--sam--som-analysis)
4. [Customer Persona Research](#4-customer-persona-research)
5. [Pricing Strategy Validation](#5-pricing-strategy-validation)
6. [Unit Economics & Gemini API Cost Model](#6-unit-economics--gemini-api-cost-model)
7. [Legal Positioning & UPPA Compliance](#7-legal-positioning--uppa-compliance)
8. [Competitive Moat Analysis](#8-competitive-moat-analysis)
9. [Key Risks & Mitigations](#9-key-risks--mitigations)
10. [Verdict: Go / No-Go Assessment](#10-verdict--go--no-go-assessment)

---

## 1. Executive Market Thesis

**The Core Insight:** There are ~86 million homeowner households in the US. Approximately 44% hire contractors annually. The vast majority have zero tools to verify whether they're being overcharged. They Google "[project type] cost in [city]" and get vague ranges from content-farm articles. No one is doing what ungouge.ai proposes: **take a photo of your actual quote → get a line-by-line fairness analysis against authoritative cost data.**

**The Gap:** The market has:
- Tools that help *contractors* estimate (Buildxact, ProEst, Contractor+) — these serve the supply side
- Free bid *comparison* tools (GreatBuildz BidCompareAI) — these compare bids to each other, not to fair market rates
- Generic cost lookup sites (Homewyse, HomeAdvisor cost guides) — no quote analysis, just ranges
- One scrappy startup (ConsultAPro / CheckThisEstimate.com) — charges $10 for a human contractor to review, not scalable

**Nobody is doing AI-powered, cost-database-verified, line-item analysis of contractor quotes for homeowners.**

This is a genuine whitespace opportunity.

---

## 2. Competitive Landscape Deep Dive

### 2.1 Direct Competitors (Homeowner-Facing Quote Analysis)

#### GreatBuildz BidCompareAI
- **What it does:** Free tool where homeowners upload up to 4 contractor bids; AI generates side-by-side comparison
- **Launched:** August 2025
- **Pricing:** Free (lead-gen for their contractor matching service)
- **Key limitation:** Compares bids *to each other*, not against fair market pricing. If all 3 contractors are overcharging, BidCompareAI says "they look similar." It's a feature, not a product.
- **Traction:** Significant press coverage (Miami Herald, WTOP, Fox affiliates). LA-based company with established contractor network.
- **Business model:** They monetize by matching homeowners with contractors (referral fees). The AI tool is a top-of-funnel marketing play.
- **Threat level: MEDIUM.** They validate the market but aren't solving the same problem. If they added cost database verification, they'd be a serious competitor. Monitor closely.

#### ConsultAPro (CheckThisEstimate.com)
- **What it does:** For $10, founder Christopher Fenton (a contractor) reviews your estimate via virtual appointment
- **Launched:** ~2024-2025
- **Pricing:** $10 per consultation
- **Key limitation:** Completely unscalable. One human reviewer. Limited to trades the founder knows.
- **Traction:** Minimal — basic WordPress site, no press coverage found
- **Threat level: LOW.** Validates demand at micro scale. Not a technology play.

#### Homewyse.com
- **What it does:** Free cost calculators for hundreds of home improvement tasks with location-adjusted pricing
- **Established:** 10+ years
- **Pricing:** Free (ad-supported)
- **Key limitation:** Provides cost ranges, not quote analysis. Homeowner has to manually compare line items. No OCR, no upload, no AI.
- **Traction:** High organic traffic. Likely millions of monthly visitors. Strong SEO presence.
- **Business model:** Advertising, contractor lead generation
- **Threat level: LOW-MEDIUM.** They own the SEO real estate for "how much does [X] cost in [city]" queries. They could theoretically add quote analysis but haven't in 10+ years. More likely a partnership or pSEO template to learn from.

### 2.2 Adjacent Competitors (Contractor-Facing Estimating Tools)

| Tool | Target User | Pricing | Relevance |
|------|-------------|---------|-----------|
| **Buildxact** | Builders/remodelers | $199-399/mo | For contractors, not homeowners |
| **Contractor+ (Estimatic AI)** | Small contractors | $29-99/mo | AI estimating for contractors |
| **ProEst** | Commercial estimators | Enterprise pricing | Wrong market entirely |
| **One Click Contractor** | Remodeling contractors | ~$200/mo | Contractor sales tool |
| **Handoff.ai** | Remodelers/handymen | Unknown | AI estimating for contractors |
| **Houzz Pro** | Design/remodel pros | $85-399/mo | Includes estimating |

**Key insight:** The entire estimating software industry is built for the *contractor* side. The homeowner side has been completely ignored because homeowners are not repeat buyers of software — they need it once or twice and they're done. This is why per-quote or low-cost subscription pricing is essential.

### 2.3 Indirect Competitors & Substitutes

| Alternative | What Homeowners Do Today | ungouge.ai Advantage |
|-------------|--------------------------|---------------------|
| **"Get 3 quotes"** | The standard advice | Time-consuming (days/weeks), still no benchmark for fairness |
| **Google "[project] cost [city]"** | Read HomeAdvisor/Angi articles | Vague ranges ("$5,000-$15,000"), no line-item analysis |
| **Ask Reddit/Facebook** | Post quote to r/homeimprovement | Anecdotal, location-blind, inconsistent |
| **Hire a consultant** | Pay a contractor to review | $50-200+, hard to find, conflict of interest |
| **Do nothing** | Accept the quote or negotiate blind | The default — and the problem |

### 2.4 Failed/Pivoted Companies in This Space

No major failures found in the *homeowner quote analysis* space because **nobody has seriously tried it.** This is both encouraging (whitespace) and cautionary (unproven demand at scale). The closest analog is the home inspection industry — homeowners routinely pay $300-500 for someone to verify the condition of a house. Paying $10-50 to verify the fairness of a $15,000 quote is arguably a much easier sell.

---

## 3. TAM / SAM / SOM Analysis

### 3.1 Total Addressable Market (TAM)

**US Home Improvement Market:** $894.2 billion (2024, GM Insights)

**Professional contractor spending subset:** ~$477 billion (Q3 2025 projection, Harvard JCHS LIRA report)

**But our TAM isn't "home improvement spending" — it's "homeowner willingness to pay for quote verification."**

**Better TAM calculation:**
- US homeowner households: ~86 million
- % who hire contractors annually: ~44% = **37.8 million households**
- % who get formal written quotes: ~70% (est.) = **26.5 million quote events per year**
- Average willingness to pay for verification: $15-30 per quote
- **TAM = 26.5M × $20 = $530 million/year**

This is a theoretical maximum if every homeowner who gets a quote pays for analysis. Obviously unrealistic, but it's the TAM ceiling.

### 3.2 Serviceable Addressable Market (SAM)

**Narrow to our realistic reach:**
- Homeowners who search online before hiring (digitally savvy): ~60% of 26.5M = 15.9M
- Who have projects >$1,000 (worth verifying): ~50% = 7.95M
- Who would consider using an online tool: ~30% = 2.39M
- **SAM = 2.39M × $20 = $47.8 million/year**

### 3.3 Serviceable Obtainable Market (SOM) — Year 1-3

**Year 1 (Concierge + Early MVP):**
- Target: 500-2,000 paying users
- Revenue: $10,000 - $40,000
- Source: pSEO organic traffic + Reddit/social marketing

**Year 2 (Automated MVP + Growth):**
- Target: 5,000-15,000 paying users
- Revenue: $100,000 - $300,000
- Source: Compounding pSEO + word of mouth + content marketing

**Year 3 (Mature Product):**
- Target: 20,000-50,000 paying users
- Revenue: $400,000 - $1,000,000
- Source: Brand recognition + partnerships + expanded trades

**Jason's Target ($30k-$100k/year):** Very achievable in Year 1-2 with just 1,500-5,000 quote analyses at $20/each.

---

## 4. Customer Persona Research

### 4.1 Primary Persona: "Cautious Carol"

**Demographics:**
- Age: 35-55
- Homeowner (single-family, suburban)
- Household income: $75,000-$150,000
- First or second major renovation
- College educated, comfortable with technology

**Psychographics:**
- Risk-averse — terrified of being ripped off
- Researches everything before buying (reads reviews, compares prices)
- Has heard horror stories about contractor overcharging
- Doesn't know enough about construction to evaluate quotes
- Values time — doesn't want to get 5+ quotes just to feel safe

**Trigger events:**
- Just received a quote that "feels high" but can't articulate why
- Got 2 quotes that are wildly different and doesn't know which is fair
- Insurance claim situation where contractor's estimate seems inflated
- First-time major project (kitchen, roof, HVAC) — no frame of reference

**Quote:** *"I got a quote for $18,000 for a bathroom remodel and I have no idea if that's reasonable. I don't want to insult the contractor by negotiating, but I also don't want to be a sucker."*

### 4.2 Secondary Persona: "Insurance Ian"

**Demographics:**
- Age: 30-65
- Homeowner dealing with property damage claim
- Any income level (insurance claims are democratic)

**Situation:**
- Had storm/water/fire damage
- Contractor gave them an estimate for repairs
- Insurance adjuster gave a different (usually lower) number
- Caught between two parties with competing financial interests
- Needs an independent verification

**Key insight:** This is where ungouge.ai must be EXTREMELY careful about UPPA. See Section 7.

### 4.3 Tertiary Persona: "Landlord Larry"

**Demographics:**
- Owns 1-10 rental properties
- Gets contractor quotes frequently
- More cost-conscious than owner-occupants
- Could be a repeat subscriber ($49/month plan)

**Value prop:** Subscription model natural fit. Gets 2-5 quotes per month, needs quick verification.

### 4.4 Emerging Persona: "Realtor Rachel"

**Uses case:** Real estate agents advising clients on pre-sale renovations or post-inspection repairs. Could recommend ungouge.ai to clients. B2B2C channel.

---

## 5. Pricing Strategy Validation

### 5.1 Pricing Benchmarks in Adjacent Markets

| Service | Price | Comparison |
|---------|-------|------------|
| Home inspection | $300-500 | Full property inspection |
| ConsultAPro quote review | $10 | Human review, basic |
| BidCompareAI | Free | Bid comparison only, lead-gen model |
| Homewyse | Free | DIY cost lookup, ad-supported |
| ChatGPT Plus (DIY analysis) | $20/mo | Generic, no cost database |
| Contractor+ estimating | $29-99/mo | For contractors |

### 5.2 Pricing Options Analysis

#### Option A: Per-Quote ($19-29/quote)
- **Pros:** Low barrier, matches the use case (most homeowners need 1-3 analyses), easy to understand value
- **Cons:** Lower LTV, harder to build recurring revenue, harder to forecast
- **Best for:** Cautious Carol (one-time need)

#### Option B: Subscription ($49/month)
- **Pros:** Recurring revenue, higher LTV, predictable
- **Cons:** Most homeowners don't need monthly analysis, high churn expected
- **Best for:** Landlord Larry (repeat need)

#### Option C: Hybrid (recommended)
- **Single analysis:** $19.99
- **3-pack:** $39.99 ($13.33/each)
- **Monthly unlimited:** $49.99/month
- **Annual unlimited:** $399/year ($33.25/month)

**Recommendation: Start with $19.99/single quote analysis.** This is the easiest to validate, easiest to explain, and matches the user's mental model ("I have a quote, I want it checked"). Add subscription later once you have repeat users.

### 5.3 Price Sensitivity Analysis

The key question: **At a $15,000 average project cost, would you pay $20 to know if you're being overcharged?**

This is a no-brainer value proposition. $20 is 0.13% of the project cost. If ungouge.ai saves the homeowner even $500 (by giving them data to negotiate), the ROI is 25x.

**Price ceiling:** ~$50/analysis for residential. Above that, the perceived risk of "what if the tool is wrong" exceeds the price.

**Price floor:** ~$10/analysis. Below this, the product feels cheap/unreliable. You want the price to signal quality.

**Sweet spot: $19.99** — psychologically under $20, feels like a serious tool, delivers obvious ROI.

---

## 6. Unit Economics & Gemini API Cost Model

### 6.1 Gemini 1.5 Pro Pricing (Current)

| Component | Cost |
|-----------|------|
| Input tokens (≤200K context) | $1.25 per 1M tokens |
| Input tokens (>200K context) | $2.50 per 1M tokens |
| Output tokens (≤200K context) | $5.00 per 1M tokens |
| Output tokens (>200K context) | $10.00 per 1M tokens |
| Image/document input | Included in token count |

### 6.2 Per-Quote Cost Breakdown

**Typical contractor quote:** 1-3 pages, mix of text and line items

**Gemini processing per analysis:**
- Image/OCR input: ~2,000-5,000 tokens (1-3 page document)
- System prompt + Craftsman data context: ~3,000-5,000 tokens
- Total input: ~8,000 tokens
- Output (detailed analysis): ~2,000-4,000 tokens
- **Total tokens per analysis: ~12,000**

**Gemini cost per analysis:**
- Input: 8,000 tokens × $1.25/1M = $0.01
- Output: 4,000 tokens × $5.00/1M = $0.02
- **Total Gemini cost: ~$0.03 per analysis**

Even with generous estimates (longer quotes, multiple passes, error retries), the AI cost per analysis is **$0.05-0.15 maximum.**

### 6.3 Craftsman National Estimator Cost

- National Estimator Cloud: **$13.99/month** for 10 costbooks
- This is a fixed cost regardless of volume
- At 100 analyses/month: $0.14/analysis
- At 1,000 analyses/month: $0.014/analysis
- **Note:** Need to verify if their Terms of Service allow programmatic/API access for a consumer-facing product. This is a critical dependency. If they don't offer an API, you may need to license the data differently or use it as a lookup reference rather than automated integration.

### 6.4 Full Cost Stack Per Analysis

| Cost Item | Per Analysis (at 500/mo) | Per Analysis (at 5,000/mo) |
|-----------|--------------------------|----------------------------|
| Gemini API | $0.05 | $0.05 |
| Craftsman data (amortized) | $0.03 | $0.003 |
| Bubble.io hosting | $0.06 | $0.006 |
| Postmark email | $0.001 | $0.001 |
| Stripe fees (2.9% + $0.30) | $0.88 | $0.88 |
| **Total COGS** | **$1.02** | **$0.94** |
| **Revenue at $19.99** | **$19.99** | **$19.99** |
| **Gross Margin** | **$18.97 (94.9%)** | **$19.05 (95.3%)** |

**This is a SaaS-grade margin.** The unit economics are exceptional because AI API costs have collapsed and the Craftsman data is a flat monthly fee.

### 6.5 Break-Even Analysis

**Monthly fixed costs:**
- Bubble.io (Growth plan): $119/month
- Craftsman National Estimator Cloud: $13.99/month
- Domain/hosting: ~$15/month
- Postmark: ~$15/month (for volume)
- Misc tools: ~$50/month
- **Total fixed: ~$213/month**

**Break-even: 11 analyses/month at $19.99** (after variable costs)

This means Jason needs just **11 paying customers per month** to cover all costs. Anything beyond that is pure profit margin.

---

## 7. Legal Positioning & UPPA Compliance

### 7.1 The UPPA Risk

UPPA (Unauthorized Practice of Public Adjusting) laws exist in most states and prohibit unlicensed individuals/companies from:
- Negotiating insurance claims on behalf of policyholders
- Acting as an advocate in insurance settlement disputes
- Adjusting or appraising insured losses

**Key states with aggressive UPPA enforcement:** Florida, Texas, Iowa, Missouri, Oregon

### 7.2 How ungouge.ai Avoids UPPA Violations

**Critical positioning: ungouge.ai is a MARKET RESEARCH and CONSUMER EDUCATION tool, NOT an insurance adjusting service.**

**Safe language:**
- ✅ "Compare your quote to typical market rates"
- ✅ "See how your quote compares to published cost data"
- ✅ "Market research tool for informed consumers"
- ✅ "Educational cost comparison"

**Dangerous language:**
- ❌ "We'll tell you if your contractor is overcharging"
- ❌ "Use our report to negotiate with your insurance company"
- ❌ "We'll help you settle your claim"
- ❌ "Our analysis proves you're being gouged"

### 7.3 Recommended Legal Safeguards

1. **Disclaimer on every report:** "This analysis is for educational and market research purposes only. It does not constitute professional adjusting, appraising, or legal advice. Cost data represents published national averages adjusted for location and should not be used as the sole basis for insurance claim decisions."

2. **Terms of Service:** Explicitly state the tool is not a substitute for licensed professional advice.

3. **No insurance claim features:** Don't build any feature that specifically targets insurance claims. If Insurance Ian uses the tool, that's his choice, but don't market to that use case.

4. **Consult a lawyer ($500-1,000):** Before launch, have an insurance regulatory attorney in your state review the product positioning and disclaimers. This is non-negotiable given the legal landscape.

---

## 8. Competitive Moat Analysis

### 8.1 Moat Components (Weakest to Strongest)

| Moat Type | Strength | Assessment |
|-----------|----------|------------|
| **Technology** | WEAK | Anyone can use Gemini + cost data. No proprietary AI. |
| **Data** | MEDIUM | Craftsman data is publicly available to licensees. But your prompt engineering, analysis templates, and trade-specific knowledge will compound. |
| **Brand/SEO** | STRONG (if executed) | First-mover in "is my contractor quote fair?" keyword space. pSEO with 25,000+ pages creates a defensible organic moat that takes competitors years to replicate. |
| **Network effects** | MEDIUM-LONG TERM | Every quote analyzed improves your understanding of real-world pricing patterns. Over time, your proprietary dataset of "what contractors actually charge vs. what's fair" becomes uniquely valuable. |
| **Switching costs** | WEAK | Per-use product, no lock-in. Must win on convenience + accuracy. |

### 8.2 The Real Moat: Programmatic SEO at Scale

The pSEO strategy is the single most important competitive advantage. Here's why:

**Target keyword structure:** "how much does [trade/project] cost in [city], [state]"

**Scale math:**
- 50 trades × 500 cities = **25,000 unique landing pages**
- Each page targets a long-tail keyword with high purchase intent
- Competitor would need to replicate this entire content infrastructure
- Google rewards comprehensive, location-specific content

**Examples of target pages:**
- "How much does a kitchen remodel cost in Austin, TX"
- "Average HVAC replacement cost in Denver, CO"
- "Roof replacement pricing in Miami, FL"
- "Bathroom renovation costs in Portland, OR"

Each page includes: local cost ranges from Craftsman data, typical line items, what to look for in a quote, and a CTA to "Upload your quote for instant analysis."

**This is how Homewyse built their traffic empire** — except ungouge.ai has a monetizable conversion action (quote analysis) that Homewyse doesn't.

---

## 9. Key Risks & Mitigations

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Craftsman API doesn't exist / no programmatic access** | HIGH | CRITICAL | Verify API availability immediately. Fallback: manually build cost database from published books + BLS data |
| **UPPA legal challenge** | LOW | HIGH | Proper disclaimers, legal review, position as market research |
| **GreatBuildz adds cost verification** | MEDIUM | HIGH | Move fast, build SEO moat before they iterate |
| **Low conversion from pSEO traffic** | MEDIUM | MEDIUM | A/B test CTAs, offer free "preview" analysis, build email funnel |
| **Gemini accuracy issues with OCR** | LOW | MEDIUM | Multi-pass verification, human review for concierge phase |
| **Homeowner doesn't trust AI analysis** | MEDIUM | MEDIUM | Show data sources, include Craftsman citations, build social proof |
| **Seasonality of home improvement** | CERTAIN | LOW | Revenue peaks spring/summer, plan cash reserves for winter |
| **Google algorithm change kills pSEO** | LOW-MEDIUM | HIGH | Diversify traffic: social, email, partnerships, paid ads |

### 🚨 Critical Pre-Build Validation Required

**#1 PRIORITY: Verify Craftsman data access method.**
The entire product depends on having programmatic access to location-adjusted cost data. The Craftsman National Estimator Cloud is $13.99/month and appears to be a web app, not an API. Options:
1. Contact Craftsman directly about API/data licensing
2. Use their web app as a manual lookup during concierge phase
3. Build your own cost database from: BLS wage data + material supplier APIs + published cost guides
4. Explore alternative data sources (RSMeans, HomeAdvisor cost data, BLS Occupational Employment Statistics)

---

## 10. Verdict: Go / No-Go Assessment

### ✅ STRONG GO — with caveats

**Bull case:**
- Genuine whitespace — no one is doing AI-powered quote analysis for homeowners
- Exceptional unit economics (95%+ gross margin)
- Low break-even (11 analyses/month)
- Massive TAM with clear path to $30k-$100k/year
- pSEO strategy creates defensible organic moat
- Concierge-first approach de-risks the build

**Bear case:**
- Unproven demand at scale (no one has proven homeowners will pay for this)
- Craftsman API access is unverified (critical dependency)
- Low switching costs / easy to replicate technically
- GreatBuildz is adjacent and well-funded

**The decisive factor:** The concierge phase (March 2026) will answer the demand question with minimal investment. If 20-50 homeowners pay $19.99 for manual quote analysis in Month 1, the automated product is a slam dunk.

### Recommended Immediate Actions (This Week)

1. **Contact Craftsman Book Company** about data licensing / API access
2. **Search for "is my contractor quote fair" on Google** — map every result on page 1-3. These are your SEO targets.
3. **Post in r/homeimprovement** asking "Would you pay $20 to have your contractor quote analyzed against fair market data?" — free demand validation
4. **Register the LLC** (Wyoming, as planned)
5. **Buy the domain** (ungouge.ai) if not already owned

---

## Appendix A: Top 50 Trades for pSEO

| # | Trade/Project | Search Volume Potential | Avg Project Cost |
|---|---------------|----------------------|------------------|
| 1 | Kitchen remodel | Very High | $15,000-$50,000 |
| 2 | Bathroom remodel | Very High | $10,000-$30,000 |
| 3 | Roof replacement | Very High | $8,000-$25,000 |
| 4 | HVAC replacement | Very High | $5,000-$15,000 |
| 5 | Window replacement | High | $8,000-$20,000 |
| 6 | Siding replacement | High | $8,000-$20,000 |
| 7 | Deck building/replacement | High | $5,000-$15,000 |
| 8 | Basement finishing | High | $20,000-$60,000 |
| 9 | Electrical panel upgrade | High | $1,500-$4,000 |
| 10 | Plumbing repipe | Medium-High | $4,000-$15,000 |
| 11 | Concrete/driveway | Medium-High | $3,000-$10,000 |
| 12 | Painting (exterior) | Medium-High | $3,000-$8,000 |
| 13 | Painting (interior) | Medium | $2,000-$6,000 |
| 14 | Flooring installation | High | $3,000-$12,000 |
| 15 | Fence installation | Medium-High | $2,000-$8,000 |
| 16 | Garage door replacement | Medium | $1,000-$4,000 |
| 17 | Water heater replacement | Medium-High | $1,000-$3,500 |
| 18 | Foundation repair | Medium | $5,000-$20,000 |
| 19 | Tree removal | Medium | $500-$3,000 |
| 20 | Landscaping | Medium | $3,000-$15,000 |
| 21 | Insulation | Medium | $1,500-$5,000 |
| 22 | Gutter installation | Medium | $1,000-$3,000 |
| 23 | Door replacement (entry) | Medium | $1,000-$4,000 |
| 24 | Septic system | Medium | $5,000-$15,000 |
| 25 | Swimming pool | Medium | $30,000-$80,000 |
| 26 | Home addition | Medium | $40,000-$100,000+ |
| 27 | Patio/paver installation | Medium | $3,000-$10,000 |
| 28 | Stucco repair/replacement | Medium | $3,000-$10,000 |
| 29 | Chimney repair | Medium | $1,000-$5,000 |
| 30 | Waterproofing (basement) | Medium | $3,000-$10,000 |
| 31 | Cabinet refacing | Medium | $5,000-$15,000 |
| 32 | Countertop replacement | Medium | $2,000-$8,000 |
| 33 | Shower/tub replacement | Medium | $2,000-$8,000 |
| 34 | Tile installation | Medium | $1,500-$5,000 |
| 35 | Drywall repair | Low-Medium | $500-$2,000 |
| 36 | Carpet installation | Medium | $1,500-$5,000 |
| 37 | Solar panel installation | Medium-High | $15,000-$30,000 |
| 38 | EV charger installation | Growing | $1,000-$3,000 |
| 39 | Asbestos removal | Low-Medium | $1,500-$10,000 |
| 40 | Mold remediation | Medium | $1,500-$10,000 |
| 41 | Termite treatment | Medium | $500-$3,000 |
| 42 | Fire damage restoration | Low-Medium | $5,000-$50,000+ |
| 43 | Water damage restoration | Medium | $2,000-$10,000 |
| 44 | Appliance installation | Low-Medium | $500-$2,000 |
| 45 | Retaining wall | Medium | $3,000-$10,000 |
| 46 | French drain | Low-Medium | $2,000-$6,000 |
| 47 | Sump pump | Low-Medium | $1,000-$3,000 |
| 48 | Well drilling/repair | Low | $3,000-$15,000 |
| 49 | Generator installation | Growing | $3,000-$10,000 |
| 50 | Smart home wiring | Growing | $1,500-$5,000 |

## Appendix B: Top 100 Cities for pSEO (by population + home improvement spending)

**Tier 1 — Must-have (top 30 metros):**
New York, Los Angeles, Chicago, Houston, Phoenix, Philadelphia, San Antonio, San Diego, Dallas, Austin, Jacksonville, San Jose, Fort Worth, Columbus, Charlotte, Indianapolis, San Francisco, Seattle, Denver, Nashville, Washington DC, Oklahoma City, El Paso, Las Vegas, Memphis, Louisville, Baltimore, Milwaukee, Albuquerque, Tucson

**Tier 2 — High value (next 30):**
Fresno, Sacramento, Mesa, Kansas City, Atlanta, Omaha, Colorado Springs, Raleigh, Long Beach, Virginia Beach, Miami, Oakland, Minneapolis, Tampa, Tulsa, Arlington, New Orleans, Wichita, Cleveland, Bakersfield, Aurora, Anaheim, Honolulu, Santa Ana, Riverside, Corpus Christi, Lexington, Stockton, St. Louis, Pittsburgh

**Tier 3 — Long tail (next 40):**
Cincinnati, Anchorage, Greensboro, Plano, Newark, Lincoln, Orlando, Irvine, Toledo, Durham, Chula Vista, Fort Wayne, St. Petersburg, Laredo, Norfolk, Madison, Chandler, Lubbock, Scottsdale, Reno, Glendale, Gilbert, Winston-Salem, North Las Vegas, Irving, Chesapeake, Boise, Richmond, Spokane, Baton Rouge, Des Moines, Tacoma, Hialeah, San Bernardino, Modesto, Fontana, Moreno Valley, Fayetteville, Salt Lake City, Huntsville

**Total: 100 cities × 50 trades = 5,000 high-priority pages**
**Expand to 500 cities × 50 trades = 25,000 pages in Phase 2**

---

*End of Phase 1: Market Viability Analysis*
*Next: Phase 2 — Division of Labor Document*
*Next: Phase 3 — Enhanced Business Plan with Financial Models*
*Next: Phase 4 — Implementation Playbook*
