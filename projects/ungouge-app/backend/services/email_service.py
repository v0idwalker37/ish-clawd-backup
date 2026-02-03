"""
Email notification service for Ungouge.ai
Sends professional, anti-lead-gen HTML emails with dev mode logging
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Dev mode toggle - set to False to enable real SMTP
DEV_MODE = os.getenv("EMAIL_DEV_MODE", "true").lower() == "true"

# SMTP Configuration (for production)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@ungouge.ai")
FROM_NAME = os.getenv("FROM_NAME", "Ungouge.ai")

# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def _load_template(template_name: str, **kwargs) -> str:
    """Load and render HTML email template"""
    template_path = TEMPLATE_DIR / template_name
    
    if not template_path.exists():
        logger.error(f"Template not found: {template_path}")
        return f"<html><body><p>Template {template_name} not found</p></body></html>"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Simple template variable replacement
    for key, value in kwargs.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    
    return template


def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Send email via SMTP or log to console in dev mode
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML email body
        
    Returns:
        bool: True if sent successfully (or logged in dev mode)
    """
    if DEV_MODE:
        logger.info("=" * 80)
        logger.info(f"[DEV MODE] Email would be sent:")
        logger.info(f"To: {to_email}")
        logger.info(f"From: {FROM_NAME} <{FROM_EMAIL}>")
        logger.info(f"Subject: {subject}")
        logger.info("-" * 80)
        logger.info("HTML Body Preview:")
        logger.info(html_body[:500] + "..." if len(html_body) > 500 else html_body)
        logger.info("=" * 80)
        return True
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email
        
        # Attach HTML body
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Send via SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def send_welcome_email(to_email: str, user_name: str) -> bool:
    """
    Send welcome email to new user
    
    Anti-lead-gen messaging: No upsells, no marketing pressure.
    Just a genuine welcome to a service that respects your time.
    
    Args:
        to_email: User's email address
        user_name: User's display name
        
    Returns:
        bool: True if sent successfully
    """
    subject = "Welcome to Ungouge.ai – Research Without the Runaround"
    
    html_body = _load_template(
        "welcome.html",
        user_name=user_name,
        current_year=2024
    )
    
    return _send_email(to_email, subject, html_body)


def send_report_ready(
    to_email: str,
    user_name: str,
    report_title: str,
    report_url: str,
    preview_text: Optional[str] = None
) -> bool:
    """
    Notify user that their research report is ready
    
    Anti-lead-gen: Just the facts. Your report is done. Here's the link.
    No "upgrade now" nonsense.
    
    Args:
        to_email: User's email address
        user_name: User's display name
        report_title: Title of the completed report
        report_url: Direct link to view the report
        preview_text: Optional preview snippet
        
    Returns:
        bool: True if sent successfully
    """
    subject = f"Your research report is ready: {report_title}"
    
    html_body = _load_template(
        "report_ready.html",
        user_name=user_name,
        report_title=report_title,
        report_url=report_url,
        preview_text=preview_text or "Your comprehensive research analysis is complete.",
        current_year=2024
    )
    
    return _send_email(to_email, subject, html_body)


def send_password_reset(
    to_email: str,
    user_name: str,
    reset_url: str,
    expiry_hours: int = 24
) -> bool:
    """
    Send password reset link
    
    Anti-lead-gen: Security-focused, no marketing junk mixed into
    a sensitive security email.
    
    Args:
        to_email: User's email address
        user_name: User's display name
        reset_url: Password reset link with token
        expiry_hours: How many hours until link expires
        
    Returns:
        bool: True if sent successfully
    """
    subject = "Reset your Ungouge.ai password"
    
    html_body = _load_template(
        "password_reset.html",
        user_name=user_name,
        reset_url=reset_url,
        expiry_hours=expiry_hours,
        current_year=2024
    )
    
    return _send_email(to_email, subject, html_body)


def send_weekly_digest(
    to_email: str,
    user_name: str,
    reports_this_week: int,
    total_reports: int,
    recent_reports: list,
    insights: Optional[str] = None
) -> bool:
    """
    Send weekly activity digest
    
    Anti-lead-gen: Optional digest (user controls frequency).
    Shows your activity, not sales pitches. Unsubscribe is prominent.
    
    Args:
        to_email: User's email address
        user_name: User's display name
        reports_this_week: Number of reports created this week
        total_reports: Total lifetime reports
        recent_reports: List of dicts with 'title' and 'url' keys
        insights: Optional personalized insights text
        
    Returns:
        bool: True if sent successfully
    """
    subject = f"Your week in research – {reports_this_week} reports created"
    
    # Build recent reports HTML list
    reports_html = ""
    for report in recent_reports[:5]:  # Max 5 recent
        reports_html += f'''
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #e0e0e0;">
                <a href="{report.get('url', '#')}" style="color: #2563eb; text-decoration: none; font-weight: 500;">
                    {report.get('title', 'Untitled Report')}
                </a>
            </td>
        </tr>
        '''
    
    html_body = _load_template(
        "weekly_digest.html",
        user_name=user_name,
        reports_this_week=reports_this_week,
        total_reports=total_reports,
        reports_html=reports_html,
        insights=insights or "Keep up the great research work!",
        current_year=2024
    )
    
    return _send_email(to_email, subject, html_body)


# Convenience function for testing
def test_all_emails():
    """Send all email types to console (dev mode only)"""
    if not DEV_MODE:
        logger.warning("test_all_emails() should only be run in DEV_MODE")
        return
    
    print("\n📧 Testing all email templates...\n")
    
    send_welcome_email("user@example.com", "Alex")
    
    send_report_ready(
        "user@example.com",
        "Alex",
        "Best Dishwashers Under $600",
        "https://ungouge.ai/reports/abc123",
        "We analyzed 47 models to find the best value options."
    )
    
    send_password_reset(
        "user@example.com",
        "Alex",
        "https://ungouge.ai/reset-password?token=xyz789"
    )
    
    send_weekly_digest(
        "user@example.com",
        "Alex",
        3,
        12,
        [
            {"title": "Best Running Shoes 2024", "url": "https://ungouge.ai/reports/1"},
            {"title": "Laptop Buying Guide", "url": "https://ungouge.ai/reports/2"},
            {"title": "Coffee Maker Comparison", "url": "https://ungouge.ai/reports/3"},
        ],
        "You've been researching a lot of tech this week!"
    )
    
    print("\n✅ All email templates tested!\n")


if __name__ == "__main__":
    # Test emails in dev mode
    logging.basicConfig(level=logging.INFO)
    test_all_emails()
