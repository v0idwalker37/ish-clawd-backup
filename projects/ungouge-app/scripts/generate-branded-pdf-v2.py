#!/usr/bin/env python3
"""Generate branded Ungouge PDF - simpler approach"""
import fitz  # PyMuPDF
import markdown
from pathlib import Path
import re

def split_at_h2(html):
    """Split HTML content at H2 tags for page breaks"""
    # Find all H2 positions
    h2_pattern = r'<h2[^>]*>.*?</h2>'
    matches = list(re.finditer(h2_pattern, html, re.DOTALL))
    
    if not matches:
        return [html]
    
    sections = []
    last_end = 0
    
    for match in matches:
        # Everything before this H2
        before = html[last_end:match.start()].strip()
        if before:
            sections.append(before)
        # This H2 and everything until next H2
        last_end = match.start()
    
    # Add final section
    if last_end < len(html):
        sections.append(html[last_end:].strip())
    
    return sections if sections else [html]

def create_branded_pdf(md_file, output_file):
    """Create a branded PDF from markdown"""
    
    # Read and process markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    # Convert to HTML
    html = markdown.markdown(content, extensions=['extra', 'tables'])
    
    # Split at H2 headings for page breaks
    sections = split_at_h2(html)
    
    # Brand colors
    GREEN = "#10b981"
    GRAY = "#94a3b8"
    
    # Full styled template
    def make_html(body_html, page_num, is_first=False):
        header = f"""
        <div style="border-bottom: 2px solid {GREEN}; padding-bottom: 8px; margin-bottom: 25px;">
            <span style="font-size: 20px; font-weight: 700; color: {GREEN};">Ungouge.ai</span>
            <span style="font-size: 10px; color: {GRAY}; margin-left: 10px;">Know Before You Sign</span>
        </div>
        """ if not is_first else ""
        
        return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; 
       font-size: 11pt; line-height: 1.6; color: #1f2937; margin: 0; padding: 20px; }}
h1 {{ font-size: 26pt; font-weight: 700; color: {GREEN}; margin: 15px 0 12px 0; line-height: 1.2; }}
h2 {{ font-size: 18pt; font-weight: 600; color: {GREEN}; margin: 25px 0 10px 0; 
      padding-top: 8px; border-top: 2px solid {GREEN}; }}
h3 {{ font-size: 14pt; font-weight: 600; color: #374151; margin: 18px 0 8px 0; }}
h4 {{ font-size: 12pt; font-weight: 600; color: #4b5563; margin: 12px 0 6px 0; }}
p {{ margin: 0 0 10px 0; }}
ul, ol {{ margin: 8px 0 12px 20px; }}
li {{ margin: 4px 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 10pt; }}
th {{ background-color: {GREEN}; color: white; padding: 8px; text-align: left; font-weight: 600; }}
td {{ border: 1px solid #e5e7eb; padding: 6px; }}
tr:nth-child(even) {{ background-color: #f9fafb; }}
strong {{ color: #111827; font-weight: 600; }}
blockquote {{ border-left: 3px solid {GREEN}; margin: 12px 0; padding-left: 15px; color: #6b7280; }}
</style></head><body>
{header}
{body_html}
</body></html>"""
    
    # Create PDF
    doc = fitz.open()
    
    for idx, section in enumerate(sections):
        if not section.strip():
            continue
        
        is_first = (idx == 0)
        html_content = make_html(section, idx + 1, is_first)
        
        # Create new page
        page = doc.new_page(width=612, height=792)  # Letter size
        
        # Insert HTML
        rect = fitz.Rect(50, 50, 562, 742)  # Margins
        page.insert_htmlbox(rect, html_content)
    
    # Save
    doc.save(output_file)
    doc.close()
    print(f"✅ Created: {output_file.name}")

# Generate
md_file = Path('/Users/moltbot/clawd/projects/ungouge-app/content/blog/bathroom-remodel-cost-breakdown.md')
output_file = Path('/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/bathroom-remodel-branded.pdf')
output_file.parent.mkdir(parents=True, exist_ok=True)

print("🎨 Generating branded PDF with Ungouge template...\n")
create_branded_pdf(md_file, output_file)
print(f"\n✅ Proof of concept complete!")
print(f"📂 Location: {output_file}")
