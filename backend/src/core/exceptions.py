"""Custom exceptions for the application.

Enterprise-grade exception hierarchy with:
- Typed error codes for client handling
- Correlation IDs for distributed tracing
- Retry hints for retryable errors
- RFC 7807 Problem Details compatibility
"""

from datetime import datetime
from typing import Any

from src.core.error_codes import ErrorCode, get_error_metadata


class AppException(Exception):
    """Base application exception with enterprise features.

    Attributes:
        message: Human-readable error message
        error_code: Typed error code from catalog
        status_code: HTTP status code
        details: Additional error context
        correlation_id: Request correlation ID for tracing
        retry_after: Seconds to wait before retry (for retryable errors)
        timestamp: When the error occurred
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        retry_after: int | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.correlation_id = correlation_id
        self.retry_after = retry_after
        self.timestamp = datetime.utcnow()

        # Use metadata-defined status code if not explicitly provided
        metadata = get_error_metadata(error_code)
        self.status_code = status_code or metadata.get("http_status", 500)

        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert to RFC 7807 Problem Details format."""
        result = {
            "type": f"https://api.processmining.io/errors/{self.error_code.value}",
            "title": get_error_metadata(self.error_code).get("title", "Error"),
            "status": self.status_code,
            "detail": self.message,
            "error_code": self.error_code.value,
            "timestamp": self.timestamp.isoformat(),
            **self.details,
        }

        if self.correlation_id:
            result["correlation_id"] = self.correlation_id

        if self.retry_after:
            result["retry_after"] = self.retry_after

        return result


# =============================================================================
# Validation Errors (422)
# =============================================================================


class ValidationError(AppException):
    """Validation failed."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        error_code: ErrorCode = ErrorCode.VALIDATION_FAILED,
        **kwargs,
    ):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=422,
            details=details,
            **kwargs,
        )


class InvalidInputError(ValidationError):
    """Invalid input data."""

    def __init__(self, message: str, field: str | None = None, **kwargs):
        super().__init__(
            message=message,
            field=field,
            error_code=ErrorCode.INVALID_INPUT,
            **kwargs,
        )


class InvalidFileError(ValidationError):
    """Invalid file upload."""

    def __init__(
        self,
        message: str,
        filename: str | None = None,
        expected_types: list[str] | None = None,
        **kwargs,
    ):
        details = {}
        if filename:
            details["filename"] = filename
        if expected_types:
            details["expected_types"] = expected_types

        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_FILE_TYPE,
            **kwargs,
        )
        self.details.update(details)


# =============================================================================
# Resource Errors (404, 409)
# =============================================================================


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(
        self,
        resource: str,
        resource_id: str,
        error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
        **kwargs,
    ):
        super().__init__(
            message=f"{resource} not found: {resource_id}",
            error_code=error_code,
            status_code=404,
            details={"resource": resource, "id": resource_id},
            **kwargs,
        )


class ProjectNotFoundError(NotFoundError):
    """Project not found."""

    def __init__(self, project_id: str, **kwargs):
        super().__init__(
            resource="Project",
            resource_id=project_id,
            error_code=ErrorCode.PROJECT_NOT_FOUND,
            **kwargs,
        )


class ProcessNotFoundError(NotFoundError):
    """Process (event log) not found."""

    def __init__(self, process_id: str, **kwargs):
        super().__init__(
            resource="Process",
            resource_id=process_id,
            error_code=ErrorCode.PROCESS_NOT_FOUND,
            **kwargs,
        )


class ModelNotFoundError(NotFoundError):
    """Process model not found."""

    def __init__(self, model_id: str, **kwargs):
        super().__init__(
            resource="Model",
            resource_id=model_id,
            error_code=ErrorCode.MODEL_NOT_FOUND,
            **kwargs,
        )


class ConflictError(AppException):
    """Resource conflict (e.g., duplicate, concurrent modification)."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.RESOURCE_CONFLICT,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=409,
            **kwargs,
        )


class ConcurrencyError(ConflictError):
    """Concurrent modification detected."""

    def __init__(
        self,
        resource: str,
        resource_id: str,
        current_version: str | None = None,
        **kwargs,
    ):
        details = {"resource": resource, "id": resource_id}
        if current_version:
            details["current_version"] = current_version

        super().__init__(
            message=f"{resource} was modified by another request",
            error_code=ErrorCode.CONCURRENCY_CONFLICT,
            **kwargs,
        )
        self.details.update(details)


