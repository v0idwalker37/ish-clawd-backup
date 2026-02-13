"""Playwright browser management for the Image Quote Scraper."""

import os
import json
import logging
import random
from typing import Optional

from ..config import (
    HEADLESS, BROWSER_TIMEOUT, USER_AGENTS,
    FACEBOOK_COOKIES_FILE, SECRETS_DIR,
)

logger = logging.getLogger(__name__)

# Singleton browser context
_playwright = None
_browser = None


def get_playwright():
    """Get or create the Playwright instance."""
    global _playwright
    if _playwright is None:
        from playwright.sync_api import sync_playwright
        _playwright = sync_playwright().start()
    return _playwright


def create_browser(headless: Optional[bool] = None):
    """Create a new browser instance with stealth settings."""
    global _browser
    if _browser is not None:
        return _browser

    pw = get_playwright()
    h = headless if headless is not None else HEADLESS

    _browser = pw.chromium.launch(
        headless=h,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
        ],
    )

    logger.info(f"Browser launched (headless={h})")
    return _browser


def create_stealth_context(browser=None, user_agent: str = None):
    """Create a browser context with anti-detection measures."""
    if browser is None:
        browser = create_browser()

    ua = user_agent or random.choice(USER_AGENTS)

    context = browser.new_context(
        user_agent=ua,
        viewport={"width": 1366, "height": 768},
        locale="en-US",
        timezone_id="America/New_York",
        color_scheme="light",
        # Add some common permissions
        permissions=["geolocation"],
        geolocation={"latitude": 40.7128, "longitude": -74.0060},  # NYC
    )

    # Add anti-detection scripts
    context.add_init_script("""
        // Override navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Override navigator.plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Override navigator.languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        // Override chrome detection
        window.chrome = {
            runtime: {},
        };
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)

    return context


def save_cookies(context, filepath: str = None):
    """Save browser cookies for session reuse."""
    filepath = filepath or FACEBOOK_COOKIES_FILE
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        cookies = context.cookies()
        with open(filepath, "w") as f:
            json.dump(cookies, f, indent=2)
        logger.info(f"Saved {len(cookies)} cookies to {filepath}")
    except Exception as e:
        logger.error(f"Error saving cookies: {e}")


def load_cookies(context, filepath: str = None) -> bool:
    """Load previously saved cookies."""
    filepath = filepath or FACEBOOK_COOKIES_FILE
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, "r") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        logger.info(f"Loaded {len(cookies)} cookies from {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error loading cookies: {e}")
        return False


def close_browser():
    """Close browser and Playwright."""
    global _browser, _playwright
    if _browser:
        try:
            _browser.close()
        except Exception:
            pass
        _browser = None
    if _playwright:
        try:
            _playwright.stop()
        except Exception:
            pass
        _playwright = None
