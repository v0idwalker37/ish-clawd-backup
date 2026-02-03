"""
Custom exceptions with user-friendly error messages and recovery suggestions.

These exceptions provide:
1. User-friendly error messages (not technical stack traces)
2. HTTP status codes for API responses
3. Actionable recovery suggestions
4. Detailed logging context for debugging
"""

from typing import Optional, Dict, Any


class UngougeException(Exception):
    """Base exception for all Ungouge.ai errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        suggestion: Optional[str] = None,
        log_context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.suggestion = suggestion or self._default_suggestion()
        self.log_context = log_context or {}
        super().__init__(self.message)
    
    def _default_suggestion(self) -> str:
        """Default recovery suggestion"""
        return "Please try again. If the problem persists, contact support."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to API response format"""
        response = {
            "error": self.message,
            "suggestion": self.suggestion
        }
        if self.log_context:
            # Add safe context info that won't leak sensitive data
            safe_context = {k: v for k, v in self.log_context.items() 
                           if k not in ['password', 'token', 'api_key']}
            response["context"] = safe_context
        return response


# === FILE UPLOAD ERRORS ===

class FileValidationError(UngougeException):
    """File validation failed"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            status_code=400,
            **kwargs
        )
    
    def _default_suggestion(self) -> str:
        return "Please check your file and try again. Supported formats: PDF, PNG, JPG (max 10MB)."


class FileTooLargeError(FileValidationError):
    """File exceeds size limit"""
    
    def __init__(self, size_mb: float, max_mb: int = 10):
        super().__init__(
            message=f"File is too large ({size_mb:.1f}MB). Maximum size is {max_mb}MB.",
            suggestion=(
                f"Please reduce your file size to under {max_mb}MB. "
                "Try compressing the PDF, reducing image resolution, or splitting into multiple files."
            ),
            log_context={"file_size_mb": size_mb, "max_size_mb": max_mb}
        )


class EmptyFileError(FileValidationError):
    """File is empty or contains no data"""
    
    def __init__(self, filename: str):
        super().__init__(
            message=f"The file '{filename}' appears to be empty or corrupt.",
            suggestion=(
                "Please check that your file:\n"
                "• Contains visible text or images\n"
                "• Is not password-protected\n"
                "• Opens correctly on your device\n"
                "• Was not corrupted during upload"
            ),
            log_context={"filename": filename}
        )


class UnsupportedFileTypeError(FileValidationError):
    """File type not supported"""
    
    def __init__(self, content_type: str, filename: str):
        super().__init__(
            message=f"File type '{content_type}' is not supported.",
            suggestion=(
                "Please upload one of the following formats:\n"
                "• PDF documents (.pdf)\n"
                "• Images: PNG (.png), JPEG (.jpg, .jpeg)\n"
                "\n"
                "If you have a different format, try converting it or taking a clear photo/screenshot."
            ),
            log_context={"content_type": content_type, "filename": filename}
        )


class CorruptFileError(FileValidationError):
    """File is corrupt or cannot be read"""
    
    def __init__(self, filename: str, error_details: str):
        super().__init__(
            message=f"Unable to read '{filename}'. The file may be corrupt or password-protected.",
            suggestion=(
                "Please try:\n"
                "• Re-download the original file\n"
                "• Remove password protection if present\n"
                "• Convert to a different format (PDF → image, or vice versa)\n"
                "• Take a clear screenshot/photo of the document"
            ),
            log_context={"filename": filename, "error": error_details}
        )


class TextExtractionError(FileValidationError):
    """Could not extract text from file"""
    
    def __init__(self, filename: str):
        super().__init__(
            message="Could not extract readable text from your file.",
            suggestion=(
                "Please ensure:\n"
                "• Text is clearly visible (not blurry or too small)\n"
                "• Document is not scanned at very low resolution\n"
                "• For images: text is horizontal and well-lit\n"
                "• PDF is not a scan of a blank page\n"
                "\n"
                "If issues persist, try manually entering the quote details instead."
            ),
            log_context={"filename": filename}
        )


class NoLineItemsFoundError(FileValidationError):
    """AI could not find any line items in the quote"""
    
    def __init__(self, filename: str):
        super().__init__(
            message="No pricing or line items found in the uploaded file.",
            suggestion=(
                "This doesn't look like a contractor quote. Please ensure:\n"
                "• The file contains an itemized quote (not just an estimate request)\n"
                "• Prices and line items are clearly visible\n"
                "• The document is complete (not a cover page only)\n"
                "\n"
                "You can also enter the quote details manually using the form."
            ),
            log_context={"filename": filename}
        )


# === AUTHENTICATION ERRORS ===

class AuthenticationError(UngougeException):
    """Authentication failed"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            status_code=401,
            **kwargs
        )
    
    def _default_suggestion(self) -> str:
        return "Please check your credentials and try again."


