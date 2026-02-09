#!/usr/bin/env python3
"""Generate PDFs using PyMuPDF"""
from pathlib import Path
import markdown
import fitz  # PyMuPDF

blog_dir = Path('/Users/moltbot/clawd/projects/ungouge-app/content/blog')
output_dir = Path('/Users/moltbot/clawd/projects/ungouge-app/output/blog-pdfs-fixed')
output_dir.mkdir(parents=True, exist_ok=True)

md_files = sorted(blog_dir.glob('*.md'))

print(f"Converting {len(md_files)} blog posts to PDF...\n")

for md_file in md_files:
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML
    html_content = markdown.markdown(md_content, extensions=['extra'])
    
    # Create PDF
    pdf_file = output_dir / f"{md_file.stem}.pdf"
    
    try:
        # Create new PDF
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)  # Letter size
        
        # Insert HTML (PyMuPDF supports this)
        story = fitz.Story(html=html_content)
        writer = fitz.DocumentWriter(str(pdf_file))
        
        # Simple layout - one long page
        mediabox = fitz.paper_rect("letter")
        where = mediabox + (36, 36, -36, -36)  # margins
        
        more = True
        while more:
            device = writer.begin_page(mediabox)
            more, _ = story.place(where)
            story.draw(device)
            writer.end_page()
        
        writer.close()
        print(f"✓ {pdf_file.name}")
        
    except Exception as e:
        print(f"✗ Failed: {md_file.name} - {str(e)}")

print(f"\n✅ Done! PDFs in: {output_dir}")
