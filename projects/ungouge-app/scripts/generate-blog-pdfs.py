#!/usr/bin/env python3
"""
Generate PDFs from blog markdown files
"""
import os
import sys
import subprocess
from pathlib import Path
import markdown

def convert_md_to_pdf(md_file, output_dir):
    """Convert markdown file to PDF using HTML intermediate"""
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML
    html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
    
    # Wrap in styled HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{ 
                color: #059669; 
                border-bottom: 3px solid #059669;
                padding-bottom: 10px;
            }}
            h2 {{ 
                color: #047857; 
                margin-top: 30px;
            }}
            h3 {{ color: #065f46; }}
            code {{
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
            }}
            pre {{
                background: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #059669;
                color: white;
            }}
            blockquote {{
                border-left: 4px solid #059669;
                margin-left: 0;
                padding-left: 20px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Save HTML temporarily
    html_file = md_file.with_suffix('.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    # Generate PDF using macOS Safari/WebKit (via cupsfilter or textutil)
    pdf_file = output_dir / f"{md_file.stem}.pdf"
    
    # Try using wkhtmltopdf if available, otherwise use cupsfilter
    try:
        # Use cupsfilter (macOS built-in)
        subprocess.run([
            'cupsfilter',
            str(html_file),
            '-o', str(pdf_file)
        ], check=True, capture_output=True)
        print(f"✓ Generated: {pdf_file.name}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try textutil as backup
        try:
            subprocess.run([
                'textutil',
                '-convert', 'html',
                '-output', str(pdf_file),
                str(html_file)
            ], check=True)
            print(f"✓ Generated: {pdf_file.name}")
        except Exception as e:
            print(f"✗ Failed to generate {md_file.name}: {e}")
    
    # Cleanup HTML
    html_file.unlink()

def main():
    blog_dir = Path('/Users/moltbot/clawd/projects/ungouge-app/content/blog')
    output_dir = Path('/Users/moltbot/clawd/projects/ungouge-app/output/blog-pdfs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all markdown files
    md_files = sorted(blog_dir.glob('*.md'))
    
    print(f"Converting {len(md_files)} blog posts to PDF...\n")
    
    for md_file in md_files:
        convert_md_to_pdf(md_file, output_dir)
    
    print(f"\n✅ Done! PDFs saved to: {output_dir}")

if __name__ == '__main__':
    main()
