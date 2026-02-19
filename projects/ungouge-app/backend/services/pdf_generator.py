"""
PDF Report Generator for UnGouge
Generates branded PDF reports from quote analysis data using ReportLab.

V2 — Overhauled for AI-powered analysis output:
  - Structured overall assessment (paragraphs, bullets, numbered recs)
  - Full explanation text (no truncation)
  - Row highlighting for gouging/issues
  - Title-cased project types
  - Clean currency formatting ($7,000 not $7,000.00)
  - Page numbers
  - Zebra-striped table rows
"""

import re
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    PageBreak,
)

from models.report import Report


# ── Brand Colors ──────────────────────────────────────────────
BRAND_PRIMARY = colors.HexColor("#1E40AF")
BRAND_SECONDARY = colors.HexColor("#3B82F6")
BRAND_ACCENT = colors.HexColor("#059669")        # Emerald-600
BRAND_WARNING = colors.HexColor("#D97706")        # Amber-600
BRAND_DANGER = colors.HexColor("#DC2626")         # Red-600
BRAND_DARK = colors.HexColor("#1F2937")
BRAND_LIGHT_BG = colors.HexColor("#F0F7FF")
BRAND_TABLE_HEADER = colors.HexColor("#1E3A5F")
WHITE = colors.white

ASSESSMENT_COLORS = {
    "fair": BRAND_ACCENT,
    "slightly_high": BRAND_WARNING,
    "high": colors.HexColor("#EA580C"),           # Orange-600
    "gouging": BRAND_DANGER,
    "suspiciously_low": colors.HexColor("#2563EB"),
    "unknown": colors.HexColor("#6B7280"),
}

ASSESSMENT_LABELS = {
    "fair": "✓ Fair Price",
    "slightly_high": "⚠ Slightly High",
    "high": "⚠ High",
    "gouging": "✗ Possible Gouge",
    "suspiciously_low": "↓ Suspiciously Low",
    "unknown": "? Unknown",
}

# Row background tints for critical assessments
ASSESSMENT_ROW_BG = {
    "gouging": colors.HexColor("#FEE2E2"),       # Red-100
    "high": colors.HexColor("#FFEDD5"),           # Orange-100
    "suspiciously_low": colors.HexColor("#DBEAFE"),  # Blue-100
}


def _build_styles():
    """Build custom paragraph styles for the PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "BrandTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=26,
        textColor=BRAND_PRIMARY,
        spaceAfter=4,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        "BrandSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        textColor=colors.HexColor("#6B7280"),
        spaceAfter=16,
    ))
    styles.add(ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=BRAND_PRIMARY,
        spaceBefore=20,
        spaceAfter=8,
        borderPadding=(0, 0, 4, 0),
    ))
    styles.add(ParagraphStyle(
        "SubHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=BRAND_DARK,
        spaceBefore=10,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "BodyText_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=BRAND_DARK,
        leading=14,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=BRAND_DARK,
        leading=14,
        leftIndent=18,
        spaceAfter=3,
        bulletIndent=6,
    ))
    styles.add(ParagraphStyle(
        "NumberedText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=BRAND_DARK,
        leading=14,
        leftIndent=24,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "RedFlagText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#991B1B"),
        leading=14,
        spaceAfter=6,
        leftIndent=12,
        borderPadding=(4, 8, 4, 8),
    ))
    styles.add(ParagraphStyle(
        "SmallGray",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=colors.HexColor("#9CA3AF"),
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=BRAND_DARK,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        "CellTextBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=BRAND_DARK,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        "CellExplanation",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=colors.HexColor("#374151"),
        leading=11,
    ))
    styles.add(ParagraphStyle(
        "FooterText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=colors.HexColor("#9CA3AF"),
        alignment=TA_CENTER,
    ))
    return styles


def _fmt_currency(value: float) -> str:
    """Format a number as USD currency — no cents for round numbers."""
    if value == 0:
        return "$0"
    if value == int(value):
        return f"${int(value):,}"
    return f"${value:,.2f}"


def _title_case_project(raw: str) -> str:
    """Convert 'home_remodel' → 'Home Remodel'."""
    return raw.replace("_", " ").title()


def _assessment_badge(assessment: str) -> str:
    """Return a styled assessment label for use in Paragraphs."""
    label = ASSESSMENT_LABELS.get(assessment, assessment)
    color_hex = ASSESSMENT_COLORS.get(assessment, colors.gray)
    if hasattr(color_hex, "hexval"):
        hex_str = color_hex.hexval()
    else:
        hex_str = str(color_hex)
    return f'<font color="{hex_str}"><b>{label}</b></font>'


def _parse_date(date_str: str) -> str:
    """Parse ISO date string to human-readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except (ValueError, AttributeError):
        return date_str


def _savings_color_hex(overpay: float) -> str:
    if overpay > 0:
        return "#DC2626"
    return "#059669"


