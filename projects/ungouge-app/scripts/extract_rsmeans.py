#!/usr/bin/env python3
"""
RSMeans Contractor's Pricing Guide: Residential Repair & Remodeling
Comprehensive OCR extraction using Tesseract TSV output.

Extracts tabular pricing data from scanned page images and outputs structured JSON.
"""

import os
import sys
import json
import re
import csv
import io
import subprocess
from datetime import date
from collections import defaultdict


def log(msg):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()


# Configuration
PAGES_DIR = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/pages"
OUTPUT_JSON = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/rsmeans_extracted_data.json"
TESSERACT_BIN = "/usr/local/bin/tesseract"

# Column boundaries (from TSV `left` positions, calibrated from sample pages)
COL_ITEM_MAX = 660
COL_UNIT_MIN = 660
COL_UNIT_MAX = 745
COL_MATERIAL_MIN = 745
COL_MATERIAL_MAX = 870
COL_LABOR_MIN = 870
COL_LABOR_MAX = 980
COL_EQUIP_MIN = 980
COL_EQUIP_MAX = 1110
COL_TOTAL_MIN = 1110
COL_TOTAL_MAX = 1220
COL_SPEC_MIN = 1220

# Known section headers
KNOWN_SECTIONS = [
    "Job Costs",
    "Foundation",
    "Rough Frame / Structure",
    "Rough Frame/Structure",
    "Exterior Trim",
    "Roofing",
    "Siding",
    "Doors",
    "Windows",
    "Finish Carpentry / Trimwork",
    "Finish Carpentry/Trimwork",
    "Cabinets and Countertops",
    "Cabinets & Countertops",
    "Insulation",
    "Walls / Ceilings",
    "Walls/Ceilings",
    "Finish Flooring",
    "Rough Mechanical",
    "Rough Electrical",
    "Finish Mechanical",
    "Finish Electrical",
    "Improvements / Appliances / Treatments",
    "Improvements/Appliances/Treatments",
    "Location Factors",
]

UNIT_CORRECTIONS = {
    "SF": "S.F.", "SF.": "S.F.", "SE": "S.F.", "SE.": "S.F.",
    "S.E": "S.F.", "S.E.": "S.F.",
    "LF": "L.F.", "LF.": "L.F.", "LE": "L.F.", "LE.": "L.F.",
    "L.E": "L.F.", "L.E.": "L.F.",
    "Sq": "Sq.", "Sq,": "Sq.",
    "Ea": "Ea.", "Ea,": "Ea.",
    "VLF": "V.L.F.", "V.LE.": "V.L.F.",
}


