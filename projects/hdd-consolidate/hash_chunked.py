#!/usr/bin/env python3
"""
Chunked file hashing - processes files with per-file commits and timeout handling.
Resumes automatically from where it left off (only hashes files with hash IS NULL).
"""

import sqlite3
import hashlib
import os
import sys
import time
import signal
from pathlib import Path

DB_PATH = Path(__file__).parent / 'index.db'
BATCH_SIZE = 500  # query batch size (commit is per-file)
LOG_PATH = Path(__file__).parent / 'hash_progress.log'
PER_FILE_TIMEOUT = 300  # 5 min max per file
PROGRESS_INTERVAL = 50  # log every N files


class FileTimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):
    raise FileTimeoutError("File hashing timed out")


def log(msg):
    """Log to both console and file"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')


def sha256_file(path, chunk_size=65536):
    """Hash file in chunks with timeout protection"""
    hasher = hashlib.sha256()
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    try:
        file_size = os.path.getsize(path)
        # Dynamic timeout: 5 min base + 1 min per GB
        timeout = max(PER_FILE_TIMEOUT, int(file_size / 1_000_000_000) * 60 + PER_FILE_TIMEOUT)
        signal.alarm(timeout)
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        signal.alarm(0)
        return hasher.hexdigest()
    except FileTimeoutError:
        signal.alarm(0)
        return None
    except Exception:
        signal.alarm(0)
        return None
    finally:
        signal.signal(signal.SIGALRM, old_handler)


def main():
    log("=== Starting chunked hash processing (v2 - per-file commit) ===")

    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL;")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM files WHERE hash IS NULL")
    remaining = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM files")
    total = c.fetchone()[0]

    log(f"Total files: {total:,}")
    log(f"Remaining: {remaining:,}")
    log(f"Batch query size: {BATCH_SIZE}, commit: per-file")
    log("")

    processed = 0
    errors = 0
    batch_num = 0

    while remaining > 0:
        batch_num += 1
        # Fetch a batch of unhashed files
        c.execute(
            "SELECT id, full_path FROM files WHERE hash IS NULL LIMIT ?",
            (BATCH_SIZE,),
        )
        files = c.fetchall()
        if not files:
            log("No more files to process")
            break

        log(f"Batch {batch_num}: Fetched {len(files)} files to hash...")

        for i, (file_id, path) in enumerate(files, 1):
            file_hash = sha256_file(path)

            if file_hash:
                c.execute("UPDATE files SET hash = ? WHERE id = ?", (file_hash, file_id))
                processed += 1
            else:
                c.execute("UPDATE files SET hash = 'ERROR' WHERE id = ?", (file_id,))
                errors += 1
                log(f"  ERROR: {path}")

            # Commit after every file so progress is never lost
            conn.commit()

            # Periodic progress log
            if (processed + errors) % PROGRESS_INTERVAL == 0:
                c.execute("SELECT COUNT(*) FROM files WHERE hash IS NULL")
                remaining = c.fetchone()[0]
                pct = ((total - remaining) / total) * 100
                log(
                    f"  Progress: {pct:.1f}% ({total - remaining:,}/{total:,}) "
                    f"| remaining={remaining:,} errors={errors}"
                )

        # Update remaining after each batch
        c.execute("SELECT COUNT(*) FROM files WHERE hash IS NULL")
        remaining = c.fetchone()[0]
        pct = ((total - remaining) / total) * 100
        log(f"  Batch {batch_num} done: {pct:.1f}% ({total - remaining:,}/{total:,}) | remaining={remaining:,} errors={errors}")
        log("")

        time.sleep(0.05)

    conn.close()

    log("=== Hash processing complete ===")
    log(f"Total processed: {processed:,}")
    log(f"Total errors: {errors}")


if __name__ == '__main__':
    main()
