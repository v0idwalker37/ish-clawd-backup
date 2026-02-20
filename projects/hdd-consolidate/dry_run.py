#!/usr/bin/env python3
"""
HDD Consolidation — Dry Run Scanner
====================================
Phase 1 (fast): Walk source drives, collect file sizes, estimate dedup.
Phase 2 (thorough): Hash files with duplicate sizes for accurate dedup.

Outputs a JSON manifest + human-readable summary.
"""

import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────
SOURCE_DRIVES = [
    ("/media/ungouge/Number_2", "Number_2"),
    ("/media/ungouge/BOH 2", "BOH2"),
]
DEST_DRIVE = "/media/ungouge/Blackhole01"
PROJECT_DIR = "/home/ungouge/clawd/projects/hdd-consolidate"
MANIFEST_PATH = os.path.join(PROJECT_DIR, "manifest.json")
REPORT_PATH = os.path.join(PROJECT_DIR, "dry_run_report.txt")
PROGRESS_PATH = os.path.join(PROJECT_DIR, "progress.json")

# Image types that will get a JPG conversion copy (original also kept)
CONVERT_EXTENSIONS = {
    '.cr2', '.cr3', '.nef', '.arw', '.orf', '.rw2', '.dng',  # Camera RAW
    '.psd',                                                     # Photoshop
    '.tiff', '.tif',                                            # TIFF
    '.heic', '.heif',                                           # Apple HEIC
    '.raw',                                                     # Generic RAW
}

# ── Helpers ────────────────────────────────────────────────────────────────

def human_size(nbytes):
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if abs(nbytes) < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} PB"


def hash_file(path, chunk_size=1 << 16):
    """SHA-256 of file content. Returns None on error."""
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, OSError):
        return None


def save_progress(data):
    with open(PROGRESS_PATH, 'w') as f:
        json.dump(data, f)


# ── Phase 1: Fast scan (stat only) ────────────────────────────────────────

def scan_drives():
    """Walk source drives, collect path + size + extension. No hashing."""
    all_files = []
    errors = []
    for mount, label in SOURCE_DRIVES:
        print(f"\n📂 Scanning {label} ({mount}) ...")
        drive_count = 0
        drive_size = 0
        for root, _dirs, filenames in os.walk(mount):
            for fname in filenames:
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, mount)
                try:
                    st = os.stat(full)
                    ext = os.path.splitext(fname)[1].lower()
                    all_files.append({
                        'full_path': full,
                        'rel_path': rel,
                        'drive': label,
                        'size': st.st_size,
                        'ext': ext,
                    })
                    drive_count += 1
                    drive_size += st.st_size
                    if drive_count % 50000 == 0:
                        print(f"   ... {drive_count:,} files ({human_size(drive_size)})")
                except (PermissionError, OSError) as e:
                    errors.append({'path': full, 'error': str(e)})
        print(f"   ✓ {label}: {drive_count:,} files, {human_size(drive_size)}")
    return all_files, errors


# ── Phase 2: Hash duplicates ──────────────────────────────────────────────

def hash_for_dedup(all_files):
    """
    Group by file size. For size groups with >1 file, compute SHA-256.
    Files with unique sizes are guaranteed unique (no hash needed for dedup
    but we still assign a pseudo-hash based on size for tracking).
    """
    by_size = defaultdict(list)
    for f in all_files:
        by_size[f['size']].append(f)

    unique_sizes = 0
    need_hash = 0
    for size, group in by_size.items():
        if len(group) == 1:
            unique_sizes += 1
            group[0]['hash'] = f"unique_size_{size}"
        else:
            need_hash += len(group)

    print(f"\n🔑 Hashing phase:")
    print(f"   {unique_sizes:,} files have unique sizes (no hash needed)")
    print(f"   {need_hash:,} files need SHA-256 (shared sizes)")

    hashed = 0
    hash_errors = 0
    start = time.time()
    total_to_hash = need_hash

    for size, group in by_size.items():
        if len(group) <= 1:
            continue
        for f in group:
            h = hash_file(f['full_path'])
            if h:
                f['hash'] = h
            else:
                f['hash'] = f"error_{f['full_path']}"
                hash_errors += 1
            hashed += 1
            if hashed % 5000 == 0:
                elapsed = time.time() - start
                rate = hashed / elapsed if elapsed > 0 else 0
                eta = (total_to_hash - hashed) / rate if rate > 0 else 0
                print(f"   ... hashed {hashed:,}/{total_to_hash:,} "
                      f"({rate:.0f}/s, ETA {eta/60:.0f}min)")
                save_progress({
                    'phase': 'hashing',
                    'hashed': hashed,
                    'total': total_to_hash,
                    'errors': hash_errors,
                    'elapsed_s': elapsed,
                })

    elapsed = time.time() - start
    print(f"   ✓ Hashed {hashed:,} files in {elapsed/60:.1f} min "
          f"({hash_errors} errors)")
    return all_files


