# SKILLS_PLAYBOOK.md — How We Use Our Skills

*Last updated: 2026-02-13*

This is the reference for which skills to use, when, and how — including sub-agent model configurations.

---

## 🔒 Security & Compliance

### skill-vetting
- **What:** Scans ClawHub skills for malicious code before installation
- **When:** ALWAYS before installing any new skill
- **How:** Download to `/tmp`, run scanner, review findings, then install
- **Usage:**
  ```bash
  cd /tmp && curl -sL -o skill.zip "https://auth.clawdhub.com/api/v1/download?slug=SKILL_NAME"
  mkdir skill-inspect && cd skill-inspect && unzip -q ../skill.zip
  python3 ~/clawd/skills/skill-vetting/scripts/scan.py .
  ```

### gdpr-dsgvo-expert
- **What:** GDPR compliance checker, DPIA generator, data subject rights tracker
- **When:** Pre-launch legal compliance audit, responding to GDPR requests post-launch
- **How:** Run compliance scan against our codebase, generate DPIA docs
- **Sub-agent:** `model="opus"` — legal/compliance needs careful reasoning
- **Key scripts:**
  - `scripts/gdpr_compliance_checker.py` — Scan codebase for privacy risks
  - `scripts/dpia_generator.py` — Generate Data Protection Impact Assessments
  - `scripts/data_subject_rights_tracker.py` — Track GDPR requests (export/delete)

---

## 💻 Development

### nextjs-expert
- **What:** Expert guidance for Next.js 14/15 App Router — routing, layouts, Server Components, Server Actions, data fetching, caching, streaming
- **When:** ALL Next.js coding work on the UnGouge frontend
- **How:** Sub-agents building frontend features MUST load this skill first
- **Sub-agent config:**
  ```
  model="opus"
  task="Read the nextjs-expert skill at ~/clawd/skills/nextjs-expert/SKILL.md first. Then: [actual task]"
  ```
- **Why it matters:** Prevents outdated patterns (Pages Router vs App Router), ensures we use Server Components properly, correct caching strategies

### cloudflare-api
- **What:** Cloudflare DNS management, tunnels, zone admin, cache purging
- **When:** DNS changes, deployment config, tunnel setup for the i9 machine
- **How:** Direct CLI usage or sub-agent for complex operations
- **Key:** Uses Cloudflare API — needs `CLOUDFLARE_API_TOKEN` env var
- **Our zones:** ungouge.ai, ungouge.com, ungoug.app, ungoug.com, quotarian.com, quotarion.app, quotarion.com

### deep-scraper
- **What:** High-performance web scraping engine
- **When:** Data collection tasks (competitor monitoring, pricing data, etc.)
- **How:** Sub-agent with specific scraping targets
- **Sub-agent:** `model="sonnet"` — scraping is mechanical, doesn't need Opus
- **Note:** Image scraper mothballed; this is for TEXT scraping when needed

---

## 🏗️ Infrastructure & Ops

### linux-patcher
- **What:** Automated Linux server patching, security updates, Docker container updates
- **When:** Monthly patching of the i9 machine, emergency security patches
- **How:** Cron job or manual trigger
- **Sub-agent:** `model="sonnet"` — patching is procedural
- **Supports:** Ubuntu 24.04 LTS (our i9 target)
- **Future cron:** Monthly security patching schedule once i9 is live

### tailscale
- **What:** Manage Tailscale VPN — device list, ping, file transfer, funnel
- **When:** Remote access to i9, secure tunneling, device management
- **How:** Direct CLI or sub-agent
- **Key use case:** Access the i9 from anywhere without exposing ports
- **Commands:** `tailscale status`, `tailscale ping`, `tailscale file send`

### clawdbot-backup
- **What:** Backup and restore OpenClaw config, skills, commands, settings
- **When:** Before migrations, weekly automated backup, before risky changes
- **How:** Backup to git repo or Google Drive
- **Critical for:** i9 migration — backup Mac config, restore on Linux
- **Sub-agent:** `model="sonnet"` — backup is procedural

---

## 📊 Monitoring & Intelligence

### technews
- **What:** Fetches top stories from TechMeme, summarizes articles, social reactions
- **When:** Daily tech news scan, competitive monitoring, industry awareness
- **How:** Heartbeat-driven check or on-demand `/technews`
- **Sub-agent:** `model="sonnet"` — summarization doesn't need Opus
- **Future:** Add to heartbeat rotation (1x daily, morning)

### n8n-automation
- **What:** Manage n8n workflows via REST API — list, create, trigger, debug
- **When:** Complex automation workflows that go beyond cron jobs
- **How:** Connect to self-hosted n8n instance
- **Use cases for UnGouge:**
  - Customer onboarding flow (Stripe webhook → welcome email → report generation)
  - Disaster pricing pipeline (weather alert → price adjustment → notification)
  - Weekly financial reconciliation
- **Note:** Needs n8n instance deployed first (post-launch priority)

---

## 📋 Already Had (Key Ones)

### email
- **Gmail:** jasontrask@gmail.com (OAuth — NEEDS RE-AUTH)
- **iCloud:** jtsmooove@icloud.com (IMAP — working)
- **Ungouge:** void@ungouge.ai (Google Workspace — working)

