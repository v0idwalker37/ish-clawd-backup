"""
PDF Report Generator for UnGouge
Generates branded PDF reports from quote analysis data using ReportLab.
"""

import html
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
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

from models.report import Report


# ── Brand Colors ──────────────────────────────────────────────
BRAND_PRIMARY = colors.HexColor("#1E40AF")      # Deep blue
BRAND_SECONDARY = colors.HexColor("#3B82F6")     # Bright blue
BRAND_ACCENT = colors.HexColor("#10B981")        # Green (for "fair")
BRAND_WARNING = colors.HexColor("#F59E0B")        # Amber (for "slightly_high")
BRAND_DANGER = colors.HexColor("#EF4444")         # Red (for "gouging/high")
BRAND_DARK = colors.HexColor("#1F2937")           # Near-black text
BRAND_LIGHT_BG = colors.HexColor("#F0F7FF")       # Light blue bg
BRAND_TABLE_HEADER = colors.HexColor("#1E3A5F")   # Dark header
WHITE = colors.white

ASSESSMENT_COLORS = {
    "fair": BRAND_ACCENT,
    "slightly_high": BRAND_WARNING,
    "high": BRAND_DANGER,
    "gouging": BRAND_DANGER,
    "unknown": colors.HexColor("#6B7280"),
}

ASSESSMENT_LABELS = {
    "fair": "✓ Fair Price",
    "slightly_high": "⚠ Slightly High",
    "high": "⚠ High",
    "gouging": "✗ Gouging",
    "unknown": "? Unknown",
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
        "BodyText_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=BRAND_DARK,
        leading=14,
        spaceAfter=6,
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
        textColor=colors.HexColor("#4B5563"),
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


def _sanitize(text: str, max_len: int = 500) -> str:
    """Sanitize user/AI-controlled text for safe insertion into ReportLab Paragraph().

    Strips any XML/HTML tags (which ReportLab would process), then HTML-escapes
    remaining special characters. Prevents XML injection into PDF generation.

    Security note: ReportLab's Paragraph() processes XML tags in text content.
    User data and LLM output must be sanitized before insertion to prevent
    layout corruption or injection attacks.
    """
    if not text:
        return ""
    # Strip any XML/HTML tags first (handles prompt-injected formatting)
    clean = re.sub(r'<[^>]+>', '', str(text))
    # Escape remaining XML special characters (& < > " ')
    clean = html.escape(clean)
    # Truncate if needed
    if len(clean) > max_len:
        clean = clean[:max_len] + "..."
    return clean


def _fmt_currency(value: float) -> str:
    """Format a number as USD currency."""
    return f"${value:,.2f}"


def _assessment_badge(assessment: str) -> str:
    """Return a styled assessment label for use in Paragraphs."""
    label = ASSESSMENT_LABELS.get(assessment, assessment)
    color_hex = ASSESSMENT_COLORS.get(assessment, colors.gray)
    if hasattr(color_hex, "hexval"):
        hex_str = color_hex.hexval()
    else:
        hex_str = str(color_hex)
    return f'<font color="{hex_str}"><b>{label}</b></font>'


def _build_header(report: Report, styles):
    """Build the branded header section."""
    elements = []

    # Logo text (since we don't have an image file, use styled text)
    elements.append(Paragraph("UnGouge<font color='#3B82F6'>.ai</font>", styles["BrandTitle"]))
    elements.append(Paragraph(
        "Independent Contractor Quote Analysis",
        styles["BrandSubtitle"],
    ))

    # Divider
    elements.append(HRFlowable(
        width="100%", thickness=2, color=BRAND_PRIMARY,
        spaceBefore=2, spaceAfter=12,
    ))

    return elements


def _build_summary_table(report: Report, styles):
    """Build the project summary info box."""
    elements = []
    elements.append(Paragraph("Project Summary", styles["SectionHeader"]))

    # Savings calculation
    potential_overpay = report.total_quoted - report.total_fair_high
    savings_text = (
        f"Potential overpayment: {_fmt_currency(potential_overpay)}"
        if potential_overpay > 0
        else "Quote is within fair market range"
    )

    data = [
        [
            Paragraph("<b>Project Type</b>", styles["CellText"]),
            Paragraph(_sanitize(report.project_type), styles["CellText"]),
            Paragraph("<b>Total Quoted</b>", styles["CellText"]),
            Paragraph(f"<b>{_fmt_currency(report.total_quoted)}</b>", styles["CellTextBold"]),
        ],
        [
            Paragraph("<b>Location</b>", styles["CellText"]),
            Paragraph(_sanitize(report.location), styles["CellText"]),
            Paragraph("<b>Fair Range</b>", styles["CellText"]),
            Paragraph(
                f"{_fmt_currency(report.total_fair_low)} – {_fmt_currency(report.total_fair_high)}",
                styles["CellText"],
            ),
        ],
        [
            Paragraph("<b>Report Date</b>", styles["CellText"]),
            Paragraph(
                _parse_date(report.created_at),
                styles["CellText"],
            ),
            Paragraph("<b>Savings Alert</b>", styles["CellText"]),
            Paragraph(
                f'<font color="{_savings_color_hex(potential_overpay)}">{savings_text}</font>',
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


def _savings_color_hex(overpay: float) -> str:
    if overpay > 0:
        return "#EF4444"
    return "#10B981"


def _parse_date(date_str: str) -> str:
    """Parse ISO date string to human-readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except (ValueError, AttributeError):
        return date_str


def _build_overall_assessment(report: Report, styles):
    """Build the overall assessment paragraph."""
    elements = []
    elements.append(Paragraph("Overall Assessment", styles["SectionHeader"]))
    elements.append(Paragraph(_sanitize(report.overall_assessment, max_len=1000), styles["BodyText_Custom"]))
    return elements


def _build_line_items_table(report: Report, styles):
    """Build the detailed line items analysis table."""
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
    row_colors = []  # Track assessment per row for conditional coloring

    for item in report.line_items:
        assessment_color = ASSESSMENT_COLORS.get(item.assessment, colors.gray)
        row_colors.append(assessment_color)

        row = [
            Paragraph(f"<b>{_sanitize(item.item_name, max_len=100)}</b>", styles["CellText"]),
            Paragraph(_fmt_currency(item.quoted_price), styles["CellText"]),
            Paragraph(
                f"{_fmt_currency(item.fair_price_low)} –\n{_fmt_currency(item.fair_price_high)}",
                styles["CellText"],
            ),
            Paragraph(_assessment_badge(item.assessment), styles["CellText"]),
            Paragraph(_sanitize(item.explanation, max_len=200), styles["CellExplanation"]),
        ]
        data.append(row)

    col_widths = [1.2 * inch, 0.9 * inch, 1.2 * inch, 1.0 * inch, 2.4 * inch]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    # Build table style
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

    # Alternate row backgrounds for readability
    for i in range(1, len(data)):
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

    Args:
        report: The Report model containing all analysis data.

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
        title=f"UnGouge Report – {_sanitize(report.project_type, max_len=100)}",
        author="UnGouge.ai",
    )

    # Assemble all sections
    elements = []
    elements.extend(_build_header(report, styles))
    elements.extend(_build_summary_table(report, styles))
    elements.append(Spacer(1, 12))
    elements.extend(_build_overall_assessment(report, styles))
    elements.append(Spacer(1, 8))
    elements.extend(_build_line_items_table(report, styles))
    elements.extend(_build_footer(styles))

    doc.build(elements)
    return buffer.getvalue()
