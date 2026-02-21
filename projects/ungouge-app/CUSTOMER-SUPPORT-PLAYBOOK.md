# Customer Support Playbook

## Quick Reference

**Support channels:**
- Email: human@ungouge.ai
- Chat: Zedd AI widget (escalates to human)
- Response time goal: <24 hours (usually <6 hours)

**Common scenarios:**
1. Report accuracy questioned
2. Refund request
3. Upload issues (file format, size)
4. Payment failed / charge disputed
5. "My contractor says you're wrong"
6. Feature request
7. Technical bug
8. Privacy / data concerns

---

## Scenario 1: Report Accuracy Questioned

**Customer email:**
> "Your report says my quote is 20% high, but I got 3 other quotes and they were all similar. How can they all be overpriced?"

**Response template:**

Hi [Name],

Great question. This is actually more common than you'd think.

**Why multiple quotes can all be overpriced:**

1. **Regional pricing coordination** — In smaller markets or specialized trades, contractors often know each other's typical rates. Not collusion (illegal), just market awareness.

2. **Similar markups** — If all contractors use standard markup percentages (even if those percentages are high), you'll get similar quotes that are all inflated.

3. **Material cost inflation** — If contractors are all buying from the same suppliers and applying 60-80% markups (when 20-40% is standard), they'll all quote similar high prices.

**Your options:**

✅ **Use our analysis to negotiate** — Show the contractor our breakdown: "Your material markup is 80%. Industry standard is 20-40%. Can we adjust that?"

✅ **Get quotes from different types of contractors** — Try a smaller, independent contractor vs large firms. Different overhead = different pricing.

✅ **DIY some components** — Handle demolition yourself, source materials directly, hire contractor for labor only.

**Our accuracy:**

We're currently at 65-75% accuracy against verified market data. We're continuously improving, but we're not perfect. If you genuinely believe our analysis is off, let me know specifics and I'll review it personally.

**Want a second opinion?** Reply with the other quotes and I'll compare them all.

Best,  
Jason

---

## Scenario 2: Refund Request (Unhappy Customer)

**Customer email:**
> "This report didn't help me at all. I want a refund."

**Response template:**

Hi [Name],

I'm sorry the report didn't meet your expectations.

**No problem—we'll refund you.**

Can you help me understand what was missing or unclear? This feedback helps us improve for other customers.

Specifically:
- Was the analysis too vague?
- Did you need more detail on specific line items?
- Was the recommendation unclear?
- Something else?

**Your refund will process within 2-3 business days** to the original payment method.

Again, sorry we didn't deliver value this time. If you have another quote in the future and want to give us another shot, reach out—I'll personally review it before sending the report.

Best,  
Jason

**Internal note:** Issue refund immediately. Don't argue. Learn from feedback. Mark user as "Refunded - Feedback: [reason]" in database.

---

## Scenario 3: Upload Issues (File format, size, quality)

**Customer email:**
> "I keep trying to upload my quote but it says 'Upload failed.' Help!"

**Response template:**

Hi [Name],

Let's troubleshoot this.

**Common issues:**

1. **File size too large** — Our limit is 10MB. If your PDF/image is bigger, try compressing it (tinypng.com for images, smallpdf.com for PDFs)

2. **Unsupported format** — We accept PDF, JPG, PNG, HEIC. If you have a Word doc or Excel file, convert to PDF first.

3. **Browser issue** — Try a different browser (Chrome usually works best). Clear cache if still having issues.

4. **Slow connection** — Large files on slow connections can timeout. Try uploading from WiFi instead of cellular.

**Alternative: Email it to me**

Can't get it to upload? Just reply to this email with the quote attached. I'll upload it manually and start your analysis.

Let me know if none of these work!

Jason

**Internal action:** If user emails quote, manually upload via admin panel and mark as "Manual Upload - Customer Assistance"

---

## Scenario 4: Payment Failed / Charge Disputed

**Customer email:**
> "My card was declined but I see a charge. What's going on?"

**Response template:**

Hi [Name],

Sorry for the confusion!

**What likely happened:**

Stripe (our payment processor) placed a **temporary authorization hold** on your card when you initiated checkout. This shows as a "pending" charge but isn't actually captured.

If payment failed, that hold will drop off in 1-3 business days (depending on your bank).

**To complete your order:**

1. Try a different payment method (different card, Apple Pay, etc.)
2. Or contact your bank to authorize the charge (sometimes they block it as fraud protection)

**If you were actually charged:**

Check your email for a receipt from payments@ungouge.ai. If you have one, you were charged and your report is being generated.

If you don't have a receipt but see a permanent charge (not pending), reply and I'll investigate with Stripe support.

Let me know!  
Jason

**Internal action:** Check Stripe dashboard for payment intent status. If failed, confirm hold. If succeeded, confirm report was generated.

---

## Scenario 5: "My Contractor Says You're Wrong"

**Customer email:**
> "I showed your report to my contractor and he says your labor rates are outdated and material costs have gone up. Who's right?"

**Response template:**

Hi [Name],

