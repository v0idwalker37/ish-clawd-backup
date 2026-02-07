# 1build.com API Research - Game-Changer for Ungouge

**Date:** 2026-02-07  
**Researcher:** Ish  
**Priority:** HIGH - This could transform Ungouge's cost data strategy  

---

## TL;DR

**1build.com** is a Y Combinator startup that provides the ONLY live construction cost API in the market. It's basically "Plaid for construction costs" — exactly what Ungouge needs to deliver accurate, real-time quote analysis.

**Why it matters:**
- **68 million live data points** across materials, labor, and equipment
- **3,000+ US counties** covered (local/regional pricing, not just national averages)
- **Daily updates** from Home Depot, Lowe's, + regional LBM suppliers
- **GraphQL API** (modern, flexible, only fetch what you need)
- **Pre-built assemblies** (e.g., "Kitchen Remodel Package", "Roof Replacement")
- **Covers all trades** our cost models address (roof, kitchen, HVAC, bathroom, etc.)

**Bottom line:** Instead of manually maintaining 14 cost models with static data, we could query live, county-specific pricing via API.

---

## What is 1build?

**Company:**
- Y Combinator backed (credible, well-funded)
- Founded to solve construction cost data fragmentation
- "Plaid for construction cost data" positioning
- Integrations with major estimating software (Buildxact, Procore ecosystem)

**Product:**
- API-first platform (developer-focused)
- GraphQL interface (modern, efficient queries)
- Coverage: Materials, Labor, Equipment, Assemblies, Scopes
- Geographic: Every US county (3,000+)
- Update frequency: Daily (from retailers + suppliers)

**Website:** https://www.1build.com  
**API Docs:** https://developer.1build.com/1build-api-reference/  
**Contact:** help@1build.com  

---

## Technical Details

### API Architecture

**Type:** GraphQL  
**Endpoint:** https://gateway-external.1build.com/  
**Authentication:** API key in header (`1build-api-key`)  

**Key Types:**
- **EXTERNAL** - Backend integrations (private, no referrer restrictions)
- **EMBEDDED** - Client-side integrations (requires domain whitelist)

### Core Data Types

#### 1. **Source**
The fundamental data unit. Represents:

| Source Type | Description | Example |
|-------------|-------------|---------|
| **MATERIAL** | Physical construction material | "5/8\" 4X8' Type-X Drywall" |
| **EQUIPMENT** | Tools/machines (typically rental) | "15-17' Electric Scissor Lift (Daily Rental)" |
| **ASSEMBLY** | Composed of multiple nested sources | "Flooring: Sheet Carpet" (includes carpet + padding + labor) |
| **LABOR** | Professional rates per unit time | "Tile and Stone Setter" ($45.67/hr) |
| **SCOPE** | Work scope billed to contractor | "Testing - Soil" |
| **GENERAL_CONDITIONS** | Project overhead/general conditions | Site supervision, insurance, permits |

**Source Fields (partial list):**
- `id` - Unique identifier
- `name` - Item name (e.g., "2X4 12' Douglas Fir #2")
- `description` - Detailed product description
- `materialRateUsdCents` - Material cost per unit (in cents)
- `laborRateUsdCents` - Labor cost per hour (in cents)
- `burdenedLaborRateUsdCents` - Labor + overhead (workers comp, insurance, taxes)
- `productionRate` - Units installable per hour (e.g., 100 SF/hr)
- `calculatedUnitRateUsdCents` - Total cost per unit: `Material + (Labor / ProductionRate)`
- `uom` - Unit of measure (LF, SF, EA, GAL, etc.)
- `knownUoms` - Alternative UOMs with recalculated rates
- `nestedSources` - For assemblies, the component materials/labor
- `imagesUrls` - Product images
- `externalProductUrl` - Link to retailer product page
- `stockQuantity` - Availability at local store
- `csiDivision`, `csiSection`, `csiTitle` - CSI MasterFormat classification
- `nahbDivision`, `nahbCode` - NAHB cost codes
- `categoryPath` - Hierarchical category (e.g., ["Interiors", "Drywall", "Type X"])
- `state`, `county` - Location for pricing

#### 2. **CategoryTreeItem**
Hierarchical organization of all sources. Allows browsing by trade/division.

**Fields:**
- `id` - Category path (e.g., "Plumbing, Rough-In > ABS Pipe")
- `name` - Category name
- `hasSubCategories` - Boolean (true if drill-down possible)

