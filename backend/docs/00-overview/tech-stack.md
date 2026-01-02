# Technology Stack

> **Version:** 1.0.0
> **Python:** ≥3.11
> **Last Updated:** 2026-01-02

## Tech Stack Matrix

### Core Process Mining

| Technology | Version | License | Purpose | Critical? | Replaceable? |
|------------|---------|---------|---------|-----------|--------------|
| **PM4Py** | ≥2.7.0 | GPL-3.0 | Process mining algorithms (discovery, conformance, analytics) | ✅ Yes | ❌ No - Core dependency |
| **NetworkX** | ≥3.2 | BSD-3 | Graph analysis for organizational mining | ✅ Yes | ⚠️ Difficult - Deep integration |

**PM4Py Capabilities:**
- **Discovery Algorithms:** Alpha, Alpha+, Inductive, Heuristics, ILP, DFG
- **Conformance:** Token replay, Alignments
- **Model Formats:** Petri nets, Process trees, BPMN, DFG
- **Analytics:** Bottleneck detection, variant analysis, performance metrics

> [!IMPORTANT]
> **PM4Py GPL License Implications**
> - GPL-3.0 is viral for distribution
> - SaaS deployment = no source code distribution requirement
> - If distributing binary: entire codebase must be GPL
> - Consider commercial alternatives: Celonis SDK, ProcessGold API

---

### Web Framework Stack

| Technology | Version | License | Purpose | Alternatives |
|------------|---------|---------|---------|--------------|
| **FastAPI** | ≥0.109.0 | MIT | Async web framework, auto OpenAPI docs | Django REST, Flask, Litestar |
| **Uvicorn** | ≥0.27.0 | BSD-3 | ASGI server (production via Gunicorn) | Hypercorn, Daphne |
| **Pydantic** | ≥2.5.0 | MIT | Data validation, settings management | Marshmallow, attrs+cattrs |
| **python-multipart** | latest | Apache-2.0 | File upload support | - |
| **python-jose[cryptography]** | ≥3.3.0 | MIT | JWT token handling | PyJWT (used instead) |

**Why FastAPI?**
- ✅ Native async/await support
- ✅ Auto-generated OpenAPI/Swagger docs
- ✅ Type-safe dependency injection
- ✅ Pydantic integration (validation + serialization)
- ✅ 3x faster than Flask in benchmarks
- ❌ Smaller ecosystem than Django

---

### Data Persistence

#### Database

| Technology | Version | License | Purpose | Migration Path |
|------------|---------|---------|---------|----------------|
| **SQLAlchemy** | ≥2.0.0 | MIT | Async ORM (2.0 style) | - |
| **aiosqlite** | ≥0.19.0 | MIT | Async SQLite driver | asyncpg (for PostgreSQL) |
| **Alembic** | ≥1.13.0 | MIT | Database migrations | - |

**Current Database: SQLite**
- ✅ Zero-config, file-based, perfect for MVP
- ✅ ACID compliant, ~1M+ events
- ❌ Single-writer (no horizontal scaling)
- ❌ No network access (embedded only)

**Production Database: PostgreSQL (Recommended)**
```python
# Migration path
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"
```

#### Caching & Queue

| Technology | Version | License | Purpose | Alternatives |
|------------|---------|---------|---------|--------------|
| **Redis** | ≥5.0.0 | BSD-3 | Cache, session store, Celery broker | Memcached (cache only) |
| **redis-py** | ≥5.0.0 | MIT | Redis Python client | - |

**Redis Use Cases:**
1. **Cache:** Analytics results (bottlenecks, conformance) - TTL 3600s
2. **Session Store:** User sessions, JWT blacklist
3. **Task Queue:** Celery broker + result backend
4. **Rate Limiting:** Token bucket per user

---

### High-Performance Data Processing

| Technology | Version | License | Purpose | Performance Gain |
|------------|---------|---------|---------|------------------|
| **DuckDB** | ≥1.0.0 | MIT | Embedded OLAP database for CSV ingestion | **10x faster** than pandas |
| **PyArrow** | ≥15.0.0 | Apache-2.0 | Columnar data format (Arrow IPC) | Zero-copy data exchange |

**DuckDB Advantage:**
```python
# Traditional pandas approach: ~10s for 100K rows
df = pd.read_csv("events.csv")
for _, row in df.iterrows():
    db.add(ProcessEvent(**row))

# DuckDB approach: ~1s for 100K rows
result = duckdb.execute("SELECT * FROM 'events.csv'").arrow()
db.execute(insert(ProcessEvent).values(result.to_pylist()))
```

