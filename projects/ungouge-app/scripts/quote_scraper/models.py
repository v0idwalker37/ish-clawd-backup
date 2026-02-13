"""Data models for the quote scraper."""

from dataclasses import dataclass, field, asdict
from typing import Optional, List
import json
from datetime import datetime


@dataclass
class RawQuote:
    source: str  # reddit, angi, homeadvisor
    source_url: str
    source_id: str  # post ID, review ID
    raw_text: str
    author: str  # anonymized
    date_posted: str
    date_collected: str

    def to_dict(self):
        return asdict(self)


@dataclass
class ExtractedQuote:
    raw: RawQuote
    dollar_amount: float
    project_type: str  # mapped to our 34 types
    location_state: str
    location_city: str
    year: int
    square_footage: Optional[float] = None
    scope: str = ""
    confidence: float = 0.0  # 0-1 how confident we are in extraction
    line_items: List[dict] = field(default_factory=list)

    def to_dict(self):
        d = asdict(self)
        return d

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @staticmethod
    def from_dict(d):
        raw_d = d.get("raw", {})
        raw = RawQuote(**raw_d)
        return ExtractedQuote(
            raw=raw,
            dollar_amount=d.get("dollar_amount", 0),
            project_type=d.get("project_type", "unknown"),
            location_state=d.get("location_state", ""),
            location_city=d.get("location_city", ""),
            year=d.get("year", 0),
            square_footage=d.get("square_footage"),
            scope=d.get("scope", ""),
            confidence=d.get("confidence", 0.0),
            line_items=d.get("line_items", []),
        )
