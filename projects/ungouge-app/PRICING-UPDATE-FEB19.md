# Pricing Update: $19.99 → $9.99 Early Adopter Pricing

**Date:** February 19, 2026
**Status:** Backend complete, Frontend in progress

## Strategy

Launch at $9.99 to build data moat quickly:
- Early Adopter Pricing (normally $19.99)
- Grandfather clause: early users keep $9.99 pricing
- Plan to increase to $14.99 (Month 6), then $19.99 (Month 9)
- Free resubmit policy: total-only quotes can resubmit itemized within 90 days for free

## Backend Changes (✅ COMPLETE)

### Files Modified:
1. **backend/routers/payments.py**
   - Updated all `1999` → `999` (4 locations)
   - Updated docstrings to reflect $9.99

2. **backend/services/payment.py**
   - `REPORT_PRICE_CENTS = 999` (was 1999)
   - Updated all docstrings

3. **backend/alembic/versions/20260219_0004_add_resubmit_tracking.py** (NEW)
   - Added `original_quote_id` field to quotes table
   - Added `resubmit_eligible_until` field (90-day window)
   - Foreign key constraint + index

4. **backend/models/database.py**
   - Added two new fields to Quote model:
     ```python
     original_quote_id: Mapped[Optional[str]]
     resubmit_eligible_until: Mapped[Optional[datetime]]
     ```

### Deployment Steps:
```bash
# Run migration
cd backend
alembic upgrade head

# Deploy to Cloud Run
gcloud builds submit --config=cloudbuild.yaml
```

### Stripe Update Required:
- Create new $9.99 price in Stripe dashboard
- Update price ID in environment variables (or keep using inline price_data)

## Frontend Changes (🔄 IN PROGRESS)

### Completed:
1. ✅ **QuoteForm.tsx**
   - Updated payment summary: "$9.99" with "$19.99" strikethrough
   - Added "Early Adopter Pricing" label
   - Updated button text

### Remaining Files to Update:

**High Priority (User-Facing):**
1. **ChatWidget.tsx** - FAQ answers mentioning price
2. **HomePageContent.tsx** - Multiple price references on landing page
3. **app/page.tsx** - Homepage metadata
4. **app/pricing/page.tsx** - Pricing page (main pricing display)
5. **app/support/page.tsx** - Support FAQs

**Medium Priority (SEO/Metadata):**
6. **lib/seo.ts** - SEO metadata (price: '9.99')
7. **app/layout.tsx** - Global metadata
8. **app/opengraph-image.tsx** - OG image text

**Low Priority (Legal):**
9. **app/terms/page.tsx** - Terms of service pricing references

### Messaging Template:

**Primary:** `$9.99`
**With context:** `$9.99 (Early Adopter Pricing)`
**Full explanation:** `$9.99 Early Adopter Pricing (normally $19.99)`
**Strikethrough style:**
```tsx
<div className="text-2xl font-bold text-primary-600">$9.99</div>
<div className="text-xs text-gray-500 line-through">$19.99</div>
```

## Free Resubmit Policy (🔜 TODO)

### Logic Needed:
1. **At quote submission:** If original was total-only (is_estimated=true), set `resubmit_eligible_until = now() + 90 days`
2. **At upload:** Check if user has eligible resubmit for same project+location within 90 days
3. **At checkout:** If resubmit eligible, skip payment → mark as paid → generate report
4. **In report email:** Mention free resubmit policy for total-only quotes

### Files to Modify:
- `backend/routers/quotes.py` - Detection logic at submission
- `backend/routers/payments.py` - Free checkout bypass
- `frontend/src/components/QuoteForm.tsx` - Show "Free Resubmit" badge if eligible
- Email templates - Add resubmit messaging

## Testing Checklist

### Backend:
- [ ] Run migration successfully
- [ ] Create test checkout → verify $9.99 in Stripe
- [ ] Complete payment → verify report generation
- [ ] Check receipt email shows "$9.99"

### Frontend:
- [ ] All pages show $9.99 (not $19.99)
- [ ] "Early Adopter Pricing" messaging visible
- [ ] Strikethrough $19.99 shows on key pages
- [ ] No broken layouts from price changes

### End-to-End:
- [ ] Upload quote → see $9.99 in payment summary
- [ ] Complete Stripe checkout → charge is $9.99
- [ ] Receive email with correct pricing
- [ ] PDF report generated successfully

## Rollback Plan

If issues arise:
1. Revert backend: `git revert <commit>` + redeploy
2. Revert frontend: `git revert <commit>` + `vercel --prod`
3. Stripe: Old price IDs still exist, switch back in env vars

## Next Steps

1. **Jason approval** - Confirm $9.99 strategy before deploying
2. **Complete frontend updates** - All price references
3. **Run migration** - `alembic upgrade head`
4. **Deploy backend** - Cloud Run
5. **Deploy frontend** - Vercel
6. **Test end-to-end** - Full payment flow
7. **Implement free resubmit logic** - Phase 2 (can deploy after pricing)

---

**Current Status:** Backend ready to deploy, Frontend ~50% complete.
**Estimated completion:** 30 more minutes for frontend updates.
