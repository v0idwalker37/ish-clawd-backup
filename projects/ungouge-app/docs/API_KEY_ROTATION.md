# API Key Rotation - Post Security Audit

**Status:** In Progress  
**Date Started:** 2026-02-02  
**Reason:** Migrate personal → business accounts, post-security-audit best practice

---

## Priority 1: Gemini API Key

**Current:** None (OpenAI 4o was being tested)  
**Target:** Google Gemini API via ungouge.ai workspace

**Steps:**
- [ ] Sign into https://aistudio.google.com/app/apikey with ungouge.ai account
- [ ] Create new API key
- [ ] Add to `backend/.env` as `GEMINI_API_KEY`
- [ ] Test extraction on sample quotes
- [ ] Remove old OpenAI key from `.env` (if present)

---

## Priority 2: Stripe API Keys

**Current:** Unknown (check if personal or business)  
**Target:** Stripe account under ungouge.ai business

**Steps:**
- [ ] Verify current Stripe account ownership
- [ ] If personal: Create new Stripe business account
- [ ] Generate new API keys (test + live)
- [ ] Update `backend/.env` with new keys
- [ ] Test payment flow end-to-end
- [ ] Revoke old keys

**Notes:**
- Test mode keys first, live keys only after full verification
- Update webhook secrets if using Stripe webhooks

---

## Priority 3: Email Service (SendGrid/Mailgun/etc.)

**Current:** Unknown (check backend config)  
**Target:** Business account for transactional emails

**Steps:**
- [ ] Identify current email provider
- [ ] Create business account (or verify existing)
- [ ] Generate new API key
- [ ] Update `backend/.env`
- [ ] Test quote delivery emails
- [ ] Verify SPF/DKIM/DMARC records
- [ ] Revoke old key

---

## Priority 4: GitHub Tokens/Deploy Keys

**Current:** Unknown (check if any exist)  
**Target:** Business GitHub account or org

**Steps:**
- [ ] Audit existing GitHub tokens (`gh auth status`)
- [ ] If using personal tokens, create org/business account
- [ ] Generate new personal access tokens or deploy keys
- [ ] Update CI/CD configs if applicable
- [ ] Revoke old tokens

---

## Priority 5: Database Credentials

**Current:** Recently created (likely already secure)  
**Target:** Verify strength, document rotation process

**Steps:**
- [ ] Verify Supabase credentials are in `.env` (not hardcoded)
- [ ] Document credential location
- [ ] Set calendar reminder for 90-day rotation
- [ ] Test connection with current creds

---

## Checklist Completion

**Completed:**
- None yet

**In Progress:**
- Gemini API key (waiting on Jason)

**Blocked:**
- All others (need to audit current setup first)

---

## Post-Rotation Verification

After rotating each key:
1. Test the affected service end-to-end
2. Verify no hardcoded references remain
3. Update documentation
4. Revoke old key
5. Monitor logs for any auth failures

---

## Security Notes

- All keys stored in `.env` files (gitignored)
- Never commit keys to git history
- Use different keys for dev/staging/production
- Set calendar reminders for 90-day rotation cycle
- Document key owners and rotation procedures
