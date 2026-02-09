# Construction Cost Data API Research
**Date:** February 9, 2026  
**Purpose:** Evaluate alternatives to Craftsman API for Ungouge.ai cost modeling

---

## Current State: Craftsman API

**What we have:**
- Sandbox credentials (username: ungouge, password: ungouge2026)
- API endpoint: `https://nec-api-sandbox.craftsman-book.com`
- API key: `20bac80e-121d-4965-a0c9-30a833b98f77`

**Strengths:**
- We have working access (sandbox)
- Data is comprehensive for basic cost modeling
- Familiar format (likely REST API)

**Weaknesses:**
- Unknown production pricing
- Unknown data freshness (static vs live)
- Limited county-level granularity (likely regional)
- Unknown API rate limits
- Sandbox-only access (production unclear)

**Action needed:** Verify sandbox vs production status, get pricing quote

---

## Alternative: 1build.com API

### Overview
- **Company:** Y Combinator-backed (launched 2023)
- **Positioning:** "Plaid for construction cost data"
- **Website:** https://www.1build.com / https://developer.1build.com
- **Status:** Production-ready, actively used by Buildxact and other major platforms

### Data Coverage
- **68 million live construction costs**
- **3,000+ US counties** (county-specific, not regional)
- **25,000+ unique items and assemblies**
- **All CSI divisions** (comprehensive trade coverage)
- **Real-time pricing** from big-box retailers + local LBM suppliers

