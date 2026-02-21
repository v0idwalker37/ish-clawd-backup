# Launch Announcements - Ready to Post

## Reddit Post: r/HomeImprovement

**Title:** I built a tool to verify contractor quotes (with real pricing data, not lead-gen)

**Body:**

Hey r/HomeImprovement,

I kept seeing posts here asking "Is this quote too high?" with people getting wildly conflicting advice. So I built something to help.

**What it does:**  
You upload a contractor quote → We analyze it against real market data (material costs, labor rates, regional pricing) → You get a report in 24 hours telling you if it's fair or inflated.

**What it's NOT:**
- Not a lead-gen tool (we never sell your data or connect you with contractors)
- Not a calculator giving you generic ranges
- Not HomeAdvisor/Thumbtack/Angie's List in disguise

**How it works:**
1. Upload quote (PDF, photo, whatever)
2. We compare each line item against RSMeans cost data + regional labor rates
3. You get a detailed report: Fair / High / Red Flags / Recommendations

**Pricing:** $19.99 per quote. (Promo code LAUNCH2026 for free analysis while in beta)

I'm a Vermont homesteader who got tired of seeing people overpay because they had no way to verify pricing. Built this to solve that problem.

**Try it:** https://ungouge.ai

Happy to answer questions. Also open to feedback—still in beta and actively improving.

---

## Twitter/X Thread

**Tweet 1:**  
🏠 Just launched UnGouge — verify contractor quotes before you sign

Most homeowners have NO IDEA if they're being overcharged. $24K for a bathroom remodel... fair or gouging?

We built a tool that tells you: https://ungouge.ai

Here's how it works 🧵

**Tweet 2:**  
The problem: Contractor pricing is opaque

• No standard rates
• Every project is "unique"
• Lead-gen sites (HomeAdvisor, Thumbtack) sell your info, don't verify pricing
• Getting 3 quotes takes weeks and still leaves you guessing

**Tweet 3:**  
UnGouge is different:

✅ Upload your quote (PDF, photo, email)  
✅ We analyze line-by-line vs real market data  
✅ Get report in 24 hours  
❌ We NEVER sell your data  
❌ We NEVER connect you with contractors  

Just honest pricing analysis. That's it.

**Tweet 4:**  
What we check:

• Material costs (are they marking up cabinets 180%?)
• Labor rates (is $150/hr fair for your region?)
• Scope accuracy (is anything missing or inflated?)
• Red flags (vague descriptions, missing permits, suspicious fees)

**Tweet 5:**  
Example: $42K kitchen remodel quote

Our analysis found:
- Materials marked up 180% (should be 20-40%)
- Labor rate 40% above market
- **Actual fair price: $32K**
- **You're overpaying: $10K**

That's $10K saved for $19.99.

**Tweet 6:**  
Why I built this:

I'm an off-grid Vermont homesteader. Watched friends overpay contractors by $5K-$20K because they had no way to verify pricing.

Lead-gen sites don't help—they *sell you* to contractors. We needed something independent.

**Tweet 7:**  
Early adopter pricing: $19.99/quote

🎁 Promo code **LAUNCH2026** for free analysis (limited time)

Try it: https://ungouge.ai

Built for homeowners, by a homeowner. No VC funding. No lead-gen BS. Just data.

---

## LinkedIn Post

**Post:**

🏠 Launching UnGouge: Independent Contractor Quote Verification

**The Problem:**  
72% of homeowners feel uncertain about whether their contractor quotes are fair (Consumer Reports, 2025). The home improvement industry has a pricing transparency problem.

