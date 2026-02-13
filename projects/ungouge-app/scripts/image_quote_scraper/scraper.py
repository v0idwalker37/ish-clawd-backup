#!/usr/bin/env python3
"""
Ungouge Image Quote Scraper — Main Orchestrator

Collects contractor quote images/PDFs from multiple sources:
Facebook groups, Reddit, Google Drive, contractor forums, Angi, YouTube.

Usage:
    python3 scripts/image_quote_scraper/scraper.py --sources reddit,gdrive --max-files 20 --test-mode
    python3 scripts/image_quote_scraper/scraper.py --sources all --headless --max-hours 6
    python3 scripts/image_quote_scraper/scraper.py --resume
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
from typing import List, Optional

# Fix imports when run directly
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from scripts.image_quote_scraper.config import (
    DATA_DIR, OUTPUT_DIR, METADATA_DIR, LOGS_DIR,
    RESUME_FILE, ensure_dirs,
)
from scripts.image_quote_scraper.models import SourceType, ScrapeResult
from scripts.image_quote_scraper.extraction.dedup import ImageDedupEngine
from scripts.image_quote_scraper.extraction.classifier import classify_file
from scripts.image_quote_scraper.status import ImageScraperStatus
from scripts.image_quote_scraper.utils.storage import update_master_list

# Force unbuffered output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
else:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)


# === Logging Setup ===
def setup_logging():
    """Set up console + file logging."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, f"image_scraper_{today}.log")

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Console handler (INFO)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    root_logger.addHandler(console)

    # File handler (DEBUG)
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: could not set up file logging: {e}")

    return logging.getLogger(__name__)


ALL_SOURCES = ["facebook", "reddit", "gdrive", "forums", "angi", "youtube"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ungouge Image Quote Scraper — Collects contractor quote images/PDFs"
    )
    parser.add_argument(
        "--sources",
        type=str,
        default="all",
        help="Comma-separated sources: facebook,reddit,gdrive,forums,angi,youtube (or 'all')",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=500,
        help="Stop after collecting N files total",
    )
    parser.add_argument(
        "--max-hours",
        type=float,
        default=6.0,
        help="Maximum runtime in hours",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode (small sample from each source, max 10 files)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last saved state",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--classify",
        action="store_true",
        default=True,
        help="Run classification on downloaded files (default: True)",
    )
    parser.add_argument(
        "--no-classify",
        action="store_true",
        help="Skip classification of downloaded files",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Custom config file path",
    )
    return parser.parse_args()


