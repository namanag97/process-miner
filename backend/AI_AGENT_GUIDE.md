# AI Agent Guide: Backend Codebase

> **Quick Start for AI Agents**: Your comprehensive guide to navigating, understanding, and contributing to the Process Mining SaaS backend.

**Last Updated**: 2026-01-07  
**Tech Stack**: FastAPI + Python 3.10+ + SQLAlchemy + PM4Py + Temporal  
**Architecture**: Clean Architecture with Platform/Feature Layer Separation

---

## 🎯 Quick Context

### What This System Does
A **Process Mining SaaS platform** that analyzes event logs to discover process models, check conformance, detect bottlenecks, and provide ML-powered predictions. Think of it as "analytics for business processes" - upload CSV/XES logs, get insights.

### System Scale
- **19 API Routers**: Discovery, Conformance, Analytics, OCPM, Predictions, etc.
- **6 Architecture Layers**: Platform, Features, API, Services, Domain, Infrastructure
- **23 Database Tables**: Multi-tenant (Org → Workspace → Project → Dataset)
- **~50K Lines of Code**: Well-structured, DDD-inspired

---

## 📁 Navigation Map

### Critical Files (Start Here)

| File | Purpose | When to Read |
|------|---------|--------------|
| [`README.md`](file:///Users/namanagarwal/system/backend/README.md) | Project overview, setup, API endpoints | First time setup |
| [`ARCHITECTURE.md`](file:///Users/namanagarwal/system/backend/ARCHITECTURE.md) | Platform/Feature layer separation | Understanding structure |
| [`AGENT_HANDOFF.md`](file:///Users/namanagarwal/system/backend/AGENT_HANDOFF.md) | DDD refactoring status, remaining work | Continuing refactoring |
| [`Makefile`](file:///Users/namanagarwal/system/backend/Makefile) | Development commands | Running tests, linting |
| [`pyproject.toml`](file:///Users/namanagarwal/system/backend/pyproject.toml) | Dependencies, linter config, import rules | Understanding dependencies |

### Folder Structure

```
backend/
├── src/                          # All source code
│   ├── platform/                 # 🏢 SaaS Infrastructure (NEVER imports features)
│   │   ├── core/                 # Config, exceptions, security, logging
│   │   ├── infrastructure/       # Cache, tasks, metrics, tracing
│   │   ├── auth/                 # Authentication router & service
│   │   ├── users/                # User management
│   │   ├── workspaces/           # Workspace & authorization
│   │   ├── projects/             # Project management
│   │   ├── storage/              # File storage (S3/MinIO)
│   │   ├── jobs/                 # Background jobs
│   │   └── temporal/             # Temporal workflows & workers
│   │
│   ├── features/                 # 🎯 Domain Logic (CAN import platform)
│   │   └── process_mining/
│   │       ├── models/           # Dataset, Analysis, ProcessCase, etc.
│   │       ├── ingestion/        # CSV/XES parsing (DuckDB + PM4Py)
│   │       ├── discovery/        # Mining algorithms (Alpha, Inductive, Heuristics)
│   │       ├── conformance/      # Token replay, alignments
│   │       ├── analytics/        # Performance, bottlenecks, KPIs
│   │       ├── filtering/        # Event log filtering
│   │       ├── organizational/   # Social network analysis
│   │       ├── predictions/      # ML models (scikit-learn, XGBoost)
│   │       ├── simulation/       # Process simulation
│   │       ├── ocpm/             # Object-Centric Process Mining
│   │       └── visualization/    # Graph rendering
│   │
│   ├── api/                      # 🌐 Presentation Layer
│   │   ├── main.py               # FastAPI app, middleware, CORS
│   │   ├── dependencies.py       # Dependency injection
│   │   └── routers/              # API endpoints (grouped by feature)
│   │
│   └── shared/                   # 🔄 Cross-cutting (both layers can import)
│       ├── database.py           # SQLAlchemy Base
│       ├── types/                # Common type definitions
│       └── utils/                # Shared utilities
│
├── tests/                        # Pytest tests (unit, integration, e2e)
├── alembic/                      # Database migrations
├── docs/                         # Comprehensive documentation
│   ├── 01-features/              # Feature-by-feature docs
│   ├── 02-layers/                # Layer architecture docs
│   └── 03-cross-cutting/         # Error handling, logging, testing
│
├── data/                         # Runtime data (gitignored)
│   ├── storage/                  # Uploaded files
│   └── exports/                  # Generated exports
│
└── .agent/workflows/             # AI agent workflow definitions
```

---

## 🏗️ Architecture Principles

### Layer Rules (CRITICAL)

```python
# ✅ ALLOWED
from src.platform.core.config import get_settings          # Platform internal
from src.features.process_mining.models import Dataset     # Feature internal
from src.features.process_mining.discovery import service  # Feature → Platform OK

# ❌ FORBIDDEN
from src.features.* import *                               # Platform → Features NEVER
from src.api.* import *                                    # Services → API NEVER
```

**Why?** Platform is reusable SaaS infrastructure. Features are domain-specific. This separation enables:
- Swapping process mining for other domains (e.g., supply chain analytics)
- Independent testing of platform vs. features
- Clear boundaries enforced by `import-linter` (run `make lint-imports`)

### Import Linter Contracts

Defined in [`pyproject.toml`](file:///Users/namanagarwal/system/backend/pyproject.toml#L222-L285):
1. **Domain Independence**: Domain layer cannot import infrastructure/API
2. **Services Independence**: Services cannot import API
3. **Platform Core Independence**: Platform core cannot import features
4. **Platform Core Purity**: Platform core cannot import platform services

Run `make lint-imports` (custom alias) or `import-linter` to verify.

---

## 🛠️ Common Development Tasks

### 1. Add a New API Endpoint

**Example: Add a new analytics endpoint**

```python
# Step 1: Define Pydantic schema (if needed)
# File: src/features/process_mining/analytics/schemas.py
from pydantic import BaseModel

class BottleneckResponse(BaseModel):
    activity: str
    avg_waiting_time: float
    frequency: int

# Step 2: Add service logic
# File: src/features/process_mining/analytics/service.py
from src.features.process_mining.models import Dataset

class AnalyticsService:
    async def detect_bottlenecks(self, dataset_id: int) -> list[BottleneckResponse]:
        # Business logic here
        pass

# Step 3: Add router endpoint
# File: src/features/process_mining/analytics/router.py
from fastapi import APIRouter, Depends
from src.api.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/datasets/{dataset_id}/bottlenecks")
async def get_bottlenecks(
    dataset_id: int,
    service: AnalyticsService = Depends(),
    user = Depends(get_current_user)
):
    return await service.detect_bottlenecks(dataset_id)

# Step 4: Register router in main.py
# File: src/api/main.py
from src.features.process_mining.analytics.router import router as analytics_router
app.include_router(analytics_router, prefix="/api/v1")
```

**Testing:**
```bash
make test                    # Run all tests
make run                     # Start dev server
curl http://localhost:8001/docs  # Check Swagger UI
```

### 2. Add a Database Migration

```bash
# Auto-generate migration from model changes
.venv/bin/alembic revision --autogenerate -m "Add bottleneck_cache table"

# Review migration in alembic/versions/xxxxx_add_bottleneck_cache.py

# Apply migration
.venv/bin/alembic upgrade head

# Rollback if needed
.venv/bin/alembic downgrade -1
```

### 3. Add Background Job with Temporal

```python
# Step 1: Define workflow
# File: src/platform/temporal/workflows/example.py
from temporalio import workflow

@workflow.defn
class ExampleWorkflow:
    @workflow.run
    async def run(self, dataset_id: int) -> dict:
        # Workflow logic
        return {"status": "complete"}

# Step 2: Create activity
# File: src/platform/temporal/activities/example.py
from temporalio import activity

@activity.defn
async def process_data(dataset_id: int):
    # Activity logic
    pass

# Step 3: Start workflow from API
# File: src/features/process_mining/analytics/service.py
from src.platform.temporal.workflows.example import ExampleWorkflow

async def trigger_analysis(self, dataset_id: int):
    handle = await self.temporal_client.start_workflow(
        ExampleWorkflow.run,
        dataset_id,
        id=f"analysis-{dataset_id}",
        task_queue="analysis-queue"
    )
    return handle.id
```

### 4. Fix a Bug

1. **Locate the bug** using error logs or stack traces
2. **Write a failing test** that reproduces the bug
3. **Fix the code**
4. **Run tests** to ensure fix works: `make test`
5. **Check code quality**: `make check` (lint + typecheck + security)

### 5. Add PM4Py Integration

```python
# Example: Add new discovery algorithm
# File: src/features/process_mining/discovery/service.py
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer

class DiscoveryService:
    async def discover_with_split_miner(self, dataset_id: int):
        # Load event log
        log = await self._load_pm4py_log(dataset_id)
        
        # Apply PM4Py algorithm
        net, im, fm = pm4py.discover_petri_net_split_miner(log)
        
        # Serialize and store
        model_data = self._serialize_petri_net(net, im, fm)
        return await self._save_model(dataset_id, "split_miner", model_data)
```

---

## 🧪 Testing Strategy

### Test Structure

```
tests/
├── unit/                    # Fast, no I/O (mocked dependencies)
├── integration/             # DB interactions, service integration
└── e2e/                     # Full API workflow tests
```

### Running Tests

```bash
make test                    # All tests
make test-cov                # With coverage report
pytest tests/unit -v         # Just unit tests
pytest tests/ -k "test_discover" -v  # Specific test pattern
pytest tests/ -m "not slow" -v       # Skip slow tests
```

### Writing Tests

```python
# tests/features/analytics/test_bottleneck_detection.py
import pytest
from src.features.process_mining.analytics.service import AnalyticsService

@pytest.mark.asyncio
async def test_detect_bottlenecks(sample_dataset):
    """Test bottleneck detection returns expected structure."""
    service = AnalyticsService()
    
    result = await service.detect_bottlenecks(sample_dataset.id)
    
    assert len(result) > 0
    assert all(hasattr(b, 'activity') for b in result)
    assert all(b.avg_waiting_time >= 0 for b in result)
```

Use fixtures from [`tests/conftest.py`](file:///Users/namanagarwal/system/backend/tests/conftest.py) for common setup.

---

## 🔍 Code Patterns & Conventions

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

### Error Handling

Use structured exceptions from `src/platform/core/exceptions.py`:

```python
from src.platform.core.exceptions import NotFoundError, ValidationError

# Raise specific exceptions
if not dataset:
    raise NotFoundError(
        resource_type="Dataset",
        resource_id=dataset_id,
        message="Dataset not found"
    )

# Exceptions are automatically converted to RFC 7807 Problem Details
# Returns: {"type": "not_found", "title": "Dataset not found", ...}
```

### Logging

Use `structlog` for structured logging:

```python
import structlog

logger = structlog.get_logger(__name__)

# Structured logging with context
logger.info(
    "dataset_ingested",
    dataset_id=dataset.id,
    rows=row_count,
    duration_ms=elapsed
)

# Error logging
logger.error(
    "ingestion_failed",
    dataset_id=dataset.id,
    error=str(exc),
    exc_info=True
)
```

### Async Patterns

```python
# DB operations are async
async def get_dataset(dataset_id: int) -> Dataset:
    async with AsyncSession() as session:
        result = await session.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        return result.scalar_one_or_none()

# Use dependency injection for services
from fastapi import Depends

def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()

@router.get("/analytics")
async def analytics(service: AnalyticsService = Depends(get_analytics_service)):
    return await service.get_analytics()
```

---

## 🚀 Development Workflow

### Daily Workflow

```bash
# 1. Start development server
cd backend
source .venv/bin/activate
make dev                     # Auto-restart on file changes

# 2. Make changes to code

# 3. Run quality checks
make check                   # Lint + typecheck + security
make test                    # Run tests

# 4. Start Temporal (if using workflows)
make temporal-up             # Start Temporal server
make temporal-ingestion-worker  # Start workers in separate terminal
```

### Available Commands (Makefile)

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make lint` | Run Ruff linter |
| `make format` | Format code with Ruff |
| `make typecheck` | Run mypy type checker |
| `make security` | Run Bandit security scanner |
| `make test` | Run pytest tests |
| `make test-cov` | Run tests with coverage |
| `make check` | Run all quality checks |
| `make dev` | Start dev server (kills port, auto-restart) |
| `make clean-dev` | Clean logs, cache, storage |
| `make reset-dev` | Reset database + clean |
| `make temporal-up` | Start Temporal server |
| `make temporal-workers` | Start all Temporal workers |

### Workflows (in `.agent/workflows/`)

Use predefined workflows for common tasks:
- `/check_backend` - Full quality checks
- `/start_servers` - Start backend + frontend
- `/db_migrate` - Run database migrations
- `/debug_api` - Debug API endpoints
- `/test_coverage` - Run tests with coverage

---

## 📚 Key Documentation

### Must-Read Docs

1. **[README.md](file:///Users/namanagarwal/system/backend/README.md)** - Project overview, quick start
2. **[ARCHITECTURE.md](file:///Users/namanagarwal/system/backend/ARCHITECTURE.md)** - Layer separation
3. **[AGENT_HANDOFF.md](file:///Users/namanagarwal/system/backend/AGENT_HANDOFF.md)** - Current refactoring status
4. **[docs/README.md](file:///Users/namanagarwal/system/backend/docs/README.md)** - Comprehensive documentation index

### Documentation by Topic

| Topic | Document |
|-------|----------|
| **Architecture** | [docs/README.md](file:///Users/namanagarwal/system/backend/docs/README.md) |
| **Features** | [docs/01-features/README.md](file:///Users/namanagarwal/system/backend/docs/01-features/README.md) |
| **Layers** | [docs/02-layers/README.md](file:///Users/namanagarwal/system/backend/docs/02-layers/README.md) |
| **Error Handling** | [docs/03-cross-cutting/](file:///Users/namanagarwal/system/backend/docs/03-cross-cutting/) |
| **API Reference** | http://localhost:8001/docs (Swagger UI) |

---

## 🐛 Debugging & Troubleshooting

### Common Issues

**Issue**: Import errors like `ModuleNotFoundError: No module named 'src'`
- **Fix**: Ensure you're in virtual environment: `source .venv/bin/activate`
- **Fix**: Install in editable mode: `pip install -e ".[dev]"`

**Issue**: Database migration conflicts
- **Fix**: Check migration history: `alembic history`
- **Fix**: Merge migrations: `alembic merge -m "merge heads" <rev1> <rev2>`

**Issue**: Port 8001 already in use
- **Fix**: Use `make dev` (auto-kills port) or `lsof -ti:8001 | xargs kill -9`

**Issue**: Temporal workflow failures
- **Fix**: Check Temporal UI: http://localhost:8088
- **Fix**: Check worker logs: `make temporal-logs`

### Dev Console

Access at http://localhost:8001/dev/console
- Real-time logs
- API request tracing
- System metrics

---

## 🎓 Learning Path

### Week 1: Foundations
1. Read [README.md](file:///Users/namanagarwal/system/backend/README.md)
2. Understand [ARCHITECTURE.md](file:///Users/namanagarwal/system/backend/ARCHITECTURE.md)
3. Run `make dev` and explore Swagger UI
4. Read a feature router (e.g., `src/features/process_mining/analytics/router.py`)

### Week 2: Deep Dive
1. Study Platform layer (`src/platform/`)
2. Study Feature layer (`src/features/process_mining/`)
3. Understand Temporal workflows (`src/platform/temporal/`)
4. Write a simple test

### Week 3: Contribute
1. Pick a small feature or bug fix
2. Follow development workflow
3. Run quality checks: `make check`
4. Submit changes

---

## 📊 Key Metrics & Stats

- **Code Quality**: Ruff + mypy + Bandit
- **Test Coverage**: Target 30%+ (check with `make test-cov`)
- **Import Linter**: 4 contracts enforced
- **API Endpoints**: 80+ endpoints across 19 routers
- **Database Tables**: 23 tables (multi-tenant architecture)

---

## 🔗 Related Resources

- **Frontend AI Agent Guide**: [`../frontend-new/AI_AGENT_GUIDE.md`](file:///Users/namanagarwal/system/frontend-new/AI_AGENT_GUIDE.md)
- **System Overview**: [`../SYSTEM_OVERVIEW.md`](file:///Users/namanagarwal/system/SYSTEM_OVERVIEW.md)
- **API Documentation**: http://localhost:8001/docs
- **Temporal UI**: http://localhost:8088

---

**Ready to contribute?** Start with a simple task like adding a new endpoint or fixing a small bug. Use `make check` and `make test` to ensure quality! 🚀
