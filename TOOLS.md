# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## Model Usage Preference

**ALWAYS use Opus 4.6 for:**
- ALL coding tasks (no exceptions)
- ALL sub-agents that write code
- Complex reasoning/architecture decisions
- Multi-step research or deep analysis
- High-stakes tasks (financial, business decisions)
- Anything ambiguous that needs careful judgment

**Jason's explicit instruction (Feb 6):** "YES! :)" — Switch to 4.6 for all coding work

**Sonnet 4.5 only for:** Routine chat, quick questions, simple file reads, heartbeat checks

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

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
