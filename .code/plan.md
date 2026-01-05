# Plan: Simplify Logging and Observability Setup

## Current State Analysis

The codebase has **excessive logging and observability complexity** with multiple overlapping systems:

### Current Systems:
1. **Structlog** (`logging_config.py`) - Core structured logging ✅ KEEP
2. **DevConsole Logs** (`dev_logs.py`, `devconsole_types.py`) - Frontend dev console ✅ KEEP (Simplify)
3. **OpenTelemetry Tracing** (`tracing.py`, `devconsole_exporter.py`) - Distributed tracing ❌ REMOVE
4. **Prometheus Metrics** (`metrics.py`) - Metrics collection ❌ REMOVE
5. **Telemetry Proxy** (`telemetry/proxy.py`, `telemetry/test.py`) - Frontend telemetry proxy ❌ REMOVE
6. **DevTools Tracing** (`devtools/tracing.py`) - Function call decorator ❌ REMOVE
7. **Log Broker** (`log_broker.py`) - Redis pubsub for multi-worker ✅ KEEP
8. **Streaming** (`devtools/streaming.py`) - SSE endpoint ✅ KEEP

### Problems:
- **Too many layers**: Logs go through structlog → DevConsole → Redis → SSE
- **Too many concepts**: Traces, Metrics, Logs, Heartbeats, Events
- **Optional dependencies** making code complex (prometheus-client, opentelemetry-*)
- **Multiple import paths** for similar functionality
- **Unused features**: OTLP export, Prometheus metrics endpoint

## Goal

**Simple, effective observability:**
1. **Dev Console** - Real-time logs via SSE for development
2. **Excellent API Error Messages** - Clear, actionable error responses
3. **Clean Logging** - Single path: structlog → DevConsole (if debug mode)

## Implementation Plan

### Phase 1: Remove OpenTelemetry Integration
**Files to modify:**
- `backend/src/platform/infrastructure/tracing.py` - DELETE entire file
- `backend/src/platform/infrastructure/devconsole_exporter.py` - DELETE entire file
- `backend/src/api/main.py` - Remove tracing setup in `_setup_observability()`
- `backend/src/platform/health/router.py` - Remove tracing imports if any

**Impact:** Removes ~500 lines of complex tracing code

### Phase 2: Remove Prometheus Metrics
**Files to modify:**
- `backend/src/platform/infrastructure/metrics.py` - DELETE entire file
- `backend/src/api/main.py` - Remove `/metrics` endpoint and metrics imports
- Remove any `record_*_metric()` calls throughout codebase

**Impact:** Removes ~350 lines of metrics code

### Phase 3: Remove Telemetry Proxy
**Files to modify:**
- `backend/src/platform/telemetry/proxy.py` - DELETE entire file
- `backend/src/platform/telemetry/test.py` - DELETE entire file
- `backend/src/api/main.py` - Remove telemetry router includes
- Consider deleting `backend/src/platform/telemetry/` directory entirely if empty

**Impact:** Removes frontend→backend telemetry forwarding (not needed)

### Phase 4: Remove DevTools Function Tracing
**Files to modify:**
- `backend/src/platform/devtools/tracing.py` - DELETE entire file
- Remove any `@trace` decorator usage in services

**Impact:** Removes decorator-based function tracing (too verbose)

### Phase 5: Simplify DevConsole Logging
**Files to consolidate:**
- **MERGE** `dev_logs.py` and `devconsole_types.py` into single `devconsole.py`
- Simplify logging functions to just:
  - `log_api_request()`
  - `log_api_response()`
  - `log_error()`
  - `log_info()`  # Generic info log

**Remove:**
- `log_pm4py_operation()` - Too specific, use generic logging
- `log_circuit_breaker()` - Not using circuit breakers
- `log_perf_warning()` - Covered by slow request middleware
- `log_database_query()` - Too verbose
- `log_cache_operation()` - Too verbose
- `log_validation()` - Use regular logging
- `log_auth_event()` - Use regular logging

**Keep:**
- `SystemMetrics` - Still useful for heartbeat
- `HeartbeatMessage` - Still useful for SSE
- `DevLogEntry` - Core log structure
- Redis pubsub via `log_broker.py` - Needed for multi-worker

**Impact:** Reduces from ~530 lines to ~200 lines

### Phase 6: Simplify Middleware Logging
**Files to modify:**
- `backend/src/platform/core/middleware.py`
  - Keep `RequestLoggingMiddleware`
  - Keep `PerformanceLoggingMiddleware`
  - Simplify DevConsole integration - just call `log_api_request/response`

**Impact:** Cleaner middleware, less coupling

### Phase 7: Enhance API Error Responses
**Files to modify:**
- `backend/src/platform/core/exceptions.py` - Review and ensure clear error messages
- `backend/src/api/main.py` - Review exception handlers
  - Ensure `AppException` handler returns detailed, actionable errors
  - Ensure global exception handler logs full stack trace in debug mode
  - Add helpful "what to do next" hints in error messages

