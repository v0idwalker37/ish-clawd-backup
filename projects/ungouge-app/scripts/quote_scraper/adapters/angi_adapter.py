"""Angi.com adapter — scrapes cost guide pages for pricing data."""

import re
import json
import logging
import hashlib
from datetime import datetime
from typing import List, Optional

from .base_adapter import BaseAdapter
from ..models import RawQuote, ExtractedQuote
from ..config import ANGI_COST_PAGES, ANGI_COST_PATHS, ANGI_DELAY, RESUME_FILE
from ..dedup import DedupEngine
from ..status import StatusTracker

logger = logging.getLogger(__name__)


class AngiAdapter(BaseAdapter):
    """Scrape cost guides from Angi.com."""

    SOURCE_NAME = "angi"
    BASE_DELAY = ANGI_DELAY

    def __init__(self, dedup: DedupEngine, status: StatusTracker,
                 shutdown_event=None):
        super().__init__(dedup, status, shutdown_event)

    def run(self, max_quotes: int = 1000) -> List[ExtractedQuote]:
        """Scrape Angi cost guides."""
        logger.info(f"[angi] Starting Angi scraper (max {max_quotes} quotes)")
        self.status.init_source("angi")

        resume_state = self._load_resume_state()
        completed_urls = set(resume_state.get("completed_urls", []))

        # Scrape article-style cost guides
        all_urls = list(ANGI_COST_PAGES)

        # Also try /costs/ path pattern
        for path in ANGI_COST_PATHS:
            url = f"https://www.angi.com{path}"
            if url not in all_urls:
                all_urls.append(url)

        for url in all_urls:
            if self.should_stop() or len(self.collected_quotes) >= max_quotes:
                break

            if url in completed_urls:
                logger.debug(f"[angi] Skipping completed: {url}")
                continue

            logger.info(f"[angi] Fetching: {url} "
                       f"({len(self.collected_quotes)}/{max_quotes} quotes)")

            try:
                self._scrape_cost_page(url)
                completed_urls.add(url)
                self._save_resume_state(list(completed_urls))
            except Exception as e:
                logger.error(f"[angi] Error scraping {url}: {e}")
                self.status.record_error("angi")

        logger.info(f"[angi] Finished. Collected {len(self.collected_quotes)} quotes")
        self.status.set_source_status("angi", "done")
        return self.collected_quotes

    def _scrape_cost_page(self, url: str):
        """Scrape a single Angi cost guide page."""
        resp = self.fetch_url(url)
        if not resp:
            return

        html = resp.text
        
        # Check for Cloudflare challenge
        if self._is_cloudflare_blocked(html):
            logger.warning(f"[angi] Cloudflare blocked: {url}")
            self.status.record_error("angi")
            return

        # Extract text content (strip HTML tags)
        text = self._html_to_text(html)
        if not text or len(text) < 100:
            logger.debug(f"[angi] No useful content: {url}")
            return

        # Try to extract structured cost data from the page
        self._extract_cost_guide_data(text, url, html)

    def _is_cloudflare_blocked(self, html: str) -> bool:
        """Detect Cloudflare challenge pages."""
        indicators = [
            "Checking your browser",
            "cf-browser-verification",
            "Cloudflare",
            "Just a moment",
            "_cf_chl_opt",
        ]
        return any(ind in html for ind in indicators)

    def _html_to_text(self, html: str) -> str:
        """Basic HTML to text conversion."""
        # Remove script and style blocks
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Decode common entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _extract_cost_guide_data(self, text: str, url: str, html: str):
        """Extract pricing data from Angi cost guide text."""
        # Angi cost guides typically have structured pricing info
        # Look for patterns like "Average cost: $X,XXX" or "ranges from $X to $Y"
        
        # Detect project type from URL
        project_type = self._detect_project_from_url(url)
        
        # Split text into sections (~500 char chunks with overlap)
        chunks = self._chunk_text(text, chunk_size=600, overlap=100)
        
        for i, chunk in enumerate(chunks):
            if self.should_stop():
                return

            # Only process chunks that have dollar amounts
            if not re.search(r'\$\d', chunk):
                continue

            source_id = hashlib.sha256(
                f"{url}:{i}".encode()
            ).hexdigest()[:12]

            raw = RawQuote(
                source="angi",
                source_url=url,
                source_id=source_id,
                raw_text=chunk,
                author="angi_cost_guide",
                date_posted=datetime.utcnow().strftime("%Y-%m-%d"),
                date_collected=datetime.utcnow().isoformat(),
            )

            self.process_raw_quote(raw)

        # Also try to extract structured JSON-LD data if present
        self._extract_json_ld(html, url)

    def _extract_json_ld(self, html: str, url: str):
        """Extract structured data from JSON-LD in page."""
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
        """Process a JSON-LD item for pricing data."""
        if not isinstance(item, dict):
            return
        
        # Look for pricing info in structured data
        text_parts = []
        
        if "description" in item:
            text_parts.append(str(item["description"]))
        if "articleBody" in item:
            text_parts.append(str(item["articleBody"])[:2000])
        if "text" in item:
            text_parts.append(str(item["text"])[:2000])
        
        combined = " ".join(text_parts)
        if combined and re.search(r'\$\d', combined):
            source_id = hashlib.sha256(
                f"jsonld:{url}".encode()
            ).hexdigest()[:12]

            raw = RawQuote(
                source="angi",
                source_url=url,
                source_id=source_id,
                raw_text=combined[:5000],
                author="angi_structured",
                date_posted=datetime.utcnow().strftime("%Y-%m-%d"),
                date_collected=datetime.utcnow().isoformat(),
            )
            self.process_raw_quote(raw)

    def _detect_project_from_url(self, url: str) -> str:
        """Guess project type from URL path."""
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
            "mold": "mold_remediation",
            "asbestos": "asbestos_removal",
            "waterproof": "waterproofing",
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
                return state.get("angi", {})
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

        state["angi"] = {
            "completed_urls": completed_urls,
            "last_updated": datetime.utcnow().isoformat(),
        }

        os.makedirs(os.path.dirname(RESUME_FILE), exist_ok=True)
        try:
            with open(RESUME_FILE, "w") as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            logger.error(f"[angi] Error saving resume state: {e}")
