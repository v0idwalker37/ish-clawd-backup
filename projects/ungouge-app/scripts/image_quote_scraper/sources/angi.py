"""Angi/HomeAdvisor Scraper — Extracts quote images from cost guides and reviews.

This is tricky — they have Cloudflare anti-scraping. We use Playwright with
stealth settings and skip gracefully if blocked.
"""

import re
import time
import logging
from typing import List, Optional, Set
from urllib.parse import urljoin
import threading

from ..config import ANGI_PROJECT_TYPES, IMAGE_EXTENSIONS
from ..models import QuoteFile, SourceType, ScrapeResult
from ..extraction.downloader import download_file
from ..extraction.dedup import ImageDedupEngine
from ..status import ImageScraperStatus
from ..utils.stealth import StealthManager

logger = logging.getLogger(__name__)

# Angi cost guide URL patterns
ANGI_COST_URL = "https://www.angi.com/articles/how-much-does-{project_type}-cost.htm"
ANGI_COSTS_URL = "https://www.angi.com/costs/{project_type}"
HOMEADVISOR_COST_URL = "https://www.homeadvisor.com/cost/{project_type}/"


class AngiScraper:
    """Scrapes Angi/HomeAdvisor for contractor quote images."""

    def __init__(self, dedup: ImageDedupEngine, status: ImageScraperStatus,
                 shutdown_event: Optional[threading.Event] = None,
                 headless: bool = True):
        self.dedup = dedup
        self.status = status
        self.shutdown_event = shutdown_event
        self.stealth = StealthManager("angi", shutdown_event)
        self.headless = headless
        self.collected_files: List[QuoteFile] = []
        self.seen_urls: Set[str] = set()
        self._blocked = False

    def run(self, max_files: int = 40) -> ScrapeResult:
        """Run the Angi scraper."""
        self.status.init_source("angi")
        result = ScrapeResult(source=SourceType.ANGI)
        start_time = time.time()

        # Try Angi cost guides
        for project_type in ANGI_PROJECT_TYPES:
            if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                break
            if self._blocked:
                logger.warning("[angi] Blocked by Cloudflare, stopping Angi scraper")
                break

            # Try both URL patterns
            urls = [
                ANGI_COSTS_URL.format(project_type=project_type),
                ANGI_COST_URL.format(project_type=project_type),
            ]

            for url in urls:
                if self.stealth.should_stop() or self._blocked:
                    break
                try:
                    self._scrape_cost_page(url, project_type)
                except Exception as e:
                    logger.debug(f"[angi] Error on {url}: {e}")
                    self.status.record_error("angi")

        result.status = "blocked" if self._blocked else "done"
        result.files_downloaded = len(self.collected_files)
        result.files = self.collected_files
        result.elapsed_seconds = time.time() - start_time
        self.status.set_source_status("angi", result.status)
        return result

    def _scrape_cost_page(self, url: str, project_type: str):
        """Scrape a cost guide page for embedded images."""
        import requests as req

        if url in self.seen_urls:
            return
        self.seen_urls.add(url)

        self.stealth.rate_limit()
        self.status.set_last_url("angi", url)
        self.status.record_post_scanned("angi")

        headers = self.stealth.get_headers()

        try:
            resp = req.get(url, headers=headers, timeout=30, allow_redirects=True)

            if resp.status_code == 403:
                logger.warning(f"[angi] Blocked (403): {url}")
                self._blocked = True
                return

            if resp.status_code == 503:
                logger.warning(f"[angi] Cloudflare challenge (503): {url}")
                self._blocked = True
                return

            if resp.status_code != 200:
                logger.debug(f"[angi] HTTP {resp.status_code}: {url}")
                return

            # Check for Cloudflare challenge page
            if "cf-browser-verification" in resp.text or "challenge-platform" in resp.text:
                logger.warning("[angi] Cloudflare challenge detected")
                self._blocked = True
                return

            # Parse for images
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
            except ImportError:
                logger.warning("[angi] BeautifulSoup not available")
                return

            # Find content images (not icons/logos)
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src") or ""
                alt = (img.get("alt") or "").lower()

                if not src or not src.startswith("http"):
                    if src and src.startswith("/"):
                        src = urljoin(url, src)
                    else:
                        continue

                # Look for quote/estimate related images
                quote_indicators = [
                    "quote", "estimate", "cost", "price",
                    "breakdown", "invoice", "sample",
                ]
                is_relevant = (
                    any(kw in alt for kw in quote_indicators) or
                    any(kw in src.lower() for kw in quote_indicators)
                )

                # Also get large content images (likely screenshots of quotes)
                width = img.get("width")
                height = img.get("height")
                is_large = False
                try:
                    if width and height:
                        is_large = int(width) > 300 and int(height) > 200
                except (ValueError, TypeError):
                    pass

                if is_relevant or is_large:
                    self._download_image(src, url, project_type)

            self.stealth.reset_backoff()

        except req.exceptions.Timeout:
            logger.debug(f"[angi] Timeout: {url}")
        except req.exceptions.ConnectionError:
            logger.debug(f"[angi] Connection error: {url}")
            self.stealth.backoff()

    def _download_image(self, img_url: str, page_url: str, project_type: str):
        """Download an image from Angi/HomeAdvisor."""
        if img_url in self.seen_urls:
            return
        self.seen_urls.add(img_url)

        # Skip common non-content images
        skip_patterns = [
            "logo", "icon", "avatar", "sprite",
            "social", "badge", "arrow", "check",
            "star", "rating", "play-button",
        ]
        if any(pat in img_url.lower() for pat in skip_patterns):
            return

        if self.dedup.is_duplicate(source_url=img_url):
            self.status.record_duplicate()
            return

        metadata = {
            "post_title": f"Angi Cost Guide: {project_type}",
            "post_url": page_url,
            "post_text": f"From Angi.com cost guide for {project_type}",
        }

        quote_file = download_file(img_url, SourceType.ANGI, metadata)
        if quote_file:
            self.dedup.mark_seen(
                file_hash=quote_file.file_hash,
                source="angi",
                source_url=img_url,
                file_type=quote_file.file_type,
                file_size=quote_file.file_size,
                file_path=quote_file.file_path,
            )
            self.collected_files.append(quote_file)
            self.status.record_image_found("angi")
            self.status.record_download("angi")

    def close(self):
        pass