**Why DuckDB?**
- ✅ Columnar storage (better compression)
- ✅ Vectorized query execution
- ✅ Native Arrow support
- ✅ SQL interface for data transformation
- ✅ Embedded (no server required)

---

### Background Jobs & Async Tasks

| Technology | Version | License | Purpose | Status |
|------------|---------|---------|---------|--------|
| **Celery** | ≥5.3.0 | BSD-3 | Distributed task queue | ⚠️ Implemented, not active |
| **Flower** | ≥2.0.0 | BSD-3 | Celery monitoring UI | ⚠️ Optional |
| **celery-types** | latest | MIT | Celery type stubs | Dev dependency |

**Celery Task Examples:**
```python
@celery_app.task(bind=True, max_retries=3)
def discover_process_model_async(self, dataset_id: str, miner_type: str):
    """Long-running discovery for 100K+ events"""
    return MiningService().discover_model(dataset_id, miner_type)

@celery_app.task
def generate_conformance_report_async(dataset_id: str, model_id: str):
    """Alignment-based conformance (can take 5+ minutes)"""
    return ConformanceService().check_alignments(dataset_id, model_id)
```

**Celery Queues:**
- `celery` (default) - General tasks
- `priority` - High-priority user requests
- `analytics` - Long-running analytics

---

### Machine Learning

| Technology | Version | License | Purpose | Used For |
|------------|---------|---------|---------|----------|
| **scikit-learn** | ≥1.4.0 | BSD-3 | Classical ML algorithms | Next activity prediction, outcome classification |
| **XGBoost** | ≥2.0.0 | Apache-2.0 | Gradient boosting | Remaining time prediction |
| **NumPy** | ≥1.24.0 | BSD-3 | Numerical computing | Feature engineering |
| **pandas** | ≥2.0.0 | BSD-3 | Data manipulation | Log preprocessing (limited use) |

**ML Use Cases:**
1. **Next Activity Prediction:** RandomForest on activity sequences
2. **Remaining Time Prediction:** XGBoost regression
3. **Outcome Classification:** Logistic regression on case features

> [!WARNING]
> **Pandas Usage**
> - Avoid pandas for large files (use DuckDB instead)
> - Pandas only used for small transformations (<10K rows)
> - Memory inefficient for event logs >100K rows

---

### Authentication & Security

| Technology | Version | License | Purpose | Alternatives |
|------------|---------|---------|---------|--------------|
| **PyJWT** | ≥2.8.0 | MIT | JWT token encoding/decoding | python-jose, authlib |
| **passlib[bcrypt]** | ≥1.7.4 | BSD | Password hashing | argon2-cffi |
| **bcrypt** | ≥4.1.0 | Apache-2.0 | Bcrypt algorithm | - |
| **cryptography** | ≥41.0.0 | Apache-2.0/BSD | Cryptographic primitives | - |

**Security Configuration:**
```python
# JWT Settings
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 1440  # 24 hours

# Password Hashing (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
rounds = 12  # Cost factor (2^12 iterations)
```

**JWT Claims:**
```json
{
  "sub": "user_id",
  "org_id": "org_uuid",
  "email": "user@example.com",
  "role": "workspace_member",
  "exp": 1704153600,
  "iat": 1704067200
}
```

---

### Observability Stack

#### Logging

| Technology | Version | License | Purpose | Config |
|------------|---------|---------|---------|--------|
| **structlog** | ≥24.1.0 | MIT/Apache-2.0 | Structured logging | JSON (prod) / Console (dev) |

**Structlog Configuration:**
```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer() if LOG_JSON else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

**Log Example:**
```json
{
  "event": "process_model_discovered",
  "dataset_id": "abc123",
  "miner_type": "inductive",
  "num_events": 10523,
  "duration_ms": 1234,
  "fitness": 0.95,
  "timestamp": "2026-01-02T10:30:45.123Z",
  "level": "info",
  "logger": "src.services.mining",
  "request_id": "req_xyz789"
}
```

#### Metrics

| Technology | Version | License | Purpose | Endpoint |
|------------|---------|---------|---------|----------|
| **prometheus-client** | ≥0.19.0 | Apache-2.0 | Metrics collection | `/metrics` |

**Available Metrics:**
```python
# HTTP Metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

