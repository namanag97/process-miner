# Backend CLAUDE.md

## Overview

FastAPI-based Python backend for the Process Mining SaaS platform. Uses PM4Py for process mining algorithms, SQLite/DuckDB for data storage, and Temporal for async workflows.

## Quick Commands

```bash
# Start dev server (port 8001)
cd backend/src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

# Run tests
.venv/bin/python -m pytest tests/ -v

# Run quality checks
make check

# Database migrations
.venv/bin/alembic upgrade head
.venv/bin/alembic revision --autogenerate -m "description"
```

## Directory Structure

```
backend/
├── src/                 # Source code (see src/CLAUDE.md)
│   ├── api/            # FastAPI app and routers
│   ├── features/       # Process mining features
│   ├── infra/          # Infrastructure layer
│   ├── application/    # CQRS application layer
│   └── shared/         # Shared utilities
├── tests/               # Pytest test suite
├── alembic/             # Database migrations
├── data/                # Local data storage
├── docs/                # Backend-specific docs
└── pyproject.toml       # Dependencies & config
```

## Key Files

- `src/api/main.py` - FastAPI app entry point
- `src/api/routers/__init__.py` - Router registry
- `pyproject.toml` - Dependencies, linting, import-linter rules
- `alembic.ini` - Migration configuration
- `Makefile` - Common development tasks

## Layer Architecture

```
API Layer (src/api/)
    ↓
Features Layer (src/features/)  ←→  Infrastructure Layer (src/infra/)
    ↓                                    ↓
                Shared Layer (src/shared/)
```

**Rules (enforced by import-linter):**
1. Features cannot import from API layer
2. Infrastructure should not import from features
3. Shared layer has no internal dependencies

## Dev Credentials

```
Email:    analyst@example.com
Password: TestPass123
```

Pre-seeded: `mvp-org-001`, `mvp-ws-001`, `mvp-proj-001`, `mvp-user-001`

## Testing

```bash
# All tests
.venv/bin/python -m pytest tests/ -v

# Single file
.venv/bin/python -m pytest tests/api/test_datasets.py -v

# With coverage
.venv/bin/python -m pytest tests/ --cov=src --cov-report=html
```

## API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI Spec: http://localhost:8001/openapi.json

## Key Patterns

### Error Handling
```python
from src.infra.core.exceptions import AppException, ErrorCode

raise AppException(
    message="Dataset not found",
    error_code=ErrorCode.RESOURCE_NOT_FOUND,
    status_code=404
)
```

### Database Access
```python
from src.infra.infrastructure.database import get_db_session

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

### Feature Module Pattern
```python
# features/process_mining/{feature}/router.py
router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/datasets/{id}/bottlenecks")
async def get_bottlenecks(id: str, db: AsyncSession = Depends(get_db_session)):
    return await AnalyticsService(db).get_bottlenecks(id)
```
