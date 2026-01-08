# Backend Source Code CLAUDE.md

## Overview

Main source code directory following a layered architecture with feature modules for process mining.

## Directory Structure

```
src/
├── api/                      # API Layer - FastAPI application
│   ├── main.py              # App factory, middleware, exception handlers
│   └── routers/             # Router imports and __all__ exports
│       ├── __init__.py      # Central router registry
│       ├── operations.py    # Temporal operation status (SSE)
│       └── workflows.py     # Workflow database records
│
├── application/              # CQRS Application Layer
│   ├── commands/            # Command handlers (write operations)
│   ├── queries/             # Query handlers (read operations)
│   ├── projections/         # Read model projections
│   └── bootstrap.py         # CQRS initialization
│
├── features/                 # Feature Modules Layer
│   └── process_mining/      # Core PM feature
│       ├── models/          # SQLAlchemy models (Dataset, DatasetColumn, etc.)
│       ├── schemas/         # Pydantic schemas for all features
│       ├── datasets/        # Dataset management
│       │   └── api/         # Upload, mapping, ingest, CRUD routers
│       ├── ingestion/       # DuckDB-based ingestion services
│       ├── discovery/       # Process discovery (Alpha, Inductive, Heuristics)
│       ├── conformance/     # Conformance checking (token replay, alignments)
│       ├── analytics/       # Performance analytics (bottlenecks, cycle time)
│       ├── visualization/   # DFG, Petri net graph generation
│       ├── predictions/     # ML predictions (next activity, remaining time)
│       ├── organizational/  # Organizational mining (SNA, handovers)
│       ├── simulation/      # What-if analysis
│       ├── filtering/       # Event log filtering
│       ├── ocpm/            # Object-Centric PM (OCEL 2.0)
│       ├── statistics/      # Dataset statistics endpoints
│       ├── ai/              # AI chat assistant
│       ├── analyses/        # Stored analysis results
│       ├── workflows/       # Workflow automation
│       └── business_use_cases/ # P2P, O2C templates
│
├── infra/                    # Infrastructure Layer
│   ├── core/                # Core infrastructure
│   │   ├── config.py        # Settings and environment
│   │   ├── exceptions.py    # AppException, ErrorCode
│   │   ├── logging_config.py # Structlog configuration
│   │   ├── middleware.py    # Request/performance logging
│   │   ├── security.py      # Password hashing, JWT utils
│   │   └── rate_limit.py    # SlowAPI rate limiting
│   ├── infrastructure/      # External integrations
│   │   ├── database.py      # SQLAlchemy async sessions
│   │   ├── object_storage.py # S3/MinIO/local storage
│   │   └── cache.py         # Redis/in-memory caching
│   ├── auth/                # JWT authentication
│   ├── users/               # User management
│   │   ├── api/             # Auth, org, workspace, project routers
│   │   ├── schemas/         # User-related schemas
│   │   └── services/        # User services
│   ├── organizations/       # Organization management
│   ├── workspaces/          # Workspace RBAC
│   ├── projects/            # Project management
│   ├── temporal/            # Temporal workflow orchestration
│   │   ├── workflows/       # Workflow definitions
│   │   ├── activities/      # Activity implementations
│   │   └── workers/         # Temporal workers
│   ├── jobs/                # Background job tracking
│   ├── health/              # Health check endpoints
│   ├── audit/               # Audit logging
│   ├── devconsole/          # SSE log streaming
│   └── devtools/            # Development utilities
│
├── shared/                   # Shared Layer
│   ├── types/               # Common type definitions
│   ├── constants/           # Application constants
│   └── utils/               # Utility functions
│
└── data/                     # Data configuration
```

## Layer Dependencies (Enforced by import-linter)

```
┌─────────────────────────────────────────────────────┐
│  API Layer (src/api/)                               │
│  - Can import from: features, infra, shared         │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Features Layer (src/features/)                     │
│  - Can import from: infra, shared                   │
│  - Cannot import from: api                          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Infrastructure Layer (src/infra/)                  │
│  - Can import from: shared                          │
│  - Should not import from: features, api            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Shared Layer (src/shared/)                         │
│  - No internal dependencies                         │
└─────────────────────────────────────────────────────┘
```

## Key Patterns

### Feature Module Pattern

Each feature follows this structure:

```python
# router.py - FastAPI endpoints
from fastapi import APIRouter, Depends
from src.infra.infrastructure.database import get_db_session

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/datasets/{dataset_id}/bottlenecks")
async def get_bottlenecks(
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    return await AnalyticsService(db).get_bottlenecks(dataset_id)

# service.py - Business logic
class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_bottlenecks(self, dataset_id: str) -> BottleneckResponse:
        event_log = await self._load_event_log(dataset_id)
        # PM4Py algorithm execution
        return result

# schemas.py - Pydantic models
class BottleneckResponse(BaseModel):
    bottlenecks: list[Bottleneck]
    analysis_time: float
```

### Error Handling

```python
from src.infra.core.exceptions import AppException, ErrorCode

raise AppException(
    message="Dataset not found",
    error_code=ErrorCode.RESOURCE_NOT_FOUND,
    status_code=404,
    details={"dataset_id": dataset_id}
)
```

### Database Access

```python
from src.infra.infrastructure.database import get_db_session, write_session_maker

# In route handler (read operations)
@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Item))
    return result.scalars().all()

# In service (write operations)
async with write_session_maker() as db:
    db.add(new_item)
    await db.commit()
```

### Temporal Workflow Pattern

```python
from src.infra.temporal.workflows import DatasetIngestionWorkflow
from temporalio.client import Client

# Starting a workflow
client = await Client.connect("localhost:7233")
workflow_id = f"ingest-{dataset_id}"
handle = await client.start_workflow(
    DatasetIngestionWorkflow.run,
    args=[dataset_id],
    id=workflow_id,
    task_queue="process-mining-queue",
)
```

## Canonical Import Paths

**IMPORTANT**: Always use these canonical paths. Deprecated paths are blocked by import-linter.

### Models
```python
# CORRECT
from src.features.process_mining.models import Dataset, DatasetStatus

# WRONG (deleted duplicates)
# from src.features.process_mining.datasets.models import Dataset
```

### Schemas
```python
# CORRECT
from src.features.process_mining.schemas.datasets import DatasetResponse
from src.features.process_mining.schemas.analytics import BottleneckResponse
```

### Ingestion Services
```python
# CORRECT
from src.features.process_mining.ingestion import IngestionService, load_event_log

# WRONG (deprecated shims)
# from src.features.process_mining.services.ingestion import ...
```

## Import Rules Summary

1. `api/` can import from any layer
2. `features/` cannot import from `api/`
3. `infra/` should not import from `features/`
4. `shared/` is standalone - no internal dependencies

Run `make check-imports` to verify compliance.
