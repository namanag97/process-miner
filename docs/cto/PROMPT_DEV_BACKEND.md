# BACKEND DEV TASK: Audit All APIs

## Your Mission

Audit `/backend/src/api/routers/` completely.

## What CTO Needs

### 1. Router Inventory

List every router file:

| File | Routes Count | Purpose |
| ---- | ------------ | ------- |

### 2. Endpoint Inventory

For EACH endpoint:

| Router | Path | Method | Handler Function | Has Tests? | Works? |
| ------ | ---- | ------ | ---------------- | ---------- | ------ |

### 3. PM4Py Usage

Find all PM4Py imports and usages:

| File | PM4Py Function | Purpose | Exposed via API? |
| ---- | -------------- | ------- | ---------------- |

Search in:

- `/backend/src/services/`
- `/backend/src/api/routers/`

### 4. Error Handling

For key endpoints (upload, discovery, conformance):

| Endpoint | Error Handling | Returns What on Error? |
| -------- | -------------- | ---------------------- |

### 5. Test Coverage

Check `/backend/tests/` for test files:

| Router | Test File Exists? | Tests Pass? |
| ------ | ----------------- | ----------- |

## Commands to Run

```bash
# List all router files
ls -la /backend/src/api/routers/

# Count endpoints per router (grep for @router decorators)
grep -c "@router\." backend/src/api/routers/*.py

# Check test files
ls -la /backend/tests/

# Run tests to see what passes
cd backend && python -m pytest tests/ -v --tb=short
```

## Output

Update `/docs/cto/CTO_KNOWLEDGE_BASE.md` Backend section.

Report format:

```
Backend Audit Complete:
- X router files
- Y total endpoints
- Z endpoints tested
- Top issues: [list]
```
