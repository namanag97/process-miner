"""Shared API Response Schemas for Swagger Documentation.

Provides reusable response schemas with examples for consistent API documentation.
"""

from typing import Any

from pydantic import BaseModel, Field


# =============================================================================
# Standard Error Response Schema
# =============================================================================


class ErrorDetail(BaseModel):
    """Standard error response schema (RFC 7807 Problem Details)."""

    type: str = Field(
        ...,
        description="Error type URI",
        json_schema_extra={"example": "https://api.processmining.io/errors/RESOURCE_NOT_FOUND"},
    )
    title: str = Field(
        ...,
        description="Short error title",
        json_schema_extra={"example": "Resource Not Found"},
    )
    status: int = Field(
        ...,
        description="HTTP status code",
        json_schema_extra={"example": 404},
    )
    detail: str = Field(
        ...,
        description="Human-readable error message",
        json_schema_extra={"example": "The project you requested could not be found. Please verify the ID is correct."},
    )
    error_code: str = Field(
        ...,
        description="Machine-readable error code",
        json_schema_extra={"example": "PROJECT_NOT_FOUND"},
    )
    timestamp: str = Field(
        ...,
        description="When the error occurred (ISO 8601)",
        json_schema_extra={"example": "2024-01-15T10:30:00Z"},
    )
    correlation_id: str | None = Field(
        None,
        description="Request correlation ID for support",
    )


class ValidationErrorDetail(BaseModel):
    """Validation error response schema."""

    detail: list[dict[str, Any]] = Field(
        ...,
        description="List of validation errors",
        json_schema_extra={
            "example": [
                {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address",
                    "type": "value_error.email",
                }
            ]
        },
    )


# =============================================================================
# Common Response Examples for Swagger
# =============================================================================

COMMON_RESPONSES = {
    401: {
        "description": "**Authentication Required** - Missing or invalid JWT token",
        "content": {
            "application/json": {
                "example": {
                    "type": "https://api.processmining.io/errors/AUTHENTICATION_FAILED",
                    "title": "Authentication Failed",
                    "status": 401,
                    "detail": "Please log in to access this resource.",
                    "error_code": "AUTHENTICATION_FAILED",
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            }
        },
    },
    403: {
        "description": "**Forbidden** - Insufficient permissions for this action",
        "content": {
            "application/json": {
                "example": {
                    "type": "https://api.processmining.io/errors/AUTHORIZATION_FAILED",
                    "title": "Authorization Failed",
                    "status": 403,
                    "detail": "You don't have permission to perform this action. Contact your workspace admin.",
                    "error_code": "AUTHORIZATION_FAILED",
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            }
        },
    },
    404: {
        "description": "**Not Found** - The requested resource does not exist",
        "content": {
            "application/json": {
                "example": {
                    "type": "https://api.processmining.io/errors/RESOURCE_NOT_FOUND",
                    "title": "Resource Not Found",
                    "status": 404,
                    "detail": "The resource you requested could not be found. Please verify the ID is correct.",
                    "error_code": "RESOURCE_NOT_FOUND",
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            }
        },
    },
    422: {
        "description": "**Validation Error** - Invalid request data",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["body", "name"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        }
                    ]
                }
            }
        },
    },
    429: {
        "description": "**Rate Limited** - Too many requests, wait before retrying",
        "content": {
            "application/json": {
                "example": {
                    "type": "https://api.processmining.io/errors/RATE_LIMIT_EXCEEDED",
                    "title": "Rate Limit Exceeded",
                    "status": 429,
                    "detail": "Too many requests. Please wait 60 seconds before trying again.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": 60,
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            }
        },
    },
    500: {
        "description": "**Server Error** - An unexpected error occurred",
        "content": {
            "application/json": {
                "example": {
                    "type": "https://api.processmining.io/errors/INTERNAL_ERROR",
                    "title": "Internal Server Error",
                    "status": 500,
                    "detail": "An unexpected error occurred. Our team has been notified.",
                    "error_code": "INTERNAL_ERROR",
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            }
        },
    },
}


# =============================================================================
# Module-Specific Response Examples
# =============================================================================


AUTH_RESPONSES = {
    **COMMON_RESPONSES,
    200: {
        "description": "**Success** - Authentication successful",
    },
    201: {
        "description": "**Created** - User registered successfully",
    },
}


DATASET_RESPONSES = {
    **COMMON_RESPONSES,
    200: {
        "description": "**Success** - Operation completed",
    },
    202: {
        "description": "**Accepted** - Job queued for background processing. Poll `/jobs/{job_id}` for status.",
    },
    400: {
        "description": "**Bad Request** - Dataset not in correct state for this operation",
        "content": {
            "application/json": {
                "example": {
                    "type": "https://api.processmining.io/errors/INVALID_STATE",
                    "title": "Invalid State",
                    "status": 400,
                    "detail": "Dataset must be in MAPPED state to trigger ingestion. Current: PENDING",
                    "error_code": "INVALID_STATE",
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            }
        },
    },
    413: {
        "description": "**File Too Large** - Uploaded file exceeds maximum size limit",
        "content": {
            "application/json": {
                "example": {
                    "type": "https://api.processmining.io/errors/FILE_TOO_LARGE",
                    "title": "File Too Large",
                    "status": 413,
                    "detail": "File exceeds the maximum size of 100MB. Use presigned upload for larger files.",
                    "error_code": "FILE_TOO_LARGE",
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            }
        },
    },
}


PROJECT_RESPONSES = {
    **COMMON_RESPONSES,
    200: {
        "description": "**Success** - Project operation completed",
    },
    201: {
        "description": "**Created** - Project created successfully",
    },
    204: {
        "description": "**No Content** - Project deleted successfully",
    },
}


WORKSPACE_RESPONSES = {
    **COMMON_RESPONSES,
    200: {
        "description": "**Success** - Workspace operation completed",
    },
    201: {
        "description": "**Created** - Workspace created successfully",
    },
    204: {
        "description": "**No Content** - Workspace deleted successfully",
    },
}
