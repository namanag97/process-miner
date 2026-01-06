"""User-friendly error message templates.

Provides consistent, actionable error messages for API responses.
Messages are designed to be:
- Clear and concise
- Actionable (what to do next)
- Non-technical (avoid internal details)
"""

from typing import Any


# =============================================================================
# Message Templates
# =============================================================================


class ErrorMessages:
    """Centralized error message templates."""

    # -------------------------------------------------------------------------
    # Resource Errors
    # -------------------------------------------------------------------------

    @staticmethod
    def resource_not_found(resource_type: str, resource_id: str) -> str:
        """Resource not found message."""
        return f"The {resource_type.lower()} you requested could not be found. Please verify the ID '{resource_id}' is correct."

    @staticmethod
    def resource_already_exists(resource_type: str, identifier: str) -> str:
        """Resource already exists message."""
        return f"A {resource_type.lower()} with this identifier already exists: '{identifier}'. Please use a different value."

    @staticmethod
    def resource_conflict(resource_type: str, reason: str) -> str:
        """Resource conflict message."""
        return f"Cannot modify {resource_type.lower()}: {reason}"

    # -------------------------------------------------------------------------
    # Authentication Errors
    # -------------------------------------------------------------------------

    @staticmethod
    def invalid_credentials() -> str:
        """Invalid login credentials."""
        return "Invalid email or password. Please check your credentials and try again."

    @staticmethod
    def token_expired() -> str:
        """Token has expired."""
        return "Your session has expired. Please log in again to continue."

    @staticmethod
    def token_invalid() -> str:
        """Token is invalid."""
        return "Your authentication token is invalid. Please log in again."

    @staticmethod
    def authentication_required() -> str:
        """Authentication is required."""
        return "Please log in to access this resource."

    # -------------------------------------------------------------------------
    # Authorization Errors
    # -------------------------------------------------------------------------

    @staticmethod
    def permission_denied(action: str, resource_type: str | None = None) -> str:
        """Permission denied message."""
        if resource_type:
            return f"You don't have permission to {action} this {resource_type.lower()}. Contact your workspace admin for access."
        return f"You don't have permission to {action}. Contact your workspace admin for access."

    @staticmethod
    def forbidden_action(action: str) -> str:
        """Forbidden action message."""
        return f"This action is not allowed: {action}"

    # -------------------------------------------------------------------------
    # Validation Errors
    # -------------------------------------------------------------------------

    @staticmethod
    def invalid_field(field: str, reason: str) -> str:
        """Invalid field value."""
        return f"Invalid value for '{field}': {reason}"

    @staticmethod
    def required_field(field: str) -> str:
        """Required field missing."""
        return f"The field '{field}' is required."

    @staticmethod
    def invalid_uuid(field: str) -> str:
        """Invalid UUID format."""
        return f"Invalid ID format for '{field}'. Expected a valid UUID."

    @staticmethod
    def invalid_file_type(filename: str, expected_types: list[str]) -> str:
        """Invalid file type."""
        types_str = ", ".join(expected_types)
        return f"Invalid file type for '{filename}'. Supported formats: {types_str}"

    @staticmethod
    def file_too_large(filename: str, max_size_mb: float) -> str:
        """File too large."""
        return f"File '{filename}' exceeds the maximum size of {max_size_mb}MB."

    # -------------------------------------------------------------------------
    # Processing Errors
    # -------------------------------------------------------------------------

    @staticmethod
    def processing_failed(operation: str, hint: str | None = None) -> str:
        """Processing operation failed."""
        msg = f"Failed to {operation}."
        if hint:
            msg += f" {hint}"
        return msg

    @staticmethod
    def processing_timeout(operation: str, timeout_seconds: int) -> str:
        """Processing timed out."""
        return f"The {operation} operation timed out after {timeout_seconds} seconds. Try with a smaller dataset or simpler parameters."

    @staticmethod
    def insufficient_data(operation: str, requirement: str) -> str:
        """Insufficient data for operation."""
        return f"Not enough data to perform {operation}. {requirement}"

    # -------------------------------------------------------------------------
    # Rate Limiting
    # -------------------------------------------------------------------------

    @staticmethod
    def rate_limit_exceeded(retry_after: int) -> str:
        """Rate limit exceeded."""
        return f"Too many requests. Please wait {retry_after} seconds before trying again."

    # -------------------------------------------------------------------------
    # Service Errors
    # -------------------------------------------------------------------------

    @staticmethod
    def service_unavailable(service: str, retry_after: int | None = None) -> str:
        """Service temporarily unavailable."""
        msg = f"The {service} service is temporarily unavailable."
        if retry_after:
            msg += f" Please try again in {retry_after} seconds."
        else:
            msg += " Please try again later."
        return msg

    @staticmethod
    def internal_error() -> str:
        """Internal server error."""
        return "An unexpected error occurred. Our team has been notified. Please try again later."

    # -------------------------------------------------------------------------
    # Dataset-Specific Messages
    # -------------------------------------------------------------------------

    @staticmethod
    def dataset_not_ready(status: str) -> str:
        """Dataset is not ready for processing."""
        return f"This dataset is not ready for analysis (status: {status}). Please wait for processing to complete."

    @staticmethod
    def invalid_column_mapping(column: str, expected: str) -> str:
        """Invalid column mapping."""
        return f"Column '{column}' could not be mapped. {expected}"

    @staticmethod
    def missing_required_columns(columns: list[str]) -> str:
        """Missing required columns."""
        cols_str = ", ".join(columns)
        return f"The uploaded file is missing required columns: {cols_str}"


# =============================================================================
# Helper Functions
# =============================================================================


def format_error_details(
    message: str,
    *,
    field: str | None = None,
    code: str | None = None,
    hint: str | None = None,
) -> dict[str, Any]:
    """Format error details for API response.

    Returns a dictionary suitable for HTTPException detail parameter.
    """
    result: dict[str, Any] = {"message": message}
    if field:
        result["field"] = field
    if code:
        result["code"] = code
    if hint:
        result["hint"] = hint
    return result


# Convenience alias
messages = ErrorMessages()