### Data Types Supported
1. **MATERIAL** - Physical construction materials (e.g., "5/8" 4X8' Type-X Drywall")
2. **EQUIPMENT** - Tools/machines, typically rentals (e.g., "15-17' Electric Scissor Lift")
3. **ASSEMBLY** - Pre-built combinations (e.g., "Flooring: Sheet Carpet" with nested materials)
4. **LABOR** - Professional labor rates (e.g., "Tile and Stone Setter")
5. **SCOPE** - Scopes of work (e.g., "Testing - Soil")

### Technical Architecture
- **API type:** GraphQL (modern, flexible)
- **Endpoint:** `https://gateway-external.1build.com/`
- **Authentication:** API key in header (`1build-api-key`)
- **Key types:**
  - EXTERNAL (backend integrations, must be kept secret)
  - EMBEDDED (client-side, requires referrer whitelist)

### Data Granularity
- **Location:** County-level (can query by state/county, zipcode, or GPS coordinates)
- **Costs returned:**
  - `materialRateUsdCents` - Material cost per unit
  - `laborRateUsdCents` - Labor cost (per hour for most, per unit for assemblies)
  - `burdenedLaborRateUsdCents` - Labor + insurance/workers comp/benefits
  - `productionRate` - Units installable per hour
  - `calculatedUnitRateUsdCents` - Total unit cost (material + labor/production)
- **Multiple UOMs:** Each source can have different unit rates (e.g., LF, SF, EA)

### Example API Response
```json
{
  "id": "8514f9ba-23e6-41c0-914e-a47cb233320c",
  "name": "1-Stage and Whole House Water Filtration System",
  "calculatedUnitRateUsdCents": 31502,  // $315.02
  "laborRateUsdCents": 2856,             // $28.56/hour
  "materialRateUsdCents": 31025,         // $310.25
  "sourceType": "MATERIAL",
  "uom": "EA",
  "state": "California",
  "county": "Los Angeles County",
  "imagesUrls": ["https://..."],
  "description": "...",
  "externalProductUrl": "https://homedepot.com/..."
}
```

### Key Features
1. **Product images** - Visual reference for homeowners
2. **External URLs** - Link to supplier product pages
3. **Stock quantity** - Real-time inventory (where available)
4. **Category browsing** - Hierarchical navigation (no billing for category queries)
5. **Search + filter** - Full-text search, price range filters, supplier filters
6. **CSI coding** - Industry-standard CSI division/section/title
7. **NAHB coding** - Residential construction codes

### Pricing Model
- **Billing unit:** Per Source or NestedSource object returned
- **Free queries:** `categoryTreeItems` (browse categories without billing)
- **Unknown:** Cost per API call (need to contact sales)
- **Inquiry sent:** Feb 7, 2026 to sales team

### API Usage Pattern (Recommended by 1build)
1. User enters search term (e.g., "drywall")
2. Search all sources: `sources(searchTerm: "drywall")` → top results
3. Simultaneously query categories: `categoryTreeItems(searchTerm: "drywall")` → matching categories
4. User narrows by category → drill down with categoryPath
5. User selects specific source → full details + nested sources (for assemblies)

### Integration Complexity
- **GraphQL client required** (more complex than REST)
- **Schema is well-documented** (auto-generated docs)
- **Example queries provided** (good developer experience)
- **No rate limit info in docs** (need to verify with sales)

---

## Alternative: RSMeans Data (Gordian)

### Overview
- **Company:** Gordian (established, industry standard)
- **Website:** https://www.gordian.com/products/rsmeans-data-services/
- **Reputation:** Gold standard for construction cost data (used by architects, engineers, contractors)

### Strengths
- Most trusted name in construction cost data
- Decades of historical data
- Comprehensive coverage
- Detailed cost breakdowns

### Weaknesses
- **Expensive** - Typically $1,000s/year for data access
- **Static data** - Updated quarterly or annually, not real-time
- **API unclear** - RSMeans offers "Data Online" but API access is gated
- **Enterprise-focused** - Not designed for consumer-facing apps like Ungouge

### Verdict for Ungouge
❌ **Not suitable** - Too expensive, too enterprise-focused, not real-time

---

## Comparison Matrix

| Feature | Craftsman API | 1build.com | RSMeans |
|---------|---------------|------------|---------|
| **Data points** | Unknown | 68M | Very high |
| **Granularity** | Regional? | County-level | Regional |
| **Freshness** | Unknown | Real-time | Quarterly/Annual |
| **API type** | REST? | GraphQL | Unknown |
| **Pricing** | Unknown | Unknown (inquiry sent) | $1,000s/year |
| **Images** | Unknown | Yes | Limited |
| **Supplier links** | Unknown | Yes | No |
| **Assembly support** | Unknown | Yes (nested sources) | Yes |
| **County coverage** | Unknown | 3,000+ US counties | National |
| **Production ready** | Unknown (sandbox only) | Yes | Yes |
| **Developer UX** | Unknown | Excellent docs | Poor |

---

## Recommendation for Jason

### Short-term (Pre-launch)
1. ✅ **Verify Craftsman API status**
   - Is sandbox data sufficient for MVP?
   - What's the production pricing?
   - What's the data coverage (regional vs county)?
   - Are there rate limits?

2. ⏳ **Wait for 1build response**
   - Sent inquiry Feb 7, 2026
   - If pricing is reasonable ($100-500/month?), strongly consider

### Long-term (Post-launch)

**If 1build pricing is competitive:**
- ✅ Switch to 1build for better data quality
- ✅ Real-time pricing = more accurate quotes
- ✅ County-level = better regional adjustments
- ✅ Product images = better UX for homeowners
- ✅ Supplier links = transparency (aligns with Ungouge brand)

**If 1build is too expensive:**
- Continue with Craftsman API (if production access is reasonable)
- Build own cost database over time from submitted quotes (long-term play)

### Questions for 1build Sales Call
1. What's the pricing model? (Per API call? Monthly flat rate? Tiered?)
2. What are the rate limits?
3. Is there a startup/small business tier?
4. Can we get a free trial or pilot program?
5. What's the typical use case pricing? (e.g., 1,000 quote analyses/month)
6. Do you offer volume discounts?
7. What's included in "burdened labor rate" calculations?
8. How often is pricing data updated? (daily? weekly?)
9. What's the SLA for API uptime?
10. Are there any restrictions on consumer-facing use cases?

---

## Technical Integration Notes (1build)

### GraphQL Query Example (Window Replacement)
```graphql
query searchWindows($input: SourceSearchInput!) {
  sources(input: $input) {
    nodes {
      id
      name
      sourceType
      uom
      materialRateUsdCents
      laborRateUsdCents
      burdenedLaborRateUsdCents
      productionRate
      calculatedUnitRateUsdCents
      description
      imagesUrls
      externalProductUrl
      state
      county
      csiDivision
      csiSection
    }
    totalCount
    dataLocation {
      countyName
      stateName
    }
  }
}

# Variables:
{
  "input": {
    "state": "Vermont",
    "county": "Washington County",
    "searchTerm": "vinyl double hung window",
    "sourceType": "MATERIAL",
    "page": {
      "limit": 10,
      "offset": 0
    }
  }
}
```

### Integration Pattern for Ungouge
1. User uploads quote with project type "window replacement"
2. Backend extracts window specs (size, type, quantity)
3. GraphQL query to 1build: search for matching windows in user's county
4. Get `calculatedUnitRateUsdCents` for comparison
5. Apply Ungouge's markup analysis (contractor cost vs fair retail)
6. Show user: "Fair price for this window: $450-650. Quote shows: $950. **31% overcharge**"

### Cost Model Enhancement
- Current: Static CSV data, regional multipliers
- With 1build: Dynamic county-level data, supplier-specific pricing
- Benefit: More accurate, always current, less maintenance

---

## Next Steps

- [x] Research 1build.com API (completed Feb 9)
- [ ] Wait for 1build sales response (inquiry sent Feb 7)
- [ ] Verify Craftsman API production status and pricing
- [ ] Schedule comparison call with Jason
- [ ] Prototype 1build integration (if pricing is reasonable)
- [ ] Cost-benefit analysis: API cost vs improved accuracy/UX

---

*Research compiled by Ish, Feb 9, 2026, 1:50 AM*
