# Quote Analysis Validation Results

**Date:** 2026-02-16 16:39:48
**Tests:** 20 | **Passed:** 18 | **Failed:** 2
**Pass Rate:** 90%

## Summary

| # | Test Name | Score | Verdict | Expected | Match Rate | Result |
|---|-----------|-------|---------|----------|------------|--------|
| 1 | Bathroom Remodel - Vermont - Mid-Range | 68.7 | fair | fair | 100% | ✅ PASS |
| 2 | Kitchen Renovation - Texas - Overpriced | 45.9 | high | high, very_high | 100% | ✅ PASS |
| 3 | Roof Replacement - California - Below Market | 40.4 | very_high | fair, high | 100% | ❌ FAIL |
| 4 | HVAC Installation - Florida - Fair | 74.5 | fair | fair | 100% | ✅ PASS |
| 5 | Interior Painting - Midwest - High Side | 68.6 | fair | fair, high | 100% | ✅ PASS |
| 6 | Bathroom Remodel - California - High-End | 47.8 | high | fair, high | 78% | ✅ PASS |
| 7 | Kitchen Remodel - Ohio - Fair Mid-Range | 59.2 | high | fair | 100% | ❌ FAIL |
| 8 | Roof Replacement - Florida - Suspiciously Low | 46.2 | high | suspiciously_low, high | 67% | ✅ PASS |
| 9 | Deck Building - Massachusetts - Composite | 48.2 | high | fair, high | 83% | ✅ PASS |
| 10 | Window Replacement - New Jersey - 10 Windows | 71.9 | fair | fair | 100% | ✅ PASS |
| 11 | Siding Replacement - Minnesota - Vinyl | 66.7 | fair | fair, high | 100% | ✅ PASS |
| 12 | HVAC Full System - New York - Fair | 69.2 | fair | fair, high | 83% | ✅ PASS |
| 13 | Interior Painting - Georgia - Fair | 75.5 | fair | fair, below_market | 100% | ✅ PASS |
| 14 | Bathroom Remodel - Texas - Budget | 76.8 | fair | fair, below_market | 88% | ✅ PASS |
| 15 | Kitchen Remodel - Connecticut - Very High | 42.8 | very_high | high, very_high | 100% | ✅ PASS |
| 16 | Roof Replacement - Texas - Good Deal | 70.1 | fair | fair, below_market | 100% | ✅ PASS |
| 17 | Electrical Panel Upgrade - Washington - Fair | 54.1 | high | fair, high | 50% | ✅ PASS |
| 18 | Deck Building - Alabama - Budget | 77.8 | fair | fair, below_market | 50% | ✅ PASS |
| 19 | Water Heater Install - Colorado - Fair | 76.7 | fair | fair, below_market | 40% | ✅ PASS |
| 20 | Hardwood Flooring - Virginia - Fair | 73.1 | fair | fair, high | 100% | ✅ PASS |

## Aggregate Statistics

- **Average fairness score:** 62.7/100
- **Average line item match rate:** 87%
- **Score range:** 40.4 - 77.8

### Verdict Distribution

- **fair:** 12 quotes
- **high:** 6 quotes
- **very_high:** 2 quotes

## Failed Tests — Details

### Roof Replacement - California - Below Market
- **Score:** 40.4 (expected (45, 80))
- **Verdict:** very_high (expected fair, high)
- **Items matched:** 5/5
- **Note:** $12k in CA is at the lower end. Model says mid ~$11,700 adjusted. Missing underlayment/drip edge flags expected.

| Line Item | Assessment | Score | Matched To | Confidence |
|-----------|------------|-------|-----------|------------|
| Asphalt shingles (architectural) | excessive | 5 | materials_asphalt_shingles_architectural_cost_per_square | 0.85 |
| Tear off and removal | fair_to_high | 61 | tear off and removal | 1.00 |
| Installation labor | fair_to_high | 60 | installation labor | 1.00 |
| Flashing and trim | high | 41 | flashing | 0.70 |
| Cleanup and disposal | excessive | 18 | cleanup and disposal | 1.00 |

### Kitchen Remodel - Ohio - Fair Mid-Range
- **Score:** 59.2 (expected (60, 90))
- **Verdict:** high (expected fair)
- **Items matched:** 9/9
- **Note:** Reasonable mid-range kitchen in a moderate-cost Midwest area.

