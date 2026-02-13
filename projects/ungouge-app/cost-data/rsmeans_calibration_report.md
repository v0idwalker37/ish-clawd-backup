# RSMeans Calibration Report
**Generated:** 2026-02-12 11:32
**Source:** RSMeans Contractor's Pricing Guide: Residential Repair & Remodeling 2026
**Script:** `scripts/calibrate_with_rsmeans.py`

## Summary

- **Types matched:** 31
- **High-confidence types:** 18
- **Low-confidence types:** 13
- **Flags raised:** 24
- **RSMeans types not in models:** none
- **Model types without RSMeans:** septic_system, solar_installation, well_drilling

## High-Confidence Calibration Results

These types have labor percentages between 10-70%, indicating reliable data.

| Project Type | Items | Parsed | Labor % | Avg Material | Avg Labor | Avg Total | Flags |
|---|---|---|---|---|---|---|---|
| bathroom_remodel | 93 | 20 | 19.2% | $436.35 | $159.50 | $564.04 | ⚠️ 1 |
| concrete_work | 25 | 20 | 66.5% | $164.95 | $46.58 | $211.53 | ⚠️ 2 |
| deck_building | 3 | 3 | 23.2% | $19.54 | $6.20 | $25.73 | ⚠️ 1 |
| electrical_panel_upgrade | 3 | 3 | 66.7% | $35.00 | $27.18 | $40.73 | ⚠️ 2 |
| electrical_work | 39 | 19 | 29.1% | $42.67 | $40.12 | $74.56 | ⚠️ 1 |
| fence_installation | 5 | 5 | 16.6% | $609.30 | $128.80 | $738.10 | ⚠️ 2 |
| hvac_replacement | 59 | 20 | 15.8% | $2324.30 | $275.65 | $2599.95 | ⚠️ 1 |
| kitchen_remodel | 57 | 20 | 12.8% | $433.33 | $66.05 | $495.38 | ⚠️ 1 |
| mini_split | 11 | 11 | 36.3% | $1060.45 | $482.27 | $1542.73 | ⚠️ 1 |
| plumbing_repair | 36 | 20 | 58.8% | $447.54 | $183.32 | $599.06 | ✅ |
| pool_inground | 7 | 7 | 11.6% | $1862.35 | $243.74 | $2105.24 | ⚠️ 2 |
| retaining_wall | 12 | 12 | 60.1% | $34.57 | $10.25 | $44.82 | ✅ |
| roof_replacement | 94 | 18 | 27.1% | $189.56 | $80.82 | $270.38 | ⚠️ 3 |
| siding_fiber_cement | 3 | 3 | 24.0% | $4.78 | $1.48 | $6.26 | ⚠️ 1 |
| siding_replacement | 58 | 17 | 18.4% | $22.49 | $8.28 | $30.77 | ⚠️ 2 |
| siding_vinyl | 7 | 7 | 18.7% | $160.39 | $35.69 | $196.08 | ⚠️ 1 |
| tree_removal | 16 | 6 | 11.9% | $517.49 | $506.78 | $4497.52 | ⚠️ 2 |
| window_replacement | 42 | 20 | 46.5% | $447.88 | $59.79 | $529.85 | ⚠️ 1 |

## Low-Confidence Data (Reference Only)

These types have labor percentages outside 10-70% or insufficient items.
Data included as reference but NOT used for calibration adjustments.

| Project Type | Items | Labor % | Issue |
|---|---|---|---|
| basement_finishing | 34 | 227.6% | Labor % too high (228%) — likely column misalignment |
| concrete_patio | 13 | 133.5% | Labor % too high (133%) — likely column misalignment |
| driveway | 13 | 133.5% | Labor % too high (133%) — likely column misalignment |
| exterior_painting | 10 | 73.7% | Labor % too high (74%) — likely column misalignment |
| flooring_installation | 40 | 158.7% | Labor % too high (159%) — likely column misalignment |
| flooring_lvp | 13 | 537.7% | Labor % too high (538%) — likely column misalignment |
| foundation_repair | 15 | 98.3% | Labor % too high (98%) — likely column misalignment |
| garage_door | 4 | 3.3% | Labor % too low (3.3%) — may be equipment-heavy |
| gutter_installation | 7 | 1.8% | Labor % too low (1.8%) — may be equipment-heavy |
| home_addition | 58 | 84.2% | Labor % too high (84%) — likely column misalignment |
| insulation | 18 | 509.9% | Labor % too high (510%) — likely column misalignment |
| painting_interior | 10 | 73.7% | Labor % too high (74%) — likely column misalignment |
| water_heater_replacement | 14 | 111.1% | Labor % too high (111%) — likely column misalignment |

