#!/usr/bin/env python3
"""
Ungouge Quote Scraper — Main entry point.

Collects contractor quotes from Reddit, Angi, and HomeAdvisor.

Usage:
    python3 -m scripts.quote_scraper.scraper --sources reddit,angi,homeadvisor --max-hours 3 --max-quotes 1500
    
Or directly:
    python3 scripts/quote_scraper/scraper.py --sources reddit --max-quotes 10 --max-hours 0.1
"""

import sys
import os
import argparse
import signal
import json
import time
import threading
import logging
from datetime import datetime
from typing import List

# Fix imports when run directly
if __name__ == "__main__":
    # Add project root to path so we can import as a package
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from scripts.quote_scraper.config import (
    DATA_DIR, QUOTES_RAW_DIR, DEDUP_DB_PATH,
)
from scripts.quote_scraper.models import ExtractedQuote
from scripts.quote_scraper.dedup import DedupEngine
from scripts.quote_scraper.status import StatusTracker
from scripts.quote_scraper.adapters.reddit_adapter import RedditAdapter
from scripts.quote_scraper.adapters.angi_adapter import AngiAdapter
from scripts.quote_scraper.adapters.homeadvisor_adapter import HomeAdvisorAdapter

# Force unbuffered output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
else:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

# === Logging Setup ===
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Ungouge Quote Scraper")
    parser.add_argument(
        "--sources",
        type=str,
        default="reddit,angi,homeadvisor",
        help="Comma-separated list of sources: reddit,angi,homeadvisor",
    )
    parser.add_argument(
        "--max-hours",
        type=float,
        default=3.0,
        help="Maximum runtime in hours",
    )
    parser.add_argument(
        "--max-quotes",
        type=int,
        default=1000,
        help="Maximum total quotes to collect",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset resume state and start fresh",
    )
    return parser.parse_args()


def ensure_dirs():
    """Create all necessary directories."""
    for d in [DATA_DIR, QUOTES_RAW_DIR]:
        os.makedirs(d, exist_ok=True)


def save_quotes(quotes: List[ExtractedQuote], source_name: str):
    """Save collected quotes to a dated JSON file."""
    if not quotes:
        return

    today = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{today}_{source_name}.json"
    filepath = os.path.join(QUOTES_RAW_DIR, filename)

    # Load existing quotes from today if any
    existing = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Append new quotes
    for q in quotes:
        existing.append(q.to_dict())

    # Write atomically
    tmp = filepath + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        os.replace(tmp, filepath)
        logger.info(f"Saved {len(quotes)} quotes to {filepath} "
                   f"(total in file: {len(existing)})")
    except IOError as e:
        logger.error(f"Error saving quotes: {e}")


def load_existing_quotes(dedup: DedupEngine):
    """Load existing quotes into dedup DB."""
    existing_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "cost-data", "real-quotes.json"
    )
    existing_file = os.path.normpath(existing_file)
    
    if os.path.exists(existing_file):
        count = dedup.load_existing_quotes(existing_file)
        logger.info(f"Loaded {count} existing quotes into dedup DB "
                   f"(total seen: {dedup.get_total_seen()})")
    else:
        logger.warning(f"Existing quotes file not found: {existing_file}")


def main():
    args = parse_args()
    sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    max_seconds = args.max_hours * 3600
    max_quotes = args.max_quotes

    logger.info("=" * 60)
    logger.info("Ungouge Quote Scraper Starting")
    logger.info(f"  Sources: {', '.join(sources)}")
    logger.info(f"  Max hours: {args.max_hours}")
    logger.info(f"  Max quotes: {max_quotes}")
    logger.info("=" * 60)

    # Setup
    ensure_dirs()

    # Reset resume state if requested
    if args.reset:
        resume_file = os.path.join(DATA_DIR, "scraper_resume.json")
        if os.path.exists(resume_file):
            os.remove(resume_file)
            logger.info("Resume state reset")

    # Initialize components
    dedup = DedupEngine()
    status = StatusTracker()
    shutdown_event = threading.Event()

    # Load existing quotes into dedup
    load_existing_quotes(dedup)

    # Graceful shutdown handler
    def signal_handler(signum, frame):
        logger.info("\nShutdown signal received. Finishing up...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start status tracking
    status.start_periodic_write()

    # Track start time
    start_time = time.time()
    total_collected = 0

    # Allocate quotes per source (roughly equal, Reddit gets more)
    source_quota = {}
    if "reddit" in sources:
        source_quota["reddit"] = int(max_quotes * 0.6)
    if "angi" in sources:
        source_quota["angi"] = int(max_quotes * 0.2)
    if "homeadvisor" in sources:
        source_quota["homeadvisor"] = int(max_quotes * 0.2)

    # If only one source, give it all
    if len(sources) == 1:
        source_quota[sources[0]] = max_quotes

    try:
        # Run each source adapter
        for source_name in sources:
            if shutdown_event.is_set():
                break

            # Check time limit
            elapsed = time.time() - start_time
            if elapsed >= max_seconds:
                logger.info(f"Time limit reached ({args.max_hours}h)")
                break

            # Check total quote limit
            if total_collected >= max_quotes:
                logger.info(f"Quote limit reached ({max_quotes})")
                break

            quota = source_quota.get(source_name, max_quotes)
            remaining = max_quotes - total_collected
            source_max = min(quota, remaining)

            adapter = None
            try:
                if source_name == "reddit":
                    adapter = RedditAdapter(dedup, status, shutdown_event)
                elif source_name == "angi":
                    adapter = AngiAdapter(dedup, status, shutdown_event)
                elif source_name == "homeadvisor":
                    adapter = HomeAdvisorAdapter(dedup, status, shutdown_event)
                else:
                    logger.warning(f"Unknown source: {source_name}")
                    continue

                logger.info(f"\n{'='*40}")
                logger.info(f"Starting {source_name} adapter (max {source_max} quotes)")
                logger.info(f"{'='*40}")

                quotes = adapter.run(max_quotes=source_max)

                if quotes:
                    save_quotes(quotes, source_name)
                    total_collected += len(quotes)
                    logger.info(f"{source_name}: collected {len(quotes)} quotes "
                              f"(total: {total_collected})")
                elif adapter.collected_quotes:
                    # Adapter may have been interrupted — save what we have
                    save_quotes(adapter.collected_quotes, source_name)
                    total_collected += len(adapter.collected_quotes)
                    logger.info(f"{source_name}: saved {len(adapter.collected_quotes)} "
                              f"partial quotes (total: {total_collected})")

            except Exception as e:
                logger.error(f"Error in {source_name} adapter: {e}", exc_info=True)
            finally:
                if adapter:
                    adapter.close()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        # Final summary
        status.stop()
        status.log_summary()
        dedup.close()

        elapsed = time.time() - start_time
        logger.info(f"\nTotal: {total_collected} quotes in {elapsed:.0f}s")
        logger.info(f"Data saved to: {QUOTES_RAW_DIR}")
        logger.info(f"Status file: {status.status_file}")


if __name__ == "__main__":
    main()
