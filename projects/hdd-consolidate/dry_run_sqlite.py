#!/usr/bin/env python3
"""HDD Consolidation — Dry Run (robust + resumable)

Goal: estimate final size for copying *one unique copy of every file* from:
  - /media/ungouge/Number_2
  - /media/ungouge/BOH 2
Into:
  - /media/ungouge/Blackhole01

Dedup rule: content hash (SHA-256). Optimize by hashing only files that share
sizes (since identical content => identical size).

Output:
  - index.db (sqlite)
  - dry_run_report.txt
  - dry_run_manifest.json (chosen unique files)

Safe:
  - NO deletes on source drives
  - NO writes to destination drive (dry run only)
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_DIR = Path("/home/ungouge/clawd/projects/hdd-consolidate")
DB_PATH = PROJECT_DIR / "index.db"
REPORT_PATH = PROJECT_DIR / "dry_run_report.txt"
MANIFEST_PATH = PROJECT_DIR / "dry_run_manifest.json"
LOG_PATH = PROJECT_DIR / "dry_run_sqlite.log"

SOURCE_DRIVES = [
    ("/media/ungouge/Number_2", "Number_2"),
    ("/media/ungouge/BOH 2", "BOH2"),
]
DEST_DRIVE = "/media/ungouge/Blackhole01"

CONVERT_EXTENSIONS = {
    ".cr2", ".cr3", ".nef", ".arw", ".orf", ".rw2", ".dng",
    ".psd",
    ".tiff", ".tif",
    ".heic", ".heif",
    ".raw",
}

BATCH_INSERT = 2000
PRINT_EVERY = 50000
HASH_PRINT_EVERY = 5000


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def human_size(nbytes: int) -> str:
    n = float(nbytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def sha256_file(path: str, chunk_size: int = 1 << 20) -> str | None:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def ensure_mounted() -> None:
    for mount, label in SOURCE_DRIVES:
        if not os.path.ismount(mount):
            raise RuntimeError(f"Source drive {label} not mounted at {mount}")
    if not os.path.ismount(DEST_DRIVE):
        raise RuntimeError(f"Destination drive not mounted at {DEST_DRIVE}")


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
          id INTEGER PRIMARY KEY,
          drive TEXT NOT NULL,
          full_path TEXT NOT NULL UNIQUE,
          rel_path TEXT NOT NULL,
          size INTEGER NOT NULL,
          ext TEXT NOT NULL,
          hash TEXT,
          needs_convert INTEGER NOT NULL DEFAULT 0,
          err TEXT
        );
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_files_size ON files(size);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_files_hash ON files(hash);")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
          key TEXT PRIMARY KEY,
          value TEXT
        );
        """
    )
    return conn