## Discrepancy Flags

These items showed >20% difference between RSMeans data and our model estimates.
Review and consider adjusting model ranges.

- ⚡ bathroom_remodel labor %: RSMeans is 57% lower (model=45.00, RSMeans=19.15)
- ⚡ concrete_work labor %: RSMeans is 33% higher (model=50.00, RSMeans=66.53)
- ⚡ concrete_work avg material/unit: RSMeans is 362% higher (model=35.73, RSMeans=164.95)
- ⚡ deck_building labor %: RSMeans is 34% lower (model=35.00, RSMeans=23.24)
- ⚡ electrical_panel_upgrade labor %: RSMeans is 21% higher (model=55.00, RSMeans=66.73)
- ⚡ electrical_panel_upgrade avg material/unit: RSMeans is 93% lower (model=510.00, RSMeans=35.00)
- ⚡ electrical_work labor %: RSMeans is 47% lower (model=55.00, RSMeans=29.05)
- ⚡ fence_installation labor %: RSMeans is 52% lower (model=35.00, RSMeans=16.64)
- ⚡ fence_installation avg material/unit: RSMeans is 2154% higher (model=27.03, RSMeans=609.30)
- ⚡ hvac_replacement labor %: RSMeans is 60% lower (model=40.00, RSMeans=15.85)
- ⚡ kitchen_remodel labor %: RSMeans is 49% lower (model=25.00, RSMeans=12.78)
- ⚡ mini_split labor %: RSMeans is 21% higher (model=30.00, RSMeans=36.28)
- ⚡ pool_inground labor %: RSMeans is 71% lower (model=40.00, RSMeans=11.58)
- ⚡ pool_inground avg material/unit: RSMeans is 94% lower (model=30208.33, RSMeans=1862.35)
- ⚡ roof_replacement labor %: RSMeans is 23% lower (model=35.00, RSMeans=27.11)
- ⚡ roof_replacement avg material/unit: RSMeans is 381% higher (model=39.41, RSMeans=189.56)
- ⚡ roof_replacement total/unit (mid): RSMeans is 40% lower (model=450.00, RSMeans=270.38)
- ⚡ siding_fiber_cement labor %: RSMeans is 52% lower (model=50.00, RSMeans=23.97)
- ⚡ siding_replacement labor %: RSMeans is 59% lower (model=45.00, RSMeans=18.41)
- ⚡ siding_replacement avg material/unit: RSMeans is 185% higher (model=7.90, RSMeans=22.49)
- ⚡ siding_vinyl labor %: RSMeans is 59% lower (model=45.00, RSMeans=18.67)
- ⚡ tree_removal labor %: RSMeans is 86% lower (model=85.00, RSMeans=11.86)
- ⚡ tree_removal avg material/unit: RSMeans is 139% higher (model=216.67, RSMeans=517.49)
- ⚡ window_replacement labor %: RSMeans is 86% higher (model=25.00, RSMeans=46.53)

## Detailed Per-Type Analysis

### 🟢 bathroom_remodel

- **Items found:** 93 | **Items parsed:** 20
- **Labor %:** 19.2%
- **Avg per unit:** Material $436.35 | Labor $159.50 | Total $564.04
- **Confidence:** HIGH
- **Flags:**
  - ⚡ bathroom_remodel labor %: RSMeans is 57% lower (model=45.00, RSMeans=19.15)
- **RSMeans section totals:** min=$4.00, max=$6225.00

### 🟢 concrete_work

- **Items found:** 25 | **Items parsed:** 20
- **Labor %:** 66.5%
- **Avg per unit:** Material $164.95 | Labor $46.58 | Total $211.53
- **Confidence:** HIGH
- **Flags:**
  - ⚡ concrete_work labor %: RSMeans is 33% higher (model=50.00, RSMeans=66.53)
  - ⚡ concrete_work avg material/unit: RSMeans is 362% higher (model=35.73, RSMeans=164.95)
- **RSMeans section totals:** min=$12.85, max=$23.00

### 🟢 deck_building

