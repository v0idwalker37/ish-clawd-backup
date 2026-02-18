# Security Guidelines

## Credentials Storage

### ✅ SECURE (Current Setup)

All API keys and secrets are stored in:
- **Backend:** `.env` file (gitignored, owner-only permissions)
- **Environment variables** loaded via `os.getenv()`
- No hardcoded secrets in source code

### 📋 API Keys Inventory

**Development:**
- Craftsman API (sandbox): Stored in `.env`
- OpenAI API: To be added when needed
- Stripe (test mode): To be added when payment implemented

**Production (future):**
- Use environment variables on hosting platform (Railway, Vercel, etc.)
- Rotate all keys before production launch
- Use production Craftsman API ($350/mo or $2K/year raw data)

## File Permissions

Sensitive config files are set to owner-only (600):
```bash
chmod 600 backend/.env
chmod 600 ~/.config/moltbook/credentials.json
chmod 600 ~/clawd/skills/email/config.json
```

## .gitignore Coverage

The following are excluded from git:
- `.env` and `.env.local` files
- `config.json` files in skills directories
- Database files (`*.db`, `*.sqlite`)
- `node_modules/` and `venv/`

## Pre-Production Checklist

Before deploying to production:

1. **Generate strong secrets:**
   ```bash
   openssl rand -hex 32  # For JWT_SECRET_KEY
   ```

2. **Rotate all API keys:**
   - Get production Craftsman API key
   - Switch Stripe to live mode keys
   - Generate new JWT secret

3. **Environment Variables:**
   - Set all secrets as environment variables on hosting platform
   - Never commit `.env` to git
   - Document required env vars in `.env.example`

4. **Database:**
   - Use PostgreSQL in production (not SQLite)
   - Store connection string in environment variable
   - Enable SSL/TLS for database connections

5. **HTTPS:**
   - Enforce HTTPS in production
   - Set secure cookie flags
   - Enable HSTS headers

## Incident Response

If credentials are accidentally exposed:

1. **Immediately rotate** the compromised key
2. **Check git history** for commits containing secrets
3. **Use BFG Repo-Cleaner** to remove from git history if needed
4. **Monitor** for unauthorized usage
5. **Document** the incident and lessons learned

## Contact

Security concerns: Jason Trask (jasontrask@gmail.com)