| Line Item | Assessment | Score | Matched To | Confidence |
|-----------|------------|-------|-----------|------------|
| Stock cabinets | fair | 85 | cabinets | 0.85 |
| Laminate countertops | fair | 85 | countertops | 0.85 |
| Appliance package (mid-range) | fair_to_high | 69 | appliance package | 0.85 |
| Vinyl plank flooring | fair_to_high | 61 | flooring | 0.70 |
| Plumbing (sink and dishwasher) | fair | 85 | plumbing rough in and fixtures | 0.61 |
| Electrical work | fair_to_high | 66 | electrical work | 1.00 |
| Backsplash (ceramic tile) | excessive | 5 | components_backsplash_ceramic_tile_per_sq_ft | 0.85 |
| Demolition and cleanup | excessive | 5 | cleanup | 0.70 |
| Permits | fair_to_high | 52 | permits | 1.00 |


## All Tests — Line Item Analysis

### 1. ✅ Bathroom Remodel - Vermont - Mid-Range
Score: 68.7 | Verdict: fair | Region: northeast (×0.988) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Tile work - floor and walls | fair_to_high | 61 | tile work floor and walls |
| Plumbing rough-in and fixtures | fair | 85 | plumbing rough in and fixtures |
| Vanity and countertop | fair_to_high | 51 | vanity and countertop |
| Toilet installation | fair_to_high | 56 | toilet installation |
| Shower/tub installation | fair_to_high | 64 | shower tub installation |
| Electrical and lighting | fair_to_high | 69 | electrical and lighting |
| Drywall and painting | fair_to_high | 65 | drywall and painting |
| Permits and cleanup | fair_to_high | 57 | permits and cleanup |

**Recommendations:**
- Request exact material specs (brand, grade, model) for major material items before signing.
- Request exact material specs (brand, grade, model) for major material items before signing.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.

### 2. ✅ Kitchen Renovation - Texas - Overpriced
Score: 45.9 | Verdict: high | Region: southwest (×0.831) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Cabinets (semi-custom) | fair_to_high | 57 | cabinets |
| Countertops (quartz) | excessive | 17 | countertops |
| Appliance package | fair_to_high | 58 | appliance package |
| Flooring (tile) | excessive | 17 | flooring |
| Plumbing | fair_to_high | 61 | plumbing |
| Electrical work | high | 41 | electrical work |
| Backsplash | excessive | 17 | backsplash |
| Permits and fees | excessive | 18 | permits and fees |

**Recommendations:**
- Negotiate 'Countertops (quartz)' — currently $8,500, expected range is $1,496-$5,360
- Negotiate 'Flooring (tile)' — currently $4,500, expected range is $798-$2,992
- Negotiate 'Electrical work' — currently $3,500, expected range is $665-$3,324

### 3. ❌ Roof Replacement - California - Below Market
Score: 40.4 | Verdict: very_high | Region: west_coast (×1.19) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Asphalt shingles (architectural) | excessive | 5 | materials_asphalt_shingles_architectural_cost_per_square |
| Tear off and removal | fair_to_high | 61 | tear off and removal |
| Installation labor | fair_to_high | 60 | installation labor |
| Flashing and trim | high | 41 | flashing |
| Cleanup and disposal | excessive | 18 | cleanup and disposal |

**Missing standard items:** underlayment, drip edge, ridge caps

**Recommendations:**
- Negotiate 'Asphalt shingles (architectural)' — currently $3,500, expected range is $119-$214
- Negotiate 'Flashing and trim' — currently $1,000, expected range is $238-$952
- Negotiate 'Cleanup and disposal' — currently $1,000, expected range is $357-$714

### 4. ✅ HVAC Installation - Florida - Fair
Score: 74.5 | Verdict: fair | Region: southeast (×0.87) | Total analysis: fair

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| AC unit (3 ton, 16 SEER) | fair_to_high | 60 | ac unit |
| Installation labor | fair_to_high | 58 | ac installation |
| Thermostat (smart) | fair_to_high | 64 | thermostat |
| Ductwork modification | fair | 85 | ductwork |
| Permits and inspection | fair_to_high | 58 | permits |

**Missing standard items:** equipment

**Recommendations:**
- Request quotes for missing standard items: equipment. These are typically needed and may result in change orders.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.