- **Items found:** 3 | **Items parsed:** 3
- **Labor %:** 23.2%
- **Avg per unit:** Material $19.54 | Labor $6.20 | Total $25.73
- **Confidence:** HIGH
- **Flags:**
  - ⚡ deck_building labor %: RSMeans is 34% lower (model=35.00, RSMeans=23.24)
- **RSMeans section totals:** min=$48.20, max=$48.20

### 🟢 electrical_panel_upgrade

- **Items found:** 3 | **Items parsed:** 3
- **Labor %:** 66.7%
- **Avg per unit:** Material $35.00 | Labor $27.18 | Total $40.73
- **Confidence:** HIGH
- **Flags:**
  - ⚡ electrical_panel_upgrade labor %: RSMeans is 21% higher (model=55.00, RSMeans=66.73)
  - ⚡ electrical_panel_upgrade avg material/unit: RSMeans is 93% lower (model=510.00, RSMeans=35.00)
- **RSMeans section totals:** min=$5.70, max=$60.00

### 🟢 electrical_work

- **Items found:** 39 | **Items parsed:** 19
- **Labor %:** 29.1%
- **Avg per unit:** Material $42.67 | Labor $40.12 | Total $74.56
- **Confidence:** HIGH
- **Flags:**
  - ⚡ electrical_work labor %: RSMeans is 47% lower (model=55.00, RSMeans=29.05)
- **RSMeans section totals:** min=$5.70, max=$1736.00

### 🟢 fence_installation

- **Items found:** 5 | **Items parsed:** 5
- **Labor %:** 16.6%
- **Avg per unit:** Material $609.30 | Labor $128.80 | Total $738.10
- **Confidence:** HIGH
- **Flags:**
  - ⚡ fence_installation labor %: RSMeans is 52% lower (model=35.00, RSMeans=16.64)
  - ⚡ fence_installation avg material/unit: RSMeans is 2154% higher (model=27.03, RSMeans=609.30)
- **RSMeans section totals:** min=$229.50, max=$2430.00

### 🟢 hvac_replacement

- **Items found:** 59 | **Items parsed:** 20
- **Labor %:** 15.8%
- **Avg per unit:** Material $2324.30 | Labor $275.65 | Total $2599.95
- **Confidence:** HIGH
- **Flags:**
  - ⚡ hvac_replacement labor %: RSMeans is 60% lower (model=40.00, RSMeans=15.85)
- **RSMeans section totals:** min=$4.00, max=$6225.00

### 🟢 kitchen_remodel

- **Items found:** 57 | **Items parsed:** 20
- **Labor %:** 12.8%
- **Avg per unit:** Material $433.33 | Labor $66.05 | Total $495.38
- **Confidence:** HIGH
- **Flags:**
  - ⚡ kitchen_remodel labor %: RSMeans is 49% lower (model=25.00, RSMeans=12.78)
- **RSMeans section totals:** min=$3.57, max=$3665.00

### 🟢 mini_split

- **Items found:** 11 | **Items parsed:** 11
- **Labor %:** 36.3%
- **Avg per unit:** Material $1060.45 | Labor $482.27 | Total $1542.73
- **Confidence:** HIGH
- **Flags:**
  - ⚡ mini_split labor %: RSMeans is 21% higher (model=30.00, RSMeans=36.28)
- **RSMeans section totals:** min=$755.00, max=$1180.00

### 🟢 plumbing_repair

- **Items found:** 36 | **Items parsed:** 20
- **Labor %:** 58.8%
- **Avg per unit:** Material $447.54 | Labor $183.32 | Total $599.06
- **Confidence:** HIGH
- **RSMeans section totals:** min=$4.00, max=$427.00

### 🟢 pool_inground

- **Items found:** 7 | **Items parsed:** 7
- **Labor %:** 11.6%
- **Avg per unit:** Material $1862.35 | Labor $243.74 | Total $2105.24
- **Confidence:** HIGH
- **Flags:**
  - ⚡ pool_inground labor %: RSMeans is 71% lower (model=40.00, RSMeans=11.58)
  - ⚡ pool_inground avg material/unit: RSMeans is 94% lower (model=30208.33, RSMeans=1862.35)
- **RSMeans section totals:** min=$6.11, max=$8270.00

### 🟢 retaining_wall

- **Items found:** 12 | **Items parsed:** 12
- **Labor %:** 60.1%
- **Avg per unit:** Material $34.57 | Labor $10.25 | Total $44.82
- **Confidence:** HIGH
- **RSMeans section totals:** min=$9.25, max=$19.75

