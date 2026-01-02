# Logging

> **Framework:** Structlog (structured logging)
> **Location:** `src/core/logging_config.py`, `src/core/middleware.py`
> **Status:** ✅ Fully Implemented

---

## Quick Reference Card

### What It Does
Provides **structured, contextual logging** with automatic request correlation, performance tracking, and dual output modes (JSON for production, colored console for development).

### Key Features
- **Structured Logs:** Key-value pairs instead of string concatenation
- **Context Binding:** Automatic `request_id`, `user_id`, `org_id` propagation
- **Dual Output:** JSON (production) / Colored console (development)
- **Performance Tracking:** Automatic request duration logging
- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

### Development vs Production

**Development (colored console):**
```
2026-01-02 10:30:15 [info     ] dataset_uploaded dataset_id=xyz789 filename=events.csv total_cases=100 [src.api.routers.datasets:45]
```

**Production (JSON):**
```json
{"event": "dataset_uploaded", "dataset_id": "xyz789", "filename": "events.csv", "total_cases": 100, "level": "info", "timestamp": "2026-01-02T10:30:15.123Z", "logger": "src.api.routers.datasets", "request_id": "req_abc123"}
```

### Common Gotchas

> [!TIP]
> **Use structured logging, not string formatting**
> ```python
> # GOOD
> logger.info("dataset_uploaded", dataset_id=dataset_id, total_cases=100)
>
> # BAD
> logger.info(f"Dataset {dataset_id} uploaded with {total_cases} cases")
> ```

> [!WARNING]
> **Avoid logging sensitive data**
> - Don't log passwords, tokens, API keys
> - Sanitize user input before logging
> - Use `privacy.anonymize()` for PII data

---

## Configuration

### Environment Variables

```env
# Log Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log Format (true = JSON, false = colored console)
LOG_JSON=false

# Debug Mode (enables verbose logging)
DEBUG=true
```

### Structlog Setup

**File:** `src/core/logging_config.py`

```python
import structlog
import logging
from typing import Any
from src.core.config import settings

def configure_logging():
    """Configure structlog with dual output modes"""

    # Determine processors based on environment
    processors = [
        structlog.stdlib.filter_by_level,          # Filter by log level
        structlog.stdlib.add_log_level,            # Add "level" field
        structlog.stdlib.add_logger_name,          # Add "logger" field
        structlog.processors.TimeStamper(fmt="iso"),  # ISO 8601 timestamp
        structlog.processors.StackInfoRenderer(),  # Stack traces
        structlog.processors.format_exc_info,      # Format exceptions
        structlog.processors.UnicodeDecoder(),     # Decode bytes to str
    ]

    # Add final renderer based on environment
    if settings.LOG_JSON:
        # Production: JSON output for log aggregation (ELK, CloudWatch, etc.)
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Colored console output for readability
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback
            )
        )

    structlog.configure(
        processors=processors,
        context_class=dict,                        # Use dict for context
        logger_factory=structlog.stdlib.LoggerFactory(),  # Use stdlib logging
        cache_logger_on_first_use=True,            # Performance optimization
    )

    # Configure stdlib logging level
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(message)s",  # Structlog handles formatting
    )
```

---

## Request Context Binding

### Middleware Implementation

**File:** `src/core/middleware.py`

```python
import structlog
import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = structlog.get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Generates/extracts request_id
    2. Binds request context to all logs within the request
    3. Logs request start, completion, and duration
    """

    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # Bind context to all logs in this request
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        )

        # Log request start
        logger.info(
            "request_started",
            user_agent=request.headers.get("user-agent")
        )

        # Track request duration
        start_time = time.time()

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Log request completion
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2)
            )

            # Add request_id to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000

            # Log request failure
            logger.error(
                "request_failed",
                error=str(exc),
                duration_ms=round(duration_ms, 2),
                exc_info=True
            )

            raise

        finally:
            # Clear context after request
            structlog.contextvars.clear_contextvars()
```

---

## Usage in Services

### Basic Logging

**File:** `src/services/ingestion.py`

