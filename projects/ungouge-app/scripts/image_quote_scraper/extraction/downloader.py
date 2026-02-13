"""Download images/PDFs from URLs with proper error handling."""

import os
import re
import hashlib
import logging
import mimetypes
import requests
import time
import random
from typing import Optional, Tuple
from urllib.parse import urlparse, unquote

from ..config import (
    IMAGE_EXTENSIONS, DOCUMENT_EXTENSIONS,
    GDRIVE_URL_PATTERN, DROPBOX_URL_PATTERN,
    USER_AGENTS, RATE_LIMITS,
)
from ..models import QuoteFile, SourceType, FileType
from ..utils.storage import get_output_dir, get_next_filename, save_file_with_metadata

logger = logging.getLogger(__name__)

# Max file size: 50 MB
MAX_FILE_SIZE = 50 * 1024 * 1024

# Common image content types
IMAGE_CONTENT_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "image/bmp", "image/tiff",
}
DOCUMENT_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}


def download_file(url: str, source: SourceType, metadata: dict = None,
                  output_dir: str = None) -> Optional[QuoteFile]:
    """Download a file from URL and save it with metadata.
    
    Args:
        url: URL to download
        source: Source type (facebook, reddit, etc.)
        metadata: Additional metadata (post_title, post_url, etc.)
        output_dir: Override output directory
    
    Returns:
        QuoteFile if successful, None if failed
    """
    metadata = metadata or {}

    # Handle special URLs
    url = normalize_download_url(url)
    if not url:
        return None

    try:
        # Download with streaming
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "image/*,application/pdf,*/*;q=0.8",
            "Referer": metadata.get("post_url", ""),
        }

        resp = requests.get(url, headers=headers, stream=True,
                            timeout=30, allow_redirects=True)

        if resp.status_code != 200:
            logger.debug(f"Download failed ({resp.status_code}): {url}")
            return None

        # Check content type
        content_type = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
        
        # Determine file extension
        extension = get_extension(url, content_type)
        if not extension:
            logger.debug(f"Unknown file type ({content_type}): {url}")
            return None

        # Check if it's an image or document
        if extension not in IMAGE_EXTENSIONS and extension not in DOCUMENT_EXTENSIONS:
            logger.debug(f"Not an image/document ({extension}): {url}")
            return None

        # Check content length
        content_length = int(resp.headers.get("Content-Length", 0))
        if content_length > MAX_FILE_SIZE:
            logger.debug(f"File too large ({content_length} bytes): {url}")
            return None

        # Read content
        content = b""
        for chunk in resp.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > MAX_FILE_SIZE:
                logger.debug(f"File exceeded max size during download: {url}")
                return None

        if len(content) < 1000:
            logger.debug(f"File too small ({len(content)} bytes), likely an error page: {url}")
            return None

        # Calculate hashes
        md5_hash = hashlib.md5(content).hexdigest()

        # Determine file type
        if extension in IMAGE_EXTENSIONS:
            file_type_str = f"image/{extension.lstrip('.')}"
        elif extension == ".pdf":
            file_type_str = "application/pdf"
        else:
            file_type_str = content_type or f"application/{extension.lstrip('.')}"

        # Save file
        if output_dir is None:
            output_dir = get_output_dir(source.value)

        filepath = get_next_filename(output_dir, prefix="quote", extension=extension)
        with open(filepath, "wb") as f:
            f.write(content)

        # Create QuoteFile
        from datetime import datetime
        file_id = f"{source.value}_{md5_hash[:12]}"

        quote_file = QuoteFile(
            file_id=file_id,
            source=source,
            source_url=url,
            post_url=metadata.get("post_url", ""),
            post_title=metadata.get("post_title", ""),
            post_text=metadata.get("post_text", "")[:500],
            author="redacted",
            date_posted=metadata.get("date_posted", ""),
            date_collected=datetime.utcnow().isoformat(),
            file_type=file_type_str,
            file_extension=extension,
            file_size=len(content),
            file_path=filepath,
            file_hash=md5_hash,
            group_name=metadata.get("group_name", ""),
            subreddit=metadata.get("subreddit", ""),
            forum_name=metadata.get("forum_name", ""),
        )

        # Save metadata
        save_file_with_metadata(filepath, quote_file)

        logger.info(f"Downloaded {extension} ({len(content)} bytes) → {os.path.basename(filepath)}")
        return quote_file

    except requests.exceptions.Timeout:
        logger.debug(f"Download timeout: {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.debug(f"Connection error downloading: {url}")
        return None
    except Exception as e:
        logger.error(f"Download error ({url}): {e}")
        return None


def normalize_download_url(url: str) -> Optional[str]:
    """Normalize special URLs (Google Drive, Dropbox, imgur) to direct download links."""
    if not url:
        return None

    # Google Drive
    gdrive_match = re.search(GDRIVE_URL_PATTERN, url)
    if gdrive_match:
        file_id = gdrive_match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    # Dropbox: change ?dl=0 to ?dl=1
    if "dropbox.com" in url:
        url = re.sub(r'\?dl=0', '?dl=1', url)
        if "?dl=" not in url:
            url += "?dl=1" if "?" not in url else "&dl=1"
        return url

    # Imgur: ensure direct image link
    if "imgur.com" in url and not url.endswith(('.jpg', '.png', '.gif', '.webp')):
        # Convert gallery URL to direct image
        if "/a/" not in url and "/gallery/" not in url:
            # Single image page: add .jpg
            parsed = urlparse(url)
            path = parsed.path.rstrip("/")
            if "." not in path.split("/")[-1]:
                return f"https://i.imgur.com{path}.jpg"

    # Reddit preview images → direct URL
    if "preview.redd.it" in url:
        # These are already direct image URLs
        return url.split("?")[0] if "?" in url else url

    return url


def get_extension(url: str, content_type: str = "") -> Optional[str]:
    """Determine file extension from URL and content type."""
    # Try content type first
    if content_type in IMAGE_CONTENT_TYPES:
        ext_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif",
            "image/bmp": ".bmp",
            "image/tiff": ".tiff",
        }
        return ext_map.get(content_type)

    if content_type in DOCUMENT_CONTENT_TYPES:
        ext_map = {
            "application/pdf": ".pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/msword": ".doc",
        }
        return ext_map.get(content_type)

    # Try URL path
    parsed = urlparse(url)
    path = unquote(parsed.path)
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext in IMAGE_EXTENSIONS or ext in DOCUMENT_EXTENSIONS:
        return ext

    # Fallback: guess from content type
    ext = mimetypes.guess_extension(content_type)
    if ext == ".jpe":
        ext = ".jpg"
    return ext


