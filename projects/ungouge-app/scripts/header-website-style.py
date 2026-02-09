#!/usr/bin/env python3
"""
Header matching website style - adapted for print
Website: Dark gradient bg, green gradient text
PDF: Light bg, green accents, logo, print-friendly
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pathlib import Path

output = Path('/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/HEADER-WEBSITE-STYLE.pdf')
output.parent.mkdir(parents=True, exist_ok=True)

c = canvas.Canvas(str(output), pagesize=letter)

# Clean white background (print-friendly)
c.setFillColorRGB(1, 1, 1)
c.rect(0, 0, 8.5*inch, 11*inch, fill=1)

# Subtle gray background for header area (like website's dark theme but lighter)
c.setFillColorRGB(0.97, 0.98, 0.99)  # Very light gray
c.rect(0, 11*inch - 1.5*inch, 8.5*inch, 1.5*inch, fill=1)

# Green accent line at bottom of header (website's green)
GREEN = (0.063, 0.725, 0.506)  # #10b981
c.setFillColorRGB(*GREEN)
c.rect(0, 11*inch - 1.5*inch, 8.5*inch, 4, fill=1)  # 4pt line

# Logo 
logo_path = '/Users/moltbot/clawd/projects/ungouge-app/frontend/public/images/logo.png'
try:
    logo = ImageReader(logo_path)
    # Scale to fit header nicely
    logo_width = 2.5*inch
    logo_height = logo_width / 3.2
    
    # Center vertically in header area
    c.drawImage(logo, 0.75*inch, 11*inch - 1*inch - logo_height/2, 
                width=logo_width, height=logo_height, mask='auto')
    
    # Tagline next to logo (like website)
    c.setFillColorRGB(0.392, 0.439, 0.545)  # Gray like website #94a3b8
    c.setFont("Helvetica", 13)
    c.drawString(3.5*inch, 11*inch - 0.9*inch, "Know Before You Sign")
    
except Exception as e:
    print(f"Error loading logo: {e}")
    # Fallback
    c.setFillColorRGB(*GREEN)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(0.75*inch, 11*inch - 0.95*inch, "Ungouge.ai")

# Add sample content to show full page
c.setFillColorRGB(0.122, 0.161, 0.220)
c.setFont("Helvetica-Bold", 28)
c.drawString(0.75*inch, 9*inch, "Sample Title")

c.setFont("Helvetica", 12)
c.drawString(0.75*inch, 8.5*inch, "This is sample body text to show the full layout.")

# Footer with green accent
c.setStrokeColorRGB(*GREEN)
c.setLineWidth(2)
c.line(0.75*inch, 0.8*inch, 7.75*inch, 0.8*inch)

c.setFillColorRGB(0.392, 0.439, 0.545)
c.setFont("Helvetica", 9)
c.drawString(0.75*inch, 0.6*inch, "ungouge.ai")

c.showPage()
c.save()

print(f"✅ Website-style header saved: {output}")
