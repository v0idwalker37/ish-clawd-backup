#!/usr/bin/env python3
"""
SIMPLE bathroom PDF - minimal formatting, just get it working
"""
from fpdf import FPDF
from pathlib import Path

class SimplePDF(FPDF):
    def header(self):
        header_path = '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/header-final.jpg'
        try:
            self.image(header_path, 0, 0, 210)
            self.ln(40)
        except:
            self.ln(25)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 100, 100)
        self.cell(90, 10, 'ungouge.ai', align='L')
        self.cell(0, 10, f'Page {self.page_no()}', align='R')

# Read markdown as plain text
md_file = Path('/Users/moltbot/clawd/projects/ungouge-app/content/blog/bathroom-remodel-cost-breakdown.md')
with open(md_file, 'r') as f:
    lines = f.readlines()

# Skip frontmatter
start = 0
if lines[0].startswith('---'):
    for i, line in enumerate(lines[1:], 1):
        if line.startswith('---'):
            start = i + 1
            break

# Create PDF
pdf = SimplePDF()
pdf.set_left_margin(20)
pdf.set_right_margin(20)
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=25)

# Add content line by line
for line in lines[start:]:
    line = line.strip()
    if not line:
        pdf.ln(4)
        continue
    
    # Clean unicode
    line = line.replace('\u2014', '-').replace('\u2013', '-')
    line = line.replace('\u2018', "'").replace('\u2019', "'")
    line = line.replace('\u201c', '"').replace('\u201d', '"')
    line = line.encode('latin-1', 'ignore').decode('latin-1')
    
    # Detect headings by markdown syntax
    if line.startswith('# '):
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 20)
        pdf.multi_cell(0, 8, line[2:])
        pdf.ln(2)
    elif line.startswith('## '):
        pdf.add_page()  # New page for H2
        pdf.set_font('Helvetica', 'B', 16)
        pdf.multi_cell(0, 7, line[3:])
        pdf.ln(2)
    elif line.startswith('### '):
        pdf.ln(2)
        pdf.set_font('Helvetica', 'B', 13)
        pdf.multi_cell(0, 6, line[4:])
        pdf.ln(1)
    elif line.startswith('####'):
        pdf.set_font('Helvetica', 'B', 12)
        pdf.multi_cell(0, 5, line[5:])
    elif line.startswith('|') or line.startswith('---'):
        # Skip table formatting
        continue
    else:
        pdf.set_font('Helvetica', '', 11)
        pdf.multi_cell(0, 5, line)

output = '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/Bathroom_Simple.pdf'
pdf.output(output)
print(f"✅ Created: {output}")
print(f"📄 {pdf.page_no()} pages")
