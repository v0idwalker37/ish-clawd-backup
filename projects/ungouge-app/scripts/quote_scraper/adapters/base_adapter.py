"""Base adapter class with common anti-detection and rate limiting."""

import time
import random
import logging
import requests
from typing import Optional, List

from ..config import (
    USER_AGENTS, JITTER_MIN, JITTER_MAX,
    SESSION_BREAK_EVERY, SESSION_BREAK_MIN, SESSION_BREAK_MAX,
    BACKOFF_INITIAL, BACKOFF_MULTIPLIER, BACKOFF_MAX,
)
from ..models import RawQuote, ExtractedQuote
from ..extractor import extract_quotes
from ..dedup import DedupEngine
from ..status import StatusTracker

logger = logging.getLogger(__name__)


class BaseAdapter:
    """Base class for all source adapters."""

    SOURCE_NAME = "base"
    BASE_DELAY = 2.0

    def __init__(self, dedup: DedupEngine, status: StatusTracker, 
                 shutdown_event=None):
        self.dedup = dedup
        self.status = status
        self.shutdown_event = shutdown_event
        self.session = requests.Session()
        self._request_count = 0
        self._backoff_seconds = BACKOFF_INITIAL
        self._ua_index = random.randint(0, len(USER_AGENTS) - 1)
        self.collected_quotes: List[ExtractedQuote] = []

    def _get_headers(self) -> dict:
        """Get headers with rotating user agent."""
        self._ua_index = (self._ua_index + 1) % len(USER_AGENTS)
        return {
            "User-Agent": USER_AGENTS[self._ua_index],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }

    def _rate_limit(self):
        """Apply rate limiting with jitter and session breaks."""
        if self.should_stop():
            return

        # Session break every N requests
        self._request_count += 1
        if self._request_count % SESSION_BREAK_EVERY == 0:
            pause = random.uniform(SESSION_BREAK_MIN, SESSION_BREAK_MAX)
            logger.info(f"[{self.SOURCE_NAME}] Session break: {pause:.0f}s "
                       f"(after {self._request_count} requests)")
            self._interruptible_sleep(pause)
            # Reset backoff after session break
            self._backoff_seconds = BACKOFF_INITIAL

        # Normal rate limiting with jitter
        delay = self.BASE_DELAY + random.uniform(JITTER_MIN, JITTER_MAX)
        self._interruptible_sleep(delay)

    def _interruptible_sleep(self, seconds: float):
        """Sleep that can be interrupted by shutdown."""
        if self.shutdown_event:
            self.shutdown_event.wait(timeout=seconds)
        else:
            time.sleep(seconds)

    def _backoff(self):
        """Exponential backoff on errors."""
        logger.warning(f"[{self.SOURCE_NAME}] Backing off: {self._backoff_seconds}s")
        self._interruptible_sleep(self._backoff_seconds)
        self._backoff_seconds = min(
            self._backoff_seconds * BACKOFF_MULTIPLIER, BACKOFF_MAX
        )

    def _reset_backoff(self):
        self._backoff_seconds = BACKOFF_INITIAL

    def fetch_url(self, url: str, json_mode: bool = False, 
                  allow_redirects: bool = True) -> Optional[requests.Response]:
        """Fetch a URL with error handling and anti-detection."""
        if self.should_stop():
            return None

        self._rate_limit()
        self.status.record_request(self.SOURCE_NAME)
        self.status.set_last_url(self.SOURCE_NAME, url)

        try:
            headers = self._get_headers()
            if json_mode:
                headers["Accept"] = "application/json"

            resp = self.session.get(
                url,
                headers=headers,
                timeout=30,
                allow_redirects=allow_redirects,
            )

            # Check for blocks/rate limits
            if resp.status_code == 429:
                logger.warning(f"[{self.SOURCE_NAME}] Rate limited (429): {url}")
                self.status.record_error(self.SOURCE_NAME)
                self._backoff()
                return None

            if resp.status_code == 403:
                logger.warning(f"[{self.SOURCE_NAME}] Forbidden (403): {url}")
                self.status.record_error(self.SOURCE_NAME)
                self._backoff()
                return None

            if resp.status_code == 404:
                logger.debug(f"[{self.SOURCE_NAME}] Not found (404): {url}")
                return None

            # Check for login redirect
            if resp.status_code in (301, 302, 303, 307, 308):
                final_url = resp.headers.get("Location", "")
                if "login" in final_url.lower() or "signin" in final_url.lower():
                    logger.warning(f"[{self.SOURCE_NAME}] Login redirect: {url}")
                    return None

            if resp.status_code >= 400:
                logger.warning(f"[{self.SOURCE_NAME}] HTTP {resp.status_code}: {url}")
                self.status.record_error(self.SOURCE_NAME)
                return None

            self._reset_backoff()
            return resp

        except requests.exceptions.Timeout:
            logger.warning(f"[{self.SOURCE_NAME}] Timeout: {url}")
            self.status.record_error(self.SOURCE_NAME)
            return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"[{self.SOURCE_NAME}] Connection error: {url}")
            self.status.record_error(self.SOURCE_NAME)
            self._backoff()
            return None
        except Exception as e:
            logger.error(f"[{self.SOURCE_NAME}] Fetch error: {e}")
            self.status.record_error(self.SOURCE_NAME)
            return None

    def process_raw_quote(self, raw: RawQuote) -> List[ExtractedQuote]:
        """Extract quotes from raw text and check for duplicates."""
        extracted = extract_quotes(raw)
        new_quotes = []

        for eq in extracted:
            location = f"{eq.location_city},{eq.location_state}"
            if self.dedup.is_duplicate(
                eq.raw.source, eq.dollar_amount, eq.project_type, location
            ):
                self.status.record_duplicate()
                continue

            # Mark as seen
            self.dedup.mark_seen(
                eq.raw.source, eq.raw.source_url, eq.raw.source_id,
                eq.dollar_amount, eq.project_type, location
            )
            self.status.record_quote(self.SOURCE_NAME)
            new_quotes.append(eq)

        self.collected_quotes.extend(new_quotes)
        return new_quotes

    def should_stop(self) -> bool:
        """Check if we should stop (shutdown signal)."""
        if self.shutdown_event and self.shutdown_event.is_set():
            return True
        return False

    def run(self, max_quotes: int = 1000) -> List[ExtractedQuote]:
        """Run the adapter. Override in subclasses."""
        raise NotImplementedError

    def close(self):
        """Clean up."""
        self.session.close()
