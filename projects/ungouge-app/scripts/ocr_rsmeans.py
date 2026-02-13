#!/usr/bin/env python3
"""
OCR RSMeans pricing book pages using Tesseract.
Extracts text from all pricing pages (15-294) and saves to text files.
"""

import os
import sys
import pytesseract
from PIL import Image
import json
from concurrent.futures import ProcessPoolExecutor, as_completed

PAGES_DIR = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/pages"
OUTPUT_DIR = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/ocr_text"
COMBINED_OUTPUT = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/rsmeans_full_text.txt"

def ocr_page(page_file):
    """OCR a single page image and return (page_num, text)."""
    page_num = int(page_file.split('_')[1].split('.')[0])
    img_path = os.path.join(PAGES_DIR, page_file)
    
    try:
        img = Image.open(img_path)
        # Use PSM 6 for uniform block of text (good for tables)
        text = pytesseract.image_to_string(img, config='--psm 6 --oem 3')
        return (page_num, text)
    except Exception as e:
        return (page_num, f"ERROR: {e}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get all page files
    page_files = sorted([f for f in os.listdir(PAGES_DIR) if f.startswith('page_') and f.endswith('.png')])
    print(f"Found {len(page_files)} pages to OCR")
    
    results = {}
    total = len(page_files)
    
    # Process pages (can't easily parallelize tesseract, but let's try)
    for i, page_file in enumerate(page_files):
        page_num, text = ocr_page(page_file)
        results[page_num] = text
        
        # Save individual page text
        txt_path = os.path.join(OUTPUT_DIR, f"page_{page_num:03d}.txt")
        with open(txt_path, 'w') as f:
            f.write(text)
        
        if (i + 1) % 20 == 0:
            print(f"  Processed {i+1}/{total} pages...")
    
    # Combine all text
    print(f"\nCombining all {len(results)} pages into {COMBINED_OUTPUT}")
    with open(COMBINED_OUTPUT, 'w') as f:
        for page_num in sorted(results.keys()):
            f.write(f"\n{'='*80}\n")
            f.write(f"PAGE {page_num} (Book page {page_num - 14})\n")
            f.write(f"{'='*80}\n\n")
            f.write(results[page_num])
            f.write("\n")
    
    total_chars = sum(len(t) for t in results.values())
    print(f"Done! {len(results)} pages, {total_chars:,} total characters")
    print(f"Combined file: {COMBINED_OUTPUT}")

if __name__ == "__main__":
    main()
