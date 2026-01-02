# Cross-Cutting Concerns

> **Definition:** Functionality that spans multiple layers and features
> **Examples:** Logging, error handling, authentication, caching, monitoring

---

## Overview

Cross-cutting concerns are architectural aspects that affect the entire system. Unlike features that live in specific layers, these concerns cut across all layers and must be applied consistently.

```mermaid
mindmap
  root((Cross-Cutting<br/>Concerns))
    Security
      Authentication
      Authorization
      Data Privacy
    Reliability
      Error Handling
      Retry Logic
      Circuit Breaker
      Idempotency
    Observability
      Logging
      Metrics
      Tracing
      Health Checks
    Performance
      Caching
      Rate Limiting
      Connection Pooling
    Development
      Testing
      Documentation
      Code Quality
```

---

## Documentation Index

### 1. [Error Handling](./error-handling.md)
**Standard:** RFC 7807 Problem Details

**Topics:**
- Exception hierarchy
- Error codes catalog
- HTTP status mapping
- Correlation IDs
- Retry hints
- Error responses

**Key Files:**
- `src/core/exceptions.py` - Exception classes
- `src/core/error_codes.py` - Error catalog
- `src/api/main.py` - Exception handlers

### 2. [Logging](./logging.md)
**Framework:** Structlog (structured logging)

**Topics:**
- Structured vs traditional logging
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Context binding (request_id, user_id)
- JSON output (production)
- Console output (development)
- Performance logging

**Key Files:**
- `src/core/logging_config.py` - Structlog configuration
- `src/core/middleware.py` - Request logging middleware

### 3. [Authentication & Authorization](./auth.md)
**Standard:** JWT (JSON Web Tokens) + RBAC

**Topics:**
- JWT token structure
- Login/register flow
- Token refresh
- Role-based access control (RBAC)
- Workspace-level permissions
- Dependency injection patterns

**Key Files:**
- `src/api/routers/auth.py` - Auth endpoints
- `src/api/dependencies.py` - Auth dependencies
- `src/models/orm.py` - User, Organization, Workspace tables

### 4. [Caching Strategy](./caching.md)
**Technology:** Redis

**Topics:**
- Cache-aside pattern
- TTL strategies
- Cache invalidation
- Cache keys naming
- Fallback behavior (no Redis)

**Key Files:**
- `src/infrastructure/cache.py` - Redis wrapper
- `src/services/*.py` - Service-level caching

### 5. [Testing Guide](./testing.md)
**Framework:** Pytest

**Topics:**
- Unit tests (domain layer)
- Integration tests (with test DB)
- API tests (with TestClient)
- Fixtures and factories
- Mocking strategies
- Coverage targets

**Key Files:**
- `tests/conftest.py` - Pytest fixtures
- `tests/test_*.py` - Test suites

### 6. [Performance Optimization](./performance.md)

**Topics:**
- Database query optimization
- PM4Py circuit breaker
- DuckDB for CSV ingestion
- Connection pooling
- Async patterns
- Memory management

**Key Files:**
- `src/infrastructure/circuit_breaker.py` - Circuit breaker
- `src/services/duckdb_ingestion.py` - Fast ingestion
- `src/models/database.py` - Connection pooling

### 7. [Observability](./observability.md)

**Topics:**
- Prometheus metrics
- OpenTelemetry tracing
- Health checks
- Real-time log streaming
- Frontend DevConsole integration

**Key Files:**
- `src/infrastructure/metrics.py` - Prometheus metrics
- `src/infrastructure/tracing.py` - OpenTelemetry
- `src/api/routers/health.py` - Health endpoints

### 8. [Resilience Patterns](./resilience.md)

**Topics:**
- Circuit breaker (PM4Py operations)
- Retry with exponential backoff
- Timeouts
- Graceful degradation
- Bulkhead pattern

**Key Files:**
- `src/infrastructure/circuit_breaker.py` - Circuit breaker
- `src/infrastructure/retry.py` - Retry logic

