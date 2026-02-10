# Git Secret Scanning Block - Action Required

## Problem

GitHub's secret scanning is blocking all pushes to the repository because **secrets exist in git history** (not just current files). Even though we've removed the files from the current commit, the secrets are still in previous commits.

## Blocked Secrets in History

1. **Google OAuth Client ID** and **Client Secret** in:
   - `skills/google-drive/ungouge-oauth-credentials.json`
   - `skills/google-drive/complete-auth.py`
   - `skills/google-drive/get-auth-url.py`
   - `skills/google-drive/setup-drive-api.py`

2. **Stripe Test API Key** in:
   - `projects/ungouge-dashboard/backend/.env.cloudrun`

## What We've Done

- ✅ Removed files from current commit
- ✅ Added to `.gitignore`
- ✅ Committed changes locally

## What's Blocked

- ❌ Cannot push to GitHub until git history is cleaned

## Solutions (Pick One)

### Option A: Clean Git History (Nuclear Option)
Rewrite all commits to remove secrets. **This will break anyone else's local clones.**

```bash
cd /Users/moltbot/clawd

# Use BFG Repo-Cleaner (safer than git filter-branch)
brew install bfg

# Remove secrets from history
bfg --delete-files '.env.cloudrun'
bfg --delete-files 'ungouge-oauth-credentials.json'
bfg --delete-files 'complete-auth.py'
bfg --delete-files 'get-auth-url.py'
bfg --delete-files 'setup-drive-api.py'

# Force push (destructive)
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin --force --all
```

**Risk:** Destroys existing clones. Anyone with a clone must re-clone.

### Option B: New Repository (Clean Slate)
Create a new repo, copy only current files (no history).

```bash
cd /Users/moltbot

# Create new repo without history
git clone --depth 1 /Users/moltbot/clawd clawd-clean
cd clawd-clean
rm -rf .git
git init
git add -A
git commit -m "Initial commit - clean history"

# Create new GitHub repo
# Push to new repo
git remote add origin https://github.com/v0idwalker37/ish-clawd-clean.git
git push -u origin main
```

**Benefit:** Clean history, no secrets ever committed.  
**Downside:** Lose all git history (not a huge deal for this project).

### Option 3: Ignore and Use Google Drive Backup Only
- Keep committing locally
- Don't push to GitHub
- Use Google Drive as primary backup
- GitHub as secondary (manual zip upload periodically)

**Benefit:** Simplest, no git surgery.  
**Downside:** No GitHub backup until we fix this.

## Recommended Approach

**Option B (New Repository)** is cleanest:
1. Export current state to new repo (no history)
2. All secrets stay local-only
3. Push clean codebase to GitHub
4. Old repo can be archived/deleted

## Secrets That Need Rotation

Since these secrets were committed (even if never pushed publicly), best practice is to rotate them:

1. **Google OAuth credentials** — Generate new client ID/secret in Google Cloud Console
2. **Stripe test key** — Regenerate in Stripe dashboard
3. **Craftsman API credentials** — Verify if production or sandbox

## Next Steps

**Jason:** Choose Option A, B, or C. I can execute whichever you prefer. For now, all work is committed locally and backed up to Google Drive (tonight's session).

---

*Issue documented: Feb 10, 2026 1:25 AM EST*
