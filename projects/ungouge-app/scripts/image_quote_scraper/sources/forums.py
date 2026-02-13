"""Contractor Forum Scraper — Scrapes images/PDFs from contractor forums.

Targets: ContractorTalk.com, DIYChatroom.com, HouseRepairTalk.com,
Terry Love Plumbing forums, GardenWeb forums.

Uses requests + BeautifulSoup (simpler than Playwright for forums).
"""

import re
import time
import logging
import requests as req
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse
import threading

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from ..config import FORUM_TARGETS, IMAGE_EXTENSIONS, DOCUMENT_EXTENSIONS
from ..models import QuoteFile, SourceType, ScrapeResult
from ..extraction.downloader import download_file, extract_urls_from_text
from ..extraction.dedup import ImageDedupEngine
from ..status import ImageScraperStatus
from ..utils.stealth import StealthManager

logger = logging.getLogger(__name__)

# Quote-related keywords for searching forums
QUOTE_KEYWORDS = [
    "quote", "estimate", "bid", "cost breakdown",
    "is this fair", "overpriced", "how much should",
    "contractor charged", "got quoted",
]


class ForumScraper:
    """Scrapes contractor forums for quote images and documents."""

    def __init__(self, dedup: ImageDedupEngine, status: ImageScraperStatus,
                 shutdown_event: Optional[threading.Event] = None):
        self.dedup = dedup
        self.status = status
        self.shutdown_event = shutdown_event
        self.stealth = StealthManager("forums", shutdown_event)
        self.collected_files: List[QuoteFile] = []
        self.seen_urls: Set[str] = set()
        self.session = req.Session()

    def run(self, max_files: int = 75) -> ScrapeResult:
        """Run the forum scraper."""
        if BeautifulSoup is None:
            logger.error("[forums] BeautifulSoup not installed. pip install beautifulsoup4")
            return ScrapeResult(source=SourceType.FORUMS, status="dependency_missing")

        self.status.init_source("forums")
        result = ScrapeResult(source=SourceType.FORUMS)
        start_time = time.time()

        for forum_name, forum_config in FORUM_TARGETS.items():
            if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                break

            logger.info(f"[forums] Scraping {forum_name}...")

            try:
                self._scrape_forum(forum_name, forum_config, max_files)
                self.status.record_group_done("forums")
            except Exception as e:
                logger.error(f"[forums] Error scraping {forum_name}: {e}")
                self.status.record_error("forums")

            # Break between forums
            self.stealth.random_delay(5, 15)

        result.status = "done"
        result.files_downloaded = len(self.collected_files)
        result.files = self.collected_files
        result.elapsed_seconds = time.time() - start_time
        self.status.set_source_status("forums", "done")
        return result

    def _scrape_forum(self, forum_name: str, config: dict, max_files: int):
        """Scrape a single forum."""
        base_url = config["base_url"]
        keywords = config.get("keywords", QUOTE_KEYWORDS)

        # Strategy 1: Search the forum for quote-related threads
        for keyword in keywords:
            if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                break

            thread_urls = self._search_forum(base_url, keyword, forum_name)
            logger.info(f"[forums] {forum_name}: '{keyword}' → {len(thread_urls)} threads")

            for thread_url in thread_urls[:20]:  # Max 20 threads per keyword
                if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                    break

                self._scrape_thread(thread_url, forum_name)

    def _search_forum(self, base_url: str, keyword: str, forum_name: str) -> List[str]:
        """Search a forum for threads matching a keyword. Returns thread URLs."""
        urls = []

        # Use Google site-specific search (more reliable than forum search)
        from urllib.parse import quote_plus
        domain = urlparse(base_url).netloc
        search_query = f'site:{domain} "{keyword}" image OR pdf OR attachment'
        google_url = f"https://www.google.com/search?q={quote_plus(search_query)}&num=20"

        headers = self.stealth.get_headers()
        self.stealth.rate_limit()

        try:
            resp = self.session.get(google_url, headers=headers, timeout=30)
            if resp.status_code == 200:
                # Extract forum thread URLs from Google results
                pattern = rf'https?://{re.escape(domain)}/[^\s"<>]+'
                for match in re.finditer(pattern, resp.text):
                    url = match.group(0).rstrip('"').rstrip("'")
                    # Filter to thread-like URLs
                    if self._looks_like_thread(url):
                        urls.append(url)
            elif resp.status_code == 429:
                logger.warning("[forums] Google rate limited, backing off")
                self.stealth.backoff()
        except Exception as e:
            logger.debug(f"[forums] Search error for {forum_name}: {e}")

        # Deduplicate
        return list(dict.fromkeys(urls))

    def _looks_like_thread(self, url: str) -> bool:
        """Check if a URL looks like a forum thread (vs. category page, etc.)."""
        url_lower = url.lower()
        # Common thread URL patterns
        thread_indicators = [
            "/threads/", "/topic/", "/t/",
            "/showthread", "/viewtopic",
            "/index.php?topic=",
            "-thread-", "/discussion/",
        ]
        return any(ind in url_lower for ind in thread_indicators)

    def _scrape_thread(self, thread_url: str, forum_name: str):
        """Scrape a single forum thread for image/document attachments."""
        if thread_url in self.seen_urls:
            return
        self.seen_urls.add(thread_url)

        headers = self.stealth.get_headers()
        self.stealth.rate_limit()
        self.status.set_last_url("forums", thread_url)
        self.status.record_post_scanned("forums")

        try:
            resp = self.session.get(thread_url, headers=headers, timeout=30)
            if resp.status_code != 200:
                return

            soup = BeautifulSoup(resp.text, "html.parser")
            base_url = f"{urlparse(thread_url).scheme}://{urlparse(thread_url).netloc}"

            # Extract thread title
            title = ""
            title_tag = soup.find("h1") or soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)

            # Find all images in the thread
            for img in soup.find_all("img"):
                if self.stealth.should_stop():
                    return

                src = img.get("src") or img.get("data-src") or ""
                if not src:
                    continue

                # Make absolute URL
                if src.startswith("/"):
                    src = urljoin(base_url, src)
                elif not src.startswith("http"):
                    continue

                # Filter out icons, avatars, smileys
                if self._is_content_image(src):
                    metadata = {
                        "post_title": title,
                        "post_url": thread_url,
                        "forum_name": forum_name,
                    }
                    self._download_url(src, metadata, forum_name)

            # Find all links to files (PDF, DOCX, etc.)
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if not href:
                    continue

                # Make absolute
                if href.startswith("/"):
                    href = urljoin(base_url, href)
                elif not href.startswith("http"):
                    continue

                link_text = link.get_text(strip=True).lower()

                # Check for file links
                if self._is_file_link(href, link_text):
                    metadata = {
                        "post_title": title,
                        "post_url": thread_url,
                        "forum_name": forum_name,
                    }
                    self._download_url(href, metadata, forum_name)

            # Also check for embedded file URLs in post text
            for post_div in soup.find_all(class_=re.compile(r'post|message|content', re.I)):
                text = post_div.get_text()
                file_urls = extract_urls_from_text(text)
                for url in file_urls:
                    metadata = {
                        "post_title": title,
                        "post_url": thread_url,
                        "post_text": text[:500],
                        "forum_name": forum_name,
                    }
                    self._download_url(url, metadata, forum_name)

        except Exception as e:
            logger.debug(f"[forums] Error scraping thread {thread_url}: {e}")

    def _is_content_image(self, src: str) -> bool:
        """Check if an image URL is a real content image."""
        src_lower = src.lower()
        skip_patterns = [
            "avatar", "icon", "smiley", "emoji", "emoticon",
            "logo", "banner", "sprite", "button", "badge",
            "placeholder", "loading", "pixel", "spacer",
            "thumb_", "/icons/", "/smilies/",
        ]
        if any(pat in src_lower for pat in skip_patterns):
            return False

        # Must have an image extension or be from a known CDN
        parsed = urlparse(src)
        path = parsed.path.lower()
        if any(path.endswith(ext) for ext in IMAGE_EXTENSIONS):
            return True

        # Forum attachment URLs
        if "attachment" in src_lower or "upload" in src_lower:
            return True

        return False

    def _is_file_link(self, href: str, text: str) -> bool:
        """Check if a link points to a downloadable file."""
        href_lower = href.lower()
        # Direct file extensions
        if any(href_lower.endswith(ext) for ext in DOCUMENT_EXTENSIONS | IMAGE_EXTENSIONS):
            return True
        # Attachment download links
        if "attachment" in href_lower or "download" in href_lower:
            return True
        # Cloud storage links
        if "drive.google.com" in href_lower or "dropbox.com" in href_lower:
            return True
        # Text hints
        if any(kw in text for kw in ["pdf", "download", "attachment", "file"]):
            return True
        return False

    def _download_url(self, url: str, metadata: dict, forum_name: str):
        """Download a file URL."""
        if url in self.seen_urls:
            return
        self.seen_urls.add(url)

        if self.dedup.is_duplicate(source_url=url):
            self.status.record_duplicate()
            return

        quote_file = download_file(url, SourceType.FORUMS, metadata)
        if quote_file:
            quote_file.forum_name = forum_name
            self.dedup.mark_seen(
                file_hash=quote_file.file_hash,
                source="forums",
                source_url=url,
                file_type=quote_file.file_type,
                file_size=quote_file.file_size,
                file_path=quote_file.file_path,
            )
            self.collected_files.append(quote_file)

            if quote_file.file_extension in IMAGE_EXTENSIONS:
                self.status.record_image_found("forums")
            else:
                self.status.record_pdf_found("forums")
            self.status.record_download("forums")

    def close(self):
        self.session.close()
