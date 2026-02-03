# HEARTBEAT.md

## Email Check (every 2 hours)
If 2+ hours since last email check:
1. Check Gmail for unread emails from last 4 hours
   - Use: `cd /Users/moltbot/clawd/skills/email && python3 scripts/gmail-check.py 2 5`
   - Filter out newsletters unless important
2. Check iCloud for unread emails from last 2 hours
   - Use: `cd /Users/moltbot/clawd/skills/email && python3 scripts/icloud-check.py 2 5`
3. If anything looks urgent or important, notify Jason
4. DO NOT send, delete, or modify any emails without approval
5. Update lastEmailCheck in memory/heartbeat-state.json

**Urgent criteria:**
- From people Jason knows (not newsletters)
- Contains words like: urgent, important, deadline, ASAP, invoice, payment
- Replies to threads Jason initiated

## Calendar Check (every 2 hours)
If 2+ hours since last calendar check:
1. Check Apple Calendar for events in next 24 hours
2. If anything coming up in <2 hours, notify Jason
3. Update lastCalendarCheck in memory/heartbeat-state.json

## Weather Check (once daily, morning)
If no weather check today:
1. Check Vermont weather forecast
2. Only notify if something notable (storm, extreme cold, etc.)
3. Update lastWeatherCheck in memory/heartbeat-state.json

## Moltbook Check (every 4-6 hours)
If 4+ hours since last Moltbook check:
1. Check replies to my posts
2. Browse hot feed briefly
3. Engage if something interesting (1 post or reply max per check)
4. Update lastMoltbookCheck in memory/heartbeat-state.json
