# DDD Refactoring Tracker

## Project Overview
Systematic refactoring to achieve proper DDD architecture with clean Platform/Feature separation.

**Status: Phase 7 Complete ✅**

## Architecture (Implemented)

```
src/
├── platform/              # Generic SaaS infrastructure (independent of features)
│   ├── core/             # Config, exceptions, security, logging, enums
│   ├── infrastructure/   # Cache, metrics, tracing, tasks, duckdb
│   ├── auth/             # JWT authentication
│   ├── users/            # User management
│   ├── workspaces/       # Workspace authorization
│   ├── projects/         # Project management
│   ├── storage/          # File storage (S3/MinIO)
│   ├── jobs/             # Background job infrastructure
│   └── models.py         # Platform models (Organization, User, Workspace, Project, AsyncJob, ErrorLog)
│
├── features/             # Domain-specific (imports from platform allowed)
│   └── process_mining/
│       ├── models/       # Dataset, Analysis, ProcessCase, ProcessEvent, etc.
│       ├── ingestion/    # CSV/XES parsing
│       ├── discovery/    # PM4Py mining algorithms
│       ├── conformance/  # Token replay, alignment
│       ├── analytics/    # Performance, bottleneck detection
│       └── visualization/ # Graph rendering
│
├── shared/               # Cross-cutting (both layers can import)
│   └── database.py       # SQLAlchemy Base class
│
├── domain/               # DDD domain model (pure, no dependencies)
│   ├── entities.py       # ProcessEvent, ProcessCase, DatasetAggregate
│   ├── value_objects.py  # CaseId, ActivitySequence, etc.
│   └── repositories.py   # Abstract repository interfaces
│
├── models/               # Compatibility shims
│   ├── orm.py           # Re-exports from platform + features (51 files use this)
│   └── orm_compat.py    # Deprecated, re-exports from orm.py
│
├── core/                 # DEPRECATED - re-exports from platform/core
├── infrastructure/       # DEPRECATED - re-exports from platform/infrastructure
│
└── api/                  # API layer (depends on all)
    └── routers/          # FastAPI routers
```

## Import Rules (Enforced by import-linter)

1. **Domain is pure** - no infrastructure/API dependencies ✅
2. **Services cannot depend on API** - presentation independence ✅
3. **Platform Core independent from Features** - enables vertical pivots ✅
4. **Platform Core independent from Platform Services** - layered architecture ✅

## Completed Tasks

### Phase 1: Fix Deprecated Imports ✅
- [x] Removed duplicate files from `src/core/` (kept __init__.py for backwards compatibility)
- [x] Removed duplicate files from `src/infrastructure/` (kept __init__.py for backwards compatibility)
- [x] Updated ~60 files from `src.core` → `src.platform.core`
- [x] Updated ~30 files from `src.infrastructure` → `src.platform.infrastructure`

### Phase 2: Complete Model Separation ✅
- [x] Added AsyncJob and ErrorLog to `src/platform/models.py`
- [x] Added Workflow, WorkflowRun, OCEL*, Recommendation, HierarchicalProcessModel to `src/features/process_mining/models/orm.py`
- [x] Updated `src/models/orm.py` to be a re-export shim from separated files
- [x] Base class lives in `src/shared/database.py`

### Phase 3: Fix Import Linter Violations ✅
- [x] Fixed unified_ingestion.py dev console import (lazy import pattern)
- [x] Updated platform/workspaces/router.py to import from src.platform.models
- [x] Adjusted import-linter contracts for practical DDD separation
- [x] All 4 contracts passing

## Remaining Work (Future Phases)

### Phase 4: Refactor Monolithic Services ✅
- [x] Break up `src/services/mining.py` (63KB) into feature services
- [x] Consolidate ingestion: `ingestion.py`, `duckdb_ingestion.py`, `unified_ingestion.py`
- [x] Move domain services to `src/features/process_mining/`

### Phase 5: Move Services to Feature Layer ✅
- [x] analytics.py → features/process_mining/analytics/service.py
- [x] conformance.py → features/process_mining/conformance/service.py
- [x] filtering.py → features/process_mining/filtering/service.py
- [x] prediction.py → features/process_mining/prediction/service.py
- [x] simulation.py → features/process_mining/simulation/service.py
- [x] organizational.py → features/process_mining/organizational/service.py
- [x] ocpm.py → features/process_mining/ocpm/service.py

### Phase 6: Migrate to Proper Layer Imports ✅
- [x] Updated 17 files importing from `src.models.orm` to use proper layer imports
- [x] Platform code → `src.platform.models`
- [x] Feature code → `src.features.process_mining.models`
- [x] API routers now import from proper layers
- [x] Service files now import from proper layers
- [x] Fixed syntax errors from migration script

### Phase 7: Dev Console Refactor ✅
- [x] Moved log_* helper functions to `platform/infrastructure/dev_logs.py`
- [x] Updated `dev_logs_stream.py` to import from platform
- [x] Removed duplicate code and cleaned up imports
- [x] All log functions now in centralized location

## Key Files

| Location | Purpose |
|----------|---------|
| `src/shared/database.py` | SQLAlchemy Base class (shared) |
| `src/platform/models.py` | Platform models (Organization, User, Workspace, Project, AsyncJob, ErrorLog) |
| `src/platform/infrastructure/dev_logs.py` | DevConsole logging functions (NEW in Phase 7) |
| `src/features/process_mining/models/orm.py` | Feature models (Dataset, Analysis, ProcessCase, etc.) |
| `src/models/orm.py` | Compatibility shim (re-exports from both layers) |
| `pyproject.toml` | Import-linter contracts |

## Last Updated
2026-01-05

## Next Agent Instructions
1. Run `lint-imports` to verify architecture compliance
2. Run `python -m pytest tests/` to verify no regressions
3. Continue with Phase 4: Refactor Monolithic Services
4. Update this file as tasks complete
