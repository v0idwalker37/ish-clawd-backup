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
from models.report import Report, LineItemAnalysis

logger = logging.getLogger("ungouge.analyzer_ai")

# Valid assessment values (must match models/report.py)
VALID_ASSESSMENTS = {"fair", "slightly_high", "high", "gouging", "suspiciously_low", "unknown"}

SYSTEM_PROMPT = """You are a professional construction cost analyst working for UnGouge.ai, an independent contractor quote analysis service.

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

    return Report(
        id="",  # Set by caller
        project_type=quote.project_type,
        location=quote.location,
        total_quoted=float(data.get("total_quoted", 0)),
        total_fair_low=round(float(data.get("total_fair_low", 0)), 2),
        total_fair_high=round(float(data.get("total_fair_high", 0)), 2),
        overall_assessment=overall,
        line_items=line_analyses,
        created_at="",  # Set by caller
    )


async def analyze_quote(
    quote: QuoteSubmission,
    db: AsyncSession,
) -> Report:
    """
    Main quote analysis function — AI-powered.

    Tries Gemini 2.5 Pro with Search Grounding first (best quality).
    Falls back to Gemini 2.0 Flash (fast, no grounding) on failure.

    Same signature as analyzer_v2.analyze_quote for drop-in replacement.
    """
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
