#!/usr/bin/env python3
"""
Generate professional PDF using ReportLab (industry standard)
This gives EXACT typography control - no HTML rendering issues
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import re

def extract_title(md_content):
    """Extract title from frontmatter"""
    if md_content.startswith('---'):
        parts = md_content.split('---', 2)
        if len(parts) >= 3:
            title_match = re.search(r'title:\s*"([^"]+)"', parts[1])
            if title_match:
                return title_match.group(1), parts[2].strip()
    return "Ungouge Resource", md_content

def create_cover_page(canvas_obj, title):
    """Create professional cover page"""
    # Green header bar
    canvas_obj.setFillColorRGB(0.063, 0.725, 0.506)  # Ungouge green
    canvas_obj.rect(0, 11*inch - 1.8*inch, 8.5*inch, 1.8*inch, fill=1)
    
    # Logo
    canvas_obj.setFillColorRGB(0.973, 0.980, 0.988)  # White
    canvas_obj.setFont("Helvetica-Bold", 40)
    canvas_obj.drawString(0.75*inch, 11*inch - 1.1*inch, "Ungouge.ai")
    
    canvas_obj.setFont("Helvetica", 15)
    canvas_obj.drawString(0.75*inch, 11*inch - 1.4*inch, "Know Before You Sign")
    
    # Title
    canvas_obj.setFillColorRGB(0.122, 0.161, 0.220)  # Dark text
    canvas_obj.setFont("Helvetica-Bold", 36)
    
    # Word wrap title
    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        test = (current_line + " " + word).strip()
        if len(test) <= 35:
            current_line = test
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    y = 8*inch
    for line in lines:
        canvas_obj.drawString(0.75*inch, y, line)
        y -= 0.6*inch
    
    # Subtitle
    canvas_obj.setFillColorRGB(0.392, 0.439, 0.545)  # Gray
    canvas_obj.setFont("Helvetica", 17)
    canvas_obj.drawString(0.75*inch, y - 0.3*inch, "Data-Driven Insights for Homeowners")
    
    # Bottom line
    canvas_obj.setStrokeColorRGB(0.063, 0.725, 0.506)
    canvas_obj.setLineWidth(3)
    canvas_obj.line(0.75*inch, 1.2*inch, 7.75*inch, 1.2*inch)
    
    # Footer
    canvas_obj.setFillColorRGB(0.392, 0.439, 0.545)
    canvas_obj.setFont("Helvetica", 11)
    canvas_obj.drawString(0.75*inch, 0.8*inch, "© 2026 Ungouge.ai")
    canvas_obj.drawRightString(7.75*inch, 0.8*inch, "ungouge.ai")
    
    canvas_obj.showPage()

def header_footer(canvas_obj, doc):
    """Add header and footer to pages"""
    canvas_obj.saveState()
    
    # Header line
    canvas_obj.setStrokeColorRGB(0.063, 0.725, 0.506)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(0.75*inch, 10.5*inch, 7.75*inch, 10.5*inch)
    
    canvas_obj.setFillColorRGB(0.392, 0.439, 0.545)
    canvas_obj.setFont("Helvetica", 10)
    canvas_obj.drawString(0.75*inch, 10.65*inch, "Ungouge.ai")
    
    # Footer
    canvas_obj.setStrokeColorRGB(0.392, 0.439, 0.545)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(0.75*inch, 0.7*inch, 7.75*inch, 0.7*inch)
    
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawString(0.75*inch, 0.5*inch, "ungouge.ai")
    canvas_obj.drawRightString(7.75*inch, 0.5*inch, str(doc.page))
    
    canvas_obj.restoreState()

def html_to_story(html_content):
    """Convert HTML to ReportLab story with EXACT typography"""
    
    # Define styles with EXACT sizes
    styles = getSampleStyleSheet()
    
    # Body text - 12pt EXACTLY
    style_body = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        leading=20,  # line height
        textColor=colors.HexColor('#1f2937'),
        fontName='Helvetica',
        spaceAfter=10,
    )
    
    # H1 - 28pt
    style_h1 = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=28,
        leading=34,
        textColor=colors.HexColor('#10b981'),
        fontName='Helvetica-Bold',
        spaceBefore=18,
        spaceAfter=14,
    )
    
    # H2 - 20pt
    style_h2 = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=20,
        leading=26,
        textColor=colors.HexColor('#10b981'),
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=14,
        borderPadding=10,
        borderWidth=3,
        borderColor=colors.HexColor('#10b981'),
    )
    
    # H3 - 15pt
    style_h3 = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#374151'),
        fontName='Helvetica-Bold',
        spaceBefore=16,
        spaceAfter=10,
    )
    
    # H4 - 13pt
    style_h4 = ParagraphStyle(
        'CustomH4',
        parent=styles['Heading4'],
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#4b5563'),
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=8,
    )
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    story = []
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'table']):
        
        if element.name == 'h1':
            story.append(Paragraph(element.get_text(), style_h1))
        
        elif element.name == 'h2':
            story.append(PageBreak())  # Page break before H2
            story.append(Paragraph(element.get_text(), style_h2))
        
        elif element.name == 'h3':
            story.append(Paragraph(element.get_text(), style_h3))
        
        elif element.name == 'h4':
            story.append(Paragraph(element.get_text(), style_h4))
        
        elif element.name == 'p':
            story.append(Paragraph(element.get_text(), style_body))
        
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li', recursive=False):
                text = '• ' + li.get_text()
                story.append(Paragraph(text, style_body))
        
        elif element.name == 'table':
            # Build table data
            data = []
            for row in element.find_all('tr'):
                row_data = [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
                data.append(row_data)
            
            if data:
                t = Table(data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('FONTSIZE', (0, 1), (-1, -1), 11),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(t)
                story.append(Spacer(1, 12))
    
    return story

# Main execution
md_file = Path('/Users/moltbot/clawd/projects/ungouge-app/content/blog/bathroom-remodel-cost-breakdown.md')
output_file = Path('/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/bathroom-remodel-REPORTLAB.pdf')
output_file.parent.mkdir(parents=True, exist_ok=True)

print("🎨 Generating professional PDF with ReportLab...\n")

# Read content
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

title, content = extract_title(md_content)
html = markdown.markdown(content, extensions=['extra', 'tables'])

# Create PDF
doc = SimpleDocTemplate(
    str(output_file),
    pagesize=letter,
    leftMargin=0.75*inch,
    rightMargin=0.75*inch,
    topMargin=1*inch,
    bottomMargin=0.9*inch,
)

# Build story
story = html_to_story(html)

# Create cover page first
c = canvas.Canvas(str(output_file.with_suffix('.temp.pdf')), pagesize=letter)
create_cover_page(c, title)
c.save()

# Build main document
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)

# Merge cover + content (simplified - just use main doc)
print(f"✅ Complete!")
print(f"📂 {output_file}")