# =============================================================================
# Processing Errors (500, 504)
# =============================================================================


class ProcessingError(AppException):
    """Processing failed."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.PROCESSING_FAILED,
        details: dict | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=500,
            details=details,
            **kwargs,
        )


class DiscoveryError(ProcessingError):
    """Process discovery failed."""

    def __init__(self, message: str, miner_type: str | None = None, **kwargs):
        details = {}
        if miner_type:
            details["miner_type"] = miner_type
        super().__init__(
            message=message,
            error_code=ErrorCode.DISCOVERY_FAILED,
            details=details,
            **kwargs,
        )


class ConformanceError(ProcessingError):
    """Conformance checking failed."""

    def __init__(self, message: str, method: str | None = None, **kwargs):
        details = {}
        if method:
            details["method"] = method
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFORMANCE_CHECK_FAILED,
            details=details,
            **kwargs,
        )


class IngestionError(ProcessingError):
    """Data ingestion failed."""

    def __init__(
        self,
        message: str,
        filename: str | None = None,
        line_number: int | None = None,
        **kwargs,
    ):
        details = {}
        if filename:
            details["filename"] = filename
        if line_number:
            details["line_number"] = line_number
        super().__init__(
            message=message,
            error_code=ErrorCode.INGESTION_FAILED,
            details=details,
            **kwargs,
        )


class TimeoutError(ProcessingError):
    """Operation timed out."""

    def __init__(
        self,
        message: str = "Operation timed out",
        operation: str | None = None,
        timeout_seconds: float | None = None,
        **kwargs,
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(
            message=message,
            error_code=ErrorCode.PROCESSING_TIMEOUT,
            details=details,
            **kwargs,
        )
        self.status_code = 504


class InsufficientDataError(ProcessingError):
    """Not enough data for the requested operation."""

    def __init__(
        self,
        message: str,
        required: int | None = None,
        actual: int | None = None,
        **kwargs,
    ):
        details = {}
        if required:
            details["required"] = required
        if actual:
            details["actual"] = actual
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_DATA,
            details=details,
            **kwargs,
        )


# =============================================================================
# External Service Errors (502, 503)
# =============================================================================


class ExternalServiceError(AppException):
    """External service failed."""

    def __init__(
        self,
        message: str,
        service: str,
        error_code: ErrorCode = ErrorCode.EXTERNAL_SERVICE_ERROR,
        retry_after: int | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=502,
            details={"service": service},
            retry_after=retry_after,
            **kwargs,
        )


class PM4PyError(ExternalServiceError):
    """PM4Py operation failed."""

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        original_error: str | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            service="pm4py",
            error_code=ErrorCode.PM4PY_ERROR,
            **kwargs,
        )
        if operation:
            self.details["operation"] = operation
        if original_error:
            self.details["original_error"] = original_error


class DatabaseError(ExternalServiceError):
    """Database operation failed."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            service="database",
            error_code=ErrorCode.DATABASE_ERROR,
            **kwargs,
        )


class ServiceUnavailableError(ExternalServiceError):
    """Required service is unavailable."""

    def __init__(
        self,
        service: str,
        retry_after: int = 30,
        **kwargs,
    ):
        super().__init__(
            message=f"{service} is temporarily unavailable",
            service=service,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            retry_after=retry_after,
            **kwargs,
        )
        self.status_code = 503


# =============================================================================
# Authentication & Authorization (401, 403)
# =============================================================================


class AuthenticationError(AppException):
    """Authentication failed (invalid or missing credentials)."""

    def __init__(
        self,
        message: str = "Authentication required",
        error_code: ErrorCode = ErrorCode.AUTHENTICATION_FAILED,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=401,
            **kwargs,
        )


class AuthorizationError(AppException):
    """Authorization failed (insufficient permissions)."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        error_code: ErrorCode = ErrorCode.AUTHORIZATION_FAILED,
        required_permission: str | None = None,
        **kwargs,
    ):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=403,
            details=details,
            **kwargs,
        )


class ForbiddenError(AuthorizationError):
    """Forbidden action (alias for AuthorizationError)."""
    pass


# =============================================================================
# Rate Limiting (429)
# =============================================================================


class RateLimitError(AppException):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: int | None = None,
        window_seconds: int | None = None,
        retry_after: int = 60,
        **kwargs,
    ):
        details = {}
        if limit:
            details["limit"] = limit
        if window_seconds:
            details["window_seconds"] = window_seconds

        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            details=details,
            retry_after=retry_after,
            **kwargs,
        )
