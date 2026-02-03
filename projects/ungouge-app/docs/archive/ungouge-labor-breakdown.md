# Ungouge.ai — Labor Breakdown & Hours Estimate

> **Updated:** Jason is committing **20 hours/week** to this project. This dramatically compresses timelines and allows parallel workstreams (marketing + testing + business setup running alongside the build).

## Summary

| Area | Ish (AI) Hours | Jason Hours | External Help | Total |
|------|---------------|-------------|---------------|-------|
| **Phase 1: MVP Build (Wk 1–4)** | 80–100 | 40–50 | 0 | 120–150 |
| **Phase 2: Growth Features (Wk 5–6)** | 40–60 | 25–30 | 0–5 | 65–95 |
| **Phase 3: Scale (Wk 7–10)** | 30–50 | 20–25 | 5–10 | 55–85 |
| **Legal & Business Setup (Wk 1–2)** | 2–3 | 10–14 | 2–4 | 14–21 |
| **Marketing & Content (Wk 1–6)** | 15–20 | 30–40 | 0–5 | 45–65 |
| **Ongoing Ops (Post-Launch)** | 5/mo | 8/mo | 0 | 13/mo |
| **TOTAL (First 6 Weeks to Launch)** | **~150** | **~120** | **~5–15** | **~275–300** |

Jason's commitment: **20 hrs/week × 6 weeks = 120 hours to launch.** This enables:
- ✅ Legal/business setup running in parallel with build (Week 1–2)
- ✅ Marketing prep starting Week 2 (not waiting until product is done)
- ✅ Deeper testing with more sample quotes across all 6 categories
- ✅ Launch with higher polish and all 6 categories instead of 3
- ✅ Referral program and SEO content ready at launch, not Phase 2

---

## Phase 1: MVP Build (Weeks 1–4) — Compressed Timeline

> With 20 hrs/week, Jason runs **3 parallel tracks** during the build: (A) legal/business setup, (B) content/marketing prep, (C) product testing & feedback. He doesn't wait for Ish to finish building before starting his work.

### What Ish Builds (80–100 hours)

| Task | Hours | Notes |
|------|-------|-------|
| Project scaffolding (Next.js + FastAPI + DB) | 4–6 | Boilerplate, CI/CD, env config |
| Database schema design & migrations | 3–4 | Users, Reports, LineItems, Benchmarks |
| User authentication system | 4–6 | NextAuth.js, JWT, email verification |
| File upload component & pipeline | 4–6 | react-dropzone, S3/Cloudflare R2 storage |
| OCR pipeline (PDF text + Vision API) | 8–12 | PyMuPDF for text PDFs, GPT-4o Vision for images |
| AI parsing prompts & testing | 10–15 | Prompt engineering, structured JSON output, validation |
| Price benchmarking engine | 10–15 | Craftsman API integration, fallback data tables, regional adjustments |
| Red flag detection rules | 6–8 | Rule engine for vague items, missing scope, unusual pricing |
| Quality/warranty lookup | 4–6 | Brand/model database, warranty info retrieval |
| Report generation engine | 8–10 | Data → structured report, summary + line-by-line |
| Report display page (frontend) | 6–8 | Responsive design, charts/visualizations |
| PDF export | 3–4 | Server-side PDF generation |
| Stripe integration | 4–6 | Products, checkout, webhooks, subscription management |
| Email delivery setup | 2–3 | Resend/Postmark integration, templates |
| User dashboard | 4–6 | Saved reports, account management, billing |
| Mobile responsiveness | 3–4 | CSS/layout optimization |
| Testing & bug fixes | 8–10 | Cross-browser, sample quotes, edge cases |
| Deployment & production setup | 3–4 | Vercel + Railway/Render, domain, SSL |

### What Jason Does — Parallel Tracks (40–50 hours over Weeks 1–4)

**Track A: Legal & Business Setup (Week 1–2, ~14 hrs)**

| Task | Hours | Notes |
|------|-------|-------|
| File LLC (Wyoming or VT) | 2–3 | Online filing, same day |
| Apply for EIN | 0.5 | IRS.gov, instant |
| Open business bank account (Mercury) | 2 | Online, may take 1–3 days to verify |
| Set up Stripe business account | 1 | Connect bank, verify identity |
| Shop for Tech E&O insurance | 2 | Get 2–3 quotes, bind policy |
| Review Terms of Service (Ish drafts) | 1.5 | Read, understand, request edits |
| Review Privacy Policy (Ish drafts) | 1 | CCPA/GDPR compliance check |
| Draft operating agreement | 1 | Single-member LLC template |
| Domain DNS configuration | 1 | Point ungouge.com to Vercel |
| Set up business email (hello@ungouge.com) | 1 | Google Workspace or Zoho free |
| Bookkeeping setup (Wave or spreadsheet) | 1 | Track expenses from day 1 |

**Track B: Content & Marketing Prep (Week 2–4, ~16 hrs)**

