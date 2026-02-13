"""HomeAdvisor adapter — scrapes cost guide pages for pricing data."""

import re
import json
import logging
import hashlib
from datetime import datetime
from typing import List, Optional

from .base_adapter import BaseAdapter
from ..models import RawQuote, ExtractedQuote
from ..config import HOMEADVISOR_COST_PAGES, HOMEADVISOR_DELAY, RESUME_FILE
from ..dedup import DedupEngine
from ..status import StatusTracker

logger = logging.getLogger(__name__)


class HomeAdvisorAdapter(BaseAdapter):
    """Scrape cost guides from HomeAdvisor.com."""

    SOURCE_NAME = "homeadvisor"
    BASE_DELAY = HOMEADVISOR_DELAY

    def __init__(self, dedup: DedupEngine, status: StatusTracker,
                 shutdown_event=None):
        super().__init__(dedup, status, shutdown_event)

    def run(self, max_quotes: int = 1000) -> List[ExtractedQuote]:
        """Scrape HomeAdvisor cost guides."""
        logger.info(f"[homeadvisor] Starting HomeAdvisor scraper (max {max_quotes} quotes)")
        self.status.init_source("homeadvisor")

        resume_state = self._load_resume_state()
        completed_urls = set(resume_state.get("completed_urls", []))

        for url in HOMEADVISOR_COST_PAGES:
            if self.should_stop() or len(self.collected_quotes) >= max_quotes:
                break

            if url in completed_urls:
                logger.debug(f"[homeadvisor] Skipping completed: {url}")
                continue

            logger.info(f"[homeadvisor] Fetching: {url} "
                       f"({len(self.collected_quotes)}/{max_quotes} quotes)")

            try:
                self._scrape_cost_page(url)
                completed_urls.add(url)
                self._save_resume_state(list(completed_urls))
            except Exception as e:
                logger.error(f"[homeadvisor] Error scraping {url}: {e}")
                self.status.record_error("homeadvisor")

        # Also try to discover additional cost pages
        if not self.should_stop() and len(self.collected_quotes) < max_quotes:
            self._discover_cost_pages(completed_urls, max_quotes)

        logger.info(f"[homeadvisor] Finished. Collected {len(self.collected_quotes)} quotes")
        self.status.set_source_status("homeadvisor", "done")
        return self.collected_quotes

    def _scrape_cost_page(self, url: str):
        """Scrape a single HomeAdvisor cost guide page."""
        resp = self.fetch_url(url)
        if not resp:
            return

        html = resp.text

        # Check for blocks
        if self._is_blocked(html):
            logger.warning(f"[homeadvisor] Blocked: {url}")
            self.status.record_error("homeadvisor")
            return

        # Extract text content
        text = self._html_to_text(html)
        if not text or len(text) < 100:
            logger.debug(f"[homeadvisor] No useful content: {url}")
            return

        # Extract structured cost data
        self._extract_cost_data(text, url, html)

    def _is_blocked(self, html: str) -> bool:
        """Detect blocking."""
        indicators = [
            "Checking your browser",
            "cf-browser-verification",
            "Access Denied",
            "Robot or human",
            "captcha",
        ]
        return any(ind.lower() in html.lower() for ind in indicators)

    def _html_to_text(self, html: str) -> str:
        """Basic HTML to text conversion."""
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _extract_cost_data(self, text: str, url: str, html: str):
        """Extract pricing data from HomeAdvisor cost guide."""
        project_type = self._detect_project_from_url(url)

        # HomeAdvisor pages often have structured cost ranges
        # Look for patterns like "Average Cost: $X,XXX" or "Typical Range: $X - $Y"
        
        # Try JSON-LD first
        self._extract_json_ld(html, url)

        # Process text in chunks
        chunks = self._chunk_text(text, chunk_size=600, overlap=100)

        for i, chunk in enumerate(chunks):
            if self.should_stop():
                return

            if not re.search(r'\$\d', chunk):
                continue

            source_id = hashlib.sha256(
                f"{url}:{i}".encode()
            ).hexdigest()[:12]

            raw = RawQuote(
                source="homeadvisor",
                source_url=url,
                source_id=source_id,
                raw_text=chunk,
                author="homeadvisor_cost_guide",
                date_posted=datetime.utcnow().strftime("%Y-%m-%d"),
                date_collected=datetime.utcnow().isoformat(),
            )

            self.process_raw_quote(raw)

    def _extract_json_ld(self, html: str, url: str):
        """Extract structured data from JSON-LD."""
        ld_pattern = r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>'
        matches = re.findall(ld_pattern, html, re.DOTALL | re.IGNORECASE)

        for match in matches:
            try:
                data = json.loads(match)
                if isinstance(data, list):
                    for item in data:
                        self._process_json_ld_item(item, url)
                else:
                    self._process_json_ld_item(data, url)
            except (json.JSONDecodeError, ValueError):
                continue

    def _process_json_ld_item(self, item: dict, url: str):
        """Process a JSON-LD item."""
        if not isinstance(item, dict):
            return

        text_parts = []
        for key in ("description", "articleBody", "text"):
            if key in item:
                text_parts.append(str(item[key])[:2000])

        combined = " ".join(text_parts)
        if combined and re.search(r'\$\d', combined):
            source_id = hashlib.sha256(
                f"jsonld:{url}".encode()
            ).hexdigest()[:12]

            raw = RawQuote(
                source="homeadvisor",
                source_url=url,
                source_id=source_id,
                raw_text=combined[:5000],
                author="homeadvisor_structured",
                date_posted=datetime.utcnow().strftime("%Y-%m-%d"),
                date_collected=datetime.utcnow().isoformat(),
            )
            self.process_raw_quote(raw)

    def _discover_cost_pages(self, completed_urls: set, max_quotes: int):
        """Try to find additional cost guide pages from the cost index."""
        logger.info("[homeadvisor] Discovering additional cost pages...")
        
        index_url = "https://www.homeadvisor.com/cost/"
        resp = self.fetch_url(index_url)
        if not resp:
            return

        # Find links to cost pages
        link_pattern = r'href="(/cost/[^"]+)"'
        matches = re.findall(link_pattern, resp.text)

        new_urls = set()
        for path in matches:
            full_url = f"https://www.homeadvisor.com{path}"
            if full_url not in completed_urls and full_url not in new_urls:
                new_urls.add(full_url)

        logger.info(f"[homeadvisor] Found {len(new_urls)} additional cost pages")

        for url in list(new_urls)[:50]:  # Cap at 50 extra pages
            if self.should_stop() or len(self.collected_quotes) >= max_quotes:
                break

            try:
                self._scrape_cost_page(url)
                completed_urls.add(url)
            except Exception as e:
                logger.error(f"[homeadvisor] Error: {e}")

        self._save_resume_state(list(completed_urls))

    def _detect_project_from_url(self, url: str) -> str:
        """Guess project type from URL."""
        url_lower = url.lower()
        url_map = {
            "roof": "roof_replacement",
            "bathroom": "bathroom_remodel",
            "kitchen": "kitchen_remodel",
            "hvac": "hvac_install",
            "plumb": "plumbing_repair",
            "electric": "electrical_work",
            "paint": "painting_interior",
            "floor": "flooring_install",
            "window": "window_replacement",
            "siding": "siding_install",
            "deck": "deck_build",
            "fence": "fence_install",
            "concrete": "concrete_work",
            "landscap": "landscaping",
            "tree": "tree_removal",
            "garage": "garage_door",
            "insulation": "insulation",
            "gutter": "gutter_install",
            "solar": "solar_install",
            "basement": "basement_finish",
            "addition": "addition",
            "drywall": "drywall",
            "water-heater": "plumbing_repair",
            "septic": "septic",
            "pool": "pool_install",
        }
        for key, ptype in url_map.items():
            if key in url_lower:
                return ptype
        return "general_remodel"

    def _chunk_text(self, text: str, chunk_size: int = 600,
                    overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            start = end - overlap
            if start < 0:
                break
        return chunks

    def _load_resume_state(self) -> dict:
        import os
        if os.path.exists(RESUME_FILE):
            try:
                with open(RESUME_FILE, "r") as f:
                    state = json.load(f)
                return state.get("homeadvisor", {})
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_resume_state(self, completed_urls: list):
        import os
        state = {}
        if os.path.exists(RESUME_FILE):
            try:
                with open(RESUME_FILE, "r") as f:
                    state = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        state["homeadvisor"] = {
            "completed_urls": completed_urls,
            "last_updated": datetime.utcnow().isoformat(),
        }

        os.makedirs(os.path.dirname(RESUME_FILE), exist_ok=True)
        try:
            with open(RESUME_FILE, "w") as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            logger.error(f"[homeadvisor] Error saving resume state: {e}")