### 5. ✅ Interior Painting - Midwest - High Side
Score: 68.6 | Verdict: fair | Region: midwest (×0.932) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Paint materials (premium) | high | 40 | paint materials |
| Paint labor (2000 sqft) | fair_to_high | 68 | paint labor |
| Prep work and repair | fair_to_high | 62 | prep work |

**Recommendations:**
- Negotiate 'Paint materials (premium)' — currently $1,500, expected range is $373-$1,398
- Request a detailed takeoff with quantities and unit pricing to replace round-number allowances.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.

### 6. ✅ Bathroom Remodel - California - High-End
Score: 47.8 | Verdict: high | Region: west_coast (×1.19) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Custom tile work (porcelain) | high | 32 | tile work |
| Plumbing - full rough-in | fair_to_high | 53 | plumbing rough in |
| Custom vanity (double sink) | excessive | 17 | vanity and sink |
| Frameless glass shower door | fair_to_high | 52 | glass shower door |
| Toilet (comfort height) | unmatched | 50 | none |
| Electrical and recessed lighting | fair_to_high | 60 | electrical and lighting |
| Heated floor system | unmatched | 50 | none |
| Drywall, painting, and finishing | fair_to_high | 56 | drywall and painting |
| Permits and project management | high | 36 | permits and cleanup |

**Missing standard items:** fixtures

**Recommendations:**
- Negotiate 'Custom tile work (porcelain)' — currently $8,500, expected range is $1,785-$7,140
- Negotiate 'Custom vanity (double sink)' — currently $4,500, expected range is $476-$2,975
- Negotiate 'Permits and project management' — currently $2,000, expected range is $238-$1,785

### 7. ❌ Kitchen Remodel - Ohio - Fair Mid-Range
Score: 59.2 | Verdict: high | Region: midwest (×0.923) | Total analysis: fair

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Stock cabinets | fair | 85 | cabinets |
| Laminate countertops | fair | 85 | countertops |
| Appliance package (mid-range) | fair_to_high | 69 | appliance package |
| Vinyl plank flooring | fair_to_high | 61 | flooring |
| Plumbing (sink and dishwasher) | fair | 85 | plumbing rough in and fixtures |
| Electrical work | fair_to_high | 66 | electrical work |
| Backsplash (ceramic tile) | excessive | 5 | components_backsplash_ceramic_tile_per_sq_ft |
| Demolition and cleanup | excessive | 5 | cleanup |
| Permits | fair_to_high | 52 | permits |

**Missing standard items:** appliances

**Recommendations:**
- Negotiate 'Backsplash (ceramic tile)' — currently $1,500, expected range is $7-$23
- Negotiate 'Demolition and cleanup' — currently $1,500, expected range is $92-$554
- Request quotes for missing standard items: appliances. These are typically needed and may result in change orders.

### 8. ✅ Roof Replacement - Florida - Suspiciously Low
Score: 46.2 | Verdict: high | Region: southeast (×0.87) | Total analysis: below_range

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Roofing materials | below_range | 80 | roofing materials |
| Labor | unmatched | 50 | none |
| Cleanup | fair_to_high | 51 | cleanup |

**Missing standard items:** shingles, underlayment, flashing, tear off, drip edge, ridge caps

**Recommendations:**
- Request quotes for missing standard items: shingles, underlayment, flashing, tear off, drip edge, ridge caps. These are typically needed and may result in change orders.
- Ask who is pulling permits, include permit fees in writing, and verify inspection milestones.
- Request exact material specs (brand, grade, model) for major material items before signing.

### 9. ✅ Deck Building - Massachusetts - Composite
Score: 48.2 | Verdict: high | Region: northeast (×1.12) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Composite decking material | fair_to_high | 56 | decking material |
| Framing lumber | unmatched | 50 | none |
| Railing (composite) | fair_to_high | 57 | railing |
| Labor - framing and installation | excessive | 15 | railing installation |
| Stairs and landing | fair_to_high | 61 | stairs |
| Permits and engineering | high | 37 | permits |

**Missing standard items:** fasteners

**Recommendations:**
- Negotiate 'Labor - framing and installation' — currently $8,000, expected range is $560-$4,480
- Negotiate 'Permits and engineering' — currently $1,500, expected range is $112-$1,344
- Request quotes for missing standard items: fasteners. These are typically needed and may result in change orders.

