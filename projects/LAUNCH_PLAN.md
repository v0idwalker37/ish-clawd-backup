# UnGouge Launch Plan - From Setup to Operating Business

*Created: 2026-02-04*  
*Status: Pre-Launch - Building Infrastructure*

---

## Current Reality Check ✅

**What EXISTS:**
- ✅ Domain: ungouge.ai (+ related domains)
- ✅ Google Workspace: *@ungouge.ai email addresses
- ✅ Dashboard: https://dashboard.ungouge.ai (authenticated, live)
- ✅ Ungouge.ai codebase: Full-stack app (frontend + backend)
- ✅ YouTube scripts: 3 episodes written, ready to produce
- ✅ Blog templates: Ready for content
- ✅ Branding: Complete (colors, voice, positioning)

**What DOESN'T exist yet:**
- ❌ YouTube channel (needs creation)
- ❌ Podcast platforms (Spotify, Apple Podcasts, etc.)
- ❌ Ungouge.ai deployed (code exists, not live)
- ❌ Analytics (nothing to measure yet)
- ❌ Payment processing (Stripe setup needed)

**Your Question:** What do we need to do to move from "setup" to "operating the company"?

---

## The Launch Sequence

### **PHASE 1: Platform Accounts & Content Setup** (Week 1)
*Create the channels, organize the content*

#### 1.1 YouTube Channel Creation (30 min)
**What:**
- Create "UnGouge Digest" YouTube channel
- Configure channel settings (branding, description)
- Upload channel art (logo, banner)
- Set up custom URL (if eligible)

**Who Does It:** Jason (needs your Google account)  
**My Role:** Provide step-by-step guide, branding assets

**Output:** youtube.com/@UnGougeDigest (or similar)

---

#### 1.2 YouTube Content Organization (1 hour)
**What:**
- Move 3 scripts from `/projects/ungouge-digest/scripts/` to dashboard
- Create "Content Calendar" in dashboard (when to upload)
- Set up production checklist (script → recording → editing → upload)
- Upload schedule tracker

**Files to Organize:**
- Episode 1: "How Contractors Are Ripping You Off"
- Episode 2: "The Kitchen Remodel Scam"
- Episode 3: "Emergency Repair Pricing Tricks"

**Output:** Scripts easily accessible, production workflow clear

---

#### 1.3 Podcast Platform Accounts (1-2 hours)
**What:** Create accounts on:
- Spotify for Podcasters (free hosting + distribution)
- Apple Podcasts (via Spotify or direct)
- YouTube Podcasts (use same channel)
- Google Podcasts (automatic via YouTube)

**My Role:** 
- Research which platforms matter most
- Provide signup guides
- Set up RSS feed if needed

**Output:** Podcast available on all major platforms

---

#### 1.4 Analytics Setup (30 min)
**What:**
- YouTube Analytics (automatic when channel created)
- Google Analytics 4 on ungouge.ai (when deployed)
- Dashboard API connections (when channels go live)

**Output:** Ready to track metrics when content launches

---

### **PHASE 2: Ungouge.ai Deployment** (Week 2)
*Get the main product LIVE*

#### 2.1 Review Current Codebase (2 hours)
**What I'll Do:**
- Review `/projects/ungouge-app/` 
- Check what's complete vs what needs finishing
- Identify any missing features
- Test locally to ensure it works

**Your Input Needed:**
- Any feature changes since Feb 1?
- Ready to go live or need tweaks?

**Output:** Status report on what's ready, what's not

---

#### 2.2 Deploy Ungouge.ai (3-4 hours)
**What:**
- Deploy frontend (Vercel or Cloudflare Pages - free)
- Deploy backend (Google Cloud Run - ~$0-10/mo)
- Configure custom domain (ungouge.ai)
- SSL certificates (automatic)
- Environment variables (API keys, secrets)

**Prerequisites:**
- Gemini API key (for AI quote analysis)
- Stripe account (for payments)
- Email service (SendGrid or similar for notifications)

**Output:** https://ungouge.ai LIVE and accepting quotes

---

#### 2.3 Payment Processing Setup (1-2 hours)
**What:**
- Stripe account creation (if not done)
- Payment integration testing
- Webhook setup for payment confirmations
- $19.99 pricing configured

**Output:** Can accept real payments

---

#### 2.4 Email Notifications (1 hour)
**What:**
- Configure email sending (SendGrid, Mailgun, or Gmail API)
- Templates: Quote received, Analysis complete, Payment receipt
- Test full flow

