"""Facebook Group Scraper — Downloads quote images/PDFs from Facebook groups.

Uses Playwright for browser automation with aggressive anti-detection.
Strategy: Login → Navigate groups → Scroll posts → Detect images/PDFs → Download.
"""

import os
import re
import json
import time
import random
import logging
from datetime import datetime
from typing import List, Optional, Set
import threading

from ..config import (
    FACEBOOK_GROUPS, FACEBOOK_CREDS_FILE, FACEBOOK_COOKIES_FILE,
    FB_SCROLL_DELAY, FB_ACTION_DELAY, FB_MAX_SCROLLS_PER_GROUP,
    FB_SUSPICIOUS_PAUSE, BROWSER_TIMEOUT,
    load_facebook_creds,
)
from ..models import QuoteFile, SourceType, ScrapeResult
from ..extraction.downloader import download_file, extract_urls_from_text
from ..extraction.dedup import ImageDedupEngine
from ..status import ImageScraperStatus
from ..utils.stealth import StealthManager, human_like_scroll, simulate_reading_pause
from ..utils.browser import (
    create_browser, create_stealth_context,
    save_cookies, load_cookies, close_browser,
)

logger = logging.getLogger(__name__)

# Quote-related keywords to look for in posts
QUOTE_KEYWORDS = [
    "quote", "estimate", "bid", "cost", "price", "quoted",
    "contractor", "is this fair", "overpriced", "reasonable",
    "how much", "charges", "charging", "breakdown", "line item",
    "invoice", "proposal", "scope of work",
]

# Image patterns on Facebook
FB_IMAGE_SELECTORS = [
    'img[data-visualcompletion="media-vc-image"]',
    'img[class*="scaledImageFit"]',
    'div[data-pagelet*="Photo"] img',
    'a[href*="/photo"] img',
    'img[src*="scontent"]',
]


