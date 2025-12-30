# API Overhaul Handoff

**Reference:** `docs/API_OVERHAUL_PLAN.md`

---

## Current Status

| Phase | Task | Status |
|-------|------|--------|
| 1.1 | Performance DFG | TODO |
| 1.2 | Variant Complexity | TODO |
| 1.3 | Activities Endpoint | TODO |
| 1.4 | Explorer Data Endpoint | TODO |
| 2.1 | OCEL Blob Storage | TODO |
| 2.2 | Real OC-DFG | TODO |
| 3.1 | Alignment Diagnostics | TODO |
| 4.1 | Enhanced Bottlenecks | TODO |
| 4.2 | Rework Chains | TODO |
| 5.x | PM4Py Extras | TODO |

---

## Quick Start for New Session

```bash
# 1. Check current task status
cat docs/API_OVERHAUL_PLAN.md | grep "Status:"

# 2. Find next TODO task and implement

# 3. After changes, verify
make check
make test
```

---

## Implementation Order

1. **Phase 1.1** - Performance DFG (foundation)
2. **Phase 1.3** - Activities endpoint
3. **Phase 1.2** - Variant complexity
4. **Phase 1.4** - Explorer data (combines above)
5. **Phase 2.1** - OCEL blob (requires migration)
6. **Phase 2.2** - Real OC-DFG
7. **Phase 3.1** - Conformance alignments
8. **Phase 4.1** - Enhanced bottlenecks
9. **Phase 4.2** - Rework chains
10. **Phase 5.x** - PM4Py extras

---

## Key Files

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

1. Update status in `API_OVERHAUL_PLAN.md`: `**Status:** DONE`
2. Run `make check`

---

## After ALL Tasks Complete

```bash
# Lint & type check
make check

# Tests
make test

# Migration (if ORM changed)
alembic revision --autogenerate -m "API overhaul"
alembic upgrade head

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