**Example Categories:**
- Roofing > Asphalt Shingles > Architectural
- Plumbing > Fixtures > Toilets
- HVAC > Furnaces > Gas > 90%+ AFUE
- Flooring > Tile > Ceramic > 12x12

---

## Key API Queries

### 1. `sources` - Search for cost data

**Input:**
```graphql
{
  state: "Vermont",
  county: "Washington County",
  searchTerm: "asphalt shingle architectural",
  categoryPath: ["Roofing", "Shingles"],
  page: { limit: 10, offset: 0 },
  sortBy: { type: "RATE" },  // or "MATCH_SCORE", "NAME"
  filter: {
    rateUsdCentsGte: 10000,  // Min price filter
    rateUsdCentsLte: 50000,  // Max price filter
    supplier: "Home Depot"    // Filter by supplier
  }
}
```

**Returns:**
- Paginated list of matching sources
- Each source includes material + labor + calculated total
- Sorted by relevance, name, or rate
- `dataLocation` confirms county used for pricing

**Cost:** Billed per Source object returned (exact pricing unknown, must contact 1build)

### 2. `categoryTreeItems` - Browse categories

**Input:**
```graphql
{
  state: "Vermont",
  county: "Washington County",
  searchTerm: "roofing",  // Optional
  categoryPath: ["Exteriors"],  // Drill into subcategory
  page: { limit: 20 }
}
```

**Returns:**
- List of categories/subcategories
- Indicates if further drill-down available
- Helps users navigate to specific items

**Cost:** FREE (no billing for category browsing)

### 3. `sourcesBatch` - Bulk retrieval by ID

**Input:**
```graphql
{
  items: [
    { sourceId: "abc-123" },
    { sourceId: "def-456" }
  ],
  state: "Vermont",
  county: "Washington County"
}
```

**Returns:**
- Up to 1,000 sources in one request
- Useful for refreshing saved estimates
- Priced per source

### 4. `sourcesCounts` - Get result counts by supplier