def extract_urls_from_text(text: str) -> list:
    """Extract all image/PDF/document URLs from text."""
    urls = []
    if not text:
        return urls

    # General URL pattern
    url_pattern = r'https?://[^\s<>"\')\]]+\.(?:jpg|jpeg|png|webp|gif|pdf|docx?)\b[^\s<>"\')\]]*'
    for match in re.finditer(url_pattern, text, re.IGNORECASE):
        urls.append(match.group(0))

    # Google Drive links
    for match in re.finditer(GDRIVE_URL_PATTERN, text):
        urls.append(match.group(0))

    # Dropbox links
    for match in re.finditer(DROPBOX_URL_PATTERN, text):
        url = match.group(0)
        if any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.docx']):
            urls.append(url)
        elif 'dl=' in url:
            urls.append(url)  # It's a file download link

    # Imgur links
    imgur_pattern = r'https?://(?:i\.)?imgur\.com/[a-zA-Z0-9]+'
    for match in re.finditer(imgur_pattern, text):
        urls.append(match.group(0))

    # Reddit image links
    reddit_img_pattern = r'https?://(?:i\.redd\.it|preview\.redd\.it)/[^\s<>"\')\]]+'
    for match in re.finditer(reddit_img_pattern, text):
        urls.append(match.group(0))

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)

    return unique