### 10. ✅ Window Replacement - New Jersey - 10 Windows
Score: 71.9 | Verdict: fair | Region: northeast (×1.168) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Vinyl double-hung windows (10) | fair | 85 | vinyl double hung windows |
| Installation labor | fair | 85 | installation labor |
| Trim and finishing | fair | 85 | trim and finishing |
| Disposal of old windows | suspiciously_low | 25 | windows |

**Recommendations:**
- Verify 'Disposal of old windows' — $500 is below typical range. Confirm scope, materials, and warranty.
- Request a detailed takeoff with quantities and unit pricing to replace round-number allowances.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.

### 11. ✅ Siding Replacement - Minnesota - Vinyl
Score: 66.7 | Verdict: fair | Region: midwest (×1.033) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Vinyl siding material | fair | 85 | siding material |
| Old siding removal | fair_to_high | 66 | old siding removal |
| Installation labor | fair_to_high | 69 | siding installation |
| Trim and accessories | fair_to_high | 65 | trim and accessories |
| Permits and cleanup | fair_to_high | 51 | permits and cleanup |

**Recommendations:**
- Request exact material specs (brand, grade, model) for major material items before signing.
- Request a detailed takeoff with quantities and unit pricing to replace round-number allowances.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.

### 12. ✅ HVAC Full System - New York - Fair
Score: 69.2 | Verdict: fair | Region: northeast (×1.38) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| AC unit (3.5 ton, 16 SEER) | unmatched | 50 | none |
| Gas furnace (80k BTU) | fair | 85 | furnace |
| Installation labor | fair_to_high | 50 | ac installation |
| Thermostat (Ecobee) | fair_to_high | 69 | thermostat |
| Ductwork modification | fair | 85 | ductwork |
| Permits and inspection | fair_to_high | 59 | permits |

**Missing standard items:** equipment

**Recommendations:**
- Request quotes for missing standard items: equipment. These are typically needed and may result in change orders.
- Request a detailed takeoff with quantities and unit pricing to replace round-number allowances.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.

### 13. ✅ Interior Painting - Georgia - Fair
Score: 75.5 | Verdict: fair | Region: southeast (×0.85) | Total analysis: excessive

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Paint materials | fair | 85 | paint materials |
| Paint labor | fair | 85 | paint labor |
| Prep work | fair | 85 | prep work |

**Recommendations:**
- Overall total is significantly above market rates. Strongly recommend getting multiple competing quotes.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.

### 14. ✅ Bathroom Remodel - Texas - Budget
Score: 76.8 | Verdict: fair | Region: southwest (×0.831) | Total analysis: fair

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Tile work (ceramic, basic) | fair | 85 | tile work |
| Plumbing fixtures (basic) | fair_to_high | 66 | plumbing fixtures |
| Vanity (stock 36-inch) | unmatched | 50 | none |
| Toilet | fair | 85 | toilet |
| Tub/shower surround | fair | 85 | shower tub installation |
| Electrical | fair | 85 | electrical |
| Drywall and paint | fair | 85 | drywall and painting |
| Cleanup | excessive | 17 | cleanup |

**Recommendations:**
- Negotiate 'Cleanup' — currently $750, expected range is $83-$499
- Request exact material specs (brand, grade, model) for major material items before signing.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.

### 15. ✅ Kitchen Remodel - Connecticut - Very High
Score: 42.8 | Verdict: very_high | Region: northeast (×1.092) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Custom cabinets | fair_to_high | 51 | cabinets |
| Quartz countertops | high | 38 | quartz countertops |
| High-end appliance package | fair_to_high | 52 | appliance package |
| Hardwood flooring | excessive | 17 | flooring |
| Plumbing | fair_to_high | 60 | plumbing |
| Electrical work | high | 42 | electrical work |
| Backsplash (glass tile) | excessive | 5 | components_backsplash_glass_tile_per_sq_ft |
| Permits and project management | excessive | 14 | permits and cleanup |

**Missing standard items:** appliances

**Recommendations:**
- Negotiate 'Quartz countertops' — currently $12,000, expected range is $3,276-$10,920
- Negotiate 'Hardwood flooring' — currently $6,000, expected range is $1,048-$3,931
- Negotiate 'Electrical work' — currently $4,500, expected range is $874-$4,368

