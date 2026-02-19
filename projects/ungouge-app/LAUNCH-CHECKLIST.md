# Launch Checklist — Final Steps

*Per Jason's priority order (2026-02-19 1:30 PM)*

---

## 🚨 CRITICAL: PDF Size Fixed

**Status:** Deploying now (backend rev 00054)

**What changed:**
- Created ultra-lightweight "Telegram PDF" (default)
- 6pt fonts, minimal styling, max 15 line items
- Truncated text, compact tables
- **Target:** 1-page quote ~1.5MB, 3-page quote ~2-3MB

**Test it:**
1. Download a PDF from any report
2. Check file size (should be < 5MB, ideally < 3MB)
3. Send via Telegram to verify

**If still too big:**
- We can remove more items (max 10 instead of 15)
- Remove all formatting (plain text only)
- Or use web link instead of PDF attachment

---

## ✅ Order of Operations (From Jason)

### 1. Test Real Payment (15 min)

**Steps:**
- [ ] Go to https://ungouge.ai/analyze
- [ ] Upload a quote (or use manual entry)
- [ ] Complete all steps
- [ ] **Pay $19.99** (real Stripe charge)
- [ ] Verify: Credit card charged correctly
- [ ] Verify: Report unlocks immediately
- [ ] Verify: Receipt email arrives (check jasontrask@gmail.com)

**What to check:**
- Payment goes through without errors
- Redirect back to report works
- Report displays with all data
- Email receipt arrives within 2 minutes

**If it fails:**
- Check Stripe dashboard for errors
- Check backend logs (Cloud Run)
- Check email delivery logs

---

### 2. Mobile Responsive Test (30 min)

**Yes, this means testing on actual mobile devices (iPhone, iPad, etc.)**

**Pages to test:**
- [ ] **Homepage** (ungouge.ai)
  - Hero section readable?
  - CTA buttons tappable?
  - No horizontal scroll?
  
- [ ] **Quote form** (/analyze)
  - All 3 steps work on mobile?
  - File upload works?
  - Line items easy to add/edit?
  - Payment button visible?
  
- [ ] **Report page** (/report/[id])
  - Tables scroll horizontally if needed?
  - Text readable (not too small)?
  - PDF download works?
  - Filter buttons work?
  
- [ ] **Dashboard** (/dashboard)
  - Stats cards stack properly?
  - Sidebar hamburger menu works?
  - Tables responsive?
  
- [ ] **Blog** (/blog)
  - Post listing readable?
  - Individual posts formatted well?

**How to test:**
- Use Safari on iPhone
- Chrome on Android (if you have one)
- Rotate phone (portrait + landscape)
- Try on iPad too

**Common issues to look for:**
- Text too small to read
- Buttons too small to tap
- Horizontal scrolling (bad)
- Overlapping content
- Hidden navigation

---

### 3. Email Delivery Test (15 min)

**Templates to test:**

**A. Welcome Email** (optional, if implemented)
- [ ] Register new account
- [ ] Check email arrives
- [ ] Links work

**B. Password Reset**
- [ ] Request password reset
- [ ] Email arrives within 2 minutes
- [ ] Reset link works
- [ ] Can set new password

**C. Payment Receipt**
- [ ] Complete a paid quote analysis
- [ ] Receipt email arrives
- [ ] Shows correct amount ($19.99)
- [ ] Contains report link
- [ ] Link opens report

**D. Report Ready** (if you want this)
- [ ] Complete payment
- [ ] "Report Ready" email arrives
- [ ] Link works

**Check all emails for:**
- No broken images
- Links work (click every link)
- Formatting looks good (not plain text mess)
- Unsubscribe link present (if applicable)
- From address correct (noreply@ungouge.ai or support@ungouge.ai)

---

### 4. Smoke Test (20 min)

**Full end-to-end flow:**

**Path 1: Upload Quote**
- [ ] Visit homepage
- [ ] Click "Analyze Quote"
- [ ] **Upload** multi-file quote (3 JPGs)
- [ ] Verify parsing works (all items extracted)
- [ ] Review line items (edit if needed)
- [ ] Submit quote
- [ ] Pay $19.99
- [ ] View report
- [ ] Download PDF (< 5MB)
- [ ] Check dashboard (stats updated)
- [ ] Delete quote (should work without 500 error)

**Path 2: Manual Entry**
- [ ] Click "Enter Details Manually"
- [ ] Fill project info
- [ ] Add 3-5 line items manually
- [ ] Submit
- [ ] Pay (can use promo code if you have one)
- [ ] View report
- [ ] PDF download

**Path 3: User Account**
- [ ] Register new account
- [ ] Verify email works
- [ ] Login
- [ ] Submit quote
- [ ] Logout
- [ ] Login again
- [ ] View past quotes
- [ ] Account settings work

**What you're looking for:**
- No 404 errors
- No white screens
- No "500 Internal Server Error"
- All features work as expected
- Performance is acceptable (not super slow)

---

## 🎯 Total-Only Quotes Solution

**Jason said:** "IF we could make magic happen around this in particular we would have something special."

**Status:** Fully designed, ready to implement (3-4 hours)

**What it does:**
- Detects quotes with only a total (no line item costs)
- AI estimates breakdown based on project type + location + industry standards
- Shows estimates with BIG disclaimers: "These are estimates, not actual costs"
- Still provides value even without itemization

**Decision:** Build this now or post-launch?

**Recommendation:** 
- If smoke test goes well → **build it today** (3-4 hours)
- If smoke test finds issues → **fix those first, build this post-launch**

**Design doc:** `TOTAL-ONLY-QUOTES-SOLUTION.md`

---

## 📋 Additional Items (Not Blocker)

### A. Complete void@ungouge.ai OAuth (5 min)
- [ ] Open `/home/ungouge/clawd/skills/email/workspace-auth-url.txt`
- [ ] Click URL, authorize in browser
- [ ] Done

### B. Review Dashboard Stats (2 min)
- [ ] Check if numbers look accurate
- [ ] Total reports correct?
- [ ] Savings calculations right?

### C. PDF Size Verification (2 min)
- [ ] Download PDF
- [ ] Check file size
- [ ] If < 5MB → ✅ good
- [ ] If > 5MB → we'll compress more

---

## 🚀 Launch Decision

**After completing items 1-4 above, ask yourself:**

1. Does the core product work? (upload → pay → report)
2. Can users actually use it? (mobile responsive enough)
3. Are emails arriving? (payment receipts critical)
4. Any showstopper bugs?

**If all ✅ → LAUNCH**

**If any ❌ → Fix the critical bugs, then launch**

---

## 📞 What to Tell Me

After running through this checklist:

1. **What broke?** (be specific)
2. **What worked perfectly?**
3. **PDF file size?** (exact MB)
4. **Should I build total-only quotes now?** (yes/no/later)
5. **When are we launching?** (today, tomorrow, this week?)

---

**I'm ready to fix anything that breaks and build the total-only solution if you want it.** 🚀

Let's ship this thing.