# ── Dedup analysis ────────────────────────────────────────────────────────

def analyze_dedup(all_files):
    """Build unique file set and calculate stats."""
    by_hash = defaultdict(list)
    for f in all_files:
        by_hash[f.get('hash', f['full_path'])].append(f)

    unique_files = []
    total_dupes = 0
    dupe_space_saved = 0

    for h, group in by_hash.items():
        # Keep the first occurrence
        unique_files.append(group[0])
        if len(group) > 1:
            total_dupes += len(group) - 1
            dupe_space_saved += sum(f['size'] for f in group[1:])

    # Calculate conversion overhead (JPG copies of convertible images)
    convert_count = 0
    convert_est_size = 0
    for f in unique_files:
        if f['ext'] in CONVERT_EXTENSIONS:
            convert_count += 1
            # Rough estimate: JPG at 100% quality ≈ 30-50% of RAW size
            # PSD/TIFF can vary. Conservative estimate: 40% of original.
            convert_est_size += int(f['size'] * 0.4)

    unique_total_size = sum(f['size'] for f in unique_files)
    final_est_size = unique_total_size + convert_est_size

    # Extension breakdown
    ext_stats = defaultdict(lambda: {'count': 0, 'size': 0})
    for f in unique_files:
        ext = f['ext'] if f['ext'] else '(no ext)'
        ext_stats[ext]['count'] += 1
        ext_stats[ext]['size'] += f['size']

    return {
        'unique_files': unique_files,
        'total_files_scanned': len(all_files),
        'unique_file_count': len(unique_files),
        'duplicate_count': total_dupes,
        'duplicate_space_saved': dupe_space_saved,
        'unique_total_size': unique_total_size,
        'convert_count': convert_count,
        'convert_est_size': convert_est_size,
        'final_est_size': final_est_size,
        'ext_stats': dict(ext_stats),
    }


# ── Report ────────────────────────────────────────────────────────────────

