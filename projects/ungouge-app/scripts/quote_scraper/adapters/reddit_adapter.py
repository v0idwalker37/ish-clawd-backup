"""Reddit adapter — uses Reddit's JSON API (no auth needed for read)."""

import json
import logging
import re
import time
import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Set

from .base_adapter import BaseAdapter
from ..models import RawQuote, ExtractedQuote
from ..config import SUBREDDITS, SEARCH_TERMS, REDDIT_DELAY, RESUME_FILE
from ..dedup import DedupEngine
from ..status import StatusTracker

logger = logging.getLogger(__name__)


class RedditAdapter(BaseAdapter):
    """Scrape contractor quotes from Reddit using the JSON API.
    
    Strategy: Since Reddit's search.json requires auth, we use:
    1. Subreddit listings (hot, new, top) — paginate through posts
    2. Filter posts locally by search terms
    3. Fetch comments for posts that contain dollar amounts
    """

    SOURCE_NAME = "reddit"
    BASE_DELAY = REDDIT_DELAY

    def __init__(self, dedup: DedupEngine, status: StatusTracker, 
                 shutdown_event=None):
        super().__init__(dedup, status, shutdown_event)
        self.seen_post_ids: Set[str] = set()
        self._consecutive_403s = 0
        # Reddit detects session cookies for anti-bot — don't use session
        self.session.close()
        self.session = None  # We'll use requests.get() directly

    _REDDIT_UAS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def _get_headers(self) -> dict:
        """Reddit needs browser-like headers for JSON API."""
        self._ua_index = (self._ua_index + 1) % len(self._REDDIT_UAS)
        return {
            "User-Agent": self._REDDIT_UAS[self._ua_index],
        }

    def fetch_url(self, url, json_mode=False, allow_redirects=True):
        """Override to use direct requests.get() instead of session.
        
        Reddit's anti-bot tracks session cookies — using stateless requests avoids this.
        """
        import requests as req

        if self.should_stop():
            return None

        self._rate_limit()
        self.status.record_request(self.SOURCE_NAME)
        self.status.set_last_url(self.SOURCE_NAME, url)

        try:
            headers = self._get_headers()
            resp = req.get(url, headers=headers, timeout=30, 
                          allow_redirects=allow_redirects)

            if resp.status_code == 429:
                logger.warning(f"[reddit] Rate limited (429): {url}")
                self.status.record_error(self.SOURCE_NAME)
                self._backoff()
                return None

            if resp.status_code == 403:
                logger.warning(f"[reddit] Forbidden (403): {url}")
                self.status.record_error(self.SOURCE_NAME)
                self._backoff()
                return None

            if resp.status_code == 404:
                logger.debug(f"[reddit] Not found: {url}")
                return None

            if resp.status_code >= 400:
                logger.warning(f"[reddit] HTTP {resp.status_code}: {url}")
                self.status.record_error(self.SOURCE_NAME)
                return None

            self._reset_backoff()
            return resp

        except req.exceptions.Timeout:
            logger.warning(f"[reddit] Timeout: {url}")
            self.status.record_error(self.SOURCE_NAME)
            return None
        except req.exceptions.ConnectionError:
            logger.warning(f"[reddit] Connection error: {url}")
            self.status.record_error(self.SOURCE_NAME)
            self._backoff()
            return None
        except Exception as e:
            logger.error(f"[reddit] Fetch error: {e}")
            self.status.record_error(self.SOURCE_NAME)
            return None

    def close(self):
        """No session to close."""
        pass

    def run(self, max_quotes: int = 1000) -> List[ExtractedQuote]:
        """Scrape Reddit for contractor quotes."""
        logger.info(f"[reddit] Starting Reddit scraper (max {max_quotes} quotes)")
        self.status.init_source("reddit")

        resume_state = self._load_resume_state()
        completed_listings = set(resume_state.get("completed_listings", []))

        # Strategy: iterate subreddits x sort_types, paginate each
        sort_types = ["hot", "new", "top"]
        time_filters = {"top": ["year", "all"]}  # top needs time filter

        for subreddit in SUBREDDITS:
            if self.should_stop() or len(self.collected_quotes) >= max_quotes:
                break

            for sort in sort_types:
                if self.should_stop() or len(self.collected_quotes) >= max_quotes:
                    break

                filters = time_filters.get(sort, [None])
                for time_filter in filters:
                    listing_key = f"{subreddit}:{sort}:{time_filter or 'none'}"
                    if listing_key in completed_listings:
                        logger.debug(f"[reddit] Skipping completed: {listing_key}")
                        continue

                    if self.should_stop() or len(self.collected_quotes) >= max_quotes:
                        break

                    logger.info(f"[reddit] Browsing r/{subreddit}/{sort}"
                               f"{f'?t={time_filter}' if time_filter else ''} "
                               f"({len(self.collected_quotes)}/{max_quotes} quotes)")

                    try:
                        self._browse_listing(subreddit, sort, time_filter, max_quotes)
                        completed_listings.add(listing_key)
                        self._save_resume_state(list(completed_listings))
                    except Exception as e:
                        logger.error(f"[reddit] Error browsing r/{subreddit}/{sort}: {e}")
                        self.status.record_error("reddit")

        logger.info(f"[reddit] Finished. Collected {len(self.collected_quotes)} quotes")
        self.status.set_source_status("reddit", "done")
        return self.collected_quotes

    def _browse_listing(self, subreddit: str, sort: str, 
                        time_filter: Optional[str], max_quotes: int):
        """Browse a subreddit listing and process posts with quote-related content."""
        after = None
        pages = 0
        max_pages = 15  # ~375 posts per listing

        while pages < max_pages:
            if self.should_stop() or len(self.collected_quotes) >= max_quotes:
                break

            url = f"https://old.reddit.com/r/{subreddit}/{sort}.json?limit=25"
            if time_filter:
                url += f"&t={time_filter}"
            if after:
                url += f"&after={after}"

            resp = self.fetch_url(url, json_mode=True)
            if not resp:
                # Retry once after a longer pause for Reddit's intermittent 403s
                self._consecutive_403s += 1
                if self._consecutive_403s <= 3:
                    logger.info(f"[reddit] Retrying after pause (attempt {self._consecutive_403s})")
                    self._interruptible_sleep(15)
                    resp = self.fetch_url(url, json_mode=True)
                if not resp:
                    if self._consecutive_403s > 5:
                        logger.warning("[reddit] Too many consecutive failures, stopping listing")
                        break
                    continue
            else:
                self._consecutive_403s = 0

            try:
                data = resp.json()
            except (json.JSONDecodeError, ValueError):
                logger.warning(f"[reddit] Invalid JSON from listing: {url}")
                break

            posts = data.get("data", {}).get("children", [])
            if not posts:
                break

            quote_posts_found = 0
            for post_data in posts:
                if self.should_stop() or len(self.collected_quotes) >= max_quotes:
                    break

                try:
                    post = post_data.get("data", {})
                    # Local filter: check if post mentions quote-related terms
                    title = (post.get("title", "") or "").lower()
                    selftext = (post.get("selftext", "") or "").lower()
                    combined = title + " " + selftext

                    # Must match at least one search term
                    has_term = any(term in combined for term in SEARCH_TERMS)
                    # Or has a dollar amount
                    has_dollar = bool(re.search(r'\$\d', combined) or
                                    re.search(r'\d+k\b', combined))

                    if has_term or has_dollar:
                        quote_posts_found += 1
                        self._process_post(post, subreddit)

                except Exception as e:
                    logger.error(f"[reddit] Error processing post: {e}")

            # Pagination
            after = data.get("data", {}).get("after")
            if not after:
                break

            pages += 1

            # If we went through a full page with no relevant posts, skip ahead
            if quote_posts_found == 0 and pages > 3:
                logger.debug(f"[reddit] No relevant posts in page {pages}, stopping listing")
                break

    def _process_post(self, post: dict, subreddit: str):
        """Process a single Reddit post and its comments."""
        post_id = post.get("id", "")
        if not post_id or post_id in self.seen_post_ids:
            return
        self.seen_post_ids.add(post_id)

        # Check if post is too old (>2 years)
        created_utc = post.get("created_utc", 0)
        if created_utc:
            post_age_days = (time.time() - created_utc) / 86400
            if post_age_days > 730:  # 2 years
                return

        # Build raw text from title + selftext
        title = post.get("title", "") or ""
        selftext = post.get("selftext", "") or ""
        full_text = f"{title}\n\n{selftext}".strip()

        if len(full_text) < 30:
            return

        # Check for dollar amounts before creating RawQuote (quick filter)
        has_dollar = bool(re.search(r'\$\d', full_text) or 
                         re.search(r'\d+k\b', full_text, re.I))

        if has_dollar:
            permalink = post.get("permalink", "")
            source_url = f"https://www.reddit.com{permalink}" if permalink else ""

            date_posted = ""
            if created_utc:
                date_posted = datetime.fromtimestamp(
                    created_utc, tz=timezone.utc
                ).isoformat()

            raw = RawQuote(
                source="reddit",
                source_url=source_url,
                source_id=post_id,
                raw_text=full_text[:5000],  # Cap at 5000 chars
                author="anon",  # Don't store usernames
                date_posted=date_posted,
                date_collected=datetime.utcnow().isoformat(),
            )

            self.process_raw_quote(raw)

        # Also fetch comments for this post (people share quotes in replies)
        num_comments = post.get("num_comments", 0)
        if num_comments and num_comments > 0:
            self._fetch_comments(post_id, subreddit)

    def _fetch_comments(self, post_id: str, subreddit: str):
        """Fetch and process comments for a post."""
        url = f"https://old.reddit.com/r/{subreddit}/comments/{post_id}.json?limit=100&depth=3"

        resp = self.fetch_url(url, json_mode=True)
        if not resp:
            return

        try:
            data = resp.json()
        except (json.JSONDecodeError, ValueError):
            return

        if not isinstance(data, list) or len(data) < 2:
            return

        # data[1] contains comments
        comments = data[1].get("data", {}).get("children", [])
        self._process_comments(comments, post_id, subreddit)

    def _process_comments(self, comments: list, post_id: str, subreddit: str):
        """Recursively process comments."""
        for comment_data in comments:
            if self.should_stop():
                return

            comment = comment_data.get("data", {})
            if comment_data.get("kind") != "t1":
                continue

            body = comment.get("body", "") or ""
            if len(body) < 30:
                continue

            # Quick filter: does it contain dollar amounts?
            has_dollar = bool(re.search(r'\$\d', body) or 
                            re.search(r'\d+k\b', body, re.I))

            if has_dollar:
                comment_id = comment.get("id", "")
                full_id = f"{post_id}_{comment_id}"

                if full_id not in self.seen_post_ids:
                    self.seen_post_ids.add(full_id)

                    created_utc = comment.get("created_utc", 0)
                    date_posted = ""
                    if created_utc:
                        date_posted = datetime.fromtimestamp(
                            created_utc, tz=timezone.utc
                        ).isoformat()

                    permalink = comment.get("permalink", "")
                    source_url = f"https://www.reddit.com{permalink}" if permalink else ""

                    raw = RawQuote(
                        source="reddit",
                        source_url=source_url,
                        source_id=full_id,
                        raw_text=body[:5000],
                        author="anon",
                        date_posted=date_posted,
                        date_collected=datetime.utcnow().isoformat(),
                    )

                    self.process_raw_quote(raw)

            # Process replies regardless
            replies = comment.get("replies")
            if isinstance(replies, dict):
                reply_children = replies.get("data", {}).get("children", [])
                self._process_comments(reply_children, post_id, subreddit)

    def _load_resume_state(self) -> dict:
        """Load resume state from file."""
        import os
        if os.path.exists(RESUME_FILE):
            try:
                with open(RESUME_FILE, "r") as f:
                    state = json.load(f)
                return state.get("reddit", {})
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_resume_state(self, completed_listings: list):
        """Save resume state to file."""
        import os
        state = {}
        if os.path.exists(RESUME_FILE):
            try:
                with open(RESUME_FILE, "r") as f:
                    state = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        state["reddit"] = {
            "completed_listings": completed_listings,
            "last_updated": datetime.utcnow().isoformat(),
        }

        os.makedirs(os.path.dirname(RESUME_FILE), exist_ok=True)
        try:
            with open(RESUME_FILE, "w") as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            logger.error(f"[reddit] Error saving resume state: {e}")