class InvalidCredentialsError(AuthenticationError):
    """Email or password is incorrect"""
    
    def __init__(self):
        super().__init__(
            message="Invalid email or password.",
            suggestion=(
                "Please check:\n"
                "• Your email is spelled correctly\n"
                "• Your password is correct (passwords are case-sensitive)\n"
                "• You're using the account you registered with\n"
                "\n"
                "Forgot your password? Use the 'Forgot Password' link to reset it."
            )
        )


class AccountInactiveError(AuthenticationError):
    """Account is deactivated"""
    
    def __init__(self):
        super().__init__(
            message="Your account has been deactivated.",
            suggestion=(
                "Your account is not currently active. "
                "Please contact support if you believe this is an error."
            ),
            status_code=403
        )


class EmailNotVerifiedError(AuthenticationError):
    """Email address not verified"""
    
    def __init__(self):
        super().__init__(
            message="Please verify your email address before logging in.",
            suggestion=(
                "Check your inbox for a verification email. "
                "Didn't receive it? Request a new verification email from your account settings."
            ),
            status_code=403
        )


class TokenExpiredError(AuthenticationError):
    """JWT token has expired"""
    
    def __init__(self):
        super().__init__(
            message="Your session has expired.",
            suggestion="Please log in again to continue."
        )


class TokenBlacklistedError(AuthenticationError):
    """Token has been revoked"""
    
    def __init__(self):
        super().__init__(
            message="This session is no longer valid.",
            suggestion="Please log in again."
        )


# === AUTHORIZATION ERRORS ===

class AuthorizationError(UngougeException):
    """User is not authorized to perform this action"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            status_code=403,
            **kwargs
        )
    
    def _default_suggestion(self) -> str:
        return "You don't have permission to access this resource."


class QuoteAccessDeniedError(AuthorizationError):
    """User cannot access this quote"""
    
    def __init__(self, quote_id: str):
        super().__init__(
            message="You don't have permission to view this quote.",
            suggestion=(
                "This quote belongs to another user. "
                "You can only view quotes you've submitted yourself. "
                "If you need access, ask the quote owner to share it with you."
            ),
            log_context={"quote_id": quote_id}
        )


# === PAYMENT ERRORS ===

class PaymentError(UngougeException):
    """Payment processing failed"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            status_code=402,
            **kwargs
        )
    
    def _default_suggestion(self) -> str:
        return "Please check your payment details and try again."


class PaymentMethodError(PaymentError):
    """Payment method is invalid or declined"""
    
    def __init__(self, reason: str):
        suggestions = {
            "card_declined": (
                "Your card was declined. Please:\n"
                "• Check that you have sufficient funds\n"
                "• Verify the card number and expiration date\n"
                "• Try a different payment method\n"
                "• Contact your bank if the problem persists"
            ),
            "expired_card": (
                "Your card has expired. Please:\n"
                "• Update your card expiration date\n"
                "• Use a different payment method"
            ),
            "insufficient_funds": (
                "Insufficient funds. Please:\n"
                "• Check your account balance\n"
                "• Try a different payment method"
            ),
            "invalid_card": (
                "The card number appears to be invalid. Please:\n"
                "• Double-check the card number\n"
                "• Ensure all digits are entered correctly\n"
                "• Try a different card"
            ),
        }
        
        super().__init__(
            message=f"Payment failed: {reason.replace('_', ' ')}",
            suggestion=suggestions.get(reason, self._default_suggestion()),
            log_context={"payment_decline_reason": reason}
        )


