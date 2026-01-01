# Dependency Map — Ripple Effect Tracker

> Before modifying a file, check here to understand what might break.

---

## 🔴 CRITICAL Impact (Database/Schema)

### `backend/src/models/orm.py`

**Impact**: CRITICAL — 23+ files depend on this  
**Consumers**: All services, all routers, migrations

**If you change this**:

- [ ] Update corresponding Pydantic models in `schemas.py`
- [ ] Create Alembic migration: `alembic revision --autogenerate -m "describe_change"`
- [ ] Run full test suite: `make backend-test`
- [ ] Regenerate SDK: `cd sdk && npm run generate && npm run build`
- [ ] Update `backend/docs/DATA_CONTRACTS.md`

---

### `backend/src/models/schemas.py`

**Impact**: CRITICAL — 13 routers + SDK depend on this  
**Consumers**: All routers, TypeScript SDK, frontend

**If you change this**:

- [ ] Ensure ORM model matches (if adding fields)
- [ ] Regenerate SDK: `cd sdk && npm run generate && npm run build`
- [ ] Run: `make backend-test`
- [ ] Update `backend/docs/API_REFERENCE.md`

---

## 🟠 HIGH Impact (Core Infrastructure)

### `backend/src/core/exceptions.py`

**Impact**: HIGH — 5+ files use exception hierarchy  
**Consumers**: `main.py`, `processes.py`, `ingestion.py`, `result.py`

**If you change this**:

- [ ] Update exception handler in `main.py` if changing base class
- [ ] Check all `raise` statements still work
- [ ] Run: `make backend-test`

---

### `backend/src/core/config.py`

**Impact**: HIGH — All components read config  
**Consumers**: Database, logging, all services

**If you change this**:

- [ ] Update `.env.example` with new variables
- [ ] Document in `backend/README.md`
- [ ] Test with fresh `.env` file

---

### `backend/src/services/mining.py`

**Impact**: HIGH — 7 routers depend on this  
**Consumers**: discovery, visualization, analyses, processes, filtering, analytics, conformance

**If you change this**:

- [ ] Run `pytest tests/test_discovery_router.py tests/test_pm4py_integration.py -v`
- [ ] Verify PM4Py output format hasn't changed
- [ ] Check all dependent routers still receive expected data shape

---

### `backend/src/services/filtering.py`

**Impact**: HIGH — 5 routers depend on this  
**Consumers**: filtering, analytics, organizational, predictions, simulation

**If you change this**:

- [ ] Run `pytest tests/test_filtering_router.py -v`
- [ ] Verify filter functions return valid PM4Py logs

---

## 🟡 MEDIUM Impact (Feature Services)

### `backend/src/services/conformance.py`

**Consumers**: conformance router  
**If you change**: Run `pytest tests/test_conformance_router.py -v`

### `backend/src/services/analytics.py`

**Consumers**: analytics router  
**If you change**: Run `pytest tests/test_analytics_router.py -v`

### `backend/src/services/ocpm.py`

**Consumers**: ocpm router  
**If you change**: Run `pytest tests/test_ocpm_router.py -v`

---

## 🟢 LOW Impact (Isolated Components)

| File                         | Scope                      | Test Command                      |
| ---------------------------- | -------------------------- | --------------------------------- |
| `services/simulation.py`     | simulation router only     | `pytest tests/ -k simulation`     |
| `services/organizational.py` | organizational router only | `pytest tests/ -k organizational` |
| `services/prediction.py`     | predictions router only    | `pytest tests/ -k prediction`     |
| `services/workflow.py`       | workflows router only      | `pytest tests/ -k workflow`       |

---

## Frontend → Backend Dependencies

| Frontend Feature    | Backend Endpoint               | Service           |
| ------------------- | ------------------------------ | ----------------- |
| Process Explorer    | `/processes/*`, `/discovery/*` | mining, ingestion |
| Conformance View    | `/conformance/*`               | conformance       |
| Analytics Dashboard | `/analytics/*`                 | analytics         |
| OCEL Features       | `/ocpm/*`                      | ocpm              |
