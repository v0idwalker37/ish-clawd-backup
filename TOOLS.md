# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## Model Usage Preference

**Auto-escalate to Opus when:**
- Complex reasoning/architecture decisions
- Multi-step research or deep analysis
- High-stakes tasks (financial, business decisions)
- Code involving multiple files or system design
- Anything ambiguous that needs careful judgment

**Always announce the switch:** "Switching to Opus for this — [reason]" so Jason learns the pattern.

**Default:** Sonnet 4.5 for routine chat, quick questions, file ops, automation

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

- **Location:** Northfield, Vermont (more accurate than state-wide)
- **Format:** Fahrenheit primary, Celsius in parentheses
- **Query:** `curl -s "wttr.in/Northfield+Vermont?u&format=..."`
  - `?u` flag forces USCS/imperial units (Fahrenheit)

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