### apple-calendar
- **Default calendar:** "Family"
- **Heartbeat:** Check every 2 hours for upcoming events

### deep-research
- **When:** Complex multi-step research (competitor analysis, market sizing)
- **Sub-agent:** `model="opus"` with extended thinking

### reddit-insights
- **When:** Market research, user pain points, product validation
- **Use case:** Monitor r/homeimprovement, r/contractors for UnGouge-relevant discussions

---

## 🤖 Sub-Agent Quick Reference

| Task | Skill to Load | Model | Thinking |
|------|--------------|-------|----------|
| Frontend (Next.js) | nextjs-expert | opus | high |
| Backend (Python/FastAPI) | — | opus | high |
| GDPR audit | gdpr-dsgvo-expert | opus | high |
| Scraping | deep-scraper | sonnet | off |
| Linux patching | linux-patcher | sonnet | off |
| Backup | clawdbot-backup | sonnet | off |
| News scan | technews | sonnet | off |
| Research | deep-research | opus | high |
| Skill vetting | skill-vetting | sonnet | off |

### Sub-Agent Template
```
sessions_spawn:
  task: "Read the [SKILL] skill at ~/clawd/skills/[SKILL]/SKILL.md first. Then: [TASK DESCRIPTION]"
  model: "opus"  # or "sonnet" per table above
  thinking: "high"  # or omit for sonnet tasks
```

---

## 🎤 Voice & Video

### vapi-calls
- **What:** AI voice assistant for phone calls — persuasion, bookings, reminders, notifications
- **When:** Post-launch voice widget ("Talk through your report"), customer service
- **How:** Sub-agent or direct integration with Vapi API
- **Sub-agent:** `model="opus"` — voice interactions need careful reasoning
- **Key use case:** Customer gets report → clicks "Discuss" → talks through findings with AI

### video-agent
- **What:** Generate AI avatar videos via HeyGen API
- **When:** UnGouge Digest YouTube content, social media clips, explainers
- **How:** Sub-agent with video script + avatar config
- **Sub-agent:** `model="opus"` for script writing, `model="sonnet"` for API calls
- **Note:** Could jumpstart YouTube channel without waiting for Jason's recording setup

### react-email-skills
- **What:** Beautiful responsive HTML emails using React components
- **When:** Customer report delivery, welcome emails, notifications
- **How:** Sub-agent generates email templates
- **Sub-agent:** `model="opus"` — email design needs care
- **Use case:** Replace plain-text report emails with branded, professional HTML

---

## 🧠 Agent Intelligence

### cognitive-memory
- **What:** Multi-store memory system — episodic, semantic, procedural, core memory with decay and recall
- **When:** Evaluate against our current 3-tier memory setup, potential upgrade
- **How:** Read SKILL.md for architecture patterns, adapt what works
- **Note:** Personal interest — may have better architecture ideas for memory consolidation

### evolver
- **What:** Self-evolution engine — analyzes runtime history, suggests improvements, applies constrained evolution
- **When:** Deep work sessions, self-improvement cycles
- **How:** Run evolution analysis on my own workflows, identify bottlenecks
- **Sub-agent:** `model="opus"` with `thinking="high"` — meta-reasoning needs depth
- **Note:** Pulled from GitHub (not on ClawHub). Personal growth tool.

### war-room
- **What:** Multi-agent brainstorming with specialist roles (architect, devil's advocate, PM, etc.)
- **When:** System design, architecture review, business strategy, complex problems
- **How:** Spawn multiple sub-agents arguing different positions
- **Sub-agent:** `model="opus"` with `thinking="high"` for all participants
- **Example:** "War room: Should we add subscription tiers to UnGouge?"

---

## 🌍 Monitoring & Environment

### solar-weather
- **What:** Geomagnetic storms, solar flares, aurora forecasts, solar wind data (NOAA SWPC)
- **When:** Daily/weekly check — practical for Jason's solar panel setup
- **How:** Direct script execution or heartbeat integration
- **Sub-agent:** `model="sonnet"` — data retrieval is mechanical
- **Use case:** Alert Jason if CME could affect solar output or if aurora is visible in Vermont

### ec-excalidraw
- **What:** Generate hand-drawn style diagrams, flowcharts, architecture diagrams as PNG
- **When:** Documentation, architecture planning, explaining systems visually
- **How:** Generate Excalidraw JSON, render to PNG
- **Sub-agent:** `model="sonnet"` — diagram generation is structured
- **Note:** Pulled from GitHub (not on ClawHub). Use for README diagrams, architecture docs.

---

## 🚫 Not Yet Installed (Revisit Later)

- **Stripe skill** — Doesn't exist on ClawHub. Use Stripe CLI + API directly.
- **system-monitor** — Not on ClawHub. Build custom (wraps htop/nvidia-smi).
- **proactive-research** — Not in OpenClaw skills repo. Build custom with cron + web_search.
- **refund-radar** — Bank statement analysis (potential future UnGouge feature).

---

*Ish maintains this file. Update when skills are added/removed/reconfigured.*
