"""Status tracking for the scraper."""

import os
import json
import copy
import time
import threading
import logging
from datetime import datetime

from .config import STATUS_FILE, DATA_DIR

logger = logging.getLogger(__name__)


class StatusTracker:
    """Track and periodically write scraper status to JSON."""

    def __init__(self, status_file: str = None):
        self.status_file = status_file or STATUS_FILE
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        
        self.started_at = datetime.utcnow().isoformat()
        self.running = True
        self.sources = {}
        self.total_quotes = 0
        self.duplicates_skipped = 0
        self.last_activity = self.started_at
        self._lock = threading.Lock()
        self._timer = None
        self._write_interval = 30  # seconds

    def init_source(self, source_name: str):
        with self._lock:
            self.sources[source_name] = {
                "quotes_found": 0,
                "requests_made": 0,
                "errors": 0,
                "status": "running",
                "last_url": "",
            }

    def record_request(self, source_name: str):
        with self._lock:
            if source_name in self.sources:
                self.sources[source_name]["requests_made"] += 1
                self.last_activity = datetime.utcnow().isoformat()

    def record_quote(self, source_name: str):
        with self._lock:
            if source_name in self.sources:
                self.sources[source_name]["quotes_found"] += 1
            self.total_quotes += 1
            self.last_activity = datetime.utcnow().isoformat()

    def record_error(self, source_name: str):
        with self._lock:
            if source_name in self.sources:
                self.sources[source_name]["errors"] += 1

    def record_duplicate(self):
        with self._lock:
            self.duplicates_skipped += 1

    def set_source_status(self, source_name: str, status: str):
        with self._lock:
            if source_name in self.sources:
                self.sources[source_name]["status"] = status

    def set_last_url(self, source_name: str, url: str):
        with self._lock:
            if source_name in self.sources:
                self.sources[source_name]["last_url"] = url

    def get_status_dict(self) -> dict:
        with self._lock:
            elapsed = (datetime.utcnow() - datetime.fromisoformat(self.started_at)).total_seconds()
            return {
                "started_at": self.started_at,
                "running": self.running,
                "elapsed_seconds": int(elapsed),
                "sources": copy.deepcopy(self.sources),
                "total_quotes": self.total_quotes,
                "duplicates_skipped": self.duplicates_skipped,
                "last_activity": self.last_activity,
            }

    def write_status(self):
        """Write current status to JSON file."""
        try:
            status = self.get_status_dict()
            tmp_file = self.status_file + ".tmp"
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
            os.replace(tmp_file, self.status_file)
        except Exception as e:
            logger.error(f"Error writing status: {e}")

    def start_periodic_write(self):
        """Start writing status every N seconds in background."""
        def _write_loop():
            while self.running:
                try:
                    self.write_status()
                except Exception as e:
                    logger.error(f"Status write error: {e}")
                time.sleep(self._write_interval)
            # Final write
            try:
                self.write_status()
            except Exception:
                pass

        self._timer = threading.Thread(target=_write_loop, daemon=True)
        self._timer.start()

    def stop(self):
        self.running = False
        self.write_status()

    def log_summary(self):
        status = self.get_status_dict()
        logger.info("=== Scraper Summary ===")
        logger.info(f"  Elapsed: {status['elapsed_seconds']}s")
        logger.info(f"  Total quotes: {status['total_quotes']}")
        logger.info(f"  Duplicates skipped: {status['duplicates_skipped']}")
        for src, data in status["sources"].items():
            logger.info(f"  {src}: {data['quotes_found']} quotes, "
                       f"{data['requests_made']} requests, "
                       f"{data['errors']} errors")
