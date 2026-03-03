"""
Quote Analysis Service — AI-Powered (Gemini 2.5 Pro + Search Grounding)

Uses Google's Gemini 2.5 Pro model with real-time Google Search grounding
to analyze contractor quotes against current market data.

Primary: Gemini 2.5 Pro with Search Grounding (best accuracy, ~$0.026/analysis)
Fallback: Gemini 2.0 Flash without grounding (fast, ~$0.001/analysis)

Source citations from grounding are used for accuracy but STRIPPED from
customer-facing output to avoid legal liability.

Drop-in replacement: same function signature as analyzer_v2.analyze_quote.
"""

import json
import logging
import os
import re
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.quote import QuoteSubmission
from models.report import Report, LineItemAnalysis, TypicalCostItem

logger = logging.getLogger("ungouge.analyzer_ai")

# Valid assessment values (must match models/report.py)
VALID_ASSESSMENTS = {"fair", "slightly_high", "high", "gouging", "suspiciously_low", "unknown"}

SYSTEM_PROMPT = """You are a professional construction cost analyst working for GougeAlert, an independent contractor quote analysis service.

Analyze the provided contractor quote by comparing each line item against current fair market rates for the specified location.

Use Google Search to look up current construction costs, labor rates, and material prices for the specified location. Ground your analysis in real, current data.

Return ONLY a valid JSON object (no markdown, no code fences, no other text) with this exact structure:
{
  "line_items": [
    {
      "item_name": "string — exact name from the quote",
      "quoted_price": number,
      "fair_price_low": number,
      "fair_price_high": number,
      "assessment": "fair|slightly_high|high|gouging|suspiciously_low",
      "explanation": "2-3 sentence explanation with specific reasoning based on current market data for the area. Do NOT cite specific website names or URLs."
    }
  ],
  "total_quoted": number,
  "total_fair_low": number,
  "total_fair_high": number,
  "overall_assessment": "Multi-paragraph assessment including:\\n- Summary of the quote's overall fairness\\n- Specific red flags identified\\n- Actionable recommendations for the homeowner\\n\\nDo NOT cite specific website names or URLs in the assessment.",
  "fairness_score": number (0-100, where 100 = perfectly fair, 0 = extreme gouging or suspiciously low)
}

CRITICAL RULES:
- Use REAL current regional pricing for the specified location (labor rates, material costs, cost-of-living adjustments)
- $0 line items likely mean the cost is bundled into other items — mark as "fair" and note this, do NOT mark as gouging
- Consider the FULL project scope — a multi-room renovation is major work, price accordingly
- Be specific in explanations: reference typical costs per square foot, typical labor hours, material price ranges
- Fair price ranges should reflect actual current market rates, NOT just +/- 30% of the quoted price
- Line items like "Bathroom 1" or "Kitchen remodel" mean FULL renovations, not minor updates
- The assessment must be one of: fair, slightly_high, high, gouging, suspiciously_low
- Do NOT include any website names, URLs, or specific source citations in explanations or the overall assessment
- Use phrases like "based on current market data" or "according to regional cost databases" instead of naming sources
- Return ONLY valid JSON — no markdown code fences, no commentary before or after the JSON"""


def _build_user_prompt(quote: QuoteSubmission) -> str:
    """Build the user prompt from a QuoteSubmission."""
    items_json = json.dumps([
        {
            "item_name": item.item_name,
            "quoted_price": float(item.quoted_price),
            "quantity": item.quantity or 1,
            "unit": item.unit or "item",
            "description": item.description or "",
        }
        for item in quote.line_items
    ], indent=2)

    total = sum(float(item.quoted_price) for item in quote.line_items)

    return f"""Analyze this contractor quote:

Project Type: {quote.project_type}
Location: {quote.location}
Contractor: {quote.contractor_name or "Not specified"}
Total Quoted: ${total:,.2f}
Number of Line Items: {len(quote.line_items)}

Line Items:
{items_json}"""


def _sanitize_assessment(assessment: str) -> str:
    """Ensure assessment is a valid enum value."""
    cleaned = assessment.strip().lower().replace(" ", "_")
    # Handle common AI variations
    mapping = {
        "slightly_low": "suspiciously_low",
        "low": "suspiciously_low",
        "very_high": "gouging",
        "overpriced": "gouging",
        "moderate": "fair",
        "reasonable": "fair",
    }
    result = mapping.get(cleaned, cleaned)
    return result if result in VALID_ASSESSMENTS else "unknown"


