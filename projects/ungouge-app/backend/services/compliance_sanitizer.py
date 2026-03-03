"""Compliance sanitizer utilities.

Primary purpose:
- Enforce hardcoded zero-tolerance vocabulary removals for UPPA-adjacent terms.
- Prevent accidental inclusion of prohibited terms in any user-facing output.

This is intentionally simple and deterministic: it does not attempt to
"reinterpret" content; it just removes unsafe tokens.
"""

from __future__ import annotations

import re

# Hard zero-tolerance terms (case-insensitive, whole-word where possible)
PROHIBITED_TERMS = [
    "insurance",
    "deductible",
    "claim",
    "adjuster",
    "settlement",
    "policy",
    "payout",
    "coverage",
    "advocate",
]

# Optional: defamation-risk terms. We remove them rather than rewriting.
DEFAMATION_RISK_TERMS = [
    "fraud",
    "scam",
    "thief",
    "steal",
    "stole",
]


def _compile_terms(terms: list[str]) -> re.Pattern:
    # Word boundary match, but allow pluralization in a minimal way.
    joined = "|".join(re.escape(t) for t in terms)
    return re.compile(rf"\b(?:{joined})s?\b", flags=re.IGNORECASE)


_PROHIBITED_RE = _compile_terms(PROHIBITED_TERMS)
_DEFAMATION_RE = _compile_terms(DEFAMATION_RISK_TERMS)


def sanitize_text(text: str) -> str:
    """Remove prohibited vocabulary from user-facing text."""
    if not text:
        return text

    # Remove prohibited terms
    text = _PROHIBITED_RE.sub("", text)

    # Remove defamation-risk terms (conservative)
    text = _DEFAMATION_RE.sub("", text)

    # Normalize whitespace created by removals
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
