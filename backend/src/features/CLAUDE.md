# Backend Features CLAUDE.md

## Overview
Process mining feature modules. Contains the core PM4Py-based algorithms and analytics capabilities.

## Directory Structure

```
features/
└── process_mining/
    ├── analytics/       # Performance analytics
    │   ├── router.py    # API endpoints
    │   ├── service.py   # Business logic
    │   └── schemas.py   # Request/response schemas
    ├── discovery/       # Process discovery algorithms
    ├── conformance/     # Conformance checking
    ├── predictions/     # ML-based predictions
    ├── organizational/  # Org mining (social network)
    └── schemas/         # Shared schemas
```

## Feature Pattern

Each feature follows this structure:
```python
# router.py - FastAPI endpoints
@router.post("/discover")
async def discover_model(...):
    return await service.discover(...)

# service.py - Business logic
class DiscoveryService:
    async def discover(self, dataset_id: UUID, algorithm: str):
        event_log = await load_event_log(dataset_id)
        # PM4Py algorithm execution
        return result

# schemas.py - Pydantic models
class DiscoveryRequest(BaseModel):
    dataset_id: UUID
    algorithm: Literal["alpha", "inductive", "heuristics"]
```

## PM4Py Integration

Features use PM4Py for process mining:
```python
import pm4py

# Discovery
net, im, fm = pm4py.discover_petri_net_inductive(log)

# Conformance
result = pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)

# Analytics
dfg = pm4py.discover_dfg(log)
```

## Import Rules

- Can import from `infra/` for database, storage access
- Can import from `shared/` for utilities
- Cannot import from `api/` (presentation layer)
- Cannot import from `application/` directly
