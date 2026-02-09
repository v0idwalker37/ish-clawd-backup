#!/usr/bin/env python3
"""
FPDF header template for Ungouge PDFs
Using Jason's script as base
"""
from fpdf import FPDF

class UngougePDF(FPDF):
    def header(self):
        # 1. Green Header Background
        # #10b981 = RGB(16, 185, 129)
        self.set_fill_color(16, 185, 129)
        self.rect(0, 0, 210, 40, 'F')  # Width 210mm (A4), Height 40mm
        
        # 2. Logo
        logo_path = '/Users/moltbot/clawd/projects/ungouge-app/frontend/public/images/logo.png'
        try:
            self.image(logo_path, 10, 8, 60)  # x=10, y=8, w=60mm
        except:
            # Fallback if logo doesn't load
            self.set_font('Arial', 'B', 24)
            self.set_text_color(255, 255, 255)
            self.set_xy(10, 12)
            self.cell(0, 10, 'Ungouge.ai', 0, 0, 'L')
        
        # 3. Tagline
        self.set_font('Arial', 'B', 12)
        self.set_text_color(255, 255, 255)  # White text
        self.set_xy(10, 28)
        self.cell(0, 10, 'Know Before You Sign', 0, 0, 'C')
        
        # Line break to move to main body
        self.ln(40)
    
    def footer(self):
        # Footer with page number
        self.set_y(-15)
        self.set_font('Arial', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'ungouge.ai - Page {self.page_no()}', 0, 0, 'C')

# Create PDF object
pdf = UngougePDF()
pdf.add_page()
pdf.set_font('Arial', '', 12)

# Add sample content
pdf.set_text_color(0, 0, 0)
pdf.set_font('Arial', 'B', 24)
pdf.cell(0, 10, 'Sample Document Title', 0, 1, 'L')
pdf.ln(5)

pdf.set_font('Arial', '', 12)
pdf.multi_cell(0, 6, 'This is sample body text to show how the header and footer will appear on every page. The green header contains the Ungouge.ai logo and tagline.')

# Save the file
output_path = '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/Ungouge_FPDF_Template.pdf'
pdf.output(output_path)

print(f"✅ FPDF template created: {output_path}")
