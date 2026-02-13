"""Configuration for the Image Quote Scraper."""

import os
import json

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "quote_images_raw")
METADATA_DIR = os.path.join(DATA_DIR, "quote_metadata")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
DEDUP_DB_PATH = os.path.join(DATA_DIR, "quotes_images_seen.db")
STATUS_FILE = os.path.join(DATA_DIR, "image_scraper_status.json")
RESUME_FILE = os.path.join(DATA_DIR, "image_scraper_state.json")
SECRETS_DIR = os.path.join(os.path.expanduser("~"), "clawd", ".secrets")

# === Rate Limits (seconds between requests) ===
RATE_LIMITS = {
    "facebook": 5,      # Very conservative — most ban-prone
    "reddit": 2,
    "forums": 2,
    "gdrive": 1,        # No rate limit on Drive downloads
    "angi": 5,          # Has Cloudflare
    "youtube": 3,
}

# === Session breaks ===
SESSION_BREAK_EVERY = 50     # Pause after N requests
SESSION_BREAK_DURATION = (120, 300)  # 2-5 minutes random

# === Backoff ===
BACKOFF_INITIAL = 30          # seconds
BACKOFF_MULTIPLIER = 2
BACKOFF_MAX = 300             # 5 minutes

# === Jitter ===
JITTER_MIN = 0.5
JITTER_MAX = 3.0

# === Browser settings ===
HEADLESS = False              # Set True after testing
BROWSER_TIMEOUT = 30000       # 30 seconds

# === User Agents ===
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
]

# === Facebook Config ===
FACEBOOK_CREDS_FILE = os.path.join(SECRETS_DIR, "facebook_creds.json")
FACEBOOK_COOKIES_FILE = os.path.join(SECRETS_DIR, "facebook_cookies.json")

FACEBOOK_GROUPS = [
    "homeimprovement",
    "diy-home-repair",
    "homeowner-help",
    # Jason will join 20-30 groups, we'll add them later
    # Format: group URL slug (the part after facebook.com/groups/)
]

# Facebook anti-ban timing
FB_SCROLL_DELAY = (3, 8)        # seconds between scrolls
FB_ACTION_DELAY = (3, 10)       # seconds between actions
FB_SESSION_BREAK = (120, 300)   # 2-5 min break every 30 min
FB_MAX_SCROLLS_PER_GROUP = 100  # Stop scrolling after this many
FB_SUSPICIOUS_PAUSE = 1800      # 30 min if suspicious activity detected

# === Reddit Config ===
SUBREDDITS = [
    "homeimprovement", "HomeOwners", "Contractor", "Renovations",
    "Roofing", "HVAC", "Plumbing", "Electricians",
    "Landscaping", "solar", "Insulation",
]

REDDIT_SEARCH_TERMS = [
    "quote", "estimate", "bid", "cost", "price",
    "how much", "is this fair", "got quoted", "contractor charged",
]

# === Google Drive Search Queries ===
GDRIVE_SEARCH_QUERIES = [
    'site:drive.google.com "contractor quote" OR "estimate" filetype:pdf',
    'site:drive.google.com "roofing quote" filetype:pdf',
    'site:drive.google.com "hvac estimate" filetype:pdf',
    'site:drive.google.com "plumbing quote" filetype:pdf',
    'site:drive.google.com "electrical estimate" filetype:pdf',
    'site:drive.google.com "bathroom remodel quote" filetype:pdf',
    'site:drive.google.com "kitchen remodel estimate" filetype:pdf',
    'site:drive.google.com "painting estimate" filetype:pdf',
    'site:drive.google.com "landscaping quote" filetype:pdf',
    'site:drive.google.com "flooring estimate" filetype:pdf',
    'site:dropbox.com "contractor quote" OR "estimate"',
    'site:dropbox.com "roofing quote" OR "hvac estimate"',
    # Reddit-hosted quotes
    '"contractor quote" filetype:pdf site:reddit.com',
    '"contractor estimate" filetype:pdf',
    '"is this quote fair" filetype:jpg OR filetype:png',
]

# === Forum Config ===
FORUM_TARGETS = {
    "contractortalk": {
        "base_url": "https://www.contractortalk.com",
        "search_url": "https://www.contractortalk.com/search/",
        "keywords": ["quote", "estimate", "bid", "cost breakdown"],
    },
    "diychatroom": {
        "base_url": "https://www.diychatroom.com",
        "search_url": "https://www.diychatroom.com/search/",
        "keywords": ["quote", "estimate", "bid", "cost"],
    },
    "houserepair": {
        "base_url": "https://www.houserepairtalk.com",
        "search_url": "https://www.houserepairtalk.com/search/",
        "keywords": ["quote", "estimate", "bid"],
    },
    "terrylove": {
        "base_url": "https://terrylove.com/forums",
        "search_url": "https://terrylove.com/forums/index.php?search/",
        "keywords": ["quote", "estimate", "bid", "cost"],
    },
}

# === Angi Config ===
ANGI_PROJECT_TYPES = [
    "roof-replacement", "bathroom-remodel", "kitchen-remodel",
    "hvac-system", "plumbing", "electrician", "interior-painting",
    "exterior-painting", "flooring", "window-replacement",
    "siding", "deck-building", "fence-installation", "concrete",
    "landscaping", "tree-removal", "garage-door", "insulation",
    "gutter-installation", "solar-panels", "basement-remodel",
    "home-addition", "drywall", "water-heater", "swimming-pool",
]

# === YouTube Config ===
YOUTUBE_CHANNELS = [
    "This Old House",
    "Home RenoVision DIY",
    "Matt Risinger",
    "The Honest Carpenter",
    "Home Repair Tutor",
]

YOUTUBE_SEARCH_TERMS = [
    "contractor quote review",
    "is this quote fair",
    "contractor estimate",
    "roofing quote",
    "hvac estimate",
    "remodel quote",
]

# === Claude API for classification ===
CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# === File patterns ===
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}
DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls"}
ALL_QUOTE_EXTENSIONS = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS

IMAGE_URL_PATTERN = r'(?:https?://\S+\.(?:jpg|jpeg|png|webp|gif|bmp)(?:\?\S*)?)'
PDF_URL_PATTERN = r'(?:https?://\S+\.pdf(?:\?\S*)?)'
GDRIVE_URL_PATTERN = r'https?://drive\.google\.com/(?:file/d/|open\?id=|uc\?id=)([a-zA-Z0-9_-]+)'
DROPBOX_URL_PATTERN = r'https?://(?:www\.)?dropbox\.com/\S+'
IMGUR_URL_PATTERN = r'https?://(?:i\.)?imgur\.com/\S+'
REDDIT_IMAGE_PATTERN = r'https?://(?:i\.redd\.it|preview\.redd\.it)/\S+'

# === Helpers ===
def load_facebook_creds() -> dict:
    """Load Facebook credentials from secrets file."""
    if os.path.exists(FACEBOOK_CREDS_FILE):
        try:
            with open(FACEBOOK_CREDS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading Facebook creds: {e}")
    return {}


def ensure_dirs():
    """Create all necessary directories."""
    for d in [DATA_DIR, OUTPUT_DIR, METADATA_DIR, LOGS_DIR]:
        os.makedirs(d, exist_ok=True)
