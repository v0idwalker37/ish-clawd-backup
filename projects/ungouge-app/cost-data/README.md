# Construction Cost Data Collection

**Scraped:** February 11, 2026  
**Purpose:** Market data for Ungouge.ai quote analysis engine

## Files

### 1. `bls-labor-rates.json` (15 KB)
**Source:** Bureau of Labor Statistics — Occupational Employment and Wage Statistics (OEWS)  
**Quality:** ⭐⭐⭐⭐⭐ (Government data, comprehensive, reliable)

Contains:
- **4 detailed trade profiles** with national, state, metro, and industry data:
  - Carpenters (47-2031): Median $27.09/hr, Mean $29.31/hr
  - Electricians (47-2111): Median $29.61/hr, Mean $32.60/hr
  - Plumbers/Pipefitters (47-2152): Median $29.59/hr, Mean $32.62/hr
  - Roofers (47-2181): Median $24.05/hr, Mean $26.85/hr
- **May 2024 national summary** for 20+ construction trades (from Table 1)
- Wage percentiles (10th through 90th)
- State-level data (top 5 by employment, concentration, pay)
- Metro area breakdowns (top 10 by employment, concentration, pay)
- Industry sector breakdowns
- **Vermont-specific data** (carpenters: highest concentration in US, LQ 2.32)

**Ungouge use:** Core labor rate benchmarks for quote validation

---

### 2. `census-construction-data.json` (2 KB)
**Source:** U.S. Census Bureau — Value of Construction Put in Place (C30)  
**Quality:** ⭐⭐⭐⭐ (Government data, macro-level)

Contains:
- October 2025 construction spending (SAAR): $2.175 trillion total
- Private residential: $913.9 billion annual rate
- Public construction: $524.0 billion
- Year-over-year and month-over-month trends
- Market size context for Ungouge's addressable market

**Ungouge use:** Market sizing, trend analysis

---

### 3. `homeadvisor-cost-guides.json` (11 KB)
**Source:** HomeAdvisor/Angi Cost Guides  
**Quality:** ⭐⭐⭐ (Industry data, self-reported, lead-gen platform)

Contains cost ranges for **14 project categories**:
| Category | Average Cost | Range |
|----------|-------------|-------|
| Roofing | Varies by material | $100-$1,800/square |
| Deck Building | $8,265 | $4,340-$12,602 |
| Kitchen Remodel | $26,956 | $14,582-$41,534 |
| Bathroom Remodel | $12,125 | $6,639-$17,621 |
| Flooring | $3,156 | $200-$12,000 |
| Painting | $2-$6/sqft | $400-$4,200/project |
| Siding | $10,750 | $5,400-$16,000 |
| Windows | $850/window | $300-$2,100/window |
| HVAC | $7,500 | $5,000-$12,500 |
| Electrical | $1,563 (wiring) | $603-$2,592 |
| Fencing | $10-$20/lin ft (wood) | $1-$45/lin ft |
| Gutters | $1,179 | $627-$1,731 |
| Concrete | $6,400 (driveway) | $2,700-$14,500 |
| Plumbing | Varies | $45-$200/hr |

Each category includes material breakdowns, size-based estimates, and regional variations.

**Caveats:** HomeAdvisor is a lead-gen platform (competitor). Data is self-reported and may skew high to justify referral fees.

**Ungouge use:** Consumer-facing cost ranges, competitor pricing baseline

---

### 4. `remodeling-cost-vs-value.json` (6 KB)
**Source:** Remodeling Magazine / Zonda / JLC — 2025 Cost vs. Value Report  
**Quality:** ⭐⭐⭐⭐⭐ (Industry gold standard, 38th annual edition, 119 US markets)

Contains:
- **Top 10 projects by ROI** with actual costs and resale values
- ROI ranges from 84.7% to 267.7%
- Regional ROI variations (Northeast, Midwest, South, West)
- 28 total project categories including new 2025 additions (generators, ADUs, solar, basement)
- Key insight: **Exterior projects consistently outperform interior** for ROI

Top 3 by ROI:
1. Garage Door Replacement: 267.7% ROI ($4,672 cost → $12,507 resale)
2. Steel Entry Door: 216.4% ROI ($2,435 cost → $5,270 resale)
3. Manufactured Stone Veneer: 207.9% ROI ($11,702 cost → $24,328 resale)

**Caveat:** Primary source (remodeling.hw.net) blocked by Cloudflare. Data from secondary sources.

**Ungouge use:** Quote context ("is this price reasonable?"), ROI data for customer reports

---

### 5. `prevailing-wage-rates.json` (7 KB)
**Source:** Compiled from eBacon, DOL Davis-Bacon, state licensing boards  
**Quality:** ⭐⭐⭐ (Representative estimates, not official rate tables)

Contains:
- Representative prevailing wage rates for **8 major states** (CA, NY, TX, FL, IL, PA, OH, WA)
- Rates for 4-5 trades per state (carpenter, electrician, plumber, roofer, laborer)
- Total compensation packages (hourly + fringe benefits)
- List of states with/without prevailing wage laws
- Key insight: Private residential rates are typically **20-40% lower** than prevailing wages

**Caveats:** 
- State prevailing wage portals are interactive databases (not easily scraped)
- TX and FL have NO state prevailing wage laws
- Rates are approximate/representative — actual rates vary by county

**Ungouge use:** Upper-bound labor rate reference, understanding union vs non-union markets

---

## Data Quality Summary

| Source | Reliability | Coverage | Freshness | Usefulness for Ungouge |
|--------|-----------|----------|-----------|----------------------|
| BLS OEWS | Excellent | National+State+Metro | May 2023/2024 | ⭐⭐⭐⭐⭐ Core labor rates |
| Census C30 | Excellent | National | Oct 2025 | ⭐⭐⭐ Market sizing |
| HomeAdvisor | Good | 14 categories | 2025-2026 | ⭐⭐⭐⭐ Consumer cost ranges |
| Cost vs Value | Excellent | 28 projects, 119 markets | 2025 | ⭐⭐⭐⭐⭐ ROI context |
| Prevailing Wage | Fair | 8 states | 2024-2025 | ⭐⭐⭐ Rate ceiling reference |

## Sources That Were Blocked

- **JCHS Harvard** (jchs.harvard.edu) — Cloudflare 403. Contains homeowner improvement spending by project type.
- **Remodeling Magazine** (remodeling.hw.net) — Cloudflare 403. Primary Cost vs Value source.
- **JLC** (jlconline.com) — Cloudflare 403. Alternative Cost vs Value host.
- **BLS current year pages** (oes/current/) — Redirected to generic tables page. Used 2023/may/ URLs instead.

## Recommended Next Steps

1. **1build.com API** — Already contacted (Feb 7). 68M data points, 3,000+ counties. Would be best real-time source.
2. **RS Means / Gordian** — Industry standard cost database. Subscription required ($$$).
3. **Craftsman Cost Data** — Already integrated in Ungouge cost models.
4. **Home Depot/Lowe's pricing** — Could scrape material prices for common items.
5. **Contractor licensing databases** — State-by-state for license verification features.

## Rate Limiting Notes

All scraping was done with:
- 10-20 second delays between page fetches
- Respectful of robots.txt
- No automation headers
- Single-threaded requests
