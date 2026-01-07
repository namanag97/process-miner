# Process Mining Feature CLAUDE.md

## Overview
Core process mining feature modules built on PM4Py. Contains algorithms for discovery, conformance, analytics, predictions, and organizational mining.

## Canonical Import Paths

**IMPORTANT**: Always use the canonical paths below. Deprecated paths are blocked by import-linter.

### Models (Single Source of Truth)
```python
# CORRECT - Canonical path
from src.features.process_mining.models import Dataset, DatasetStatus, UploadedFile
from src.features.process_mining.models import DatasetColumn, DatasetColumnMapping

# WRONG - Deleted duplicate (import-linter will block)
# from src.features.process_mining.datasets.models import Dataset  # DELETED
```

### Datasets API
```python
# CORRECT - Canonical path (registered with main router)
from src.features.process_mining.datasets.api import upload_router, mapping_router
from src.features.process_mining.datasets.api import crud_router, export_router

# WRONG - Deleted duplicate (import-linter will block)
# from src.features.process_mining.api.datasets import router  # DELETED
```

### Ingestion Services
```python
# CORRECT - Canonical path
from src.features.process_mining.ingestion import IngestionService, DuckDBParser
from src.features.process_mining.ingestion import UnifiedIngestionService

# WRONG - Deprecated shims (import-linter will warn)
# from src.features.process_mining.services.ingestion import ...  # SHIM
# from src.features.process_mining.datasets.services.ingestion import ...  # SHIM
```

### Schemas
```python
# CORRECT - Use specific schema modules
from src.features.process_mining.schemas.datasets import DatasetResponse
from src.features.process_mining.schemas.analytics import BottleneckAnalysis
from src.features.process_mining.schemas.discovery import DiscoveryRequest
```

## Directory Structure

```
process_mining/
├── models/              # Canonical SQLAlchemy models (Dataset, etc.)
├── schemas/             # Pydantic schemas for API
├── datasets/
│   └── api/             # Canonical datasets API routers
├── ingestion/           # Canonical ingestion services (DuckDB parser, etc.)
├── analytics/           # Performance analytics
├── discovery/           # Process discovery algorithms
├── conformance/         # Conformance checking
├── predictions/         # ML-based predictions
├── organizational/      # Social network analysis
├── simulation/          # What-if analysis
└── ocpm/                # Object-Centric Process Mining
```

## Anti-Duplication Rules

The following import-linter contracts prevent duplicate code:

1. **Contract 6**: No imports from `src.features.process_mining.api.datasets` (deleted)
2. **Contract 7**: No imports from `src.features.process_mining.datasets.models` (deleted)
3. **Contract 8**: No imports from `src.features.process_mining.services.ingestion` (shim)
4. **Contract 9**: No imports from `src.features.process_mining.datasets.services.ingestion` (shim)

Run `make check-imports` to verify compliance.

## Feature Module Pattern

Each feature follows this pattern:

```python
# router.py - FastAPI endpoints
@router.post("/discover")
async def discover_model(request: DiscoveryRequest):
    return await service.discover(request)

# service.py - Business logic
class DiscoveryService:
    async def discover(self, request: DiscoveryRequest):
        event_log = await load_event_log(request.dataset_id)
        # PM4Py algorithm execution
        return result

# schemas.py - Pydantic models
class DiscoveryRequest(BaseModel):
    dataset_id: UUID
    algorithm: Literal["alpha", "inductive", "heuristics"]
```