**Input:** Same as `sources`  
**Returns:** Total count + breakdown by supplier (Home Depot, Lowe's, local LBM)

### 5. `uoms` - List all units of measure

**Returns:** All supported UOMs with descriptions
- LF (Linear Feet)
- SF (Square Feet)
- EA (Each)
- GAL (Gallon)
- CY (Cubic Yard)
- etc.

---

## Example Use Cases for Ungouge

### 1. **Roof Replacement Quote Verification**

**Scenario:** User uploads quote for "2,000 SF asphalt shingle roof in Northfield, Vermont"

**API Query:**
```graphql
query {
  sources(input: {
    state: "Vermont",
    county: "Washington County",
    searchTerm: "architectural asphalt shingle",
    categoryPath: ["Roofing", "Shingles"],
    page: { limit: 5 }
  }) {
    nodes {
      name
      materialRateUsdCents
      laborRateUsdCents
      productionRate
      calculatedUnitRateUsdCents
      uom
    }
    dataLocation {
      countyName
      stateName
    }
  }
}
```

**Response (example):**
```json
{
  "nodes": [
    {
      "name": "Architectural Asphalt Shingle - 30 Year Warranty",
      "materialRateUsdCents": 165,  // $1.65/SF
      "laborRateUsdCents": 4567,    // $45.67/hr
      "productionRate": 25,          // 25 SF/hr
      "calculatedUnitRateUsdCents": 348,  // $3.48/SF total
      "uom": "SF"
    },
    ...
  ],
  "dataLocation": {
    "countyName": "Washington County",
    "stateName": "Vermont"
  }
}
```

**Ungouge Analysis:**
- User's quote: $8,500 for 2,000 SF = $4.25/SF
- 1build data: $3.48/SF (fair market)
- **Verdict:** Quote is 22% higher than market rate
- **Breakdown:** Material ($1.65/SF) + Labor ($1.83/SF) = $3.48/SF

---

### 2. **Kitchen Remodel - Cabinet Pricing**

**API Query:**
```graphql
query {
  sources(input: {
    state: "Vermont",
    county: "Washington County",
    searchTerm: "semi-custom kitchen cabinet",
    categoryPath: ["Interiors", "Cabinetry"],
    page: { limit: 10 }
  }) {
    nodes {
      name
      materialRateUsdCents
      laborRateUsdCents
      calculatedUnitRateUsdCents
      uom
      description
    }
  }
}
```

**Returns:** Semi-custom cabinets by linear foot, with installation labor included.

---

### 3. **HVAC Replacement - Furnace Pricing**

**API Query:**
```graphql
query {
  sources(input: {
    state: "Vermont",
    county: "Washington County",
    searchTerm: "gas furnace 90% AFUE 80,000 BTU",
    categoryPath: ["HVAC", "Heating", "Furnaces"],
    sourceType: MATERIAL,
    page: { limit: 5 }
  }) {
    nodes {
      name
      materialRateUsdCents  // Equipment cost
      laborRateUsdCents     // Install labor
      calculatedUnitRateUsdCents
      uom
      description
      imagesUrls
      externalProductUrl
    }
  }
}
```

**Plus:** Query for labor separately
```graphql
query {
  sources(input: {
    state: "Vermont",
    county: "Washington County",
    searchTerm: "HVAC technician installer",
    sourceType: LABOR
  }) {
    nodes {
      name
      laborRateUsdCents  // e.g., $7,500/hr burdened
      burdenedLaborRateUsdCents  // Includes overhead
    }
  }
}
```

---

### 4. **Assembly-Based Estimation**

**Scenario:** User wants cost for "standard bathroom remodel"

**API Query:**
```graphql
query {
  sources(input: {
    state: "Vermont",
    county: "Washington County",
    searchTerm: "bathroom remodel",
    sourceType: ASSEMBLY,
    page: { limit: 5 }
  }) {
    nodes {
      name
      calculatedUnitRateUsdCents
      uom
      nestedSources {  // Show component breakdown
        name
        quantity
        materialRateUsdCents
        laborRateUsdCents
      }
    }
  }
}
```

**Returns:** Pre-built assemblies like:
- "5' x 8' Bathroom Remodel - Standard"
- Breakdown: Toilet, vanity, tub/shower, tile, fixtures, labor
- Total per SF or per EA

---

## Pricing & Business Model

**Pricing Model:** NOT publicly listed (standard for B2B APIs)

**Billing Structure (inferred from docs):**
- **FREE:** Category browsing (`categoryTreeItems`)
- **PAID:** Source object retrieval (`sources`, `sourcesBatch`)
- Likely tiered:
  - Startup tier: X,XXX API calls/month
  - Growth tier: XX,XXX calls/month
  - Enterprise: Custom

**To get pricing:**
- Contact: help@1build.com
- Request developer API key + pricing details
- Mention use case: "Quote verification tool for homeowners"

**Comparable Pricing (estimates):**
- RSMeans Data Online: $2,000-$5,000/year (static data, manual lookup)
- Xactimate: $400-$1,200/month (insurance/restoration focused)
- 1build: Likely $500-$2,000/month for API access (pure speculation)

**ROI for Ungouge:**
- If API costs $1,000/month
- Break-even: 50 quote analyses/month at $19.99 each
- Benefit: Live, local data vs. manual maintenance of 14 cost models

---

## Integration Strategy for Ungouge

### Option 1: **Direct API Integration** (Recommended for MVP)

**Workflow:**
1. User uploads quote with location (ZIP code or city/state)
2. Ungouge extracts line items (Gemini OCR)
3. For each line item:
   - Query 1build API with `searchTerm` + location
   - Retrieve top 3-5 matching sources
   - Use fuzzy matching to select best match
   - Compare quoted price vs. 1build `calculatedUnitRateUsdCents`
4. Generate report showing:
   - Line item: "Architectural Asphalt Shingles"
   - Quoted price: $4.25/SF
   - Market rate (1build): $3.48/SF
   - Variance: +22% (OVERPRICED)
   - Source: 1build (Washington County, VT - Feb 7, 2026)

**Pros:**
- Always up-to-date pricing
- Minimal maintenance (no manual cost model updates)
- County-level accuracy (better than our current models)
- Material + labor separation (more transparent)

**Cons:**
- API cost per quote analysis
- Requires active internet connection
- Dependent on 1build uptime

---

### Option 2: **Hybrid Approach** (Cost-Optimized)

**Workflow:**
1. Cache common items (e.g., "asphalt shingles", "2x4 lumber") locally
2. Refresh cache weekly via batch API calls
3. For uncommon items, query API in real-time
4. Fall back to our manual cost models if API unavailable

**Pros:**
- Reduced API call volume (lower cost)
- Faster response time (cached lookups)
- Resilient to API downtime

**Cons:**
- More complex implementation
- Cache invalidation logic needed
- Hybrid data sources (consistency challenge)

---

### Option 3: **1build as Data Source for Cost Models** (Long-Term)

**Workflow:**
1. Use 1build API to BUILD our 14 cost models
2. Query API monthly to update our static data
3. Serve quote analysis from our own database
4. Attribute data source: "Cost data powered by 1build"

**Pros:**
- Predictable API costs (monthly batch refresh)
- Fast quote analysis (no real-time API dependency)
- Full control over data structure

**Cons:**
- Data freshness lag (monthly vs. daily)
- Still requires API access
- More storage/DB management

---

## Competitive Advantage

**Current Ungouge Strategy:**
- 14 manually maintained cost models
- Mix of BLS data, Home Depot pricing, crew hour estimates
- National/regional averages (not county-specific)
- Static data (requires manual updates)

**With 1build Integration:**
- **68 million live data points** (vs. our ~100-200 manual entries)
- **County-specific pricing** (e.g., Washington County, VT vs. Los Angeles, CA)
- **Daily updates** (vs. our quarterly manual refreshes)
- **Material + labor + equipment** (vs. our estimated labor rates)
- **Pre-built assemblies** (vs. our manual assembly calculations)
- **Supplier-specific data** (Home Depot vs. Lowe's vs. local LBM)

**Positioning:**
- "Ungouge uses live, local construction cost data to analyze your quote"
- "Powered by 1build - 68 million data points across 3,000+ US counties"
- Instant credibility vs. competitors (BidCompareAI, etc.)

---

## Potential Concerns

### 1. **API Cost**
- **Risk:** If 1build charges per API call, costs could scale with user growth
- **Mitigation:** Caching, hybrid approach, batch queries

### 2. **Vendor Lock-In**
- **Risk:** Dependent on 1build for core data
- **Mitigation:** Build our own cost models in parallel, use 1build as enhancement

### 3. **Data Accuracy**
- **Risk:** 1build data might not match every contractor's actual pricing
- **Mitigation:** Present as "market average" not "guaranteed fair price"

### 4. **Coverage Gaps**
- **Risk:** Some niche items may not be in 1build database
- **Mitigation:** Fall back to our manual cost models for gaps

---

## Next Steps

### Immediate (This Week)
1. **Contact 1build** (help@1build.com)
   - Request API key for testing
   - Get pricing details
   - Ask about trial/developer tier

2. **Run Test Queries**
   - Query Vermont counties for common items (shingles, cabinets, HVAC)
   - Compare 1build data to our manual cost models
   - Assess coverage quality

3. **Evaluate Pricing**
   - Calculate API cost per quote analysis
   - Model break-even scenarios
   - Decide: Direct integration vs. hybrid vs. data source

### Short-Term (Next 2-4 Weeks)
4. **Prototype Integration**
   - Build proof-of-concept: Upload quote → 1build API → analysis report
   - Test with 10-20 real contractor quotes
   - Measure accuracy vs. current cost models

5. **Decision Point**
   - If API cost is reasonable: Build production integration
   - If too expensive: Use as data source to improve our models
   - If coverage gaps: Hybrid approach (1build + manual models)

### Long-Term (Post-Launch)
6. **Attribution & Partnership**
   - If we use 1build extensively, explore partnership/referral deal
   - "Powered by 1build" branding (with their permission)
   - Potentially negotiate volume pricing

---

## Resources

- **Website:** https://www.1build.com
- **Developer Docs:** https://developer.1build.com/1build-api-reference/
- **GraphQL Playground:** (likely available after API key issued)
- **Support:** help@1build.com
- **YC Launch Post:** https://www.ycombinator.com/launches/IQo-1build-plaid-for-construction-cost-data

---

## Conclusion

**1build API is a potential game-changer for Ungouge.**

Instead of manually maintaining static cost models, we could query live, county-specific construction cost data via API. This would:
- Increase accuracy (68M data points vs. our ~200)
- Reduce maintenance burden (daily updates vs. manual quarterly refreshes)
- Improve credibility ("Powered by 1build" vs. "our estimates")
- Enable county-level precision (Northfield, VT vs. national average)

**Recommendation:** Contact 1build ASAP to get API key + pricing. Run tests with real Vermont quotes. If pricing is reasonable ($500-$1,500/month), integrate directly into Ungouge backend. If too expensive, use as data source to improve our manual cost models.

**Priority:** HIGH - This could differentiate Ungouge from all competitors.

---

**Researched by:** Ish  
**Date:** 2026-02-07 (Autonomous Session #2)
