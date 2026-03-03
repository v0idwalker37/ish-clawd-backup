"""
Async email notification service for GougeAlert

Design choice: aiosmtplib + email.mime
  - aiosmtplib is the async counterpart to smtplib — battle-tested, zero vendor lock-in
  - Works with any SMTP provider (Gmail, SES, Postmark, self-hosted)
  - No paid SDK dependency (resend is nice but ties you to one vendor)

Features:
  - Non-blocking: callers use asyncio.create_task() so API responses aren't delayed
  - Rate limiting: max 3 emails per user per hour (in-memory counter)
  - Graceful failure: email errors are logged, never crash the request
  - Dev mode: logs email to console instead of sending via SMTP
  - Template rendering: loads HTML files from email-templates/ and replaces {{variables}}
"""

import asyncio
import logging
import os
import time
from collections import defaultdict
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

import aiosmtplib

logger = logging.getLogger("ungouge.email")

# ── Configuration ────────────────────────────────────────────────────────

DEV_MODE = os.getenv("EMAIL_DEV_MODE", "false").lower() == "true"

# Resend SMTP defaults — override via env if needed
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.resend.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "resend")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "") or os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@gougealert.com")
FROM_NAME = os.getenv("FROM_NAME", "GougeAlert")

# Template directory: <project>/email-templates/
TEMPLATE_DIR = Path(__file__).parent.parent.parent / "email-templates"

if DEV_MODE:
    logger.warning(
        "⚠️  EMAIL_DEV_MODE is ON — emails will be logged to console, NOT sent via SMTP. "
        "Set EMAIL_DEV_MODE=false and configure SMTP_* env vars for production."
    )

# ── Rate Limiting (in-memory, per-process) ───────────────────────────────
# Tracks: { user_email: [timestamp, timestamp, ...] }
# Max 3 emails per user per rolling hour window.

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_MAX = 3
_RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds


def _check_rate_limit(user_email: str) -> bool:
    """
    Returns True if the email can be sent (under limit).
    Returns False if rate-limited.
    """
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW

    # Prune old entries
    _rate_limit_store[user_email] = [
        ts for ts in _rate_limit_store[user_email] if ts > window_start
    ]

    if len(_rate_limit_store[user_email]) >= _RATE_LIMIT_MAX:
        return False

    _rate_limit_store[user_email].append(now)
    return True


# ── Template Loading ─────────────────────────────────────────────────────

def _load_template(filename: str, **variables) -> str:
    """
    Load an HTML template from email-templates/ and replace {{variables}}.

    Handles simple mustache-style conditionals:
      {{#name}} ... {{/name}}  → included if 'name' is truthy, stripped otherwise
    """
    template_path = TEMPLATE_DIR / filename

    if not template_path.exists():
        logger.error(f"Email template not found: {template_path}")
        return f"<html><body><p>Email template '{filename}' not found.</p></body></html>"

    html = template_path.read_text(encoding="utf-8")

    # Handle {{#var}}...{{/var}} conditional blocks
    import re
    for key, value in variables.items():
        pattern = re.compile(r"\{\{#" + re.escape(key) + r"\}\}(.*?)\{\{/" + re.escape(key) + r"\}\}", re.DOTALL)
        if value:
            # Keep the inner content, replace {{key}} inside it too
            html = pattern.sub(r"\1", html)
        else:
            # Remove the entire block
            html = pattern.sub("", html)

    # Replace {{variable}} placeholders
    for key, value in variables.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))

    return html


# ── Core Sender ──────────────────────────────────────────────────────────

