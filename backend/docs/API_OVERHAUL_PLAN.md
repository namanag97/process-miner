# Backend API Overhaul Plan

## Goal
Overhaul backend API to fully support frontend and leverage PM4Py capabilities.

---

# API Overhaul Handoff

**Last Updated:** 2025-12-30
**Last Completed:** Phase 1 (Process Explorer APIs)

---

## Current Status

| Phase | Task | Status |
|-------|------|--------|
| 1.1 | Performance DFG | ✅ DONE |
| 1.2 | Variant Complexity | ✅ DONE |
| 1.3 | Activities Endpoint | ✅ DONE |
| 1.4 | Explorer Data Endpoint | ✅ DONE |
| 2.1 | OCEL Blob Storage | TODO |
| 2.2 | Real OC-DFG | TODO |
| 3.1 | Alignment Diagnostics | TODO |
| 4.1 | Enhanced Bottlenecks | TODO |
| 4.2 | Rework Chains | TODO |
| 5.x | PM4Py Extras | TODO |

---

## Quick Start for New Session

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Check current task status
cat docs/API_OVERHAUL_PLAN.md | grep "Status:"

# 3. Find next TODO task (Phase 2.1) and implement

# 4. After changes, verify
make check
```

---

## Next Task: Phase 2.1 - OCEL Blob Storage

**Priority:** HIGH

**What to do:**
1. Add `ocel_data: Mapped[Optional[bytes]]` column to `OCELLog` in `src/models/orm.py`
2. Update `src/services/ocpm.py` to store/retrieve OCEL blob
3. Create Alembic migration: `alembic revision --autogenerate -m "Add ocel_data blob"`
4. Run migration: `alembic upgrade head`

---

## Phase 1 Implementation Summary (Completed)

### New Endpoints Created:
- `GET /visualization/{log_id}/dfg?include_performance=true` - DFG with timing metrics
- `GET /processes/{id}/variants?include_complexity=true&top_k_percent=80` - Variants with complexity
- `GET /processes/{id}/activities` - Activity statistics
- `GET /visualization/{log_id}/explorer-data` - Unified explorer data

### New Schemas Added:
- `ActivityDetailResponse` - Activity stats with frequency, timing, position
- `ProcessExplorerDataResponse` - Combined DFG + variants + activities + statistics

### New Service Methods:
- `mining_service.get_dfg_data_with_performance()` - Performance DFG via PM4Py
- `mining_service.get_activity_statistics()` - Activity-level metrics
- `mining_service.calculate_variant_complexity()` - Complexity scoring

### Key Files Modified:
- `src/models/schemas.py` - New response schemas
- `src/services/mining.py` - New analysis methods
- `src/api/routers/visualization.py` - DFG + explorer-data endpoints
- `src/api/routers/processes.py` - Variants + activities endpoints

---

## Implementation Order (Remaining)

1. **Phase 2.1** - OCEL blob storage (requires migration)
2. **Phase 2.2** - Real OC-DFG endpoint
3. **Phase 3.1** - Conformance alignment diagnostics
4. **Phase 4.1** - Enhanced bottlenecks
5. **Phase 4.2** - Rework chains
6. **Phase 5.x** - PM4Py extras (temporal, skeleton, batches)

---

## Key Files Reference

| Purpose | Path |
|---------|------|
| Schemas | `src/models/schemas.py` |
| ORM | `src/models/orm.py` |
| Mining Service | `src/services/mining.py` |
| OCPM Service | `src/services/ocpm.py` |
| Analytics Service | `src/services/analytics.py` |
| Conformance Service | `src/services/conformance.py` |
| Visualization Router | `src/api/routers/visualization.py` |
| Processes Router | `src/api/routers/processes.py` |
| OCPM Router | `src/api/routers/ocpm.py` |
| Analytics Router | `src/api/routers/analytics.py` |

---

## After Each Task

1. Update status in this file: `**Status:** DONE`
2. Run `make check`

---

## After ALL Tasks Complete

```bash
# Lint & type check
make check

# Tests
make test

# SDK regeneration (once at end)
cd sdk && npm run generate && npm run build
```

---

## PM4Py Functions Reference

| Need | PM4Py Function |
|------|----------------|
| Performance DFG | `pm4py.discover_performance_dfg()` |
| Alignments | `pm4py.conformance_diagnostics_alignments()` |
| OC-DFG | `pm4py.ocel_discover_ocdfg()` |
| Log Skeleton | `pm4py.discover_log_skeleton()` |
| Batches | `pm4py.discover_batches()` |
| Temporal | `pm4py.get_all_case_durations()` |

---

## Frontend Reference

- Frontend QA: `/Users/namanagarwal/system/frontend/files/review1.md`
- PM4Py API Schema: `/Users/namanagarwal/system/demo/pm4py-api-schema.json`

---

## Phase 1: Process Explorer APIs [HIGH] ✅ COMPLETE

### 1.1 Performance DFG
**Status:** DONE

**Files:** `schemas.py`, `mining.py`, `visualization.py`

Update `DFGEdge`:
```python
avg_duration_seconds: Optional[float] = None
min_duration_seconds: Optional[float] = None
max_duration_seconds: Optional[float] = None
```

Add to `mining.py`:
```python
def get_dfg_data_with_performance(self, event_log: EventLog) -> dict:
    pm4py_log = self._to_pm4py_log(event_log)
    perf_dfg = pm4py.discover_performance_dfg(pm4py_log)
    # Returns {(src, tgt): {'mean': ..., 'min': ..., 'max': ...}}
