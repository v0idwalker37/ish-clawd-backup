#!/usr/bin/env python3
"""
Drive Deduplication Tool
Scans multiple drives, finds exact duplicates by content hash,
generates a report, and optionally consolidates to a single structure.

Usage:
  # Step 1: Scan and report (safe, read-only)
  python3 dedup.py scan /mnt/drive1 /mnt/drive2 /mnt/drive3

  # Step 2: Review the report
  cat dedup_report.txt

  # Step 3: Consolidate (moves unique files to output dir)
  python3 dedup.py consolidate /mnt/output --report dedup_report.json

Author: Ish for Jason | 2026-02-13
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Fast hash: read first 64KB + last 64KB + filesize for quick matching
# Full hash: SHA-256 of entire file for confirmation
QUICK_HASH_SIZE = 65536  # 64KB


def quick_hash(filepath):
    """Fast hash using file size + first/last 64KB chunks."""
    try:
        size = os.path.getsize(filepath)
        hasher = hashlib.md5()
        hasher.update(str(size).encode())

        with open(filepath, 'rb') as f:
            hasher.update(f.read(QUICK_HASH_SIZE))
            if size > QUICK_HASH_SIZE * 2:
                f.seek(-QUICK_HASH_SIZE, 2)
                hasher.update(f.read(QUICK_HASH_SIZE))

        return hasher.hexdigest()
    except (OSError, PermissionError) as e:
        print(f"  ⚠ Skipping {filepath}: {e}", file=sys.stderr)
        return None


def full_hash(filepath):
    """Full SHA-256 hash of entire file."""
    try:
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(8192 * 1024)  # 8MB chunks
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, PermissionError) as e:
        print(f"  ⚠ Skipping {filepath}: {e}", file=sys.stderr)
        return None


def scan_drives(drive_paths, min_size=1024):
    """
    Scan drives and find duplicates.
    Phase 1: Group by file size (instant)
    Phase 2: Quick hash size-matched files (fast)
    Phase 3: Full hash quick-hash-matched files (thorough)
    """
    print(f"\n{'='*60}")
    print(f"  DRIVE DEDUPLICATION SCANNER")
    print(f"  Drives: {', '.join(drive_paths)}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Phase 1: Index all files by size
    print("📂 Phase 1: Indexing files by size...")
    size_groups = defaultdict(list)
    total_files = 0
    total_size = 0
    skipped = 0

    for drive in drive_paths:
        drive_files = 0
        for root, dirs, files in os.walk(drive):
            # Skip hidden dirs and system dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('$RECYCLE.BIN', 'System Volume Information', '.Trash')]

            for filename in files:
                if filename.startswith('.'):
                    continue

                filepath = os.path.join(root, filename)
                try:
                    size = os.path.getsize(filepath)
                    if size < min_size:  # Skip tiny files
                        skipped += 1
                        continue
                    size_groups[size].append(filepath)
                    total_files += 1
                    total_size += size
                    drive_files += 1
                except (OSError, PermissionError):
                    skipped += 1

        print(f"  ✅ {drive}: {drive_files:,} files indexed")

    print(f"\n  Total: {total_files:,} files, {total_size / (1024**3):.1f} GB")
    print(f"  Skipped: {skipped:,} (tiny/inaccessible)")

    # Filter to only groups with potential duplicates
    potential_dupes = {size: paths for size, paths in size_groups.items() if len(paths) > 1}
    files_to_hash = sum(len(paths) for paths in potential_dupes.values())
    print(f"  Potential duplicates (same size): {files_to_hash:,} files in {len(potential_dupes):,} groups")

    # Phase 2: Quick hash
    print(f"\n🔍 Phase 2: Quick hashing {files_to_hash:,} files...")
    quick_groups = defaultdict(list)
    hashed = 0

    for size, paths in potential_dupes.items():
        for filepath in paths:
            h = quick_hash(filepath)
            if h:
                quick_groups[(size, h)].append(filepath)
            hashed += 1
            if hashed % 5000 == 0:
                print(f"  ... {hashed:,}/{files_to_hash:,} quick-hashed")

    # Filter to confirmed quick-hash matches
    quick_dupes = {k: paths for k, paths in quick_groups.items() if len(paths) > 1}
    confirm_count = sum(len(paths) for paths in quick_dupes.values())
    print(f"  Quick-hash matches: {confirm_count:,} files in {len(quick_dupes):,} groups")

    # Phase 3: Full hash confirmation
    print(f"\n🔐 Phase 3: Full SHA-256 verification...")
    final_groups = defaultdict(list)
    verified = 0

    for key, paths in quick_dupes.items():
        for filepath in paths:
            h = full_hash(filepath)
            if h:
                final_groups[h].append(filepath)
            verified += 1
            if verified % 1000 == 0:
                print(f"  ... {verified:,}/{confirm_count:,} verified")

    # Final duplicate groups
    duplicates = {h: paths for h, paths in final_groups.items() if len(paths) > 1}

    # Calculate stats
    total_dupe_files = sum(len(paths) for paths in duplicates.values())
    unique_files = total_files - total_dupe_files + len(duplicates)
    wasted_space = sum(
        os.path.getsize(paths[0]) * (len(paths) - 1)
        for paths in duplicates.values()
        if os.path.exists(paths[0])
    )

    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  Total files scanned:    {total_files:,}")
    print(f"  Unique files:           {unique_files:,}")
    print(f"  Duplicate groups:       {len(duplicates):,}")
    print(f"  Total duplicate files:  {total_dupe_files:,}")
    print(f"  Wasted space:           {wasted_space / (1024**3):.2f} GB")
    print(f"{'='*60}\n")

    return duplicates, total_files, unique_files, wasted_space


def generate_report(duplicates, output_prefix="dedup_report"):
    """Generate human-readable and machine-readable reports."""

    # JSON report (for consolidation step)
    json_report = {
        "generated": datetime.now().isoformat(),
        "duplicate_groups": len(duplicates),
        "groups": {}
    }

    # Text report (for human review)
    with open(f"{output_prefix}.txt", 'w') as f:
        f.write(f"DEDUPLICATION REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duplicate groups: {len(duplicates)}\n")
        f.write(f"{'='*60}\n\n")

        for i, (hash_val, paths) in enumerate(sorted(duplicates.items()), 1):
            size = 0
            try:
                size = os.path.getsize(paths[0])
            except OSError:
                pass

            f.write(f"Group {i} — {len(paths)} copies, {size / (1024**2):.1f} MB each\n")
            f.write(f"  SHA-256: {hash_val}\n")
            f.write(f"  KEEP: {paths[0]}\n")
            for p in paths[1:]:
                f.write(f"  DUPE: {p}\n")
            f.write(f"\n")

            json_report["groups"][hash_val] = {
                "keep": paths[0],
                "duplicates": paths[1:],
                "size": size,
                "count": len(paths)
            }

    with open(f"{output_prefix}.json", 'w') as f:
        json.dump(json_report, f, indent=2)

    print(f"📄 Reports saved:")
    print(f"   {output_prefix}.txt  (human-readable)")
    print(f"   {output_prefix}.json (for consolidation)")


def consolidate(report_path, output_dir, dry_run=True):
    """
    Consolidate unique files into a single directory structure.
    Preserves the folder structure from the 'keep' path.
    """
    with open(report_path) as f:
        report = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    moved = 0
    errors = 0

    action = "Would move" if dry_run else "Moving"
    print(f"\n{'DRY RUN — ' if dry_run else ''}Consolidating to {output_dir}\n")

    # Collect all 'keep' files
    for hash_val, group in report["groups"].items():
        src = group["keep"]
        if not os.path.exists(src):
            print(f"  ⚠ Missing: {src}")
            errors += 1
            continue

        # Preserve relative path structure
        # Use the deepest meaningful directory structure
        parts = Path(src).parts
        # Skip drive mount point (e.g., /mnt/drive1)
        # Keep everything after the drive root
        try:
            # Find where the drive path ends
            rel_path = os.path.basename(src)
            for i, part in enumerate(parts):
                if part in ('mnt', 'media', 'Volumes'):
                    rel_path = os.path.join(*parts[i+2:])  # skip mount + drive name
                    break
        except Exception:
            rel_path = os.path.basename(src)

        dst = os.path.join(output_dir, rel_path)

        if dry_run:
            print(f"  {action}: {src} → {dst}")
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            try:
                import shutil
                shutil.copy2(src, dst)  # copy2 preserves metadata
                moved += 1
                if moved % 1000 == 0:
                    print(f"  ... {moved:,} files moved")
            except Exception as e:
                print(f"  ⚠ Error copying {src}: {e}")
                errors += 1

    print(f"\n{'Would move' if dry_run else 'Moved'}: {moved:,} files")
    if errors:
        print(f"Errors: {errors}")
    if dry_run:
        print(f"\nRun without --dry-run to execute.")


def main():
    parser = argparse.ArgumentParser(description="Drive Deduplication Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan drives and generate report")
    scan_parser.add_argument("drives", nargs="+", help="Drive paths to scan")
    scan_parser.add_argument("--min-size", type=int, default=1024, help="Min file size in bytes (default: 1KB)")
    scan_parser.add_argument("--output", default="dedup_report", help="Report output prefix")

    # Consolidate command
    cons_parser = subparsers.add_parser("consolidate", help="Consolidate unique files")
    cons_parser.add_argument("output_dir", help="Output directory for consolidated files")
    cons_parser.add_argument("--report", default="dedup_report.json", help="JSON report from scan step")
    cons_parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default)")
    cons_parser.add_argument("--execute", action="store_true", help="Actually move files")

    args = parser.parse_args()

    if args.command == "scan":
        duplicates, total, unique, wasted = scan_drives(args.drives, args.min_size)
        generate_report(duplicates, args.output)
    elif args.command == "consolidate":
        dry_run = not args.execute
        consolidate(args.report, args.output_dir, dry_run=dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
