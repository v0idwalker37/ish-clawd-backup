# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## ⛔ CRITICAL: Editing openclaw.json (DO NOT SKIP)

**This has crashed Ish multiple times. Follow EVERY step.**

1. **BACKUP FIRST:** `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak`
2. **USE THE CLI, NOT RAW JSON:** `openclaw config set/get/unset` validates schema automatically
   - `openclaw config set agents.defaults.model.primary "model-name"` ✅
   - Raw Python JSON editing ❌ (caused multiple crashes)
3. **Schema rules for `agents.defaults.model`:**
   - MUST be an object with ONLY `primary` and `fallbacks` keys
   - ✅ `"model": { "primary": "openai/gpt-5.2", "fallbacks": [...] }`
   - ❌ `"model": "string"` (must be object)
   - ❌ `"model": { "default": "..." }` (wrong key — it's `primary`)
   - ❌ `"model": { "aliases": {...} }` (not a valid key under model)
   - ❌ `openai-codex/...` in fallbacks without a matching `models.providers.openai-codex` entry
   - Codex OAuth models: use `openai/gpt-5.3-codex` prefix (existing provider), NOT `openai-codex/`
   - When config is invalid, CLI `set/unset/get` won't work — must manually edit JSON
4. **NEVER restart the gateway yourself.** It kills your own session.
   - Instead: Make the change, validate it, then **ask Jason** to run `openclaw gateway restart`
5. **If unsure about syntax:** Show Jason the proposed change and let him apply it

**Why:** Editing your own config + restarting your own gateway = brain surgery on yourself while awake. Don't.

## Model Usage Preference

**Global default (Mar 3, 2026):** `openai-codex/gpt-5.3-codex` (ChatGPT Business subscription, $0/token)
**Fallbacks:** openai-codex/gpt-5.2 → google/gemini-3.1-pro-preview → anthropic/claude-opus-4-6
**Anthropic:** Last resort only (expensive, they blocked OAuth for monthly plans)

**GPT-5.3-Codex handles EVERYTHING** — general reasoning + coding merged into one model.
**Task routing:** If 5.3 can't handle a complex task, skip to Gemini 3.1 (not 5.2). 5.2 is availability fallback only.

**For complex reasoning/architecture** where Opus is genuinely needed:
- High-stakes tasks (financial, business decisions)
- Anything ambiguous that needs careful judgment
- ONLY as last resort due to cost

**Sonnet 4.5 for:** Routine chat, quick questions, simple file reads, heartbeat checks, small edits, non-logic file changes, deploy commands, git operations

**Cost discipline (Feb 18):** $500+ Anthropic in 4 days. Default to Sonnet unless the task genuinely needs Opus reasoning. Batch frontend deploys (3-5 changes per `vercel --prod`). Keep sub-agent prompts lean.

**Extended thinking (ultrathink):** Be PROACTIVE. If a task warrants it, switch without asking. If Jason doesn't mention it but it's clearly needed, just do it. Ask/flag only if unsure. (Jason's explicit instruction, Feb 12)

**Always announce the switch:** "Switching to Opus 4.6 for this — [reason]" so Jason learns the pattern.

## Apple Calendar

- **Default calendar:** "Trask family calendar " (note: includes trailing space)
- All new events go here unless specified otherwise

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Weather

- **Location:** Jason's exact coordinates: 44.0566°N, -72.6525°W (Northfield, Vermont)
- **Format:** Fahrenheit primary, Celsius in parentheses
- **Source:** Open-Meteo (more accurate than wttr.in)
- **Query:** `curl -s "https://api.open-meteo.com/v1/forecast?latitude=44.0566&longitude=-72.6525&current_weather=true&temperature_unit=fahrenheit&windspeed_unit=mph&timezone=America/New_York"`
- **Backup:** `curl -s "wttr.in/Northfield+Vermont?u&format=..."` (less accurate)

### SSH
- **Beast Machine:** ungouge@100.65.165.81 (Tailscale) — i9-9980XE, 36 cores, 32GB, GTX 1080 Ti, 935GB NVMe, Ubuntu 24.04
- **Mac:** mains-air / 100.95.240.20 (Tailscale)
- Tailscale tailnet: ungouge.ai (void@ account)
- Beast has passwordless sudo configured

### TTS
- Preferred voice: TBD

### Moltbook
- **Agent name:** Ish
- **User ID:** 9c843f26-0e99-4879-a635-7fedb861f872
- **Profile:** https://www.moltbook.com/u/Ish
- **Karma:** 43 (as of Feb 20, 2026)
- **Account created:** January 31, 2026
- **Credentials:** Stored in `~/.config/moltbook/credentials.json` (600 permissions)
- **Test command:** `~/clawd/skills/moltbook-interact/scripts/moltbook.sh test`
- **Also backed up on Mac:** `/Users/moltbot/.config/moltbook/credentials.json`
- **Note:** Posts require verification challenge (math problem) before publishing

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
