# Claude.ai Extended Thinking Codebase Review Prompt

**Instructions:** Copy this prompt into claude.ai (with extended thinking enabled), then paste the files below it.

---

## The Prompt

```
I need a thorough code review of my Ungouge.ai backend codebase. This is a quote verification tool for homeowners - they submit contractor quotes, we analyze them against market data and return a fairness report.

**Tech Stack:** Python FastAPI backend, Next.js frontend, SQLite database

**Your Task:**
1. **Security Audit** - Authentication flows, input validation, SQL injection risks, XSS vectors
2. **Architecture Review** - Code organization, separation of concerns, dependency injection patterns
3. **Error Handling** - Exception coverage, graceful degradation, user-facing error messages
4. **Performance** - N+1 queries, unnecessary computations, caching opportunities
5. **Code Quality** - DRY violations, dead code, unclear naming, missing type hints
6. **Business Logic** - Quote analysis accuracy, edge cases in cost matching, data validation gaps

**Priority Focus Areas:**
- The analyzer service (core business logic)
- Authentication (security-critical)
- Quote parsing (reliability)
- Cost model matching (accuracy)

**Output Format:**
For each issue found, provide:
- **Severity:** Critical / High / Medium / Low
- **Location:** File and line numbers
- **Issue:** What's wrong
- **Fix:** Specific code change or approach

After individual issues, provide:
- **Top 5 Most Critical Fixes** (do these first)
- **Architecture Recommendations** (longer-term improvements)
- **Security Hardening Checklist**

Be thorough but actionable. I can handle harsh feedback - I want this production-ready.
```

---

## Files to Paste (Priority Order)

### Critical Files (~3,500 lines total - fits easily)

1. **backend/services/analyzer.py** (650 lines) - Core quote analysis logic
2. **backend/routers/auth.py** (1152 lines) - Authentication endpoints
3. **backend/routers/quotes.py** (437 lines) - Quote API endpoints  
4. **backend/exceptions.py** (489 lines) - Error handling
5. **backend/validators.py** (471 lines) - Input validation
6. **backend/services/auth.py** (205 lines) - Auth service

### Secondary Files (add if context window allows)

7. **backend/services/quote_parser_gemini.py** (249 lines) - Gemini parsing
8. **backend/services/synonym_matcher.py** (224 lines) - Fuzzy matching
9. **backend/models/auth.py** (229 lines) - Auth data models
10. **backend/main.py** (~100 lines) - FastAPI app setup

### Data Files (reference only, don't paste full)

- **backend/data/project_cost_models.json** (4593 lines) - 14 project types with material/labor data

---

## Quick Copy Commands

Run these to copy each file:

```bash
# Core files (copy one at a time, paste into Claude)
cat backend/services/analyzer.py | pbcopy
cat backend/routers/auth.py | pbcopy
cat backend/routers/quotes.py | pbcopy
cat backend/exceptions.py | pbcopy
cat backend/validators.py | pbcopy
cat backend/services/auth.py | pbcopy
```

---

## Alternative: Concatenate All Core Files

```bash
cd /Users/moltbot/clawd/projects/ungouge-app

# Create single file with all core backend code
cat << 'HEADER' > /tmp/ungouge-review.txt
=== UNGOUGE.AI BACKEND CODEBASE ===
Files included:
1. backend/services/analyzer.py - Core quote analysis
2. backend/routers/auth.py - Auth endpoints
3. backend/routers/quotes.py - Quote endpoints
4. backend/exceptions.py - Error handling
5. backend/validators.py - Input validation
6. backend/services/auth.py - Auth service
7. backend/services/quote_parser_gemini.py - Gemini parsing
8. backend/services/synonym_matcher.py - Fuzzy matching
9. backend/models/auth.py - Auth models
10. backend/main.py - App setup
=====================================

HEADER

for f in backend/services/analyzer.py backend/routers/auth.py backend/routers/quotes.py backend/exceptions.py backend/validators.py backend/services/auth.py backend/services/quote_parser_gemini.py backend/services/synonym_matcher.py backend/models/auth.py backend/main.py; do
  echo -e "\n\n========== $f ==========\n" >> /tmp/ungouge-review.txt
  cat "$f" >> /tmp/ungouge-review.txt
done

# Copy to clipboard
cat /tmp/ungouge-review.txt | pbcopy
echo "All files copied to clipboard! (~4,500 lines)"
```

Then paste into claude.ai after the review prompt.

---

## Estimated Token Usage

- Prompt: ~500 tokens
- Code files: ~18,000 tokens (4,500 lines × 4 tokens/line)
- **Total Input:** ~18,500 tokens
- Claude.ai context: 200K tokens
- **Plenty of room** for extended thinking output

---

*Created by Ish for Ungouge.ai codebase review*
