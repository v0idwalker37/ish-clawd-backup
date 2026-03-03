# Security Audit — 2026-03-03

Scope: OpenClaw runtime + host posture + app dependency quick scan.

## Executive Summary

- **Critical:** OpenClaw skill safety scan flags `skills/evolver` (`capability-evolver`) for dangerous code patterns (exec + env harvesting patterns). Treat as untrusted until reviewed.
- **Warning:** `gateway.trustedProxies` unset. Low impact while gateway remains loopback-only; required if reverse proxy is introduced.
- **Warning (functional/security-adjacent):** Telegram group policy is allowlist with empty allowFrom list (all group messages dropped).
- **Open ports:** OpenClaw loopback ports are local-only; SSH appears bound on all interfaces.
- **Updates:** OpenClaw update available (`2026.3.2`) but requires elevated/system-level install permissions.
- **Memory:** healthy (Gemini embeddings active, vector + FTS ready).

## Commands Run

- `openclaw security audit --deep`
- `openclaw status --deep`
- `openclaw health --json`
- `openclaw memory status --deep`
- `openclaw update status`
- `openclaw cron list --json`
- `openclaw sessions cleanup --agent main --json`
- `openclaw sessions cleanup --agent main --dry-run --enforce --json`
- Host checks: `uname -a`, `/etc/os-release`, `id`, `ss -ltnp`, firewall checks, update checks, disk layout checks.
- Dependency quick scan: frontend `npm audit --omit=dev --audit-level=high --json`, backend `pip check`, `pip list --outdated`.

## Findings

### 1) OpenClaw Security Audit

#### Critical
- `skills.code_safety`: Skill `capability-evolver` contains dangerous patterns (shell execution + env-harvesting indicators).
- Recommendation: quarantine/remove skill directory unless actively trusted and audited.

#### Warn
- `gateway.trusted_proxies_missing`: configure trusted proxy headers if exposing control UI through reverse proxy.

#### Info
- Browser control enabled, elevated tools enabled, webhook hooks disabled.

### 2) Stale Cron / Session Health

- `openclaw cron list` shows **1 active cron job** (`Nightly Memory Cleanup`) and no stale jobs.
- `openclaw sessions cleanup --enforce` pruned **0** sessions. No stale/missing session files under current retention policy.
- Old session entries referencing removed models still exist historically, but there are no active cron jobs using those models.

### 3) Host Posture

- OS: Ubuntu 24.04 LTS.
- Unattended upgrades: **enabled and active**.
- Firewall tools (`ufw`, `firewalld`) not installed; nftables/iptables rules not present in current probe output.
- Listening services include SSH on public interfaces and OpenClaw loopback listeners.
- Disk encryption: no explicit LUKS device observed from non-root checks (needs privileged verification to confirm definitively).

### 4) Dependency Scan

#### Frontend (`npm audit`)
- **2 high vulnerabilities**:
  - `jspdf` (<4.2.0): PDF injection/object injection advisories.
  - `next` (<15.5.10 / <15.0.8 advisory ranges): DoS-related advisories.
- Current app uses Next 14.2.35; update path likely requires careful framework upgrade planning.

#### Backend (Python)
- `pip check`: no broken requirements.
- Many outdated packages present (FastAPI/Starlette/OpenAI/SQLAlchemy/Cryptography/etc.).
- `pip-audit` not installed in current venv, so CVE scan for Python deps is incomplete.

## PII / Ghost Posture Impact

- No immediate evidence of public PII leak in this audit pass.
- Main PII-risk vector is operational exposure (SSH + outdated deps + unvetted skill code), not current branding/code artifacts.

## Recommended Next Actions (Priority Order)

1. Quarantine untrusted skill: `skills/evolver` (critical).
2. Complete OpenClaw upgrade to `2026.3.2` with privileged/system install command.
3. Verify SSH hardening (key-only, no password auth, fail2ban/allowlist) with privileged checks.
4. Decide on host firewall baseline (ufw/nftables) to reduce attack surface.
5. Plan dependency hardening sprint:
   - immediate `jspdf` upgrade to >=4.2.0,
   - Next.js security-track upgrade plan,
   - install/run `pip-audit` for backend CVE map.
6. Optional: set `gateway.trustedProxies` if proxying dashboard externally.

## Blockers

- OpenClaw update attempt from this session failed with EACCES on global install path (`/usr/lib/node_modules/openclaw`).
- Elevated execution is not available from this Telegram session context.