class StripeConnectionError(PaymentError):
    """Cannot connect to Stripe"""
    
    def __init__(self, error_msg: str):
        super().__init__(
            message="Payment service is temporarily unavailable.",
            suggestion=(
                "We're experiencing technical difficulties with our payment processor. "
                "Please try again in a few minutes. Your card has not been charged."
            ),
            status_code=503,
            log_context={"stripe_error": error_msg}
        )


# === DATA VALIDATION ERRORS ===

class ValidationError(UngougeException):
    """Input data validation failed"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            status_code=400,
            **kwargs
        )
        self.field = field
    
    def _default_suggestion(self) -> str:
        return "Please check your input and try again."


class MissingRequiredFieldError(ValidationError):
    """Required field is missing"""
    
    def __init__(self, field: str):
        super().__init__(
            message=f"Missing required field: {field}",
            field=field,
            suggestion=f"Please provide a value for '{field}'."
        )


class InvalidDataFormatError(ValidationError):
    """Data format is invalid"""
    
    def __init__(self, field: str, expected_format: str, provided_value: Any):
        super().__init__(
            message=f"Invalid format for '{field}'. Expected {expected_format}.",
            field=field,
            suggestion=(
                f"Please provide '{field}' in the correct format: {expected_format}.\n"
                f"You provided: {provided_value}"
            ),
            log_context={"field": field, "expected": expected_format, "provided": str(provided_value)}
        )


# === RESOURCE ERRORS ===

class ResourceNotFoundError(UngougeException):
    """Requested resource does not exist"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            status_code=404,
            suggestion=(
                f"The {resource_type.lower()} you're looking for doesn't exist or may have been deleted. "
                "Please check the URL and try again."
            ),
            log_context={"resource_type": resource_type, "resource_id": resource_id}
        )


# === RATE LIMITING ERRORS ===

class RateLimitExceededError(UngougeException):
    """Too many requests"""
    
    def __init__(self, limit: str, retry_after: Optional[int] = None):
        retry_msg = f" Please try again in {retry_after} seconds." if retry_after else ""
        
        super().__init__(
            message=f"Rate limit exceeded: {limit}",
            status_code=429,
            suggestion=(
                f"You've made too many requests. {retry_msg}\n"
                "To avoid rate limits:\n"
                "• Wait a few minutes between requests\n"
                "• Sign up for an account for higher limits\n"
                "• Contact support if you need enterprise access"
            ),
            log_context={"limit": limit, "retry_after": retry_after}
        )


# === AI/API ERRORS ===

class AIProcessingError(UngougeException):
    """AI processing failed"""
    
    def __init__(self, service: str, error_details: str):
        super().__init__(
            message=f"AI processing temporarily unavailable ({service}).",
            status_code=503,
            suggestion=(
                "We're experiencing technical difficulties with our AI service. "
                "Please try again in a few minutes, or enter your quote details manually."
            ),
            log_context={"ai_service": service, "error": error_details}
        )


class ExternalAPIError(UngougeException):
    """External API call failed"""
    
    def __init__(self, api_name: str, error_msg: str):
        super().__init__(
            message=f"External service error: {api_name}",
            status_code=503,
            suggestion=(
                f"We couldn't connect to {api_name}. "
                "This is likely a temporary issue. Please try again in a few minutes."
            ),
            log_context={"api": api_name, "error": error_msg}
        )


# === DATABASE ERRORS ===

class DatabaseError(UngougeException):
    """Database operation failed"""
    
    def __init__(self, operation: str, error_msg: str):
        super().__init__(
            message="A database error occurred. Please try again.",
            status_code=500,
            suggestion=(
                "We're experiencing technical difficulties. "
                "Your data has not been saved. Please try again in a few moments."
            ),
            log_context={"operation": operation, "error": error_msg}
        )


class DuplicateResourceError(UngougeException):
    """Resource already exists"""
    
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            message=f"{resource_type} already exists: {identifier}",
            status_code=409,
            suggestion=(
                f"A {resource_type.lower()} with this {identifier} already exists. "
                "Please use a different value or retrieve the existing resource."
            ),
            log_context={"resource_type": resource_type, "identifier": identifier}
        )