def meta_get(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def meta_set(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES (?,?)", (key, value))
    conn.commit()


def scan_sources(conn: sqlite3.Connection) -> None:
    log("Phase 1/3: scanning source drives (stat only)")

    total_inserted = 0
    for mount, label in SOURCE_DRIVES:
        meta_key = f"scan_complete:{label}"
        already = meta_get(conn, meta_key)
        if already:
            log(f"Skipping {label} — already marked complete ({already})")
            continue

        log(f"Scanning {label} ({mount})")
        inserted = 0
        bytes_seen = 0
        batch = []

        for root, _dirs, files in os.walk(mount, onerror=lambda e: log(f"os.walk error: {e}")):
            for name in files:
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, mount)
                ext = os.path.splitext(name)[1].lower()
                needs_convert = 1 if ext in CONVERT_EXTENSIONS else 0
                try:
                    st = os.stat(full_path)
                    size = int(st.st_size)
                    bytes_seen += size
                    batch.append((label, full_path, rel_path, size, ext, needs_convert, None))
                except (OSError, PermissionError) as e:
                    batch.append((label, full_path, rel_path, 0, ext, needs_convert, str(e)))

                if len(batch) >= BATCH_INSERT:
                    conn.executemany(
                        "INSERT OR IGNORE INTO files(drive, full_path, rel_path, size, ext, needs_convert, err) VALUES (?,?,?,?,?,?,?)",
                        batch,
                    )
                    conn.commit()
                    inserted += len(batch)
                    total_inserted += len(batch)
                    batch.clear()

                    if inserted % PRINT_EVERY == 0:
                        log(f"  {label}: {inserted:,} files indexed ({human_size(bytes_seen)})")

        if batch:
            conn.executemany(
                "INSERT OR IGNORE INTO files(drive, full_path, rel_path, size, ext, needs_convert, err) VALUES (?,?,?,?,?,?,?)",
                batch,
            )
            conn.commit()
            inserted += len(batch)
            total_inserted += len(batch)
            batch.clear()

        log(f"✓ {label}: indexed ~{inserted:,} files ({human_size(bytes_seen)})")
        meta_set(conn, meta_key, time.strftime("%Y-%m-%d %H:%M:%S"))

    meta_set(conn, "scan_completed_at", time.strftime("%Y-%m-%d %H:%M:%S"))
    total_in_db = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    log(f"Scan done. Total files in DB: {total_in_db:,}")


def fill_unique_size_hashes(conn: sqlite3.Connection) -> None:
    # For sizes that appear exactly once, we can assign a unique hash based on size.
    log("Phase 2/3: assigning hashes for unique-size files")
    conn.execute(
        """
        WITH uniq AS (
          SELECT size FROM files GROUP BY size HAVING COUNT(*) = 1
        )
        UPDATE files
          SET hash = 'SIZE:' || size
        WHERE hash IS NULL AND size IN (SELECT size FROM uniq);
        """
    )
    conn.commit()
    log("✓ Unique-size hash assignment complete")


def hash_duplicate_sizes(conn: sqlite3.Connection) -> None:
    log("Phase 3/3: hashing files that share sizes (SHA-256)")

    # Fetch sizes with duplicates
    dup_sizes = [row[0] for row in conn.execute("SELECT size FROM files GROUP BY size HAVING COUNT(*) > 1 AND size > 0").fetchall()]
    log(f"Sizes needing hashing: {len(dup_sizes):,}")

    total_to_hash = 0
    for size in dup_sizes:
        total_to_hash += conn.execute("SELECT COUNT(*) FROM files WHERE size=? AND hash IS NULL", (size,)).fetchone()[0]

    log(f"Files needing SHA-256: {total_to_hash:,}")
    start = time.time()
    done = 0

    for size in dup_sizes:
        rows = conn.execute("SELECT id, full_path FROM files WHERE size=? AND hash IS NULL", (size,)).fetchall()
        updates = []
        for file_id, full_path in rows:
            h = sha256_file(full_path)
            if not h:
                h = f"ERR:{full_path}"
            updates.append((h, file_id))

        if updates:
            conn.executemany("UPDATE files SET hash=? WHERE id=?", updates)
            conn.commit()
            done += len(updates)

        if done and done % HASH_PRINT_EVERY == 0:
            elapsed = time.time() - start
            rate = done / elapsed if elapsed > 0 else 0
            eta = (total_to_hash - done) / rate if rate > 0 else 0
            log(f"  hashed {done:,}/{total_to_hash:,} ({rate:.0f}/s, ETA {eta/60:.0f} min)")

    log("✓ Hashing complete")


def build_report_and_manifest(conn: sqlite3.Connection) -> dict:
    # Destination free space
    dest_stat = os.statvfs(DEST_DRIVE)
    dest_free = int(dest_stat.f_bavail * dest_stat.f_frsize)

    total_scanned = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    total_bytes = conn.execute("SELECT COALESCE(SUM(size),0) FROM files").fetchone()[0]

    # Unique chosen file per hash: choose smallest id per hash
    unique_count = conn.execute("SELECT COUNT(*) FROM (SELECT hash FROM files GROUP BY hash)").fetchone()[0]
    chosen_total = conn.execute(
        """
        SELECT COALESCE(SUM(f.size),0)
        FROM files f
        JOIN (SELECT MIN(id) AS id FROM files GROUP BY hash) c
        ON f.id = c.id;
        """
    ).fetchone()[0]

    dup_count = total_scanned - unique_count
    dup_space_saved = total_bytes - chosen_total

    # Conversion estimate: 40% heuristic
    convert_count = conn.execute(
        """
        SELECT COUNT(*) FROM files f
        JOIN (SELECT MIN(id) AS id FROM files GROUP BY hash) c
        ON f.id = c.id
        WHERE f.needs_convert = 1;
        """
    ).fetchone()[0]

    convert_est_size = conn.execute(
        """
        SELECT COALESCE(SUM(CAST(f.size * 0.4 AS INTEGER)),0)
        FROM files f
        JOIN (SELECT MIN(id) AS id FROM files GROUP BY hash) c
        ON f.id = c.id
        WHERE f.needs_convert = 1;
        """
    ).fetchone()[0]

    final_est_size = int(chosen_total + convert_est_size)

    # Extension breakdown (top 20 by count)
    ext_top = conn.execute(
        """
        SELECT ext, COUNT(*) AS c, COALESCE(SUM(size),0) AS s
        FROM files f
        JOIN (SELECT MIN(id) AS id FROM files GROUP BY hash) c2
        ON f.id = c2.id
        GROUP BY ext
        ORDER BY c DESC
        LIMIT 20;
        """
    ).fetchall()

    fits = final_est_size < dest_free

    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("HDD CONSOLIDATION — DRY RUN REPORT")
    report_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 70)
    report_lines.append("")

    report_lines.append("SUMMARY")
    report_lines.append(f"  Total files scanned:    {total_scanned:,}")
    report_lines.append(f"  Unique files (by hash): {unique_count:,}")
    report_lines.append(f"  Duplicates removed:     {dup_count:,}")
    report_lines.append(f"  Dedup space saved:      {human_size(dup_space_saved)}")
    report_lines.append("")

    report_lines.append("SIZE ESTIMATES")
    report_lines.append(f"  Unique files total:     {human_size(chosen_total)}")
    report_lines.append(f"  JPG conversions (~40%): {human_size(convert_est_size)} ({convert_count:,} files)")
    report_lines.append(f"  Estimated final size:   {human_size(final_est_size)}")
    report_lines.append(f"  Blackhole01 free:       {human_size(dest_free)}")
    report_lines.append(f"  Will it fit?            {'YES' if fits else 'NO'}")
    report_lines.append("")

    report_lines.append("TOP FILE TYPES (unique only, by count)")
    for ext, c, s in ext_top:
        report_lines.append(f"  {ext or '(no ext)':>10}: {c:>10,} files  ({human_size(s)})")

    report = "\n".join(report_lines) + "\n"
    REPORT_PATH.write_text(report, encoding="utf-8")

    # Manifest: chosen unique files list (for the copy/convert phase)
    chosen_rows = conn.execute(
        """
        SELECT f.drive, f.full_path, f.rel_path, f.size, f.ext, f.hash, f.needs_convert
        FROM files f
        JOIN (SELECT MIN(id) AS id FROM files GROUP BY hash) c
        ON f.id = c.id
        ORDER BY f.drive, f.rel_path;
        """
    ).fetchall()

    manifest = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "sources": [m for m, _ in SOURCE_DRIVES],
        "destination": DEST_DRIVE,
        "stats": {
            "total_scanned": total_scanned,
            "unique": unique_count,
            "duplicates": dup_count,
            "unique_total_size": chosen_total,
            "convert_count": convert_count,
            "convert_est_size": convert_est_size,
            "final_est_size": final_est_size,
            "dest_free": dest_free,
            "fits": fits,
        },
        "chosen": [
            {
                "drive": r[0],
                "full_path": r[1],
                "rel_path": r[2],
                "size": r[3],
                "ext": r[4],
                "hash": r[5],
                "needs_convert": bool(r[6]),
            }
            for r in chosen_rows
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return manifest


def main() -> int:
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        ensure_mounted()
    except Exception as e:
        log(f"ERROR: {e}")
        return 2

    conn = connect_db()

    scan_done = meta_get(conn, "scan_completed_at")
    if not scan_done:
        existing = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        log(f"Scan not marked complete yet. Current DB rows: {existing:,}. Continuing scan...")
        scan_sources(conn)
    else:
        log(f"Scan already completed at {scan_done} — skipping scan.")

    fill_unique_size_hashes(conn)
    hash_duplicate_sizes(conn)

    log("Building report + manifest...")
    manifest = build_report_and_manifest(conn)
    log(f"Report written: {REPORT_PATH}")
    log(f"Manifest written: {MANIFEST_PATH}")
    log("Dry run COMPLETE.")

    # Print a tiny summary for the log
    s = manifest["stats"]
    log(
        "SUMMARY: "
        f"scanned={s['total_scanned']:,} unique={s['unique']:,} "
        f"dupes={s['duplicates']:,} est_final={human_size(s['final_est_size'])} "
        f"dest_free={human_size(s['dest_free'])} fits={s['fits']}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