This is a fair question. Let's dig into it.

**Our data sources (as of 2026):**
- RSMeans 2026 cost data (updated quarterly)
- Craftsman National Estimator 2026
- Real-time market research + submitted quotes

**Where contractors push back:**

1. **"Material costs have gone up"** — True, but by how much? If they claim 50% increase in the last 6 months, ask for receipts. 10-15% annual increase is normal. 50%+ is suspicious.

2. **"Labor rates are higher in our area"** — Possibly true for micro-markets (wealthy suburbs vs rural). Ask: "What's your hourly rate?" Compare it to our regional data. If it's 20%+ higher, ask why.

3. **"This is specialized work"** — Sometimes legitimate. Custom work, difficult access, or rare skills command premiums. But "specialized" shouldn't mean 100% markup across the board.

**What to do:**

✅ **Ask for specifics** — "Which line items are you disputing?" Don't let them dismiss the whole report vaguely.

✅ **Request proof** — "Can you show me your supplier invoice for the materials?" (They won't always provide it, but asking shows you're informed.)

✅ **Get a second opinion** — If they insist we're wrong, get another contractor's quote and compare.

**Bottom line:**

Our analysis is data-driven, but not perfect. Contractors have more granular, real-time info. A good contractor will explain their pricing—not just dismiss your questions.

Want me to review the contractor's specific objections? Reply with what they said and I'll give you my take.

Jason

---

## Scenario 6: Feature Request

**Customer email:**
> "Can you add a feature to compare multiple quotes side-by-side?"

**Response template:**

Hi [Name],

Love this idea! Side-by-side quote comparison is on our roadmap.

**Current workaround:**

Submit each quote separately ($19.99 each). Once analyzed, you can open the reports side-by-side in different browser tabs and compare.

**Future plan:**

We're building:
- Multi-quote upload (submit 2-5 quotes at once)
- Comparison dashboard (see all quotes in one view)
- Discount for bulk submissions ($50 for 3 quotes vs $60 individually)

**ETA:** Targeting Q2 2026 (April-June)

Want early access when it launches? I'll add you to the beta tester list.

Thanks for the feedback!  
Jason

**Internal action:** Add feature request to roadmap. Add user to "Beta Testers" list.

---

## Scenario 7: Technical Bug

**Customer email:**
> "My report page shows a broken image / won't load / has weird formatting."

**Response template:**

Hi [Name],

Sorry you're running into this! Let me get it fixed.

**Quick troubleshooting:**

1. **Try a different browser** (Chrome, Firefox, Safari)
2. **Clear cache and hard reload** (Ctrl+Shift+R on Windows, Cmd+Shift+R on Mac)
3. **Disable browser extensions** (sometimes ad blockers break things)

**If none of that works:**

Reply with:
- What browser + version you're using (e.g., Chrome 120 on Windows)
- Screenshot of the issue (if possible)
- Your quote ID: [quote_id]

I'll investigate and fix it ASAP. In the meantime, I can email you a PDF of the report directly.

Thanks for the report!  
Jason

**Internal action:** 
- Check error logs for quote ID
- Reproduce bug if possible
- Fix or escalate to development
- Send PDF report manually if urgent

---

## Scenario 8: Privacy / Data Concerns

**Customer email:**
> "What do you do with my data? Do you share it with contractors?"

**Response template:**

Hi [Name],

Great question. Here's exactly what happens to your data:

**What we do:**
✅ Store your quote to generate the analysis  
✅ Store your email to send you the report  
✅ Store your payment info with Stripe (we never see your card details)  
✅ Let you access your past reports  

**What we DON'T do:**
❌ Sell your data to anyone  
❌ Share your quote with contractors  
❌ Use your info for lead generation  
❌ Give it to third parties (except Stripe for payments, Google for AI analysis)  

**Why we're different:**

