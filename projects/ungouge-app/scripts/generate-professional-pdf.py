#!/usr/bin/env python3
"""Generate PROFESSIONAL branded PDF with proper design"""
import fitz
import markdown
from pathlib import Path
import re

def create_professional_pdf(md_file, output_file):
    """Create professional PDF with cover page + proper design"""
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            title_match = re.search(r'title:\s*"([^"]+)"', parts[1])
            title = title_match.group(1) if title_match else "Ungouge Resource"
            content = parts[2].strip()
        else:
            title = "Ungouge Resource"
    else:
        title = "Ungouge Resource"
    
    # Convert to HTML
    html = markdown.markdown(content, extensions=['extra', 'tables'])
    
    # Split at H2 for page breaks
    sections = re.split(r'(<h2[^>]*>.*?</h2>)', html, flags=re.DOTALL)
    
    # Recombine H2 with following content
    formatted_sections = []
    i = 0
    while i < len(sections):
        if '<h2' in sections[i]:
            # This is an H2, combine with next section
            if i + 1 < len(sections):
                formatted_sections.append(sections[i] + sections[i + 1])
                i += 2
            else:
                formatted_sections.append(sections[i])
                i += 1
        else:
            # This is content before first H2
            if sections[i].strip():
                formatted_sections.append(sections[i])
            i += 1
    
    # Brand colors
    GREEN = "#10b981"
    DARK = "#0f172a"
    LIGHT = "#f8fafc"
    GRAY = "#64748b"
    
    doc = fitz.open()
    
    # === COVER PAGE ===
    cover = doc.new_page(width=612, height=792)
    
    # Green accent bar at top
    cover.draw_rect(fitz.Rect(0, 0, 612, 120), color=(0.063, 0.725, 0.506), fill=(0.063, 0.725, 0.506))
    
    # Logo/brand name
    cover.insert_text((60, 70), "Ungouge.ai", fontsize=36, color=(0.97, 0.98, 0.99))
    cover.insert_text((60, 95), "Know Before You Sign", fontsize=14, color=(0.97, 0.98, 0.99))
    
    # Main title
    title_lines = []
    words = title.split()
    current_line = ""
    for word in words:
        if len(current_line + " " + word) < 45:
            current_line = (current_line + " " + word).strip()
        else:
            title_lines.append(current_line)
            current_line = word
    if current_line:
        title_lines.append(current_line)
    
    y_pos = 220
    for line in title_lines:
        cover.insert_text((60, y_pos), line, fontsize=32)
        y_pos += 40
    
    # Subtitle/tagline
    cover.insert_text((60, y_pos + 20), "Data-driven insights for homeowners", fontsize=16, color=(0.39, 0.44, 0.55))
    
    # Bottom footer
    cover.draw_line(fitz.Point(60, 720), fitz.Point(552, 720), color=(0.063, 0.725, 0.506), width=2)
    cover.insert_text((60, 750), "© 2026 Ungouge.ai · ungouge.ai", fontsize=10, color=(0.39, 0.44, 0.55))
    
    # === CONTENT PAGES ===
    page_num = 2
    
    for idx, section in enumerate(formatted_sections):
        if not section.strip():
            continue
        
        # Build HTML with CONSISTENT 12pt font
        full_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
    body {{ 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
        font-size: 12pt; 
        line-height: 1.7; 
        color: #1f2937;
        margin: 0;
        padding: 0;
    }}
    h1 {{ 
        font-size: 28pt; 
        font-weight: 700; 
        color: {GREEN}; 
        margin: 20px 0 15px 0; 
        line-height: 1.3; 
    }}
    h2 {{ 
        font-size: 22pt; 
        font-weight: 600; 
        color: {GREEN}; 
        margin: 0 0 15px 0; 
        padding-top: 0;
        border-top: 3px solid {GREEN};
        padding-top: 10px;
    }}
    h3 {{ 
        font-size: 16pt; 
        font-weight: 600; 
        color: #374151; 
        margin: 20px 0 10px 0; 
    }}
    h4 {{ 
        font-size: 14pt; 
        font-weight: 600; 
        color: #4b5563; 
        margin: 15px 0 8px 0; 
    }}
    p {{ 
        margin: 0 0 12pt 0;
        font-size: 12pt;
    }}
    ul, ol {{ 
        margin: 10pt 0 15pt 25pt;
        font-size: 12pt;
    }}
    li {{ 
        margin: 5pt 0;
        font-size: 12pt;
    }}
    table {{ 
        border-collapse: collapse; 
        width: 100%; 
        margin: 20pt 0;
        font-size: 11pt;
    }}
    th {{ 
        background-color: {GREEN}; 
        color: white; 
        padding: 10pt; 
        text-align: left; 
        font-weight: 600;
        font-size: 11pt;
    }}
    td {{ 
        border: 1px solid #e5e7eb; 
        padding: 8pt;
        font-size: 11pt;
    }}
    tr:nth-child(even) {{ 
        background-color: #f9fafb; 
    }}
    strong {{ 
        color: #111827; 
        font-weight: 600;
        font-size: 12pt;
    }}
    blockquote {{ 
        border-left: 4px solid {GREEN}; 
        margin: 15pt 0; 
        padding-left: 20pt; 
        color: #6b7280;
        font-size: 12pt;
    }}
</style>
</head>
<body>{section}</body>
</html>"""
        
        # Create new page
        page = doc.new_page(width=612, height=792)
        
        # Header
        page.draw_line(fitz.Point(60, 50), fitz.Point(552, 50), color=(0.063, 0.725, 0.506), width=2)
        page.insert_text((60, 45), "Ungouge.ai", fontsize=10, color=(0.39, 0.44, 0.55))
        
        # Content area
        rect = fitz.Rect(60, 70, 552, 720)
        page.insert_htmlbox(rect, full_html)
        
        # Footer with page number
        page.draw_line(fitz.Point(60, 740), fitz.Point(552, 740), color=(0.39, 0.44, 0.55), width=0.5)
        page.insert_text((520, 760), f"{page_num}", fontsize=10, color=(0.39, 0.44, 0.55))
        page.insert_text((60, 760), "ungouge.ai", fontsize=9, color=(0.39, 0.44, 0.55))
        
        page_num += 1
    
    # Save
    doc.save(output_file)
    doc.close()
    print(f"✅ Created: {output_file.name}")

# Generate
md_file = Path('/Users/moltbot/clawd/projects/ungouge-app/content/blog/bathroom-remodel-cost-breakdown.md')
output_file = Path('/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/bathroom-remodel-professional-v2.pdf')
output_file.parent.mkdir(parents=True, exist_ok=True)

print("🎨 Generating PROFESSIONAL branded PDF...\n")
create_professional_pdf(md_file, output_file)
print(f"\n✅ Professional PDF complete!")
print(f"📂 {output_file}")
