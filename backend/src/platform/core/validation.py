"""Validation utilities for platform layer.

Provides reusable validation functions for API endpoints:
- UUID validation for path/query parameters
- String sanitization for search queries
- Common field validators
"""

import re
from typing import Any

from fastapi import HTTPException

# UUID v4 pattern (case-insensitive)
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)

# Password requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


def validate_uuid(value: str, field_name: str = "id") -> str:
    """Validate and return a UUID string.

    Args:
        value: The string to validate
        field_name: Name of the field for error messages

    Returns:
        The validated UUID string (lowercase) or MVP ID

    Raises:
        HTTPException: 400 if invalid UUID format
    """
    # Allow MVP IDs in development (mvp-org-001, mvp-ws-001, mvp-user-001)
    if value and value.startswith("mvp-"):
        return value

    if not value or not UUID_PATTERN.match(value):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_UUID",
                "message": f"Invalid {field_name} format. Expected UUID (e.g., '550e8400-e29b-41d4-a716-446655440000').",
                "field": field_name,
            },
        )
    return value.lower()


def is_valid_uuid(value: str | None) -> bool:
    """Check if string is valid UUID format.

    Args:
        value: The string to check

    Returns:
        True if valid UUID format, False otherwise
    """
    return bool(value and UUID_PATTERN.match(value))


def sanitize_search_query(query: str | None) -> str | None:
    """Sanitize a search query for safe use in SQL LIKE clauses.

    Escapes SQL wildcards to prevent injection.

    Args:
        query: The search query to sanitize

    Returns:
        Sanitized query string or None
    """
    if not query:
        return None

    # Escape SQL LIKE wildcards
    sanitized = query.replace("\\", "\\\\")  # Escape backslashes first
    sanitized = sanitized.replace("%", "\\%")
    sanitized = sanitized.replace("_", "\\_")

    # Strip leading/trailing whitespace
    return sanitized.strip() or None


def validate_password_strength(password: str) -> list[str]:
    """Validate password meets strength requirements.

    Args:
        password: The password to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")

    if len(password) > PASSWORD_MAX_LENGTH:
        errors.append(f"Password must be at most {PASSWORD_MAX_LENGTH} characters")

    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")

    return errors


def validate_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Validate and normalize pagination parameters.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (page, page_size) with valid values

    Raises:
        HTTPException: 400 if invalid parameters
    """
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PAGINATION",
                "message": "Page number must be at least 1",
                "field": "page",
            },
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PAGINATION",
                "message": "Page size must be between 1 and 100",
                "field": "page_size",
            },
        )

    return page, page_size


def normalize_email(email: str) -> str:
    """Normalize email address to lowercase.

    Args:
        email: The email to normalize

    Returns:
        Lowercase email string
    """
    return email.lower().strip()


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calculate total number of pages for pagination.

    Args:
        total: Total number of items
        page_size: Items per page

    Returns:
        Total number of pages (minimum 0)
    """
    if total <= 0 or page_size <= 0:
        return 0
    return (total + page_size - 1) // page_size
