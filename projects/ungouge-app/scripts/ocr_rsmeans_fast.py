#!/usr/bin/env python3
"""
Fast parallel OCR of RSMeans pricing book using Tesseract + multiprocessing.
"""

import os
import sys
import subprocess
from multiprocessing import Pool, cpu_count
import time

PAGES_DIR = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/pages"
OUTPUT_DIR = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/ocr_text"
COMBINED_OUTPUT = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/rsmeans_full_text.txt"

def ocr_page(args):
    """OCR a single page using tesseract CLI (faster than pytesseract wrapper)."""
    page_file, output_dir = args
    page_num = int(page_file.split('_')[1].split('.')[0])
    img_path = os.path.join(PAGES_DIR, page_file)
    txt_base = os.path.join(output_dir, f"page_{page_num:03d}")
    
    # Check if already done
    if os.path.exists(txt_base + ".txt"):
        with open(txt_base + ".txt") as f:
            return (page_num, f.read())
    
    try:
        # Use tesseract CLI directly (faster)
        result = subprocess.run(
            ['tesseract', img_path, txt_base, '--psm', '6', '--oem', '3'],
            capture_output=True, text=True, timeout=30
        )
        with open(txt_base + ".txt") as f:
            text = f.read()
        return (page_num, text)
    except Exception as e:
        return (page_num, f"ERROR: {e}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    page_files = sorted([f for f in os.listdir(PAGES_DIR) if f.startswith('page_') and f.endswith('.png')])
    print(f"Found {len(page_files)} pages to OCR")
    
    # Use all available CPU cores
    num_workers = min(cpu_count(), 8)
    print(f"Using {num_workers} parallel workers")
    
    args = [(f, OUTPUT_DIR) for f in page_files]
    
    start = time.time()
    results = {}
    
    with Pool(num_workers) as pool:
        for i, (page_num, text) in enumerate(pool.imap_unordered(ocr_page, args)):
            results[page_num] = text
            if (i + 1) % 50 == 0:
                elapsed = time.time() - start
                rate = (i + 1) / elapsed
                remaining = (len(page_files) - i - 1) / rate
                print(f"  {i+1}/{len(page_files)} pages ({rate:.1f}/sec, ~{remaining:.0f}s remaining)")
    
    elapsed = time.time() - start
    print(f"\nOCR complete: {len(results)} pages in {elapsed:.1f}s ({len(results)/elapsed:.1f} pages/sec)")
    
    # Combine all text
    print(f"Writing combined file: {COMBINED_OUTPUT}")
    with open(COMBINED_OUTPUT, 'w') as f:
        for page_num in sorted(results.keys()):
            book_page = page_num - 14
            f.write(f"\n{'='*80}\n")
            f.write(f"PAGE {page_num} (Book page {book_page})\n")
            f.write(f"{'='*80}\n\n")
            f.write(results[page_num])
            f.write("\n")
    
    total_chars = sum(len(t) for t in results.values())
    print(f"Combined file: {total_chars:,} characters")

if __name__ == "__main__":
    main()
