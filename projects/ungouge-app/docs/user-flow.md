# UnGouge.ai — User Flow

## Happy Path (Manual Entry)

```
1. LANDING PAGE (ungouge.ai)
   ├── Hero: "Know if your contractor's quote is fair. $19.99."
   ├── CTA: "Analyze My Quote" → /analyze
   └── Social proof: "X quotes analyzed" counter
   
2. QUOTE INPUT (/analyze)
   ├── Step 1: Select project type (14 categories, visual cards)
   ├── Step 2: Enter details
   │   ├── Project size/scope (pre-filled ranges)
   │   ├── Location (ZIP code → regional multiplier)
   │   └── Quality tier: Budget / Mid-Range / Premium
   ├── Step 3: Enter line items from quote
   │   ├── Add rows: Description + Amount
   │   ├── OR upload quote (photo/PDF) → AI extraction
   │   └── Total auto-calculated
   └── Step 4: Review & Pay
       ├── Summary of what they entered
       ├── "Your report will include: [preview list]"
       └── Stripe Checkout ($19.99)
   
3. PROCESSING (/processing)
   ├── Loading animation: "Analyzing your quote..."
   ├── Progress indicators:
   │   ├── ✅ Quote received
   │   ├── ⏳ Comparing to market data...
   │   ├── ⏳ Checking for red flags...
   │   └── ⏳ Generating report...
   └── ~10-30 seconds for AI analysis
   
4. REPORT (/report/{id})
   ├── Header: Overall Score (0-100 gauge)
   │   ├── 80-100: "✅ Fair Price" (green)
   │   ├── 60-79: "⚠️ Slightly High" (yellow)  
   │   ├── 40-59: "🔶 Above Market" (orange)
   │   └── 0-39: "🚩 Significantly Overpriced" (red)
   │
   ├── Section 1: Cost Breakdown
   │   ├── Table: Their Price vs Market Range
   │   ├── Each line item: ✅ Fair / ⚠️ High / 🚩 Red Flag
   │   └── Materials vs Labor split comparison
   │
   ├── Section 2: Regional Context
   │   ├── "In [region], this type of project typically costs..."
   │   ├── Regional multiplier explanation
   │   └── How their quote compares to local market
   │
   ├── Section 3: Red Flags & Alerts
   │   ├── Missing standard items (things they should have quoted)
   │   ├── Suspiciously high line items
   │   ├── Common upsells flagged
   │   └── Vague descriptions that need clarification
   │
   ├── Section 4: Recommendations
   │   ├── "Ask your contractor about..."
   │   ├── "Consider getting a second quote for..."
   │   ├── DIY potential for specific items
   │   └── Quality tier explanation
   │
   ├── Section 5: What a Fair Quote Looks Like
   │   ├── Expected cost breakdown for this project
   │   ├── Materials list with typical prices
   │   └── Labor hours estimate
   │
   └── Actions:
       ├── 📄 Download PDF Report
       ├── 📧 Email Report
       ├── 🔗 Share Link (read-only, expires 30 days)
       └── 🔄 Analyze Another Quote (-20% returning customer?)
```

## Upload Path (Photo/PDF)

```
2b. UPLOAD FLOW (/analyze?mode=upload)
    ├── Drag & drop or camera capture
    ├── Accepted: JPG, PNG, PDF
    ├── AI extraction (Gemini Vision):
    │   ├── Detect project type
    │   ├── Extract line items + amounts
    │   ├── Extract contractor info
    │   └── Extract location (if on quote)
    ├── User confirms/edits extracted data
    └── Continues to Step 4 (Review & Pay)
```

## Error States
- Invalid ZIP code → "Enter a valid US ZIP code"
- No line items → "Add at least one line item from your quote"
- Upload failed → "We couldn't read that file. Try manual entry."
- Payment failed → "Payment didn't go through. Try another card."
- Analysis error → "Something went wrong. You won't be charged." + support email

## Conversion Optimization
- Show sample report on landing page (anonymized)
- "See what you'll get" preview before payment
- Trust badges: "No lead gen", "No contractor referrals", "Data stays private"
- Money-back guarantee: "Not useful? Email us for a refund."
- Blog posts link to /analyze with pre-selected project type
