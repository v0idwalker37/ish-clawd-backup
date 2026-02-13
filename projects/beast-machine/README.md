# Beast Machine — i9 Utility Scripts

Scripts ready to run once Ubuntu 24.04 is installed on the Beast.

## Setup (run once after Ubuntu install)

```bash
sudo apt update && sudo apt install -y python3 python3-pip libmagic1
pip3 install Pillow rawpy psd-tools pillow-heif imageio
```

## Drive Deduplication

Three drives (~80% full each, mostly mirrors). Goal: one clean copy of each file.

```bash
# Step 1: Mount all three drives
sudo mount /dev/sdX1 /mnt/drive-5tb
sudo mount /dev/sdY1 /mnt/drive-6tb
sudo mount /dev/sdZ1 /mnt/drive-4tb

# Step 2: Scan (read-only, generates report)
python3 scripts/dedup.py scan /mnt/drive-5tb /mnt/drive-6tb /mnt/drive-4tb

# Step 3: Review the report
less dedup_report.txt

# Step 4: Consolidate (dry run first!)
python3 scripts/dedup.py consolidate /mnt/drive-6tb/consolidated --dry-run

# Step 5: Execute (after reviewing dry run)
python3 scripts/dedup.py consolidate /mnt/drive-6tb/consolidated --execute
```

## Image Converter (RAW/PSD → JPEG)

Converts .CR2, .CR3, .NEF, .ARW, .DNG, .PSD, .TIFF, .HEIC → JPEG.

```bash
# Preview what would be converted
python3 scripts/convert_to_jpeg.py /mnt/drive-6tb/Photos --dry-run

# Convert everything at 85% quality
python3 scripts/convert_to_jpeg.py /mnt/drive-6tb/Photos

# Convert and move originals to separate folder
python3 scripts/convert_to_jpeg.py /mnt/drive-6tb/Photos --move-originals

# Only convert camera RAW files
python3 scripts/convert_to_jpeg.py /mnt/drive-6tb/Photos --types raw
```

## Recommended Workflow

1. Mount all three drives
2. Run dedup scan → review report → consolidate to 6TB drive
3. Run image converter on consolidated folder
4. Verify results
5. Format the other two drives for new use

## Hardware

- i9-9880, 32GB DDR4, NVMe, GTX 1080 Ti
- Ubuntu 24.04 LTS
- Drives: 5TB + 6TB + 4TB (HDD)