async def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Send an email via async SMTP or log to console in dev mode.

    Returns True on success, False on failure. Never raises.
    """
    if DEV_MODE:
        logger.info(
            f"[DEV MODE] Email → {to_email}\n"
            f"  From: {FROM_NAME} <{FROM_EMAIL}>\n"
            f"  Subject: {subject}\n"
            f"  Body: {html_body[:300]}..."
        )
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Reply-To"] = FROM_EMAIL
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        if SMTP_PORT == 465:
            # SSL (Resend, etc.)
            await aiosmtplib.send(
                msg,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USER,
                password=SMTP_PASSWORD,
                use_tls=True,
            )
        else:
            # STARTTLS (Gmail, etc.)
            await aiosmtplib.send(
                msg,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USER,
                password=SMTP_PASSWORD,
                start_tls=True,
            )

        logger.info(f"Email sent to {to_email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}", exc_info=True)
        return False


# ── Public API ───────────────────────────────────────────────────────────

async def send_welcome_email(user_email: str, user_name: str) -> bool:
    """
    Send welcome email after registration.
    Uses email-templates/welcome.html.
    """
    if not _check_rate_limit(user_email):
        logger.warning(f"Rate limited: welcome email to {user_email}")
        return False

    html = _load_template(
        "welcome.html",
        name=user_name,
        current_year=datetime.utcnow().year,
    )

    return await _send_email(
        to_email=user_email,
        subject="Welcome to GougeAlert — Know Before You Pay",
        html_body=html,
    )


async def send_receipt_email(
    user_email: str,
    user_name: str,
    amount: str,
    quote_id: str,
    date: str,
    payment_method: str = "Credit Card",
    report_url: Optional[str] = None,
) -> bool:
    """
    Send payment receipt after successful checkout.
    Uses email-templates/receipt.html.

    Args:
        amount: Formatted string like "$19.99"
        quote_id: The quote/report ID
        date: Human-readable date string
        payment_method: e.g. "Visa ending in 4242"
        report_url: Link to view the report
    """
    if not _check_rate_limit(user_email):
        logger.warning(f"Rate limited: receipt email to {user_email}")
        return False

    frontend_url = os.getenv("FRONTEND_URL", "https://gougealert.com")
    if report_url is None:
        report_url = f"{frontend_url}/report/{quote_id}"

    html = _load_template(
        "receipt.html",
        report_id=quote_id,
        payment_date=date,
        payment_method=payment_method,
        report_url=report_url,
        current_year=datetime.utcnow().year,
    )

    return await _send_email(
        to_email=user_email,
        subject=f"Your GougeAlert Receipt — {amount}",
        html_body=html,
    )


async def send_report_ready_email(
    user_email: str,
    user_name: str,
    quote_id: str,
    report_url: Optional[str] = None,
    total_quoted: Optional[str] = None,
    fair_range_low: Optional[str] = None,
    fair_range_high: Optional[str] = None,
    potential_savings: Optional[str] = None,
) -> bool:
    """
    Notify user that their quote analysis report is ready.
    Uses email-templates/report-ready.html.
    """
    if not _check_rate_limit(user_email):
        logger.warning(f"Rate limited: report-ready email to {user_email}")
        return False

    frontend_url = os.getenv("FRONTEND_URL", "https://gougealert.com")
    if report_url is None:
        report_url = f"{frontend_url}/report/{quote_id}"

    html = _load_template(
        "report-ready.html",
        report_url=report_url,
        total_quoted=total_quoted or "See report",
        fair_range_low=fair_range_low or "—",
        fair_range_high=fair_range_high or "—",
        potential_savings=potential_savings or "—",
        current_year=datetime.utcnow().year,
    )

    return await _send_email(
        to_email=user_email,
        subject="Your Quote Analysis is Ready — GougeAlert",
        html_body=html,
    )


# ── Legacy-compatible wrappers ───────────────────────────────────────────
# These maintain backward compatibility with the old synchronous API
# used by mfa_service.py and other existing callers.

def send_mfa_code(
    to_email: str,
    user_name: str,
    code: str,
    expiry_minutes: int = 10,
) -> bool:
    """
    Send MFA verification code (synchronous wrapper for existing callers).
    Uses inline HTML template — no external file needed.
    """
    subject = f"Your GougeAlert verification code: {code}"

    html_body = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px;">
  <div style="max-width: 480px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <div style="text-align: center; margin-bottom: 30px;">
      <h1 style="color: #2563eb; font-size: 24px; margin: 0;">GougeAlert</h1>
    </div>
    <p style="color: #374151; font-size: 16px; line-height: 1.6;">Hi {user_name},</p>
    <p style="color: #374151; font-size: 16px; line-height: 1.6;">Your verification code is:</p>
    <div style="background: #f0f9ff; border: 2px solid #2563eb; border-radius: 8px; padding: 20px; text-align: center; margin: 24px 0;">
      <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #1e40af;">{code}</span>
    </div>
    <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
      This code expires in {expiry_minutes} minutes. If you didn't request this code, you can safely ignore this email.
    </p>
    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
    <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 0;">
      This is an automated security email from GougeAlert<br>We never sell your data. Ever.
    </p>
  </div>
</body></html>'''

    if DEV_MODE:
        logger.info(
            f"[DEV MODE] MFA Email → {to_email}\n"
            f"  Subject: {subject}\n"
            f"  Code: {code}"
        )
        return True

    try:
        import smtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        if SMTP_PORT == 465:
            # SSL (Resend, etc.)
            import ssl
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # STARTTLS (Gmail, etc.)
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

        logger.info(f"MFA code sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send MFA code to {to_email}: {e}", exc_info=True)
        return False


def send_password_reset(
    to_email: str,
    user_name: str,
    reset_url: str,
    expiry_hours: int = 24,
) -> bool:
    """
    Send password reset email (synchronous wrapper — kept for existing callers).
    """
    subject = "Reset your GougeAlert password"

    html_body = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px;">
  <div style="max-width: 480px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <div style="text-align: center; margin-bottom: 30px;">
      <h1 style="color: #2563eb; font-size: 24px; margin: 0;">GougeAlert</h1>
    </div>
    <p style="color: #374151; font-size: 16px; line-height: 1.6;">Hi {user_name},</p>
    <p style="color: #374151; font-size: 16px; line-height: 1.6;">
      We received a request to reset your password. Click the button below to choose a new one:
    </p>
    <div style="text-align: center; margin: 30px 0;">
      <a href="{reset_url}" style="display: inline-block; background-color: #2563eb; color: #ffffff; font-size: 16px; font-weight: 700; text-decoration: none; padding: 14px 48px; border-radius: 6px;">
        Reset Password
      </a>
    </div>
    <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
      This link expires in {expiry_hours} hours. If you didn't request this, you can safely ignore this email.
    </p>
    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
    <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 0;">
      This is an automated security email from GougeAlert
    </p>
  </div>
</body></html>'''

    if DEV_MODE:
        logger.info(
            f"[DEV MODE] Password Reset Email → {to_email}\n"
            f"  Subject: {subject}\n"
            f"  Reset URL: {reset_url}"
        )
        return True

    try:
        import smtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        if SMTP_PORT == 465:
            # SSL (Resend, etc.)
            import ssl
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # STARTTLS (Gmail, etc.)
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

        logger.info(f"Password reset email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}", exc_info=True)
        return False
