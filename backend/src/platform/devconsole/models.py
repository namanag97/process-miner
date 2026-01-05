"""DevConsole data models for real-time observability."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """Log levels for DevConsole categorization."""

    INFO = "info"
    API_REQ = "api-req"
    API_RES = "api-res"
    ERROR = "error"


class DevLogEntry(BaseModel):
    """Enhanced log entry with rich metadata."""

    id: str
    timestamp: str
    level: str
    source: str
    message: str
    data: dict | None = None
    duration: int | None = None  # ms
    status: int | None = None
    request_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    timing: dict[str, float] | None = None
    importance: int = 3  # 1-5: 1=noise, 2=low, 3=medium, 4=high, 5=critical


class SystemMetrics(BaseModel):
    """Real-time system metrics snapshot."""

    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    active_requests: int
    requests_per_second: float
    avg_response_time_ms: float
    error_rate_percent: float


class HeartbeatMessage(BaseModel):
    """Periodic heartbeat with system state."""

    type: str = "heartbeat"
    timestamp: str
    metrics: SystemMetrics
    recent_errors: int
    slow_requests: int


# Log ID counter
_log_id_counter = 0


def get_next_log_id() -> int:
    """Get next log ID (thread-safe for async context)."""
    global _log_id_counter
    _log_id_counter += 1
    return _log_id_counter


def create_log_entry(
    level: LogLevel,
    source: str,
    message: str,
    data: dict | None = None,
    duration: int | None = None,
    status: int | None = None,
    request_id: str | None = None,
    tags: list[str] | None = None,
    timing: dict[str, float] | None = None,
    importance: int = 3,
) -> DevLogEntry:
    """Create a log entry for DevConsole.

    Args:
        level: Log level
        source: Source identifier (e.g., "BE GET /api/...")
        message: Log message
        data: Optional structured data
        duration: Optional duration in milliseconds
        status: Optional HTTP status code
        request_id: Optional request ID for correlation
        tags: Optional list of tags for filtering
        timing: Optional timing breakdown dict
        importance: Importance level 1-5

    Returns:
        The created DevLogEntry
    """
    log_id = get_next_log_id()

    return DevLogEntry(
        id=f"be-{log_id}",
        timestamp=datetime.utcnow().isoformat() + "Z",
        level=level.value,
        source=source,
        message=message,
        data=data,
        duration=duration,
        status=status,
        request_id=request_id,
        tags=tags or [],
        timing=timing,
        importance=importance,
    )
