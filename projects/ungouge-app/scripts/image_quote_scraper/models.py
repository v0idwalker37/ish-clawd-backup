"""Data models for the Image Quote Scraper."""

from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    FACEBOOK = "facebook"
    REDDIT = "reddit"
    GDRIVE = "gdrive"
    FORUMS = "forums"
    ANGI = "angi"
    YOUTUBE = "youtube"


class FileType(str, Enum):
    IMAGE = "image"
    PDF = "pdf"
    DOCX = "docx"
    OTHER = "other"


class ClassificationResult(str, Enum):
    QUOTE = "quote"           # Confirmed contractor quote
    NOT_QUOTE = "not_quote"   # Definitely not a quote
    UNSURE = "unsure"         # Needs manual review
    PENDING = "pending"       # Not yet classified


@dataclass
class QuoteFile:
    """Represents a downloaded quote file (image/PDF)."""
    file_id: str                    # Unique ID for this file
    source: SourceType
    source_url: str                 # Where we found it
    post_url: str = ""              # URL of the containing post
    post_title: str = ""            # Title of the containing post
    post_text: str = ""             # Text context around the file
    author: str = "redacted"        # Always redact
    date_posted: str = ""           # When the original post was made
    date_collected: str = ""        # When we downloaded it
    file_type: str = ""             # MIME type (image/png, application/pdf, etc.)
    file_extension: str = ""        # .jpg, .pdf, etc.
    file_size: int = 0              # bytes
    file_path: str = ""             # Where we saved it locally
    file_hash: str = ""             # MD5/pHash for dedup
    perceptual_hash: str = ""       # pHash for images
    classification: ClassificationResult = ClassificationResult.PENDING
    classification_reason: str = ""
    group_name: str = ""            # Facebook group name
    subreddit: str = ""             # Reddit subreddit
    forum_name: str = ""            # Forum name
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["source"] = self.source.value
        d["classification"] = self.classification.value
        return d

    def to_metadata_dict(self) -> dict:
        """Metadata to save alongside each downloaded file."""
        return {
            "file_id": self.file_id,
            "source": self.source.value,
            "source_url": self.source_url,
            "post_url": self.post_url,
            "post_title": self.post_title,
            "author": self.author,
            "date_posted": self.date_posted,
            "date_collected": self.date_collected,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "classification": self.classification.value,
            "group_name": self.group_name,
            "subreddit": self.subreddit,
            "forum_name": self.forum_name,
        }

    @staticmethod
    def from_dict(d: dict) -> "QuoteFile":
        d = d.copy()
        d["source"] = SourceType(d.get("source", "reddit"))
        d["classification"] = ClassificationResult(d.get("classification", "pending"))
        return QuoteFile(**{k: v for k, v in d.items() if k in QuoteFile.__dataclass_fields__})


@dataclass
class ScrapeResult:
    """Summary of a scraping session."""
    source: SourceType
    files_found: int = 0
    files_downloaded: int = 0
    duplicates_skipped: int = 0
    errors: int = 0
    elapsed_seconds: float = 0.0
    status: str = "pending"
    files: List[QuoteFile] = field(default_factory=list)
