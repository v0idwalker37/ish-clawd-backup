# Total-Only Quote Problem — Solution Design

## The Problem

**User Pain Point:** Many contractors provide quotes with itemized descriptions but only one total price:

```Example Quote from Contractor:
Kitchen Remodel Project
- Custom maple cabinets with soft-close hinges
- Granite countertops (Level 3)
- Tile backsplash
- Demolition and prep work
- Labor and installation

Total: $35,000
```

**Why This Sucks:**
- Can't identify which specific items are overpriced
- Less negotiation leverage (can't say "your cabinet price is 30% high")
- Less actionable insights for homeowner
- Still want to analyze these quotes — they're common!

---

## Solution: Hybrid AI Estimation with Transparency

**Approach:** Detect total-only quotes → AI generates estimated breakdown → Show with prominent disclaimer

### Phase 1: Detection (Parser)

**In `quote_parser_gemini.py`:**

```python
def detect_total_only_quote(parsed_data: dict) -> bool:
    """
    Detect if quote is total-only (no itemized costs).
    
    Returns True if:
    - Only 1-2 line items
    - All line items have $0 or same price as total
    - Descriptions present but no individual costs
    """
    items = parsed_data.get("line_items", [])
    total = parsed_data.get("total", 0)
    
    if len(items) <= 2:
        return True
    
    # Check if all items are $0 or match total
    non_zero_items = [i for i in items if i.get("quoted_price", 0) > 0]
    if len(non_zero_items) <= 1:
        return True
    
    # Check if one item matches total (probably "Project Total" line)
    for item in items:
        if abs(item.get("quoted_price", 0) - total) < 1:
            return True
    
    return False
```

### Phase 2: AI-Powered Breakdown

**New function:**

```python
async def generate_estimated_breakdown(
    project_type: str,
    location: str,
    descriptions: list[str],
    total: float,
) -> dict:
    """
    Use Gemini to estimate line item costs based on:
    - Project type
    - Location (regional pricing)
    - Description text
    - Industry standard percentages
    - Total budget
    
    Returns estimated line items with confidence levels.
    """
    
    prompt = f'''You are a construction cost estimator. Break down this total-only quote into estimated line item costs.

Project: {project_type}
Location: {location}
Total Budget: ${total:,.2f}

Items mentioned:
{chr(10).join(f"- {desc}" for desc in descriptions)}

Based on:
1. Typical cost percentages for {project_type} projects
2. Regional pricing in {location}
3. Industry standards and BLS labor rates

Provide estimated costs for each item. Use typical breakdowns:
- Materials: Usually 40-50% of total
- Labor: Usually 35-45% of total
- Overhead/profit: Usually 10-20% of total

Return JSON with estimated line items:
{{
  "line_items": [
    {{
      "item_name": "...",
      "description": "...",
      "quoted_price": 0.00,  // Per-unit price
      "quantity": 1,
      "unit": "item",
      "estimated_total": 0.00,  // This item's portion of total
      "confidence": "high|medium|low",
      "reasoning": "Based on typical X% of total for this item type"
    }}
  ],
  "methodology": "Brief explanation of estimation approach",
  "disclaimer": "These are estimates. Actual costs may vary. Request itemized quote for accuracy."
}}

Be conservative. If unsure, mark confidence as "low".
'''
    
    # Call Gemini
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    
    # Parse JSON
    result = json.loads(response.text)
    
    return result
```

### Phase 3: Frontend Handling

**In `QuoteForm.tsx` or `FileUpload.tsx`:**

```tsx
{parsedData.is_total_only_estimate && (
  <div className="bg-amber-50 border-l-4 border-amber-500 p-4 mb-6">
    <div className="flex items-start gap-3">
      <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
      <div>
        <h4 className="font-bold text-amber-900 mb-1">
          ⚠️ Estimated Breakdown
        </h4>
        <p className="text-amber-800 text-sm mb-2">
          This quote doesn't include itemized costs. We've estimated the breakdown 
          based on typical {projectType} projects in {location}.
        </p>
        <p className="text-amber-700 text-xs">
          <strong>For better analysis:</strong> Ask your contractor for an itemized 
          quote with individual costs for each item.
        </p>
      </div>
    </div>
  </div>
)}
```

**On report page:**

```tsx
{report.is_estimated && (
  <div className="card border-l-4 border-amber-400 bg-amber-50">
    <div className="flex items-start gap-4">
      <AlertCircle className="w-8 h-8 text-amber-600 flex-shrink-0" />
      <div>
        <h3 className="text-lg font-bold text-amber-900 mb-2">
          Estimated Line Item Breakdown
        </h3>
        <p className="text-amber-800 mb-3">
          Your contractor provided only a total price. We estimated individual 
          item costs based on:
        </p>
        <ul className="text-amber-700 text-sm space-y-1 mb-3">
          <li>✓ Typical cost breakdowns for {projectType} projects</li>
          <li>✓ Regional pricing in {location}</li>
          <li>✓ Bureau of Labor Statistics data</li>
          <li>✓ Industry standard percentages</li>
        </ul>
        <div className="bg-amber-100 border border-amber-300 rounded-lg p-3">
          <p className="text-amber-900 text-sm font-semibold">
            ⚠️ Important: These are estimates, not actual costs.
          </p>
          <p className="text-amber-800 text-xs mt-1">
            Request an itemized quote from your contractor for accurate 
            per-item analysis. This will give you much stronger negotiating power.
          </p>
        </div>
      </div>
    </div>
  </div>
)}
```

### Phase 4: Database Schema

**Add to `AnalysisReport` model:**

```python
is_estimated: Mapped[bool] = mapped_column(Boolean, default=False)
estimation_confidence: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # "high", "medium", "low"
estimation_methodology: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

**Migration:**

```bash
cd backend
alembic revision --autogenerate -m "add estimated breakdown fields"
alembic upgrade head
```

---

## Implementation Plan

### Step 1: Detection (30 min)
- [ ] Add `detect_total_only_quote()` to parser
- [ ] Test with sample total-only quotes
- [ ] Return flag in parsed_data

### Step 2: AI Breakdown (1 hour)
- [ ] Implement `generate_estimated_breakdown()` 
- [ ] Test with various project types
- [ ] Validate that estimates sum to total
- [ ] Tune prompt for accuracy

### Step 3: Backend Integration (30 min)
- [ ] Modify `parse-upload` endpoint to detect + estimate
- [ ] Add estimation fields to response
- [ ] Store `is_estimated` flag in database

### Step 4: Frontend Warnings (45 min)
- [ ] Add warning banner to upload success page
- [ ] Add prominent disclaimer to report page
- [ ] Show confidence levels for each item
- [ ] Add "Request Itemized Quote" CTA

### Step 5: Testing (30 min)
- [ ] Test with real total-only quotes
- [ ] Verify estimates are reasonable
- [ ] Check that warnings display correctly
- [ ] Verify PDF includes disclaimer

**Total Effort:** ~3-4 hours

---

## Example Estimations

### Kitchen Remodel ($35,000 total)

**Typical Breakdown:**
- Cabinets: 30-40% → $10,500-14,000
- Countertops: 15-20% → $5,250-7,000
- Appliances: 15-20% → $5,250-7,000
- Flooring: 7-10% → $2,450-3,500
- Backsplash: 5-8% → $1,750-2,800
- Labor: 25-30% → $8,750-10,500
- Overhead/Profit: 10-15% → $3,500-5,250

**AI Estimation Logic:**
1. Identify categories from descriptions
2. Apply industry standard percentages
3. Adjust for location (BLS regional multipliers)
4. Distribute remaining budget proportionally
5. Round to reasonable numbers ($10,437 → $10,500)

### Roof Replacement ($15,000 total)

**Typical Breakdown:**
- Shingles/Materials: 40-45% → $6,000-6,750
- Labor (tear-off + install): 35-40% → $5,250-6,000
- Disposal: 5-8% → $750-1,200
- Underlayment/ice shield: 8-12% → $1,200-1,800
- Permits: 2-3% → $300-450
- Overhead/Profit: 10-15% → $1,500-2,250

---

## Benefits

**For Users:**
- Can still analyze total-only quotes (don't lose these conversions)
- Get actionable insights even without itemization
- Educated on why itemized quotes are better
- Talking points for negotiation ("Cabinets typically run $X-Y")

**For UnGouge:**
- Handles real-world quote formats
- Reduces abandonment (don't reject quotes)
- Shows value even with limited data
- Educates users on best practices

**For Contractors:**
- Encourages better quoting practices
- Transparent about what homeowners can see
- May prompt more itemization industry-wide

---

## Risks & Mitigations

**Risk:** Users trust estimates too much
- **Mitigation:** Prominent warnings, conservative estimates, mark confidence

**Risk:** Estimates wildly inaccurate
- **Mitigation:** Test with real quotes, tune prompts, show ranges not single values

**Risk:** Legal liability ("You said cabinets cost $X but...")
- **Mitigation:** Disclaimers, ToS update, "estimates not guarantees"

**Risk:** Contractors see this as insulting
- **Mitigation:** Explain we're helping homeowners ask better questions

---

## Alternative: Simple Total Comparison

**If estimation is too complex, fallback:**

Just compare the total against:
- Average total for this project type in this location
- Fair range: Low-Average-High
- Show disclaimer: "For better analysis, request itemized quote"

**Pros:** Simpler, less risk
**Cons:** Less value, less differentiation

---

## Recommendation

**Implement Phase 1-2 first (detection + basic estimation)**
- Get it working with Gemini estimates
- Add warnings/disclaimers
- Ship and gather feedback

**Then iterate:**
- Refine estimation accuracy based on real quotes
- Add user feedback loop ("Were these estimates helpful?")
- Build database of typical breakdowns over time

**Timeline:** Can ship basic version in 1-2 days, refine over next week.

---

**Next Steps:**
1. Review this approach with Jason
2. If approved, implement detection first
3. Test with sample quotes
4. Deploy and iterate

