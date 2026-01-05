# Agent Handoff: DDD Refactoring Continuation

## Quick Start

```bash
cd /Users/namanagarwal/system/backend
source .venv/bin/activate

# Verify current state
lint-imports                    # Should show 4 contracts kept, 0 broken
python -c "from src.models.orm import *; print('OK')"  # Should work
```

## Current State (Phase 1 Complete)

### Architecture Achieved
```
src/
├── platform/                 # ✅ SaaS infrastructure (independent)
│   ├── core/                # Config, security, logging, enums
│   ├── infrastructure/      # Tasks, cache, metrics, tracing
│   ├── models.py            # Organization, User, Workspace, Project, AsyncJob, ErrorLog
│   └── [auth, users, workspaces, projects, storage, jobs]/
│
├── features/                # ✅ Process mining domain
│   └── process_mining/
│       └── models/orm.py    # Dataset, Analysis, ProcessCase, ProcessEvent, etc.
│
├── shared/                  # ✅ Cross-cutting
│   └── database.py          # SQLAlchemy Base class
│
├── models/                  # ⚠️ Compatibility shims (51 files still use this)
│   └── orm.py               # Re-exports from platform + features
│
├── core/                    # 🗑️ DEPRECATED shim → platform/core
├── infrastructure/          # 🗑️ DEPRECATED shim → platform/infrastructure
│
├── services/                # ❌ NEEDS REFACTORING (Phase 4-5)
│   └── mining.py            # 63KB monolith!
│
└── api/routers/             # ✅ Updated imports
```

### What Was Done
1. Deleted duplicate files from `src/core/` and `src/infrastructure/`
2. Updated ~60 files: `src.core` → `src.platform.core`
3. Updated ~30 files: `src.infrastructure` → `src.platform.infrastructure`
4. Separated models into platform/features layers
5. Created `src/models/orm.py` as re-export shim
6. Fixed import linter violations

## Remaining Work (Priority Order)

### Phase 4: Refactor Mining Service (HIGH PRIORITY)
The `src/services/mining.py` is a **63KB monolith**. Break it up:

```python
# Target structure:
src/features/process_mining/
├── discovery/
│   └── service.py          # Extract from mining.py: discover(), get_dfg()
├── mining/
│   ├── alpha.py            # Alpha miner logic
│   ├── inductive.py        # Inductive miner logic
│   ├── heuristic.py        # Heuristic miner logic
│   └── service.py          # Orchestration
```

**Key methods to extract from mining.py:**
- `discover()` - main entry point (~200 lines)
- `_create_pm4py_log()` - log creation
- `_serialize_model()` / `_deserialize_model()` - joblib serialization
- Algorithm-specific code for each miner type

### Phase 5: Consolidate Ingestion (MEDIUM PRIORITY)
Three overlapping implementations exist:
- `src/services/ingestion.py` - PM4Py-based
- `src/services/duckdb_ingestion.py` - DuckDB/Arrow-based
- `src/services/unified_ingestion.py` - Facade

**Action:** Create single `src/features/process_mining/ingestion/service.py` that:
1. Routes CSV → DuckDB path (fast)
2. Routes XES → PM4Py path
3. Removes duplication

### Phase 6: Move Services to Feature Layer (MEDIUM PRIORITY)
| Current Location | Target Location |
|-----------------|-----------------|
| `src/services/analytics.py` | `src/features/process_mining/analytics/service.py` |
| `src/services/conformance.py` | `src/features/process_mining/conformance/service.py` |
| `src/services/filtering.py` | `src/features/process_mining/filtering/service.py` |
| `src/services/prediction.py` | `src/features/process_mining/prediction/service.py` |
| `src/services/simulation.py` | `src/features/process_mining/simulation/service.py` |
| `src/services/organizational.py` | `src/features/process_mining/organizational/service.py` |
| `src/services/ocpm.py` | `src/features/process_mining/ocpm/service.py` |

### Phase 7: Migrate Legacy Imports (LOW PRIORITY)
51 files still import from `src.models.orm`. Gradually update:
- Platform code → `from src.platform.models import ...`
- Feature code → `from src.features.process_mining.models import ...`

## Key Files Reference

| File | Purpose | Notes |
|------|---------|-------|
| `src/shared/database.py` | SQLAlchemy Base | Both layers import this |
| `src/platform/models.py` | Platform entities | Org, User, Workspace, Project, AsyncJob, ErrorLog |
| `src/features/process_mining/models/orm.py` | Feature entities | Dataset, Analysis, ProcessCase, etc. |
| `src/models/orm.py` | Compat shim | Re-exports everything (51 consumers) |
| `src/services/mining.py` | Mining monolith | 63KB - needs breaking up |
| `pyproject.toml` | Import linter config | Lines 222-290 |
| `REFACTORING_TRACKER.md` | Progress tracker | Update as you complete tasks |

## Import Linter Contracts

```toml
# pyproject.toml contracts:
1. Domain Independence          - src.domain cannot import infra/api
2. Services Independence        - src.services cannot import src.api
3. Platform Core from Features  - src.platform.core cannot import src.features
4. Platform Core Independence   - src.platform.core cannot import platform services
```

Run `lint-imports` after changes to verify.

## Gotchas & Warnings

### 1. Circular Import Risk
Platform models reference Feature models via string type hints:
```python
# src/platform/models.py - Project class
datasets: Mapped[list["Dataset"]] = relationship(...)  # String reference!
```
Don't add direct imports - use string references or TYPE_CHECKING.

### 2. Dev Console Logging
`src/api/routers/dev_logs_stream.py` contains logging helpers used by various layers. This is a layering violation fixed with lazy imports:
```python
# Pattern used in services:
def _log_validation(...):
    try:
        from src.api.routers.dev_logs_stream import log_validation
        log_validation(...)
    except ImportError:
        pass
```
Future fix: Move log_* functions to `src/platform/infrastructure/`.

### 3. The 51 Files Problem
Many files import from `src.models.orm`:
```python
from src.models.orm import Dataset, User, ...
```
This works but isn't ideal DDD. Low priority to fix.

### 4. Tasks.py Complexity
`src/platform/infrastructure/tasks.py` is large and imports from everywhere. It needs feature models for orchestration - this is acceptable.

## Verification Commands

```bash
# Import linter (must pass)
lint-imports

# Quick import test
python -c "from src.models.orm import *; print('OK')"

# Service import test
python -c "from src.services.mining import mining_service; print('OK')"

# Run tests (if available)
python -m pytest tests/ -v

# Type check
python -m mypy src/ --ignore-missing-imports
```

## Recommended Approach

### For Mining.py Refactor:
1. Read `src/services/mining.py` to understand structure
2. Identify cohesive method groups
3. Create new files in `src/features/process_mining/discovery/`
4. Move methods one group at a time
5. Update imports in calling code
6. Run `lint-imports` after each move
7. Test thoroughly

### For Service Migration:
1. Copy service to feature location
2. Update imports to use `src.platform.core`
3. Update callers to import from new location
4. Add re-export in `src/services/__init__.py` for backwards compat
5. Run `lint-imports`

## Contact
Update `REFACTORING_TRACKER.md` with progress for next agent.
