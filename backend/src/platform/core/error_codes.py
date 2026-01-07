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
    - DIS: Discovery-specific errors
    """

    # ==========================================================================
    # Validation Errors (1xx)
    # ==========================================================================
    BAD_REQUEST = "ERR_099"  # General bad request (400)
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

    # ==========================================================================
    # Security Errors (6xx)
    # ==========================================================================
    AUTHENTICATION_FAILED = "ERR_600"
    AUTHORIZATION_FAILED = "ERR_601"
    TOKEN_EXPIRED = "ERR_602"
    TOKEN_INVALID = "ERR_603"


class DiscoveryErrorCode(str, Enum):
    """Discovery-specific error codes.

    Used for pre-flight validation and mining operation failures.
    Format: ERR_DIS_{NUMBER}
    """

    # Pre-flight validation errors (blocking)
    EMPTY_EVENT_LOG = "ERR_DIS_001"
    MISSING_CASE_ID = "ERR_DIS_002"
    MISSING_ACTIVITY = "ERR_DIS_003"
    TOO_MANY_ACTIVITIES = "ERR_DIS_004"  # >500 unique activities (warning)
    MISSING_TIMESTAMPS = "ERR_DIS_005"
    INVALID_TIMESTAMPS = "ERR_DIS_006"

    # Mining operation errors
    EXCESSIVE_LOOPS = "ERR_DIS_007"  # >10 self-loops detected
    DISCONNECTED_GRAPH = "ERR_DIS_008"  # Graph has isolated components
    MEMORY_EXCEEDED = "ERR_DIS_009"  # Estimated memory >4GB
    TIMEOUT_EXCEEDED = "ERR_DIS_010"  # Operation took >300s
    ALGORITHM_FAILURE = "ERR_DIS_011"  # PM4Py internal error


# Error code metadata for documentation and client handling
ERROR_METADATA: dict[ErrorCode, dict] = {
    # Validation Errors (1xx)
    ErrorCode.VALIDATION_FAILED: {
        "title": "Validation Failed",
        "description": "The request failed validation checks",
        "http_status": 422,
        "retryable": False,
        "user_message": "Please check your input and try again.",
    },
    ErrorCode.INVALID_INPUT: {
        "title": "Invalid Input",
        "description": "One or more input values are invalid",
        "http_status": 422,
        "retryable": False,
        "user_message": "The provided value is invalid. Please check the field requirements.",
    },
    ErrorCode.MISSING_REQUIRED_FIELD: {
        "title": "Missing Required Field",
        "description": "A required field was not provided",
        "http_status": 422,
        "retryable": False,
        "user_message": "Please provide all required fields.",
    },
    ErrorCode.INVALID_FILE_TYPE: {
        "title": "Invalid File Type",
        "description": "The uploaded file type is not supported",
        "http_status": 422,
        "retryable": False,
        "user_message": "Please upload a file in a supported format (CSV, XES, or OCEL).",
    },
    ErrorCode.FILE_TOO_LARGE: {
        "title": "File Too Large",
        "description": "The uploaded file exceeds the maximum allowed size",
        "http_status": 422,
        "retryable": False,
        "user_message": "Please upload a smaller file or contact support for larger datasets.",
    },
    ErrorCode.INVALID_COLUMN_MAPPING: {
        "title": "Invalid Column Mapping",
        "description": "The column mapping configuration is invalid",
        "http_status": 422,
        "retryable": False,
        "user_message": "Please verify your column mapping includes case_id, activity, and timestamp.",
    },
    # Resource Errors (2xx)
    ErrorCode.RESOURCE_NOT_FOUND: {
        "title": "Resource Not Found",
        "description": "The requested resource does not exist",
        "http_status": 404,
        "retryable": False,
        "user_message": "The requested item could not be found.",
    },
    ErrorCode.PROJECT_NOT_FOUND: {
        "title": "Project Not Found",
        "description": "The specified project does not exist",
        "http_status": 404,
        "retryable": False,
        "user_message": "The project could not be found. It may have been deleted.",
    },
    ErrorCode.PROCESS_NOT_FOUND: {
        "title": "Dataset Not Found",
        "description": "The specified dataset/event log does not exist",
        "http_status": 404,
        "retryable": False,
        "user_message": "The dataset could not be found. It may have been deleted.",
    },
    ErrorCode.RESOURCE_ALREADY_EXISTS: {
        "title": "Resource Already Exists",
        "description": "A resource with this identifier already exists",
        "http_status": 409,
        "retryable": False,
        "user_message": "An item with this identifier already exists. Please use a different value.",
    },
    ErrorCode.RESOURCE_CONFLICT: {
        "title": "Resource Conflict",
        "description": "The operation conflicts with the current state",
        "http_status": 409,
        "retryable": False,
        "user_message": "This operation cannot be performed due to a conflict.",
    },
    ErrorCode.CONCURRENCY_CONFLICT: {
        "title": "Concurrency Conflict",
        "description": "The resource was modified by another request",
        "http_status": 409,
        "retryable": True,
        "user_message": "The item was updated by someone else. Please refresh and try again.",
    },
    # Processing Errors (3xx)
    ErrorCode.PROCESSING_FAILED: {
        "title": "Processing Failed",
        "description": "The operation could not be completed",
        "http_status": 500,
        "retryable": True,
        "user_message": "An error occurred while processing. Please try again.",
    },
    ErrorCode.DISCOVERY_FAILED: {
        "title": "Process Discovery Failed",
        "description": "Failed to discover process model from event log",
        "http_status": 500,
        "retryable": True,
        "user_message": "Could not discover process model. Try with different mining parameters.",
    },
    ErrorCode.CONFORMANCE_CHECK_FAILED: {
        "title": "Conformance Check Failed",
        "description": "Failed to perform conformance checking",
        "http_status": 500,
        "retryable": True,
        "user_message": "Conformance checking failed. Ensure the model and log are compatible.",
    },
    ErrorCode.INGESTION_FAILED: {
        "title": "Data Ingestion Failed",
        "description": "Failed to ingest the uploaded data",
        "http_status": 500,
        "retryable": True,
        "user_message": "Could not process the uploaded file. Please verify the file format.",
    },
    ErrorCode.PROCESSING_TIMEOUT: {
        "title": "Processing Timeout",
        "description": "The operation took too long to complete",
        "http_status": 504,
        "retryable": True,
        "user_message": "The operation timed out. Try with a smaller dataset or simpler parameters.",
    },
    ErrorCode.INSUFFICIENT_DATA: {
        "title": "Insufficient Data",
        "description": "Not enough data to perform the requested operation",
        "http_status": 422,
        "retryable": False,
        "user_message": "Not enough data for this analysis. Please ensure your dataset meets minimum requirements.",
    },
    # External Service Errors (4xx)
    ErrorCode.EXTERNAL_SERVICE_ERROR: {
        "title": "External Service Error",
        "description": "An external service encountered an error",
        "http_status": 502,
        "retryable": True,
        "user_message": "A service dependency is unavailable. Please try again later.",
    },
    ErrorCode.PM4PY_ERROR: {
        "title": "Process Mining Error",
        "description": "An error occurred in the process mining engine",
        "http_status": 500,
        "retryable": True,
        "user_message": "The process mining engine encountered an error. Please try again.",
    },
    ErrorCode.DATABASE_ERROR: {
        "title": "Database Error",
        "description": "A database operation failed",
        "http_status": 500,
        "retryable": True,
        "user_message": "A database error occurred. Please try again.",
    },
    ErrorCode.SERVICE_UNAVAILABLE: {
        "title": "Service Unavailable",
        "description": "A required service is temporarily unavailable",
        "http_status": 503,
        "retryable": True,
        "user_message": "The service is temporarily unavailable. Please try again in a few minutes.",
    },
    # System Errors (5xx)
    ErrorCode.INTERNAL_ERROR: {
        "title": "Internal Server Error",
        "description": "An unexpected error occurred",
        "http_status": 500,
        "retryable": False,
        "user_message": "An unexpected error occurred. Our team has been notified.",
    },
    ErrorCode.RATE_LIMIT_EXCEEDED: {
        "title": "Rate Limit Exceeded",
        "description": "Too many requests, please slow down",
        "http_status": 429,
        "retryable": True,
        "user_message": "You've made too many requests. Please wait before trying again.",
    },
    # Security Errors (6xx)
    ErrorCode.AUTHENTICATION_FAILED: {
        "title": "Authentication Failed",
        "description": "Invalid or missing authentication credentials",
        "http_status": 401,
        "retryable": False,
        "user_message": "Please log in to access this resource.",
    },
    ErrorCode.AUTHORIZATION_FAILED: {
        "title": "Authorization Failed",
        "description": "Insufficient permissions for this operation",
        "http_status": 403,
        "retryable": False,
        "user_message": "You don't have permission to perform this action.",
    },
    ErrorCode.TOKEN_EXPIRED: {
        "title": "Token Expired",
        "description": "The authentication token has expired",
        "http_status": 401,
        "retryable": False,
        "user_message": "Your session has expired. Please log in again.",
    },
    ErrorCode.TOKEN_INVALID: {
        "title": "Token Invalid",
        "description": "The authentication token is invalid",
        "http_status": 401,
        "retryable": False,
        "user_message": "Your session is invalid. Please log in again.",
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
