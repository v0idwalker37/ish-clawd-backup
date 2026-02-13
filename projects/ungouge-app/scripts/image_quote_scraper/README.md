# Image Quote Scraper for Ungouge.ai

Production-grade, multi-source contractor quote image/PDF scraper. Collects actual contractor quote documents (images, PDFs, DOCX) from 6 sources to train Ungouge's pricing models.

## Quick Start

```bash
cd /Users/moltbot/clawd/projects/ungouge-app

# Test mode (max 10 files, 30 min)
python3 scripts/image_quote_scraper/scraper.py --sources reddit,gdrive --test-mode

# Full run, all sources, headless browser
python3 scripts/image_quote_scraper/scraper.py --sources all --headless --max-hours 6

# Just Facebook, 100 files max
python3 scripts/image_quote_scraper/scraper.py --sources facebook --max-files 100

# Resume interrupted run
python3 scripts/image_quote_scraper/scraper.py --resume

# Skip classification (faster)
python3 scripts/image_quote_scraper/scraper.py --sources reddit --no-classify
```

## Sources (Priority Order)

| Source | Expected Yield | Method | Status |
|--------|---------------|--------|--------|
| Facebook Groups | 200-300 | Playwright browser automation | Ready (needs creds) |
| Reddit | 150-200 | JSON API (no auth) | ✅ Tested |
| Google Drive | 30-50 | Google search scraping | ✅ Ready |
| Contractor Forums | 50-75 | requests + BeautifulSoup | ✅ Ready |
| Angi/HomeAdvisor | 20-40 | requests (graceful Cloudflare skip) | ✅ Ready |
| YouTube | 10-20 | HTML scraping | ✅ Ready |

## Architecture

```
image_quote_scraper/
├── scraper.py              # Main orchestrator + CLI
├── config.py               # All settings, rate limits, credentials
├── models.py               # Data models (QuoteFile, ScrapeResult, etc.)
├── status.py               # Real-time status tracking (JSON updates every 30s)
├── sources/
│   ├── facebook.py         # Facebook group scraper (Playwright)
│   ├── reddit.py           # Reddit image/PDF detector
│   ├── gdrive.py           # Google Drive public link hunter
│   ├── forums.py           # Contractor forum scraper
│   ├── angi.py             # Angi/HomeAdvisor review parser
│   └── youtube.py          # YouTube comment extractor
├── extraction/
│   ├── downloader.py       # Download images/PDFs from URLs
│   ├── classifier.py       # Is this actually a contractor quote? (Claude Vision)
│   └── dedup.py            # Perceptual hash + MD5 deduplication
└── utils/
    ├── browser.py           # Playwright browser management
    ├── stealth.py           # Anti-detection (delays, user agents, etc.)
    └── storage.py           # File organization and metadata
```

## Output Structure

```
data/
├── quote_images_raw/
│   └── 2026-02-12/
│       ├── facebook/
│       │   ├── quote_0001.jpg
│       │   └── quote_0001_metadata.json
│       ├── reddit/
│       ├── gdrive/
│       ├── forums/
│       ├── angi/
│       └── youtube/
├── quote_metadata/
│   └── collected_quotes.json       # Master list of all collected files
├── logs/
│   └── image_scraper_2026-02-12.log
├── image_scraper_status.json       # Real-time status (updates every 30s)
├── image_scraper_state.json        # Resume state
└── quotes_images_seen.db           # SQLite dedup database
```

## Facebook Setup

1. Create `/Users/moltbot/clawd/.secrets/facebook_creds.json`:
   ```json
   {
     "email": "your-email@example.com",
     "password": "your-password"
   }
   ```

2. Account must be 3+ days old
3. Join 20-30 home improvement groups
4. First test in headed mode (visible browser): `--sources facebook` (no `--headless`)
5. After confirming login works, switch to `--headless`

### Facebook Groups to Join
- Home Improvement Tips & DIY
- Homeowner Help
- DIY Home Repair
- Contractor Reviews & Recommendations
- (Add group slugs to `config.py` FACEBOOK_GROUPS list)

## Anti-Detection Measures

- **Rate limiting**: Per-source configurable delays (2-5s between requests)
- **Session breaks**: 2-5 min pause every 50 requests
- **User agent rotation**: 8 common browser UAs
- **Human-like scrolling**: Variable scroll distance, occasional scroll-back
- **Exponential backoff**: Auto-backs off on rate limits or errors
- **Stealth browser**: Anti-webdriver detection, realistic fingerprints
- **Graceful failure**: Never crashes, skips blocked sources

## Classification

Uses Claude Vision API (~$0.002/image) to classify:
- **YES** → Confirmed contractor quote → keep
- **NO** → Not a quote (receipt, meme, etc.) → discard
- **UNSURE** → Flag for manual review

Set `ANTHROPIC_API_KEY` environment variable for classification.

## Deduplication

- **Images**: Perceptual hash (pHash) — catches near-identical images even with minor cropping/compression
- **Documents**: MD5 hash — catches exact duplicates
- **URLs**: Tracks all downloaded URLs to avoid re-fetching
- **SQLite DB**: `data/quotes_images_seen.db`

## Dependencies

```bash
pip3 install --user playwright beautifulsoup4 Pillow imagehash requests anthropic
playwright install chromium  # For Facebook/Angi browser automation
```

## Monitoring

Watch status in real-time:
```bash
watch -n 5 cat /Users/moltbot/clawd/projects/ungouge-app/data/image_scraper_status.json
```

## Timeline

- **Feb 12**: Scraper built and tested ✅
- **Feb 13-15**: Jason ages Facebook account, joins groups
- **Feb 16**: First real Facebook run (midnight-6am)
- **Feb 17-23**: Nightly collection runs → 500-600 files
