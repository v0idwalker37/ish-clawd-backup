"""File organization and metadata storage."""

import os
import json
import logging
from datetime import datetime
from typing import Optional

from ..config import OUTPUT_DIR, METADATA_DIR
from ..models import QuoteFile

logger = logging.getLogger(__name__)


def get_output_dir(source_name: str, date: str = None) -> str:
    """Get the output directory for a source on a given date.
    
    Structure: data/quote_images_raw/YYYY-MM-DD/source/
    """
    if date is None:
        date = datetime.utcnow().strftime("%Y-%m-%d")
    path = os.path.join(OUTPUT_DIR, date, source_name)
    os.makedirs(path, exist_ok=True)
    return path


def save_file_with_metadata(filepath: str, quote_file: QuoteFile):
    """Save metadata JSON alongside a downloaded file."""
    meta_path = filepath.rsplit(".", 1)[0] + "_metadata.json"
    try:
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(quote_file.to_metadata_dict(), f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving metadata for {filepath}: {e}")


def get_next_filename(output_dir: str, prefix: str = "quote", extension: str = ".jpg") -> str:
    """Get the next sequential filename in a directory.
    
    Returns full path like: /path/to/dir/quote_001.jpg
    """
    existing = os.listdir(output_dir)
    max_num = 0
    for f in existing:
        if f.startswith(prefix + "_") and not f.endswith("_metadata.json"):
            try:
                num = int(f.split("_")[1].split(".")[0])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                pass
    
    next_num = max_num + 1
    filename = f"{prefix}_{next_num:04d}{extension}"
    return os.path.join(output_dir, filename)


def update_master_list(quote_file: QuoteFile):
    """Update the master collected_quotes.json file."""
    master_file = os.path.join(METADATA_DIR, "collected_quotes.json")
    os.makedirs(METADATA_DIR, exist_ok=True)
    
    existing = []
    if os.path.exists(master_file):
        try:
            with open(master_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = []
    
    existing.append(quote_file.to_dict())
    
    try:
        tmp = master_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        os.replace(tmp, master_file)
    except Exception as e:
        logger.error(f"Error updating master list: {e}")


def count_collected_files() -> int:
    """Count total files collected across all dates and sources."""
    count = 0
    if not os.path.exists(OUTPUT_DIR):
        return 0
    for date_dir in os.listdir(OUTPUT_DIR):
        date_path = os.path.join(OUTPUT_DIR, date_dir)
        if not os.path.isdir(date_path):
            continue
        for source_dir in os.listdir(date_path):
            source_path = os.path.join(date_path, source_dir)
            if not os.path.isdir(source_path):
                continue
            for f in os.listdir(source_path):
                if not f.endswith("_metadata.json"):
                    count += 1
    return count
