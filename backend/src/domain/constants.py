"""
Centralized constants to eliminate magic numbers across the codebase.

This module provides named constants for:
- HTTP status codes
- Display/pagination limits
- Default configurations
- Performance thresholds
"""

from enum import IntEnum


class HttpStatus(IntEnum):
    """Standard HTTP status codes used in API responses."""

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503


class DisplayLimits(IntEnum):
    """Limits for displaying data in API responses."""

    SMALL = 10
    DEFAULT = 20
    MEDIUM = 50
    LARGE = 100
    MAX_VARIANTS = 100
    MAX_ACTIVITIES = 50
    MAX_TRANSITIONS = 100
    MAX_PREVIEW_ROWS = 20


class PaginationDefaults(IntEnum):
    """Default pagination values."""

    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    FIRST_PAGE = 1


class PerformanceThresholds:
    """Thresholds for performance analysis."""

    BOTTLENECK_THRESHOLD = 0.8
    SLA_WARNING_THRESHOLD = 0.9
    FREQUENCY_HIGH = 0.7
    FREQUENCY_MEDIUM = 0.3
    DURATION_OUTLIER_STDDEV = 2.0


class AnalysisDefaults:
    """Default values for analysis operations."""

    TOP_N_VARIANTS = 10
    TOP_N_ACTIVITIES = 20
    CONFORMANCE_THRESHOLD = 0.8
    MIN_SUPPORT = 0.05
    MIN_CONFIDENCE = 0.8


class FileSettings:
    """File handling constants."""

    MAX_UPLOAD_SIZE_MB = 100
    CHUNK_SIZE_BYTES = 8192
    SUPPORTED_EXTENSIONS = {".csv", ".xes", ".json", ".xlsx"}


class CacheSettings:
    """Cache configuration constants."""

    DEFAULT_TTL_SECONDS = 300
    SHORT_TTL_SECONDS = 60
    LONG_TTL_SECONDS = 3600
