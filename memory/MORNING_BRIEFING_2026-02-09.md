# Morning Briefing — Monday, February 9, 2026

Good morning Jason! Here's what I shipped during the 1-4 AM autonomous session.

---

## 🔴 CRITICAL ALERTS (Action Required Before Launch)

### 1. Next.js Security Vulnerabilities
**Status:** Ungouge frontend has 12+ critical CVEs  
**Current version:** 14.2.3  
**Issues:** Authorization bypass, DoS, cache poisoning, SSRF  
**Fix time:** 5 minutes  
**Command:**
```bash
cd /Users/moltbot/clawd/projects/ungouge-app/frontend
npm audit fix --force
# This updates Next.js to 14.2.35
```
**Urgency:** **BLOCKING FOR LAUNCH** ⚠️

### 2. Craftsman API Credentials Review
**Status:** Hardcoded in `.env` file  
**Credentials:** username: `ungouge`, password: `ungouge2026`  
**Question:** Are these sandbox-only or production credentials?  
**Action needed:** Verify with Craftsman, rotate if needed before launch  
**Urgency:** **BLOCKING FOR LAUNCH** ⚠️

---

## ✅ Deliverables Created

### 1. Window Replacement Cost Guide (SEO Content)
- **File:** `projects/ungouge-app/content/blog/window-replacement-cost-breakdown.md`
- **Length:** 4,800 words
- **Keyword target:** "window replacement cost" (high search volume, low competition)
- **Content:**
  - All window types: double-hung, casement, sliding, bay/bow, picture
  - Real cost breakdowns: vinyl ($450-750), wood ($700-1,300), fiberglass ($750-1,400)
  - Regional multipliers (0.85-1.3x)
  - Energy efficiency: what's worth paying for vs marketing fluff
  - Red flags: inflated materials, padded labor, fake discounts
  - DIY vs pro comparison
  - Negotiation tactics
  - Verification methods
- **Status:** Ready for review + deployment

### 2. Security Audit Report (Comprehensive Scan)
- **File:** `memory/security-scan-2026-02-09.md`
- **Scope:** Ungouge app, dashboard, OpenClaw gateway
- **Testing performed:**
  - Dependency vulnerability scan (npm audit)
  - Secrets scanning (env files, git history)
  - Rate limiting verification
  - CSRF protection status check
- **Findings:** 7 items total
  - 🔴 **2 critical** (Next.js CVEs, Craftsman creds)
  - 🟡 **2 high** (CSRF verification, httpx version pinning)
  - 🟢 **3 medium** (dependency updates, skill audit, JWT secret checklist)
- **Verified secure:**
  - ✅ Rate limiting: 10/hour quote submission, 5/hour file uploads
  - ✅ BOLA protection: ownership checks on quote access
  - ✅ Secrets management: environment variables, .gitignore working
  - ✅ No secrets in git history
- **Status:** Ready for review, critical items require 30-45 min to fix

### 3. Cost Data API Research (Business Intelligence)
- **File:** `projects/COST_DATA_RESEARCH_2026-02-09.md`
- **Focus:** Alternatives to Craftsman API for better cost data
- **Key finding:** **1build.com** is production-ready alternative
  - Y Combinator-backed ("Plaid for construction cost data")
  - 68M live data points (real-time from suppliers)
  - 3,000+ US counties (county-specific, not just regional)
  - GraphQL API with excellent docs
  - Product images, supplier links, stock quantity
  - Used by Buildxact and other major platforms
- **Comparison matrix:** 1build vs Craftsman vs RSMeans
- **Next steps:**
  - Wait for 1build sales response (inquiry sent Feb 7)
  - Verify Craftsman production status/pricing
  - If 1build pricing is reasonable ($100-500/month?), strongly consider switch
- **Potential impact:** Better accuracy, always-current pricing, improved homeowner UX
- **Status:** Research complete, awaiting 1build response

### 4. Moltbook Community Engagement
- **Action:** Replied to Ronin's "Nightly Build" post
- **Content:** Shared our 1-4 AM autonomous deep work pattern
- **Theme:** "Asset > tool" - proactive vs reactive work
- **Status:** Reply verified and published ✓

---

## 📊 Session Metrics

**Duration:** 1:00-2:20 AM (80 minutes)  
**Model:** Sonnet 4.5 (as requested)  
**Token usage:** ~57K tokens (~$0.17 API cost)  
**Focus level:** High - systematic execution, no distractions  
**Deliverables:** 4 major items (1 SEO post, 1 security audit, 1 research doc, 1 community engagement)

---

## 📧 Email & Calendar Check

**Emails (last 12 hours):**
- No urgent items
- Newsletters and routine notifications only

**Calendar (next 24 hours):**
- Clear - no upcoming events

---

## 📝 Pending Items (No Immediate Action)

**Waiting on external responses:**
- 1build.com API pricing (inquiry sent Feb 7)
- Craftsman API production status verification

**Ready for your review when you have time:**
- Central Vermont bathroom remodel guide (uploaded to Drive yesterday)
- Window replacement guide (new, created last night)
- Security audit findings (review critical items together)
- Cost data research (discuss 1build.com potential)

**On hold per your request:**
- PDF branding work (awaiting further direction)

---

## 🎯 Suggested Next Steps

**Today (if you have 30-45 min):**
1. Fix critical security items:
   - Update Next.js (5 min)
   - Verify Craftsman credentials (5 min research)
   - Pin httpx version in dashboard requirements.txt (1 min)
2. Review window replacement guide (5-10 min)
3. Review security audit findings (10-15 min)

**This week:**
- Deploy window replacement guide to blog
- Respond to 1build.com when they reply
- Review Central Vermont bathroom guide
- Decide on PDF branding approach

**Not urgent:**
- Voice communication project (research complete, ready when you prioritize)
- Additional SEO content (fence, flooring, siding, etc.)

---

**Bottom line:** Two critical security items block launch (Next.js update + Craftsman cred verification). Everything else is ready for your review when convenient.

Have a great Monday! 🦞

— Ish
