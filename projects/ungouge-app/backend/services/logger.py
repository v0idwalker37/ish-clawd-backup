"""
Structured logging configuration for Ungouge.ai
"""
import logging
import sys
from pythonjsonlogger import jsonlogger

# Create logger
logger = logging.getLogger("ungouge")
logger.setLevel(logging.INFO)

# Create console handler with JSON formatter
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={"asctime": "timestamp", "levelname": "level"}
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Helper functions for common log events

def log_auth_success(user_id: str, action: str, ip_address: str = None):
    """Log successful authentication event"""
    logger.info(
        f"auth_{action}_success",
        extra={
            "user_id": user_id,
            "action": action,
            "ip_address": ip_address,
            "event_type": "auth_success"
        }
    )

def _mask_email(email: str) -> str:
    """
    GDPR R-12: Mask email for log output.
    Shows first 3 chars of local part + ***@domain.
    Example: jason.trask@gmail.com → jas***@gmail.com
    """
    if not email or "@" not in email:
        return email or ""
    local, domain = email.rsplit("@", 1)
    visible = local[:3] if len(local) >= 3 else local[:1]
    return f"{visible}***@{domain}"


def log_auth_failure(email: str, action: str, reason: str, ip_address: str = None):
    """Log failed authentication event (email is masked — GDPR R-12)"""
    logger.warning(
        f"auth_{action}_failed",
        extra={
            "email": _mask_email(email),
            "action": action,
            "reason": reason,
            # IP retained — legitimate interest for security (Art. 6(1)(f))
            "ip_address": ip_address,
            "event_type": "auth_failure"
        }
    )

def log_access_denied(resource: str, user_id: str = None, ip_address: str = None):
    """Log access denied event"""
    logger.warning(
        "access_denied",
        extra={
            "resource": resource,
            "user_id": user_id,
            "ip_address": ip_address,
            "event_type": "access_denied"
        }
    )

def log_quote_submission(quote_id: str, user_id: str = None, project_type: str = None, ip_address: str = None):
    """Log quote submission"""
    logger.info(
        "quote_submitted",
        extra={
            "quote_id": quote_id,
            "user_id": user_id,
            "project_type": project_type,
            "ip_address": ip_address,
            "event_type": "quote_submission"
        }
    )

def log_rate_limit_exceeded(endpoint: str, ip_address: str):
    """Log rate limit exceeded"""
    logger.warning(
        "rate_limit_exceeded",
        extra={
            "endpoint": endpoint,
            "ip_address": ip_address,
            "event_type": "rate_limit"
        }
    )

def log_error(error_type: str, message: str, details: dict = None):
    """Log application error"""
    extra = {
        "error_type": error_type,
        "event_type": "error"
    }
    if details:
        extra.update(details)
    
    logger.error(message, extra=extra)
