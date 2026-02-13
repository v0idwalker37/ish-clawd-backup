"""YouTube Comment Scraper — Extracts file links from home improvement video comments.

Strategy: Search for home improvement videos, scan comments for Google Drive/Imgur
links to contractor quotes.

Uses YouTube's public HTML pages (no API key required, though we support the API).
"""

import re
import time
import logging
import requests as req
from typing import List, Optional, Set
from urllib.parse import quote_plus
import threading
import json

from ..config import YOUTUBE_CHANNELS, YOUTUBE_SEARCH_TERMS
from ..models import QuoteFile, SourceType, ScrapeResult
from ..extraction.downloader import download_file, extract_urls_from_text
from ..extraction.dedup import ImageDedupEngine
from ..status import ImageScraperStatus
from ..utils.stealth import StealthManager

logger = logging.getLogger(__name__)

# YouTube Data API key (optional)
YOUTUBE_API_KEY = ""  # Set if available


class YouTubeScraper:
    """Scrapes YouTube comments for contractor quote file links."""

    def __init__(self, dedup: ImageDedupEngine, status: ImageScraperStatus,
                 shutdown_event: Optional[threading.Event] = None):
        self.dedup = dedup
        self.status = status
        self.shutdown_event = shutdown_event
        self.stealth = StealthManager("youtube", shutdown_event)
        self.collected_files: List[QuoteFile] = []
        self.seen_urls: Set[str] = set()
        self.seen_video_ids: Set[str] = set()

    def run(self, max_files: int = 20) -> ScrapeResult:
        """Run the YouTube scraper."""
        self.status.init_source("youtube")
        result = ScrapeResult(source=SourceType.YOUTUBE)
        start_time = time.time()

        # Strategy: Search YouTube for home improvement videos, then check comments
        for search_term in YOUTUBE_SEARCH_TERMS:
            if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                break

            logger.info(f"[youtube] Searching: {search_term}")

            try:
                video_ids = self._search_videos(search_term)
                logger.info(f"[youtube] Found {len(video_ids)} videos")

                for video_id in video_ids[:10]:  # Max 10 videos per search
                    if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                        break

                    if video_id in self.seen_video_ids:
                        continue
                    self.seen_video_ids.add(video_id)

                    self._scan_video_comments(video_id, search_term)

            except Exception as e:
                logger.error(f"[youtube] Error searching '{search_term}': {e}")
                self.status.record_error("youtube")

            self.stealth.random_delay(3, 8)

        result.status = "done"
        result.files_downloaded = len(self.collected_files)
        result.files = self.collected_files
        result.elapsed_seconds = time.time() - start_time
        self.status.set_source_status("youtube", "done")
        return result

    def _search_videos(self, query: str) -> List[str]:
        """Search YouTube for video IDs."""
        video_ids = []
        encoded = quote_plus(query)

        # Use YouTube's search page
        url = f"https://www.youtube.com/results?search_query={encoded}"
        headers = self.stealth.get_headers()
        self.stealth.rate_limit()

        try:
            resp = req.get(url, headers=headers, timeout=30)
            if resp.status_code != 200:
                return []

            # Extract video IDs from page
            pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
            matches = re.findall(pattern, resp.text)

            # Deduplicate while preserving order
            seen = set()
            for vid in matches:
                if vid not in seen:
                    seen.add(vid)
                    video_ids.append(vid)
                    if len(video_ids) >= 20:
                        break

        except Exception as e:
            logger.debug(f"[youtube] Search error: {e}")

        return video_ids

    def _scan_video_comments(self, video_id: str, search_context: str):
        """Scan a video's comments for file links (Google Drive, Imgur, etc.)."""
        self.status.record_post_scanned("youtube")
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        self.status.set_last_url("youtube", video_url)

        # YouTube comments are loaded via XHR — we need to use the innertube API
        try:
            comments = self._fetch_comments_innertube(video_id)
            if not comments:
                return

            for comment_text in comments:
                if self.stealth.should_stop():
                    return

                # Look for file links in comments
                file_urls = extract_urls_from_text(comment_text)
                if not file_urls:
                    continue

                # Also check for keywords suggesting this is a quote
                text_lower = comment_text.lower()
                is_quote_related = any(kw in text_lower for kw in [
                    "quote", "estimate", "bid", "cost", "$",
                    "contractor", "price", "charged",
                ])

                if not is_quote_related:
                    continue

                for url in file_urls:
                    if self.stealth.should_stop():
                        return

                    metadata = {
                        "post_title": f"YouTube comment on video {video_id}",
                        "post_url": video_url,
                        "post_text": comment_text[:500],
                    }
                    self._download_url(url, metadata)

        except Exception as e:
            logger.debug(f"[youtube] Error scanning comments for {video_id}: {e}")

    def _fetch_comments_innertube(self, video_id: str) -> List[str]:
        """Fetch comments using YouTube's innertube API."""
        comments = []

        # First, get the continuation token from the video page
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = self.stealth.get_headers()
        self.stealth.rate_limit()

        try:
            resp = req.get(url, headers=headers, timeout=30)
            if resp.status_code != 200:
                return []

            # Extract initial comments data
            # YouTube embeds comment data in the initial page load
            pattern = r'"commentRenderer".*?"text":\{"runs":\[\{"text":"((?:[^"\\]|\\.)*)"\}'
            matches = re.findall(pattern, resp.text)

            for text in matches:
                # Unescape JSON string
                try:
                    unescaped = text.encode().decode('unicode_escape')
                    comments.append(unescaped)
                except Exception:
                    comments.append(text)

            # Also try to extract from ytInitialData
            yt_data_match = re.search(r'var ytInitialData = ({.*?});</script>', resp.text, re.DOTALL)
            if yt_data_match:
                try:
                    yt_data = json.loads(yt_data_match.group(1))
                    # Navigate the deeply nested comment structure
                    comments.extend(self._extract_comments_from_data(yt_data))
                except (json.JSONDecodeError, KeyError):
                    pass

        except Exception as e:
            logger.debug(f"[youtube] Error fetching comments: {e}")

        return comments[:100]  # Cap at 100 comments

    def _extract_comments_from_data(self, data: dict) -> List[str]:
        """Recursively extract comment text from YouTube's data structure."""
        comments = []

        if isinstance(data, dict):
            # Look for comment text
            if "contentText" in data:
                runs = data["contentText"].get("runs", [])
                text = "".join(r.get("text", "") for r in runs)
                if text:
                    comments.append(text)

            # Recurse
            for value in data.values():
                comments.extend(self._extract_comments_from_data(value))

        elif isinstance(data, list):
            for item in data:
                comments.extend(self._extract_comments_from_data(item))

        return comments

    def _download_url(self, url: str, metadata: dict):
        """Download a file URL from a YouTube comment."""
        if url in self.seen_urls:
            return
        self.seen_urls.add(url)

        if self.dedup.is_duplicate(source_url=url):
            self.status.record_duplicate()
            return

        quote_file = download_file(url, SourceType.YOUTUBE, metadata)
        if quote_file:
            self.dedup.mark_seen(
                file_hash=quote_file.file_hash,
                source="youtube",
                source_url=url,
                file_type=quote_file.file_type,
                file_size=quote_file.file_size,
                file_path=quote_file.file_path,
            )
            self.collected_files.append(quote_file)

            if quote_file.file_extension in {".jpg", ".jpeg", ".png", ".webp"}:
                self.status.record_image_found("youtube")
            else:
                self.status.record_pdf_found("youtube")
            self.status.record_download("youtube")

    def close(self):
        pass