| Task | Hours | Notes |
|------|-------|-------|
| Write/sketch "dream report" for Ish | 2 | What the ideal Ungouge output looks like |
| Draft landing page copy (with Ish) | 2 | Value prop, how-it-works, CTA |
| Set up social media profiles (4 platforms) | 2 | Twitter/X, LinkedIn, Facebook, Instagram |
| Create "Coming Soon" landing page | 1 | Email capture, launch teaser |
| Write/edit 5 blog articles (Ish drafts, Jason reviews) | 5 | SEO-targeted "cost of X" articles |
| Create lead magnet ("23 Red Flags in Contractor Quotes") | 1 | Ish drafts, Jason reviews/approves |
| Build launch contact list (press, bloggers, forums) | 2 | 20–30 targets for launch day outreach |
| Identify 10 home inspectors for partnership outreach | 1 | Local + national chains |

**Track C: Product Testing & Feedback (Week 2–4, ~14 hrs)**

| Task | Hours | Notes |
|------|-------|-------|
| Collect 25–30 sample quotes | 5–6 | Friends, family, Facebook groups, online — ALL 6 categories |
| Test OCR pipeline as it's built | 2 | Upload real quotes, report issues to Ish |
| Review AI parsing accuracy | 2 | Compare parsed output to actual quote line items |
| Test reports for tone and clarity | 2 | Read every report like a homeowner would |
| End-to-end flow testing | 2 | Upload → parse → report → payment → email |
| Provide UI/UX feedback | 1 | Mobile + desktop walkthrough |

---

## Phase 2: Launch + Early Growth (Weeks 5–6)

> With Jason's bandwidth, launch prep and growth features happen simultaneously. Referral program, SEO content, and partnerships are ready at launch — not bolted on later.

### What Ish Builds (40–60 hours)

| Task | Hours | Notes |
|------|-------|-------|
| Multi-quote comparison | 8–10 | Side-by-side analysis for 2–3 quotes |
| Referral program system | 4–6 | Codes, tracking, reward logic |
| Regional ZIP adjustments | 6–8 | BLS data integration, area modifiers |
| Programmatic SEO pages | 8–12 | Template + city/trade data → 500+ auto-generated pages |
| Negotiation script generator | 3–4 | AI-generated "what to say" for each overpriced item |
| "What's Missing" checklist engine | 3–4 | Per-category expected items vs. what's in the quote |
| Admin dashboard | 6–8 | Internal tool for reviewing analyses, user management |
| Analytics integration | 2–3 | GA4 + PostHog setup |
| Bug fixes & optimization | 5–8 | Performance, accuracy improvements from beta feedback |

### What Jason Does (25–30 hours)

| Task | Hours | Notes |
|------|-------|-------|
| Write/edit 10 more blog articles (Ish drafts) | 6–8 | "[Project] cost in [City]" SEO content |
| Partnership outreach: email/call 15–20 inspectors | 4–5 | Pitch deck ready from Phase 1 |
| Partnership outreach: 5–10 real estate agents | 2–3 | Post-closing referral opportunity |
| Execute Product Hunt launch | 3 | Schedule, post, engage comments all day |
| Execute Reddit/HN/IndieHackers launch | 2 | Cross-post, engage |
| Email blast to waitlist | 1 | Launch announcement |
| Press outreach (10–15 bloggers/journalists) | 2–3 | Personalized pitches |
| Test multi-quote comparison feature | 1 | Upload 2–3 quotes for same project |
| Test referral program flow | 1 | Create code, share, verify reward |
| Monitor first 50 real user reports for accuracy | 3–4 | Manual QA, flag issues to Ish |
| Social media: daily posts for launch week | 2 | Announce, share results, engage |

---

## Phase 3: Scale & Optimize (Weeks 7–10)

### What Ish Builds (30–50 hours)

| Task | Hours | Notes |
|------|-------|-------|
| Partner API (white-label for inspectors) | 10–15 | API endpoints, co-branded reports |
| Contractor referral marketplace | 8–12 | Listing, matching, affiliate tracking |
| User feedback pipeline | 4–6 | "Was this accurate?" → data improvement |
| Advanced subscription management | 4–6 | Tier management, usage limits |
| Performance optimization | 4–6 | Caching, query optimization, cost reduction |

### What Jason Does (20–25 hours/week continuing)

| Task | Hours/wk | Notes |
|------|----------|-------|
| Customer support & community | 3–4 | Handle inquiries, monitor forums |
| Partnership formalization | 4–5 | Revenue-share contracts, onboarding inspectors |
| Content marketing | 4–5 | 2 articles/week, social posts, newsletter |
| Data quality review | 2–3 | Spot-check reports, refine benchmarks with Ish |
| A/B test analysis | 1–2 | Review pricing experiments, conversion data |
| Feature prioritization | 1–2 | Based on user feedback, decide what Ish builds next |
| Paid ads experiments | 2–3 | Small Google Ads campaigns ($300/mo budget) |
| Business admin | 1–2 | Bookkeeping, insurance, legal compliance |

---

## Legal & Business Setup (Folded into Phase 1, Week 1–2)

> With 20 hrs/week, legal/business setup runs as Track A in parallel with the build. All of this completes by end of Week 2 so Stripe and banking are ready when the product needs them.