Lead-gen sites (HomeAdvisor, Thumbtack, Angie's List) make money by selling your contact info to 3-5 contractors. That's their entire business model.

**We make money by charging you $19.99 for analysis.** We have zero incentive to sell your data.

**Data deletion:**

Want your data deleted? Just ask. We'll wipe your account + all quotes within 48 hours.

**Read our full Privacy Policy:** https://ungouge.ai/privacy

Any other questions?  
Jason

---

## Scenario 9: Contractor Wants to Use UnGouge

**Customer email:**
> "I'm a contractor. Can I use UnGouge to verify my own quotes before sending them to customers?"

**Response template:**

Hi [Name],

Interesting use case! We built UnGouge for homeowners, but I can see how it would help contractors too.

**How you could use it:**

✅ **Self-audit before sending** — Submit your own quote to see if anything looks inflated or unclear  
✅ **Competitive analysis** — Submit competitor quotes to see how they price vs you  
✅ **Customer trust** — Offer "UnGouge-verified pricing" as a differentiator  

**Pricing for contractors:**

Currently same as homeowners ($19.99/quote). If you're analyzing 5+ quotes/month, let's talk bulk pricing.

Reply if you want to discuss a contractor plan. We're exploring this.

Thanks,  
Jason

**Internal note:** Track contractor interest. If 10+ contractors ask, build a B2B offering.

---

## Scenario 10: Spam / Scam Accusations

**Customer email:**
> "This is a scam. You're just trying to steal my money."

**Response template:**

Hi [Name],

I understand the skepticism—there are a lot of scams online.

**Here's how you can verify we're legit:**

✅ **Real business:** UnGouge LLC, registered in Vermont (you can verify with VT Secretary of State)  
✅ **Secure payments:** We use Stripe (same payment processor as Shopify, Lyft, DoorDash). We never see your card details.  
✅ **Refund policy:** If our report doesn't help, we refund you—no questions asked.  
✅ **No data selling:** Check our Privacy Policy. We don't sell data or generate leads.  

**Try us risk-free:**

Use promo code **LAUNCH2026** for a free analysis. No credit card required. If it's helpful, you can pay for future quotes.

If you're still skeptical, that's fine—no hard feelings. But we're real people trying to solve a real problem.

Best,  
Jason

---

## Scenario 11: Report Says "Suspiciously Low"

**Customer email:**
> "Your report says my quote is suspiciously low. What does that mean?"

**Response template:**

Hi [Name],

"Suspiciously low" means your quote is 15-30%+ *below* typical market rates.

**Why this matters:**

A quote that's way below market could mean:

🚩 **Cutting corners** — Unlicensed work, subpar materials, skipped permits  
🚩 **Bait-and-switch** — Low quote to win the job, then change orders pile up  
🚩 **Inexperience** — Contractor underestimated complexity, will lose money, might bail  
🚩 **Desperate for work** — Financial trouble, might not finish the job  

**What to do:**

1. **Ask questions:** How are they so much cheaper? Where are they saving money?
2. **Verify credentials:** License, insurance, references
3. **Get it in writing:** Fixed-price contract with change order clause
4. **Check reviews:** Do past customers mention quality issues?

**Not always a red flag:**

Sometimes contractors charge less because:
- Small team = lower overhead
- Trying to build a portfolio
- Slow season, willing to discount

**Bottom line:**

Don't automatically reject it, but verify *why* it's low. Cheap can be good—or it can be expensive later.

Want help evaluating the contractor? Reply with their info.

Jason

---

## Scenario 12: Promo Code Not Working

**Customer email:**
> "I tried code LAUNCH2026 but it says invalid."

**Response template:**

Hi [Name],

Let me check that for you.

**Common issues:**

1. **Already used** — Each code works once per account. If you used it before, it won't work again.
2. **Expired** — Some codes are time-limited. LAUNCH2026 is active until [DATE].
3. **Case-sensitive** — Try all caps: LAUNCH2026

**If none of that works:**

I'll manually apply the discount. Reply with your quote ID and I'll mark it as free.

Or use this backup code: **BETATESTER**

Sorry for the hassle!  
Jason

**Internal action:** Check promo code status in database. If expired/invalid, create new one-time code for user.

---

## Response Time SLAs

| Priority | Response Time | Resolution Time |
|----------|---------------|-----------------|
| Critical (payment issue, report not delivered) | <2 hours | <24 hours |
| High (upload issue, technical bug) | <6 hours | <48 hours |
| Medium (general question, feature request) | <24 hours | N/A |
| Low (feedback, testimonial request) | <48 hours | N/A |

---

## Escalation Matrix

**Tier 1 (Zedd AI):**
- Common questions (How does it work? Pricing? File formats?)
- Status checks (Is my report ready?)
- Simple troubleshooting (Try different browser, clear cache)

**Tier 2 (Support Email / Jason):**
- Refunds
- Payment issues
- Technical bugs
- Accuracy disputes
- Privacy concerns

**Tier 3 (Engineering / Manual Review):**
- Complex bugs
- Data corruption
- Security issues
- Infrastructure problems

**How to escalate:** Zedd AI auto-escalates if it can't answer after 2 back-and-forth exchanges. Email support escalates to engineering via Slack/email.

---

## Canned Responses (Quick Templates)

### Report delayed
"Hi [Name], your report is taking longer than expected due to [reason]. Should be ready by [TIME]. Sorry for the delay!"

### General thanks
"Thanks for using UnGouge! Let me know if you have any questions. -Jason"

### Can't help with that
"That's outside what we currently offer, but I'll add it to our feature roadmap. Thanks for the suggestion!"

### Bug acknowledged
"Confirmed bug. We're on it. I'll email you when it's fixed. In the meantime, [workaround]."

---

## Customer Sentiment Tracking

After each interaction, tag:
- 😊 **Happy** — Problem solved, positive feedback
- 😐 **Neutral** — Question answered, no strong reaction
- 😠 **Unhappy** — Frustrated, refund requested, complained

**Goal:** 80%+ Happy, <5% Unhappy

**If Unhappy rate >10%:** Review common complaints, fix root causes

---

**All scenarios documented. Support playbook ready!**

Train Zedd AI on these responses. Use as templates for human support. Update as new scenarios emerge.