```python
import structlog

logger = structlog.get_logger(__name__)

class IngestionService:
    async def ingest_csv(
        self,
        db: AsyncSession,
        file_path: str,
        column_mapping: dict,
        name: str
    ) -> Dataset:
        """Ingest CSV with structured logging"""

        logger.info(
            "csv_ingestion_started",
            filename=Path(file_path).name,
            column_mapping=column_mapping
        )

        start_time = time.time()

        try:
            # Parse CSV with DuckDB
            arrow_table = duckdb.execute(
                f"SELECT * FROM read_csv_auto('{file_path}')"
            ).arrow()

            row_count = len(arrow_table)

            logger.debug(
                "csv_parsed",
                rows=row_count,
                duration_ms=(time.time() - start_time) * 1000
            )

            # Bulk insert into database
            dataset = await self._bulk_insert(db, arrow_table, name)

            logger.info(
                "csv_ingestion_completed",
                dataset_id=dataset.id,
                total_cases=dataset.total_cases,
                total_events=dataset.total_events,
                duration_ms=(time.time() - start_time) * 1000
            )

            return dataset

        except Exception as e:
            logger.error(
                "csv_ingestion_failed",
                filename=Path(file_path).name,
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
                exc_info=True  # Include stack trace
            )
            raise
```

### Log Output Examples

**Development Console:**
```
2026-01-02 10:30:00 [info     ] csv_ingestion_started filename=events.csv column_mapping={'case_id': 'case_id', 'activity': 'activity'} [src.services.ingestion:25]
2026-01-02 10:30:01 [debug    ] csv_parsed rows=10523 duration_ms=245.3 [src.services.ingestion:35]
2026-01-02 10:30:02 [info     ] csv_ingestion_completed dataset_id=xyz789 total_cases=100 total_events=523 duration_ms=1234.5 [src.services.ingestion:45]
```

**Production JSON:**
```json
{"event": "csv_ingestion_started", "filename": "events.csv", "column_mapping": {"case_id": "case_id", "activity": "activity"}, "level": "info", "timestamp": "2026-01-02T10:30:00.123Z", "logger": "src.services.ingestion", "request_id": "req_abc123"}
{"event": "csv_parsed", "rows": 10523, "duration_ms": 245.3, "level": "debug", "timestamp": "2026-01-02T10:30:01.368Z", "logger": "src.services.ingestion", "request_id": "req_abc123"}
{"event": "csv_ingestion_completed", "dataset_id": "xyz789", "total_cases": 100, "total_events": 523, "duration_ms": 1234.5, "level": "info", "timestamp": "2026-01-02T10:30:02.357Z", "logger": "src.services.ingestion", "request_id": "req_abc123"}
```

---

## Log Levels

### When to Use Each Level

| Level | Purpose | Examples | Production Volume |
|-------|---------|----------|-------------------|
| **DEBUG** | Internal state, detailed traces | Variable values, SQL queries, step-by-step flow | ❌ Disabled (too verbose) |
| **INFO** | Business events, normal operations | User login, dataset upload, model discovery | ✅ Enabled (moderate) |
| **WARNING** | Degraded performance, deprecations | Slow queries, circuit breaker triggered, cache miss | ✅ Enabled |
| **ERROR** | Operation failures, exceptions | Failed uploads, PM4Py errors, DB connection loss | ✅ Enabled (always) |
| **CRITICAL** | System failures, data corruption | Database unavailable, OOM errors | ✅ Enabled (always) |

### Usage Examples

```python
import structlog

logger = structlog.get_logger(__name__)

# DEBUG - Internal state (development only)
logger.debug(
    "database_query_executed",
    query="SELECT * FROM datasets WHERE id = ?",
    params=["xyz789"],
    duration_ms=12.3
)

# INFO - Business events (production)
logger.info(
    "user_logged_in",
    user_id="user_123",
    email="user@example.com",
    organization_id="org_456"
)

# WARNING - Degraded performance
logger.warning(
    "slow_query_detected",
    query="SELECT * FROM process_events WHERE dataset_id = ?",
    duration_ms=5234.1,
    threshold_ms=1000
)

# ERROR - Operation failure
logger.error(
    "pm4py_discovery_failed",
    dataset_id="xyz789",
    miner_type="inductive",
    error="TimeoutError: Discovery exceeded 60 seconds",
    exc_info=True  # Include stack trace
)

# CRITICAL - System failure
logger.critical(
    "database_connection_lost",
    error="SQLAlchemy connection pool exhausted",
    active_connections=20,
    max_connections=20
)
```

---

## Performance Logging

### Automatic Request Duration

All requests automatically log duration via `RequestLoggingMiddleware`:

```json
{
  "event": "request_completed",
  "request_id": "req_abc123",
  "method": "POST",
  "path": "/api/v1/datasets/upload",
  "status_code": 201,
  "duration_ms": 1234.5,
  "timestamp": "2026-01-02T10:30:02.357Z"
}
```

