"""
PDF Report Generator for GougeAlert
Generates branded PDF reports matching the website's visual identity.

V3 — Full website-matched branding:
  - Sky-blue primary palette matching tailwind config
  - Embedded logo in header
  - Dark footer matching website footer
  - Privacy/trust badges
  - Proper card-style pricing layout
  - Structured overall assessment (paragraphs, bullets, numbered recs)
  - Full explanation text (no truncation)
  - Row highlighting for gouging/issues
"""

import os
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
    Image,
    KeepTogether,
)

from models.report import Report


# ── Brand Colors (matches tailwind.config.js primary palette) ─────
PRIMARY_50  = colors.HexColor("#f0f9ff")
PRIMARY_100 = colors.HexColor("#e0f2fe")
PRIMARY_200 = colors.HexColor("#bae6fd")
PRIMARY_300 = colors.HexColor("#7dd3fc")
PRIMARY_400 = colors.HexColor("#38bdf8")
PRIMARY_500 = colors.HexColor("#0ea5e9")
PRIMARY_600 = colors.HexColor("#0284c7")   # Main brand color
PRIMARY_700 = colors.HexColor("#0369a1")
PRIMARY_800 = colors.HexColor("#075985")
PRIMARY_900 = colors.HexColor("#0c4a6e")

# Semantic
SUCCESS     = colors.HexColor("#10b981")   # Emerald-500
SUCCESS_700 = colors.HexColor("#047857")
WARNING     = colors.HexColor("#f59e0b")   # Amber-500
DANGER      = colors.HexColor("#ef4444")   # Red-500
DANGER_700  = colors.HexColor("#b91c1c")

# Neutrals
GRAY_50  = colors.HexColor("#F9FAFB")
GRAY_100 = colors.HexColor("#F3F4F6")
GRAY_200 = colors.HexColor("#E5E7EB")
GRAY_300 = colors.HexColor("#D1D5DB")
GRAY_400 = colors.HexColor("#9CA3AF")
GRAY_500 = colors.HexColor("#6B7280")
GRAY_600 = colors.HexColor("#4B5563")
GRAY_700 = colors.HexColor("#374151")
GRAY_800 = colors.HexColor("#1F2937")
GRAY_900 = colors.HexColor("#111827")
WHITE    = colors.white

ASSESSMENT_COLORS = {
    "fair":              SUCCESS_700,
    "slightly_high":     colors.HexColor("#D97706"),
    "high":              colors.HexColor("#EA580C"),
    "gouging":           DANGER_700,
    "suspiciously_low":  PRIMARY_700,
    "unknown":           GRAY_500,
}

ASSESSMENT_LABELS = {
    "fair":              "Fair Price",
    "slightly_high":     "Slightly High",
    "high":              "High",
    "gouging":           "Possible Gouge",
    "suspiciously_low":  "Suspiciously Low",
    "unknown":           "Unknown",
}

ASSESSMENT_ROW_BG = {
    "gouging":           colors.HexColor("#FEE2E2"),
    "high":              colors.HexColor("#FFEDD5"),
    "suspiciously_low":  colors.HexColor("#DBEAFE"),
}

# Logo path — relative to backend root
LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "logo.png")


