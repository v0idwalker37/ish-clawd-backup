# ungouge.ai - Project Documentation

**AI-powered quote analysis to help businesses avoid overpaying.**

---

## 📁 Documentation Overview

This folder contains everything you need to build, launch, and scale ungouge.ai from idea to profitable business.

### **Core Documents**

1. **[ungouge-mvp-roadmap.md](ungouge-mvp-roadmap.md)** ⭐ START HERE
   - Complete 12-week MVP roadmap
   - Phase-by-phase breakdown (6 phases)
   - Technical architecture decisions
   - Success metrics and risk mitigation
   - Post-MVP feature ideas
   - **Use this for:** Overall project planning and decision-making

2. **[ungouge-implementation-checklist.md](ungouge-implementation-checklist.md)**
   - Week-by-week task checklist
   - Concrete implementation steps
   - Code snippets and database schemas
   - Setup instructions
   - **Use this for:** Daily/weekly execution (check off as you build)

3. **[ungouge-business-brief.md](ungouge-business-brief.md)**
   - One-page business overview
   - Problem/solution, target customer, business model
   - Competitive analysis
   - Elevator pitch
   - **Use this for:** Explaining the concept to others, validation, fundraising

---

## 🚀 Quick Start Guide

### **Phase 0: Validation (Before Writing Code)**

1. **Read all three documents** (30 minutes)
2. **Create landing page** with email capture (use Carrd, Webflow, or simple Next.js page)
   - Headline: "Stop Overpaying on Vendor Quotes"
   - Subhead: "AI-powered analysis in 60 seconds. Know exactly where you're being overcharged."
   - CTA: "Join Waitlist" or "Get Free Analysis"
3. **Drive 50-100 signups** (test demand before building)
   - Post on LinkedIn/Twitter
   - Share in relevant communities (r/smallbusiness, IT manager groups)
   - Run small ad campaign ($100 budget)
4. **Interview 5-10 signups**
   - "What quotes do you struggle with most?"
   - "How do you currently compare pricing?"
   - "Would you pay $29 for instant analysis?"
5. **Manual concierge MVP** (validate value)
   - Offer 5 people free quote analysis (do it manually with ChatGPT/Claude)
   - See if they find it valuable
   - Ask for testimonial

**Decision Point:** If <20% signup-to-paid intent, pivot or refine value prop. If >30%, proceed to build.

---

### **Phase 1: Foundation (Week 1-2)**

1. **Register domain** (ungouge.ai or .com alternative)
2. **Set up tech stack:**
   - GitHub repo
   - Vercel account (connect to repo)
   - Supabase project
   - Get API keys (OpenAI, Anthropic, Stripe)
3. **Follow checklist:** [ungouge-implementation-checklist.md](ungouge-implementation-checklist.md) Week 1-2 section
4. **Create database schema** (users, quotes, line_items, analyses)
5. **Build "hello world"** Next.js app + deploy to Vercel

**Milestone:** Can upload a file and store it in R2/S3.

---

### **Phase 2-5: Build Core Features (Week 3-11)**

Follow the week-by-week checklist in [ungouge-implementation-checklist.md](ungouge-implementation-checklist.md).

**Key Milestones:**
- **Week 4:** AI parsing works on test quotes
- **Week 6:** Gouging score calculated accurately
- **Week 7:** First complete report generated
- **Week 9:** Payment flow functional
- **Week 11:** Beta testing with real users

---

### **Phase 6: Launch (Week 12)**

1. **Product Hunt launch**
2. **Social media blitz** (Twitter, LinkedIn)
3. **Email waitlist** ("We're live!")
4. **Monitor metrics:**
   - Signups per day
   - Conversion rate (signup → paid)
   - Parsing accuracy
   - User feedback (NPS)

**Target:** 100 signups in first 30 days, 20%+ conversion.

---

## 🎯 The One-Sentence Mission

**"Help businesses stop overpaying by making quote analysis instant, accurate, and actionable."**

---

## 📊 Key Metrics to Track

### **Pirate Metrics (AARRR)**

1. **Acquisition:** How many signups/week?
2. **Activation:** % who complete first analysis?
3. **Retention:** % who return for 2nd analysis?
4. **Revenue:** Average $ per user (ARPU)?
5. **Referral:** % who share or refer others?

### **North Star Metric**

**"Total dollars saved by users"** (self-reported + estimated)
- This is your marketing hook: "Our users have saved $X million"