### 🟢 roof_replacement

- **Items found:** 94 | **Items parsed:** 18
- **Labor %:** 27.1%
- **Avg per unit:** Material $189.56 | Labor $80.82 | Total $270.38
- **Confidence:** HIGH
- **Flags:**
  - ⚡ roof_replacement labor %: RSMeans is 23% lower (model=35.00, RSMeans=27.11)
  - ⚡ roof_replacement avg material/unit: RSMeans is 381% higher (model=39.41, RSMeans=189.56)
  - ⚡ roof_replacement total/unit (mid): RSMeans is 40% lower (model=450.00, RSMeans=270.38)
- **RSMeans section totals:** min=$2.64, max=$4770.00

### 🟢 siding_fiber_cement

- **Items found:** 3 | **Items parsed:** 3
- **Labor %:** 24.0%
- **Avg per unit:** Material $4.78 | Labor $1.48 | Total $6.26
- **Confidence:** HIGH
- **Flags:**
  - ⚡ siding_fiber_cement labor %: RSMeans is 52% lower (model=50.00, RSMeans=23.97)
- **RSMeans section totals:** min=$3.52, max=$10.08

### 🟢 siding_replacement

- **Items found:** 58 | **Items parsed:** 17
- **Labor %:** 18.4%
- **Avg per unit:** Material $22.49 | Labor $8.28 | Total $30.77
- **Confidence:** HIGH
- **Flags:**
  - ⚡ siding_replacement labor %: RSMeans is 59% lower (model=45.00, RSMeans=18.41)
  - ⚡ siding_replacement avg material/unit: RSMeans is 185% higher (model=7.90, RSMeans=22.49)
- **RSMeans section totals:** min=$3.52, max=$3644.00

### 🟢 siding_vinyl

- **Items found:** 7 | **Items parsed:** 7
- **Labor %:** 18.7%
- **Avg per unit:** Material $160.39 | Labor $35.69 | Total $196.08
- **Confidence:** HIGH
- **Flags:**
  - ⚡ siding_vinyl labor %: RSMeans is 59% lower (model=45.00, RSMeans=18.67)
- **RSMeans section totals:** min=$4.81, max=$1289.00

### 🟢 tree_removal

- **Items found:** 16 | **Items parsed:** 6
- **Labor %:** 11.9%
- **Avg per unit:** Material $517.49 | Labor $506.78 | Total $4497.52
- **Confidence:** HIGH
- **Flags:**
  - ⚡ tree_removal labor %: RSMeans is 86% lower (model=85.00, RSMeans=11.86)
  - ⚡ tree_removal avg material/unit: RSMeans is 139% higher (model=216.67, RSMeans=517.49)
- **RSMeans section totals:** min=$3.84, max=$21050.00

### 🟢 window_replacement

- **Items found:** 42 | **Items parsed:** 20
- **Labor %:** 46.5%
- **Avg per unit:** Material $447.88 | Labor $59.79 | Total $529.85
- **Confidence:** HIGH
- **Flags:**
  - ⚡ window_replacement labor %: RSMeans is 86% higher (model=25.00, RSMeans=46.53)
- **RSMeans section totals:** min=$18.10, max=$763.00

### 🟡 basement_finishing

- **Items found:** 34 | **Items parsed:** 17
- **Labor %:** 227.6%
- **Avg per unit:** Material $111.78 | Labor $13.69 | Total $122.33
- **Confidence:** LOW
- **RSMeans section totals:** min=$1.08, max=$182.90

### 🟡 concrete_patio

- **Items found:** 13 | **Items parsed:** 12
- **Labor %:** 133.5%
- **Avg per unit:** Material $40.86 | Labor $19.28 | Total $45.13
- **Confidence:** LOW
- **RSMeans section totals:** min=$1.67, max=$81.00

### 🟡 driveway

- **Items found:** 13 | **Items parsed:** 12
- **Labor %:** 133.5%
- **Avg per unit:** Material $40.86 | Labor $19.28 | Total $45.13
- **Confidence:** LOW
- **RSMeans section totals:** min=$1.67, max=$81.00

### 🟡 exterior_painting

- **Items found:** 10 | **Items parsed:** 10
- **Labor %:** 73.7%
- **Avg per unit:** Material $43.80 | Labor $19.05 | Total $25.84
- **Confidence:** LOW
- **RSMeans section totals:** min=$1.38, max=$75.00