def run_tesseract_tsv(image_path):
    """Run Tesseract OCR and return TSV output as list of dicts."""
    try:
        result = subprocess.run(
            [TESSERACT_BIN, image_path, "stdout", "--psm", "6",
             "-c", "tessedit_create_tsv=1", "tsv"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return []

        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:
            return []

        reader = csv.DictReader(io.StringIO(result.stdout), delimiter='\t')
        words = []
        for row in reader:
            try:
                word = {
                    'level': int(row.get('level', 0)),
                    'block_num': int(row.get('block_num', 0)),
                    'par_num': int(row.get('par_num', 0)),
                    'line_num': int(row.get('line_num', 0)),
                    'word_num': int(row.get('word_num', 0)),
                    'left': int(row.get('left', 0)),
                    'top': int(row.get('top', 0)),
                    'width': int(row.get('width', 0)),
                    'height': int(row.get('height', 0)),
                    'conf': float(row.get('conf', -1)),
                    'text': row.get('text', '').strip(),
                }
                words.append(word)
            except (ValueError, KeyError):
                continue
        return words
    except subprocess.TimeoutExpired:
        return []
    except Exception:
        return []


def classify_column(left):
    """Determine which column a word belongs to based on x-position."""
    if left < COL_ITEM_MAX:
        return 'item'
    elif COL_UNIT_MIN <= left < COL_UNIT_MAX:
        return 'unit'
    elif COL_MATERIAL_MIN <= left < COL_MATERIAL_MAX:
        return 'material'
    elif COL_LABOR_MIN <= left < COL_LABOR_MAX:
        return 'labor'
    elif COL_EQUIP_MIN <= left < COL_EQUIP_MAX:
        return 'equipment'
    elif COL_TOTAL_MIN <= left < COL_TOTAL_MAX:
        return 'total'
    elif left >= COL_SPEC_MIN:
        return 'specification'
    else:
        return 'unknown'


def group_words_into_lines(words):
    """Group words into lines based on their top position."""
    word_list = [w for w in words if w['level'] == 5 and w['text']]
    if not word_list:
        return []

    word_list.sort(key=lambda w: (w['top'], w['left']))

    lines = []
    current_line = [word_list[0]]
    for w in word_list[1:]:
        last_top = current_line[-1]['top']
        if abs(w['top'] - last_top) < 15:
            current_line.append(w)
        else:
            lines.append(current_line)
            current_line = [w]
    if current_line:
        lines.append(current_line)

    return lines


def parse_number(text):
    """Parse a number from OCR text. Returns float or None."""
    if not text:
        return None
    text = text.strip().replace('$', '').replace(',', '').replace('O', '0')
    text = text.replace('|', '')
    if text.endswith('.') and text.count('.') > 1:
        text = text[:-1]
    if text.startswith('.'):
        text = '0' + text
    # Handle common OCR: 'l' -> '1' only if the text looks numeric
    if re.match(r'^[\dl.,\-]+$', text):
        text = text.replace('l', '1')

    try:
        return float(text)
    except ValueError:
        cleaned = re.sub(r'[^\d.\-]', '', text)
        if cleaned:
            try:
                return float(cleaned)
            except ValueError:
                return None
    return None


def is_section_header(line_words):
    """Check if a line is likely a section header (top banner)."""
    if not line_words:
        return False, ""
    avg_top = sum(w['top'] for w in line_words) / len(line_words)
    if avg_top > 120:
        return False, ""

    text = ' '.join(w['text'] for w in line_words if w['conf'] > 30)
    text_lower = text.lower().strip()
    for section in KNOWN_SECTIONS:
        section_lower = section.lower()
        if section_lower in text_lower or text_lower in section_lower:
            return True, section
        first_words = section_lower.split()
        text_words = text_lower.split()
        if text_words and first_words and text_words[0] == first_words[0]:
            if len(text_words) == 1 and len(first_words) == 1:
                return True, section
            elif len(text_words) >= 2 and len(first_words) >= 2:
                if text_words[1] == first_words[1] or (len(text_words[1]) > 2 and text_words[1][:3] == first_words[1][:3]):
                    return True, section
    return False, ""


def is_subsection_header(line_words):
    """Check if a line is a subsection header (shaded bar with column headers)."""
    if not line_words:
        return False, ""

    left_words = [w for w in line_words if w['left'] < 500 and w['conf'] > 40]
    has_col_headers = any(
        w['text'] in ('Unit', 'Material', 'Labor', 'Equip.', 'Total', 'Specification', 'Lobor')
        for w in line_words
    )

    if left_words and has_col_headers:
        text = ' '.join(w['text'] for w in left_words
                       if w['text'] not in ('|', 'Unit', 'Material', 'Labor', 'Equip.', 'Total', 'Specification', 'Lobor'))
        text = text.strip()
        if text and len(text) > 1:
            return True, text

    return False, ""


def is_item_group_header(line_words):
    """Check if a line is an item group header (bold left-aligned text)."""
    if not line_words:
        return False, ""

    left_words = [w for w in line_words if w['left'] < COL_ITEM_MAX and w['conf'] > 30]
    right_words = [w for w in line_words if w['left'] >= COL_UNIT_MIN and w['text'] not in ('|', '', '-')]

    if left_words and not right_words:
        text = ' '.join(w['text'] for w in left_words if w['text'] not in ('|', ''))
        text = text.strip()
        if text and len(text) > 1 and not text.startswith('For customer') and not text.isdigit():
            avg_conf = sum(w['conf'] for w in left_words) / len(left_words)
            if avg_conf > 40:
                return True, text

    return False, ""


def parse_data_row(line_words):
    """Parse a data row into its column values."""
    row = {
        'item': '', 'unit': '',
        'material': None, 'labor': None,
        'equipment': None, 'total': None,
        'specification': '',
    }

    columns = defaultdict(list)
    for w in line_words:
        if w['text'] in ('|', '—', '——', '———', '', '-') or w['conf'] < 20:
            continue
        col = classify_column(w['left'])
        if col != 'unknown':
            columns[col].append(w)

    if 'item' in columns:
        row['item'] = ' '.join(w['text'] for w in sorted(columns['item'], key=lambda x: x['left']))

    if 'unit' in columns:
        unit_text = ' '.join(w['text'] for w in columns['unit']).strip()
        if unit_text in UNIT_CORRECTIONS:
            unit_text = UNIT_CORRECTIONS[unit_text]
        row['unit'] = unit_text

    for col_name in ('material', 'labor', 'equipment', 'total'):
        if col_name in columns:
            texts = [w['text'] for w in columns[col_name] if w['conf'] > 25]
            for t in texts:
                val = parse_number(t)
                if val is not None:
                    row[col_name] = val
                    break

    if 'specification' in columns:
        row['specification'] = ' '.join(
            w['text'] for w in sorted(columns['specification'], key=lambda x: x['left'])
            if w['conf'] > 30
        )

    return row


def has_pricing_data(row):
    """Check if a row has at least some pricing data."""
    return any(v is not None for v in [row['material'], row['labor'], row['equipment'], row['total']])


def extract_page(page_num, image_path):
    """Extract all data from a single page."""
    words = run_tesseract_tsv(image_path)
    if not words:
        return None

    text_words = [w for w in words if w['level'] == 5 and w['text'].strip() and w['conf'] > 20]
    if len(text_words) < 10:
        return None

    lines = group_words_into_lines(words)
    if not lines:
        return None

    result = {
        'page': page_num,
        'section': '',
        'subsections': [],
        'is_trade_labor': False,
        'is_location_factors': False,
    }

    current_section = ''
    current_subsection = ''
    current_item_group = ''
    current_items = []
    last_item = None

    for line in lines:
        good_words = [w for w in line if w['conf'] > 30 and w['text'].strip()]
        if not good_words:
            continue

        line_text = ' '.join(w['text'] for w in good_words)

        # Skip footer
        if 'customer support' in line_text.lower() or '800.874.2291' in line_text:
            continue

        # Check section header
        is_sec, sec_name = is_section_header(line)
        if is_sec:
            current_section = sec_name
            result['section'] = sec_name
            if 'location factor' in sec_name.lower():
                result['is_location_factors'] = True
            continue

        if result.get('is_location_factors'):
            continue

        # Check subsection header
        is_sub, sub_name = is_subsection_header(line)
        if is_sub:
            if current_subsection and current_items:
                result['subsections'].append({
                    'subsection': current_subsection,
                    'items': current_items
                })
            current_subsection = sub_name
            current_items = []
            current_item_group = ''
            if 'trade labor' in sub_name.lower():
                result['is_trade_labor'] = True
            continue

        # Check item group header
        is_group, group_name = is_item_group_header(line)
        if is_group:
            current_item_group = group_name
            continue

        # Parse data row
        row = parse_data_row(line)

        # Spec continuation
        if last_item and not row['item'] and not has_pricing_data(row) and row['specification']:
            last_item['specification'] += ' ' + row['specification']
            continue

        if row['item'] or has_pricing_data(row):
            item_name = row['item'].strip()

            if has_pricing_data(row):
                full_item = ''
                if current_item_group:
                    full_item = current_item_group + ' - ' + item_name if item_name else current_item_group
                else:
                    full_item = item_name

                item_entry = {
                    'item': full_item,
                    'unit': row['unit'],
                    'material': row['material'],
                    'labor': row['labor'],
                    'equipment': row['equipment'],
                    'total': row['total'],
                    'specification': row['specification'],
                }
                current_items.append(item_entry)
                last_item = item_entry
            elif item_name and not has_pricing_data(row):
                if len(item_name) > 2:
                    current_item_group = item_name
        elif row['specification'] and not row['item'] and not has_pricing_data(row):
            if last_item:
                last_item['specification'] += ' ' + row['specification']

    # Save last subsection
    if current_subsection and current_items:
        result['subsections'].append({
            'subsection': current_subsection,
            'items': current_items
        })
    elif current_items:
        result['subsections'].append({
            'subsection': current_item_group or 'General',
            'items': current_items
        })

    return result


def extract_trade_labor_rates(all_results):
    """Extract trade labor rates from Job Costs pages."""
    rates = {}
    current_trade = ''

    for result in all_results:
        if not result or not result.get('is_trade_labor'):
            continue

        for sub_data in result['subsections']:
            for item in sub_data['items']:
                item_lower = item['item'].lower()

                for trade in ['carpenter', 'drywaller', 'roofer', 'painter', 'mason',
                              'electrician', 'plumber', 'common laborer']:
                    if trade in item_lower:
                        current_trade = trade
                        break

                if not current_trade:
                    continue

                if current_trade not in rates:
                    rates[current_trade] = {}

                unit = item.get('unit', '').lower()
                labor = item.get('labor') or item.get('total')
                if not labor:
                    continue

                if 'minimum' in item_lower:
                    rates[current_trade]['minimum'] = labor
                elif unit in ('day',):
                    rates[current_trade]['daily'] = labor
                elif unit in ('week',):
                    rates[current_trade]['weekly'] = labor

    return rates


def main():
    log("=" * 70)
    log("RSMeans Contractor's Pricing Guide - Data Extraction")
    log("=" * 70)

    page_files = sorted([
        f for f in os.listdir(PAGES_DIR)
        if f.startswith('page_') and f.endswith('.png')
    ])
    log(f"Found {len(page_files)} page images")

    all_results = []
    stats = {
        'total_pages_processed': 0,
        'total_items_extracted': 0,
        'blank_pages_skipped': 0,
        'extraction_errors': 0,
        'pages_with_data': 0,
    }

    for i, page_file in enumerate(page_files):
        page_num = int(page_file.split('_')[1].split('.')[0])
        image_path = os.path.join(PAGES_DIR, page_file)

        if (i + 1) % 25 == 0 or i == 0:
            log(f"Processing page {page_num} ({i + 1}/{len(page_files)})...")

        try:
            result = extract_page(page_num, image_path)
            stats['total_pages_processed'] += 1

            if result is None:
                stats['blank_pages_skipped'] += 1
                all_results.append(None)
                continue

            page_items = sum(len(s['items']) for s in result['subsections'])
            if page_items > 0:
                stats['pages_with_data'] += 1
            stats['total_items_extracted'] += page_items
            all_results.append(result)

        except Exception as e:
            log(f"  ERROR on page {page_num}: {e}")
            stats['extraction_errors'] += 1
            all_results.append(None)

    log(f"\nProcessing complete. Building output...")

    # Organize into sections
    sections_output = []
    current_section = ''

    for result in all_results:
        if result is None:
            continue

        page_section = result.get('section', '')
        if page_section:
            current_section = page_section

        if result.get('is_location_factors'):
            continue

        for sub_data in result['subsections']:
            sections_output.append({
                'section': current_section or 'Unknown',
                'subsection': sub_data['subsection'],
                'page': result['page'],
                'items': sub_data['items'],
            })

    # Extract trade labor rates
    trade_rates = extract_trade_labor_rates(all_results)

    output = {
        'source': "RSMeans Contractor's Pricing Guide: Residential Repair & Remodeling",
        'extraction_date': str(date.today()),
        'sections': sections_output,
        'trade_labor_rates': trade_rates,
        'statistics': stats,
    }

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(output, f, indent=2)

    log(f"\nOutput saved to: {OUTPUT_JSON}")
    log(f"\nStatistics:")
    log(f"  Total pages processed: {stats['total_pages_processed']}")
    log(f"  Pages with data: {stats['pages_with_data']}")
    log(f"  Blank/divider pages skipped: {stats['blank_pages_skipped']}")
    log(f"  Total items extracted: {stats['total_items_extracted']}")
    log(f"  Extraction errors: {stats['extraction_errors']}")
    log(f"  Unique sections: {len(set(s['section'] for s in sections_output))}")
    log(f"  Trade labor rates found: {len(trade_rates)}")

    section_counts = defaultdict(int)
    for s in sections_output:
        section_counts[s['section']] += len(s['items'])
    log(f"\nItems per section:")
    for sec, count in sorted(section_counts.items(), key=lambda x: -x[1]):
        log(f"  {sec}: {count} items")

    return output


if __name__ == '__main__':
    main()