### Manual Performance Tracking

**Pattern 1: Decorator**

```python
import functools
import time
import structlog

logger = structlog.get_logger(__name__)

def log_performance(operation_name: str):
    """Decorator for logging operation duration"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                logger.info(
                    f"{operation_name}_completed",
                    duration_ms=round(duration_ms, 2),
                    **kwargs  # Log function arguments
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                logger.error(
                    f"{operation_name}_failed",
                    error=str(e),
                    duration_ms=round(duration_ms, 2),
                    exc_info=True
                )

                raise

        return wrapper
    return decorator

# Usage
@log_performance("pm4py_discovery")
async def discover_model(dataset_id: str, miner_type: str):
    # ... discovery logic
    pass
```

**Pattern 2: Context Manager**

```python
from contextlib import contextmanager

@contextmanager
def log_duration(operation: str, **context):
    """Context manager for logging duration"""

    start_time = time.time()
    logger.info(f"{operation}_started", **context)

    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"{operation}_completed",
            duration_ms=round(duration_ms, 2),
            **context
        )

# Usage
with log_duration("bulk_insert", dataset_id="xyz789", row_count=10000):
    await db.execute(insert(ProcessEvent).values(rows))
```

---

## Slow Query Detection

**File:** `src/core/middleware.py:PerformanceLoggingMiddleware`

```python
class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """Log slow requests"""

    SLOW_REQUEST_THRESHOLD_MS = 1000  # 1 second

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        if duration_ms > self.SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(
                "slow_request_detected",
                path=request.url.path,
                method=request.method,
                duration_ms=round(duration_ms, 2),
                threshold_ms=self.SLOW_REQUEST_THRESHOLD_MS
            )

        return response
```

---

## Frontend DevConsole Integration

### Backend Log Endpoint

**File:** `src/api/routers/dev_logs_stream.py`

```python
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

router = APIRouter(prefix="/api/v1/dev/logs", tags=["development"])

# In-memory log buffer (last 100 logs)
LOG_BUFFER = []
MAX_BUFFER_SIZE = 100

def add_log_to_buffer(log_record: dict):
    """Add log to buffer (called by structlog processor)"""
    LOG_BUFFER.append(log_record)
    if len(LOG_BUFFER) > MAX_BUFFER_SIZE:
        LOG_BUFFER.pop(0)

@router.get("/stream")
async def stream_logs():
    """Server-Sent Events endpoint for real-time log streaming"""

    async def event_generator():
        last_index = 0

        while True:
            # Send new logs since last_index
            if last_index < len(LOG_BUFFER):
                for log in LOG_BUFFER[last_index:]:
                    yield {
                        "data": json.dumps(log),
                        "event": "log"
                    }
                last_index = len(LOG_BUFFER)

            await asyncio.sleep(0.5)  # Poll every 500ms

    return EventSourceResponse(event_generator())

@router.get("")
async def get_recent_logs(limit: int = 50):
    """Get recent logs (HTTP polling alternative)"""
    return LOG_BUFFER[-limit:]
```

### Frontend DevConsole Usage

```typescript
// React component for live log streaming
import { useEffect, useState } from 'react';

export function DevConsole() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const eventSource = new EventSource('http://localhost:8001/api/v1/dev/logs/stream');

    eventSource.addEventListener('log', (event) => {
      const log = JSON.parse(event.data);
      setLogs((prev) => [...prev, log].slice(-100));  // Keep last 100
    });

    return () => eventSource.close();
  }, []);

  return (
    <div className="dev-console">
      {logs.map((log, i) => (
        <div key={i} className={`log log-${log.level}`}>
          <span className="timestamp">{log.timestamp}</span>
          <span className="level">{log.level}</span>
          <span className="event">{log.event}</span>
          <span className="details">{JSON.stringify(log)}</span>
        </div>
      ))}
    </div>
  );
}
```

---

## Log Aggregation (Production)

### JSON Logs → ELK Stack

**1. Configure JSON output:**
```env
LOG_JSON=true
```

**2. Ship logs to Logstash:**
```bash
# Docker logging driver
docker run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  your-app:latest
```

**3. Logstash configuration:**
```ruby
input {
  file {
    path => "/var/log/app/*.json"
    codec => "json"
  }
}

filter {
  # Logs are already structured, no parsing needed
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

**4. Kibana query examples:**
```
# Find all errors for a specific request
request_id:"req_abc123" AND level:"error"