def _add_page_number(canvas, doc):
    """Add page number to bottom of each page."""
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#9CA3AF"))
    canvas.drawCentredString(letter[0] / 2, 0.4 * inch, text)
    canvas.restoreState()


def _build_header(report: Report, styles):
    """Build the branded header section."""
    elements = []
    elements.append(Paragraph("UnGouge<font color='#3B82F6'>.ai</font>", styles["BrandTitle"]))
    elements.append(Paragraph(
        "Independent Contractor Quote Analysis",
        styles["BrandSubtitle"],
    ))
    elements.append(HRFlowable(
        width="100%", thickness=2, color=BRAND_PRIMARY,
        spaceBefore=2, spaceAfter=12,
    ))
    return elements


def _build_summary_table(report: Report, styles):
    """Build the project summary info box."""
    elements = []
    elements.append(Paragraph("Project Summary", styles["SectionHeader"]))

    potential_overpay = report.total_quoted - report.total_fair_high

    if potential_overpay > 0:
        verdict_text = f"Potential overpayment: {_fmt_currency(potential_overpay)}"
        verdict_label = "⚠ Price Alert"
    else:
        verdict_text = "Quote is within fair market range"
        verdict_label = "✓ Price Verdict"

    data = [
        [
            Paragraph("<b>Project Type</b>", styles["CellText"]),
            Paragraph(_title_case_project(report.project_type), styles["CellText"]),
            Paragraph("<b>Total Quoted</b>", styles["CellText"]),
            Paragraph(f"<b>{_fmt_currency(report.total_quoted)}</b>", styles["CellTextBold"]),
        ],
        [
            Paragraph("<b>Location</b>", styles["CellText"]),
            Paragraph(report.location, styles["CellText"]),
            Paragraph("<b>Fair Range</b>", styles["CellText"]),
            Paragraph(
                f"{_fmt_currency(report.total_fair_low)} – {_fmt_currency(report.total_fair_high)}",
                styles["CellText"],
            ),
        ],
        [
            Paragraph("<b>Report Date</b>", styles["CellText"]),
            Paragraph(_parse_date(report.created_at), styles["CellText"]),
            Paragraph(f"<b>{verdict_label}</b>", styles["CellText"]),
            Paragraph(
                f'<font color="{_savings_color_hex(potential_overpay)}">{verdict_text}</font>',
                styles["CellText"],
            ),
        ],
    ]

    col_widths = [1.2 * inch, 2.0 * inch, 1.2 * inch, 2.3 * inch]
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 1, BRAND_SECONDARY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DBEAFE")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(table)
    return elements


def _build_overall_assessment(report: Report, styles):
    """Build the overall assessment — structured with paragraphs, bullets, numbered items."""
    elements = []
    elements.append(Paragraph("Overall Assessment", styles["SectionHeader"]))

    text = report.overall_assessment or ""

    # Check for markdown structure
    has_markdown = bool(re.search(r'^#{2,3}\s', text, re.MULTILINE))

    if has_markdown:
        # Parse markdown sections
        sections = re.split(r'(?=^#{2,3}\s)', text, flags=re.MULTILINE)
        for section in sections:
            section = section.strip()
            if not section:
                continue

            header_match = re.match(r'^(#{2,3})\s+(.+)', section)
            if header_match:
                title = header_match.group(2).strip()
                body = section[header_match.end():].strip()
                elements.append(Paragraph(title, styles["SubHeader"]))
                if body:
                    _add_body_paragraphs(body, elements, styles)
            else:
                _add_body_paragraphs(section, elements, styles)
    else:
        # Plain text — split intelligently
        _add_body_paragraphs(text, elements, styles)

    return elements


def _add_body_paragraphs(text: str, elements: list, styles):
    """Parse text into structured paragraphs, bullets, and numbered items."""
    # Check for numbered items like 1) or 1.
    numbered_pattern = re.compile(r'(\d+)[\.\)]\s*(.+?)(?=\d+[\.\)]\s|$)', re.DOTALL)
    numbered_matches = numbered_pattern.findall(text)

    if len(numbered_matches) >= 2:
        # Has numbered list — extract intro before first number
        first_num_pos = re.search(r'\d+[\.\)]\s', text)
        if first_num_pos and first_num_pos.start() > 20:
            intro = text[:first_num_pos.start()].strip()
            if intro:
                # Split intro into sentences for readability
                _add_sentence_paragraphs(intro, elements, styles)

        for num, content in numbered_matches:
            content = content.strip().rstrip('.')
            if content:
                elements.append(Paragraph(
                    f"<b>{num}.</b>  {content}",
                    styles["NumberedText"],
                ))
        return

    # Check for bullet points
    if '•' in text or re.search(r'^\s*-\s', text, re.MULTILINE):
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                cleaned = re.sub(r'^[\s•\-*]+', '', line).strip()
                if cleaned:
                    elements.append(Paragraph(f"•  {cleaned}", styles["BulletText"]))
            elif line:
                elements.append(Paragraph(line, styles["BodyText_Custom"]))
        return

    # Plain text — split into digestible paragraphs by sentences
    _add_sentence_paragraphs(text, elements, styles)


