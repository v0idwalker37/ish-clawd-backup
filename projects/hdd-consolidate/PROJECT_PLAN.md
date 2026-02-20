# HDD Consolidation Project - COMPLETE PLAN

**Last Updated:** 2026-02-17 17:40 EST

## Project Goal
Consolidate duplicate files from multiple hard drives (BOH2, Number_2) into a single organized archive (Blackhole01) without deleting anything from source drives.

## Drive Configuration
- **Source Drives:**
  - BOH 2 (`/media/ungouge/BOH 2`) - 4.6TB total, 393GB free
  - Number_2 (`/media/ungouge/Number_2`) - 5.5TB total, 3.8TB free
  
- **Destination:**
  - Blackhole01 (`/media/ungouge/Blackhole01`) - 3.7TB free

## Strategy
1. **Hash all files** on source drives (SHA256)
2. **Identify duplicates** by comparing hashes
3. **Copy ONE unique file per hash** to Blackhole01
4. **Maintain directory structure** from source
5. **NEVER DELETE** from source drives

## Copy Priority Rules
When multiple copies of the same file exist:
1. Prefer Number_2 over BOH2
2. Prefer shortest/cleanest path
3. Skip trash/recycle bin files

## File Conversion (NOT YET IMPLEMENTED)
50,034 files need conversion:
- 14,134 CR2 (Canon RAW)
- 276 TIF
- 259 TIFF
- 122 PSD (Photoshop)
- 12 RAW

**Decision needed:** Convert before/after consolidation, target format, quality

## Duplicate Statistics (as of 2026-02-17)
- Total files scanned: 566,989
- Unique files: 247,233 (44%)
- Duplicate files: 319,756 (56%)
- Duplicate groups: 72,594
- **Wasted space: 4.7 TB**

## Top Space Wasters
1. GOPR0770.MP4 (GoPro video): 108GB (30 copies)
2. jasontraskpersonal.pst (Outlook): 101GB (8 copies)
3. GOPR0773/0774.MP4 (GoPro): 85GB each (24 copies)

## Current Status (2026-02-17 17:40)
- ✅ Hashing complete (566,989 files, 0 errors)
- ✅ Duplicate analysis complete (report generated)
- 🔄 Consolidation running (PID 52605+)
- ⏳ Estimated time: 2-4 hours (copying ~2-3TB of unique data)

## Output Files
- `index.db` - SQLite database with all file metadata and hashes
- `duplicate_report.json` - Full duplicate analysis (JSON)
- `duplicate_summary.txt` - Human-readable top 50 duplicates
- `consolidation.log` - Real-time consolidation progress
- `consolidation_progress.log` - Batch progress updates

## Scripts
- `hash_chunked.py` - Hash all files in batches
- `consolidate_to_blackhole.py` - Copy unique files to Blackhole01

## CRITICAL RULES (DO NOT FORGET)
1. **NEVER DELETE FILES FROM SOURCE DRIVES**
2. **ONLY COPY** - this is a consolidation, not a cleanup
3. **Maintain structure** - recreate source folder paths on destination
4. **One unique file per hash** - no duplicates on Blackhole01
5. **Priority: Number_2 > BOH2** when choosing which copy to keep

## Next Steps After Consolidation
1. Verify all unique files copied successfully
2. Compare file counts (source unique vs destination)
3. Decide on file conversion strategy
4. Optional: Move Blackhole01 to offline storage

---
**DO NOT REPEAT THIS CONVERSATION AGAIN** - All details are in this file.