# PM4Py Metrics
pm4py_operations_total = Counter('pm4py_operations_total', 'PM4Py operations', ['operation_type', 'status'])
pm4py_duration = Histogram('pm4py_operation_duration_seconds', 'PM4Py operation duration', ['operation_type'])

# Cache Metrics
cache_hits_total = Counter('cache_hits_total', 'Cache hits', ['cache_type'])
cache_misses_total = Counter('cache_misses_total', 'Cache misses', ['cache_type'])

# Database Metrics
db_connections_active = Gauge('db_connections_active', 'Active database connections')
```

#### Distributed Tracing (Optional)

| Technology | Version | License | Purpose | Backend |
|------------|---------|---------|---------|---------|
| **OpenTelemetry** | ≥1.22.0 | Apache-2.0 | Distributed tracing | Jaeger, Zipkin, Tempo |
| **opentelemetry-api** | ≥1.22.0 | Apache-2.0 | Tracing API | - |
| **opentelemetry-sdk** | ≥1.22.0 | Apache-2.0 | Tracing SDK | - |
| **opentelemetry-instrumentation-fastapi** | ≥0.43b0 | Apache-2.0 | Auto-instrumentation | - |

**Trace Example:**
```
Trace ID: 7d2e8a9f-3b1c-4e5d-9f8a-1c2d3e4f5a6b
  Span: POST /api/v1/discovery/discover [2.3s]
    Span: MiningService.discover_model [2.1s]
      Span: Load events from DB [0.5s]
      Span: Convert to PM4Py log [0.2s]
      Span: PM4Py Inductive Miner [1.3s]
      Span: Save model to DB [0.1s]
```

---

### Development Tools

| Technology | Version | License | Purpose | When Used |
|------------|---------|---------|---------|-----------|
| **pytest** | ≥7.4.0 | MIT | Test framework | `make test` |
| **pytest-asyncio** | ≥0.21.0 | Apache-2.0 | Async test support | All service tests |
| **pytest-cov** | ≥4.1.0 | MIT | Coverage reporting | `make test-cov` |
| **ruff** | ≥0.1.0 | MIT | Linter + formatter (Rust-based) | `make check` |
| **mypy** | ≥1.8.0 | MIT | Static type checker | `make check` |
| **bandit** | ≥1.7.0 | Apache-2.0 | Security linter | `make check` |
| **black** | ≥23.12.0 | MIT | Code formatter (deprecated by ruff) | - |
| **isort** | ≥5.13.0 | MIT | Import sorter (deprecated by ruff) | - |

**Why Ruff?**
- ✅ 10-100x faster than Black + isort
- ✅ Replaces 10+ tools (Flake8, isort, Black, etc.)
- ✅ Written in Rust (single binary)
- ✅ Drop-in replacement for existing tools

**Makefile Commands:**
```bash
make check          # Lint, format, typecheck, security scan
make test           # Run pytest
make test-cov       # Tests with coverage report
```

---

### Infrastructure & Resilience

| Technology | Version | License | Purpose | Pattern |
|------------|---------|---------|---------|---------|
| **tenacity** | ≥8.2.0 | Apache-2.0 | Retry logic | Exponential backoff |
| **circuitbreaker** | ≥1.4.0 | BSD-3 | Circuit breaker | PM4Py operations |

**Circuit Breaker Example:**
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60, expected_exception=TimeoutError)
def discover_model_with_circuit_breaker(log, miner_type):
    """Circuit opens after 5 timeouts, closes after 60s"""
    return pm4py.discover_petri_net_inductive(log)
```

**Retry Configuration:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def save_to_db_with_retry(data):
    """Retry 3 times with exponential backoff: 2s, 4s, 8s"""
    await db.save(data)
```

---

### SDK Generation

| Technology | Version | License | Purpose | Output |
|------------|---------|---------|---------|--------|
| **@openapitools/openapi-generator-cli** | ≥2.7.0 | Apache-2.0 | TypeScript SDK generation | `sdk/src/` |

**SDK Generation Workflow:**
1. FastAPI generates OpenAPI spec at `/openapi.json`
2. `npm run generate` in `sdk/` directory
3. OpenAPI Generator creates TypeScript client
4. `npm run build` compiles to `dist/`

**SDK Usage (Frontend):**
```typescript
import { ProcessesApi, Configuration } from '@/sdk';

const api = new ProcessesApi(new Configuration({
  basePath: 'http://localhost:8001',
  accessToken: 'jwt_token_here'
}));

