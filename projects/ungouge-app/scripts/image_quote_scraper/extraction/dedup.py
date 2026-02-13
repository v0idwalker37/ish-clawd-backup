"""Deduplication engine using perceptual hashing (images) and MD5 (documents).

Uses SQLite to track all seen files and prevent re-downloading.
"""

import os
import hashlib
import sqlite3
import logging
from typing import Optional
from datetime import datetime

from ..config import DEDUP_DB_PATH

logger = logging.getLogger(__name__)


class ImageDedupEngine:
    """Track seen files using perceptual hash (images) and MD5 (documents)."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEDUP_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_tables()
        self.duplicates_skipped = 0
        self._phash_available = None

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS files_seen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT NOT NULL,
                phash TEXT,
                source TEXT NOT NULL,
                source_url TEXT,
                file_type TEXT,
                file_size INTEGER,
                file_path TEXT,
                date_collected TEXT NOT NULL,
                UNIQUE(file_hash, source)
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_file_hash
            ON files_seen(file_hash)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_phash
            ON files_seen(phash)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_url
            ON files_seen(source_url)
        """)
        self.conn.commit()

    def _has_phash(self) -> bool:
        """Check if imagehash is available."""
        if self._phash_available is None:
            try:
                import imagehash
                from PIL import Image
                self._phash_available = True
            except ImportError:
                self._phash_available = False
                logger.warning("imagehash/Pillow not available, falling back to MD5 only")
        return self._phash_available

    def compute_file_hash(self, filepath: str) -> str:
        """Compute MD5 hash of a file."""
        md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                md5.update(chunk)
        return md5.hexdigest()

    def compute_phash(self, filepath: str) -> Optional[str]:
        """Compute perceptual hash for an image file."""
        if not self._has_phash():
            return None

        try:
            import imagehash
            from PIL import Image
            img = Image.open(filepath)
            phash = str(imagehash.phash(img))
            return phash
        except Exception as e:
            logger.debug(f"Could not compute phash for {filepath}: {e}")
            return None

    def is_duplicate_hash(self, file_hash: str) -> bool:
        """Check if we've seen this exact file hash before."""
        cursor = self.conn.execute(
            "SELECT 1 FROM files_seen WHERE file_hash = ?", (file_hash,)
        )
        return cursor.fetchone() is not None

    def is_duplicate_url(self, source_url: str) -> bool:
        """Check if we've already downloaded from this URL."""
        if not source_url:
            return False
        cursor = self.conn.execute(
            "SELECT 1 FROM files_seen WHERE source_url = ?", (source_url,)
        )
        return cursor.fetchone() is not None

    def is_duplicate_phash(self, phash: str, threshold: int = 8) -> bool:
        """Check if a perceptually similar image exists.
        
        Uses Hamming distance: images with distance < threshold are considered duplicates.
        Default threshold of 8 catches near-identical images with minor differences.
        """
        if not phash or not self._has_phash():
            return False

        try:
            import imagehash
            target = imagehash.hex_to_hash(phash)

            cursor = self.conn.execute(
                "SELECT phash FROM files_seen WHERE phash IS NOT NULL"
            )
            for (existing_phash,) in cursor:
                try:
                    existing = imagehash.hex_to_hash(existing_phash)
                    if target - existing < threshold:
                        return True
                except Exception:
                    continue
        except Exception as e:
            logger.debug(f"pHash comparison error: {e}")

        return False

    def is_duplicate(self, filepath: str = None, source_url: str = None,
                     file_hash: str = None) -> bool:
        """Check if a file is a duplicate (by hash, URL, or perceptual hash)."""
        # Check URL first (cheapest)
        if source_url and self.is_duplicate_url(source_url):
            self.duplicates_skipped += 1
            return True

        # Check file hash
        if file_hash and self.is_duplicate_hash(file_hash):
            self.duplicates_skipped += 1
            return True

        # Check perceptual hash for images
        if filepath and self._has_phash():
            ext = os.path.splitext(filepath)[1].lower()
            if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}:
                phash = self.compute_phash(filepath)
                if phash and self.is_duplicate_phash(phash):
                    self.duplicates_skipped += 1
                    return True

        return False

    def mark_seen(self, file_hash: str, source: str, source_url: str = "",
                  file_type: str = "", file_size: int = 0,
                  file_path: str = "", phash: str = None):
        """Mark a file as seen."""
        try:
            self.conn.execute(
                """INSERT OR IGNORE INTO files_seen
                   (file_hash, phash, source, source_url, file_type, file_size,
                    file_path, date_collected)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (file_hash, phash, source, source_url, file_type, file_size,
                 file_path, datetime.utcnow().isoformat())
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"SQLite error marking seen: {e}")

    def get_total_seen(self) -> int:
        cursor = self.conn.execute("SELECT COUNT(*) FROM files_seen")
        return cursor.fetchone()[0]

    def close(self):
        if self.conn:
            self.conn.close()
