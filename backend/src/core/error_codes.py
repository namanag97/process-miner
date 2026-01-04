"""Enterprise error code catalog.

Provides typed error codes for API responses following best practices for
error identification, debugging, and client error handling.
"""

from enum import Enum


class ErrorCode(str, Enum):
    """Typed error codes for API responses.

    Format: ERR_{CATEGORY}_{NUMBER}
    Categories:
    - 1xx: Validation errors
    - 2xx: Resource errors
    - 3xx: Processing errors
    - 4xx: External service errors
    - 5xx: System errors
    """

    # ==========================================================================
    # Validation Errors (1xx)
    # ==========================================================================
    VALIDATION_FAILED = "ERR_100"
    INVALID_INPUT = "ERR_101"
    MISSING_REQUIRED_FIELD = "ERR_102"
    INVALID_FORMAT = "ERR_103"
    VALUE_OUT_OF_RANGE = "ERR_104"
    INVALID_FILE_TYPE = "ERR_105"
    FILE_TOO_LARGE = "ERR_106"
    INVALID_COLUMN_MAPPING = "ERR_107"
    MALFORMED_CSV = "ERR_108"
    MALFORMED_XES = "ERR_109"
    MALFORMED_OCEL = "ERR_110"

    # ==========================================================================
    # Resource Errors (2xx)
    # ==========================================================================
    RESOURCE_NOT_FOUND = "ERR_200"
    PROJECT_NOT_FOUND = "ERR_201"
    PROCESS_NOT_FOUND = "ERR_202"
    MODEL_NOT_FOUND = "ERR_203"
    ANALYSIS_NOT_FOUND = "ERR_204"
    CASE_NOT_FOUND = "ERR_205"
    RESOURCE_ALREADY_EXISTS = "ERR_210"
    RESOURCE_CONFLICT = "ERR_211"
    CONCURRENCY_CONFLICT = "ERR_212"
    STALE_RESOURCE = "ERR_213"

    # ==========================================================================
    # Processing Errors (3xx)
    # ==========================================================================
    PROCESSING_FAILED = "ERR_300"
    DISCOVERY_FAILED = "ERR_301"
    CONFORMANCE_CHECK_FAILED = "ERR_302"
    ANALYSIS_FAILED = "ERR_303"
    INGESTION_FAILED = "ERR_304"
    FILTERING_FAILED = "ERR_305"
    VISUALIZATION_FAILED = "ERR_306"
    PREDICTION_FAILED = "ERR_307"
    SIMULATION_FAILED = "ERR_308"
    PROCESSING_TIMEOUT = "ERR_310"
    OPERATION_CANCELLED = "ERR_311"
    INSUFFICIENT_DATA = "ERR_312"

    # ==========================================================================
    # External Service Errors (4xx)
    # ==========================================================================
    EXTERNAL_SERVICE_ERROR = "ERR_400"
    PM4PY_ERROR = "ERR_401"
    DATABASE_ERROR = "ERR_402"
    CACHE_ERROR = "ERR_403"
    FILE_STORAGE_ERROR = "ERR_404"
    CELERY_ERROR = "ERR_405"
    REDIS_UNAVAILABLE = "ERR_406"
    SERVICE_UNAVAILABLE = "ERR_410"
    CONNECTION_TIMEOUT = "ERR_411"

    # ==========================================================================
    # System Errors (5xx)
    # ==========================================================================
    INTERNAL_ERROR = "ERR_500"
    CONFIGURATION_ERROR = "ERR_501"
    SERIALIZATION_ERROR = "ERR_502"
    DESERIALIZATION_ERROR = "ERR_503"
    MEMORY_ERROR = "ERR_504"
    RATE_LIMIT_EXCEEDED = "ERR_510"
    QUOTA_EXCEEDED = "ERR_511"


# Error code metadata for documentation and client handling
ERROR_METADATA: dict[ErrorCode, dict] = {
    ErrorCode.VALIDATION_FAILED: {
        "title": "Validation Failed",
        "description": "The request failed validation checks",
        "http_status": 422,
        "retryable": False,
    },
    ErrorCode.RESOURCE_NOT_FOUND: {
        "title": "Resource Not Found",
        "description": "The requested resource does not exist",
        "http_status": 404,
        "retryable": False,
    },
    ErrorCode.PROCESSING_TIMEOUT: {
        "title": "Processing Timeout",
        "description": "The operation took too long to complete",
        "http_status": 504,
        "retryable": True,
    },
    ErrorCode.RATE_LIMIT_EXCEEDED: {
        "title": "Rate Limit Exceeded",
        "description": "Too many requests, please slow down",
        "http_status": 429,
        "retryable": True,
    },
    ErrorCode.CONCURRENCY_CONFLICT: {
        "title": "Concurrency Conflict",
        "description": "The resource was modified by another request",
        "http_status": 409,
        "retryable": True,
    },
    ErrorCode.PM4PY_ERROR: {
        "title": "Process Mining Error",
        "description": "An error occurred in the process mining engine",
        "http_status": 500,
        "retryable": True,
    },
    ErrorCode.SERVICE_UNAVAILABLE: {
        "title": "Service Unavailable",
        "description": "A required service is temporarily unavailable",
        "http_status": 503,
        "retryable": True,
    },
    ErrorCode.INTERNAL_ERROR: {
        "title": "Internal Server Error",
        "description": "An unexpected error occurred",
        "http_status": 500,
        "retryable": False,
    },
}


def get_error_metadata(code: ErrorCode) -> dict:
    """Get metadata for an error code, with sensible defaults."""
    return ERROR_METADATA.get(
        code,
        {
            "title": code.name.replace("_", " ").title(),
            "description": f"Error code: {code.value}",
            "http_status": 500,
            "retryable": False,
        },
    )