# Slow requests (>1s)
duration_ms:>1000

# PM4Py failures
event:"pm4py_*_failed"

# Specific user actions
user_id:"user_123" AND event:"dataset_uploaded"
```

---

## Testing Logging

### Capture Logs in Tests

**File:** `tests/test_logging.py`

```python
import pytest
import structlog
from structlog.testing import LogCapture

@pytest.fixture
def log_capture():
    """Capture structlog logs in tests"""
    capture = LogCapture()
    structlog.configure(processors=[capture])
    yield capture
    structlog.reset_defaults()

def test_dataset_upload_logging(log_capture, client: TestClient):
    """Test dataset upload creates appropriate logs"""

    response = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("test.csv", b"case_id,activity,timestamp\n...")},
        data={
            "case_id_column": "case_id",
            "activity_column": "activity",
            "timestamp_column": "timestamp"
        }
    )

    assert response.status_code == 201

    # Verify logs
    logs = log_capture.entries

    # Check request started
    assert any(log["event"] == "request_started" for log in logs)

    # Check CSV ingestion
    assert any(log["event"] == "csv_ingestion_started" for log in logs)
    assert any(log["event"] == "csv_ingestion_completed" for log in logs)

    # Check request completed
    assert any(log["event"] == "request_completed" for log in logs)

    # Verify request_id propagation
    request_ids = [log.get("request_id") for log in logs if "request_id" in log]
    assert len(set(request_ids)) == 1  # All logs have same request_id
```

---

## Best Practices

### ✅ DO: Use Structured Logging

```python
# GOOD - Structured (machine-readable)
logger.info(
    "dataset_uploaded",
    dataset_id=dataset_id,
    filename=filename,
    total_cases=total_cases
)

# BAD - String formatting (hard to parse)
logger.info(f"Dataset {dataset_id} uploaded from {filename} with {total_cases} cases")
```

### ✅ DO: Log Business Events

```python
# User actions
logger.info("user_logged_in", user_id=user_id, email=email)
logger.info("dataset_uploaded", dataset_id=dataset_id)
logger.info("model_discovered", model_id=model_id, miner_type=miner_type)

# System events
logger.info("cache_hit", key=cache_key)
logger.info("circuit_breaker_opened", service="pm4py", failure_count=5)
```

### ✅ DO: Include Duration for Expensive Operations

```python
start_time = time.time()
result = await expensive_operation()
duration_ms = (time.time() - start_time) * 1000

logger.info(
    "expensive_operation_completed",
    operation="pm4py_discovery",
    duration_ms=round(duration_ms, 2)
)
```

### ❌ DON'T: Log Sensitive Data

```python
# BAD - Logs password
logger.info("user_login_attempt", email=email, password=password)  # ❌

# GOOD - Omits sensitive data
logger.info("user_login_attempt", email=email)  # ✅
```

### ❌ DON'T: Use String Concatenation

```python
# BAD
logger.info("User " + user_id + " uploaded dataset " + dataset_id)  # ❌

# GOOD
logger.info("dataset_uploaded", user_id=user_id, dataset_id=dataset_id)  # ✅
```

---

## Troubleshooting

### Logs Not Showing

**Issue:** No logs in console/file

**Solution:**
1. Check log level: `LOG_LEVEL=DEBUG` in `.env`
2. Ensure logging is configured: `configure_logging()` called in `main.py`
3. Verify logger import: `import structlog; logger = structlog.get_logger(__name__)`

### Request ID Missing

**Issue:** Logs don't have `request_id` field

**Solution:**
1. Ensure `RequestLoggingMiddleware` is registered:
   ```python
   app.add_middleware(RequestLoggingMiddleware)
   ```
2. Check middleware order (should be early in the stack)

### JSON Logs in Development

**Issue:** JSON logs in console (hard to read)

**Solution:**
```env
LOG_JSON=false  # Colored console output
```

---

## Related Documentation

- [Error Handling](./error-handling.md) - Exception logging
- [Observability](./observability.md) - Metrics and tracing
- [Middleware](../02-layers/api-layer.md#middleware) - Request logging middleware
- [DevConsole Integration](../01-features/observability/log-streaming.md) - Frontend log streaming

---

## References

- **Structlog Documentation:** https://www.structlog.org/
- **12-Factor App Logging:** https://12factor.net/logs
- **JSON Logging Best Practices:** https://www.datadoghq.com/blog/structured-logging-best-practices/
