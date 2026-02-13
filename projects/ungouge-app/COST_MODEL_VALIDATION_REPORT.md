# Cost Model Validation Report
**Date:** 2026-02-13
**Reviewer:** Automated validation (Claude)
**Scope:** All files in `cost-data/`, `backend/services/analyzer.py`, `backend/services/analyzer_v2.py`, `backend/quote_analyzer.py`, `backend/data/project_cost_models.json`

---

## Executive Summary

The Ungouge cost models are **built on real data, not placeholders**. The system ingests data from 6+ authoritative sources, covers 34 project types, and includes 640-city regional multipliers sourced from RSMeans 2026. However, there are significant calibration gaps between the cost model assumptions and the RSMeans/real-quote benchmarks, and the regional multiplier system in `analyzer.py` (v1) uses a crude ZIP-prefix approach that doesn't leverage the full city-level data.

**Overall Data Quality: B+** — Strong foundations, needs calibration refinement.

---

## 1. Data Sources Inventory

| Source | File(s) | Type | Quality |
|--------|---------|------|---------|
| BLS Occupational Employment & Wage Statistics | `bls-labor-rates.json`, `sample_bls_rates.json` | Government wage data (May 2023/2024) | ⭐⭐⭐⭐⭐ Real |
| RSMeans 2026 Contractor's Pricing Guide | `rsmeans_extracted_data.json`, `rsmeans_calibration.json`, `rsmeans_calibration_curated.json`, `rsmeans_location_factors.json`, 307 OCR page texts | Industry-standard cost book (OCR'd) | ⭐⭐⭐⭐ Real (OCR artifacts) |
| HomeAdvisor/Angi Cost Guides | `homeadvisor-cost-guides.json` | Consumer platform data, 14 categories | ⭐⭐⭐ Real (self-reported, lead-gen bias) |
| Remodeling Magazine Cost vs Value 2025 | `remodeling-cost-vs-value.json` | Industry gold standard, 28 projects, 119 markets | ⭐⭐⭐⭐⭐ Real |
| U.S. Census Construction Spending (C30) | `census-construction-data.json` | Government macro data | ⭐⭐⭐⭐ Real |
| Prevailing Wage Rates (DOL/eBacon) | `prevailing-wage-rates.json` | 8 states, 4-5 trades each | ⭐⭐⭐ Real (approximate) |
| Real Contractor Quotes (Reddit) | `real-quotes.json`, `real-quotes-summary.md` | 226 homeowner-reported quotes, 47 project types | ⭐⭐⭐⭐ Real (self-reported) |

**Verdict: All data sources are real.** No placeholder or synthetic cost data was found. The only synthetic elements are the line-item-level aggregations in `quote_analyzer.py` (which are computed from the real per-unit data).

---

## 2. Cost Model Structure (`project_cost_models.json`)

### 2.1 Coverage
- **34 project types** defined with full cost breakdowns
- Each type includes: materials, labor, typical project sizes, total project cost ranges, common upsells, and red flags
- **14 project types enriched** with BLS labor rates, HomeAdvisor benchmarks, ROI data, and prevailing wage context (70 total enrichments)
- **Real quote benchmarks** integrated for calibrated project types (sourced from 226 Reddit quotes)
- **RSMeans benchmarks** added for 31 project types (18 high-confidence, 13 low-confidence)

### 2.2 Project Types Covered

| Category | Project Types | Status |
|----------|--------------|--------|
| Roofing | roof_replacement | ✅ Full model + RSMeans + BLS + real quotes |
| Kitchen/Bath | kitchen_remodel, bathroom_remodel | ✅ Full model + RSMeans + BLS + real quotes |
| HVAC | hvac_replacement, mini_split | ✅ Full model + RSMeans + BLS + real quotes |
| Plumbing | plumbing_repair | ✅ Full model + RSMeans + BLS + real quotes |
| Electrical | electrical_work, electrical_panel_upgrade | ✅ Full model + RSMeans + BLS + real quotes |
| Exterior | siding_replacement, siding_vinyl, siding_fiber_cement, window_replacement | ✅ Full model + RSMeans + BLS + real quotes |
| Decks/Patios | deck_building, concrete_patio, concrete_work, retaining_wall | ✅ Full model + RSMeans + real quotes |
| Painting | painting_interior, exterior_painting | ✅ Full model + RSMeans + BLS |
| Flooring | flooring_installation, flooring_lvp | ✅ Full model + RSMeans |
| Fencing | fence_installation | ✅ Full model + RSMeans + BLS |
| Specialty | pool_inground, tree_removal, home_addition, basement_finishing, foundation_repair, garage_door, gutter_installation, insulation, driveway, water_heater_replacement, septic_system, solar_installation, well_drilling | ⚠️ Models present, varying RSMeans confidence |

