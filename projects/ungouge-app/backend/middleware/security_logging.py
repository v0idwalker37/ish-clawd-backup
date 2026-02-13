"""
Structured Security Logging
Captures security-relevant events in JSON format for monitoring and audit

GDPR R-12: Email addresses are masked in log output (first 3 chars + ***@domain.com).
IP addresses are retained under legitimate-interest basis (security monitoring, fraud
prevention, abuse detection — GDPR Art. 6(1)(f)).
"""

import json
import logging
import re
import time
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# ---------------------------------------------------------------------------
# R-12  Email masking utility
# ---------------------------------------------------------------------------
_EMAIL_RE = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')


def mask_email_for_log(email: str) -> str:
    """
    Mask an email address for log output.
    Shows first 3 characters of the local part + ***@domain.
    Example: jason.trask@gmail.com  →  jas***@gmail.com
    """
    if not email or "@" not in email:
        return email
    local, domain = email.rsplit("@", 1)
    visible = local[:3] if len(local) >= 3 else local[:1]
    return f"{visible}***@{domain}"


def mask_emails_in_value(value):
    """
    Recursively walk a dict/list/string and mask any email addresses found.
    """
    if isinstance(value, str):
        return _EMAIL_RE.sub(lambda m: mask_email_for_log(m.group(0)), value)
    if isinstance(value, dict):
        return {k: mask_emails_in_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(mask_emails_in_value(item) for item in value)
    return value

# Create dedicated security logger
security_logger = logging.getLogger("ungouge.security")
security_logger.setLevel(logging.INFO)

# JSON formatter for structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, "event"):
            log_data["event"] = record.event
        if hasattr(record, "details"):
            log_data["details"] = record.details
        
        return json.dumps(log_data)


# File handler for security events
def setup_security_logging(log_file: str = "logs/security.jsonl"):
    """Initialize security logging to file"""
    import os
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    handler = logging.FileHandler(log_file)
    handler.setFormatter(JSONFormatter())
    security_logger.addHandler(handler)
    
    # Also log to console in development
    if os.getenv("ENVIRONMENT") != "production":
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JSONFormatter())
        security_logger.addHandler(console_handler)


def log_security_event(
    event_type: str,
    details: Dict[str, Any],
    severity: str = "info",
    ip: Optional[str] = None,
    user_id: Optional[str] = None,
):
    """
    Log a security event
    
    Event types:
    - auth_success, auth_failure
    - rate_limit_exceeded
    - csrf_violation
    - file_upload_rejected
    - input_validation_failed
    - access_denied (BOLA)
    - suspicious_activity
    
    GDPR R-12: Email addresses inside *details* are automatically masked.
    IP addresses are kept (legitimate interest — Art. 6(1)(f): security).
    """
    # R-12: Mask any email addresses embedded in the details dict
    masked_details = mask_emails_in_value(details)

    log_data = {
        "event_type": event_type,
        "severity": severity,
        # IP retained — legitimate interest for security monitoring (Art. 6(1)(f))
        "ip": ip,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **masked_details,
    }
    
    extra = {"event": event_type, "details": log_data}
    
    if severity == "critical":
        security_logger.critical(f"SECURITY: {event_type}", extra=extra)
    elif severity == "warning":
        security_logger.warning(f"SECURITY: {event_type}", extra=extra)
    elif severity == "error":
        security_logger.error(f"SECURITY: {event_type}", extra=extra)
    else:
        security_logger.info(f"SECURITY: {event_type}", extra=extra)


class SecurityAuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all requests with security-relevant data
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract request info
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log security-relevant requests
        if self._is_security_relevant(method, path, response.status_code):
            log_security_event(
                event_type="http_request",
                details={
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "user_agent": user_agent[:200],  # Truncate
                },
                severity=self._get_severity(response.status_code),
                ip=client_ip,
            )
        
        return response
    
    @staticmethod
    def _is_security_relevant(method: str, path: str, status_code: int) -> bool:
        """Determine if a request should be logged"""
        # Always log auth endpoints
        if "/auth/" in path:
            return True
        # Always log errors
        if status_code >= 400:
            return True
        # Log state-changing requests
        if method in ["POST", "PUT", "DELETE", "PATCH"]:
            return True
        return False
    
    @staticmethod
    def _get_severity(status_code: int) -> str:
        """Map HTTP status to severity"""
        if status_code >= 500:
            return "error"
        if status_code in [401, 403]:
            return "warning"
        if status_code == 429:
            return "warning"
        return "info"
