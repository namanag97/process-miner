# Backend API Test Plan

## Scope
168 tests across 7 routers testing traditional process mining + OCPM APIs using pm4py.

## Test Files
| Router | File | Tests | Priority |
|--------|------|-------|----------|
| Processes | test_processes_router.py | 25 | 1 |
| Discovery | test_discovery_router.py | 22 | 1 |
| Conformance | test_conformance_router.py | 25 | 1 |
| OCPM | test_ocpm_router.py | 28 | 1 |
| Analytics | test_analytics_router.py | 28 | 2 |
| Filtering | test_filtering_router.py | 22 | 2 |
| PM4Py Integration | test_pm4py_integration.py | 18 | 2 |

## Test Data
**Source:** `/Users/namanagarwal/system/demo/Insurance_claims_event_log.csv` (30K cases, 180K events)

**Test datasets in `/backend/tests/data/`:**
- `insurance_small.csv` - 100 cases (fast tests)
- `insurance_medium.csv` - 1K cases (thorough tests)
- `rework_cases.csv` - Repeated activities (rework detection)
- `bottleneck_cases.csv` - Long wait times (bottleneck detection)
- `order_management_simple.jsonocel` - 10 orders, 25 items, 10 packages
- `order_management_complex.jsonocel` - 50 orders, multi-type objects

## Strategy
- **Framework:** pytest, pytest-asyncio, httpx AsyncClient
- **DB:** In-memory SQLite (async)
- **No mocking** - Real pm4py integration
- **Validate business logic** - Not just status codes
- **Async tests** - Class-based organization

## Critical Requirements
1. Fix conftest.py imports (old → new architecture)
2. Test raw OCEL JSON extraction (test_ocpm_router.py)
3. Validate all business rules (fitness ∈ [0,1], counts accurate, etc.)
4. Positive + negative + edge cases

## Execution
```bash
# All tests
pytest backend/tests/ -v

# Specific router
pytest backend/tests/test_ocpm_router.py -v

# With coverage
pytest backend/tests/ --cov=src/api --cov=src/services --cov-report=html

# Parallel (fast)
pytest backend/tests/ -n 4
```

## Success Criteria
- ✅ 90%+ endpoint coverage
- ✅ 80%+ code coverage (src/api, src/services)
- ✅ All business logic rules validated
- ✅ 0% flaky tests
- ✅ <2 min full suite (parallel)