### 16. ✅ Roof Replacement - Texas - Good Deal
Score: 70.1 | Verdict: fair | Region: southwest (×0.831) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Asphalt shingles | fair | 85 | shingles |
| Underlayment | fair | 85 | underlayment |
| Tear off and removal | fair_to_high | 69 | tear off and removal |
| Installation labor | fair_to_high | 63 | installation labor |
| Flashing | fair_to_high | 59 | flashing |
| Ridge caps and drip edge | fair_to_high | 63 | drip edge |
| Cleanup and disposal | high | 44 | cleanup and disposal |

**Recommendations:**
- Negotiate 'Cleanup and disposal' — currently $500, expected range is $249-$499
- Ask who is pulling permits, include permit fees in writing, and verify inspection milestones.
- Request exact material specs (brand, grade, model) for major material items before signing.

### 17. ✅ Electrical Panel Upgrade - Washington - Fair
Score: 54.1 | Verdict: high | Region: southeast (×0.94) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| 200-amp panel and breakers | unmatched | 50 | none |
| Installation labor | excessive | 5 | outlet installation |
| Permits and inspection | fair_to_high | 64 | permits |
| Materials and wiring | unmatched | 50 | none |

**Recommendations:**
- Negotiate 'Installation labor' — currently $2,200, expected range is $94-$329

### 18. ✅ Deck Building - Alabama - Budget
Score: 77.8 | Verdict: fair | Region: southeast (×0.87) | Total analysis: fair

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Pressure-treated lumber | unmatched | 50 | none |
| Concrete footings | unmatched | 50 | none |
| Deck framing and installation | fair_to_high | 67 | deck framing |
| Railing (wood) | fair | 85 | railing |
| Hardware and fasteners | unmatched | 50 | none |
| Permits | fair | 85 | permits |

**Missing standard items:** decking

**Recommendations:**
- Request quotes for missing standard items: decking. These are typically needed and may result in change orders.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.

### 19. ✅ Water Heater Install - Colorado - Fair
Score: 76.7 | Verdict: fair | Region: mountain (×0.9) | Total analysis: fair_to_high

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| 50-gallon water heater | fair | 85 | water heater |
| Installation labor | unmatched | 50 | none |
| Fittings and connections | unmatched | 50 | none |
| Disposal of old unit | unmatched | 50 | none |
| Permit | fair | 85 | permits |

**Missing standard items:** parts

**Recommendations:**
- Request quotes for missing standard items: parts. These are typically needed and may result in change orders.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.

### 20. ✅ Hardwood Flooring - Virginia - Fair
Score: 73.1 | Verdict: fair | Region: southeast (×1.006) | Total analysis: unknown

| Line Item | Assessment | Score | Matched To |
|-----------|------------|-------|-----------|
| Oak hardwood flooring material | fair_to_high | 67 | oak hardwood flooring material |
| Underlayment | fair | 85 | underlayment |
| Installation labor | fair_to_high | 64 | installation labor |
| Old floor removal | fair | 85 | old floor removal |
| Trim and transitions | fair_to_high | 67 | trim and transitions |
| Furniture moving and protection | fair_to_high | 63 | furniture moving and protection |
| Cleanup | fair | 85 | cleanup |

**Recommendations:**
- Request exact material specs (brand, grade, model) for major material items before signing.
- This quote appears to be within normal market range. Still worth getting one more comparison quote.


## Observations & Next Steps

### What's Working
- Project type resolution handles aliases well (kitchen renovation → kitchen_remodel)
- Regional multipliers are applied correctly
- Line item fuzzy matching catches most common descriptions
- Scoring correctly differentiates fair from overpriced quotes

### Areas for Improvement
- Per-unit vs per-project matching: Some model entries are per-sqft or per-square; need better detection of when a line item represents total cost vs unit cost
- Missing items detection is keyword-based and could use fuzzy matching
- The scoring weights may need tuning based on more real-world data
- Suspiciously low detection needs a dedicated code path for total-level analysis

### Recommended Next Steps
1. Collect real contractor quotes to validate against
2. Tune scoring weights based on expert review
3. Add per-project-size calibration (small vs medium vs large affects ranges)
4. Improve component aggregation for complex projects (kitchen, bath)
5. Add support for the 6 new models in new_models/ directory