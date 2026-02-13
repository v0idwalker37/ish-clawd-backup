# RSMeans Data Extraction Report
**Date:** 2026-02-12
**Source:** RSMeans Contractor's Pricing Guide: Residential Repair & Remodeling (322 pages)
**Method:** Tesseract 5.5.2 OCR → Python structured extraction

## Summary
- **Total project types:** 31
- **Total line items extracted:** 819
- **Pages processed:** 307 (pages 15-294 of PDF)
- **OCR text output:** 662,184 characters (725 KB)

## Data Quality Notes
- Some labor percentages exceed 100% — indicates OCR misalignment in column parsing
- Items with very low avg_total (<$20) likely represent per-unit costs (per S.F., L.F.) not whole-project costs
- Items with high avg_total ($1000+) likely represent fixture/equipment costs (whole units)
- The `costs` array in sample items may include specification numbers (e.g., "#30 felt" → 30.0)

## Extraction by Project Type

| Project Type | Items | Avg Total | Labor % | Samples |
|---|---|---|---|---|
| basement_finishing | 34 | $29.39 | 227.6% ⚠️ | 20 |
| bathroom_remodel | 93 | $1124.58 | 19.2% ✅ | 20 |
| concrete_patio | 13 | $17.34 | 133.5% ⚠️ | 13 |
| concrete_work | 25 | $17.93 | 66.5% ✅ | 20 |
| deck_building | 3 | $48.20 | 23.2% ✅ | 3 |
| driveway | 13 | $17.34 | 133.5% ⚠️ | 13 |
| electrical_panel_upgrade | 3 | $40.73 | 66.7% ✅ | 3 |
| electrical_work | 39 | $142.72 | 29.1% ✅ | 20 |
| exterior_painting | 10 | $25.84 | 73.7% ✅ | 10 |
| fence_installation | 5 | $1013.50 | 16.6% ✅ | 5 |
| flooring_installation | 40 | $23.80 | 158.7% ⚠️ | 20 |
| flooring_lvp | 13 | $15.64 | 537.7% ⚠️ | 13 |
| foundation_repair | 15 | $97.19 | 98.3% ✅ | 15 |
| garage_door | 4 | $1654.00 | 3.3% ✅ | 4 |
| gutter_installation | 7 | $5121.73 | 1.8% ✅ | 7 |
| home_addition | 58 | $65.78 | 84.2% ✅ | 20 |
| hvac_replacement | 59 | $1842.14 | 15.8% ✅ | 20 |
| insulation | 18 | $13.00 | 509.9% ⚠️ | 18 |
| kitchen_remodel | 57 | $846.95 | 12.8% ✅ | 20 |
| mini_split | 11 | $943.20 | 36.3% ✅ | 11 |
| painting_interior | 10 | $25.84 | 73.7% ✅ | 10 |
| plumbing_repair | 36 | $147.00 | 58.8% ✅ | 20 |
| pool_inground | 7 | $2105.24 | 11.6% ✅ | 7 |
| retaining_wall | 12 | $13.14 | 60.1% ✅ | 12 |
| roof_replacement | 94 | $402.76 | 27.1% ✅ | 20 |
| siding_fiber_cement | 3 | $6.80 | 24.0% ✅ | 3 |
| siding_replacement | 58 | $378.65 | 18.4% ✅ | 20 |
| siding_vinyl | 7 | $435.35 | 18.7% ✅ | 7 |
| tree_removal | 16 | $1818.23 | 11.9% ✅ | 16 |
| water_heater_replacement | 14 | $71.33 | 111.1% ⚠️ | 14 |
| window_replacement | 42 | $238.53 | 46.5% ✅ | 20 |

## High-Confidence Sections (labor % between 10-70%)
These sections have realistic labor/material ratios and are most reliable:

- **bathroom_remodel**: 93 items, 19.2% labor
- **concrete_work**: 25 items, 66.5% labor
- **deck_building**: 3 items, 23.2% labor
- **electrical_panel_upgrade**: 3 items, 66.7% labor
- **electrical_work**: 39 items, 29.1% labor
- **fence_installation**: 5 items, 16.6% labor
- **hvac_replacement**: 59 items, 15.8% labor
- **kitchen_remodel**: 57 items, 12.8% labor
- **mini_split**: 11 items, 36.3% labor
- **plumbing_repair**: 36 items, 58.8% labor
- **pool_inground**: 7 items, 11.6% labor
- **retaining_wall**: 12 items, 60.1% labor
- **roof_replacement**: 94 items, 27.1% labor
- **siding_fiber_cement**: 3 items, 24.0% labor
- **siding_replacement**: 58 items, 18.4% labor
- **siding_vinyl**: 7 items, 18.7% labor
- **tree_removal**: 16 items, 11.9% labor
- **window_replacement**: 42 items, 46.5% labor

**18 of 31 sections** have high-confidence data.

## Sample Data (Roofing)

- **Underlayment** (page 87): 
  Raw: `Install Sq. 8.70 7.80 16.50} #15 felt underlayment.`
- **Underlayment** (page 87): 
  Raw: `Install Sq. 16.15 8.60 24.75 | #30 felt underlayment.`
- **Self Adhering** (page 87): Mat=$90.00, Lab=$22.50, Total=$112.50
  Raw: `. Install Sq. 90 22.50 112.50) self adhering ice barrier roofing`
- **Self Adhering** (page 87): 
  Raw: `Install Sq. 61.50 41.50 103 __| install 90 Ib mineral surface rolled`
- **Self Adhering** (page 87): 
  Raw: `Install Sq. 115 55.50 170.50 | install 25 year fiberglass shingles.`

## Next Steps
1. Clean column misalignments (labor >100% sections)
2. Cross-reference with existing cost models to calibrate
3. Map RSMeans unit costs to whole-project estimates
4. Integrate location factors (pages 295-300) for regional adjustment
5. Compare with real contractor quote data (226 quotes already processed)