### 9. [Data Privacy & Security](./privacy.md)

**Topics:**
- PII detection
- Anonymization strategies
- GDPR compliance
- Secure file storage
- SQL injection prevention

**Key Files:**
- `src/services/privacy.py` - Anonymization service
- `src/core/config.py` - Security settings

### 10. [Development Workflow](./development-guide.md)

**Topics:**
- Local setup
- Code quality checks (ruff, mypy, bandit)
- Git workflow
- Database migrations
- SDK generation

**Key Files:**
- `Makefile` - Development commands
- `pyproject.toml` - Project configuration
- `alembic/` - Database migrations

---

## Quick Reference Matrix

| Concern | Location | Technology | Configuration | Status |
|---------|----------|------------|---------------|--------|
| **Error Handling** | `src/core/exceptions.py` | RFC 7807 | Error codes in `error_codes.py` | ✅ Implemented |
| **Logging** | `src/core/logging_config.py` | Structlog | `LOG_LEVEL`, `LOG_JSON` | ✅ Implemented |
| **Authentication** | `src/api/routers/auth.py` | JWT (PyJWT) | `JWT_SECRET`, `AUTH_ENABLED` | ✅ Implemented |
| **Caching** | `src/infrastructure/cache.py` | Redis | `CACHE_ENABLED`, `CACHE_DEFAULT_TTL` | ✅ Implemented |
| **Metrics** | `src/infrastructure/metrics.py` | Prometheus | `/metrics` endpoint | ⚠️ Partial |
| **Tracing** | `src/infrastructure/tracing.py` | OpenTelemetry | `OTEL_EXPORTER_OTLP_ENDPOINT` | ⚠️ Optional |
| **Circuit Breaker** | `src/infrastructure/circuit_breaker.py` | Custom | Failure threshold: 5, timeout: 60s | ✅ Implemented |
| **Retry Logic** | `src/infrastructure/retry.py` | Tenacity | Max 3 attempts, exponential backoff | ✅ Implemented |
| **Rate Limiting** | `src/infrastructure/rate_limiter.py` | Redis | Token bucket algorithm | ⚠️ Partial |
| **Health Checks** | `src/api/routers/health.py` | Custom | `/health`, `/health/live`, `/health/ready` | ✅ Implemented |

---

## Implementation Patterns

### Pattern 1: Request Context Binding

**File:** `src/core/middleware.py:RequestLoggingMiddleware`

Every request gets a unique `request_id` that propagates through all logs:

```python
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Bind to structlog context
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path
        )

        response = await call_next(request)

        # Clear context after request
        structlog.contextvars.clear_contextvars()

        return response
```

**Result:** All logs within a request have the same `request_id`:

```json
{"event": "request_started", "request_id": "req_abc123", "path": "/api/v1/datasets/upload"}
{"event": "dataset_uploaded", "request_id": "req_abc123", "dataset_id": "xyz789"}
{"event": "request_completed", "request_id": "req_abc123", "duration_ms": 234}
```

---

### Pattern 2: Dependency Injection for Cross-Cutting Concerns

**File:** `src/api/dependencies.py`

```python
from fastapi import Depends, HTTPException, Header
from typing import Optional

# Logging dependency
async def get_logger():
    """Inject structured logger with request context"""
    return structlog.get_logger()

# Authentication dependency
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Inject authenticated user"""
    if not authorization:
        raise HTTPException(401, "Missing authorization header")

    token = authorization.replace("Bearer ", "")
    payload = decode_jwt(token)
    user = await db.get(User, payload["sub"])

    if not user:
        raise HTTPException(401, "Invalid token")

    return user

# Cache dependency
async def get_cache() -> RedisCache:
    """Inject cache service with fallback"""
    try:
        return RedisCache(url=settings.REDIS_URL)
    except ConnectionError:
        return NoOpCache()  # Graceful degradation
```