See Phase 1 Track A above for the full breakdown. Summary: ~14 hours of Jason's time in Weeks 1–2, plus ~3 hours of Ish drafting legal docs.

---

## Marketing & Content (Runs Parallel — Weeks 2–6)

> With 20 hrs/week, marketing prep starts in Week 2 and builds momentum through launch. By Week 5, Jason has a waitlist, content live, partnerships warming, and launch day choreographed.

See Phase 1 Track B (Weeks 2–4) and Phase 2 Jason tasks (Weeks 5–6) for the full breakdown. Key totals:

| Area | Jason Hours | Ish Hours | Notes |
|------|-------------|-----------|-------|
| Landing page + copy | 2 | 3 | Ish drafts, Jason refines |
| Lead magnet PDF | 0.5 | 2 | Ish writes, Jason approves |
| Blog articles (15 total) | 12 | 10 | Ish drafts all, Jason edits/approves |
| Social media setup + content | 4 | 2 | Profiles, initial 20 posts queued |
| Product Hunt prep | 2 | 2 | Assets, narrative, scheduling |
| Press/outreach prep | 4 | 1 | Contact list, pitch emails |
| Partnership outreach | 8 | 1 | Inspectors, agents, pitch deck |
| Email templates | 0.5 | 2 | Transactional + marketing |
| Launch execution | 5 | 0 | All-hands launch day + week |
| **Total** | **~38** | **~23** | |

---

## What Might Need External Help

| Task | Cost Estimate | When | Why |
|------|--------------|------|-----|
| Logo design | $50–200 (Fiverr/99designs) | Week 1 | Professional brand image |
| Legal review of ToS/Privacy | $200–500 (one-time) | Pre-launch | Extra safety for UPPA compliance |
| Copywriting review | $100–300 | Pre-launch | Professional eye on landing page |
| E&O insurance broker | $0 (just shopping) | Pre-launch | Find best rate |
| Bookkeeper/accountant | $50–100/mo | Post-launch | Tax prep, expense tracking |

**Total external costs: $400–1,100 one-time + ~$50–100/mo ongoing**

---

## Revised Timeline (20 hrs/week)

| Milestone | Target | Confidence |
|-----------|--------|------------|
| Project kickoff | Day 1 | ✅ |
| LLC filed, bank account opened, Stripe live | End of Week 1 | High |
| Backend + frontend scaffolding deployed | End of Week 1 | High |
| Landing page live with email capture | Week 2 | High |
| Core OCR + AI pipeline working | Week 3 | High |
| 5 blog articles published | Week 3 | High |
| Full MVP functional (internal) | Week 4 | Medium-High |
| Beta testing with 25+ real quotes | Week 4 | Medium-High |
| Referral program + SEO pages live | Week 5 | Medium |
| **Public launch** | **Week 5–6** | **Medium-High** |
| 100 total reports analyzed | Week 7–8 | Medium |
| 10 inspector partnerships active | Week 8–10 | Medium |
| 100 paid conversions | Week 10–14 | Medium |
| Break-even on operating costs | Month 3–4 | Medium |

### What 20 hrs/week Changes

**Before (5–8 hrs/week):**
- Jason was a bottleneck — slow feedback loops, testing delayed, marketing deferred
- Legal setup ate half his budget for weeks
- Marketing couldn't start until product was done
- Launch at Week 6–7 with marketing as an afterthought

**Now (20 hrs/week):**
- Jason runs 3 parallel tracks from Day 1 (legal + content + testing)
- Legal/business is done by end of Week 2 — no longer a bottleneck
- Marketing has 4 weeks of prep before launch (waitlist, content, partnerships warming)
- Launch at Week 5–6 with marketing machine already running
- Can support all 6 categories at launch (more time for sample quote collection)
- Manual QA of first 50+ reports is feasible (builds data quality early)
- Partnership outreach starts Week 3, not post-launch

### What Moves Into MVP (Previously Phase 2)
With Jason's extra bandwidth for testing and feedback, these features can now ship at launch:
- ✅ **Referral program** — Jason has time to test the flow and seed initial referrals
- ✅ **All 6 categories** — Jason can collect 4–5 sample quotes per category (25–30 total)
- ✅ **Negotiation script generator** — high value, low build effort, Jason can review tone
- ✅ **"What's Missing" checklists** — Jason can validate per-category checklists
- ✅ **15 blog articles** — ready at launch for SEO indexing head start
- ✅ **Programmatic SEO pages** — 500+ city/trade pages live at launch

### Honesty Check
- **6-week launch is aggressive but achievable** with Jason's bandwidth removing feedback bottlenecks
- **The hardest part is still marketing.** But now Jason has time to actually do it properly.
- **Data accuracy will start rough** — but Jason can manually QA 50+ reports in the first 2 weeks post-launch
- **Break-even is faster** because marketing prep is front-loaded, not deferred
- **Risk: Jason burning out at 20 hrs/week** on top of other commitments. Build in buffer weeks.
- **The 20 hrs/week commitment is the single biggest de-risk factor** for this project
