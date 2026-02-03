# ungouge.ai — Phase 4: Implementation Playbook
## Week-by-Week Build Checklist + Technical Guides
### February 2026

---

# WEEK-BY-WEEK BUILD CHECKLIST

## Week 1 (Feb 3-9): Foundation

### Business Setup
- [ ] **File Wyoming LLC** → wyomingagents.com or similar registered agent service (~$100 + $100 state fee)
  - Company name: "Ungouge LLC" or "Ungouge AI LLC"
  - Registered agent: Use a Wyoming service (don't use your home address)
  - Operating agreement: Single-member LLC, standard template
- [ ] **Get EIN** → irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online (free, immediate)
- [ ] **Open business bank account** → Mercury.com or Relay.app (free, startup-friendly)
- [ ] **Purchase domain** → ungouge.ai (if not owned)

### Account Setup
- [ ] **Bubble.io** → Sign up for Growth plan ($119/month)
  - Why Growth: Need API connector, custom domain, more capacity
- [ ] **Google Cloud Platform** → console.cloud.google.com
  - Enable Gemini API (Vertex AI or AI Studio)
  - Set up billing with $300 free credit (new accounts)
  - Generate API key
- [ ] **Stripe** → stripe.com
  - Business verification with EIN
  - Set up product: "Quote Analysis" - $19.99 one-time
- [ ] **Postmark** → postmarkapp.com
  - Verify domain for email delivery
  - Set up transactional email stream
- [ ] **Craftsman National Estimator Cloud** → craftsman-book.com ($13.99/month)
  - Sign up and explore the interface
  - **CRITICAL: Email Craftsman support asking about API access or data licensing for commercial use**
  - Draft email (AI will provide)

### Research
- [ ] **Google "is my contractor quote fair"** — screenshot page 1-3 results
- [ ] **Google "[kitchen/roof/hvac] cost in [your city]"** — note who ranks
- [ ] **Read 5 posts on r/homeimprovement** about contractor pricing frustrations

**Jason's hours this week: ~8 hours**

---

## Week 2 (Feb 10-16): Legal & Validation

### Legal
- [ ] **Find UPPA-aware attorney** → search your state bar referral + "insurance regulatory attorney"
  - Budget: $500-1,000 for a 1-hour consultation + document review
  - Share: Product description, sample report mockup, disclaimer language
  - Ask: "Can a consumer-facing tool that compares contractor quotes to published cost data be construed as public adjusting?"
- [ ] **Draft Terms of Service** (AI provides template)
- [ ] **Draft Privacy Policy** (AI provides template)
- [ ] **Draft report disclaimers** (AI provides template)

### Demand Validation
- [ ] **Post on r/homeimprovement:**
  - Title: "Would you pay $20 to know if your contractor's quote is fair?"
  - Body: Describe the concept, ask for feedback
  - DO NOT link to anything yet — just gauge reaction
- [ ] **Post on r/homeowners** (similar)
- [ ] **Ask 5 friends/family** who own homes: "When was the last time you got a contractor quote? Did you feel confident it was fair?"

### Design Prep
- [ ] **Review 3-5 Bubble.io templates** for simple landing pages
- [ ] **Sketch the user flow on paper:**
  1. Land on page → See value prop
  2. Click "Analyze My Quote" → Upload image
  3. Enter zip code + project type
  4. Pay $19.99 via Stripe
  5. Receive analysis via email (concierge: within 24h; automated: within 60 seconds)

**Jason's hours this week: ~6 hours**

---

## Week 3 (Feb 17-23): Build Concierge Landing Page

### Bubble.io Landing Page Build

**Page structure:**

```
┌─────────────────────────────────────────────┐
│  HEADER: Logo | "How it Works" | "Pricing"  │
├─────────────────────────────────────────────┤
│                                             │
│  HERO SECTION                               │
│  "Is Your Contractor Overcharging You?"     │
│  "Upload your quote. Get the truth."        │
│                                             │
│  [Upload Your Quote — $19.99] ← CTA button │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  HOW IT WORKS (3 steps)                     │
│  📸 Upload  →  🤖 We Analyze  →  📊 You Know│
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  WHAT YOU GET                               │
│  ✓ Line-by-line fairness analysis           │
│  ✓ Location-adjusted cost comparison        │
│  ✓ Specific items that seem high/low        │
│  ✓ Questions to ask your contractor         │
│  ✓ Data sources cited                       │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  TRUST SIGNALS                              │
│  "Powered by Craftsman National Estimator"  │
│  "Used by X homeowners" (add after launch)  │
│  Money-back guarantee badge                 │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  FAQ (5-6 questions)                        │
│                                             │
├─────────────────────────────────────────────┤
│  FOOTER: Legal links, disclaimer            │
└─────────────────────────────────────────────┘
```

### Bubble.io Step-by-Step

1. **Create new Bubble app** → "ungouge"
2. **Install plugins:**
   - Stripe.js (for payments)
   - File Uploader (for quote images)
   - API Connector (for Gemini, later)
   - Postmark (for email delivery)
3. **Set up custom domain** → ungouge.ai pointing to Bubble
4. **Build index page** following wireframe above
5. **Build upload flow page:**
   - File upload element (accept: .jpg, .png, .pdf, .heic)
   - Input: Zip code (text, 5 digits)
   - Dropdown: Project type (from your trade list)
   - Input: Email address
   - Button: "Analyze My Quote — $19.99"
6. **Stripe Checkout integration:**
   - On button click → Create Stripe Checkout Session → Redirect
   - On success → Save order to Bubble database
   - On cancel → Return to upload page
7. **Database setup:**
   - Data type: "Analysis"
   - Fields: email, zip_code, project_type, quote_image (file), payment_id, status (pending/complete), created_date, report_text
8. **Admin page** (for Jason):
   - List of pending analyses
   - View uploaded quote image
   - Text area to write analysis
   - "Send Report" button → triggers Postmark email

**Jason's hours this week: ~10 hours**

---

## Week 4 (Feb 24-Mar 2): Polish & Soft Launch Concierge

### Finalize
- [ ] **Test full payment flow** (use Stripe test mode)
- [ ] **Test file upload** with various quote formats (phone photos, PDFs, screenshots)
- [ ] **Set up Postmark email template** for analysis reports
  - Subject: "Your ungouge.ai Quote Analysis is Ready"
  - Clean, professional HTML template with analysis results
- [ ] **Add Google Analytics** to Bubble site
- [ ] **Set up Google Search Console** → verify domain
- [ ] **Write FAQ content** (AI provides, Jason reviews)
- [ ] **Add Terms of Service and Privacy Policy pages**

### Soft Launch
- [ ] **Switch Stripe to live mode**
- [ ] **Send landing page to 5-10 friends/family** for feedback
- [ ] **Post update on Reddit** (if initial validation post went well): "I built the tool — first 10 analyses are $9.99"
- [ ] **Submit sitemap to Google Search Console**

**Jason's hours this week: ~8 hours**

---

## Weeks 5-8 (March): Concierge Operations

### Per-Analysis Workflow (Manual)

**For each paid analysis (~30-60 minutes):**

1. **Receive notification** (email or Bubble admin dashboard)
2. **Open the uploaded quote image** in a new tab
3. **Open Craftsman National Estimator Cloud** → select trade → enter zip code
4. **Line by line, compare the quote to Craftsman data:**
   - Material costs: Quote price vs. Craftsman published cost
   - Labor costs: Quote price vs. Craftsman labor rates
   - Note: Craftsman gives national average; adjust for local market (built into their zip code tool)
5. **Feed quote image + Craftsman data into Gemini** via AI Studio (manual):
   - Prompt: [See Prompt Engineering section below]
   - Gemini produces draft analysis
6. **Review and edit Gemini's output** for accuracy
7. **Paste final analysis into admin dashboard**
8. **Click "Send Report"** → customer receives email

### Target: 20-50 analyses in March
- At 45 min average: 15-37 hours of analysis work
- Revenue: $400-$1,000
- **Purpose:** Validate demand, refine analysis quality, build prompt templates

---

## Weeks 9-16 (April-May): Automate the MVP

### Gemini API Integration in Bubble

**Step 1: Set up API Connector plugin**
1. Bubble Editor → Plugins → API Connector
2. Add new API: "Gemini"
3. Authentication: API Key (header)
4. Base URL: `https://generativelanguage.googleapis.com/v1beta`

**Step 2: Create the analysis endpoint**
- Endpoint: `POST /models/gemini-1.5-pro:generateContent`
- Headers:
  - `Content-Type: application/json`
  - `x-goog-api-key: [YOUR_API_KEY]`
- Body (dynamic):
```json
{
  "contents": [{
    "parts": [
      {"text": "[SYSTEM_PROMPT + CRAFTSMAN_DATA + USER_CONTEXT]"},
      {"inline_data": {
        "mime_type": "image/jpeg",
        "data": "[BASE64_ENCODED_QUOTE_IMAGE]"
      }}
    ]
  }],
  "generationConfig": {
    "temperature": 0.3,
    "maxOutputTokens": 4096
  }
}
```

**Step 3: Build the automation workflow in Bubble**
1. User uploads quote + pays → Bubble saves to database
2. Backend workflow triggers:
   a. Fetch Craftsman data for zip code + trade (if API available; otherwise use pre-loaded data)
   b. Call Gemini API with quote image + Craftsman context
   c. Parse Gemini response
   d. Save analysis to database
   e. Send email via Postmark with formatted report
3. Status updates: pending → processing → complete
4. Error handling: If Gemini fails, flag for manual review

**Step 4: Test with 20 real quotes from concierge phase**
- Compare automated results to your manual analyses
- Adjust prompts until automated quality matches manual

---

## PROMPT ENGINEERING GUIDE

### Master Analysis Prompt (v1)

```
You are a construction cost analysis expert. A homeowner has uploaded a contractor's quote for review.

CONTEXT:
- Location: [ZIP_CODE] ([CITY, STATE])
- Project type: [PROJECT_TYPE]
- Fair market cost data for this location (from Craftsman National Estimator):
[CRAFTSMAN_DATA_FOR_THIS_TRADE_AND_LOCATION]

INSTRUCTIONS:
1. Extract every line item from the uploaded quote image (OCR)
2. For each line item, compare the quoted price to the fair market range from the cost data
3. Flag items that are:
   - 🟢 FAIR (within 15% of market rate)
   - 🟡 SLIGHTLY HIGH (15-30% above market)
   - 🔴 SIGNIFICANTLY HIGH (>30% above market)
   - ⚪ UNABLE TO VERIFY (not in cost database)
4. Calculate total quote vs. estimated fair market total
5. Identify any missing items that are typically included in this type of project
6. Provide 3-5 specific questions the homeowner should ask the contractor

OUTPUT FORMAT:
## Quote Analysis Summary
**Project:** [type]
**Location:** [city, state]
**Quoted Total:** $[amount]
**Estimated Fair Market Range:** $[low] - $[high]
**Overall Assessment:** [Fair / Slightly High / Significantly High]

## Line-by-Line Analysis
| Line Item | Quoted Price | Fair Market Range | Status |
|-----------|-------------|-------------------|--------|
[table rows]

## Items to Discuss with Your Contractor
[numbered list of specific, actionable questions]

## Important Notes
[any caveats about the analysis]

IMPORTANT DISCLAIMERS TO INCLUDE:
- This analysis is for educational and market research purposes only
- Cost data represents published averages adjusted for your location
- Actual costs may vary based on project complexity, material choices, and market conditions
- This is not a substitute for professional advice
```

### Prompt Optimization Tips
- **Temperature: 0.3** (low = more consistent, less creative)
- **Always include location context** — costs vary 30-50% by metro
- **Include specific Craftsman data** in the prompt rather than asking Gemini to "look up" costs
- **Test with 20+ real quotes** before going live
- **Version your prompts** — save each iteration with a date

---

## pSEO IMPLEMENTATION GUIDE

### Database Structure (Bubble)

**Data Type: "CityTrade"**
| Field | Type | Example |
|-------|------|---------|
| city | text | "Austin" |
| state | text | "TX" |
| zip_codes | text | "78701, 78702, ..." |
| trade | text | "Kitchen Remodel" |
| slug | text | "kitchen-remodel-cost-austin-tx" |
| cost_low | number | 15000 |
| cost_high | number | 45000 |
| cost_average | number | 28000 |
| labor_pct | number | 35 |
| material_pct | number | 55 |
| common_items | text (JSON) | "[{item, cost_range}]" |
| content_body | text | "[AI-generated unique content]" |
| meta_title | text | "Kitchen Remodel Cost in Austin, TX (2026)" |
| meta_desc | text | "Average kitchen remodel in Austin costs..." |

### Dynamic Page Template (Bubble)

URL structure: `ungouge.ai/costs/[slug]`

**Page template:**
```
H1: How Much Does a [Trade] Cost in [City], [State]?

Intro paragraph (unique per page, AI-generated)

## Average Cost Breakdown
[Data table from CityTrade record]

## What's Included in a Typical [Trade] Quote
[Common line items with cost ranges]

## How to Know If Your Quote Is Fair
[Educational content]

## CTA: Got a [Trade] Quote in [City]?
Upload it now for instant analysis — $19.99
[Upload Button]

## Related Costs in [City]
[Links to other trades in same city]

## [Trade] Costs in Nearby Cities  
[Links to same trade in nearby cities]
```

### Content Generation Workflow

1. **AI generates the 25,000 CityTrade records** with unique content per page
2. **Upload to Bubble via CSV** or Bulk API
3. **Configure dynamic page** in Bubble pointing to CityTrade data type
4. **Generate sitemap** and submit to Google Search Console
5. **Monitor indexing** — expect 3-6 months for full indexing of 25K pages

### Internal Linking Strategy
- Every city page links to other trades in that city
- Every trade page links to that trade in nearby cities
- All pages link to the homepage CTA
- Blog posts link to relevant pSEO pages
- Creates a dense link web that Google loves

---

## LAUNCH DAY RUNBOOK

### T-7 Days (Pre-Launch)
- [ ] Final end-to-end test: upload → pay → receive analysis email
- [ ] Test with 5 different quote formats (handwritten, typed, PDF, photo)
- [ ] Test on mobile (iPhone + Android)
- [ ] Verify Stripe is in live mode
- [ ] Verify Postmark is sending from ungouge.ai domain
- [ ] Check all disclaimers are present
- [ ] Prepare launch posts for Reddit, social

### T-1 Day
- [ ] Check Bubble app status — no issues
- [ ] Check Gemini API quota — sufficient
- [ ] Check Stripe dashboard — live and ready
- [ ] Prepare personal email to friends/family: "I built a thing"
- [ ] Deep breath 🧘

### Launch Day
- [ ] Flip any "coming soon" flags to live
- [ ] Post on r/homeimprovement (follow sub rules)
- [ ] Post on r/homeowners
- [ ] Post on personal social media
- [ ] Send email to friends/family
- [ ] Monitor for the first 2-3 hours:
  - Bubble logs for errors
  - Stripe dashboard for payments
  - Email inbox for customer questions
  - Gemini API usage for anomalies

### T+1 Day
- [ ] Review all analyses from Day 1 for quality
- [ ] Respond to any customer emails
- [ ] Check Reddit posts for comments/questions
- [ ] Log any bugs or issues
- [ ] Celebrate 🎉 (even if only 1 sale)

### T+7 Days
- [ ] Review first week metrics
- [ ] Send follow-up email to all customers: "How was your experience?"
- [ ] Adjust prompts based on any accuracy issues
- [ ] Plan Week 2 marketing activities

---

# QUICK REFERENCE: ALL ACCOUNTS NEEDED

| Service | URL | Cost | Purpose |
|---------|-----|------|---------|
| Wyoming LLC | wyomingagents.com | ~$200 | Business entity |
| Mercury Bank | mercury.com | Free | Business banking |
| Bubble.io | bubble.io | $119/mo | App platform |
| Google Cloud | console.cloud.google.com | ~$10/mo | Gemini API |
| Stripe | stripe.com | 2.9% + $0.30/tx | Payments |
| Postmark | postmarkapp.com | $15/mo | Transactional email |
| Craftsman Cloud | craftsman-book.com | $13.99/mo | Cost data |
| Google Search Console | search.google.com/search-console | Free | SEO monitoring |
| Google Analytics | analytics.google.com | Free | Traffic analytics |
| Namecheap/Cloudflare | namecheap.com | ~$15/yr | Domain |

**Total monthly operating cost: ~$175/month**
**Total startup cost: ~$500 (LLC + first month of tools)**

---

*End of Phase 4: Implementation Playbook*
*End of Complete Business Plan Package*

---

# WHAT'S NEXT

Jason should:
1. **Read all 4 documents** (this takes ~1 hour)
2. **Start Week 1 checklist TODAY** (LLC, accounts, Craftsman inquiry)
3. **Ask AI to draft:** Craftsman licensing inquiry email, Reddit validation post, email templates, Terms of Service
4. **Set a weekly check-in** to track progress against the timeline

The plan is designed so that **no single week requires more than 10-12 hours of Jason's time**, keeping well within the 15-20h/week budget.

**The most important thing Jason can do right now: Contact Craftsman about data access.** Everything else can proceed in parallel, but the Craftsman data question is the critical path dependency.

Good luck, Jason. Go ungouge the world. 🎯
