"""Reddit Image/PDF Scraper — Finds contractor quote images and documents on Reddit.

Extends the existing Reddit scraper to focus on posts with IMAGE and PDF attachments,
not just text quotes. Uses Reddit's JSON API (no auth needed).
"""

import re
import json
import time
import logging
import hashlib
import requests as req
from datetime import datetime, timezone
from typing import List, Optional, Set
import threading

from ..config import (
    SUBREDDITS, REDDIT_SEARCH_TERMS, RATE_LIMITS,
    IMAGE_URL_PATTERN, PDF_URL_PATTERN,
    GDRIVE_URL_PATTERN, DROPBOX_URL_PATTERN,
    IMGUR_URL_PATTERN, REDDIT_IMAGE_PATTERN,
)
from ..models import QuoteFile, SourceType, ScrapeResult
from ..extraction.downloader import download_file, extract_urls_from_text
from ..extraction.dedup import ImageDedupEngine
from ..status import ImageScraperStatus
from ..utils.stealth import StealthManager

logger = logging.getLogger(__name__)

# Reddit-specific headers
REDDIT_UAS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]


class RedditImageScraper:
    """Scrapes contractor quote images/PDFs from Reddit."""

    def __init__(self, dedup: ImageDedupEngine, status: ImageScraperStatus,
                 shutdown_event: Optional[threading.Event] = None):
        self.dedup = dedup
        self.status = status
        self.shutdown_event = shutdown_event
        self.stealth = StealthManager("reddit", shutdown_event)
        self.collected_files: List[QuoteFile] = []
        self.seen_post_ids: Set[str] = set()
        self.seen_urls: Set[str] = set()
        self._ua_index = 0
        self._consecutive_errors = 0

    def run(self, max_files: int = 200, subreddits: List[str] = None) -> ScrapeResult:
        """Run the Reddit image scraper."""
        self.status.init_source("reddit")
        subreddits = subreddits or SUBREDDITS
        result = ScrapeResult(source=SourceType.REDDIT)
        start_time = time.time()

        sort_types = ["hot", "new", "top"]
        time_filters = {"top": ["year", "all"]}

        for subreddit in subreddits:
            if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                break

            for sort in sort_types:
                if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                    break

                filters = time_filters.get(sort, [None])
                for time_filter in filters:
                    if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                        break

                    logger.info(f"[reddit] Browsing r/{subreddit}/{sort}"
                                f"{f'?t={time_filter}' if time_filter else ''} "
                                f"({len(self.collected_files)}/{max_files} files)")

                    try:
                        self._browse_listing(subreddit, sort, time_filter, max_files)
                    except Exception as e:
                        logger.error(f"[reddit] Error in r/{subreddit}/{sort}: {e}")
                        self.status.record_error("reddit")

        result.status = "done"
        result.files_downloaded = len(self.collected_files)
        result.files = self.collected_files
        result.elapsed_seconds = time.time() - start_time
        self.status.set_source_status("reddit", "done")
        return result

    def _fetch_json(self, url: str) -> Optional[dict]:
        """Fetch a URL as JSON from Reddit."""
        if self.stealth.should_stop():
            return None

        self.stealth.rate_limit()
        self.status.set_last_url("reddit", url)

        self._ua_index = (self._ua_index + 1) % len(REDDIT_UAS)
        headers = {"User-Agent": REDDIT_UAS[self._ua_index]}

        try:
            resp = req.get(url, headers=headers, timeout=30, allow_redirects=True)

            if resp.status_code == 429:
                logger.warning("[reddit] Rate limited (429)")
                self.status.record_error("reddit")
                self.stealth.backoff()
                return None

            if resp.status_code == 403:
                self._consecutive_errors += 1
                if self._consecutive_errors > 5:
                    logger.warning("[reddit] Too many 403s, backing off longer")
                    self.stealth.interruptible_sleep(60)
                self.stealth.backoff()
                return None

            if resp.status_code != 200:
                logger.debug(f"[reddit] HTTP {resp.status_code}: {url}")
                return None

            self._consecutive_errors = 0
            self.stealth.reset_backoff()
            return resp.json()

        except (req.exceptions.Timeout, req.exceptions.ConnectionError) as e:
            logger.debug(f"[reddit] Connection issue: {e}")
            self.stealth.backoff()
            return None
        except (json.JSONDecodeError, ValueError):
            logger.debug(f"[reddit] Invalid JSON: {url}")
            return None

    def _browse_listing(self, subreddit: str, sort: str,
                        time_filter: Optional[str], max_files: int):
        """Browse a subreddit listing for posts with image/PDF attachments."""
        after = None
        pages = 0
        max_pages = 15

        while pages < max_pages:
            if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                break

            url = f"https://old.reddit.com/r/{subreddit}/{sort}.json?limit=25"
            if time_filter:
                url += f"&t={time_filter}"
            if after:
                url += f"&after={after}"

            data = self._fetch_json(url)
            if not data:
                break

            posts = data.get("data", {}).get("children", [])
            if not posts:
                break

            image_posts_found = 0
            for post_data in posts:
                if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                    break

                try:
                    post = post_data.get("data", {})
                    found = self._process_post(post, subreddit)
                    if found:
                        image_posts_found += 1
                except Exception as e:
                    logger.debug(f"[reddit] Error processing post: {e}")

            after = data.get("data", {}).get("after")
            if not after:
                break
            pages += 1

            # Skip ahead if no relevant content
            if image_posts_found == 0 and pages > 3:
                break

    def _process_post(self, post: dict, subreddit: str) -> bool:
        """Process a Reddit post for image/PDF attachments. Returns True if found any."""
        post_id = post.get("id", "")
        if not post_id or post_id in self.seen_post_ids:
            return False
        self.seen_post_ids.add(post_id)

        title = post.get("title", "") or ""
        selftext = post.get("selftext", "") or ""
        post_url_field = post.get("url", "") or ""
        permalink = post.get("permalink", "")
        full_url = f"https://www.reddit.com{permalink}" if permalink else ""

        combined_text = f"{title}\n{selftext}"
        text_lower = combined_text.lower()

        # Check if post is quote-related
        is_quote_related = any(term in text_lower for term in REDDIT_SEARCH_TERMS)
        has_dollar = bool(re.search(r'\$\d', combined_text))

        if not (is_quote_related or has_dollar):
            return False

        self.status.record_post_scanned("reddit")
        found_files = False

        # Check 1: Direct image/PDF post URL
        if post_url_field and self._has_file_attachment(post_url_field):
            metadata = {
                "post_title": title,
                "post_url": full_url,
                "post_text": combined_text[:500],
                "subreddit": subreddit,
                "date_posted": self._get_post_date(post),
            }
            if self._download_url(post_url_field, metadata, subreddit):
                found_files = True

        # Check 2: URLs in selftext
        file_urls = extract_urls_from_text(selftext)
        for url in file_urls:
            if self.stealth.should_stop():
                break
            metadata = {
                "post_title": title,
                "post_url": full_url,
                "post_text": combined_text[:500],
                "subreddit": subreddit,
                "date_posted": self._get_post_date(post),
            }
            if self._download_url(url, metadata, subreddit):
                found_files = True

        # Check 3: Reddit gallery posts
        if post.get("is_gallery"):
            gallery_data = post.get("media_metadata", {})
            for media_id, media_info in gallery_data.items():
                if self.stealth.should_stop():
                    break
                img_url = self._extract_gallery_url(media_info)
                if img_url:
                    metadata = {
                        "post_title": title,
                        "post_url": full_url,
                        "post_text": combined_text[:500],
                        "subreddit": subreddit,
                        "date_posted": self._get_post_date(post),
                    }
                    if self._download_url(img_url, metadata, subreddit):
                        found_files = True

        # Check 4: Reddit preview images
        preview = post.get("preview", {})
        if preview:
            images = preview.get("images", [])
            for img in images:
                source = img.get("source", {})
                img_url = source.get("url", "").replace("&amp;", "&")
                if img_url and is_quote_related:
                    metadata = {
                        "post_title": title,
                        "post_url": full_url,
                        "post_text": combined_text[:500],
                        "subreddit": subreddit,
                        "date_posted": self._get_post_date(post),
                    }
                    if self._download_url(img_url, metadata, subreddit):
                        found_files = True

        # Check 5: Comments (look for file links)
        num_comments = post.get("num_comments", 0)
        if num_comments and num_comments > 0 and is_quote_related:
            self._check_comments(post_id, subreddit, title, full_url, combined_text)

        return found_files

    def _has_file_attachment(self, url: str) -> bool:
        """Check if a URL points to an image or document."""
        if not url:
            return False
        url_lower = url.lower()

        # Direct image links
        if any(url_lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf"]):
            return True

        # Reddit images
        if "i.redd.it" in url_lower or "preview.redd.it" in url_lower:
            return True

        # Imgur
        if "imgur.com" in url_lower:
            return True

        # Google Drive / Dropbox
        if "drive.google.com" in url_lower or "dropbox.com" in url_lower:
            return True

        return False

    def _download_url(self, url: str, metadata: dict, subreddit: str) -> bool:
        """Download a file URL. Returns True if successful."""
        if url in self.seen_urls:
            return False
        self.seen_urls.add(url)

        if self.dedup.is_duplicate(source_url=url):
            self.status.record_duplicate()
            return False

        quote_file = download_file(url, SourceType.REDDIT, metadata)
        if quote_file:
            quote_file.subreddit = subreddit
            self.dedup.mark_seen(
                file_hash=quote_file.file_hash,
                source="reddit",
                source_url=url,
                file_type=quote_file.file_type,
                file_size=quote_file.file_size,
                file_path=quote_file.file_path,
            )
            self.collected_files.append(quote_file)

            if quote_file.file_extension in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                self.status.record_image_found("reddit")
            else:
                self.status.record_pdf_found("reddit")
            self.status.record_download("reddit")
            return True

        return False

    def _check_comments(self, post_id: str, subreddit: str,
                        title: str, post_url: str, post_text: str):
        """Check post comments for file links."""
        url = f"https://old.reddit.com/r/{subreddit}/comments/{post_id}.json?limit=50&depth=2"
        data = self._fetch_json(url)
        if not data or not isinstance(data, list) or len(data) < 2:
            return

        comments = data[1].get("data", {}).get("children", [])
        self._scan_comments(comments, subreddit, title, post_url, post_text)

    def _scan_comments(self, comments: list, subreddit: str,
                       title: str, post_url: str, post_text: str):
        """Recursively scan comments for file links."""
        for comment_data in comments:
            if self.stealth.should_stop():
                return

            comment = comment_data.get("data", {})
            if comment_data.get("kind") != "t1":
                continue

            body = comment.get("body", "") or ""
            file_urls = extract_urls_from_text(body)

            for url in file_urls:
                metadata = {
                    "post_title": title,
                    "post_url": post_url,
                    "post_text": f"{post_text[:200]}\n---\nComment: {body[:300]}",
                    "subreddit": subreddit,
                    "date_posted": self._get_comment_date(comment),
                }
                self._download_url(url, metadata, subreddit)

            # Recurse into replies
            replies = comment.get("replies")
            if isinstance(replies, dict):
                reply_children = replies.get("data", {}).get("children", [])
                self._scan_comments(reply_children, subreddit, title, post_url, post_text)

    def _extract_gallery_url(self, media_info: dict) -> Optional[str]:
        """Extract the best image URL from Reddit gallery metadata."""
        if not media_info:
            return None

        # Try the source (highest quality)
        source = media_info.get("s", {})
        url = source.get("u") or source.get("gif")
        if url:
            return url.replace("&amp;", "&")

        return None

    def _get_post_date(self, post: dict) -> str:
        created_utc = post.get("created_utc", 0)
        if created_utc:
            return datetime.fromtimestamp(created_utc, tz=timezone.utc).isoformat()
        return ""

    def _get_comment_date(self, comment: dict) -> str:
        created_utc = comment.get("created_utc", 0)
        if created_utc:
            return datetime.fromtimestamp(created_utc, tz=timezone.utc).isoformat()
        return ""

    def close(self):
        pass
