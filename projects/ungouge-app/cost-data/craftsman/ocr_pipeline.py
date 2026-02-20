#!/usr/bin/env python3
"""
Craftsman National Repair & Remodeling Estimator — OCR Pipeline
================================================================
Phase 1: Convert PDF pages → PNG images (rotated correctly)
Phase 2: OCR each page → text files
Phase 3: Concatenate into full text

Designed for the scanned 444-page Craftsman book.
Uses PyMuPDF for PDF rendering + Tesseract for OCR.
"""

import os
import sys
import time
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────
PDF_PATH = Path("/home/ungouge/Downloads/Craftsman National repair and remodeling estimator.pdf")
OUT_DIR = Path("/home/ungouge/clawd/projects/ungouge-app/cost-data/craftsman")
PAGES_DIR = OUT_DIR / "pages"
OCR_DIR = OUT_DIR / "ocr_text"
FULL_TEXT = OUT_DIR / "craftsman_full_text.txt"
LOG_PATH = OUT_DIR / "ocr_pipeline.log"

DPI = 300  # OCR quality
PRINT_EVERY = 20


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


def render_and_ocr():
    log(f"Opening PDF: {PDF_PATH} ({PDF_PATH.stat().st_size / 1e6:.1f} MB)")
    doc = fitz.open(PDF_PATH)
    total_pages = len(doc)
    log(f"Total pages: {total_pages}")

    # Check for already-processed pages (resume support)
    already_done = set()
    for f in OCR_DIR.iterdir():
        if f.suffix == ".txt" and f.stem.startswith("page_"):
            already_done.add(int(f.stem.split("_")[1]))

    if already_done:
        log(f"Resuming — {len(already_done)} pages already OCR'd")

    start = time.time()
    pages_done = 0
    full_text_parts = []

    for page_num in range(total_pages):
        page_idx = page_num + 1  # 1-indexed for filenames
        png_path = PAGES_DIR / f"page_{page_idx:04d}.png"
        txt_path = OCR_DIR / f"page_{page_idx:04d}.txt"

        if page_idx in already_done and txt_path.exists():
            # Already processed — just load text for full concat
            full_text_parts.append(txt_path.read_text(encoding="utf-8", errors="replace"))
            pages_done += 1
            continue

        # Render page to image at DPI
        page = doc[page_num]
        # The PDF has rotation=180, PyMuPDF handles this automatically
        mat = fitz.Matrix(DPI / 72, DPI / 72)
        pix = page.get_pixmap(matrix=mat)

        # Save PNG
        pix.save(str(png_path))

        # OCR with Tesseract
        img = Image.open(str(png_path))
        try:
            text = pytesseract.image_to_string(img, lang="eng")
        except Exception as e:
            text = f"[OCR ERROR on page {page_idx}: {e}]"
            log(f"  OCR error on page {page_idx}: {e}")

        txt_path.write_text(text, encoding="utf-8")
        full_text_parts.append(text)
        pages_done += 1

        if pages_done % PRINT_EVERY == 0:
            elapsed = time.time() - start
            rate = pages_done / elapsed if elapsed > 0 else 0
            remaining = total_pages - pages_done
            eta = remaining / rate if rate > 0 else 0
            log(f"  Page {page_idx}/{total_pages} "
                f"({pages_done} done, {rate:.1f} pg/s, ETA {eta/60:.0f} min)")

    # Write concatenated full text
    FULL_TEXT.write_text(
        "\n\n".join(f"=== PAGE {i+1} ===\n{t}" for i, t in enumerate(full_text_parts)),
        encoding="utf-8",
    )

    elapsed = time.time() - start
    text_size = FULL_TEXT.stat().st_size
    log(f"✓ OCR complete: {total_pages} pages in {elapsed/60:.1f} min")
    log(f"  Full text: {text_size/1024:.0f} KB → {FULL_TEXT}")
    log(f"  Pages: {PAGES_DIR}")
    log(f"  OCR text: {OCR_DIR}")

    doc.close()


def main():
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    OCR_DIR.mkdir(parents=True, exist_ok=True)
    log("=" * 60)
    log("Craftsman Estimator — OCR Pipeline")
    log("=" * 60)
    render_and_ocr()
    log("Pipeline finished.")


if __name__ == "__main__":
    main()
