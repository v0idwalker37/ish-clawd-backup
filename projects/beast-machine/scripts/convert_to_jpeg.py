#!/usr/bin/env python3
"""
Batch Image Converter — RAW/PSD/etc → JPEG
Converts camera RAW files, Photoshop files, and other image formats to JPEG.
Preserves originals in a separate folder (never deletes source files).

Supported formats:
  RAW:  .cr2, .cr3, .nef, .arw, .dng, .raf, .orf, .rw2, .pef, .srw
  Edit: .psd, .psb, .tif, .tiff, .bmp, .webp, .heic, .heif, .avif
  
Usage:
  # Convert all supported files in a directory (recursive)
  python3 convert_to_jpeg.py /mnt/drive1/Photos

  # Convert with custom quality and move originals
  python3 convert_to_jpeg.py /mnt/drive1/Photos --quality 90 --move-originals

  # Dry run (preview what would be converted)
  python3 convert_to_jpeg.py /mnt/drive1/Photos --dry-run

  # Convert only RAW files
  python3 convert_to_jpeg.py /mnt/drive1/Photos --types raw

Requirements:
  pip install Pillow rawpy imageio
  # For HEIC support: pip install pillow-heif
  # For PSD support: pip install psd-tools

Author: Ish for Jason | 2026-02-13
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Try importing optional dependencies
try:
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None  # Allow large images
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import rawpy
    HAS_RAWPY = True
except ImportError:
    HAS_RAWPY = False

try:
    from psd_tools import PSDImage
    HAS_PSD = True
except ImportError:
    HAS_PSD = False

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HAS_HEIF = True
except ImportError:
    HAS_HEIF = False


# File extension categories
RAW_EXTENSIONS = {'.cr2', '.cr3', '.nef', '.arw', '.dng', '.raf', '.orf', '.rw2', '.pef', '.srw', '.3fr', '.kdc', '.mrw'}
EDIT_EXTENSIONS = {'.psd', '.psb', '.tif', '.tiff', '.bmp', '.webp'}
HEIC_EXTENSIONS = {'.heic', '.heif', '.avif'}
ALL_EXTENSIONS = RAW_EXTENSIONS | EDIT_EXTENSIONS | HEIC_EXTENSIONS


def check_dependencies():
    """Check which conversion libraries are available."""
    print("📋 Dependency check:")
    print(f"  {'✅' if HAS_PIL else '❌'} Pillow (PIL) — core image processing")
    print(f"  {'✅' if HAS_RAWPY else '❌'} rawpy — camera RAW files (.cr2, .nef, .arw, etc.)")
    print(f"  {'✅' if HAS_PSD else '❌'} psd-tools — Photoshop files (.psd, .psb)")
    print(f"  {'✅' if HAS_HEIF else '❌'} pillow-heif — HEIC/HEIF files (.heic, .heif)")
    print()

    if not HAS_PIL:
        print("❌ Pillow is REQUIRED. Install: pip install Pillow")
        sys.exit(1)

    missing = []
    if not HAS_RAWPY:
        missing.append("rawpy (pip install rawpy) — needed for camera RAW files")
    if not HAS_PSD:
        missing.append("psd-tools (pip install psd-tools) — needed for .psd files")
    if not HAS_HEIF:
        missing.append("pillow-heif (pip install pillow-heif) — needed for .heic files")

    if missing:
        print("⚠ Optional dependencies missing:")
        for m in missing:
            print(f"    pip install {m.split('(')[1].split(')')[0].replace('pip install ', '')}")
        print()

    return True


def convert_raw_to_jpeg(src_path, dst_path, quality=85):
    """Convert camera RAW file to JPEG using rawpy."""
    if not HAS_RAWPY:
        return False, "rawpy not installed"

    try:
        with rawpy.imread(str(src_path)) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                output_bps=8,
                no_auto_bright=False,
            )
        img = Image.fromarray(rgb)
        img.save(dst_path, 'JPEG', quality=quality, optimize=True)
        return True, None
    except Exception as e:
        return False, str(e)


def convert_psd_to_jpeg(src_path, dst_path, quality=85):
    """Convert PSD/PSB file to JPEG using psd-tools."""
    if not HAS_PSD:
        return False, "psd-tools not installed"

    try:
        psd = PSDImage.open(str(src_path))
        img = psd.composite()
        if img.mode in ('RGBA', 'LA', 'P'):
            # Remove alpha channel for JPEG
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(dst_path, 'JPEG', quality=quality, optimize=True)
        return True, None
    except Exception as e:
        return False, str(e)


def convert_image_to_jpeg(src_path, dst_path, quality=85):
    """Convert standard image formats to JPEG using Pillow."""
    try:
        img = Image.open(str(src_path))
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Preserve EXIF data if available
        exif_data = img.info.get('exif', b'')
        save_kwargs = {'quality': quality, 'optimize': True}
        if exif_data:
            save_kwargs['exif'] = exif_data

        img.save(dst_path, 'JPEG', **save_kwargs)
        return True, None
    except Exception as e:
        return False, str(e)


def convert_file(src_path, dst_path, quality=85):
    """Route file to appropriate converter based on extension."""
    ext = src_path.suffix.lower()

    if ext in RAW_EXTENSIONS:
        return convert_raw_to_jpeg(src_path, dst_path, quality)
    elif ext in ('.psd', '.psb'):
        return convert_psd_to_jpeg(src_path, dst_path, quality)
    else:
        return convert_image_to_jpeg(src_path, dst_path, quality)


def scan_convertible_files(input_dir, types='all'):
    """Find all convertible files in directory tree."""
    if types == 'raw':
        extensions = RAW_EXTENSIONS
    elif types == 'edit':
        extensions = EDIT_EXTENSIONS
    elif types == 'heic':
        extensions = HEIC_EXTENSIONS
    else:
        extensions = ALL_EXTENSIONS

    files = []
    for root, dirs, filenames in os.walk(input_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for filename in filenames:
            if Path(filename).suffix.lower() in extensions:
                files.append(Path(root) / filename)

    return sorted(files)


def batch_convert(input_dir, quality=85, types='all', move_originals=False,
                  originals_dir=None, dry_run=False):
    """Convert all supported files in a directory tree."""

    print(f"\n{'='*60}")
    print(f"  BATCH IMAGE CONVERTER")
    print(f"  Input: {input_dir}")
    print(f"  Quality: {quality}%")
    print(f"  Types: {types}")
    print(f"  {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*60}\n")

    files = scan_convertible_files(input_dir, types)
    print(f"📸 Found {len(files):,} files to convert\n")

    if not files:
        print("Nothing to convert!")
        return

    # Summary by extension
    ext_counts = {}
    ext_sizes = {}
    for f in files:
        ext = f.suffix.lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        try:
            ext_sizes[ext] = ext_sizes.get(ext, 0) + f.stat().st_size
        except OSError:
            pass

    print("  Extension breakdown:")
    for ext, count in sorted(ext_counts.items(), key=lambda x: -x[1]):
        size_gb = ext_sizes.get(ext, 0) / (1024**3)
        print(f"    {ext:8s} {count:6,} files  ({size_gb:.1f} GB)")
    print()

    if dry_run:
        print("Dry run complete. Run without --dry-run to convert.")
        return

    # Set up originals directory
    if move_originals:
        if not originals_dir:
            originals_dir = os.path.join(input_dir, '_originals')
        os.makedirs(originals_dir, exist_ok=True)
        print(f"📁 Originals will be moved to: {originals_dir}\n")

    converted = 0
    skipped = 0
    errors = 0
    saved_bytes = 0

    for i, src in enumerate(files, 1):
        # Output path: same location, .jpg extension
        dst = src.with_suffix('.jpg')

        # Skip if JPEG already exists
        if dst.exists():
            skipped += 1
            continue

        success, error = convert_file(src, dst, quality)

        if success:
            converted += 1
            try:
                orig_size = src.stat().st_size
                new_size = dst.stat().st_size
                saved_bytes += (orig_size - new_size)
            except OSError:
                pass

            # Move original if requested
            if move_originals:
                rel_path = src.relative_to(input_dir)
                orig_dest = Path(originals_dir) / rel_path
                orig_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(orig_dest))

            if converted % 100 == 0:
                print(f"  ... {converted:,}/{len(files):,} converted")
        else:
            errors += 1
            if errors <= 20:  # Only show first 20 errors
                print(f"  ⚠ Failed: {src.name} — {error}")

    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  Converted:  {converted:,}")
    print(f"  Skipped:    {skipped:,} (JPEG already exists)")
    print(f"  Errors:     {errors:,}")
    print(f"  Space saved: {saved_bytes / (1024**3):.2f} GB")
    if move_originals:
        print(f"  Originals:  {originals_dir}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Batch Image Converter — RAW/PSD/etc → JPEG")
    parser.add_argument("input_dir", help="Directory to scan (recursive)")
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality 1-100 (default: 85)")
    parser.add_argument("--types", choices=['all', 'raw', 'edit', 'heic'], default='all',
                        help="File types to convert")
    parser.add_argument("--move-originals", action="store_true",
                        help="Move originals to _originals/ subfolder after conversion")
    parser.add_argument("--originals-dir", help="Custom directory for originals (with --move-originals)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't convert")

    args = parser.parse_args()

    check_dependencies()
    batch_convert(
        args.input_dir,
        quality=args.quality,
        types=args.types,
        move_originals=args.move_originals,
        originals_dir=args.originals_dir,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
