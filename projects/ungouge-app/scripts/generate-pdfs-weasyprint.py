#!/usr/bin/env python3
"""Generate REAL PDFs using WeasyPrint"""
from pathlib import Path
import markdown
from weasyprint import HTML

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
    
    # Styled HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: letter; margin: 1in; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{ color: #059669; border-bottom: 3px solid #059669; padding-bottom: 10px; }}
            h2 {{ color: #047857; margin-top: 30px; }}
            h3 {{ color: #065f46; }}
            code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
            pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #059669; color: white; }}
            blockquote {{ border-left: 4px solid #059669; margin-left: 0; padding-left: 20px; color: #666; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Generate PDF
    pdf_file = output_dir / f"{md_file.stem}.pdf"
    
    try:
        HTML(string=full_html).write_pdf(str(pdf_file))
        print(f"✓ {pdf_file.name}")
    except Exception as e:
        print(f"✗ Failed: {md_file.name} - {e}")

print(f"\n✅ Done! PDFs in: {output_dir}")
