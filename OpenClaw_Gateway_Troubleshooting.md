# OpenClaw Gateway Restart Troubleshooting Guide

## Normal Startup (should just work)

### Option 1: Use the app
- Click the OpenClaw icon in your menu bar
- Click "Start Gateway" or "Restart Gateway"

### Option 2: Terminal
```bash
openclaw gateway start
```

---

## If It Doesn't Start

### 1. Check if it's already running
```bash
openclaw status
```
- If it says "running" but you can't reach Ish, try restart instead of start

### 2. If status shows "stopped", try:
```bash
openclaw gateway restart
```

### 3. If you get an error about port 18789 already in use:
```bash
# Kill any stuck process on that port
lsof -ti:18789 | xargs kill -9
openclaw gateway start
```

### 4. If you get permission errors:
```bash
# Check that openclaw binary has execute permission
ls -la $(which openclaw)
# Should show executable flag. If not:
chmod +x $(which openclaw)
```

### 5. If gateway crashes immediately after starting:
```bash
# Check logs for errors
openclaw gateway logs --tail 50
```
- Look for red ERROR lines
- Common issues: config file corrupted, port conflict, permissions

### 6. Nuclear option (resets everything, last resort):
```bash
openclaw gateway stop
rm ~/.openclaw/openclaw.lock
openclaw gateway start
```

---

## Verification Test

Once gateway is running, test that Ish is reachable:
```bash
openclaw status
```
Should show:
- Gateway: running
- Sessions: 1+ active
- Last message: recent timestamp

Then just send Ish a Telegram message. If Ish responds, you're good.

---

## If Nothing Works

1. **Reboot the Mac** (solves 90% of weird issues)
2. After reboot: `openclaw gateway start`
3. If still broken, send Ish the output of:
   ```bash
   openclaw gateway logs --tail 100
   ```
   And Ish will diagnose from the logs.

---

## Pro Tip

**Before you shut down for the flight:**
Run `openclaw status` and screenshot it. That's your baseline "working state" to compare against when you restart in Miami.

---

## What Survives Shutdown

✅ **Saved (zero data loss):**
- All memory files (MEMORY.md, daily logs, project files)
- Session history
- Configuration
- Cron jobs (they resume their schedules)

❌ **Lost (but not important):**
- Active running processes (auto-save state first)
- Temporary /tmp files
- Current conversation context window (saved to session history)

---

## Emergency Contact

If Ish is offline and you need immediate help:
- Check OpenClaw Discord: https://discord.com/invite/clawd
- OpenClaw docs: https://docs.openclaw.ai
- Local docs: `/Users/moltbot/moltbot/docs/`
