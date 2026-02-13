"""
Quote Analysis Service V2 — Uses QuoteAnalyzer engine

Wraps the standalone QuoteAnalyzer to provide the same interface as
the original services/analyzer.py but with the new analysis engine
(67.7% accuracy, 87% line item match rate, 26.7ms average).

Drop-in replacement: same function signature, same return types.
"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from models.quote import QuoteSubmission, LineItem
from models.report import Report, LineItemAnalysis
from quote_analyzer import QuoteAnalyzer

logger = logging.getLogger("ungouge.analyzer_v2")

# Singleton analyzer instance (loads cost models once)
_analyzer: Optional[QuoteAnalyzer] = None


def _get_analyzer() -> QuoteAnalyzer:
    """Get or create the QuoteAnalyzer singleton."""
    global _analyzer
    if _analyzer is None:
        _analyzer = QuoteAnalyzer()
        logger.info("QuoteAnalyzer engine loaded (v2)")
    return _analyzer


def _map_verdict_to_assessment(verdict: str) -> str:
    """Map QuoteAnalyzer verdict to the assessment strings the frontend expects."""
    mapping = {
        "fair": "fair",
        "good_deal": "fair",
        "slightly_high": "slightly_high",
        "high": "high",
        "overpriced": "gouging",
        "suspiciously_low": "suspiciously_low",
        "error": "unknown",
    }
    return mapping.get(verdict, "unknown")


def _map_item_status(item_result: dict) -> str:
    """Map a line item analysis status to the assessment string."""
    status = item_result.get("status", "unknown")
    mapping = {
        "within_range": "fair",
        "below_range": "suspiciously_low",
        "slightly_above": "slightly_high",
        "above_range": "high",
        "well_above": "gouging",
        "no_match": "unknown",
    }
    return mapping.get(status, "unknown")


async def analyze_quote(
    quote: QuoteSubmission,
    db: AsyncSession,
) -> Report:
    """
    Main quote analysis function — V2 engine.

    Same signature as services/analyzer.analyze_quote so it can be
    swapped in without changing the router.
    """
    analyzer = _get_analyzer()

    # Convert QuoteSubmission line items to the format the engine expects
    engine_items = []
    for item in quote.line_items:
        engine_items.append({
            "description": item.item_name,
            "cost": float(item.quoted_price),
        })

    # Run analysis
    result = analyzer.analyze(
        project_type=quote.project_type,
        line_items=engine_items,
        region=quote.location,
        total=None,  # Let the engine sum line items
        project_size="medium",
    )

    # Convert engine output to Report model
    line_analyses = []
    total_quoted = 0.0
    total_fair_low = 0.0
    total_fair_high = 0.0

    for item_result in result.get("line_item_analysis", []):
        quoted = item_result.get("quoted_cost", 0.0)
        fair_low = item_result.get("range_low", quoted * 0.7)
        fair_high = item_result.get("range_high", quoted * 1.1)
        assessment = _map_item_status(item_result)

        # Build explanation
        explanation = item_result.get("explanation", "")
        if not explanation:
            matched = item_result.get("matched_category", "")
            confidence = item_result.get("confidence", 0)
            if matched:
                explanation = (
                    f"Matched to '{matched}' (confidence: {confidence:.0%}). "
                    f"Fair range: ${fair_low:,.0f}–${fair_high:,.0f}."
                )
            else:
                explanation = (
                    f"No match found in cost database. "
                    f"We recommend getting 2–3 additional quotes for this item."
                )

        line_analyses.append(LineItemAnalysis(
            item_name=item_result.get("description", "Unknown"),
            quoted_price=quoted,
            fair_price_low=round(fair_low, 2),
            fair_price_high=round(fair_high, 2),
            assessment=assessment,
            explanation=explanation,
            bls_rate=0.0,
            material_cost=0.0,
        ))

        total_quoted += quoted
        total_fair_low += fair_low
        total_fair_high += fair_high

    # Use engine's total analysis if available
    total_analysis = result.get("total_analysis", {})
    if total_analysis:
        total_quoted = total_analysis.get("quoted_total", total_quoted)
        if "expected_low" in total_analysis:
            total_fair_low = total_analysis["expected_low"]
        if "expected_high" in total_analysis:
            total_fair_high = total_analysis["expected_high"]

    # Build overall assessment from engine summary
    overall_assessment = result.get("summary", "")
    if not overall_assessment:
        verdict = result.get("verdict", "unknown")
        score = result.get("fairness_score", 0)
        overall_assessment = (
            f"## Overall Assessment: {verdict.upper()}\n\n"
            f"**Fairness Score:** {score}/100\n"
            f"**Total Quoted:** ${total_quoted:,.2f}\n"
            f"**Fair Range:** ${total_fair_low:,.2f} – ${total_fair_high:,.2f}\n\n"
        )

        # Add red flags
        red_flags = result.get("red_flags", [])
        if red_flags:
            overall_assessment += "### 🚨 Red Flags\n"
            for flag in red_flags:
                if isinstance(flag, dict):
                    overall_assessment += f"• {flag.get('message', str(flag))}\n"
                else:
                    overall_assessment += f"• {flag}\n"
            overall_assessment += "\n"

        # Add recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            overall_assessment += "### Recommendations\n"
            for rec in recommendations:
                if isinstance(rec, dict):
                    overall_assessment += f"• {rec.get('message', str(rec))}\n"
                else:
                    overall_assessment += f"• {rec}\n"

    return Report(
        id="",  # Set by caller
        project_type=quote.project_type,
        location=quote.location,
        total_quoted=total_quoted,
        total_fair_low=total_fair_low,
        total_fair_high=total_fair_high,
        overall_assessment=overall_assessment,
        line_items=line_analyses,
        created_at="",  # Set by caller
    )