---

## 🛠️ Tech Stack Summary

| Layer | Technology | Why |
|-------|------------|-----|
| Frontend | Next.js 14 + TypeScript | Fast, SEO-friendly, serverless |
| UI | Tailwind CSS + shadcn/ui | Rapid prototyping, clean design |
| Backend | Next.js API routes | No separate backend needed initially |
| Database | PostgreSQL (Supabase) | Relational data, built-in auth |
| AI | OpenAI + Anthropic | GPT-4o for parsing, Claude for analysis |
| Storage | Cloudflare R2 | Cheap, S3-compatible |
| Payment | Stripe | Industry standard, easy integration |
| Hosting | Vercel | Auto-deploy, edge network |
| Email | Resend | Modern API, great DX |
| Analytics | Plausible | Privacy-friendly, simple |

**Total monthly cost (MVP scale):** ~$120-150

---

## 💰 Business Model at a Glance

**Pay-per-analysis (recommended for MVP):**
- $29 per quote
- $99 for 5-pack

**Unit Economics:**
- Revenue per analysis: $29
- AI + hosting cost: ~$2
- Gross margin: 93%
- Break-even: 6 analyses/month

**Growth Levers:**
1. **SEO:** Rank for "quote comparison," "vendor pricing"
2. **Content:** Case studies, savings calculators, industry reports
3. **Referral:** 1 free analysis per referral
4. **Partnerships:** IT consultants, business advisors (30% affiliate fee)

---

## 🏁 Next Actions (In Order)

1. [ ] **Read all three docs** (you're doing this now ✅)
2. [ ] **Decide:** Build or validate first?
   - **If validate first:** Create landing page, test demand
   - **If build now:** Jump to implementation checklist Week 1
3. [ ] **Set up project management:**
   - [ ] GitHub repo (code + issues)
   - [ ] Notion/Linear (tasks + roadmap)
   - [ ] Daily standup doc (what shipped yesterday/today?)
4. [ ] **Block calendar time:**
   - [ ] 2-4 hours/day for building (focused work)
   - [ ] 1 hour/week for user interviews
5. [ ] **Commit to shipping in 12 weeks** (or set your own deadline)

---

## 📚 Additional Resources

### **Learning**
- [Next.js Docs](https://nextjs.org/docs)
- [Supabase Quickstart](https://supabase.com/docs/guides/getting-started)
- [OpenAI API Guide](https://platform.openai.com/docs)
- [Stripe Integration Tutorial](https://stripe.com/docs/payments/quickstart)

### **Tools**
- [shadcn/ui Components](https://ui.shadcn.com)
- [Vercel Deployment](https://vercel.com/docs)
- [Plausible Analytics](https://plausible.io/docs)

### **Community**
- r/SaaS (Reddit)
- Indie Hackers (forum + podcast)
- Product Hunt (launch platform)

---

## 🤝 Get Help

**Stuck on something?**
1. Check the relevant section in [ungouge-implementation-checklist.md](ungouge-implementation-checklist.md)
2. Search the tech stack docs (links above)
3. Ask in AI tooling communities (OpenAI forum, Anthropic Discord)
4. DM me (Jason) if you're collaborating

**Found a bug in the docs?**
- Update the relevant .md file and commit changes

---

## 🎉 Final Thoughts

**This is a real business opportunity.** The problem is validated (businesses overpay constantly), the solution is feasible (AI can parse and analyze quotes), and the market is huge (every B2B transaction).

**Keys to success:**
1. **Ship fast** - 12 weeks to MVP, not 12 months
2. **Talk to users** - Weekly interviews, constant feedback
3. **Iterate in public** - Share progress, build an audience
4. **Focus on value** - If users save $8K on a $29 tool, they'll tell everyone

**You've got this. Now go build something people want to pay for.**

---

**Last Updated:** 2026-01-31  
**Status:** Documentation complete, ready to build  
**Maintainer:** Jason / Ish

---

## 📋 Document Versions

| Document | Version | Last Updated |
|----------|---------|--------------|
| MVP Roadmap | 1.0 | 2026-01-31 |
| Implementation Checklist | 1.0 | 2026-01-31 |
| Business Brief | 1.0 | 2026-01-31 |
| README | 1.0 | 2026-01-31 |

*Tip: Update versions when making significant changes to keep team aligned.*
