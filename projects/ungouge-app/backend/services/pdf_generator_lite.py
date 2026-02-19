"""
Lightweight PDF Generator for Telegram Delivery
Ultra-compressed version with minimal styling, optimized for < 5MB file size.
"""

import re
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from models.report import Report


def generate_lite_pdf(report: Report) -> bytes:
    """
    Generate ultra-lightweight PDF for Telegram delivery (< 5MB target).
    
    Stripped down to essentials:
    - No fancy styling
    - Minimal fonts
    - Compact tables
    - Truncated text
    - Maximum compression
    """
    buffer = BytesIO()
    
    # Minimal margins, maximum compression
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
        leftMargin=0.4 * inch,
        rightMargin=0.4 * inch,
        title=f"UnGouge Report",
        compress=1,
    )
    
    # Minimal styles
    styles = getSampleStyleSheet()
    
    # Ultra-compact styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.black,
        spaceAfter=8,
        fontName='Helvetica-Bold',
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=4,
        fontName='Helvetica-Bold',
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        textColor=colors.black,
    )
    
    elements = []
    
    # Header (minimal)
    elements.append(Paragraph("UnGouge.ai Quote Analysis", title_style))
    elements.append(Paragraph(f"{report.project_type} • {report.location}", body_style))
    elements.append(Spacer(1, 8))
    
    # Summary table (ultra-compact)
    summary_data = [
        ['Quoted', 'Fair Range', 'Potential Savings'],
        [
            f'${report.total_quoted:,.0f}',
            f'${report.total_fair_low:,.0f} - ${report.total_fair_high:,.0f}',
            f'${max(0, report.total_quoted - report.total_fair_high):,.0f}'
        ],
    ]
    
    summary_table = Table(summary_data, colWidths=[1.8*inch, 2.2*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 10))
    
    # Overall assessment (truncated)
    elements.append(Paragraph("Assessment", header_style))
    assessment = report.overall_assessment or ""
    
    # Truncate to first 300 chars
    if len(assessment) > 300:
        sentences = re.findall(r'[^.!?]+[.!?]+', assessment)
        truncated = ""
        for sent in sentences:
            if len(truncated) + len(sent) < 300:
                truncated += sent
            else:
                break
        assessment = truncated.strip() if truncated else assessment[:300] + "..."
    
    elements.append(Paragraph(assessment, body_style))
    elements.append(Spacer(1, 10))
    
    # Line items (ultra-compact, max 20 items)
    elements.append(Paragraph("Line Items", header_style))
    
    # Show only critical items + top 5 overpriced
    line_items = report.line_items[:20]  # Hard limit
    
    # Sort by overpayment (show worst offenders first)
    sorted_items = sorted(
        line_items,
        key=lambda x: (x.quoted_price - x.fair_price_high),
        reverse=True
    )[:15]  # Max 15 items
    
    if sorted_items:
        table_data = [['Item', 'Quoted', 'Fair', 'Status']]
        
        for item in sorted_items:
            status = '✓' if item.assessment == 'fair' else '⚠'
            if item.assessment == 'gouging':
                status = '✗'
            
            # Truncate item name
            name = item.item_name[:30] + '...' if len(item.item_name) > 30 else item.item_name
            
            table_data.append([
                name,
                f'${item.quoted_price:,.0f}',
                f'${item.fair_price_high:,.0f}',
                status
            ])
        
        items_table = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 0.6*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(items_table)
    
    if len(report.line_items) > 15:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            f"+ {len(report.line_items) - 15} more items. View full report at ungouge.ai",
            body_style
        ))
    
    # Footer
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Full detailed report: ungouge.ai", body_style))
    
    doc.build(elements)
    return buffer.getvalue()
