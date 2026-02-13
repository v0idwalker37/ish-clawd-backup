# Cost Model Validation Report

**Date:** 2026-02-13  
**Validator:** Automated deep-dive analysis  
**Scope:** All 34 project types, regional multipliers, RSMeans integration, analyzer logic

---

## Executive Summary

The UnGouge.ai cost model has **solid underlying data** — 34 project types with RSMeans-calibrated pricing, BLS labor rates, HomeAdvisor benchmarks, and real quote data for 29 categories. However, there is a **critical bug** that renders regional pricing completely non-functional, and the RSMeans calibration data (stored in `rsmeans_benchmarks`) is **not being consumed** by the analyzer engine — it sits alongside the model data as reference only.

### Overall Assessment: 🟡 Good Foundation, Critical Bugs

| Area | Status | Notes |
|------|--------|-------|
| Cost data quality | ✅ Good | Real RSMeans, BLS, HomeAdvisor data |
| Regional multipliers | 🔴 **BROKEN** | Crashes on every call, falls back to 1.0 |
| RSMeans integration | 🟡 Partial | Data exists but isn't consumed by analyzer |
| Line item matching | ✅ Good | Fuzzy matching works, synthetic items help |
| Fair price ranges | ✅ Reasonable | Within industry norms for most types |
| Total project costs | ✅ Good | 30/34 have total project cost ranges |
| Red flag detection | ✅ Good | Catches excessive, low, bundling issues |

---

## 🔴 Critical Bug #1: Regional Multipliers Completely Broken

### The Problem

**Both V1 and V2 analyzers crash when resolving regions**, silently falling back to `multiplier = 1.0` (national average).

**V2 (`quote_analyzer.py`):**
```
resolve_region("Vermont", regional_multipliers)
→ _build_state_to_region() iterates over top-level keys
→ Tries region_data.get("states", []) on the STRING value of key "source"
→ AttributeError: 'str' object has no attribute 'get'
→ Falls back to ('national_average', 1.0)
```

**V1 (`services/analyzer.py`):**
```
get_regional_multiplier("05401")
→ Iterates over regional_data.items() looking for zip_prefixes
→ Same crash: tries .get() on string values
→ Falls back to (1.0, "national_average")
```

### Root Cause

The `regional_multipliers` section in `project_cost_models.json` has this structure:
```json
{
  "source": "RSMeans Location Factors (Residential)",
  "data_year": "2026",
  "regions": {
    "northeast": { "count": 146, "min": 0.84, "max": 1.38, "avg": 1.044, "median": 1.02 }
  }
}
```

But the V2 analyzer expects:
```json
{
  "northeast": { "multiplier": 1.05, "states": ["VT", "NH", "ME", ...] }
}
```

### Impact

- **Every analysis uses national average pricing** regardless of location
- Vermont ($25k kitchen quote) gets the same assessment as NYC ($25k kitchen quote)
- A homeowner in Mississippi (factor ~0.85) gets told their quote is "fair" when it's actually 15% overpriced
- A homeowner in San Francisco (factor ~1.35) gets told their quote is "high" when it might be fair

### The Fix

The data exists in `cost-data/rsmeans_location_factors.json` with **640 city-level factors** across all 50 states + DC. This needs to be:
1. Restructured into the format the analyzer expects (state → region mapping + multiplier per region)
2. OR: the analyzer should be updated to use city/ZIP-level factors directly from `rsmeans_location_factors.json`

**Vermont factors:** 0.94–1.02 (avg ~0.98)  
**NYC:** 1.38 | **San Francisco:** 1.35 | **Rural Mississippi:** 0.82

---

## 🟡 Issue #2: RSMeans Calibration Data Not Consumed

### The Problem

Each project type has an `rsmeans_benchmarks` field with detailed RSMeans pricing (material + labor + total per unit). This data is stored in the model **but never read by the analyzer**.

The analyzer reads: `materials`, `labor`, `components`, `typical_total_project_cost`  
RSMeans data sits in: `rsmeans_benchmarks`, `rsmeans_benchmark`  

### Example: Roof Replacement

| Item | Model Value | RSMeans Value | Gap |
|------|-------------|---------------|-----|
| Arch. shingles (material/sq) | $120 | $152 (25yr) / $166 (30yr) | Model is 21-28% low on materials |
| Tear-off (labor/sq) | $72 | $41 | Model is 76% high on tear-off labor |
| Total per square | $350-650 | $220-420 | RSMeans notes: "add 20-40% markup for market" |

The calibration report acknowledges the gap: *"RSMeans significantly lower than our model. RSMeans = contractor cost basis. Market markup adds 20-40%."* This is actually **correct reasoning** — the model includes contractor markup while RSMeans is base cost. But the RSMeans data should be used to validate/constrain the ranges, not just sit as reference.