**Enhancement ideas:**
- Include request context in errors (request_id, timestamp)
- Add error categorization (validation, not_found, permission, server_error)
- Include relevant data in error response (e.g., which field failed validation)

### Phase 8: Clean Up Dependencies
**Files to modify:**
- `backend/pyproject.toml`
  - Move `prometheus-client` from optional to unused (or remove entirely)
  - Move `opentelemetry-*` from optional to unused (or remove entirely)
  - Keep `structlog` and `redis` (core dependencies)

### Phase 9: Update Main Application Setup
**Files to modify:**
- `backend/src/api/main.py`
  - Remove `_setup_observability()` function (or simplify to just Redis connection)
  - Remove `/metrics` endpoint
  - Remove tracing imports
  - Remove telemetry router

**Simplified setup:**
```python
async def lifespan(app: FastAPI):
    # Startup
    configure_logging()  # structlog
    await init_database()
    await startup_log_broker()  # Redis for DevConsole
    await _seed_mvp_data()
    mark_startup_complete()
    yield
    # Shutdown
    await close_database()
    await shutdown_log_broker()
```

### Phase 10: Consolidate DevConsole Module
**New structure:**
```
backend/src/platform/devconsole/
├── __init__.py          # Public API exports
├── models.py            # Pydantic models (DevLogEntry, SystemMetrics, etc.)
├── logging.py           # Log functions (log_api_request, log_error, etc.)
├── broker.py            # Redis pubsub (current log_broker.py)
└── streaming.py         # SSE endpoint (current devtools/streaming.py)
```

**Benefits:**
- Clear module boundary
- Single import path: `from src.platform.devconsole import log_error`
- Easier to understand and maintain

## File Changes Summary

### Files to DELETE (7 files):
1. `backend/src/platform/infrastructure/tracing.py` (~296 lines)
2. `backend/src/platform/infrastructure/devconsole_exporter.py` (~141 lines)
3. `backend/src/platform/infrastructure/metrics.py` (~344 lines)
4. `backend/src/platform/telemetry/proxy.py` (~204 lines)
5. `backend/src/platform/telemetry/test.py` (~50 lines est.)
6. `backend/src/platform/devtools/tracing.py` (~114 lines)
7. `backend/src/platform/infrastructure/dev_logs.py` (will merge)

### Files to CREATE (4 files):
1. `backend/src/platform/devconsole/__init__.py`
2. `backend/src/platform/devconsole/models.py` (from devconsole_types.py)
3. `backend/src/platform/devconsole/logging.py` (simplified from dev_logs.py)
4. `backend/src/platform/devconsole/broker.py` (move log_broker.py)

### Files to MODIFY (6 files):
1. `backend/src/api/main.py` - Remove observability setup
2. `backend/src/platform/core/middleware.py` - Simplify DevConsole calls
3. `backend/src/platform/core/exceptions.py` - Enhance error messages
4. `backend/pyproject.toml` - Clean up dependencies
5. `backend/src/platform/devtools/streaming.py` - Move to devconsole/
6. Update all imports throughout codebase

## Expected Results

### Before:
- **7 different observability systems**
- **~2000 lines** of observability code
- **Complex optional dependencies**
- **Multiple import paths** (`from src.platform.infrastructure.dev_logs`, `from src.platform.devtools.tracing`)

### After:
- **2 systems**: Structlog + DevConsole
- **~600 lines** of observability code (70% reduction)
- **Simple core dependencies** (structlog, redis)
- **Single import path**: `from src.platform.devconsole import log_error, log_info`

### Developer Experience:
```python
# Simple logging
from src.platform.devconsole import log_error, log_info
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

# For DevConsole (real-time frontend visibility)
log_info("Processing dataset", dataset_id=dataset_id, event_count=1000)

# For backend logs (structlog)
logger.info("dataset_processed", dataset_id=dataset_id, duration_ms=1234)

# For errors (both DevConsole and logs)
log_error("Failed to process dataset", error_code="DATASET_001", details={...})
```

## Testing Strategy

1. **Test DevConsole SSE stream** - Ensure logs still flow to frontend
2. **Test multi-worker setup** - Ensure Redis pubsub still works
3. **Test error responses** - Verify error messages are clear and actionable
4. **Test backend logs** - Verify structlog still works correctly
5. **Remove observability tests** - Delete tests for removed functionality

## Rollout

1. Create new `devconsole` module structure
2. Update imports across codebase (can do incrementally)
3. Remove old files once all imports updated
4. Update documentation
5. Clean up pyproject.toml dependencies

## Questions for User

None - this plan simplifies to exactly what was requested:
- ✅ Dev Console for real-time observability
- ✅ Excellent error messages on APIs
- ✅ Clean, simple logging
- ✅ No Prometheus, no OTEL, no complexity