**Usage in Router:**
```python
@router.get("/datasets")
async def list_datasets(
    current_user: User = Depends(get_current_user),  # Auth
    logger: Logger = Depends(get_logger),            # Logging
    cache: RedisCache = Depends(get_cache),          # Caching
    db: AsyncSession = Depends(get_db)
):
    logger.info("listing_datasets", user_id=current_user.id)

    # Try cache first
    cached = await cache.get(f"datasets:{current_user.id}")
    if cached:
        return json.loads(cached)

    # Query database
    datasets = await db.execute(select(Dataset).where(Dataset.user_id == current_user.id))
    result = datasets.scalars().all()

    # Cache for 5 minutes
    await cache.set(f"datasets:{current_user.id}", json.dumps(result), ttl=300)

    return result
```

---

### Pattern 3: Decorator-Based Circuit Breaker

**File:** `src/infrastructure/circuit_breaker.py`

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60, expected_exception=TimeoutError)
def pm4py_operation_with_protection(log, operation_type: str):
    """Circuit breaker prevents cascade failures from PM4Py timeouts"""

    if operation_type == "discovery":
        return pm4py.discover_petri_net_inductive(log)
    elif operation_type == "conformance":
        return pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)
    else:
        raise ValueError(f"Unknown operation: {operation_type}")
```

**Behavior:**
- First 5 timeouts: Retries normally
- After 5 failures: Circuit opens (fail fast for 60 seconds)
- After 60 seconds: Circuit half-opens (try one request)
- If successful: Circuit closes (back to normal)

---

### Pattern 4: Retry with Exponential Backoff

**File:** `src/infrastructure/retry.py`

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry_if=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True
)
async def save_to_database_with_retry(db: AsyncSession, data: dict):
    """Retry database operations with exponential backoff"""
    await db.execute(insert(Dataset).values(data))
    await db.commit()
```

**Retry Schedule:**
- Attempt 1: Immediate
- Attempt 2: Wait 2 seconds
- Attempt 3: Wait 4 seconds
- Attempt 4: Wait 8 seconds
- Max wait: 10 seconds

---

### Pattern 5: Cache-Aside (Lazy Loading)

**File:** `src/services/analytics.py`

```python
async def get_bottlenecks(
    dataset_id: str,
    cache: RedisCache,
    db: AsyncSession
) -> dict:
    """Cache-aside pattern for expensive analytics"""

    cache_key = f"bottlenecks:{dataset_id}"

    # 1. Try cache first
    cached = await cache.get(cache_key)
    if cached:
        logger.info("cache_hit", key=cache_key)
        return json.loads(cached)

    # 2. Cache miss - compute from DB
    logger.info("cache_miss", key=cache_key)
    events = await load_events(db, dataset_id)
    log = convert_to_pm4py_log(events)
    bottlenecks = pm4py.discover_performance_dfg(log)

    # 3. Write to cache
    await cache.set(cache_key, json.dumps(bottlenecks), ttl=3600)

    return bottlenecks
```

---

## Configuration by Environment

### Development (.env.dev)
```env
DEBUG=true
LOG_LEVEL=DEBUG
LOG_JSON=false                # Colored console output
AUTH_ENABLED=false            # Disable auth for local dev
CACHE_ENABLED=false           # Optional Redis
DATABASE_URL=sqlite+aiosqlite:///./data/db/dev.db
```

### Production (.env.prod)
```env
DEBUG=false
LOG_LEVEL=INFO
LOG_JSON=true                 # JSON logs for aggregation
AUTH_ENABLED=true             # Enforce authentication
CACHE_ENABLED=true            # Redis required
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/pmdb
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317  # Tracing
```

---

## Testing Cross-Cutting Concerns

### Test Error Handling

**File:** `tests/test_error_handling.py`

