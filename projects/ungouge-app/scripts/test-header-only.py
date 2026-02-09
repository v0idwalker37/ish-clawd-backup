#!/usr/bin/env python3
"""
Test JUST the header - green banner with real logo
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pathlib import Path

output = Path('/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/HEADER-TEST.pdf')
output.parent.mkdir(parents=True, exist_ok=True)

c = canvas.Canvas(str(output), pagesize=letter)

# Green banner across top
GREEN = (0.063, 0.725, 0.506)
c.setFillColorRGB(*GREEN)
c.rect(0, 11*inch - 2*inch, 8.5*inch, 2*inch, fill=1)

# Logo image (actual Ungouge logo)
logo_path = '/Users/moltbot/clawd/projects/ungouge-app/frontend/public/images/logo.png'
try:
    logo = ImageReader(logo_path)
    # Logo dimensions: 1280x400, aspect ratio 3.2:1
    # Scale to fit nicely in header
    logo_width = 3*inch
    logo_height = logo_width / 3.2  # maintain aspect ratio
    
    # Position in green banner
    c.drawImage(logo, 0.75*inch, 11*inch - 1.2*inch - logo_height/2, 
                width=logo_width, height=logo_height, mask='auto')
except Exception as e:
    # Fallback if logo doesn't load
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(0.75*inch, 11*inch - 1.1*inch, "Ungouge.ai")

# Tagline in white
c.setFillColorRGB(0.97, 0.98, 0.99)
c.setFont("Helvetica", 14)
c.drawString(4*inch, 11*inch - 1.4*inch, "Know Before You Sign")

c.showPage()
c.save()

print(f"✅ Header test saved: {output}")
print("Check if logo displays correctly")