def generate_report(stats, errors, dest_free):
    lines = []
    lines.append("=" * 65)
    lines.append("  HDD CONSOLIDATION — DRY RUN REPORT")
    lines.append(f"  Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 65)
    lines.append("")

    lines.append("📊 SUMMARY")
    lines.append(f"  Total files scanned:     {stats['total_files_scanned']:>12,}")
    lines.append(f"  Unique files:            {stats['unique_file_count']:>12,}")
    lines.append(f"  Duplicates removed:      {stats['duplicate_count']:>12,}")
    lines.append(f"  Space saved by dedup:    {human_size(stats['duplicate_space_saved']):>12}")
    lines.append("")

    lines.append("💾 SIZE ESTIMATES")
    lines.append(f"  Unique files total:      {human_size(stats['unique_total_size']):>12}")
    lines.append(f"  + JPG conversions (~):   {human_size(stats['convert_est_size']):>12}  ({stats['convert_count']:,} files)")
    lines.append(f"  ─────────────────────────────────")
    lines.append(f"  Estimated final size:    {human_size(stats['final_est_size']):>12}")
    lines.append(f"  Blackhole01 free space:  {human_size(dest_free):>12}")
    fits = stats['final_est_size'] < dest_free
    lines.append(f"  Will it fit?             {'✅ YES' if fits else '❌ NO — WILL NOT FIT'}")
    if not fits:
        over = stats['final_est_size'] - dest_free
        lines.append(f"  Overage:                 {human_size(over)}")
    lines.append("")

    lines.append("🖼️  IMAGE CONVERSIONS NEEDED")
    convert_exts = defaultdict(int)
    for f in stats['unique_files']:
        if f['ext'] in CONVERT_EXTENSIONS:
            convert_exts[f['ext']] += 1
    for ext, count in sorted(convert_exts.items(), key=lambda x: -x[1]):
        lines.append(f"  {ext:>8}  →  .jpg   ({count:,} files)")
    lines.append("")

    lines.append("📁 TOP 20 FILE TYPES (by count, unique only)")
    sorted_exts = sorted(stats['ext_stats'].items(),
                         key=lambda x: -x[1]['count'])[:20]
    for ext, info in sorted_exts:
        lines.append(f"  {ext:>10}: {info['count']:>10,} files  "
                      f"({human_size(info['size'])})")
    lines.append("")

    lines.append("📁 TOP 20 FILE TYPES (by size, unique only)")
    sorted_exts_size = sorted(stats['ext_stats'].items(),
                              key=lambda x: -x[1]['size'])[:20]
    for ext, info in sorted_exts_size:
        lines.append(f"  {ext:>10}: {human_size(info['size']):>10}  "
                      f"({info['count']:,} files)")
    lines.append("")

    if errors:
        lines.append(f"⚠️  ERRORS ({len(errors)} files could not be read)")
        for e in errors[:20]:
            lines.append(f"  {e['path']}: {e['error']}")
        if len(errors) > 20:
            lines.append(f"  ... and {len(errors) - 20} more")
    lines.append("")

    lines.append("📋 PER-DRIVE BREAKDOWN")
    for mount, label in SOURCE_DRIVES:
        drive_files = [f for f in stats['unique_files'] if f['drive'] == label]
        drive_unique_from = len(drive_files)
        all_from_drive = stats.get('_per_drive', {}).get(label, {})
        lines.append(f"  {label}:")
        lines.append(f"    Unique files sourced: {drive_unique_from:,}")
    lines.append("")

    lines.append("=" * 65)
    lines.append("  Ready to proceed? Run the copy script when confirmed.")
    lines.append("=" * 65)

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    print("🔍 HDD Consolidation — Dry Run")
    print(f"   Sources: {', '.join(l for _, l in SOURCE_DRIVES)}")
    print(f"   Destination: {DEST_DRIVE}")
    print()

    # Check drives are mounted
    for mount, label in SOURCE_DRIVES:
        if not os.path.ismount(mount):
            print(f"❌ {label} not mounted at {mount}")
            sys.exit(1)
    if not os.path.ismount(DEST_DRIVE):
        print(f"❌ Destination not mounted at {DEST_DRIVE}")
        sys.exit(1)

    dest_stat = os.statvfs(DEST_DRIVE)
    dest_free = dest_stat.f_bavail * dest_stat.f_frsize

    # Phase 1: Scan
    t0 = time.time()
    all_files, errors = scan_drives()
    scan_time = time.time() - t0
    print(f"\n⏱️  Scan completed in {scan_time/60:.1f} min")
    print(f"   Total: {len(all_files):,} files across {len(SOURCE_DRIVES)} drives")

    save_progress({
        'phase': 'scan_complete',
        'total_files': len(all_files),
        'errors': len(errors),
        'scan_time_s': scan_time,
    })

    # Phase 2: Hash for dedup
    t1 = time.time()
    all_files = hash_for_dedup(all_files)
    hash_time = time.time() - t1
    print(f"⏱️  Hashing completed in {hash_time/60:.1f} min")

    # Analyze
    stats = analyze_dedup(all_files)

    # Generate report
    report = generate_report(stats, errors, dest_free)
    print("\n" + report)

    # Save report
    with open(REPORT_PATH, 'w') as f:
        f.write(report)
    print(f"\n📄 Report saved to: {REPORT_PATH}")

    # Save manifest (unique files list for copy phase)
    manifest = {
        'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'stats': {
            'total_scanned': stats['total_files_scanned'],
            'unique_count': stats['unique_file_count'],
            'duplicate_count': stats['duplicate_count'],
            'unique_size': stats['unique_total_size'],
            'convert_count': stats['convert_count'],
            'estimated_final_size': stats['final_est_size'],
            'dest_free': dest_free,
            'fits': stats['final_est_size'] < dest_free,
        },
        'unique_files': [
            {
                'full_path': f['full_path'],
                'rel_path': f['rel_path'],
                'drive': f['drive'],
                'size': f['size'],
                'ext': f['ext'],
                'hash': f.get('hash', ''),
                'needs_convert': f['ext'] in CONVERT_EXTENSIONS,
            }
            for f in stats['unique_files']
        ],
        'errors': errors,
    }
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"📋 Manifest saved to: {MANIFEST_PATH}")
    print(f"\n✅ Dry run complete. Total time: {(time.time() - t0)/60:.1f} min")


if __name__ == '__main__':
    main()