### 🟡 flooring_installation

- **Items found:** 40 | **Items parsed:** 20
- **Labor %:** 158.7%
- **Avg per unit:** Material $71.06 | Labor $71.10 | Total $131.35
- **Confidence:** LOW
- **RSMeans section totals:** min=$1.38, max=$130.30

### 🟡 flooring_lvp

- **Items found:** 13 | **Items parsed:** 12
- **Labor %:** 537.7%
- **Avg per unit:** Material $9.29 | Labor $5.60 | Total $13.84
- **Confidence:** LOW
- **RSMeans section totals:** min=$1.96, max=$64.70

### 🟡 foundation_repair

- **Items found:** 15 | **Items parsed:** 14
- **Labor %:** 98.3%
- **Avg per unit:** Material $32.63 | Labor $7.37 | Total $40.00
- **Confidence:** LOW
- **RSMeans section totals:** min=$97.19, max=$97.19

### 🟡 garage_door

- **Items found:** 4 | **Items parsed:** 4
- **Labor %:** 3.3%
- **Avg per unit:** Material $1887.50 | Labor $637.00 | Total $2524.50
- **Confidence:** LOW
- **RSMeans section totals:** min=$1654.00, max=$1654.00

### 🟡 gutter_installation

- **Items found:** 7 | **Items parsed:** 5
- **Labor %:** 1.8%
- **Avg per unit:** Material $100.80 | Labor $3.77 | Total $4030.88
- **Confidence:** LOW
- **RSMeans section totals:** min=$8.94, max=$20120.00

### 🟡 home_addition

- **Items found:** 58 | **Items parsed:** 18
- **Labor %:** 84.2%
- **Avg per unit:** Material $105.01 | Labor $11.56 | Total $48.92
- **Confidence:** LOW
- **RSMeans section totals:** min=$5.67, max=$269.90

### 🟡 insulation

- **Items found:** 18 | **Items parsed:** 15
- **Labor %:** 509.9%
- **Avg per unit:** Material $123.40 | Labor $55.60 | Total $119.33
- **Confidence:** LOW
- **RSMeans section totals:** min=$1.15, max=$126.00

### 🟡 painting_interior

- **Items found:** 10 | **Items parsed:** 10
- **Labor %:** 73.7%
- **Avg per unit:** Material $43.80 | Labor $19.05 | Total $25.84
- **Confidence:** LOW
- **RSMeans section totals:** min=$1.38, max=$75.00

### 🟡 water_heater_replacement

- **Items found:** 14 | **Items parsed:** 14
- **Labor %:** 111.1%
- **Avg per unit:** Material $493.77 | Labor $182.78 | Total $631.12
- **Confidence:** LOW
- **RSMeans section totals:** min=$4.00, max=$146.00

## Data Quality Notes

### Understanding the Cost Scales
- RSMeans data provides **per-unit costs** (per S.F., L.F., Sq., Ea.)
- Our models provide **whole-project cost ranges** (total for a typical project)
- Direct comparison requires understanding the unit and typical project size
- Example: RSMeans roofing at $170/square × 20 squares = $3,400 materials

### OCR Artifacts
- Some `costs` arrays include specification numbers (e.g., '#30 felt' → 30.0)
- We validate by checking if costs[2] ≈ costs[0] + costs[1]
- Items failing validation are excluded from per-unit averages

### Labor Percentage Anomalies
- Sections with labor >100% have column misalignment in OCR output
- These sections' aggregate stats (avg_material, avg_labor) are unreliable
- Individual items within these sections may still be valid if they pass validation

## What Changed in the Cost Models

1. **Added `rsmeans_benchmark` field** to all 34 project types
2. **High-confidence types** (18): Full benchmark with per-unit averages and representative samples
3. **Low-confidence types** (13): Benchmark included as reference with confidence warning
4. **Unmatched model types** (3): Marked with `status: no_rsmeans_data`
5. **Existing data preserved** — no fields deleted, only additions
6. **Backup saved** at `project_cost_models_pre_rsmeans.json`

### Note on Existing `rsmeans_benchmarks`
Some models already had manually-added `rsmeans_benchmarks` (plural) from earlier work.
This calibration adds a new `rsmeans_benchmark` (singular) field with standardized,
automatically-generated data. The old `rsmeans_benchmarks` field is preserved.
