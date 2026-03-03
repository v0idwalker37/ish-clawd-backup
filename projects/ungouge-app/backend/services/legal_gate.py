"""Deterministic legal/compliance gate for customer-facing report text.

This is a lightweight enforcement layer for MVP-guarded rollout.
It does NOT provide legal advice and is not a replacement for counsel.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from models.report import Report
from services.compliance_sanitizer import sanitize_text

REQUIRED_REPORT_DISCLAIMER = (
    "This report is informational only and is not legal, insurance-adjusting, "
    "engineering, or public-adjusting advice. Weather and imagery inputs are "
    "contextual indicators and do not determine property damage causation."
)

# Hard-risk phrase families for deterministic blocks.
_BLOCK_PATTERNS = [
    r"\b(proves?|confirmed?|guaranteed?)\b.*\b(damage|caused|causation)\b",
    r"\b(you should sue|legal case|legally entitled|force settlement)\b",
    r"\b(we negotiate|we file|we appeal)\b.*\b(claim|insurer|insurance)\b",
    r"\b(contractor\s+\w+\s+is\s+(a\s+)?(fraud|scam|criminal|thief))\b",
]

# Public PII patterns (coarse).
_PII_PATTERNS = [
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",  # email
    r"\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",  # US phone
]


def _text_blob(report: Report) -> str:
    parts = [report.overall_assessment or ""]
    for item in report.line_items or []:
        parts.append(item.explanation or "")
    for t in report.typical_costs or []:
        parts.append(t.description or "")
    return "\n".join(parts)


def evaluate_report_policy(report: Report) -> Dict[str, object]:
    text = _text_blob(report)
    hits: List[str] = []

    for pat in _BLOCK_PATTERNS:
        if re.search(pat, text, flags=re.IGNORECASE):
            hits.append(f"block:{pat}")

    for pat in _PII_PATTERNS:
        if re.search(pat, text, flags=re.IGNORECASE):
            hits.append(f"pii:{pat}")

    decision = "PASS" if not hits else "PASS_WITH_EDIT"
    return {"decision": decision, "reasons": hits}


def enforce_report_policy(report: Report) -> Tuple[Report, Dict[str, object]]:
    """Apply deterministic sanitization and disclaimer enforcement.

    Returns:
      (possibly modified report, audit dict)
    """
    audit = evaluate_report_policy(report)

    # Always sanitize report text with compliance sanitizer
    report.overall_assessment = sanitize_text(report.overall_assessment or "")

    for item in report.line_items or []:
        item.explanation = sanitize_text(item.explanation or "")

    for t in report.typical_costs or []:
        t.description = sanitize_text(t.description or "")

    # If risky content detected, replace with neutral safe summary
    if audit["decision"] == "PASS_WITH_EDIT":
        report.overall_assessment = (
            "Your quote has been analyzed using market context and pricing ranges. "
            "Please use these results as guidance and consult licensed professionals "
            "for formal determinations."
        )

    # Ensure disclaimer exists exactly once
    if REQUIRED_REPORT_DISCLAIMER.lower() not in (report.overall_assessment or "").lower():
        report.overall_assessment = (report.overall_assessment or "").strip()
        if report.overall_assessment:
            report.overall_assessment += "\n\n"
        report.overall_assessment += REQUIRED_REPORT_DISCLAIMER

    return report, audit
