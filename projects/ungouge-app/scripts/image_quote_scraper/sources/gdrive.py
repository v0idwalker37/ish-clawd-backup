"""Google Drive / Dropbox Public Link Hunter.

Searches Google for publicly shared contractor quote PDFs/images
hosted on Google Drive and Dropbox.
"""

import re
import json
import time
import logging
import requests as req
from typing import List, Optional, Set
from urllib.parse import quote_plus, urlparse, parse_qs
import threading

from ..config import GDRIVE_SEARCH_QUERIES, GDRIVE_URL_PATTERN, RATE_LIMITS
from ..models import QuoteFile, SourceType, ScrapeResult
from ..extraction.downloader import download_file, normalize_download_url
from ..extraction.dedup import ImageDedupEngine
from ..status import ImageScraperStatus
from ..utils.stealth import StealthManager

logger = logging.getLogger(__name__)


class GDriveScraper:
    """Hunts for publicly shared contractor quotes on Google Drive and Dropbox."""

    def __init__(self, dedup: ImageDedupEngine, status: ImageScraperStatus,
                 shutdown_event: Optional[threading.Event] = None):
        self.dedup = dedup
        self.status = status
        self.shutdown_event = shutdown_event
        self.stealth = StealthManager("gdrive", shutdown_event)
        self.collected_files: List[QuoteFile] = []
        self.seen_urls: Set[str] = set()

    def run(self, max_files: int = 50, queries: List[str] = None) -> ScrapeResult:
        """Run the Google Drive scraper."""
        self.status.init_source("gdrive")
        queries = queries or GDRIVE_SEARCH_QUERIES
        result = ScrapeResult(source=SourceType.GDRIVE)
        start_time = time.time()

        for query in queries:
            if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                break

            logger.info(f"[gdrive] Searching: {query[:60]}...")

            try:
                urls = self._search_google(query)
                logger.info(f"[gdrive] Found {len(urls)} URLs for query")

                for url in urls:
                    if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                        break

                    self._process_url(url, query)

            except Exception as e:
                logger.error(f"[gdrive] Error searching '{query[:40]}': {e}")
                self.status.record_error("gdrive")

            # Delay between searches (Google is aggressive about blocking)
            self.stealth.random_delay(5, 15)

        result.status = "done"
        result.files_downloaded = len(self.collected_files)
        result.files = self.collected_files
        result.elapsed_seconds = time.time() - start_time
        self.status.set_source_status("gdrive", "done")
        return result

    def _search_google(self, query: str) -> List[str]:
        """Search Google for URLs matching the query.
        
        Uses Google's HTML search page (no API key needed).
        Limited to ~10 results per query to avoid blocks.
        """
        urls = []
        encoded = quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded}&num=20"

        headers = self.stealth.get_headers()
        headers["Accept"] = "text/html,application/xhtml+xml"

        try:
            self.stealth.rate_limit()
            resp = req.get(search_url, headers=headers, timeout=30)

            if resp.status_code == 429:
                logger.warning("[gdrive] Google rate limited us")
                self.stealth.backoff()
                return []

            if resp.status_code != 200:
                logger.debug(f"[gdrive] Google returned {resp.status_code}")
                return []

            # Extract URLs from search results
            content = resp.text

            # Google Drive links
            gdrive_pattern = r'https?://drive\.google\.com/(?:file/d/|open\?id=|uc\?[^"&]*id=)([a-zA-Z0-9_-]+)'
            for match in re.finditer(gdrive_pattern, content):
                full_url = match.group(0)
                if full_url not in self.seen_urls:
                    urls.append(full_url)

            # Dropbox links
            dropbox_pattern = r'https?://(?:www\.)?dropbox\.com/[^\s"<>]+'
            for match in re.finditer(dropbox_pattern, content):
                url = match.group(0).rstrip('"').rstrip("'").rstrip("\\")
                if url not in self.seen_urls:
                    urls.append(url)

            # Direct PDF links
            pdf_pattern = r'https?://[^\s"<>]+\.pdf'
            for match in re.finditer(pdf_pattern, content, re.IGNORECASE):
                url = match.group(0)
                if "google" not in url.lower() and url not in self.seen_urls:
                    urls.append(url)

            self.stealth.reset_backoff()

        except Exception as e:
            logger.debug(f"[gdrive] Search error: {e}")

        return urls

    def _process_url(self, url: str, query: str):
        """Process a found URL — download if it's a valid file."""
        if url in self.seen_urls:
            return
        self.seen_urls.add(url)

        if self.dedup.is_duplicate(source_url=url):
            self.status.record_duplicate()
            return

        self.status.record_post_scanned("gdrive")

        metadata = {
            "post_title": f"Google search: {query[:100]}",
            "post_url": url,
            "post_text": f"Found via search query: {query}",
        }

        quote_file = download_file(url, SourceType.GDRIVE, metadata)
        if quote_file:
            self.dedup.mark_seen(
                file_hash=quote_file.file_hash,
                source="gdrive",
                source_url=url,
                file_type=quote_file.file_type,
                file_size=quote_file.file_size,
                file_path=quote_file.file_path,
            )
            self.collected_files.append(quote_file)

            if quote_file.file_extension == ".pdf":
                self.status.record_pdf_found("gdrive")
            else:
                self.status.record_image_found("gdrive")
            self.status.record_download("gdrive")

    def close(self):
        pass