```python
def test_rfc7807_error_response(client: TestClient):
    """Test error responses conform to RFC 7807"""
    response = client.get("/api/v1/datasets/nonexistent")

    assert response.status_code == 404
    body = response.json()

    # RFC 7807 required fields
    assert "type" in body
    assert "title" in body
    assert "status" in body
    assert "detail" in body
    assert "instance" in body

    # Custom fields
    assert "error_code" in body
    assert "request_id" in body
    assert body["error_code"] == "DATASET_NOT_FOUND"
```

### Test Logging

```python
def test_request_logging(client: TestClient, caplog):
    """Test requests are logged with correlation IDs"""
    response = client.get(
        "/api/v1/datasets",
        headers={"X-Request-ID": "test_req_123"}
    )

    assert response.status_code == 200

    # Verify log contains request_id
    logs = [r for r in caplog.records if "request_id" in r.message]
    assert any("test_req_123" in log.message for log in logs)
```

### Test Caching

```python
@pytest.mark.asyncio
async def test_cache_aside_pattern(mock_cache, test_db):
    """Test cache-aside pattern for analytics"""

    # First call - cache miss
    result1 = await get_bottlenecks("dataset_1", mock_cache, test_db)
    assert mock_cache.get.call_count == 1
    assert mock_cache.set.call_count == 1

    # Second call - cache hit
    result2 = await get_bottlenecks("dataset_1", mock_cache, test_db)
    assert mock_cache.get.call_count == 2
    assert mock_cache.set.call_count == 1  # No new writes

    assert result1 == result2
```

---

## Monitoring Checklist

### Production Readiness

- [ ] **Logging:** JSON output enabled (`LOG_JSON=true`)
- [ ] **Metrics:** Prometheus endpoint accessible (`/metrics`)
- [ ] **Tracing:** OpenTelemetry exporting to Jaeger/Zipkin
- [ ] **Health Checks:** Kubernetes probes configured (`/health/live`, `/health/ready`)
- [ ] **Error Tracking:** Sentry/Rollbar integration (optional)
- [ ] **Caching:** Redis cluster configured
- [ ] **Authentication:** JWT secret rotated regularly
- [ ] **Rate Limiting:** Enabled for public endpoints
- [ ] **Circuit Breakers:** Configured for external dependencies
- [ ] **Database:** Connection pooling optimized

---

## Common Issues & Solutions

### Issue: Logs Missing Request Context

**Symptom:** Logs don't have `request_id` field

**Solution:** Ensure `RequestLoggingMiddleware` is registered:
```python
# src/api/main.py
app.add_middleware(RequestLoggingMiddleware)
```

---

### Issue: Cache Always Misses

**Symptom:** Cache hit rate = 0%

**Solution:** Check Redis connectivity:
```bash
redis-cli ping  # Should return PONG
echo "CACHE_ENABLED=true" >> .env
```

---

### Issue: Circuit Breaker Always Open

**Symptom:** All PM4Py operations fail immediately

**Solution:** Reduce failure threshold or increase timeout:
```python
@circuit(failure_threshold=10, recovery_timeout=120)  # More lenient
```

---

## Next Steps

Read detailed documentation for each concern:

1. **[Error Handling](./error-handling.md)** - RFC 7807, exception hierarchy
2. **[Logging](./logging.md)** - Structlog, context binding
3. **[Authentication](./auth.md)** - JWT, RBAC
4. **[Caching](./caching.md)** - Redis, cache-aside pattern
5. **[Testing](./testing.md)** - Pytest, fixtures, coverage
6. **[Performance](./performance.md)** - Optimization strategies
7. **[Observability](./observability.md)** - Metrics, tracing, health checks
8. **[Resilience](./resilience.md)** - Circuit breaker, retry logic
9. **[Privacy](./privacy.md)** - GDPR, anonymization
10. **[Development Guide](./development-guide.md)** - Workflow, tools

**Also See:**
- [Architecture Overview](../00-overview/architecture.md)
- [Layer Documentation](../02-layers/README.md)
- [Feature Documentation](../01-features/README.md)