### 2.3 Data Not Covered (Gaps)
- **31 unmapped quote types** from real quotes not yet in models (e.g., tub_to_shower_conversion, sewer_line_replacement, countertop_quartz, heat_pump, pool_resurfacing)
- No models for: chimney repair, landscape design, deck staining, pressure washing, grading/excavation

---

## 3. Regional Multiplier Assessment

### 3.1 Source & Accuracy
Regional multipliers are sourced from **RSMeans 2026 Location Factors** — the industry standard:

| Region | Factor Range | Avg | Median | Cities |
|--------|-------------|-----|--------|--------|
| Alaska/Hawaii | 1.13–1.21 | 1.168 | 1.19 | 6 |
| West Coast | 0.97–1.35 | 1.132 | 1.14 | 53 |
| Northeast | 0.84–1.38 | 1.044 | 1.02 | 146 |
| Midwest | 0.80–1.21 | 0.932 | 0.92 | 164 |
| Mountain | 0.83–1.06 | 0.908 | 0.90 | 49 |
| Southeast | 0.78–1.10 | 0.874 | 0.86 | 152 |
| Southwest | 0.78–0.91 | 0.852 | 0.86 | 70 |

**640 cities across 51 states** have individual location factors mapped to ZIP code ranges.

### 3.2 Implementation Issues

**`analyzer.py` (v1):** Uses a crude `zip_prefix[0]` lookup against `regional_multipliers` — but the model file's `regional_multipliers` object doesn't have `zip_prefixes` at the region level. The regions only have summary stats (count, min, max, avg, median) but **no `multiplier` field or `zip_prefixes` array**. This means `get_regional_multiplier()` always falls through to the default `(1.0, "national_average")`. **The v1 regional adjustment is effectively broken.**

**`quote_analyzer.py` (v2):** Uses a state-to-region mapping via `resolve_region()`. The `_build_state_to_region()` function looks for `states` arrays in each region — but the `regional_multipliers.regions` object also **lacks `states` arrays and `multiplier` fields**. It only has statistical summaries. This means the v2 analyzer also defaults to `(1.0, "national_average")` for most inputs.

**Available but unused:** The full 640-city ZIP-to-factor mapping exists in `rsmeans_location_factors.json` (`by_state` → city-level entries with `zip_range` and `factor`), but neither analyzer actually loads or uses this file.

### 3.3 Verdict
**Regional multiplier data is excellent (real RSMeans 2026), but the implementation doesn't fully utilize it.** Both analyzers effectively default to national average (1.0x) for most inputs because the `regional_multipliers` section in `project_cost_models.json` lacks the `states`/`multiplier`/`zip_prefixes` fields the code expects.

---

## 4. Accuracy Assessment by Project Type

### 4.1 High-Confidence Types (RSMeans calibrated + real quotes)

| Project Type | Model Range | Real Quote Median | RSMeans Labor % | Key Discrepancies |
|---|---|---|---|---|
| **Roof Replacement** | $7K–$19.5K (20 sq) | $18,600 (n=18) | 27.1% | Model labor % (35%) too high by 23%; material/unit 381% off |
| **Kitchen Remodel** | $14.6K–$41.5K (HA) | $71,000 (n=8) | 12.8% | Real quotes significantly higher than HomeAdvisor ranges; model labor % (25%) almost 2x RSMeans |
| **Bathroom Remodel** | $6.6K–$17.6K (HA) | $35,000 (n=21) | 19.2% | Real quotes 2-3x HomeAdvisor range; model labor % (45%) is 57% higher than RSMeans |
| **HVAC Replacement** | $5K–$12.5K (HA) | $13,500 (n=20) | 15.8% | Model labor % (40%) is 60% higher than RSMeans |
| **Plumbing Repair** | varies | $6,000 (n=13) | 58.8% | ✅ Only type where RSMeans matches model well |
| **Electrical Work** | varies | $5,500 (n=8) | 29.1% | Model labor % (55%) is 47% higher than RSMeans |
| **Deck Building** | $4.3K–$12.6K (HA) | $31,000 (n=11) | 23.2% | Real quotes 2.5-7x HomeAdvisor; model labor % 34% too high |
| **Window Replacement** | varies | $4,650 (n=9) | 46.5% | Model labor % (25%) is 86% lower than RSMeans — inverse error |
| **Siding Replacement** | $5.4K–$16K (HA) | $43,000 (n=6) | 18.4% | Real quotes 2.7-8x HomeAdvisor; model labor % 59% too high |
| **Fence Installation** | varies | $7,040 (n=8) | 16.6% | Model labor % 52% too high; material/unit 2154% off (unit mismatch) |

### 4.2 Key Findings