### Impact

- Model values are reasonable but not cross-validated at analysis time
- No runtime sanity check that model values stay within RSMeans bounds + markup
- Missed opportunity for higher accuracy

---

## Project Type Data Quality Assessment

### Tier 1: Strong Data (4+ sources, detailed components)
**Estimated accuracy: ±20%**

| Project Type | Sources | Components | TPC Sizes | Real Quotes | Confidence |
|-------------|---------|------------|-----------|-------------|------------|
| roof_replacement | RSMeans + BLS + HA + PW | Materials + Labor detailed | 3 sizes | 18 quotes | ⭐⭐⭐⭐⭐ |
| kitchen_remodel | RSMeans + BLS + HA + PW | Full component breakdown | 3×3 (size×quality) | 2 benchmarks | ⭐⭐⭐⭐⭐ |
| bathroom_remodel | RSMeans + BLS + HA + PW | Full component breakdown | 3 sizes | 2 benchmarks | ⭐⭐⭐⭐⭐ |
| hvac_replacement | RSMeans + BLS + HA + PW | System types + additional | 4 configs | 2 benchmarks | ⭐⭐⭐⭐ |
| deck_building | RSMeans + BLS + HA + PW | Materials + Labor | 3 sizes | 2 benchmarks | ⭐⭐⭐⭐ |
| window_replacement | RSMeans + BLS + HA + PW | Window types + labor | 3 configs | 2 benchmarks | ⭐⭐⭐⭐ |
| siding_replacement | RSMeans + BLS + HA + PW | Materials + Labor | 3 configs | 2 benchmarks | ⭐⭐⭐⭐ |
| painting_interior | RSMeans + BLS + HA + PW | By room + by sqft | 3 sizes | 2 benchmarks | ⭐⭐⭐⭐ |
| electrical_work | RSMeans + BLS + HA + PW | Common jobs + service | 3 job types | 2 benchmarks | ⭐⭐⭐⭐ |
| plumbing_repair | RSMeans + BLS + HA + PW | Common repairs + service | 3 job types | 2 benchmarks | ⭐⭐⭐⭐ |
| fence_installation | RSMeans + BLS + HA + PW | Materials + Labor | 3 types | 2 benchmarks | ⭐⭐⭐⭐ |
| flooring_installation | RSMeans + BLS + HA + PW | Materials + Labor | 4 sizes | 2 benchmarks | ⭐⭐⭐⭐ |
| concrete_work | RSMeans + BLS + HA + PW | Materials + Labor | 3 sizes | – | ⭐⭐⭐⭐ |
| gutter_installation | RSMeans + BLS + HA + PW | Materials + Labor | 3 sizes | 2 benchmarks | ⭐⭐⭐⭐ |

### Tier 2: Good Data (RSMeans + base model)
**Estimated accuracy: ±25-30%**

| Project Type | Sources | TPC | Real Quotes | Confidence |
|-------------|---------|-----|-------------|------------|
| water_heater_replacement | RSMeans | 4 configs | 2 benchmarks | ⭐⭐⭐ |
| electrical_panel_upgrade | RSMeans | 4 configs | 2 benchmarks | ⭐⭐⭐ |
| mini_split | RSMeans | 4 configs | 2 benchmarks | ⭐⭐⭐ |
| exterior_painting | RSMeans | 4 sizes | 2 benchmarks | ⭐⭐⭐ |
| basement_finishing | RSMeans | 4 configs | 2 benchmarks | ⭐⭐⭐ |
| garage_door | RSMeans | 4 configs | 2 benchmarks | ⭐⭐⭐ |
| tree_removal | RSMeans | 4 sizes | 2 benchmarks | ⭐⭐⭐ |
| home_addition | RSMeans | 4 sizes | 2 benchmarks | ⭐⭐⭐ |
| insulation | RSMeans | 3 configs | 2 benchmarks | ⭐⭐⭐ |
| foundation_repair | RSMeans | 4 configs | 2 benchmarks | ⭐⭐⭐ |
| concrete_patio | RSMeans | 3 configs | 2 benchmarks | ⭐⭐⭐ |
| driveway | RSMeans | 4 configs | 2 benchmarks | ⭐⭐⭐ |
| retaining_wall | RSMeans | 4 sizes | 2 benchmarks | ⭐⭐⭐ |
| pool_inground | RSMeans | 4 types | 2 benchmarks | ⭐⭐⭐ |
| siding_vinyl | RSMeans | 2 configs | 2 benchmarks | ⭐⭐⭐ |
| siding_fiber_cement | RSMeans | 2 configs | 2 benchmarks | ⭐⭐⭐ |
| flooring_lvp | RSMeans | 2 configs | 2 benchmarks | ⭐⭐⭐ |

