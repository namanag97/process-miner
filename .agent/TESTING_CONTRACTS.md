# Testing Contracts — How to Verify

> "Done" means tests pass. Here's what to run for each change type.

---

## By Change Type

### Modifying a Service (`services/*.py`)

```bash
# Unit tests for the specific service
pytest tests/ -k "{service_name}" -v

# If service is used by multiple routers, run affected router tests
pytest tests/test_{router_name}_router.py -v

# Full backend test
make backend-test
```

### Modifying a Router (`api/routers/*.py`)

```bash
# Router-specific tests
pytest tests/test_{router_name}_router.py -v

# API integration tests
pytest tests/test_api.py -v

# Verify OpenAPI spec
curl http://localhost:8001/openapi.json | python -m json.tool > /dev/null
```

### Modifying ORM Models (`models/orm.py`)

```bash
# 1. Create migration
cd backend
alembic revision --autogenerate -m "describe_change"

# 2. Review generated migration file in alembic/versions/

# 3. Apply migration
alembic upgrade head

# 4. Run full test suite (DB changes affect everything)
make backend-test

# 5. Regenerate SDK
cd sdk && npm run generate && npm run build
```

### Modifying Schemas (`models/schemas.py`)

```bash
# 1. Run all router tests (schemas affect all responses)
make backend-test

# 2. Regenerate SDK (CRITICAL)
cd backend/sdk
npm run generate
npm run build

# 3. Type check frontend if using SDK
cd frontend-new && npx tsc --noEmit
```

### Modifying Core (`core/*.py`)

```bash
# Core affects everything - full test suite
make backend-test

# Check for import errors (often reveals circular deps)
python -c "from src.api.main import app"
```

---

## REQUIRED for ALL Changes

```bash
# Before claiming done
make check  # lint + typecheck + security

# If backend running, quick health check
curl http://localhost:8001/health
```

---

## Test Coverage Gaps to Know

| Area              | Coverage   | Notes                         |
| ----------------- | ---------- | ----------------------------- |
| Routers           | ✅ Good    | All have test files           |
| Services          | ⚠️ Partial | Mining covered, others sparse |
| PM4Py integration | ✅ Good    | `test_e2e_pm4py_features.py`  |
| Business flows    | ✅ Good    | `test_business_flows.py`      |
| Error paths       | ⚠️ Partial | Happy path focus              |
| OCEL/OCPM         | ✅ Good    | `test_ocpm_router.py`         |

---

## Quick Test Commands Reference

```bash
# Run specific test file
pytest tests/test_discovery_router.py -v

# Run tests matching keyword
pytest tests/ -k "discovery or mining" -v

# Run with coverage
make backend-test-cov

# Run only fast tests (skip slow PM4Py ops)
pytest tests/ -m "not slow" -v

# Run failing tests first
pytest tests/ --ff -v
```
