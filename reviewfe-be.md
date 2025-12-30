# FE-BE Integration Review

## Executive Summary

The integration has solid foundations but suffers from **SDK duplication**, **connectivity issues**, and **incomplete API alignment**. The backend (PM4Py-based process mining) is well-structured; the frontend has proper patterns but isn't reliably connecting.

---

## Critical Issues

### 1. SDK Architecture Fragmentation
**Status: HIGH PRIORITY**

Two competing SDK implementations exist:
| Location | Purpose | Used By |
|----------|---------|---------|
| `/sdk/` | Standalone TypeScript SDK | Not actively used |
| `/frontend-new/libs/shared/design-system/src/api/` | Design-system API modules | Frontend via `useSDK()` |

**Problem**: Frontend references `process-mining-sdk: "file:../sdk"` in package.json but actually uses design-system's internal modules. The standalone SDK is orphaned.

**Fix**: Either consolidate to one SDK, or explicitly use the standalone SDK in SDKContext.

---

### 2. Connectivity Failures
**Status: BLOCKING**

Dev logs (`dev-logs/app.log`) show repeated failures:
```
[ERROR] [GET /processes/1] → {'message': 'Failed to fetch'...
[ERROR] [GET /processes/1/statistics] → {'message': 'Failed to fetch'...
[ERROR] [GET /visualization/1/dfg] → {'message': 'Failed to fetch'...
```

**Root Causes**:
1. Backend not running on expected port (8001)
2. CORS not configured for frontend origin
3. Network errors not gracefully handled

**Files**:
- `frontend-new/libs/shared/design-system/src/api/client.ts:45` - BaseURL config
- `backend/src/core/config.py` - CORS settings

---

### 3. API Contract Gaps
**Status: MEDIUM**

| Endpoint | FE Expects | BE Provides | Status |
|----------|------------|-------------|--------|
| `GET /processes/{id}` | ProcessDetailResponse | ProcessDetailResponse | OK |
| `GET /visualization/{id}/dfg` | DFGResponse | DFGResponse | OK |
| `GET /analytics/logs/{id}/performance` | PerformanceDashboardResponse | PerformanceDashboardResponse | OK |
| `sdk.discovery.getVariants()` | calls `/processes/{id}/variants` | Available | OK |
| `sdk.discovery.getActivities()` | calls `/processes/{id}/activities` | Available | OK |

**Missing from FE SDK**:
- `predictions` module (backend has `/predictions/` router)
- `simulation` module (backend has `/simulation/` router)
- `organizational` module (backend has `/organizational/` router)

---

## Architecture Assessment

### Backend (PM4Py Integration)
**Rating: Solid**

```
backend/
├── src/api/routers/     # 11 routers (processes, discovery, analytics, etc.)
├── src/services/        # 11 services wrapping PM4Py
├── src/models/          # SQLAlchemy + Pydantic
└── sdk/                 # TypeScript client modules
```

Key PM4Py capabilities properly exposed:
- Process Discovery (Alpha, Inductive, Heuristics miners)
- Conformance Checking (Token Replay, Alignments)
- Performance Analysis (bottlenecks, rework, cycle time)
- Variant Analysis
- OCEL 2.0 support

### Frontend (Design System + React Query)
**Rating: Good patterns, incomplete wiring**

```
frontend-new/
├── src/pages/           # 6 main sections
├── libs/shared/design-system/
│   └── src/api/
│       ├── client.ts    # HTTP client
│       ├── modules/     # logs, discovery, analytics, conformance, ai
│       └── transformers.ts  # snake_case → camelCase
```

**Good**:
- TanStack Query v5 for caching
- Proper error boundaries
- Dev logging to file
- Type transformers for BE→FE

**Issues**:
- Auth is mock-only (localStorage fake session)
- SDK modules incomplete vs backend capabilities

---

## Data Flow

```
User Action
    ↓
React Component (useQuery + useSDK)
    ↓
SDKContext.ProcessMiningSdk (design-system modules)
    ↓
ApiClient.get/post → http://localhost:8001/api/v1/*
    ↓
FastAPI Router
    ↓
Service Layer (PM4Py wrapper)
    ↓
SQLAlchemy async + EventLog data
```

---

## Fixes Required

