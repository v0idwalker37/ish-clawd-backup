#!/usr/bin/env python3
"""
HDD Consolidation Script
Copies ONE unique file per hash from BOH2/Number_2 to Blackhole01
Maintains directory structure, logs all operations
NO DELETIONS from source drives
"""

import sqlite3
import shutil
import os
from pathlib import Path
from datetime import datetime

# Configuration
DB_PATH = 'index.db'
DEST_BASE = '/media/ungouge/Blackhole01'
SOURCE_DRIVES = ['BOH2', 'Number_2']
LOG_FILE = 'consolidation.log'
PROGRESS_FILE = 'consolidation_progress.log'

# Map database drive names to actual mount points
DRIVE_MOUNT_MAP = {
    'BOH2': '/media/ungouge/BOH 2',
    'Number_2': '/media/ungouge/Number_2'
}

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"[{timestamp}] {msg}"
    print(message)
    with open(LOG_FILE, 'a') as f:
        f.write(message + '\n')

def progress_log(msg):
    with open(PROGRESS_FILE, 'a') as f:
        f.write(msg + '\n')

def main():
    log("Starting HDD consolidation to Blackhole01")
    log(f"Source drives: {SOURCE_DRIVES}")
    log(f"Destination: {DEST_BASE}")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all unique hashes from source drives
    cursor.execute("""
        SELECT hash, COUNT(*) as file_count
        FROM files
        WHERE hash IS NOT NULL 
        AND drive IN ('BOH2', 'Number_2')
        GROUP BY hash
        ORDER BY hash
    """)
    
    unique_hashes = cursor.fetchall()
    total_hashes = len(unique_hashes)
    log(f"Found {total_hashes:,} unique files to consolidate")
    
    # Statistics
    copied_count = 0
    skipped_count = 0
    error_count = 0
    total_bytes = 0
    
    # Process each unique hash
    for idx, (hash_val, file_count) in enumerate(unique_hashes, 1):
        # Get all files with this hash from source drives
        cursor.execute("""
            SELECT drive, full_path, size
            FROM files
            WHERE hash = ?
            AND drive IN ('BOH2', 'Number_2')
            ORDER BY 
                CASE drive 
                    WHEN 'Number_2' THEN 1
                    WHEN 'BOH2' THEN 2
                END,
                LENGTH(full_path)
        """, (hash_val,))
        
        files = cursor.fetchall()
        if not files:
            continue
        
        # Pick first file (priority: Number_2 > BOH2, then shortest path)
        source_drive, source_path, file_size = files[0]
        
        # Build destination path maintaining structure
        # Remove actual mount path prefix, keep rest
        mount_path = DRIVE_MOUNT_MAP.get(source_drive)
        if not mount_path:
            log(f"ERROR: Unknown drive {source_drive}, skipping")
            continue
        
        # Remove mount path prefix to get relative path
        if not source_path.startswith(mount_path + '/'):
            log(f"ERROR: Path {source_path} doesn't start with {mount_path}, skipping")
            continue
        
        rel_path = source_path[len(mount_path) + 1:]  # +1 to remove leading /
        dest_path = os.path.join(DEST_BASE, rel_path)
        
        # Check if already copied
        if os.path.exists(dest_path):
            skipped_count += 1
            if idx % 1000 == 0:
                progress_log(f"Progress: {idx}/{total_hashes} ({idx*100//total_hashes}%) | Copied: {copied_count:,} | Skipped: {skipped_count:,} | Errors: {error_count}")
            continue
        
        # Create destination directory
        dest_dir = os.path.dirname(dest_path)
        try:
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            copied_count += 1
            total_bytes += file_size
            
            # Log every 100 files
            if copied_count % 100 == 0:
                log(f"Copied {copied_count:,}/{total_hashes:,} files ({total_bytes / (1024**3):.2f} GB)")
                progress_log(f"Progress: {idx}/{total_hashes} ({idx*100//total_hashes}%) | Copied: {copied_count:,} | Skipped: {skipped_count:,} | Errors: {error_count}")
            
        except Exception as e:
            error_count += 1
            log(f"ERROR copying {source_path}: {e}")
            continue
    
    # Final report
    log("="*70)
    log("CONSOLIDATION COMPLETE")
    log(f"Total unique files: {total_hashes:,}")
    log(f"Files copied: {copied_count:,}")
    log(f"Files skipped (already exist): {skipped_count:,}")
    log(f"Errors: {error_count}")
    log(f"Total data copied: {total_bytes / (1024**3):.2f} GB")
    log("="*70)
    
    # Verify destination
    log("Verifying Blackhole01 file count...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM files 
        WHERE drive = 'Blackhole01'
    """)
    blackhole_count = cursor.fetchone()[0]
    log(f"Files in Blackhole01 database: {blackhole_count:,}")
    
    conn.close()

if __name__ == '__main__':
    main()