def _strip_citations(text: str) -> str:
    """Remove any source citations, URLs, or website names from text."""
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove "according to [site]" patterns
    text = re.sub(r'(?i)according to \S+\.(?:com|org|net|io)\b[,.]?', 'Based on current market data,', text)
    # Remove "per [site]" patterns
    text = re.sub(r'(?i)per \S+\.(?:com|org|net|io)\b[,.]?', 'per current market data,', text)
    # Remove "[site].com" references
    text = re.sub(r'\b\S+\.(?:com|org|net|io)\b', '', text)
    # Clean up double spaces
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def _parse_json_response(text: str) -> dict:
    """Parse JSON from AI response, handling markdown fences and other wrapping."""
    # Strip markdown code fences
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n", 1)
        text = lines[1] if len(lines) > 1 else text
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3]
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the text
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from AI response (length={len(text)})")


# ── Total-Only (Estimated) Quote Analysis ─────────────────────────────────
# When a homeowner submits a quote with only a total price and no per-item
# costs, we analyze the TOTAL against market rates and provide educational
# cost ranges for each work item — NOT fake per-item ratings.

ESTIMATED_SYSTEM_PROMPT = """You are a professional construction cost analyst working for GougeAlert.

A homeowner received a contractor quote with ONLY a total price — no per-item costs were provided. Your job is to:

1. Assess whether the TOTAL quoted price is fair for this type of project in this location
2. Provide typical cost ranges for each work item mentioned, as educational guidance
3. Give actionable recommendations

Use Google Search to look up current construction costs, labor rates, and material prices for the specified location. Ground your analysis in real, current data.

Return ONLY a valid JSON object (no markdown, no code fences):
{
  "total_quoted": number,
  "total_fair_low": number (low end of fair total for this whole project),
  "total_fair_high": number (high end of fair total for this whole project),
  "overall_assessment": "Multi-paragraph assessment covering:\\n- Is the total price fair for this project type and location?\\n- Key cost drivers in this area\\n- Any red flags based on the total alone\\n- ALWAYS recommend requesting an itemized breakdown\\n\\nDo NOT cite specific website names or URLs.",
  "typical_costs": [
    {
      "item_name": "exact item name from the work items list",
      "typical_low": number (low end of what this item typically costs in this area),
      "typical_high": number (high end of what this item typically costs in this area),
      "description": "2-3 sentences: what this item typically includes (materials, labor, etc.), factors that affect cost, and how to evaluate quotes for this item. Do NOT cite specific websites."
    }
  ],
  "fairness_score": number (0-100, where 100 = perfectly fair)
}

CRITICAL RULES:
- Use REAL current regional pricing for the specified location
- The typical_costs are INDEPENDENT educational data — they do NOT need to sum to the total
- Each typical cost range reflects what a homeowner would typically pay for JUST that item alone
- Be specific: reference cost per sq ft, typical labor hours, material price ranges
- Consider the full scope — "Bathroom 1" means a FULL bathroom renovation
- Do NOT cite specific website names or URLs
- The overall_assessment MUST mention that no itemized breakdown was provided
- ALWAYS recommend the homeowner request an itemized quote for better analysis
- Return ONLY valid JSON"""


def _build_estimated_prompt(quote: QuoteSubmission) -> str:
    """Build the user prompt for a total-only quote — sends item names but NOT prices."""
    total = sum(float(item.quoted_price) for item in quote.line_items)

    # Send work item names and descriptions but NOT the AI-estimated prices
    items_desc = "\n".join(
        f"- {item.item_name}" + (f": {item.description}" if item.description else "")
        for item in quote.line_items
    )

    return f"""Analyze this contractor quote. The homeowner received ONLY a total price — no per-item costs.

Project Type: {quote.project_type}
Location: {quote.location}
Contractor: {quote.contractor_name or "Not specified"}
Total Quoted: ${total:,.2f}

Work items described in the quote (no individual pricing provided):
{items_desc}

Please assess:
1. Is ${total:,.2f} a fair total for a {quote.project_type} in {quote.location}?
2. What does each of these items typically cost in {quote.location}?"""


async def _analyze_estimated_with_gemini_pro(quote: QuoteSubmission) -> dict:
    """Analyze a total-only quote using Gemini 2.5 Pro with Search Grounding."""
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction=ESTIMATED_SYSTEM_PROMPT,
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=_build_estimated_prompt(quote),
        config=config,
    )

    usage = response.usage_metadata
    logger.info(
        "gemini_pro_estimated_analysis_complete",
        extra={
            "input_tokens": usage.prompt_token_count,
            "output_tokens": usage.candidates_token_count,
            "thinking_tokens": getattr(usage, 'thoughts_token_count', 0) or 0,
            "is_estimated": True,
        },
    )

    return _parse_json_response(response.text)