**Existing "solutions" don't help:**
• Lead-gen platforms (HomeAdvisor, Thumbtack, Angie's List) sell your data to contractors
• Free calculators give generic ranges ($25K-$55K... not helpful)
• "Get 3 quotes" advice takes weeks and still leaves you guessing

**What we built:**  
UnGouge analyzes contractor quotes line-by-line against real market data:
- Material pricing (vs retail + fair markup ranges)
- Labor rates (trade-specific, region-adjusted)
- Project scope verification
- Red flag identification

**How it works:**
1. Homeowner uploads quote
2. AI-powered analysis against RSMeans, Craftsman, and real-time data
3. Detailed report in 24 hours: Fair / High / Recommendations

**$19.99 per quote. No subscriptions. No lead generation. Just honest data.**

**What makes us different:**
✅ We NEVER sell customer data  
✅ We NEVER refer contractors  
✅ Independent analysis—we work for the homeowner

**Why I built this:**  
I'm an off-grid homesteader in Vermont. I've seen too many people overpay $5K-$20K on home improvement projects because they had no way to verify contractor pricing.

I built UnGouge to level the playing field. Homeowners deserve pricing transparency.

**Try it:** https://ungouge.ai  
**Early access:** Use code LAUNCH2026 for free analysis

Built for homeowners. No VC funding. No BS.

#HomeImprovement #Transparency #ConsumerProtection #DataDriven #Homeownership

---

## Product Hunt Launch

**Tagline:**  
Know if your contractor quote is fair—before you sign

**Description:**

UnGouge helps homeowners verify contractor quotes using real pricing data.

**The Problem:**  
Getting a contractor quote for home improvement feels like a black box. Is $24,000 for a bathroom remodel fair? Are you being overcharged? Most homeowners have no idea.

Existing solutions don't help:
• Lead-gen sites (HomeAdvisor, Thumbtack) sell your info to 3-5 contractors who spam you
• Free calculators give useless ranges ($18K-$45K... thanks?)
• "Get 3 quotes" advice takes weeks and you still don't know which is fair

**The Solution:**  
Upload your contractor quote → We analyze it against real market data → Get a detailed report in 24 hours.

**What we analyze:**
✅ Material costs (is the markup reasonable?)  
✅ Labor rates (trade-specific, region-adjusted)  
✅ Project scope (anything missing or inflated?)  
✅ Red flags (vague descriptions, excessive fees, missing permits)

**What makes us different:**
• We NEVER sell your data
• We NEVER connect you with contractors
• No lead generation—just independent analysis
• One-time payment ($19.99/quote), no subscription

**Use cases:**
• "I got a $42K quote for a kitchen remodel—is this fair?"
• "Contractor quoted $18K for a deck—seems high?"
• "Should I negotiate this quote or just pay it?"

**Who built this:**  
Solo founder, off-grid Vermont homesteader, tired of seeing people overpay contractors.

**Early access:** Use promo code **LAUNCH2026** for free analysis

**Try it:** https://ungouge.ai

---

## Hacker News Post

**Title:** Show HN: UnGouge – Verify contractor quotes with real pricing data (anti-lead-gen)

**Body:**

Hey HN,

I built UnGouge (https://ungouge.ai) to help homeowners verify contractor quotes using real market data.

**Why this exists:**  
I'm an off-grid homesteader in Vermont. I've watched friends overpay $5K-$20K on home improvement because they had no way to verify contractor pricing. The "get 3 quotes" advice doesn't help if all 3 contractors are overcharging.

**What it does:**
- Upload contractor quote (PDF/photo/email)
- AI analyzes it against RSMeans cost data + regional labor rates
- Get detailed report in 24 hours (Fair / High / Red Flags / Recommendations)

**Tech stack:**
- Frontend: Next.js 14 (App Router), TypeScript, Tailwind
- Backend: Python FastAPI, Cloud Run
- AI: Google Gemini 2.5 Pro with Search Grounding
- Database: Cloud SQL (MySQL)
- Auth: httpOnly cookies (access 30min + refresh 7d)
- Payments: Stripe Checkout

**What I learned:**
- PDF generation in Python is painful (reportlab → WeasyPrint)
- Total-only quotes (no itemization) are way harder to analyze than itemized
- Location-based pricing adjustments matter more than I expected (NYC vs Mississippi = 1.6x difference)
- Accuracy is hard—we're at 65-75% currently, improving with more data

**Business model:**  
$19.99 per quote. No subscription, no lead gen, no selling customer data.

**Differentiator:**  
Lead-gen platforms (HomeAdvisor, Thumbtack, Angie's List) monetize by selling homeowner data to contractors. We don't. We work for the homeowner, not the contractor.

**Current status:**  
Soft launch. ~10 beta users. Promo code **LAUNCH2026** for free analysis.

**Open to feedback on:**
- Accuracy improvements (how do I get to 85%+?)
- Pricing model ($19.99 vs subscription vs freemium?)
- Customer acquisition (without becoming a lead-gen site myself)

**Try it:** https://ungouge.ai

Happy to answer technical questions about the stack, accuracy challenges, or business model.

---

## Instagram Post (Image + Caption)

**Image:** Screenshot of quote analysis dashboard showing "Fair Price" verdict with green checkmark

**Caption:**

🏠 Got a contractor quote? Verify it before you sign.

Most homeowners have NO IDEA if they're being overcharged.

$24K for a bathroom remodel... fair or gouging? 🤔

UnGouge tells you. Upload quote → Get analysis in 24 hours.

✅ Real market data (not guesses)  
✅ Region-specific pricing  
✅ No lead generation BS  

Try it free: Link in bio 👆  
Code: LAUNCH2026

#HomeImprovement #ContractorQuotes #HomeRenovation #Homeowner #DontGetGouged #DataDriven #VermontMade

---

## Facebook Post (for Business Page)

🏠 **Launching UnGouge: Know Before You Pay**

Getting a contractor quote feels like a shot in the dark. Is $32,000 for a kitchen remodel fair? Are you being overcharged?

**We built a tool to answer that question.**

📊 Upload your contractor quote  
🤖 AI analyzes it against real market data  
📧 Get detailed report in 24 hours  

**What we check:**
✅ Material costs (fair markup or excessive?)  
✅ Labor rates (reasonable for your region?)  
✅ Red flags (vague descriptions, missing permits, suspicious fees)  

**What we DON'T do:**
❌ Sell your data  
❌ Spam you with contractor referrals  
❌ Generate leads  

Just honest, independent analysis. $19.99 per quote.

**Try it free:** Use code **LAUNCH2026**  
👉 https://ungouge.ai

Built by a Vermont homesteader who got tired of people overpaying contractors.

---

## Email to Friends/Family/Network

**Subject:** I built something for homeowners (would love your feedback)

Hey [Name],

I just launched something I've been working on and wanted to share it with you first.

**What it is:**  
UnGouge (https://ungouge.ai) — a tool that verifies contractor quotes using real pricing data.

**Why I built it:**  
I kept seeing friends and neighbors overpay contractors by $5K-$20K because they had no way to know if their quote was fair. Lead-gen sites don't help—they sell your info to contractors.

I wanted something independent. So I built it.

**How it works:**
1. Upload contractor quote
2. We analyze it against real market data (material costs, labor rates, regional pricing)
3. Get detailed report in 24 hours: Fair / High / Recommendations

**Pricing:** $19.99 per quote (or free with code LAUNCH2026 for early users)

**I'd love your feedback:**
- Does this seem useful?
- Would you use it (or know someone who would)?
- What's confusing or unclear?

No pressure—just wanted to share with people I trust before going wider.

Try it here: https://ungouge.ai

Thanks for taking a look!

Jason

P.S. I built the whole thing myself (first real coding project). Still rough around the edges but functional. Feedback welcome.

---

## Discord/Slack Communities (Homeowner groups)

**Message:**

Hey all! I built a tool for homeowners and wanted to share.

**UnGouge** — Verify contractor quotes before you sign

Problem: You get a $24K bathroom quote and have NO IDEA if it's fair.

Solution: Upload it → We analyze against real market data → Report in 24 hours

**What we check:**
- Material costs (fair markup or 200% inflation?)
- Labor rates (region-specific averages)
- Red flags (vague items, missing permits, suspicious fees)

**What we're NOT:**
- Not a lead-gen tool (we never sell your data)
- Not HomeAdvisor/Thumbtack in disguise
- Not a calculator (we analyze YOUR specific quote)

**Pricing:** $19.99/quote (code LAUNCH2026 for free)

Try it: https://ungouge.ai

Built by a Vermont homesteader tired of seeing people overpay. Feedback welcome!

---

## Summary

**All announcements ready to post.**

**Posting schedule recommendation:**
- **Day 1 (Tue/Wed):** Product Hunt + Twitter thread + LinkedIn
- **Day 2:** Reddit r/HomeImprovement + Hacker News
- **Day 3:** Instagram + Facebook
- **Day 4:** Email to network
- **Ongoing:** Discord/Slack communities (when appropriate)

**Promo code to activate:** LAUNCH2026 (100% discount)

**Assets needed:**
- Screenshot of quote analysis dashboard (for Instagram/social)
- Logo/branding images
- Short demo video (optional but high-impact)

All copy is ready. Just pick your launch date and start posting!