```

Endpoint: `GET /visualization/{log_id}/dfg?include_performance=true`

---

### 1.2 Variant Complexity
**Status:** DONE

**Files:** `schemas.py`, `mining.py`, `processes.py`

Update `VariantResponse`:
```python
complexity_score: float = 0.0
rework_count: int = 0
unique_activity_count: int = 0
```

Endpoint params: `top_k_percent`, `complexity_mode`

---

### 1.3 Activities Endpoint
**Status:** DONE

**Files:** `schemas.py`, `mining.py`, `processes.py`

New `ActivityDetailResponse`:
```python
activity: str
frequency: int
frequency_percent: float
avg_duration_seconds: Optional[float]
is_start_activity: bool
is_end_activity: bool
position_avg: float
```

New endpoint: `GET /processes/{id}/activities`

---

### 1.4 Unified Explorer Data
**Status:** DONE

**Files:** `schemas.py`, `visualization.py`

New `ProcessExplorerDataResponse`:
```python
log_id: str
dfg: DFGResponse
variants: list[VariantResponse]
activities: list[ActivityDetailResponse]
statistics: StatisticsResponse
```

New endpoint: `GET /visualization/{log_id}/explorer-data`

---

## Phase 2: OCPM Enhancement [HIGH]

### 2.1 Store OCEL Blob
**Status:** TODO

**Files:** `orm.py`, `ocpm.py` (service + router)

Add to `OCELLog`:
```python
ocel_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
```

**Requires migration**

---

### 2.2 Real OC-DFG Endpoint
**Status:** TODO

**Files:** `schemas.py`, `ocpm.py` (service + router)

Update `OCDFGResponse` with proper nodes/edges per object type.

New endpoint: `GET /ocpm/logs/{log_id}/oc-dfg`

---

## Phase 3: Conformance Enhancement [MEDIUM]

### 3.1 Alignment Diagnostics
**Status:** TODO

**Files:** `schemas.py`, `conformance.py` (service)

New schemas:
```python
class AlignmentMove(BaseModel):
    log_move: Optional[str]
    model_move: Optional[str]
    move_type: str  # 'sync', 'log_only', 'model_only'

class CaseDeviationResponse(BaseModel):
    case_id: str
    fitness: float
    alignment: list[AlignmentMove]
```

Use `pm4py.conformance_diagnostics_alignments()`

---

## Phase 4: Analytics Enhancement [MEDIUM]

### 4.1 Enhanced Bottlenecks
**Status:** TODO

**Files:** `schemas.py`, `analytics.py` (service)

Add to `BottleneckResponse`:
```python
preceding_activities: list[str]
following_activities: list[str]
bottleneck_impact_score: float
```

---

### 4.2 Rework Chains
**Status:** TODO

**Files:** `schemas.py`, `analytics.py` (service + router)

New schema and endpoint: `GET /analytics/logs/{id}/rework-chains`

---

## Phase 5: PM4Py Extras [LOW]

| Task | Endpoint | PM4Py Function |
|------|----------|----------------|
| 5.1 Temporal Stats | `GET /processes/{id}/temporal-stats` | `get_all_case_durations()` |
| 5.2 Log Skeleton | `GET /processes/{id}/skeleton` | `discover_log_skeleton()` |
| 5.3 Batch Detection | `GET /processes/{id}/batches` | `discover_batches()` |

---

## Files Summary

| File | Changes |
|------|---------|
| `src/models/schemas.py` | DFGEdge, VariantResponse, ActivityDetailResponse, ProcessExplorerDataResponse, OCDFGResponse, AlignmentMove, CaseDeviationResponse, ReworkChainResponse |
| `src/models/orm.py` | Add `ocel_data` to OCELLog |
| `src/services/mining.py` | `get_dfg_data_with_performance()`, `get_activity_statistics()`, `calculate_variant_complexity()` |
| `src/services/ocpm.py` | `get_ocel_from_db()`, real OC-DFG |
| `src/services/analytics.py` | `detect_rework_chains()`, enhanced bottlenecks |
| `src/services/conformance.py` | `get_alignment_diagnostics()` |
| `src/api/routers/visualization.py` | `include_performance`, `/explorer-data` |
| `src/api/routers/processes.py` | Variant params, `/activities` |
| `src/api/routers/ocpm.py` | Store blob, `/oc-dfg` |
| `src/api/routers/analytics.py` | `/rework-chains` |