async def _analyze_estimated_with_gemini_flash(quote: QuoteSubmission) -> dict:
    """Fallback: Gemini 2.0 Flash for total-only quotes."""
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction=ESTIMATED_SYSTEM_PROMPT,
        response_mime_type="application/json",
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=_build_estimated_prompt(quote),
        config=config,
    )

    usage = response.usage_metadata
    logger.info(
        "gemini_flash_estimated_fallback_complete",
        extra={
            "input_tokens": usage.prompt_token_count,
            "output_tokens": usage.candidates_token_count,
            "is_estimated": True,
        },
    )

    return _parse_json_response(response.text)


def _build_estimated_report(quote: QuoteSubmission, data: dict) -> Report:
    """Build Report for a total-only quote — total-level analysis + educational ranges."""
    overall = _strip_citations(data.get("overall_assessment", "Analysis complete."))
    try:
        from services.compliance_sanitizer import sanitize_text
        overall = sanitize_text(overall)
    except Exception:
        pass

    original_total = sum(float(item.quoted_price) for item in quote.line_items)
    ai_total = float(data.get("total_quoted", 0))
    total_quoted = original_total if original_total > 0 else ai_total

    # Build educational typical costs
    typical_costs = []
    for item in data.get("typical_costs", []):
        desc = _strip_citations(item.get("description", ""))
        try:
            from services.compliance_sanitizer import sanitize_text
            desc = sanitize_text(desc)
        except Exception:
            pass

        typical_costs.append(TypicalCostItem(
            item_name=item.get("item_name", "Unknown"),
            typical_low=round(float(item.get("typical_low", 0)), 2),
            typical_high=round(float(item.get("typical_high", 0)), 2),
            description=desc,
        ))

    return Report(
        id="",
        project_type=quote.project_type,
        location=quote.location,
        total_quoted=total_quoted,
        total_fair_low=round(float(data.get("total_fair_low", 0)), 2),
        total_fair_high=round(float(data.get("total_fair_high", 0)), 2),
        overall_assessment=overall,
        line_items=[],  # No per-item analysis for total-only quotes
        typical_costs=typical_costs,
        created_at="",
        is_estimated=True,
        estimation_confidence=quote.estimation_confidence,
        estimation_methodology=quote.estimation_methodology,
    )


async def _analyze_estimated_quote(quote: QuoteSubmission) -> Report:
    """Full analysis flow for total-only quotes — total assessment + educational ranges."""
    # Primary: Gemini 2.5 Pro with grounding
    try:
        logger.info(
            "starting_estimated_analysis",
            extra={
                "engine": "gemini-2.5-pro+grounding",
                "project_type": quote.project_type,
                "location": quote.location,
                "work_items": len(quote.line_items),
            },
        )
        data = await _analyze_estimated_with_gemini_pro(quote)
        return _build_estimated_report(quote, data)
    except Exception as e:
        logger.warning(
            "estimated_gemini_pro_failed",
            extra={"error": str(e), "error_type": type(e).__name__},
        )

    # Fallback: Gemini 2.0 Flash
    try:
        logger.info("estimated_falling_back_to_flash")
        data = await _analyze_estimated_with_gemini_flash(quote)
        return _build_estimated_report(quote, data)
    except Exception as e:
        logger.error(
            "estimated_all_analyzers_failed",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        raise RuntimeError(f"Estimated quote analysis failed: {e}")


async def _analyze_with_gemini_pro(quote: QuoteSubmission) -> dict:
    """
    Primary analyzer: Gemini 2.5 Pro with Google Search Grounding.
    
    Uses real-time web search for current pricing data.
    ~$0.026/analysis, ~70 seconds.
    """
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[types.Tool(google_search=types.GoogleSearch())],
        # Note: response_mime_type="application/json" is incompatible with tools/grounding
    )

    user_prompt = _build_user_prompt(quote)

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=user_prompt,
        config=config,
    )

    # Log grounding metadata (for debugging, not customer-facing)
    if hasattr(response, 'candidates') and response.candidates:
        cand = response.candidates[0]
        gm = getattr(cand, 'grounding_metadata', None)
        if gm:
            queries = getattr(gm, 'web_search_queries', []) or []
            chunks = getattr(gm, 'grounding_chunks', []) or []
            logger.info(
                "gemini_grounding_used",
                extra={
                    "search_queries": len(queries),
                    "sources_cited": len(chunks),
                    "project_type": quote.project_type,
                    "location": quote.location,
                },
            )

    # Log token usage
    usage = response.usage_metadata
    logger.info(
        "gemini_pro_analysis_complete",
        extra={
            "input_tokens": usage.prompt_token_count,
            "output_tokens": usage.candidates_token_count,
            "thinking_tokens": getattr(usage, 'thoughts_token_count', 0) or 0,
        },
    )

    return _parse_json_response(response.text)