1. **HomeAdvisor ranges systematically understate actual costs.** Real quote medians exceed HomeAdvisor averages by 2-3x for most project types. This is likely because HomeAdvisor reports "average project cost" which may exclude premium materials, large homes, or high-cost regions.

2. **Labor percentage assumptions are inconsistent with RSMeans.** In 14 of 18 high-confidence RSMeans comparisons, the model's assumed labor percentage deviates by >20% from RSMeans. Most errors overstate labor share (meaning the model expects more labor cost relative to materials than RSMeans data shows).

3. **Plumbing is the best-calibrated type.** It's the only project type where RSMeans and model assumptions align closely, with no discrepancy flags.

4. **Unit-of-measure mismatches cause apparent discrepancies.** RSMeans reports per-unit costs (per S.F., L.F., Sq., Ea.) while the model has whole-project costs. The calibration script correctly identified this but some direct comparisons are misleading (e.g., fence material at $609/unit in RSMeans vs $27/unit in the model — different units).

5. **OCR quality limits RSMeans data.** 13 of 31 RSMeans project types have "low confidence" due to labor percentages >100%, indicating column misalignment in the OCR output. These types' aggregate statistics are unreliable.

---

## 5. Analyzer Engine Assessment

### 5.1 `analyzer.py` (v1) — Legacy
- Loads `project_cost_models.json` and `sample_bls_rates.json`
- Fuzzy-matches line items to cost model categories
- Calculates fair price ranges with regional adjustment
- **Regional adjustment is broken** (always returns 1.0)
- Assessment thresholds: fair (≤110% of high), slightly_high (110-125%), high (125-150%), gouging (>150%)
- Good explanation generation with red flags and project-specific advice

### 5.2 `analyzer_v2.py` — Wrapper
- Wraps `quote_analyzer.py` (the standalone engine)
- Reports 67.7% accuracy, 87% line item match rate, 26.7ms average
- Maps verdicts to frontend-expected assessment strings

### 5.3 `quote_analyzer.py` — V2 Engine (Current)
- **1,664 lines**, fully self-contained, standard library only
- Comprehensive fuzzy matching with token overlap and substring boosts
- Recursive cost range extraction from the model JSON
- **Synthetic line-item aggregations** bridge per-unit model data to project-level ranges — these are the "computed" values (not raw data) but are derived from real per-unit costs and realistic project sizes
- Red flag detection: excessive cost, suspiciously low, bundling, single-item dominance
- Missing items detection for 14 project types
- Fairness scoring (0-100) with weighted components: line items (60%), total cost (25%), completeness (10%), red flags (5%)
- Verdict thresholds: below_market (90+), fair (65-89), high (45-64), very_high (30-44), suspiciously_low (<30)
- **State → region resolution exists but doesn't work** because `regional_multipliers` in the model lacks `states` arrays

---

## 6. Recommendations

### Critical (Fix Before Launch)
1. **Fix regional multiplier pipeline:** Add `states` and `multiplier` fields to `project_cost_models.json`'s `regional_multipliers.regions`, OR have `quote_analyzer.py` load `rsmeans_location_factors.json` directly for ZIP-to-factor lookups.
2. **Recalibrate labor percentages** against RSMeans for the 14 types with >20% deviation. The current labor share assumptions significantly affect fair-price calculations.

### High Priority
3. **Adjust total project cost ranges** to reflect real quote data. HomeAdvisor-based ranges are too low; the real-quote benchmarks (already in the model under `real_quote_benchmarks`) should take priority.
4. **Clean OCR column alignment** for the 13 low-confidence RSMeans types to unlock more calibration data.
5. **Add models for top unmapped types**: tree_removal (9 quotes), garage_door (7), home_addition (6), pool_inground (6), solar_installation (5).

### Medium Priority
6. **Integrate the 640-city location factors** from `rsmeans_location_factors.json` for precise ZIP-code-level adjustments instead of region-level averages.
7. **Add more real quote data** for geographic diversity (Southeast, Mountain West underrepresented) and project types with <5 quotes.
8. **Version the cost data** with effective dates so the system can handle inflation/time adjustments.

---

## 7. Summary Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Data Authenticity | **A** | All sources are real, authoritative data |
| Source Diversity | **A** | 6+ independent sources cross-referenced |
| Project Type Coverage | **B+** | 34 types, but 31 quote types unmapped |
| Regional Accuracy | **C** | Excellent data (640 cities) but broken implementation |
| Labor % Calibration | **C** | 14/18 types deviate >20% from RSMeans |
| Total Cost Ranges | **B-** | Model ranges understate real market by 2-3x for some types |
| Analyzer Engine | **B+** | Sophisticated analysis, good UX, needs regional fix |
| **Overall** | **B+** | Strong data foundation, needs calibration & regional fix |
