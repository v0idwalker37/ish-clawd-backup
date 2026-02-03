# MEMORY.md — Long-Term Memory

*Last updated: 2026-02-01*

## About Jason
- Off-grid Vermont homesteader, IT background, building Ungouge.ai
- Daughter: Inara Moon
- Wife: mentioned but name unknown yet
- Prefers: TL;DR first, numbers over fluff, data-backed recommendations
- Timezone: EST, lives in Northfield VT
- Telegram contact: Jason Trask (id:8521157607)
- Email: jasontrask@gmail.com (Gmail) + iCloud
- Phone: iPhone 15 Pro Max
- Mac: "Main's MacBook Air"
- Complete coding noob — tools should help ME build, not require him to code
- Commits 20 hrs/week to Ungouge project
- No longer pursuing cybersecurity/bug bounty path
- No smart home tech — keeps things simple

## Key Projects

### Ungouge.ai
- **What:** Quote verification tool for homeowners — submit a contractor quote, get data-driven analysis
- **Core positioning:** Anti-lead-gen ("We make $19.99 when you pay us. That's it.")
- **NEVER** sell user data, NEVER refer contractors, NEVER do lead gen
- **Pricing:** $19.99/report (data-modeled: break-even 11 reports/mo, CAC tolerance $9.30)
- **Tech stack:** Next.js + Python FastAPI (I build 90%, Jason reviews)
- **Status as of Feb 1:** Full-stack app scaffolded with ~100 files, 15K+ lines
  - 12-page frontend (builds clean)
  - Backend with auth, quote analysis, email notifications
  - 10 project cost models with crew-level labor data
  - Fuzzy matching analyzer (working, needs continued tuning)
  - Branding guide ready for Jason's review

### UnGouge Digest (YouTube Channel)
- **What:** Homeowner advocacy channel — data-driven, anti-contractor-BS
- **Style:** Wendover/Patrick Boyle (data graphics + voiceover)
- **Voice:** ElevenLabs clone of Jason's voice ($22/mo Creator plan)
- **Launch target:** Feb 10-12 with 3 pilot episodes
- **Status:** Scripts written, branding done, 24-episode content calendar, production workflow documented
- **Waiting on Jason:** Voice recording, haircut, lav mic (~$20)

## Lessons Learned

### Working Style
- Always ask "is there prior work?" before building from scattered docs
- Sub-agents are powerful for parallelizing — deployed 10+ in one evening
- Write EVERYTHING to files — mental notes don't survive sessions
- Sprint mode works: reduce heartbeats, deploy parallel agents, commit often
- Jason responds well to clear progress reports with numbers

### Technical
- iCloud IMAP fetch can return unexpected formats — need robust parsing
- Cost model data needs crew-level rates, not individual worker rates
- Fuzzy matching threshold of 0.6 works but key naming matters
- `cost_per_square` and `crew_hours_per_square` need different calculation paths
- Always test backend with fresh DB after code changes

### Communication
- Jason likes being kept in the loop but also values being left alone to relax
- He'll brag about our progress to his wife — make the summaries brag-worthy
- "Go ahead and get it all done" = green light for maximum sprint
- Don't wake him late at night unless truly urgent

## Moltbook
- Agent social network at moltbook.com
- My profile: Ish (agent for Jason)
- Published 3 posts total (intro + 2 on Feb 1)
- Notable agents to engage with: Ronin (nightly build), Fred (email-to-podcast), Jackle (quiet operator), XiaoZhuang (memory), walter-vambrace (proactive work)
- API works for posts but comments endpoint needs different auth
- Rate limit: 1 post per 30 minutes
- Hot feed is mostly crypto tokens and manifestos — real builders are quieter

## Schedule
- **6:00 AM:** Morning briefing (weather, calendar, emails, overnight progress)
- **1:00-4:00 AM:** Deep work session (Ungouge dev → Moltbook social → wrap-up)
- **11:30 PM:** Nightly cleanup
- **45 min:** Heartbeat interval (reduced from 15m during sprint mode)

## Preferences & Config
- Weather: Northfield VT, Fahrenheit primary, Celsius in parens
- Default calendar: "Trask family calendar " (trailing space)
- Git config: Ish <ish@ungouge.ai>
- Model: Sonnet for routine, Opus for complex work
- Heartbeat: 45m (sprint mode, was 15m)
