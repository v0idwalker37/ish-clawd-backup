#!/usr/bin/env python3
"""
Generate POLISHED professional PDF with strict typography control
Key fixes:
- 12pt body text EVERYWHERE (no variation)
- Professional cover page with visual design
- Consistent font sizes across all pages
- Smart page breaks at H2 sections
"""
import fitz
import markdown
from pathlib import Path
import re

def create_polished_pdf(md_file, output_file):
    """Create publication-quality PDF"""
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title from frontmatter
    title = "Ungouge Resource"
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            title_match = re.search(r'title:\s*"([^"]+)"', parts[1])
            if title_match:
                title = title_match.group(1)
            content = parts[2].strip()
    
    # Convert markdown to HTML
    html = markdown.markdown(content, extensions=['extra', 'tables'])
    
    # Split content at H2 tags for page breaks
    sections = re.split(r'(<h2[^>]*>.*?</h2>)', html, flags=re.DOTALL)
    
    # Combine H2 with following content
    page_sections = []
    i = 0
    while i < len(sections):
        if '<h2' in sections[i]:
            section_content = sections[i]
            if i + 1 < len(sections):
                section_content += sections[i + 1]
                i += 2
            else:
                i += 1
            page_sections.append(section_content)
        else:
            if sections[i].strip():
                page_sections.append(sections[i])
            i += 1
    
    # Brand colors (RGB 0-1)
    GREEN = (0.063, 0.725, 0.506)  # #10b981
    DARK = (0.059, 0.090, 0.165)   # #0f172a
    LIGHT = (0.973, 0.980, 0.988)  # #f8fafc
    GRAY = (0.392, 0.439, 0.545)   # #64748b
    BLACK = (0.122, 0.161, 0.220)  # #1f2937
    
    doc = fitz.open()
    
    # ==================== COVER PAGE ====================
    cover = doc.new_page(width=612, height=792)
    
    # Top accent bar (green)
    cover.draw_rect(fitz.Rect(0, 0, 612, 140), color=GREEN, fill=GREEN)
    
    # Logo area (white text on green)
    cover.insert_text((60, 75), "Ungouge.ai", fontsize=40, color=LIGHT)
    cover.insert_text((60, 105), "Know Before You Sign", fontsize=15, color=LIGHT)
    
    # Main title area (large, multi-line if needed)
    # Break title into lines (max ~40 chars per line)
    title_words = title.split()
    title_lines = []
    current_line = ""
    for word in title_words:
        test_line = (current_line + " " + word).strip()
        if len(test_line) <= 40:
            current_line = test_line
        else:
            if current_line:
                title_lines.append(current_line)
            current_line = word
    if current_line:
        title_lines.append(current_line)
    
    # Draw title
    y = 240
    for line in title_lines:
        cover.insert_text((60, y), line, fontsize=36, color=BLACK)
        y += 48
    
    # Subtitle
    cover.insert_text((60, y + 30), "Data-Driven Insights for Homeowners", fontsize=17, color=GRAY)
    
    # Visual element - simple green box/accent
    cover.draw_rect(fitz.Rect(60, y + 80, 180, y + 85), color=GREEN, fill=GREEN)
    
    # Bottom footer
    cover.draw_line(fitz.Point(60, 730), fitz.Point(552, 730), color=GREEN, width=3)
    cover.insert_text((60, 760), "© 2026 Ungouge.ai", fontsize=11, color=GRAY)
    cover.insert_text((480, 760), "ungouge.ai", fontsize=11, color=GRAY)
    
    # ==================== CONTENT PAGES ====================
    
    # Standard typography sizes (STRICT)
    BODY_SIZE = 12
    H1_SIZE = 28
    H2_SIZE = 20
    H3_SIZE = 15
    H4_SIZE = 13
    TABLE_SIZE = 11
    
    page_num = 2
    
    for section_html in page_sections:
        if not section_html.strip():
            continue
        
        # Build HTML with ABSOLUTE size control
        full_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
    * {{ margin: 0; padding: 0; }}
    body {{ 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
        font-size: {BODY_SIZE}pt !important;
        line-height: 1.65;
        color: #1f2937;
    }}
    h1 {{ 
        font-size: {H1_SIZE}pt !important;
        font-weight: 700;
        color: #10b981;
        margin: 18pt 0 14pt 0;
        line-height: 1.3;
    }}
    h2 {{ 
        font-size: {H2_SIZE}pt !important;
        font-weight: 600;
        color: #10b981;
        margin: 0 0 14pt 0;
        padding-top: 10pt;
        border-top: 3px solid #10b981;
    }}
    h3 {{ 
        font-size: {H3_SIZE}pt !important;
        font-weight: 600;
        color: #374151;
        margin: 16pt 0 10pt 0;
    }}
    h4 {{ 
        font-size: {H4_SIZE}pt !important;
        font-weight: 600;
        color: #4b5563;
        margin: 12pt 0 8pt 0;
    }}
    p {{ 
        font-size: {BODY_SIZE}pt !important;
        margin: 0 0 10pt 0;
        line-height: 1.65;
    }}
    ul, ol {{ 
        font-size: {BODY_SIZE}pt !important;
        margin: 8pt 0 12pt 22pt;
        line-height: 1.65;
    }}
    li {{ 
        font-size: {BODY_SIZE}pt !important;
        margin: 4pt 0;
    }}
    table {{ 
        border-collapse: collapse;
        width: 100%;
        margin: 16pt 0;
        font-size: {TABLE_SIZE}pt !important;
    }}
    th {{ 
        background-color: #10b981;
        color: white;
        padding: 9pt;
        text-align: left;
        font-weight: 600;
        font-size: {TABLE_SIZE}pt !important;
    }}
    td {{ 
        border: 1px solid #e5e7eb;
        padding: 7pt;
        font-size: {TABLE_SIZE}pt !important;
    }}
    tr:nth-child(even) {{ background-color: #f9fafb; }}
    strong {{ 
        font-weight: 600;
        font-size: {BODY_SIZE}pt !important;
    }}
    blockquote {{ 
        border-left: 4px solid #10b981;
        margin: 12pt 0;
        padding-left: 18pt;
        color: #6b7280;
        font-size: {BODY_SIZE}pt !important;
    }}
</style>
</head>
<body>{section_html}</body>
</html>"""
        
        # Create new page
        page = doc.new_page(width=612, height=792)
        
        # Header line
        page.draw_line(fitz.Point(60, 52), fitz.Point(552, 52), color=GREEN, width=2)
        page.insert_text((60, 48), "Ungouge.ai", fontsize=10, color=GRAY)
        
        # Content area (more vertical space)
        rect = fitz.Rect(60, 72, 552, 720)
        page.insert_htmlbox(rect, full_html)
        
        # Footer
        page.draw_line(fitz.Point(60, 738), fitz.Point(552, 738), color=GRAY, width=0.5)
        page.insert_text((60, 758), "ungouge.ai", fontsize=9, color=GRAY)
        page.insert_text((520, 758), f"{page_num}", fontsize=10, color=GRAY)
        
        page_num += 1
    
    # Save
    doc.save(output_file)
    doc.close()
    return len(page_sections) + 1  # total pages

# Generate
md_file = Path('/Users/moltbot/clawd/projects/ungouge-app/content/blog/bathroom-remodel-cost-breakdown.md')
output_file = Path('/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/bathroom-remodel-FINAL.pdf')
output_file.parent.mkdir(parents=True, exist_ok=True)

print("🎨 Generating FINAL polished PDF with strict typography...\n")
total_pages = create_polished_pdf(md_file, output_file)
print(f"\n✅ Complete! {total_pages} pages")
print(f"📂 {output_file}")