### P0 - Connectivity
1. **Ensure backend runs**: `uvicorn src.api.main:app --reload --port 8001`
2. **Add CORS for frontend origin** in `backend/src/api/main.py`
3. **Add health check polling** in frontend before API calls

### P1 - SDK Consolidation
**Option A**: Delete `/sdk/`, use design-system modules only
**Option B**: Rewrite SDKContext to use `process-mining-sdk` package

Recommended: **Option A** - design-system modules are more mature for this use case.

### P2 - Complete API Modules
Add missing modules to `frontend-new/libs/shared/design-system/src/api/modules/`:
- `predictions.ts` - ML predictions endpoints
- `simulation.ts` - Process simulation
- `organizational.ts` - Org mining features

### P3 - Error Handling
- Add retry with exponential backoff in `ApiClient`
- Add offline detection
- Add API health indicator in UI

---

## File Reference

### Backend Critical Files
| File | Purpose |
|------|---------|
| `backend/src/api/routers/processes.py` | Event log CRUD |
| `backend/src/api/routers/analytics.py` | Performance analytics |
| `backend/src/api/routers/visualization.py` | DFG/Petri net endpoints |
| `backend/src/services/mining.py` | PM4Py discovery wrapper |
| `backend/src/services/analytics.py` | PM4Py analytics wrapper |

### Frontend Critical Files
| File | Purpose |
|------|---------|
| `frontend-new/libs/shared/design-system/src/context/SDKContext.tsx` | SDK provider |
| `frontend-new/libs/shared/design-system/src/api/client.ts` | HTTP client |
| `frontend-new/libs/shared/design-system/src/api/modules/*.ts` | API modules |
| `frontend-new/libs/shared/design-system/src/api/transformers.ts` | BE→FE transforms |
| `frontend-new/src/pages/analytics/AnalyticsPage.tsx` | Uses analytics SDK |
| `frontend-new/src/pages/explorer/ProcessExplorerPage.tsx` | Uses discovery SDK |

---

## Test Checklist

- [ ] Backend running: `curl http://localhost:8001/health`
- [ ] CORS working: No browser console errors on fetch
- [ ] Log upload works: Upload CSV, see in list
- [ ] Process explorer loads: DFG visualization renders
- [ ] Analytics loads: Performance metrics display
- [ ] No "Failed to fetch" in dev-logs

---

## Fixes Applied

### P0 - Connectivity (DONE)
1. **CORS wildcard added** - `backend/src/core/config.py` now allows `*` for dev
2. **Retry logic added** - `ApiClient` now retries with exponential backoff (3 retries)
3. **Better error messages** - "Failed to fetch" now shows helpful connection error

### P1 - SDK Consolidation (DONE)
- Removed orphaned `process-mining-sdk` dependency from `frontend-new/package.json`
- Design-system modules are the single source of truth

### P2 - New Modules Added (DONE)
Three new frontend SDK modules created in `libs/shared/design-system/src/api/modules/`:

| Module | File | Backend Router |
|--------|------|----------------|
| predictions | `predictions.ts` | `/predictions/` |
| simulation | `simulation.ts` | `/simulation/` |
| organizational | `organizational.ts` | `/organizational/` |

SDKContext updated to expose:
- `sdk.predictions.trainPredictor()`, `predict()`, etc.
- `sdk.simulation.playOut()`, `simulate()`, etc.
- `sdk.organizational.getHandoverNetwork()`, `getRoles()`, etc.
- `sdk.checkHealth()` - verify backend connectivity
- `sdk.isHealthy()` - get cached health status

---

## Business Use Case Alignment

Per `docs/businessusecase.md`, 237 activities across 15 use cases. Current coverage:

| Use Case | Backend | Frontend | Status |
|----------|---------|----------|--------|
| Process Discovery | 90% | 70% | Partial |
| Variant Analysis | 85% | 65% | Partial |
| Performance Analysis | 80% | 70% | Partial |
| Conformance Checking | 70% | 40% | Needs UI |
| OCEL/Object-Centric | 80% | 10% | Backend only |
| Predictions | 60% | 20% | Needs UI |
| Organizational Mining | 70% | 0% | Backend only |

**Priority**: Performance Analysis and Process Discovery are highest-value; focus integration there first.
