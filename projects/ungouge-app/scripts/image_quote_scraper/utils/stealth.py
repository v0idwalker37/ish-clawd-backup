"""Anti-detection utilities: delays, user agents, human-like behavior."""

import time
import random
import logging
from typing import Optional
import threading

from ..config import (
    USER_AGENTS, JITTER_MIN, JITTER_MAX,
    SESSION_BREAK_EVERY, SESSION_BREAK_DURATION,
    BACKOFF_INITIAL, BACKOFF_MULTIPLIER, BACKOFF_MAX,
    RATE_LIMITS,
)

logger = logging.getLogger(__name__)


class StealthManager:
    """Manages rate limiting, delays, and anti-detection for a source."""

    def __init__(self, source_name: str, shutdown_event: Optional[threading.Event] = None):
        self.source_name = source_name
        self.shutdown_event = shutdown_event
        self.request_count = 0
        self.session_start = time.time()
        self._backoff_seconds = BACKOFF_INITIAL
        self._ua_index = random.randint(0, len(USER_AGENTS) - 1)
        self.base_delay = RATE_LIMITS.get(source_name, 2)

    def get_user_agent(self) -> str:
        """Get a rotating user agent."""
        self._ua_index = (self._ua_index + 1) % len(USER_AGENTS)
        return USER_AGENTS[self._ua_index]

    def get_headers(self) -> dict:
        """Get browser-like headers with rotating UA."""
        return {
            "User-Agent": self.get_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

    def rate_limit(self):
        """Apply rate limiting with jitter and session breaks."""
        if self.should_stop():
            return

        self.request_count += 1

        # Session break every N requests
        if self.request_count % SESSION_BREAK_EVERY == 0:
            pause = random.uniform(*SESSION_BREAK_DURATION)
            logger.info(f"[{self.source_name}] Session break: {pause:.0f}s "
                        f"(after {self.request_count} requests)")
            self.interruptible_sleep(pause)
            self._backoff_seconds = BACKOFF_INITIAL

        # Normal rate limiting with jitter
        delay = self.base_delay + random.uniform(JITTER_MIN, JITTER_MAX)
        self.interruptible_sleep(delay)

    def random_delay(self, min_sec: float = 2, max_sec: float = 5):
        """Random delay between actions."""
        delay = random.uniform(min_sec, max_sec)
        self.interruptible_sleep(delay)

    def human_scroll_delay(self):
        """Simulate human scroll timing."""
        delay = random.uniform(1.5, 4.0)
        self.interruptible_sleep(delay)

    def backoff(self):
        """Exponential backoff on errors."""
        logger.warning(f"[{self.source_name}] Backing off: {self._backoff_seconds}s")
        self.interruptible_sleep(self._backoff_seconds)
        self._backoff_seconds = min(
            self._backoff_seconds * BACKOFF_MULTIPLIER, BACKOFF_MAX
        )

    def reset_backoff(self):
        self._backoff_seconds = BACKOFF_INITIAL

    def interruptible_sleep(self, seconds: float):
        """Sleep that can be interrupted by shutdown event."""
        if self.shutdown_event:
            self.shutdown_event.wait(timeout=seconds)
        else:
            time.sleep(seconds)

    def should_stop(self) -> bool:
        """Check if we should stop."""
        if self.shutdown_event and self.shutdown_event.is_set():
            return True
        return False


def human_like_scroll(page, direction="down", distance=None):
    """Perform human-like scrolling on a Playwright page.
    
    Scrolls in variable amounts with pauses, occasionally scrolls back up.
    """
    if distance is None:
        distance = random.randint(300, 800)

    if direction == "down":
        page.mouse.wheel(0, distance)
    elif direction == "up":
        page.mouse.wheel(0, -distance)

    # Small random pause after scroll
    time.sleep(random.uniform(0.3, 1.0))

    # Occasionally scroll back up a little (10% chance)
    if direction == "down" and random.random() < 0.1:
        page.mouse.wheel(0, -random.randint(50, 200))
        time.sleep(random.uniform(0.5, 1.5))


def simulate_reading_pause():
    """Pause as if reading content."""
    time.sleep(random.uniform(1.0, 3.0))