class FacebookScraper:
    """Scrapes contractor quote images from Facebook groups."""

    def __init__(self, dedup: ImageDedupEngine, status: ImageScraperStatus,
                 shutdown_event: Optional[threading.Event] = None,
                 headless: bool = False):
        self.dedup = dedup
        self.status = status
        self.shutdown_event = shutdown_event
        self.stealth = StealthManager("facebook", shutdown_event)
        self.headless = headless
        self.collected_files: List[QuoteFile] = []
        self.seen_urls: Set[str] = set()
        self.context = None
        self.page = None

    def run(self, max_files: int = 200, groups: List[str] = None) -> ScrapeResult:
        """Run the Facebook scraper."""
        self.status.init_source("facebook")
        groups = groups or FACEBOOK_GROUPS
        result = ScrapeResult(source=SourceType.FACEBOOK)
        start_time = time.time()

        if not groups:
            logger.warning("[facebook] No groups configured. Add groups to config.py")
            result.status = "no_groups"
            return result

        try:
            # Launch browser and login
            if not self._setup_browser():
                result.status = "login_failed"
                return result

            if not self._login():
                result.status = "login_failed"
                return result

            # Scrape each group
            for group in groups:
                if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                    break

                logger.info(f"[facebook] Scraping group: {group}")
                try:
                    self._scrape_group(group, max_files)
                    self.status.record_group_done("facebook")
                except Exception as e:
                    logger.error(f"[facebook] Error scraping group {group}: {e}")
                    self.status.record_error("facebook")

                # Break between groups
                if not self.stealth.should_stop():
                    self.stealth.random_delay(30, 90)

            result.status = "done"

        except Exception as e:
            logger.error(f"[facebook] Fatal error: {e}", exc_info=True)
            result.status = f"error: {str(e)[:100]}"
        finally:
            # Save cookies for next session
            if self.context:
                save_cookies(self.context)
            self._cleanup()

        result.files_downloaded = len(self.collected_files)
        result.files = self.collected_files
        result.elapsed_seconds = time.time() - start_time
        self.status.set_source_status("facebook", result.status)
        return result

    def _setup_browser(self) -> bool:
        """Set up Playwright browser."""
        try:
            browser = create_browser(headless=self.headless)
            self.context = create_stealth_context(browser)
            self.page = self.context.new_page()
            self.page.set_default_timeout(BROWSER_TIMEOUT)
            logger.info("[facebook] Browser ready")
            return True
        except Exception as e:
            logger.error(f"[facebook] Browser setup failed: {e}")
            return False

    def _login(self) -> bool:
        """Log in to Facebook, using saved cookies if available."""
        # Try cookies first
        if load_cookies(self.context):
            self.page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
            self.stealth.random_delay(3, 5)

            # Check if we're logged in
            if self._is_logged_in():
                logger.info("[facebook] Logged in via saved cookies")
                return True
            logger.info("[facebook] Cookies expired, logging in with credentials")

        # Load credentials
        creds = load_facebook_creds()
        if not creds.get("email") or not creds.get("password"):
            logger.error("[facebook] No Facebook credentials found. "
                         f"Create {FACEBOOK_CREDS_FILE} with email/password.")
            return False

        # Navigate to login page
        self.page.goto("https://www.facebook.com/login", wait_until="domcontentloaded")
        self.stealth.random_delay(2, 4)

        try:
            # Fill email
            email_input = self.page.locator("#email")
            email_input.click()
            self.stealth.random_delay(0.5, 1)
            email_input.type(creds["email"], delay=random.randint(50, 150))
            self.stealth.random_delay(0.5, 1.5)

            # Fill password
            pass_input = self.page.locator("#pass")
            pass_input.click()
            self.stealth.random_delay(0.3, 0.8)
            pass_input.type(creds["password"], delay=random.randint(50, 150))
            self.stealth.random_delay(0.5, 1)

            # Click login
            self.page.locator('button[name="login"]').click()
            self.stealth.random_delay(5, 8)

            # Check for 2FA or suspicious activity
            if self._check_for_challenges():
                return False

            if self._is_logged_in():
                logger.info("[facebook] Login successful")
                save_cookies(self.context)
                return True

            logger.error("[facebook] Login failed — could not verify logged-in state")
            return False

        except Exception as e:
            logger.error(f"[facebook] Login error: {e}")
            return False

    def _is_logged_in(self) -> bool:
        """Check if we're currently logged in to Facebook."""
        try:
            # Look for elements that only appear when logged in
            page_content = self.page.content()
            logged_in_indicators = [
                'aria-label="Your profile"',
                'aria-label="Account"',
                'aria-label="Messenger"',
                '/me/',
                'aria-label="Create"',
            ]
            return any(indicator in page_content for indicator in logged_in_indicators)
        except Exception:
            return False

    def _check_for_challenges(self) -> bool:
        """Check for 2FA, captcha, or suspicious activity challenges."""
        try:
            page_content = self.page.content().lower()

            # Check for 2FA
            if "two-factor" in page_content or "authentication code" in page_content:
                logger.error("[facebook] 2FA required! Please disable 2FA or "
                             "log in manually and save cookies.")
                return True

            # Check for suspicious activity
            if "suspicious" in page_content or "unusual activity" in page_content:
                logger.warning("[facebook] Suspicious activity detected! "
                               f"Pausing for {FB_SUSPICIOUS_PAUSE}s")
                self.stealth.interruptible_sleep(FB_SUSPICIOUS_PAUSE)
                return True

            # Check for captcha
            if "captcha" in page_content:
                logger.error("[facebook] CAPTCHA detected. Cannot proceed automatically.")
                return True

            return False

        except Exception:
            return False

    def _scrape_group(self, group_slug: str, max_files: int):
        """Scrape a single Facebook group for quote images."""
        url = f"https://www.facebook.com/groups/{group_slug}"
        logger.info(f"[facebook] Navigating to {url}")

        self.page.goto(url, wait_until="domcontentloaded")
        self.stealth.random_delay(3, 6)
        self.status.set_last_url("facebook", url)

        # Check if we can access the group
        page_content = self.page.content().lower()
        if "join group" in page_content and "private group" in page_content:
            logger.warning(f"[facebook] Cannot access private group: {group_slug}")
            return
        if "this content isn't available" in page_content:
            logger.warning(f"[facebook] Group not available: {group_slug}")
            return

        # Scroll through posts and collect images
        scroll_count = 0
        no_new_content_count = 0
        last_post_count = 0

        while scroll_count < FB_MAX_SCROLLS_PER_GROUP:
            if self.stealth.should_stop() or len(self.collected_files) >= max_files:
                break

            # Find posts with images
            try:
                self._scan_visible_posts(group_slug)
            except Exception as e:
                logger.error(f"[facebook] Error scanning posts: {e}")

            # Scroll down
            human_like_scroll(self.page, direction="down")
            self.stealth.human_scroll_delay()
            scroll_count += 1

            # Check for new content
            current_post_count = self._count_posts()
            if current_post_count == last_post_count:
                no_new_content_count += 1
                if no_new_content_count >= 5:
                    logger.info(f"[facebook] No new content after {scroll_count} scrolls, moving on")
                    break
            else:
                no_new_content_count = 0
            last_post_count = current_post_count

            # Periodic reading pause (be human-like)
            if scroll_count % 5 == 0:
                simulate_reading_pause()

            # Session break check
            if scroll_count % 30 == 0:
                pause = random.uniform(60, 180)
                logger.info(f"[facebook] Session break: {pause:.0f}s")
                self.stealth.interruptible_sleep(pause)

        logger.info(f"[facebook] Done with group {group_slug} "
                     f"({scroll_count} scrolls, {len(self.collected_files)} files total)")

    def _scan_visible_posts(self, group_slug: str):
        """Scan currently visible posts for quote-related images."""
        try:
            # Find post containers
            posts = self.page.locator('[role="article"]').all()

            for post in posts:
                if self.stealth.should_stop():
                    break

                try:
                    post_text = post.inner_text(timeout=2000)
                except Exception:
                    continue

                # Check if post is quote-related
                text_lower = post_text.lower()
                is_quote_related = any(kw in text_lower for kw in QUOTE_KEYWORDS)

                if not is_quote_related:
                    continue

                self.status.record_post_scanned("facebook")

                # Look for image attachments
                try:
                    images = post.locator("img").all()
                    for img in images:
                        try:
                            src = img.get_attribute("src", timeout=1000)
                            if not src:
                                continue

                            # Filter out profile pics, icons, emojis
                            if self._is_content_image(src):
                                self._download_image(
                                    src,
                                    post_text=post_text[:500],
                                    group_name=group_slug,
                                )
                        except Exception:
                            continue
                except Exception:
                    pass

                # Look for file attachment links (PDFs, docs)
                try:
                    links = post.locator("a").all()
                    for link in links:
                        try:
                            href = link.get_attribute("href", timeout=1000)
                            link_text = link.inner_text(timeout=1000)
                            if href and self._is_document_link(href, link_text):
                                self._download_document(
                                    href,
                                    post_text=post_text[:500],
                                    group_name=group_slug,
                                )
                        except Exception:
                            continue
                except Exception:
                    pass

        except Exception as e:
            logger.debug(f"[facebook] Error scanning posts: {e}")

    def _is_content_image(self, src: str) -> bool:
        """Check if an image URL is a real content image (not an icon/avatar)."""
        if not src or not src.startswith("http"):
            return False

        # Skip Facebook CDN profile/icon images (usually small)
        skip_patterns = [
            "emoji", "icon", "avatar", "profile",
            "static.xx", "platform-lookaside",
            "external-", "pixel",
            "safe_image.php",  # Link preview images
        ]
        src_lower = src.lower()
        if any(pat in src_lower for pat in skip_patterns):
            return False

        # Must be from Facebook's content CDN
        if "scontent" in src or "fbcdn" in src:
            return True

        # External image URLs are also fine
        if src.endswith((".jpg", ".jpeg", ".png", ".webp")):
            return True

        return False

    def _is_document_link(self, href: str, text: str) -> bool:
        """Check if a link points to a document (PDF, DOCX)."""
        if not href:
            return False

        href_lower = href.lower()
        text_lower = (text or "").lower()

        # Direct file links
        if any(href_lower.endswith(ext) for ext in [".pdf", ".docx", ".doc", ".xlsx"]):
            return True

        # Google Drive / Dropbox links
        if "drive.google.com" in href_lower or "dropbox.com" in href_lower:
            return True

        # Facebook file attachments
        if "/file/" in href_lower or "attachment" in href_lower:
            return True

        # Text indicators
        if any(kw in text_lower for kw in ["pdf", "document", "file", "download", "quote", "estimate"]):
            if "http" in href_lower:
                return True

        return False

    def _download_image(self, url: str, post_text: str = "", group_name: str = ""):
        """Download an image from Facebook."""
        if url in self.seen_urls:
            return
        self.seen_urls.add(url)

        # Check dedup
        if self.dedup.is_duplicate(source_url=url):
            self.status.record_duplicate()
            return

        metadata = {
            "post_text": post_text,
            "group_name": group_name,
            "date_posted": datetime.utcnow().isoformat(),
        }

        quote_file = download_file(url, SourceType.FACEBOOK, metadata)
        if quote_file:
            self.dedup.mark_seen(
                file_hash=quote_file.file_hash,
                source="facebook",
                source_url=url,
                file_type=quote_file.file_type,
                file_size=quote_file.file_size,
                file_path=quote_file.file_path,
            )
            self.collected_files.append(quote_file)
            self.status.record_image_found("facebook")
            self.status.record_download("facebook")

    def _download_document(self, url: str, post_text: str = "", group_name: str = ""):
        """Download a document (PDF, DOCX) link."""
        if url in self.seen_urls:
            return
        self.seen_urls.add(url)

        if self.dedup.is_duplicate(source_url=url):
            self.status.record_duplicate()
            return

        metadata = {
            "post_text": post_text,
            "group_name": group_name,
            "date_posted": datetime.utcnow().isoformat(),
        }

        quote_file = download_file(url, SourceType.FACEBOOK, metadata)
        if quote_file:
            self.dedup.mark_seen(
                file_hash=quote_file.file_hash,
                source="facebook",
                source_url=url,
                file_type=quote_file.file_type,
                file_size=quote_file.file_size,
                file_path=quote_file.file_path,
            )
            self.collected_files.append(quote_file)
            self.status.record_pdf_found("facebook")
            self.status.record_download("facebook")

    def _count_posts(self) -> int:
        """Count the number of visible posts."""
        try:
            return len(self.page.locator('[role="article"]').all())
        except Exception:
            return 0

    def _cleanup(self):
        """Clean up browser resources."""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
        except Exception:
            pass

    def close(self):
        self._cleanup()
