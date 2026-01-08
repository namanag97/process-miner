# Backend Infrastructure CLAUDE.md

## Overview

Infrastructure layer containing all external integrations, persistence, and platform services. This layer provides the technical capabilities that features and application layers depend on.

## Directory Structure

```
infra/
├── models.py            # Shared SQLAlchemy models (User, Org, Workspace, Project)
├── schemas.py           # Shared Pydantic schemas
│
├── core/                # Core infrastructure
│   ├── config.py        # Settings and environment loading
│   ├── exceptions.py    # AppException, ErrorCode
│   ├── logging_config.py # Structlog configuration
│   ├── middleware.py    # Request/performance logging
│   ├── security.py      # Password hashing, JWT utilities
│   ├── rate_limit.py    # SlowAPI rate limiting
│   └── api_logging.py   # API request/response logging
│
├── infrastructure/      # External integrations
│   ├── database.py      # SQLAlchemy async sessions
│   ├── object_storage.py # S3/MinIO/local storage
│   └── cache.py         # Redis/in-memory caching
│
├── auth/                # JWT authentication
│   └── jwt.py           # Token generation/validation
│
├── users/               # User management
│   ├── api/             # Auth, org, workspace, project routers
│   │   ├── auth.py      # Login, logout, refresh
│   │   ├── organizations.py
│   │   ├── workspaces.py
│   │   └── projects.py
│   ├── schemas/         # User-related schemas
│   └── services/        # User services
│
├── organizations/       # Organization management
├── workspaces/          # Workspace RBAC
├── projects/            # Project management
│
├── temporal/            # Temporal workflow orchestration
│   ├── workflows/       # Workflow definitions
│   ├── activities/      # Activity implementations
│   ├── activities_v2/   # V2 activities
│   ├── workflows_v2/    # V2 workflows
│   ├── workers/         # Temporal workers
│   └── compat.py        # Compatibility layer
│
├── jobs/                # Background job tracking
│   └── router.py        # Job status endpoints
│
├── health/              # Health check endpoints
│   └── router.py        # /health/live, /health/ready
│
├── audit/               # Audit logging
│   └── router.py        # Audit log endpoints
│
├── devconsole/          # Developer tools
│   ├── broker.py        # Log message broker
│   └── streaming.py     # SSE log streaming
│
├── devtools/            # Development utilities
│   ├── router.py        # Dev log endpoints
│   └── dev_data.py      # MVP data seeding
│
├── dag/                 # DAG workflow (deprecated, use Temporal)
├── storage/             # Storage utilities
├── system/              # System utilities
└── workflows/           # Workflow definitions
```

## Key Modules

### core/
Core infrastructure services:

**config.py** - Application settings
```python
from src.infra.core.config import get_settings
settings = get_settings()
print(settings.database_url)
```

**exceptions.py** - RFC 7807 error responses
```python
from src.infra.core.exceptions import AppException, ErrorCode

raise AppException(
    message="Resource not found",
    error_code=ErrorCode.RESOURCE_NOT_FOUND,
    status_code=404
)
```

**logging_config.py** - Structlog JSON logging
```python
from src.infra.core.logging_config import get_logger
logger = get_logger(__name__)
logger.info("operation_completed", user_id=user_id)
```

### infrastructure/
External service integrations:

**database.py** - Async SQLAlchemy sessions
```python
from src.infra.infrastructure.database import get_db_session, write_session_maker

# In route handler
@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db_session)):
    ...

# In service
async with write_session_maker() as db:
    db.add(item)
    await db.commit()
```

### temporal/
Workflow orchestration:

**workflows/** - Temporal workflow definitions
**activities/** - Individual activity implementations

```python
from temporalio import workflow, activity

@workflow.defn
class DatasetIngestionWorkflow:
    @workflow.run
    async def run(self, dataset_id: str) -> str:
        await workflow.execute_activity(
            parse_csv_activity,
            args=[dataset_id],
            start_to_close_timeout=timedelta(minutes=10),
        )
        return "completed"
```

### users/api/
Multi-tenant authentication and management:

- `auth.py` - Login, logout, token refresh
- `organizations.py` - Organization CRUD
- `workspaces.py` - Workspace management + RBAC
- `projects.py` - Project management

## Import Rules

**This layer should NOT import from:**
- `features/` - Process mining features
- `api/` - API layer

**Can import from:**
- `shared/` - Shared utilities

## Key Patterns

### Database Session Dependency
```python
from src.infra.infrastructure.database import get_db_session

@router.get("/resource/{id}")
async def get_resource(
    id: str,
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(select(Resource).where(Resource.id == id))
    return result.scalar_one_or_none()
```

### Authentication Dependency
```python
from src.infra.auth import get_current_user

@router.get("/protected")
async def protected_endpoint(user: User = Depends(get_current_user)):
    return {"user_id": user.id}
```

### Structured Logging
```python
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)

logger.info("request_processed",
    user_id=user_id,
    action="create_dataset",
    duration_ms=duration
)
```
