# Recovery Playbook — When Things Break

> Standard procedures for common AI-induced issues.

---

## 🔴 Build Broken

### Symptoms

- `make check` fails
- Import errors
- Syntax errors

### Fix

```bash
# 1. See what changed
git diff --name-only

# 2. Reset to clean state if needed
git stash

# 3. Fresh dependencies
cd backend
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 4. Verify
make check
```

---

## 🔴 Tests Failing After AI Changes

### Fix

```bash
# 1. Find what changed
git diff HEAD~1 --name-only

# 2. Run only affected tests
pytest tests/test_{affected_file}.py -v

# 3. If database related
cd backend
rm -f src/process_mining.db  # Delete test DB
make backend-test  # Fresh run

# 4. Check if schema changed
git diff HEAD~1 -- src/models/schemas.py
# If yes, regenerate SDK
cd sdk && npm run generate
```

---

## 🔴 Type Errors After Schema Change

### Symptoms

- `mypy` failures
- SDK type errors
- Frontend TypeScript errors

### Fix

```bash
# 1. Ensure schemas.py is valid
cd backend
python -c "from src.models.schemas import *"

# 2. Regenerate SDK
cd sdk
npm run generate
npm run build

# 3. If frontend errors
cd ../frontend-new
npx tsc --noEmit
# Fix consuming components
```

---

## 🔴 Circular Import Error

### Symptoms

- `ImportError: cannot import name X from partially initialized module`

### Fix

```bash
# 1. Find the cycle
cd backend
python -c "from src.api.main import app" 2>&1 | head -20

# 2. Common causes:
#    - Router importing from another router
#    - Service importing from router
#    - ORM model importing from service

# 3. Solution: Move shared code to core/ or create interface in types/
```

---

## 🔴 Database Migration Broken

### Symptoms

- `alembic upgrade head` fails
- Foreign key errors

### Fix

```bash
cd backend

# 1. Check current state
alembic current

# 2. If stuck, downgrade
alembic downgrade -1

# 3. Delete bad migration
rm alembic/versions/{bad_migration}.py

# 4. Regenerate
alembic revision --autogenerate -m "fixed_migration"

# 5. Review and apply
alembic upgrade head
```

---

## 🔴 PM4Py Operation Fails

### Symptoms

- PM4Py exception in service
- Empty or malformed result

### Fix

```python
# 1. Verify log format
import pm4py
log = pm4py.read_xes("test.xes")  # or read_csv
print(pm4py.stats.get_variants_as_tuples(log))

# 2. Check required columns
# Must have: case:concept:name, concept:name, time:timestamp

# 3. Common fixes:
# - Ensure timestamp is datetime, not string
# - Ensure case_id column exists
# - Copy log before mutation: log = log.copy()
```

---

## 🔴 Frontend SDK Out of Sync

### Symptoms

- TypeScript type mismatches
- API calls return unexpected shape

### Fix

```bash
# 1. Ensure backend running
cd backend && make run  # Port 8001

# 2. Regenerate SDK
cd sdk
npm run generate
npm run build

# 3. Rebuild frontend
cd ../frontend-new
npm run build
```

---

## 🟡 Quick Reset Commands

```bash
# Backend: full reset
cd backend
make clean
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make check

# Frontend: full reset
cd frontend-new
rm -rf node_modules
npm install
npx tsc --noEmit

# Database: fresh start
cd backend
rm -f data/db/process_mining.db
rm -f src/process_mining.db
alembic upgrade head
```