def load_resume_state() -> dict:
    """Load resume state from file."""
    if os.path.exists(RESUME_FILE):
        try:
            with open(RESUME_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_resume_state(state: dict):
    """Save resume state to file."""
    os.makedirs(os.path.dirname(RESUME_FILE), exist_ok=True)
    try:
        with open(RESUME_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        logging.getLogger(__name__).error(f"Error saving resume state: {e}")


def run_source(source_name: str, dedup: ImageDedupEngine,
               status: ImageScraperStatus, shutdown_event: threading.Event,
               max_files: int, headless: bool = False,
               test_mode: bool = False) -> ScrapeResult:
    """Run a single source scraper."""
    logger = logging.getLogger(__name__)

    # In test mode, limit files per source
    if test_mode:
        source_max = min(max_files, 5)
    else:
        # Allocate files per source based on expected yields
        allocation = {
            "facebook": 0.35,
            "reddit": 0.30,
            "gdrive": 0.10,
            "forums": 0.10,
            "angi": 0.10,
            "youtube": 0.05,
        }
        source_max = max(10, int(max_files * allocation.get(source_name, 0.1)))

    logger.info(f"\n{'='*50}")
    logger.info(f"Starting {source_name.upper()} scraper (max {source_max} files)")
    logger.info(f"{'='*50}")

    try:
        if source_name == "facebook":
            from scripts.image_quote_scraper.sources.facebook import FacebookScraper
            scraper = FacebookScraper(dedup, status, shutdown_event, headless=headless)
            return scraper.run(max_files=source_max)

        elif source_name == "reddit":
            from scripts.image_quote_scraper.sources.reddit import RedditImageScraper
            scraper = RedditImageScraper(dedup, status, shutdown_event)
            return scraper.run(max_files=source_max)

        elif source_name == "gdrive":
            from scripts.image_quote_scraper.sources.gdrive import GDriveScraper
            scraper = GDriveScraper(dedup, status, shutdown_event)
            return scraper.run(max_files=source_max)

        elif source_name == "forums":
            from scripts.image_quote_scraper.sources.forums import ForumScraper
            scraper = ForumScraper(dedup, status, shutdown_event)
            return scraper.run(max_files=source_max)

        elif source_name == "angi":
            from scripts.image_quote_scraper.sources.angi import AngiScraper
            scraper = AngiScraper(dedup, status, shutdown_event, headless=headless)
            return scraper.run(max_files=source_max)

        elif source_name == "youtube":
            from scripts.image_quote_scraper.sources.youtube import YouTubeScraper
            scraper = YouTubeScraper(dedup, status, shutdown_event)
            return scraper.run(max_files=source_max)

        else:
            logger.warning(f"Unknown source: {source_name}")
            return ScrapeResult(source=SourceType.REDDIT, status="unknown_source")

    except Exception as e:
        logger.error(f"Error running {source_name}: {e}", exc_info=True)
        return ScrapeResult(
            source=SourceType(source_name) if source_name in [s.value for s in SourceType] else SourceType.REDDIT,
            status=f"error: {str(e)[:100]}"
        )


def classify_collected_files(status: ImageScraperStatus,
                             results: List[ScrapeResult],
                             use_api: bool = True):
    """Run classification on all collected files."""
    logger = logging.getLogger(__name__)
    logger.info("\n" + "="*50)
    logger.info("CLASSIFYING COLLECTED FILES")
    logger.info("="*50)

    total = 0
    classified = 0

    for result in results:
        for qf in result.files:
            total += 1
            if not qf.file_path or not os.path.exists(qf.file_path):
                continue

            try:
                cl_result, reason = classify_file(qf.file_path, use_api=use_api)
                qf.classification = cl_result
                qf.classification_reason = reason
                status.record_classification(cl_result.value)
                classified += 1

                if cl_result.value == "quote":
                    logger.info(f"  ✅ QUOTE: {os.path.basename(qf.file_path)} ({reason})")
                elif cl_result.value == "not_quote":
                    logger.info(f"  ❌ NOT QUOTE: {os.path.basename(qf.file_path)} ({reason})")
                else:
                    logger.info(f"  ❓ UNSURE: {os.path.basename(qf.file_path)} ({reason})")

            except Exception as e:
                logger.error(f"  Classification error for {qf.file_path}: {e}")

    logger.info(f"Classified {classified}/{total} files")


def main():
    logger = setup_logging()
    args = parse_args()

    # Parse sources
    if args.sources.lower() == "all":
        sources = ALL_SOURCES
    else:
        sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
        # Validate
        for s in sources:
            if s not in ALL_SOURCES:
                logger.error(f"Unknown source: {s}. Valid: {', '.join(ALL_SOURCES)}")
                sys.exit(1)

    # Test mode overrides
    if args.test_mode:
        max_files = min(args.max_files, 10)
        max_hours = min(args.max_hours, 0.5)
        logger.info("🧪 TEST MODE — limited to 10 files, 30 minutes")
    else:
        max_files = args.max_files
        max_hours = args.max_hours

    max_seconds = max_hours * 3600
    headless = args.headless
    do_classify = args.classify and not args.no_classify

    logger.info("=" * 60)
    logger.info("🎯 UNGOUGE IMAGE QUOTE SCRAPER")
    logger.info("=" * 60)
    logger.info(f"  Sources: {', '.join(sources)}")
    logger.info(f"  Max files: {max_files}")
    logger.info(f"  Max hours: {max_hours}")
    logger.info(f"  Headless: {headless}")
    logger.info(f"  Classify: {do_classify}")
    logger.info(f"  Test mode: {args.test_mode}")
    logger.info("=" * 60)

    # Setup
    ensure_dirs()

    # Resume handling
    resume_state = {}
    if args.resume:
        resume_state = load_resume_state()
        if resume_state:
            completed = resume_state.get("completed_sources", [])
            sources = [s for s in sources if s not in completed]
            logger.info(f"Resuming: skipping completed sources: {completed}")
            logger.info(f"Remaining sources: {sources}")
        else:
            logger.info("No resume state found, starting fresh")

    # Initialize
    dedup = ImageDedupEngine()
    status = ImageScraperStatus()
    shutdown_event = threading.Event()

    logger.info(f"Dedup DB has {dedup.get_total_seen()} files tracked")

    # Graceful shutdown
    def signal_handler(signum, frame):
        logger.info("\n⚠️ Shutdown signal received. Finishing up...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start status tracking
    status.start_periodic_write()

    start_time = time.time()
    total_downloaded = 0
    all_results: List[ScrapeResult] = []
    completed_sources = resume_state.get("completed_sources", [])

    try:
        for source_name in sources:
            if shutdown_event.is_set():
                break

            # Check time limit
            elapsed = time.time() - start_time
            if elapsed >= max_seconds:
                logger.info(f"⏱️ Time limit reached ({max_hours}h)")
                break

            # Check file limit
            remaining = max_files - total_downloaded
            if remaining <= 0:
                logger.info(f"📦 File limit reached ({max_files})")
                break

            # Run the source
            result = run_source(
                source_name, dedup, status, shutdown_event,
                max_files=remaining, headless=headless,
                test_mode=args.test_mode,
            )

            all_results.append(result)
            total_downloaded += result.files_downloaded
            completed_sources.append(source_name)

            # Update master list
            for qf in result.files:
                update_master_list(qf)

            # Save resume state
            save_resume_state({
                "completed_sources": completed_sources,
                "last_source": source_name,
                "total_downloaded": total_downloaded,
                "paused_at": datetime.utcnow().isoformat(),
            })

            logger.info(f"✅ {source_name}: downloaded {result.files_downloaded} files "
                        f"(total: {total_downloaded})")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        # Classification pass
        if do_classify and all_results:
            try:
                classify_collected_files(status, all_results, use_api=True)
            except Exception as e:
                logger.error(f"Classification error: {e}")

        # Final summary
        status.stop()
        status.log_summary()
        dedup.close()

        elapsed = time.time() - start_time
        logger.info(f"\n{'='*60}")
        logger.info(f"🏁 SCRAPER COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"  Total files: {total_downloaded}")
        logger.info(f"  Time: {elapsed:.0f}s ({elapsed/3600:.1f}h)")
        logger.info(f"  Output: {OUTPUT_DIR}")
        logger.info(f"  Status: {status.status_file}")
        logger.info(f"  Log: {LOGS_DIR}")
        logger.info(f"{'='*60}")

    # Clean up browser if used
    try:
        from scripts.image_quote_scraper.utils.browser import close_browser
        close_browser()
    except Exception:
        pass


if __name__ == "__main__":
    main()
