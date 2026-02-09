#!/usr/bin/env python3
"""Generate branded Ungouge PDF with proper page breaks"""
import fitz  # PyMuPDF
import markdown
from pathlib import Path

def markdown_to_branded_pdf(md_file, output_file):
    """Convert markdown to branded PDF with page breaks at sections"""
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove frontmatter if present
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=['extra', 'tables'])
    
    # Split by H2 headings for page breaks
    # This is a simple approach - split on <h2> tags
    sections = []
    current_section = []
    
    for line in html_content.split('\n'):
        if '<h2>' in line and current_section:
            # Save current section and start new one
            sections.append('\n'.join(current_section))
            current_section = [line]
        else:
            current_section.append(line)
    
    # Add final section
    if current_section:
        sections.append('\n'.join(current_section))
    
    # Ungouge brand colors
    GREEN = "#10b981"
    DARK_BG = "#0f172a"
    LIGHT_TEXT = "#f8fafc"
    GRAY = "#94a3b8"
    
    # Create styled HTML for each section with branding
    def style_section(section_html, is_first=False):
        header_html = f"""
        <div style="border-bottom: 3px solid {GREEN}; padding-bottom: 10px; margin-bottom: 30px;">
            <div style="font-size: 24px; font-weight: 700; color: {GREEN};">Ungouge.ai</div>
            <div style="font-size: 11px; color: {GRAY};">Know Before You Sign</div>
        </div>
        """ if not is_first else ""
        
        footer_html = f"""
        <div style="position: absolute; bottom: 40px; left: 50px; right: 50px; border-top: 1px solid #e0e0e0; padding-top: 10px; font-size: 10px; color: {GRAY}; text-align: center;">
            ungouge.ai · Data-driven quote verification
        </div>
        """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: letter;
                    margin: 0.75in;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                    font-size: 11pt;
                    line-height: 1.7;
                    color: #1f2937;
                }}
                h1 {{
                    font-size: 28pt;
                    font-weight: 700;
                    color: {GREEN};
                    margin: 20px 0 15px 0;
                    line-height: 1.2;
                }}
                h2 {{
                    font-size: 20pt;
                    font-weight: 600;
                    color: {GREEN};
                    margin: 30px 0 12px 0;
                    padding-top: 5px;
                    border-top: 2px solid {GREEN};
                }}
                h3 {{
                    font-size: 15pt;
                    font-weight: 600;
                    color: #374151;
                    margin: 20px 0 10px 0;
                }}
                h4 {{
                    font-size: 13pt;
                    font-weight: 600;
                    color: #4b5563;
                    margin: 15px 0 8px 0;
                }}
                p {{
                    margin: 0 0 12px 0;
                }}
                ul, ol {{
                    margin: 10px 0 15px 25px;
                }}
                li {{
                    margin: 5px 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                    font-size: 10pt;
                }}
                th {{
                    background-color: {GREEN};
                    color: white;
                    padding: 10px;
                    text-align: left;
                    font-weight: 600;
                }}
                td {{
                    border: 1px solid #e5e7eb;
                    padding: 8px;
                }}
                tr:nth-child(even) {{
                    background-color: #f9fafb;
                }}
                strong {{
                    color: #111827;
                    font-weight: 600;
                }}
                code {{
                    background-color: #f3f4f6;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 10pt;
                }}
                blockquote {{
                    border-left: 4px solid {GREEN};
                    margin: 15px 0;
                    padding-left: 20px;
                    color: #6b7280;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            {header_html}
            {section_html}
            {footer_html}
        </body>
        </html>
        """
    
    # Create PDF
    doc = fitz.open()
    
    for idx, section in enumerate(sections):
        if not section.strip():
            continue
            
        is_first = (idx == 0)
        html = style_section(section, is_first)
        
        # Use fitz.Story for HTML rendering
        story = fitz.Story(html=html)
        writer = doc if idx == 0 else doc
        
        # Create pages for this section
        mediabox = fitz.paper_rect("letter")
        where = mediabox + (54, 54, -54, -54)  # 0.75 inch margins
        
        more = True
        while more:
            page = doc.new_page(width=mediabox.width, height=mediabox.height)
            more, filled = story.place(where)
            story.draw(page)
    
    # Save PDF
    doc.save(output_file)
    doc.close()
    print(f"✅ Created: {output_file}")

# Generate bathroom remodel PDF
md_file = Path('/Users/moltbot/clawd/projects/ungouge-app/content/blog/bathroom-remodel-cost-breakdown.md')
output_file = Path('/Users/moltbot/clawd/projects/ungouge-app/output/branded-pdf-proof/bathroom-remodel-cost-breakdown-branded.pdf')
output_file.parent.mkdir(parents=True, exist_ok=True)

print("🎨 Generating branded PDF proof of concept...\n")
markdown_to_branded_pdf(md_file, output_file)
print(f"\n✅ Proof of concept ready: {output_file.name}")
