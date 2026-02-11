# Cost Model Validation Checklist

**Run this checklist after both RSMeans + Craftsman books are processed and web scrape data is integrated.**

## Phase 1: Data Processing & Cross-Reference
- [ ] Process all data sources simultaneously (RSMeans, Craftsman, BLS, Census, HomeAdvisor, Remodeling Mag, State prevailing wages)
- [ ] Cross-reference aggressively — require 3+ sources to agree before accepting a baseline
- [ ] Flag any data point where sources disagree by >30%
- [ ] Run statistical analysis to catch outliers (values >2 standard deviations from median)
- [ ] Generate test cases to validate internal consistency:
  - Does kitchen model's plumbing costs match standalone plumbing model?
  - Does bathroom model's electrical costs match standalone electrical model?
  - Do regional multipliers apply consistently across all models?
  - Are crew labor rates consistent with BLS data for each trade?

## Phase 2: Synthetic Testing
- [ ] Generate 10,000 synthetic quotes across all 30 project types
- [ ] Vary: project size, location (50+ cities), material quality (budget/mid/premium)
- [ ] Check that model produces reasonable ranges (no negative costs, no 10x outliers)
- [ ] Validate that regional multipliers work correctly (LA > Boise, NYC > rural NY)
- [ ] Test edge cases: smallest viable project, largest typical project
- [ ] Catch math errors and logic bugs

## Phase 3: Real-World Testing (Automated)
- [ ] **Find 10-20 real contractor quotes online** from:
  - Yelp reviews (homeowners often mention dollar amounts)
  - Angi/HomeAdvisor quote screenshots (users post these to forums)
  - Reddit r/HomeImprovement (quote validation posts)
  - ContractorTalk forums (contractors sharing typical pricing)
  - BiggerPockets forums (rental property quotes)
  - YouTube comments (DIY channels, homeowners share costs)
- [ ] Run found quotes through our models
- [ ] Compare our analysis to what actually happened
- [ ] Document where we're obviously wrong
- [ ] Adjust assumptions and regional multipliers based on findings

## Phase 4: Real-World Testing (Manual Backup)
- [ ] If automated search doesn't find enough quotes, Jason manually collects 5-10 examples
- [ ] Same validation process as Phase 3

## Success Criteria
- ✅ 95%+ of synthetic tests produce reasonable ranges
- ✅ Real-world quotes: our estimate within ±30% of actual quote in 80%+ of cases
- ✅ No major internal consistency errors between models
- ✅ Regional multipliers validated across 10+ markets

## Notes
- This validation should happen BEFORE launch, not after
- Budget 2-3 days of work (mostly automated, Jason reviews flagged items)
- Accuracy target: 70-80% (good enough to launch)
- Plan for iteration based on first 100 customer reports
