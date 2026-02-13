"""Deduplication engine using SQLite."""

import os
import sqlite3
import json
import hashlib
import logging
from datetime import datetime
from typing import Optional

from .config import DEDUP_DB_PATH, DATA_DIR
from .extractor import content_hash

logger = logging.getLogger(__name__)


class DedupEngine:
    """Track seen quotes in SQLite to avoid duplicates."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEDUP_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()
        self.duplicates_skipped = 0

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS quotes_seen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                source_url TEXT,
                source_id TEXT,
                dollar_amount REAL,
                project_type TEXT,
                location TEXT,
                date_collected TEXT NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_hash
            ON quotes_seen(content_hash)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_id
            ON quotes_seen(source, source_id)
        """)
        self.conn.commit()

    def is_duplicate(self, source: str, dollar_amount: float, 
                     project_type: str, location: str) -> bool:
        """Check if we've already seen this quote."""
        h = content_hash(source, dollar_amount, project_type, location)
        cursor = self.conn.execute(
            "SELECT 1 FROM quotes_seen WHERE content_hash = ?", (h,)
        )
        return cursor.fetchone() is not None

    def is_source_id_seen(self, source: str, source_id: str) -> bool:
        """Check if we've already processed this source ID (post/review)."""
        cursor = self.conn.execute(
            "SELECT 1 FROM quotes_seen WHERE source = ? AND source_id = ?",
            (source, source_id)
        )
        return cursor.fetchone() is not None

    def mark_seen(self, source: str, source_url: str, source_id: str,
                  dollar_amount: float, project_type: str, location: str):
        """Mark a quote as seen."""
        h = content_hash(source, dollar_amount, project_type, location)
        try:
            self.conn.execute(
                """INSERT OR IGNORE INTO quotes_seen 
                   (content_hash, source, source_url, source_id, dollar_amount,
                    project_type, location, date_collected)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (h, source, source_url, source_id, dollar_amount,
                 project_type, location, datetime.utcnow().isoformat())
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"SQLite error marking seen: {e}")

    def load_existing_quotes(self, quotes_file: str):
        """Load existing quotes from JSON file into dedup DB."""
        if not os.path.exists(quotes_file):
            logger.warning(f"Existing quotes file not found: {quotes_file}")
            return 0

        try:
            with open(quotes_file, "r", encoding="utf-8") as f:
                quotes = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading existing quotes: {e}")
            return 0

        count = 0
        for q in quotes:
            # Handle the format from real-quotes.json
            source = q.get("source", "existing")
            source_url = q.get("source", "")
            cost = q.get("cost", 0)
            project_type = q.get("project_type", "unknown")
            location = q.get("location", {})
            if isinstance(location, dict):
                loc_str = f"{location.get('city', '')},{location.get('state', '')}"
            else:
                loc_str = str(location)
            
            source_id = hashlib.sha256(
                f"{source}|{cost}|{project_type}|{loc_str}".encode()
            ).hexdigest()[:12]
            
            if not self.is_duplicate(source, cost, project_type, loc_str):
                self.mark_seen(source, source_url, source_id, cost, project_type, loc_str)
                count += 1

        logger.info(f"Loaded {count} existing quotes into dedup DB")
        return count

    def get_total_seen(self) -> int:
        cursor = self.conn.execute("SELECT COUNT(*) FROM quotes_seen")
        return cursor.fetchone()[0]

    def close(self):
        if self.conn:
            self.conn.close()
