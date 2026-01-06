# Process Mining SaaS — MVP Gap Analysis & Technical Roadmap

> **Author**: CTO  
> **Date**: 2026-01-06  
> **Purpose**: Reality check — Are we ready for MVP? What's missing?

---

## Executive Summary: MVP Readiness

| Pipeline Stage | Status | Confidence | Notes |
|----------------|--------|------------|-------|
| **1. File Upload** | ✅ Done | 95% | 4-phase architecture, presigned URLs |
| **2. Validation** | ✅ Done | 90% | Temporal workflow, column detection |
| **3. Column Mapping** | ✅ Done | 85% | AI suggestions, manual override |
| **4. Ingestion** | ✅ Done | 85% | DuckDB parsing, Temporal orchestration |
| **5. Discovery** | ✅ Done | 90% | 17 algorithms implemented |
| **6. Visualization** | ⚠️ Partial | 60% | Backend complete, frontend integration unclear |
| **7. End-to-End Flow** | ⚠️ Untested | 40% | Need integration test |

### ⚡ Bottom Line

**Backend is ~90% MVP-ready.** The system CAN ingest data and run discovery algorithms.

**Key Gaps:**
1. No **dataset profiling** for algorithm recommendations (the Intelligence Layer from spec)
2. **Complexity slider** not implemented (user-facing simplicity control)
3. **Frontend-to-Backend flow** needs validation
4. Missing **WebSocket progress** for long-running analyses

---

## What's Already Working ✅

### Data Ingestion Pipeline

```
Upload → Validate → Map → Ingest
           ↓
4-phase architecture with Temporal workflows
```

- **Upload endpoint**: `src/features/process_mining/api/datasets/upload.py` ✅
- **Column mapping**: `src/features/process_mining/api/datasets/mapping.py` ✅  
- **Ingest trigger**: `src/features/process_mining/api/datasets/ingest.py` ✅
- **Temporal workflow**: `src/platform/temporal/workflows/ingestion.py` ✅

### Discovery Algorithms (17 implemented)

Location: `src/features/process_mining/discovery/service.py` (761 lines)

| Algorithm | MinerType Enum | Output Format |
|-----------|----------------|---------------|
| DFG | `DFG` | DFG |
| Alpha | `ALPHA` | Petri Net |
| Alpha+ | `ALPHA_PLUS` | Petri Net |
| Heuristics | `HEURISTICS` | Petri Net |
| Inductive | `INDUCTIVE` | Process Tree |
| Inductive Infrequent | `INDUCTIVE_INFREQUENT` | Process Tree |
| ILP | `ILP` | Petri Net |
| BPMN | `BPMN_INDUCTIVE` | BPMN |
| DECLARE | `DECLARE` | Declare Model |
| Log Skeleton | `LOG_SKELETON` | Log Skeleton |
| Temporal Profile | `TEMPORAL_PROFILE` | Temporal Profile |
| POWL | `POWL` | POWL |
| Prefix Tree | `PREFIX_TREE` | Prefix Tree |
| Transition System | `TRANSITION_SYSTEM` | Transition System |
| Batches | `BATCHES` | Batches |
| Correlation | `CORRELATION` | DFG |
| Performance DFG | `PERFORMANCE_DFG` | Performance DFG |

### API Infrastructure

- **22+ routers** registered in `src/api/main.py`
- **MVP seed data** auto-created (org, workspace, user)
- **Key endpoints**: datasets, discovery, visualization, conformance, analytics

---

## What's Missing ⚠️

### 1. Dataset Profiling (Intelligence Layer)

**The spec says**: *"The system recommends, not just executes."*

**Missing table:**
```sql
dataset_profiles (
  id, dataset_id, event_count, case_count, activity_count, variant_count,
  variant_explosion FLOAT,  -- THE KEY METRIC
  has_loops BOOLEAN, has_concurrent BOOLEAN, noise_estimate ENUM
)
```

**Logic needed:**
- `variant_explosion < 0.10` → All algorithms available
- `variant_explosion 0.10-0.30` → Warn on Alpha, default to Inductive
- `variant_explosion 0.30-0.50` → Hide Alpha, default to IM-Infrequent
- `variant_explosion > 0.50` → Only DFG and IM-Infrequent

### 2. DFG Cache

**Missing table:**
```sql
dfg_cache (id, dataset_id, dfg JSONB, performance_dfg JSONB, computed_at)
```

Should be computed after ingestion for instant visualization.

### 3. Complexity Slider

**The spec says**: *"One UX element maps to algorithm-specific params"*

| Slider | Heuristic `dependency_threshold` | Inductive `noise_threshold` |
|--------|----------------------------------|------------------------------|
| Simple | 0.9 | 0.5 |
| Balanced | 0.5 | 0.2 |
| Detailed | 0.2 | 0.0 |

### 4. WebSocket Progress

**Current**: Polling via `GET /jobs/{id}`  
**Needed**: `WS /analyses/{id}/progress` → `{"progress": 0.45, "message": "..."}`

---

## Prioritized Action Plan

### Sprint 1: Core MVP (5 days)

| Task | Owner | Estimate |
|------|-------|----------|
| End-to-end test: upload → ingest → discover → viz | QA | 1d |
| Add `dataset_profiles` table | BE | 0.5d |
| Compute profile after ingestion | BE | 1d |
| Add `dfg_cache` table | BE | 0.5d |
| Cache DFG after profiling | BE | 0.5d |
| Verify frontend visualization | FE | 1d |

### Sprint 2: Intelligence Layer (3 days)

| Task | Owner | Estimate |
|------|-------|----------|
| Algorithm recommendation engine | BE | 1d |
| `GET /algorithms/recommend?dataset_id=X` endpoint | BE | 0.5d |
| Complexity slider parameter mapping | BE | 0.5d |
| Frontend algorithm selector UI | FE | 1d |

### Sprint 3: Polish (2 days)

| Task | Owner | Estimate |
|------|-------|----------|
| WebSocket progress streaming | BE | 1d |
| Error taxonomy implementation | BE | 0.5d |
| API documentation | Docs | 0.5d |

---

## Verification Checklist (Before MVP Launch)

- [ ] Can upload CSV file (< 100MB)
- [ ] Column detection works (AI suggestions)
- [ ] Column mapping saves correctly
- [ ] Ingestion completes without error
- [ ] DFG generates in < 5 seconds
- [ ] Inductive Miner produces model
- [ ] Frontend displays DFG with frequencies
- [ ] Frontend displays Petri net/Process tree
- [ ] Job progress visible to user

---

## Next Steps

1. **Today**: Run end-to-end test manually to identify breaking points
2. **This week**: Implement dataset profiling + DFG cache
3. **Next week**: Intelligence layer + frontend polish

---

*This document serves as the definitive technical roadmap for MVP launch.*