def _add_sentence_paragraphs(text: str, elements: list, styles):
    """Split plain text into ~2-3 sentence paragraphs for readability."""
    sentences = re.findall(r'[^.!?]+[.!?]+', text)
    if not sentences:
        if text.strip():
            elements.append(Paragraph(text.strip(), styles["BodyText_Custom"]))
        return

    current = ''
    for sentence in sentences:
        current += sentence
        count = len(re.findall(r'[.!?]+', current))
        if count >= 2 and len(current) > 120:
            para_text = current.strip()
            # Highlight red flag paragraphs
            if re.search(r'goug|red flag|overpriced|significantly|warning', para_text, re.I):
                elements.append(Paragraph(f"🚩 {para_text}", styles["RedFlagText"]))
            else:
                elements.append(Paragraph(para_text, styles["BodyText_Custom"]))
            current = ''

    if current.strip():
        para_text = current.strip()
        if re.search(r'goug|red flag|overpriced|significantly|warning', para_text, re.I):
            elements.append(Paragraph(f"🚩 {para_text}", styles["RedFlagText"]))
        else:
            elements.append(Paragraph(para_text, styles["BodyText_Custom"]))


def _build_line_items_table(report: Report, styles):
    """Build the detailed line items analysis table — full explanations, row highlighting."""
    elements = []
    elements.append(Paragraph("Line Item Analysis", styles["SectionHeader"]))

    if not report.line_items:
        elements.append(Paragraph("No line items to display.", styles["BodyText_Custom"]))
        return elements

    # Table header
    header = [
        Paragraph("<b>Item</b>", styles["CellText"]),
        Paragraph("<b>Quoted</b>", styles["CellText"]),
        Paragraph("<b>Fair Range</b>", styles["CellText"]),
        Paragraph("<b>Assessment</b>", styles["CellText"]),
        Paragraph("<b>Explanation</b>", styles["CellText"]),
    ]

    data = [header]
    row_assessments = []

    for item in report.line_items:
        row_assessments.append(item.assessment)

        # Full explanation — no truncation
        explanation = item.explanation or ""

        row = [
            Paragraph(f"<b>{item.item_name}</b>", styles["CellText"]),
            Paragraph(_fmt_currency(item.quoted_price), styles["CellText"]),
            Paragraph(
                f"{_fmt_currency(item.fair_price_low)} –<br/>{_fmt_currency(item.fair_price_high)}",
                styles["CellText"],
            ),
            Paragraph(_assessment_badge(item.assessment), styles["CellText"]),
            Paragraph(explanation, styles["CellExplanation"]),
        ]
        data.append(row)

    # Wider explanation column for full text
    col_widths = [1.1 * inch, 0.8 * inch, 1.0 * inch, 1.0 * inch, 2.8 * inch]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_commands = [
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),

        # All cells
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
    ]

    # Row backgrounds: highlight issues, zebra-stripe the rest
    for i in range(1, len(data)):
        assessment = row_assessments[i - 1] if i - 1 < len(row_assessments) else ""

        # Critical rows get tinted backgrounds
        if assessment in ASSESSMENT_ROW_BG:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), ASSESSMENT_ROW_BG[assessment]))
        else:
            # Zebra striping
            bg = colors.HexColor("#FFFFFF") if i % 2 == 1 else colors.HexColor("#F9FAFB")
            style_commands.append(("BACKGROUND", (0, i), (-1, i), bg))

    table.setStyle(TableStyle(style_commands))
    elements.append(table)
    return elements


def _build_footer(styles):
    """Build the branded footer."""
    elements = []
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=colors.HexColor("#E5E7EB"),
        spaceBefore=0, spaceAfter=8,
    ))
    elements.append(Paragraph(
        "Generated by UnGouge.ai — Independent Contractor Quote Analysis",
        styles["FooterText"],
    ))
    elements.append(Paragraph(
        "This report is for informational purposes only. Prices are estimates based on public data and AI analysis. "
        "Actual fair pricing may vary based on project specifics, contractor qualifications, and market conditions.",
        styles["SmallGray"],
    ))
    return elements


def generate_pdf(report: Report) -> bytes:
    """
    Generate a branded PDF report from a Report model.

    Returns:
        PDF file contents as bytes.
    """
    buffer = BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        title=f"UnGouge Report – {_title_case_project(report.project_type)}",
        author="UnGouge.ai",
        compress=1,  # Enable PDF compression (reduces file size by ~50%)
    )

    elements = []
    elements.extend(_build_header(report, styles))
    elements.extend(_build_summary_table(report, styles))
    elements.append(Spacer(1, 12))
    elements.extend(_build_overall_assessment(report, styles))
    elements.append(Spacer(1, 8))
    elements.extend(_build_line_items_table(report, styles))
    elements.extend(_build_footer(styles))

    doc.build(elements, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    return buffer.getvalue()