const datasets = await api.listDatasets();
```

---

## Dependency Graph

```mermaid
graph TB
    subgraph "Web Layer"
        FastAPI --> Pydantic
        FastAPI --> Uvicorn
        Uvicorn --> Starlette
    end

    subgraph "Data Layer"
        SQLAlchemy --> aiosqlite
        SQLAlchemy --> Alembic
        DuckDB --> PyArrow
    end

    subgraph "Process Mining"
        PM4Py --> NetworkX
        PM4Py --> Pandas
        PM4Py --> NumPy
    end

    subgraph "Infrastructure"
        Celery --> Redis
        structlog --> python-json-logger
        CircuitBreaker --> PM4Py
    end

    subgraph "ML"
        sklearn --> NumPy
        XGBoost --> NumPy
    end

    FastAPI --> SQLAlchemy
    FastAPI --> Redis
    FastAPI --> PM4Py
    FastAPI --> DuckDB
    FastAPI --> structlog
    FastAPI --> PyJWT
```

---

## Version Compatibility Matrix

| Python Version | Supported? | Notes |
|---------------|------------|-------|
| 3.11 | ✅ Recommended | Best performance, async improvements |
| 3.12 | ✅ Supported | Tested, all features work |
| 3.10 | ⚠️ Legacy | Works but missing performance improvements |
| 3.9 | ❌ Not supported | Missing match/case, async improvements |

| OS | Supported? | Notes |
|----|------------|-------|
| **Linux** | ✅ Primary | Ubuntu 22.04+, Debian 11+ |
| **macOS** | ✅ Development | macOS 12+ |
| **Windows** | ⚠️ Limited | WSL2 recommended |

---

## License Summary

| License Type | Libraries | Implications |
|--------------|-----------|--------------|
| **MIT** | FastAPI, SQLAlchemy, Redis, Pydantic | ✅ Permissive, commercial-friendly |
| **Apache-2.0** | Celery, PyArrow, DuckDB, OpenTelemetry | ✅ Permissive, patent grant |
| **BSD-3** | NetworkX, scikit-learn, pandas | ✅ Permissive |
| **GPL-3.0** | PM4Py | ⚠️ Viral for distribution, OK for SaaS |

> [!IMPORTANT]
> **GPL Compliance**
> - PM4Py is GPL-3.0 (copyleft license)
> - **SaaS deployment:** No source code distribution required (AGPL would be different)
> - **Binary distribution:** Would require open-sourcing entire codebase
> - **Mitigation:** Keep PM4Py isolated in service layer, consider commercial alternatives

---

## Performance Benchmarks

### CSV Ingestion (100K events)

| Method | Time | Memory | Throughput |
|--------|------|--------|------------|
| Pandas + iterrows | 10.2s | 450 MB | 9,800 rows/s |
| Pandas + bulk insert | 3.1s | 420 MB | 32,200 rows/s |
| **DuckDB + Arrow** | **1.0s** | **180 MB** | **100,000 rows/s** |

### Process Discovery (10K events)

| Miner | Time | Memory | Quality |
|-------|------|--------|---------|
| Alpha Miner | 0.8s | 120 MB | Low (simple models) |
| Inductive Miner | 2.1s | 180 MB | High (sound models) |
| Heuristics Miner | 1.5s | 150 MB | Medium (tolerates noise) |
| ILP Miner | 45.0s | 2.1 GB | Very High (optimal) |

---

## Upgrade Paths

### SQLite → PostgreSQL

**Benefits:**
- Multi-writer concurrency
- Connection pooling
- Better indexing
- Network access
- Replication

**Migration Steps:**
```bash
# 1. Export SQLite data
sqlite3 data/db/process_mining.db .dump > backup.sql

# 2. Update DATABASE_URL
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/pmdb"

# 3. Run Alembic migrations
alembic upgrade head

# 4. Import data (convert SQLite SQL → PostgreSQL)
psql pmdb < backup_converted.sql
```

### Local Storage → S3

**Benefits:**
- Durability (99.999999999%)
- Scalability
- CDN integration
- Versioning

**Code Changes:**
```python
# Before: Local storage
UPLOAD_DIR = "./data/uploads"

# After: S3 storage
import aioboto3
storage = S3Storage(bucket="pm-uploads", region="us-east-1")
```

---

## Next Steps

- [Architecture Overview](./architecture.md) - System design and C4 diagrams
- [Getting Started](./getting-started.md) - Developer setup guide
- [Feature Documentation](../01-features/README.md) - API feature guides
