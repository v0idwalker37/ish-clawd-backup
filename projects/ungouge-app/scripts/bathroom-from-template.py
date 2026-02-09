#!/usr/bin/env python3
"""
Generate bathroom remodel PDF using Jason's template header
"""
from fpdf import FPDF
import markdown
from bs4 import BeautifulSoup
from pathlib import Path
import re

class UngougePDF(FPDF):
    def header(self):
        # Use Jason's header image
        header_path = '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/header-final.jpg'
        try:
            self.image(header_path, 0, 0, 210)  # Full A4 width
            self.ln(35)
        except:
            self.ln(20)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 100, 100)
        self.cell(90, 10, 'ungouge.ai', align='L')
        self.cell(0, 10, f'Page {self.page_no()}', align='R')

# Read bathroom remodel markdown
md_file = Path('/Users/moltbot/clawd/projects/ungouge-app/content/blog/bathroom-remodel-cost-breakdown.md')
with open(md_file, 'r') as f:
    content = f.read()

# Remove frontmatter
if content.startswith('---'):
    parts = content.split('---', 2)
    if len(parts) >= 3:
        content = parts[2].strip()

# Convert to HTML
html = markdown.markdown(content, extensions=['extra', 'tables'])
soup = BeautifulSoup(html, 'html.parser')

# Function to clean text for latin-1 encoding
def clean_text(text):
    """Replace unicode characters that don't work in FPDF"""
    replacements = {
        '\u2014': '-',  # em dash
        '\u2013': '-',  # en dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
        '\u2022': '*',  # bullet
        '\u2026': '...',  # ellipsis
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Remove any remaining non-latin1 characters
    return text.encode('latin-1', 'ignore').decode('latin-1')

# Create PDF
pdf = UngougePDF()
pdf.set_left_margin(15)
pdf.set_right_margin(15)
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=20)

# Process content
for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'table']):
    
    if element.name == 'h1':
        pdf.set_font('Helvetica', 'B', 24)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        pdf.multi_cell(0, 10, clean_text(element.get_text()))
        pdf.ln(3)
    
    elif element.name == 'h2':
        # Page break before H2
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 18)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 9, clean_text(element.get_text()))
        pdf.ln(4)
    
    elif element.name == 'h3':
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 7, clean_text(element.get_text()))
        pdf.ln(2)
    
    elif element.name == 'h4':
        pdf.ln(2)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, clean_text(element.get_text()))
        pdf.ln(1)
    
    elif element.name == 'p':
        pdf.set_font('Helvetica', '', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, clean_text(element.get_text()))
        pdf.ln(2)
    
    elif element.name in ['ul', 'ol']:
        pdf.set_font('Helvetica', '', 12)
        for li in element.find_all('li', recursive=False):
            text = '* ' + clean_text(li.get_text())
            pdf.multi_cell(0, 6, text)
        pdf.ln(2)
    
    elif element.name == 'table':
        # Skip tables - they're too complex for simple PDF
        # Just add a note
        pdf.set_font('Helvetica', 'I', 11)
        pdf.multi_cell(0, 5, '[Table content - see online version]')
        pdf.ln(3)

output_path = '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/Bathroom_Remodel_Final.pdf'
pdf.output(output_path)

print(f"✅ Bathroom remodel PDF created: {output_path}")
print(f"📄 {pdf.page_no()} pages")
