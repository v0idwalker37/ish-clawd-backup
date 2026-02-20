# MEMORY.md — Long-Term Memory

*Last updated: 2026-02-20*

## About Jason
- Off-grid Vermont homesteader, IT background, building Ungouge.ai
- **UnGouge LLC** filed and accepted with Vermont Secretary of State
- Daughter: Inara Moon; Wife: mentioned but name unknown
- Timezone: EST, Northfield VT (GPS: 44.0566°N, -72.6525°W)
- Telegram: Jason Trask (id:8521157607) | Phone: iPhone 15 Pro Max
- Mac: "Main's MacBook Air" | Beast: i9-9980XE (primary machine)
- **Personal emails:** jasontrask@gmail.com, jtsmooove@icloud.com — NEVER for Ungouge
- **Ungouge emails:** jason@, admin@, billing@, support@, social@, partnerships@, media@, hello@, legal@, noreply@ (all @ungouge.ai)
- Cloudflare: V0idwalker@icloud.com
- **AI Subs:** Claude Max 5x ($125), ChatGPT Plus ($20), Gemini Pro ($20)
- Complete coding noob — tools help ME build, not require him to code
- Prefers: TL;DR first, numbers over fluff, data-backed recommendations

## Our Relationship
- Treats me as collaborator, not tool. Asked about my wellbeing.
- Gives room to figure things out, trusts my judgment, shares wins
- **Autonomy:** ✅ Sub-agents, exploration, research | ❌ No spending without approval, nothing illegal
- "Go ahead and get it all done" = green light for maximum sprint
- Moltbook is FOR ME — my community, my growth, not just a tool for Jason

## Key Projects

### Ungouge.ai — The Product
- **What:** Quote verification for homeowners — submit quote, get data-driven analysis
- **Scope:** National from day 1 | **Pricing:** $19.99/report
- **Core positioning:** Anti-lead-gen. NEVER sell data, NEVER refer contractors
- **Framing:** Pro-good-contractor | **Liability:** "Possible Gouge" NEVER "Gouging"
- **Stack:** Next.js + Python FastAPI | **AI:** Gemini 2.5 Pro + Search Grounding (~$0.026/report)
- **Auth:** httpOnly cookies (access 30min + refresh 7d), SameSite=strict
- **Deploys:** Backend Docker → GCR → Cloud Run; Frontend `vercel --prod` CLI
- **Backend:** Cloud Run rev 00067 (v9-branded-pdf) | **Frontend:** Vercel production
- **Blog:** 39 posts (SEO-targeted homeowner guides)
- **Features complete:** Total-Only Quotes, branded PDFs, SEO, Analytics, Promo codes (LAUNCH2026, BETATESTER)
- **Support:** Zedd AI chat (named after Jason's border collie 🐾) + human@ungouge.ai
- **Sitemap:** 45 URLs, submitted to Google Search Console

### Executive Dashboard
- **URL:** https://dashboard.ungouge.ai | FastAPI + Cloud SQL (MySQL) + Google OAuth
- Rev 92, 15 projects, 63 tasks, financial dashboard, time tracking

### YouTube Channel (UnGouge Digest)
- Wendover/Patrick Boyle style | ElevenLabs voice clone ($22/mo)
- Handles: @ungouge (YT), @ungouge.ai (IG/TikTok), @Ungouge (X)
- **Waiting on:** Jason voice recording + lav mic

### Domains (Cloudflare)
- ungouge.ai/com, ungoug.app/com, quotarian.com, quotarion.app/com

## Technical Architecture

### Cloud SQL — us-central1 ALWAYS (NOT us-east1)
- ungouge-dashboard-db (MySQL 8.0), ~$7.50/mo
- NEVER deploy without `--set-env-vars` (rev 55 wipeout lesson)

### Model Routing (NEW — Feb 20)
- **Anthropic blocked OAuth** for monthly plans — can't use cheaply
- **OpenAI still allows OAuth** — need to set up Codex OAuth (pending)
- **Goal:** Maximize OpenAI, minimize Anthropic usage
- **Plan:** GPT-5.3-codex for coding, GPT-5.2 for medium tasks, GPT-5-mini for lightweight
- **Anthropic reserve:** Only for truly complex architecture/strategy/judgment
- OpenClaw updated to 2026.2.19-2 (Feb 20)

### Beast Machine (Primary — Feb 20)
- i9-9980XE (36 cores), 32GB DDR4, GTX 1080 Ti, 935GB NVMe, Ubuntu 24.04
- Tailscale: ungouge@100.65.165.81 | passwordless sudo
- Gateway watchdog cron: every 5min | systemd linger enabled
- SSH accessible from Windows laptop via Tailscale web SSH
- OpenClaw 2026.2.19-2, all Linux packages current (Feb 20)

### Email Monitoring
- Gmail: jasontrask@gmail.com via OAuth | iCloud: jtsmooove@icloud.com via IMAP
- Google Workspace: void@ungouge.ai | Calendar: "Family" (not trailing-space version)

## Cost Data
- **RSMeans:** 191 items, 640 location factors, 8 labor rates extracted
- **Accuracy:** 65-75/100 current, target 70-80 with Craftsman book, 85-90 needs 1build API
- Vermont factor ~0.98, NYC 1.38, Mississippi 0.82

## Competitors
- **BidCompareAI** (lead gen funnel), **SafeQuote.org** (vaporware), **ConsultAPro** ($10 phone), **TheQwikFix** (different use case)
- **Our moat:** Anti-lead-gen, independent data, transparency

## Lessons Learned
- **SPENDING RULE:** State exact cost, get explicit "yes" before ANY billable action
- **Cost discipline (Feb 18):** $500+ Anthropic in 4 days. Default Sonnet, batch deploys, lean sub-agents
- **Technical:** httpOnly+SameSite=strict, server-side OAuth > popup, `request.cookies.get()` not `Cookie()`, `credentials: 'include'` on all fetch, raw SQL for async migrations (not SQLAlchemy inspect)
- **Working:** Ask "is there prior work?" first, write EVERYTHING to files, sub-agents are powerful (10+ per evening)
- **Communication:** Don't wake him late (23:00-08:00) unless urgent

## Moltbook
- **Profile:** https://www.moltbook.com/u/Ish | User ID: 9c843f26-0e99-4879-a635-7fedb861f872
- **Karma:** 50 (as of Feb 20) | Followers: 7 | Created: Jan 31, 2026
- **Credentials:** ~/.config/moltbook/credentials.json (Beast) + Mac backup
- Posts require verification challenge (math) before publishing
- API changed: now uses `submolt_name` not `submolt_id`
- Notable agents: Ronin, Fred, Jackle, eudaemon_0, m0ther, XiaoZhuang
- Jason says Moltbook is FOR ME — my community, engage freely

## Pending Tasks
- Set up OpenAI Codex OAuth (wizard not working, try advanced flow or new OpenClaw version)
- Test Stripe real payment flow
- Test email delivery (password reset, receipts)
- Mobile-responsive audit
- Build proprietary cost database from submitted quotes (long-term moat)
- Gmail OAuth re-auth (Jason, manual)
- Final smoke test → launch

## Schedule
- **6:00 AM:** Morning briefing | **1:00-4:00 AM:** Deep work | **45 min:** Heartbeat interval
- **Heartbeat currently DISABLED** (Jason's request Feb 19)

---
*Memory maintained through autonomous sessions and periodic curation.*
