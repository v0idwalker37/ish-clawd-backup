#!/usr/bin/env python3
"""
Professional PDF with:
- Logo on cover page
- Smart page breaks (no awkward cuts)
- Consistent 12pt typography
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
                                 Table, TableStyle, KeepTogether, Image)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Circle, Polygon
from reportlab.graphics import renderPDF
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import re

def create_shield_logo():
    """Create a simple shield logo graphic"""
    d = Drawing(60, 70)
    # Shield shape using polygon
    shield = Polygon([
        30, 65,   # top center
        10, 60,   # top left
        5, 40,    # mid left
        15, 10,   # bottom left
        30, 5,    # bottom center
        45, 10,   # bottom right
        55, 40,   # mid right
        50, 60,   # top right
    ])
    shield.fillColor = colors.HexColor('#10b981')
    shield.strokeColor = colors.white
    shield.strokeWidth = 2
    d.add(shield)
    return d

def create_cover_page(canvas_obj, title):
    """Professional cover with logo"""
    # Green header bar
    canvas_obj.setFillColorRGB(0.063, 0.725, 0.506)
    canvas_obj.rect(0, 11*inch - 2*inch, 8.5*inch, 2*inch, fill=1)
    
    # Draw shield logo
    logo = create_shield_logo()
    renderPDF.draw(logo, canvas_obj, 0.75*inch, 11*inch - 1.5*inch)
    
    # Logo text
    canvas_obj.setFillColorRGB(0.973, 0.980, 0.988)
    canvas_obj.setFont("Helvetica-Bold", 42)
    canvas_obj.drawString(1.6*inch, 11*inch - 1.05*inch, "Ungouge.ai")
    
    canvas_obj.setFont("Helvetica", 16)
    canvas_obj.drawString(1.6*inch, 11*inch - 1.35*inch, "Know Before You Sign")
    
    # Title area
    canvas_obj.setFillColorRGB(0.122, 0.161, 0.220)
    canvas_obj.setFont("Helvetica-Bold", 34)
    
    # Word wrap
    words = title.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if len(test) <= 35:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    
    y = 7.8*inch
    for line in lines:
        canvas_obj.drawString(0.75*inch, y, line)
        y -= 0.55*inch
    
    # Subtitle
    canvas_obj.setFillColorRGB(0.392, 0.439, 0.545)
    canvas_obj.setFont("Helvetica", 16)
    canvas_obj.drawString(0.75*inch, y - 0.25*inch, "Data-Driven Insights for Homeowners")
    
    # Accent line
    canvas_obj.setFillColorRGB(0.063, 0.725, 0.506)
    canvas_obj.rect(0.75*inch, y - 0.6*inch, 2*inch, 5, fill=1)
    
    # Footer
    canvas_obj.setStrokeColorRGB(0.063, 0.725, 0.506)
    canvas_obj.setLineWidth(3)
    canvas_obj.line(0.75*inch, 1.1*inch, 7.75*inch, 1.1*inch)
    
    canvas_obj.setFillColorRGB(0.392, 0.439, 0.545)
    canvas_obj.setFont("Helvetica", 11)
    canvas_obj.drawString(0.75*inch, 0.75*inch, "© 2026 Ungouge.ai")
    canvas_obj.drawRightString(7.75*inch, 0.75*inch, "ungouge.ai")
    
    canvas_obj.showPage()

def header_footer(canvas_obj, doc):
    """Page headers and footers"""
    canvas_obj.saveState()
    
    # Header
    canvas_obj.setStrokeColorRGB(0.063, 0.725, 0.506)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(0.75*inch, 10.45*inch, 7.75*inch, 10.45*inch)
    
    canvas_obj.setFillColorRGB(0.392, 0.439, 0.545)
    canvas_obj.setFont("Helvetica", 10)
    canvas_obj.drawString(0.75*inch, 10.6*inch, "Ungouge.ai")
    
    # Footer
    canvas_obj.setStrokeColorRGB(0.392, 0.439, 0.545)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(0.75*inch, 0.7*inch, 7.75*inch, 0.7*inch)
    
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawString(0.75*inch, 0.5*inch, "ungouge.ai")
    canvas_obj.drawRightString(7.75*inch, 0.5*inch, str(doc.page))
    
    canvas_obj.restoreState()

# Typography styles
style_body = ParagraphStyle(
    'Body',
    fontName='Helvetica',
    fontSize=12,
    leading=19,
    textColor=colors.HexColor('#1f2937'),
    spaceAfter=10,
)

style_h1 = ParagraphStyle(
    'H1',
    fontName='Helvetica-Bold',
    fontSize=28,
    leading=34,
    textColor=colors.HexColor('#10b981'),
    spaceBefore=16,
    spaceAfter=12,
)

style_h2 = ParagraphStyle(
    'H2',
    fontName='Helvetica-Bold',
    fontSize=20,
    leading=26,
    textColor=colors.HexColor('#10b981'),
    spaceBefore=8,
    spaceAfter=12,
    borderWidth=3,
    borderColor=colors.HexColor('#10b981'),
    borderPadding=8,
)

style_h3 = ParagraphStyle(
    'H3',
    fontName='Helvetica-Bold',
    fontSize=15,
    leading=20,
    textColor=colors.HexColor('#374151'),
    spaceBefore=14,
    spaceAfter=8,
)

style_h4 = ParagraphStyle(
    'H4',
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=17,
    textColor=colors.HexColor('#4b5563'),
    spaceBefore=10,
    spaceAfter=6,
)

def html_to_story_smart(html_content):
    """Convert HTML to story with smart grouping to prevent awkward breaks"""
    soup = BeautifulSoup(html_content, 'html.parser')
    story = []
    section_content = []
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'table']):
        
        # H2 starts a new section - keep previous section together
        if element.name == 'h2':
            if section_content:
                story.append(KeepTogether(section_content))
                section_content = []
            story.append(PageBreak())
            section_content.append(Paragraph(element.get_text(), style_h2))
        
        elif element.name == 'h1':
            section_content.append(Paragraph(element.get_text(), style_h1))
        
        elif element.name == 'h3':
            # H3 starts a sub-section - keep together with next few elements
            if len(section_content) > 5:  # Flush if getting long
                story.append(KeepTogether(section_content))
                section_content = []
            section_content.append(Paragraph(element.get_text(), style_h3))
        
        elif element.name == 'h4':
            section_content.append(Paragraph(element.get_text(), style_h4))
        
        elif element.name == 'p':
            section_content.append(Paragraph(element.get_text(), style_body))
        
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li', recursive=False):
                text = '• ' + li.get_text()
                section_content.append(Paragraph(text, style_body))
        
        elif element.name == 'table':
            data = []
            for row in element.find_all('tr'):
                row_data = [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
                data.append(row_data)
            
            if data:
                t = Table(data, hAlign='LEFT')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                section_content.append(t)
                section_content.append(Spacer(1, 10))
    
    # Add final section
    if section_content:
        story.append(KeepTogether(section_content))
    
    return story

# Generate PDF
md_file = Path('/Users/moltbot/clawd/projects/ungouge-app/content/blog/bathroom-remodel-cost-breakdown.md')
output_file = Path('/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/bathroom-remodel-POLISHED.pdf')
output_file.parent.mkdir(parents=True, exist_ok=True)

print("🎨 Generating polished professional PDF...\n")

with open(md_file, 'r') as f:
    content = f.read()

# Extract title
title = "Ungouge Resource"
if content.startswith('---'):
    parts = content.split('---', 2)
    if len(parts) >= 3:
        match = re.search(r'title:\s*"([^"]+)"', parts[1])
        if match:
            title = match.group(1)
        content = parts[2].strip()

# Convert to HTML
html = markdown.markdown(content, extensions=['extra', 'tables'])

# Build PDF
doc = SimpleDocTemplate(
    str(output_file),
    pagesize=letter,
    leftMargin=0.75*inch,
    rightMargin=0.75*inch,
    topMargin=1*inch,
    bottomMargin=0.85*inch,
)

story = html_to_story_smart(html)
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)

# Add cover page manually
from PyPDF2 import PdfReader, PdfWriter

# Create cover separately
cover_path = output_file.with_suffix('.cover.pdf')
c = canvas.Canvas(str(cover_path), pagesize=letter)
create_cover_page(c, title)
c.save()

# Merge
output_reader = PdfReader(str(output_file))
cover_reader = PdfReader(str(cover_path))
writer = PdfWriter()

# Add cover first
writer.add_page(cover_reader.pages[0])

# Add content pages
for page in output_reader.pages:
    writer.add_page(page)

# Write final
final_path = output_file.with_suffix('.final.pdf')
with open(final_path, 'wb') as f:
    writer.write(f)

# Replace original
final_path.replace(output_file)
cover_path.unlink()

print(f"✅ Complete! ({len(output_reader.pages) + 1} pages)")
print(f"📂 {output_file}")
