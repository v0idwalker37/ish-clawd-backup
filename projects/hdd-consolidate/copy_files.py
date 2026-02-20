#!/usr/bin/env python3
"""
HDD Consolidation - Copy phase
Deduplicates by hash, converts images to JPG, preserves folder structure
"""

import sqlite3
import shutil
import os
import time
from pathlib import Path
from collections import defaultdict

# Configuration
DB_PATH = Path(__file__).parent / 'index.db'
DEST_ROOT = Path('/media/ungouge/Blackhole01')
LOG_PATH = Path(__file__).parent / 'copy_progress.log'

# Image formats to convert to JPG
CONVERT_FORMATS = {'.cr2', '.psd', '.tiff', '.tif', '.raw', '.heic', '.heif', '.dng', '.nef', '.arw'}

def log(msg):
    """Log to both console and file"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')

def get_relative_path(path, source_drive):
    """Get path relative to source drive mount point"""
    # Remove drive mount point prefix
    if source_drive == 'Number_2':
        base = '/media/ungouge/Number_2'
    elif source_drive == 'BOH2':
        base = '/media/ungouge/BOH 2'
    else:
        return Path(path).name
    
    return Path(path).relative_to(base)

def convert_to_jpg(src_path, dest_path):
    """Convert image to JPG using PIL or rawpy"""
    try:
        from PIL import Image
        import rawpy
        
        # Try rawpy for RAW formats
        if src_path.suffix.lower() in {'.cr2', '.raw', '.dng', '.nef', '.arw'}:
            with rawpy.imread(str(src_path)) as raw:
                rgb = raw.postprocess()
                img = Image.fromarray(rgb)
        else:
            # Standard PIL formats
            img = Image.open(src_path)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Save as JPG at 100% quality
        img.save(dest_path, 'JPEG', quality=100, optimize=False)
        return True
        
    except Exception as e:
        log(f"  Conversion failed: {e}")
        return False

def copy_file(src, dest):
    """Copy file with metadata preservation"""
    try:
        # Create parent directory if needed
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(str(src), str(dest))
        return True
        
    except Exception as e:
        log(f"  Copy failed: {e}")
        return False

def main():
    log("=== Starting HDD Copy & Dedup Phase ===")
    
    if not DEST_ROOT.exists():
        log(f"ERROR: Destination drive not mounted at {DEST_ROOT}")
        return 1
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get all files grouped by hash
    log("Building deduplication map...")
    c.execute("""
        SELECT hash, path, source_drive 
        FROM files 
        WHERE hash IS NOT NULL AND hash != 'ERROR'
        ORDER BY hash, path
    """)
    
    hash_groups = defaultdict(list)
    for file_hash, path, source_drive in c.fetchall():
        hash_groups[file_hash].append((path, source_drive))
    
    total_files = sum(len(group) for group in hash_groups.values())
    unique_files = len(hash_groups)
    duplicates = total_files - unique_files
    
    log(f"Total files: {total_files:,}")
    log(f"Unique files: {unique_files:,}")
    log(f"Duplicates: {duplicates:,} ({duplicates/total_files*100:.1f}%)")
    log("")
    
    # Process each unique file
    copied = 0
    converted = 0
    skipped = 0
    errors = 0
    
    for idx, (file_hash, paths) in enumerate(hash_groups.items(), 1):
        if idx % 100 == 0:
            progress = (idx / unique_files) * 100
            log(f"Progress: {progress:.1f}% ({idx:,}/{unique_files:,}) - Copied: {copied:,}, Converted: {converted:,}, Errors: {errors}")
        
        # Use first file in group (arbitrary choice for duplicates)
        src_path, source_drive = paths[0]
        src = Path(src_path)
        
        if not src.exists():
            log(f"  SKIP (missing): {src}")
            skipped += 1
            continue
        
        # Build destination path (preserve folder structure)
        rel_path = get_relative_path(src_path, source_drive)
        dest = DEST_ROOT / rel_path
        
        # Check for path collision (different hash, same path)
        if dest.exists():
            # Move to conflicts folder
            conflict_dest = DEST_ROOT / '__CONFLICTS' / source_drive / rel_path
            dest = conflict_dest
        
        # Copy original file
        if copy_file(src, dest):
            copied += 1
        else:
            errors += 1
            continue
        
        # Convert to JPG if applicable
        if src.suffix.lower() in CONVERT_FORMATS:
            jpg_dest = dest.with_suffix('.jpg')
            if jpg_dest.exists():
                jpg_dest = dest.with_stem(dest.stem + '__converted').with_suffix('.jpg')
            
            if convert_to_jpg(src, jpg_dest):
                converted += 1
                log(f"  Converted: {src.name} → {jpg_dest.name}")
    
    conn.close()
    
    log("")
    log("=== Copy Complete ===")
    log(f"Unique files copied: {copied:,}")
    log(f"Images converted to JPG: {converted:,}")
    log(f"Skipped (missing): {skipped:,}")
    log(f"Errors: {errors}")
    log(f"Space saved from dedup: {duplicates:,} files not copied")

if __name__ == '__main__':
    main()