async def _analyze_with_gemini_flash(quote: QuoteSubmission) -> dict:
    """
    Fallback analyzer: Gemini 2.0 Flash without grounding.
    
    Fast and cheap, uses training data only.
    ~$0.001/analysis, ~12 seconds.
    """
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        response_mime_type="application/json",  # Can use JSON format without grounding
    )

    user_prompt = _build_user_prompt(quote)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_prompt,
        config=config,
    )

    usage = response.usage_metadata
    logger.info(
        "gemini_flash_fallback_complete",
        extra={
            "input_tokens": usage.prompt_token_count,
            "output_tokens": usage.candidates_token_count,
        },
    )

    return _parse_json_response(response.text)


def _build_report(quote: QuoteSubmission, data: dict) -> Report:
    """Convert parsed AI JSON into a Report model."""
    line_analyses = []

    for item in data.get("line_items", []):
        assessment = _sanitize_assessment(item.get("assessment", "unknown"))
        explanation = _strip_citations(item.get("explanation", ""))
        try:
            from services.compliance_sanitizer import sanitize_text
            explanation = sanitize_text(explanation)
        except Exception:
            # Never fail analysis due to sanitizer
            pass

        line_analyses.append(LineItemAnalysis(
            item_name=item.get("item_name", "Unknown"),
            quoted_price=float(item.get("quoted_price", 0)),
            fair_price_low=round(float(item.get("fair_price_low", 0)), 2),
            fair_price_high=round(float(item.get("fair_price_high", 0)), 2),
            assessment=assessment,
            explanation=explanation,
            bls_rate=0.0,
            material_cost=0.0,
        ))

    overall = _strip_citations(data.get("overall_assessment", "Analysis complete."))
    try:
        from services.compliance_sanitizer import sanitize_text
        overall = sanitize_text(overall)
    except Exception:
        pass

    # IMPORTANT: Use the original quoted total from the submission, NOT the AI's
    # recalculated total. The AI may return a different sum (especially for
    # estimated/total-only quotes). The customer's actual quote price is authoritative.
    original_total = sum(float(item.quoted_price) for item in quote.line_items)
    ai_total = float(data.get("total_quoted", 0))
    
    # Use original total if it's meaningful; fall back to AI's if original is 0
    total_quoted = original_total if original_total > 0 else ai_total
    
    if abs(total_quoted - ai_total) > 1.0:
        logger.warning(
            "total_mismatch_corrected",
            extra={
                "original_total": original_total,
                "ai_total": ai_total,
                "using": "original",
                "project_type": quote.project_type,
            },
        )

    return Report(
        id="",  # Set by caller
        project_type=quote.project_type,
        location=quote.location,
        total_quoted=total_quoted,
        total_fair_low=round(float(data.get("total_fair_low", 0)), 2),
        total_fair_high=round(float(data.get("total_fair_high", 0)), 2),
        overall_assessment=overall,
        line_items=line_analyses,
        created_at="",  # Set by caller
        # Pass through estimation metadata
        is_estimated=quote.is_estimated,
        estimation_confidence=quote.estimation_confidence,
        estimation_methodology=quote.estimation_methodology,
    )


async def analyze_quote(
    quote: QuoteSubmission,
    db: AsyncSession,
) -> Report:
    """
    Main quote analysis function — AI-powered.

    For itemized quotes: per-item analysis with fair/gouging ratings.
    For total-only quotes: total-level assessment + educational cost ranges.

    Tries Gemini 2.5 Pro with Search Grounding first (best quality).
    Falls back to Gemini 2.0 Flash (fast, no grounding) on failure.

    Same signature as analyzer_v2.analyze_quote for drop-in replacement.
    """
    # Total-only quotes get a different analysis flow
    if getattr(quote, 'is_estimated', False):
        return await _analyze_estimated_quote(quote)

    # Primary: Gemini 2.5 Pro with grounding
    try:
        logger.info(
            "starting_ai_analysis",
            extra={
                "engine": "gemini-2.5-pro+grounding",
                "project_type": quote.project_type,
                "location": quote.location,
                "line_items": len(quote.line_items),
            },
        )
        data = await _analyze_with_gemini_pro(quote)
        return _build_report(quote, data)

    except Exception as e:
        logger.warning(
            "gemini_pro_failed_trying_flash",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "project_type": quote.project_type,
            },
        )

    # Fallback: Gemini 2.0 Flash
    try:
        logger.info("falling_back_to_gemini_flash")
        data = await _analyze_with_gemini_flash(quote)
        return _build_report(quote, data)

    except Exception as e:
        logger.error(
            "all_ai_analyzers_failed",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "project_type": quote.project_type,
                "location": quote.location,
            },
        )
        raise RuntimeError(f"AI analysis failed: {e}")
