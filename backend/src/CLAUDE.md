# Backend Source Code CLAUDE.md

## Overview
Main source code directory following hexagonal/clean architecture principles.

## Directory Structure

```
src/
├── api/                 # FastAPI routers and DTOs
│   └── main.py          # App factory, middleware, exception handlers
├── application/         # Application services, use cases, projections
├── features/            # Process mining feature modules
│   └── process_mining/  # Core PM algorithms and analytics
├── infra/               # Infrastructure layer
│   ├── database/        # SQLAlchemy models, sessions
│   ├── storage/         # S3/MinIO object storage
│   ├── temporal/        # Temporal workflow activities
│   └── devconsole/      # Developer tooling
├── shared/              # Shared utilities, types, constants
├── data/                # Data layer (raw storage paths)
└── scripts/             # Internal scripts
```

## Layer Dependencies (Enforced by import-linter)

```
API Layer → Application Layer → Infrastructure Layer
                ↓
         Features Layer (can use Infrastructure)
                ↓
         Shared Layer (used by all)
```

## Key Patterns

### Service Pattern
```python
# Services live in application/ or features/
class DatasetService:
    def __init__(self, db: AsyncSession, storage: ObjectStorage):
        self.db = db
        self.storage = storage
```

### Router Pattern
```python
# Routers in api/ or features/*/router.py
@router.get("/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    ...
```

### Error Handling
```python
from src.shared.exceptions import AppException, ErrorCode

raise AppException(
    message="Dataset not found",
    error_code=ErrorCode.RESOURCE_NOT_FOUND,
    status_code=404
)
```

## Import Rules

- `api/` can import from any layer
- `application/` cannot import from `api/`
- `features/` cannot import from `api/`
- `infra/` should not import from `features/` or `application/`
- `shared/` is standalone - no internal dependencies
