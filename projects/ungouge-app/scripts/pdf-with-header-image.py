#!/usr/bin/env python3
"""
PDF template with Jason's header image as drop-in
"""
from fpdf import FPDF

class UngougePDF(FPDF):
    def header(self):
        # Use Jason's header image directly
        header_path = '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/header-final.jpg'
        try:
            # Insert header image - full width
            self.image(header_path, 0, 0, 210)  # Full A4 width (210mm)
            self.ln(35)  # Space after header
        except Exception as e:
            print(f"Header error: {e}")
            self.ln(20)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'ungouge.ai - Page {self.page_no()}', align='C')

# Create test PDF
pdf = UngougePDF()
pdf.add_page()

# Sample content
pdf.set_font('Helvetica', 'B', 24)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 10, 'Bathroom Remodel Cost Breakdown', ln=True)
pdf.ln(5)

pdf.set_font('Helvetica', '', 12)
pdf.multi_cell(0, 6, 'This is a test document using your header image. The header should appear exactly as you designed it.')

# Add another page to test header consistency
pdf.add_page()
pdf.set_font('Helvetica', 'B', 18)
pdf.cell(0, 10, 'Section 2: Testing Header on Multiple Pages', ln=True)
pdf.ln(5)

pdf.set_font('Helvetica', '', 12)
pdf.multi_cell(0, 6, 'This is page 2 to verify the header appears on every page.')

output_path = '/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/Test_With_Header_Image.pdf'
pdf.output(output_path)

print(f"✅ PDF with header image created: {output_path}")