### Tier 3: Thin Data (base model only, no RSMeans cross-validation at runtime)
**Estimated accuracy: ±35-40%**

| Project Type | Sources | TPC | Real Quotes | Confidence |
|-------------|---------|-----|-------------|------------|
| solar_installation | Base model | Cost/watt + systems | 2 benchmarks | ⭐⭐ |
| septic_system | Base model | 4 types | 2 benchmarks | ⭐⭐ |
| well_drilling | Base model | 3 depths | 2 benchmarks | ⭐⭐ |

### Projects Missing `typical_total_project_cost`

These 4 project types lack total project cost ranges, meaning the total analysis returns "No total project cost range available":

1. **flooring_installation** — Has `typical_project_sizes` but no TPC (despite having RSMeans + BLS + HA data!)
2. **fence_installation** — Same issue
3. **concrete_work** — Same issue  
4. **gutter_installation** — Same issue

**Impact:** These projects can still match line items but cannot assess whether the total quote is fair. The "fair price range" for the whole project won't be calculated.

---

## Fair Price Range Methodology Assessment

### How It Works (V2 Engine)

1. **Line items:** Fuzzy-matched to cost categories → per-item range (low/mid/high)
2. **Regional adjustment:** `range × multiplier` (currently broken — always ×1.0)
3. **Total assessment:** Quote total compared to `typical_total_project_cost` range
4. **Fairness score:** Weighted composite:
   - 60% line item scores
   - 25% total cost score
   - 10% completeness (missing items penalty)
   - 5% red flag penalty
5. **Verdict:** Score → below_market / fair / high / very_high / suspiciously_low

### Assessment

The methodology is **sound in design**:
- ✅ Multi-factor scoring (not just "is it above the range?")
- ✅ Catches both overpriced AND suspiciously cheap quotes
- ✅ Missing item detection catches incomplete quotes
- ✅ Red flag detection for excessive items, bundling, dominance
- ✅ Synthetic line items bridge the gap between per-unit model data and real contractor quotes

**Concerns:**
- Regional adjustment is broken (critical — see above)
- The synthetic line item ranges in `_add_synthetic_line_items()` are **hardcoded fallbacks**, not derived from the model data. They're reasonable but won't auto-update if the model changes.
- `typical_total_project_cost` parsing handles `budget/midrange/high_end` strings like `"6000-16000"` — this works but the mid-point calculation uses the average of the midrange band, which may not represent the true median.
- The scoring uses linear interpolation within ranges, which can produce unintuitive scores at boundaries.

---

## Sample Analysis: Kitchen Remodel in Vermont, $25,000

Running the V2 analyzer with the current bug (region falls back to national average):

**Input:**
- Project: Kitchen remodel (medium)
- Location: Vermont (resolved as "national_average", multiplier=1.0)
- Line items: Cabinets $8,500 + Countertops $5,500 + Flooring $2,800 + Plumbing $2,200 + Electrical $1,800 + Appliances $4,200
- Total: $25,000

**Expected result (if regional worked correctly):**
- Vermont factor: ~0.98
- Medium kitchen TPC midrange: $18,000–$42,000 → adjusted $17,640–$41,160
- $25,000 falls solidly in the fair range → score ~75-85, verdict "fair"

**Actual result:**
- ⚠️ `resolve_region("Vermont")` crashes with `AttributeError`
- Falls back to multiplier=1.0
- Still uses unadjusted ranges: $18,000–$42,000
- $25,000 still falls in fair range (same verdict in this case)
- **For Vermont, the difference is minimal (~2%)** but for high-cost areas (NYC, SF) the error would be 30-40%

**The analysis logic itself is correct** — the bug just means regional differences are ignored.

---

## Bugs and Logic Errors Found

### 🔴 Critical

1. **Regional multiplier crash** — `resolve_region()` throws `AttributeError` on every call. Both V1 and V2 affected. All analyses use national average pricing.

### 🟡 Moderate

2. **4 project types missing TPC** — `flooring_installation`, `fence_installation`, `concrete_work`, `gutter_installation` have data but no `typical_total_project_cost`, so total-level analysis returns "unknown."

3. **RSMeans benchmarks not consumed at runtime** — Stored as reference data (`rsmeans_benchmarks`) but the analyzer never reads it. Missed opportunity for cross-validation.

4. **V2 adapter (`analyzer_v2.py`) field mapping mismatch** — The V2 adapter reads `item_result.get("quoted_cost")` and `item_result.get("range_low")` but the engine returns `item_result["cost"]` and `item_result["adjusted_range"]["low"]`. This means the V2-to-Report mapping likely produces incorrect `fair_price_low`/`fair_price_high` values, falling back to `quoted * 0.7` / `quoted * 1.1`.