def _build_styles():
    """Build custom paragraph styles for the PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=PRIMARY_800,
        spaceBefore=20,
        spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        "SubHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=GRAY_800,
        spaceBefore=10,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "BodyText_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=GRAY_800,
        leading=14,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=GRAY_800,
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
        textColor=GRAY_800,
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
    ))
    styles.add(ParagraphStyle(
        "SmallGray",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        textColor=GRAY_400,
        alignment=TA_CENTER,
        leading=10,
    ))
    styles.add(ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=GRAY_800,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        "CellTextBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=GRAY_800,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        "CellExplanation",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=GRAY_600,
        leading=11,
    ))
    return styles


# ── Helpers ───────────────────────────────────────────────────

def _fmt_currency(value: float) -> str:
    if value == 0:
        return "$0"
    if value == int(value):
        return f"${int(value):,}"
    return f"${value:,.2f}"


def _title_case_project(raw: str) -> str:
    return raw.replace("_", " ").title()


def _assessment_badge(assessment: str) -> str:
    label = ASSESSMENT_LABELS.get(assessment, assessment)
    clr = ASSESSMENT_COLORS.get(assessment, GRAY_500)
    hex_str = clr.hexval() if hasattr(clr, "hexval") else str(clr)
    return f'<font color="{hex_str}"><b>{label}</b></font>'


def _parse_date(date_str: str) -> str:
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except (ValueError, AttributeError):
        return date_str


# ── Page-level callbacks ──────────────────────────────────────

def _add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY_400)
    canvas.drawCentredString(letter[0] / 2, 0.35 * inch, f"Page {page_num}")
    canvas.restoreState()


# ── Section Builders ──────────────────────────────────────────

def _build_header(report: Report, styles):
    """Header matching website: white bg, logo left, tagline right."""
    elements = []

    # Top accent line (matching primary-600)
    accent_data = [[""]]
    accent = Table(accent_data, colWidths=[6.8 * inch], rowHeights=[4])
    accent.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY_600),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(accent)
    elements.append(Spacer(1, 12))

    # Logo + tagline row
    logo_cell = []
    if os.path.exists(LOGO_PATH):
        logo_cell.append(Image(LOGO_PATH, width=1.5 * inch, height=0.47 * inch))
    else:
        logo_cell.append(Paragraph(
            "GougeAlert<font color='#0284c7'>.com</font>",
            ParagraphStyle("FallbackLogo", fontName="Helvetica-Bold", fontSize=22,
                           textColor=GRAY_900),
        ))

    tagline_style = ParagraphStyle(
        "Tagline", fontName="Helvetica", fontSize=10,
        textColor=GRAY_500, alignment=TA_RIGHT,
    )

    header_data = [[
        logo_cell,
        Paragraph("Independent Contractor<br/>Quote Analysis", tagline_style),
    ]]
    header_table = Table(header_data, colWidths=[3.4 * inch, 3.4 * inch])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    # Thin separator
    elements.append(HRFlowable(
        width="100%", thickness=1, color=GRAY_200,
        spaceBefore=4, spaceAfter=14,
    ))

    return elements


def _build_estimation_disclaimer(report: Report, styles):
    """Info banner for total-only quotes — blue tint matching primary palette."""
    if not getattr(report, 'is_estimated', False):
        return []

    elements = []

    info_style = ParagraphStyle(
        "InfoText", parent=styles["BodyText_Custom"],
        fontName="Helvetica", fontSize=9, textColor=PRIMARY_800, leading=13,
    )
    info_bold = ParagraphStyle(
        "InfoBold", parent=info_style,
        fontName="Helvetica-Bold", fontSize=10,
    )

    inner = []
    inner.append(Paragraph("Total-Only Quote Analysis", info_bold))
    inner.append(Spacer(1, 4))
    inner.append(Paragraph(
        "Your contractor provided only a total price with no per-item breakdown. "
        "This report analyzes the <b>total price</b> against current market data for "
        f"{_title_case_project(report.project_type)} projects in your area, and provides "
        "typical cost ranges for each work item as educational guidance.",
        info_style,
    ))
    inner.append(Spacer(1, 4))
    inner.append(Paragraph(
        "<b>Want per-item analysis?</b> Ask your contractor for an itemized quote "
        "and re-submit it for detailed fair-price ratings on every line item.",
        info_style,
    ))

    info_table = Table([[inner]], colWidths=[6.6 * inch])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY_50),
        ("BOX", (0, 0), (-1, -1), 1.5, PRIMARY_400),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 16))
    return elements


def _build_summary_cards(report: Report, styles):
    """Pricing summary — project info line + 3 prominent cards."""
    elements = []

    # Project info line
    project_style = ParagraphStyle("ProjectLine", parent=styles["BodyText_Custom"],
                                    fontSize=11, textColor=GRAY_700)
    elements.append(Paragraph(
        f"<b>{_title_case_project(report.project_type)}</b>  ·  "
        f"{report.location}  ·  {_parse_date(report.created_at)}",
        project_style,
    ))
    elements.append(Spacer(1, 14))

    potential_overpay = report.total_quoted - report.total_fair_high

    # Styles for card contents
    label_s = ParagraphStyle("CardLabel", fontName="Helvetica-Bold", fontSize=8,
                              textColor=GRAY_500, alignment=TA_CENTER, leading=10,
                              spaceBefore=0, spaceAfter=4)
    big_price = ParagraphStyle("BigPrice", fontName="Helvetica-Bold", fontSize=20,
                                textColor=GRAY_900, alignment=TA_CENTER, leading=24)
    fair_price = ParagraphStyle("FairPrice", fontName="Helvetica-Bold", fontSize=14,
                                 textColor=SUCCESS_700, alignment=TA_CENTER, leading=18)

    is_over = potential_overpay > 0
    verdict_color = DANGER_700 if is_over else SUCCESS_700
    verdict_style = ParagraphStyle("VerdictPrice", fontName="Helvetica-Bold", fontSize=14,
                                    textColor=verdict_color, alignment=TA_CENTER, leading=18)

    # Build card cells — each cell is a list of flowables
    card1 = [
        Paragraph("TOTAL QUOTED", label_s),
        Paragraph(_fmt_currency(report.total_quoted), big_price),
    ]
    card2 = [
        Paragraph("FAIR MARKET RANGE", label_s),
        Paragraph(f"{_fmt_currency(report.total_fair_low)} – {_fmt_currency(report.total_fair_high)}", fair_price),
    ]
    card3 = [
        Paragraph("POTENTIAL OVERPAY" if is_over else "PRICE VERDICT", label_s),
        Paragraph(
            _fmt_currency(potential_overpay) if is_over else "Within fair range",
            verdict_style,
        ),
    ]

    card_table = Table([[card1, card2, card3]],
                       colWidths=[2.27 * inch, 2.27 * inch, 2.27 * inch])

    # Card backgrounds & borders
    card3_bg = colors.HexColor("#FEF2F2") if is_over else colors.HexColor("#ECFDF5")
    card3_border = colors.HexColor("#FCA5A5") if is_over else colors.HexColor("#6EE7B7")

    card_table.setStyle(TableStyle([
        # Card 1 — neutral
        ("BACKGROUND", (0, 0), (0, 0), GRAY_50),
        ("BOX", (0, 0), (0, 0), 1, GRAY_200),
        # Card 2 — green tint
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#ECFDF5")),
        ("BOX", (1, 0), (1, 0), 1, colors.HexColor("#6EE7B7")),
        # Card 3 — conditional
        ("BACKGROUND", (2, 0), (2, 0), card3_bg),
        ("BOX", (2, 0), (2, 0), 1, card3_border),
        # All cards
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(card_table)

    return elements


def _build_overall_assessment(report: Report, styles):
    """Overall assessment — structured text with paragraphs, bullets, numbered items."""
    elements = []

    # Section header with accent bar
    header_data = [[
        Paragraph("Overall Assessment", ParagraphStyle(
            "AssessHeader", fontName="Helvetica-Bold", fontSize=13,
            textColor=PRIMARY_800, leading=16,
        )),
    ]]
    header_table = Table(header_data, colWidths=[6.6 * inch])
    header_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 2, PRIMARY_500),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(Spacer(1, 16))
    elements.append(header_table)
    elements.append(Spacer(1, 8))

    text = report.overall_assessment or ""

    has_markdown = bool(re.search(r'^#{2,3}\s', text, re.MULTILINE))
    if has_markdown:
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
        _add_body_paragraphs(text, elements, styles)

    return elements


def _add_body_paragraphs(text: str, elements: list, styles):
    """Parse text into paragraphs, bullets, numbered items."""
    numbered_pattern = re.compile(r'(\d+)[\.\)]\s*(.+?)(?=\d+[\.\)]\s|$)', re.DOTALL)
    numbered_matches = numbered_pattern.findall(text)

    if len(numbered_matches) >= 2:
        first_num_pos = re.search(r'\d+[\.\)]\s', text)
        if first_num_pos and first_num_pos.start() > 20:
            intro = text[:first_num_pos.start()].strip()
            if intro:
                _add_sentence_paragraphs(intro, elements, styles)
        for num, content in numbered_matches:
            content = content.strip().rstrip('.')
            if content:
                elements.append(Paragraph(
                    f"<b>{num}.</b>  {content}",
                    styles["NumberedText"],
                ))
        return

    if '\u2022' in text or re.search(r'^\s*-\s', text, re.MULTILINE):
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('\u2022') or line.startswith('-'):
                cleaned = re.sub(r'^[\s\u2022\-*]+', '', line).strip()
                if cleaned:
                    elements.append(Paragraph(f"\u2022  {cleaned}", styles["BulletText"]))
            elif line:
                elements.append(Paragraph(line, styles["BodyText_Custom"]))
        return

    _add_sentence_paragraphs(text, elements, styles)


def _add_sentence_paragraphs(text: str, elements: list, styles):
    """Split text into ~2-3 sentence paragraphs for readability."""
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
            if re.search(r'goug|red flag|overpriced|significantly|warning', para_text, re.I):
                elements.append(Paragraph(para_text, styles["RedFlagText"]))
            else:
                elements.append(Paragraph(para_text, styles["BodyText_Custom"]))
            current = ''

    if current.strip():
        para_text = current.strip()
        if re.search(r'goug|red flag|overpriced|significantly|warning', para_text, re.I):
            elements.append(Paragraph(para_text, styles["RedFlagText"]))
        else:
            elements.append(Paragraph(para_text, styles["BodyText_Custom"]))


def _build_line_items_table(report: Report, styles):
    """Line items table — branded header, row highlighting, full explanations."""
    elements = []

    # Section header with accent bar
    header_data = [[
        Paragraph("Line Item Analysis", ParagraphStyle(
            "LineItemHeader", fontName="Helvetica-Bold", fontSize=13,
            textColor=PRIMARY_800, leading=16,
        )),
    ]]
    header_table = Table(header_data, colWidths=[6.6 * inch])
    header_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 2, PRIMARY_500),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(Spacer(1, 16))
    elements.append(header_table)
    elements.append(Spacer(1, 8))

    if not report.line_items:
        elements.append(Paragraph("No line items to display.", styles["BodyText_Custom"]))
        return elements

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
        row = [
            Paragraph(f"<b>{item.item_name}</b>", styles["CellText"]),
            Paragraph(_fmt_currency(item.quoted_price), styles["CellText"]),
            Paragraph(
                f"{_fmt_currency(item.fair_price_low)} –<br/>{_fmt_currency(item.fair_price_high)}",
                styles["CellText"],
            ),
            Paragraph(_assessment_badge(item.assessment), styles["CellText"]),
            Paragraph(item.explanation or "", styles["CellExplanation"]),
        ]
        data.append(row)

    col_widths = [1.1 * inch, 0.8 * inch, 1.0 * inch, 1.0 * inch, 2.8 * inch]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_800),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRAY_200),
        ("BOX", (0, 0), (-1, -1), 1, GRAY_300),
    ]

    for i in range(1, len(data)):
        assessment = row_assessments[i - 1] if i - 1 < len(row_assessments) else ""
        if assessment in ASSESSMENT_ROW_BG:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), ASSESSMENT_ROW_BG[assessment]))
        else:
            bg = WHITE if i % 2 == 1 else GRAY_50
            style_commands.append(("BACKGROUND", (0, i), (-1, i), bg))

    table.setStyle(TableStyle(style_commands))
    elements.append(table)
    return elements


def _build_typical_costs_section(report: Report, styles):
    """Educational 'Typical Costs' section for total-only quotes."""
    elements = []

    typical_costs = getattr(report, 'typical_costs', None)
    if not typical_costs:
        return elements

    # Section header with accent bar
    header_data = [[
        Paragraph("Typical Costs in Your Area", ParagraphStyle(
            "TypicalHeader", fontName="Helvetica-Bold", fontSize=13,
            textColor=PRIMARY_800, leading=16,
        )),
    ]]
    header_table = Table(header_data, colWidths=[6.6 * inch])
    header_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 2, PRIMARY_500),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(Spacer(1, 16))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(
        f"The following are typical cost ranges for {_title_case_project(report.project_type)} "
        f"work items in <b>{report.location}</b>, based on current market data. These are "
        "general market ranges — not what your contractor is charging for each item.",
        styles["BodyText_Custom"],
    ))
    elements.append(Spacer(1, 8))

    header = [
        Paragraph("<b>Work Item</b>", styles["CellText"]),
        Paragraph("<b>Typical Range</b>", styles["CellText"]),
        Paragraph("<b>What This Includes</b>", styles["CellText"]),
    ]

    data = [header]
    for item in typical_costs:
        row = [
            Paragraph(f"<b>{item.item_name}</b>", styles["CellText"]),
            Paragraph(
                f"{_fmt_currency(item.typical_low)} – {_fmt_currency(item.typical_high)}",
                styles["CellText"],
            ),
            Paragraph(item.description or "", styles["CellExplanation"]),
        ]
        data.append(row)

    col_widths = [1.6 * inch, 1.4 * inch, 3.7 * inch]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_800),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRAY_200),
        ("BOX", (0, 0), (-1, -1), 1, GRAY_300),
    ]
    for i in range(1, len(data)):
        bg = WHITE if i % 2 == 1 else GRAY_50
        style_commands.append(("BACKGROUND", (0, i), (-1, i), bg))

    table.setStyle(TableStyle(style_commands))
    elements.append(table)

    # CTA
    elements.append(Spacer(1, 14))
    cta_inner = []
    cta_inner.append(Paragraph(
        "<b>Want per-item analysis?</b> Ask your contractor for an itemized breakdown "
        "and submit it to GougeAlert for detailed fair-price ratings on every line item.",
        ParagraphStyle("CTAText", fontName="Helvetica", fontSize=9.5,
                        textColor=PRIMARY_800, leading=13),
    ))
    cta_table = Table([[cta_inner]], colWidths=[6.6 * inch])
    cta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY_50),
        ("BOX", (0, 0), (-1, -1), 1, PRIMARY_200),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(cta_table)

    return elements


def _build_trust_badge(styles):
    """Privacy/trust section matching website footer badges."""
    elements = []
    elements.append(Spacer(1, 16))

    badge_style = ParagraphStyle("BadgeText", fontName="Helvetica", fontSize=8,
                                  textColor=GRAY_500, leading=11, alignment=TA_CENTER)

    badge_data = [[
        Paragraph(
            "We NEVER sell your data  ·  No lead generation  ·  "
            "No contractor referrals  ·  Your privacy guaranteed",
            badge_style,
        ),
    ]]
    badge_table = Table(badge_data, colWidths=[6.8 * inch])
    badge_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRAY_50),
        ("BOX", (0, 0), (-1, -1), 1, GRAY_200),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(badge_table)
    return elements


def _build_footer(styles):
    """Dark footer matching website — brand + disclaimer."""
    elements = []
    elements.append(Spacer(1, 20))

    # Dark footer banner
    footer_inner = []
    footer_inner.append(Paragraph(
        "GougeAlert<font color='#38bdf8'>.com</font>",
        ParagraphStyle("FooterBrand", fontName="Helvetica-Bold", fontSize=12,
                        textColor=WHITE, alignment=TA_CENTER),
    ))
    footer_inner.append(Spacer(1, 3))
    footer_inner.append(Paragraph(
        "Fair contractor quote analysis powered by real market data.",
        ParagraphStyle("FooterTag", fontName="Helvetica", fontSize=8,
                        textColor=GRAY_400, alignment=TA_CENTER),
    ))
    footer_inner.append(Spacer(1, 6))
    footer_inner.append(Paragraph(
        "gougealert.com  ·  support@gougealert.com",
        ParagraphStyle("FooterLinks", fontName="Helvetica", fontSize=8,
                        textColor=PRIMARY_400, alignment=TA_CENTER),
    ))

    footer_table = Table([[footer_inner]], colWidths=[6.8 * inch])
    footer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRAY_900),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    elements.append(footer_table)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "This report is for informational purposes only. Prices are estimates based on "
        "public data and AI analysis. Actual fair pricing may vary based on project specifics, "
        "contractor qualifications, and market conditions.",
        styles["SmallGray"],
    ))

    return elements


# ── Main Generator ────────────────────────────────────────────

def generate_pdf(report: Report) -> bytes:
    """Generate a branded PDF report from a Report model."""
    buffer = BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        title=f"GougeAlert Report – {_title_case_project(report.project_type)}",
        author="GougeAlert",
        compress=1,
    )

    elements = []
    elements.extend(_build_header(report, styles))
    elements.extend(_build_estimation_disclaimer(report, styles))
    elements.extend(_build_summary_cards(report, styles))
    elements.extend(_build_overall_assessment(report, styles))

    # Total-only quotes: educational typical costs instead of per-item analysis
    if getattr(report, 'is_estimated', False) and getattr(report, 'typical_costs', None):
        elements.extend(_build_typical_costs_section(report, styles))
    else:
        elements.extend(_build_line_items_table(report, styles))

    elements.extend(_build_trust_badge(styles))
    elements.extend(_build_footer(styles))

    doc.build(elements, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    return buffer.getvalue()
