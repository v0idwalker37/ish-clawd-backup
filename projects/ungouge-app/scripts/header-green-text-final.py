#!/usr/bin/env python3
"""
Header with GREEN text branding (matches website)
NO blue logo - just green text like the website
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from pathlib import Path

output = Path('/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/HEADER-GREEN-FINAL.pdf')
output.parent.mkdir(parents=True, exist_ok=True)

c = canvas.Canvas(str(output), pagesize=letter)

# White background
c.setFillColorRGB(1, 1, 1)
c.rect(0, 0, 8.5*inch, 11*inch, fill=1)

# Light header area
c.setFillColorRGB(0.97, 0.98, 0.99)
c.rect(0, 11*inch - 1.5*inch, 8.5*inch, 1.5*inch, fill=1)

# GREEN accent line (brand color)
GREEN = (0.063, 0.725, 0.506)  # #10b981
c.setFillColorRGB(*GREEN)
c.rect(0, 11*inch - 1.5*inch, 8.5*inch, 4, fill=1)

# Brand name in GREEN (matches website)
c.setFillColorRGB(*GREEN)
c.setFont("Helvetica-Bold", 36)
c.drawString(0.75*inch, 11*inch - 0.95*inch, "Ungouge.ai")

# Tagline in gray
c.setFillColorRGB(0.392, 0.439, 0.545)
c.setFont("Helvetica", 13)
c.drawString(0.75*inch, 11*inch - 1.25*inch, "Know Before You Sign")

# Sample content
c.setFillColorRGB(0.122, 0.161, 0.220)
c.setFont("Helvetica-Bold", 28)
c.drawString(0.75*inch, 9*inch, "Sample Title")

c.setFont("Helvetica", 12)
c.drawString(0.75*inch, 8.5*inch, "This is sample body text to show the full layout.")

# Footer
c.setStrokeColorRGB(*GREEN)
c.setLineWidth(2)
c.line(0.75*inch, 0.8*inch, 7.75*inch, 0.8*inch)

c.setFillColorRGB(0.392, 0.439, 0.545)
c.setFont("Helvetica", 9)
c.drawString(0.75*inch, 0.6*inch, "ungouge.ai")

c.showPage()
c.save()

print(f"✅ GREEN text header (no blue logo): {output}")