### 🟢 Minor

5. **Synthetic line items are hardcoded** — The `_add_synthetic_line_items()` function has hundreds of lines of hardcoded ranges that don't auto-update if the underlying model changes. This is a maintenance concern but values are currently reasonable.

6. **`_get_total_project_range()` size matching** — For non-size-based TPC entries (like electrical: panel_upgrade, recessed_lights, ev_charger), it picks the most expensive entry as the "default". This is a reasonable heuristic but can mislead if someone's doing a small job.

---

## Recommendations

### Immediate (Pre-Launch Blockers)

1. **Fix regional multipliers** — Restructure `regional_multipliers` in `project_cost_models.json` to match the format the V2 analyzer expects, OR update the analyzer to read from `rsmeans_location_factors.json` directly (preferred — gives city-level accuracy with 640 data points).

2. **Fix V2 adapter field mapping** — Update `analyzer_v2.py` to read correct field names from the engine output (`cost`, `adjusted_range.low/high`, `matched_category`, `match_confidence`).

3. **Add TPC to the 4 missing project types** — `flooring_installation`, `fence_installation`, `concrete_work`, `gutter_installation` all have enough data to compute total project cost ranges.

### Short-Term (First 30 Days)

4. **Use RSMeans data for runtime validation** — When the analyzer computes a fair range, cross-check against `rsmeans_benchmarks` data. If the model range is >40% different from RSMeans + markup, flag it.

5. **Expand real quote benchmarks** — Currently 2 benchmark quotes per project type. Target 10+ for the top 10 most common project types. The existing `real-quotes.json` has more data that could be integrated.

6. **Add confidence indicators** — Tell users when a project type has strong data (4+ sources) vs thin data (1 source). This sets appropriate expectations.

### Medium-Term (60-90 Days)

7. **Auto-derive synthetic line items** — Replace hardcoded synthetic ranges with computed ranges from model + RSMeans data.

8. **ZIP-code-level pricing** — Use the full 640-city factor table for precise regional adjustment instead of state/region averages.

9. **Track accuracy** — Log predicted vs actual (if users report back) to measure and improve model accuracy over time.

---

## Data Source Inventory

| Source | File | Records | Used By Analyzer? |
|--------|------|---------|-------------------|
| RSMeans Pricing Guide | `rsmeans_calibration_curated.json` | 31 project types, 200+ items | ❌ Stored as reference only |
| RSMeans Location Factors | `rsmeans_location_factors.json` | 640 cities, 51 states | ❌ Not connected |
| RSMeans Full Text | `rsmeans_full_text.txt` | 726KB OCR text | ❌ Raw source |
| RSMeans Extracted | `rsmeans_extracted_data.json` | 187KB structured data | ❌ Not connected |
| BLS Labor Rates | `bls-labor-rates.json` | 14 occupation categories | ✅ In model as `bls_labor_rates` |
| HomeAdvisor Benchmarks | `homeadvisor-cost-guides.json` | 14 project types | ✅ In model as `market_benchmarks` |
| Remodeling Cost vs Value | `remodeling-cost-vs-value.json` | ROI data for 10 project types | ✅ In model as `roi_data` |
| Census Construction Data | `census-construction-data.json` | National construction stats | ⚠️ Background reference |
| Prevailing Wage Rates | `prevailing-wage-rates.json` | 5-8 metro areas per trade | ✅ In model as `prevailing_wage_context` |
| Real Contractor Quotes | `real-quotes.json` | 75KB, 29 project types | ✅ In model as `real_quote_benchmarks` |
| Project Cost Models | `backend/data/project_cost_models.json` | 34 project types | ✅ Primary data source |

---

## Conclusion

The UnGouge.ai cost model is **built on a solid data foundation** — real RSMeans data, BLS labor rates, HomeAdvisor benchmarks, and real quote calibration for 29 project types. The analysis methodology is well-designed with multi-factor scoring, missing item detection, and red flag alerts.

**However, the two critical bugs (regional multipliers crash + V2 adapter field mismatch) mean that in production:**
1. Every user gets national-average pricing regardless of location
2. The Report model likely shows incorrect fair price ranges for individual line items

**Fixing these two issues would immediately bring the system to a usable accuracy level** of approximately ±20-25% for the 14 Tier 1 project types and ±30% for Tier 2. This is within the stated "good enough to launch" target of 70-80% accuracy.

The RSMeans data integration opportunity (connecting the 640-city location factors and using RSMeans benchmarks for runtime validation) would further improve accuracy to an estimated ±15% for high-data project types.
