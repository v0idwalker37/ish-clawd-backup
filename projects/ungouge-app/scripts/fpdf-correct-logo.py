#!/usr/bin/env python3
"""
FPDF header with CORRECT logo from shared drive
"""
from fpdf import FPDF

class UngougePDF(FPDF):
    def header(self):
        # Green Header Background - #10b981
        self.set_fill_color(16, 185, 129)
        self.rect(0, 0, 210, 40, 'F')
        
        # Logo from shared drive
        logo_path = '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/logo.png'
        try:
            self.image(logo_path, 10, 8, 60)
        except Exception as e:
            print(f"Logo error: {e}")
            # Fallback
            self.set_font('Helvetica', 'B', 24)
            self.set_text_color(255, 255, 255)
            self.set_xy(10, 12)
            self.cell(0, 10, 'Ungouge.ai')
        
        # Tagline
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 28)
        self.cell(0, 10, 'Know Before You Sign', align='C')
        
        self.ln(40)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'ungouge.ai - Page {self.page_no()}', align='C')

# Create PDF
pdf = UngougePDF()
pdf.add_page()
pdf.set_font('Helvetica', '', 12)

# Sample content
pdf.set_text_color(0, 0, 0)
pdf.set_font('Helvetica', 'B', 24)
pdf.cell(0, 10, 'Sample Document Title', ln=True)
pdf.ln(5)

pdf.set_font('Helvetica', '', 12)
pdf.multi_cell(0, 6, 'This is sample body text with the CORRECT logo from the shared drive.')

output_path = '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/Ungouge_Correct_Logo.pdf'
pdf.output(output_path)

print(f"✅ PDF created with correct logo: {output_path}")