**Output:** Customers get emails after submitting quotes

---

### **PHASE 3: Content Production & Launch** (Week 3)
*Start publishing*

#### 3.1 First YouTube Video (Jason's work + my support)
**Jason's Part:**
- Record voiceover (using ElevenLabs voice clone)
- Film B-roll if needed (or use stock footage)
- Review edited video

**My Part:**
- Provide production checklist
- Help with editing workflow
- Write video description, tags
- Upload and schedule

**Output:** Episode 1 published on YouTube

---

#### 3.2 Dashboard Integration - Real Metrics (2 hours)
**What:**
- Connect YouTube Analytics API to dashboard
- Connect Google Analytics to dashboard
- Connect Stripe to dashboard
- Email monitoring (*@ungouge.ai only)

**Output:** Dashboard shows REAL data:
- YouTube subs, views, watch time
- Website traffic, quote submissions
- Revenue (when first sale happens)
- Inbox status

---

#### 3.3 Blog Content (1-2 hours per post)
**What:**
- Publish blog posts to ungouge.ai/blog
- Repurpose YouTube scripts into written content
- SEO optimization (keywords, meta descriptions)

**Templates exist:** `/projects/ungouge-digest/blog/`

**Output:** Fresh content for SEO, link building

---

## Week-by-Week Timeline

### **Week 1: Account Creation**
- [ ] Mon: YouTube channel creation (Jason)
- [ ] Tue: Organize scripts in dashboard
- [ ] Wed: Podcast platform accounts
- [ ] Thu: Review ungouge-app codebase
- [ ] Fri: Analytics setup planning

**Deliverable:** All platforms created, content organized

---

### **Week 2: Deploy Ungouge.ai**
- [ ] Mon-Tue: Code review & fixes
- [ ] Wed: Deploy frontend + backend
- [ ] Thu: Stripe integration
- [ ] Fri: Email notifications, final testing

**Deliverable:** https://ungouge.ai LIVE and accepting quotes

---

### **Week 3: Launch Content**
- [ ] Mon: Record Episode 1 voiceover (Jason)
- [ ] Tue: Edit video, prepare upload
- [ ] Wed: Publish Episode 1
- [ ] Thu: Connect dashboard to real metrics
- [ ] Fri: First blog post live

**Deliverable:** First video published, website live, dashboard tracking real data

---

## What I Need From You (Decision Points)

### Immediate (This Week):
1. **YouTube Channel:** Ready to create it? (I'll give you step-by-step)
2. **Ungouge.ai Review:** Want me to review the codebase now and report status?
3. **Gemini API Key:** Do you have one? (needed for AI quote analysis)
4. **Stripe Account:** Have you created it yet?

### Soon (Next Week):
5. **Hosting Preferences:** Vercel, Cloudflare, or other for frontend?
6. **Email Service:** Use Gmail API (*@ungouge.ai) or dedicated service (SendGrid)?
7. **Launch Date Target:** When do you want ungouge.ai accepting real quotes?

---

## Success Metrics - "Operating the Business"

**You'll know we're operating (not just building) when:**

✅ **Content Publishing:**
- YouTube: 1 video/week published on schedule
- Blog: 2-3 posts/month live
- Consistent cadence, not sporadic

✅ **Revenue Generation:**
- Ungouge.ai accepting quote submissions
- Payment processing working
- First $19.99 collected

✅ **Dashboard as Command Center:**
- Opens dashboard every morning
- Sees REAL metrics (not sample data)
- Makes decisions based on data shown
- Email alerts working (customer inquiries)

✅ **Business Rhythm:**
- Monday: Review dashboard, plan week
- Daily: Check inbox, respond to customers
- Weekly: Publish content (YouTube/blog)
- Monthly: Review analytics, adjust strategy

---

## My Recommended Starting Point

**START HERE: YouTube Channel Creation**

**Why:**
- 30 minutes to set up
- Unlocks content publishing
- Scripts are already written
- You need it for everything else (podcast, blog SEO)

**What I'll Do:**
1. Write step-by-step YouTube channel creation guide
2. Provide branding assets (channel art, profile pic)
3. Give you the exact description, tags, settings

**What You Do:**
1. Log into Google account (void@ungouge.ai or personal?)
2. Follow my guide (15 min)
3. Send me channel URL

**Then we move to Step 2:** Organize content in dashboard

Sound good? Want me to write that YouTube channel creation guide now?
