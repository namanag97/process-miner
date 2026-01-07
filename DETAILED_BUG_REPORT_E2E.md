# Detailed Bug Report - Frontend-Backend API Testing
**Generated:** 2026-01-07  
**Test Type:** E2E API Tests using curl-based HTTP requests  
**Backend URL:** http://localhost:8001  
**Total Endpoints Tested:** 61 endpoints  
**Bugs Found:** 18 issues (6 P0 Critical, 12 P1 High)

---

## Executive Summary

Automated E2E API testing revealed **18 bugs** across the backend API, including:
- **6 P0 Critical Issues**: Database schema mismatches, internal server errors, connection timeouts
- **12 P1 High Issues**: Validation errors, authentication issues, missing required parameters

### Key Problem Areas:
1. **Database Migration Issues** - Missing columns (`parquet_s3_key`, `ocel_storage_key`)
2. **Auth Flow Issues** - Password reset not implemented, login validation failing
3. **File Upload Endpoints** - Validation issues with multipart form data
4. **Developer Tools** - Database inspection and log streaming broken

---

## P0 - CRITICAL BUGS (6 issues) 🚨

### BUG-E2E-008: Database Schema Mismatch - Missing `parquet_s3_key` Column
**Priority:** P0 - BLOCKING  
**Category:** Database Schema  
**Endpoint:** `GET /api/v1/datasets/`  
**Impact:** **Cannot list datasets** - Core feature completely broken  

**Error:**
```
(sqlite3.OperationalError) no such column: datasets.parquet_s3_key
```

**Root Cause:**
- SQLAlchemy model `Dataset` references columns that don't exist in database:
  - `parquet_s3_key`
  - `parquet_size_bytes` 
  - `parquet_row_count`
- Missing Alembic migration or migration not applied

**Reproduction:**
```bash
curl -X GET 'http://localhost:8001/api/v1/datasets/' \
  -H 'Authorization: Bearer <token>'
```

**Fix Required:**
1. Create Alembic migration to add missing columns
2. Or remove references from model if columns not needed
3. Run `alembic upgrade head`

**Files Affected:**
- `backend/src/domains/datasets/models.py` or similar
- Missing migration file

---

### BUG-E2E-015 & BUG-E2E-016: OCPM Database Schema Mismatch - Missing `ocel_storage_key`
**Priority:** P0 - BLOCKING  
**Category:** Database Schema  
**Endpoints:** 
- `GET /api/v1/ocpm/logs`
- `POST /api/v1/ocpm/discover`  
**Impact:** **Object-Centric Process Mining completely broken**

**Error:**
```
(sqlite3.OperationalError) no such column: ocel_logs.ocel_storage_key
```

**Root Cause:**
- Model `OCELLog` references non-existent column `ocel_storage_key`
- Migration missing or not applied

**Reproduction:**
```bash
curl -X GET 'http://localhost:8001/api/v1/ocpm/logs' \
  -H 'Authorization: Bearer <token>'
```

**Fix Required:**
1. Add migration for `ocel_logs.ocel_storage_key` column
2. Run migrations
3. Update model or remove column reference

**Files Affected:**
- `backend/src/features/process_mining/models/ocel.py` (line 6)
- Missing migration

---

### BUG-E2E-011: Developer Data Inspector Broken - SQLAlchemy Session Type Error
**Priority:** P0 - BLOCKING DEV TOOLS  
**Category:** Internal Server Error  
**Endpoint:** `GET /api/v1/dev/data/tables`  
**Impact:** Cannot inspect database tables in dev mode

**Error:**
```
No inspection system is available for object of type <class 'sqlalchemy.orm.session.Session'>
```

**Root Cause:**
- Trying to use SQLAlchemy inspection API incorrectly
- Passing Session object instead of database connection/engine

**Reproduction:**
```bash
curl -X GET 'http://localhost:8001/api/v1/dev/data/tables'
```

**Fix Required:**
- Update dev data inspector to use `inspect(engine)` instead of `inspect(session)`
- Example fix:
  ```python
  from sqlalchemy import inspect
  inspector = inspect(db.bind)  # Not inspect(db)
  ```

**Files Affected:**
- Likely in `backend/src/api/routers/dev_data.py` or similar

---

### BUG-E2E-012: Log Streaming Endpoint Timeout
**Priority:** P0 - BLOCKING DEV TOOLS  
**Category:** Connection/Timeout  
**Endpoint:** `GET /api/v1/dev/logs/stream`  
**Impact:** Real-time log streaming not working

**Error:**
```
HTTPConnectionPool(host='localhost', port=8001): Read timed out.
```

**Root Cause:**
- SSE (Server-Sent Events) endpoint hangs indefinitely
- Test timeout set to 30s, endpoint never responds

**Reproduction:**
```bash
curl -X GET 'http://localhost:8001/api/v1/dev/logs/stream'
# Hangs for 30+ seconds then times out
```

**Fix Required:**
- Verify SSE implementation sends initial data/heartbeat
- Add timeout handling
- Consider if endpoint should be excluded from standard tests

**Files Affected:**
- `backend/src/api/routers/dev_logs.py` or similar

---

### BUG-E2E-005: Password Reset Not Implemented
**Priority:** P0 - FEATURE MISSING  
**Category:** Not Implemented  
**Endpoint:** `POST /api/v1/auth/reset-password`  
**Impact:** Users cannot reset passwords

**Error:**
```json
{
  "status": 500,
  "detail": "Password reset token validation is not yet available. Please contact support.",
  "code": "NOT_IMPLEMENTED"
}
```

**Root Cause:**
- Feature stubbed out but not implemented
- Returns 500 instead of proper 501 Not Implemented

**Reproduction:**
```bash
curl -X POST 'http://localhost:8001/api/v1/auth/reset-password' \
  -H 'Content-Type: application/json' \
  -d '{"token": "xyz", "new_password": "NewPass123"}'
```

**Fix Required:**
1. Either implement password reset token validation
2. Or return HTTP 501 instead of 500
3. Update error message

**Files Affected:**
- `backend/src/platform/auth/api.py` or `backend/src/api/routers/auth.py`

---

## P1 - HIGH PRIORITY BUGS (12 issues) ⚠️

### Schema/Validation Issues (9 bugs)

These bugs are **expected behavior** for invalid inputs, but highlight UX/DX issues:

#### BUG-E2E-001: Missing Required Query Parameter `dataset_id`
**Endpoint:** `GET /api/v1/algorithms/recommend`  
**Issue:** E2E test doesn't provide required `dataset_id` query param  
**Fix:** Test data generator needs to provide valid query params

#### BUG-E2E-002: Missing Required Query Parameter `dataset_id`  
**Endpoint:** `POST /api/v1/analyses`  
**Issue:** Same as above

#### BUG-E2E-006: UUID Validation Too Strict
**Endpoint:** `POST /api/v1/conformance/check`  
**Error:** `String should have at least 36 characters` (UUID validation)  
**Issue:** Test sends `"test_string"` but API expects valid UUID (36+ chars)

#### BUG-E2E-007: Multiple Missing Query Parameters
**Endpoint:** `POST /api/v1/conformance/import-model`  
**Missing:** `project_id`, `model_name`, `model_content`  
**Issue:** Parameters should be in request body, not query string (API design issue?)

#### BUG-E2E-009 & BUG-E2E-014: File Upload Endpoints Fail with JSON
**Endpoints:**
- `POST /api/v1/datasets/`
- `POST /api/v1/ocpm/upload`  
**Issue:** Expecting `multipart/form-data` but test sends `application/json`  
**Fix:** E2E tester needs file upload support

#### BUG-E2E-010: File Extension Validation
**Endpoint:** `POST /api/v1/datasets/presign`  
**Error:** `File type '' is not supported`  
**Issue:** Test sends `"test_string"` as filename (no extension)  
**Expected:** `.csv` or `.xes` extension

#### BUG-E2E-013: UUID Validation  
**Endpoint:** `POST /api/v1/discovery/discover`  
**Error:** Same UUID length validation as BUG-E2E-006

#### BUG-E2E-017 & BUG-E2E-018: Missing Query Parameters
**Endpoints:**
- `POST /api/v1/projects` (missing `workspace_id`)
- `POST /api/v1/workspaces` (missing `org_id`)  
**Issue:** Required IDs not provided in test

---

### Authentication Issues (3 bugs)

#### BUG-E2E-003: Password Validation Too Strict
**Endpoint:** `POST /api/v1/auth/register`  
**Error:**
```
Password must contain: at least one uppercase letter, at least one digit
```
**Issue:** Test password `"test_string"` doesn't meet requirements  
**Note:** This is correct validation, not a bug

#### BUG-E2E-004: Login Fails with Invalid Credentials
**Endpoint:** `POST /api/v1/auth/login`  
**Status:** 401 Unauthorized  
**Error:** `Invalid email or password`  
**Issue:** Test uses non-existent user credentials  
**Note:** This is expected behavior, but shows E2E test needs valid test users

---

## Summary by Category

| Category | Count | Severity | Impact |
|----------|-------|----------|--------|
| **Database Schema** | 3 | P0 | 🔴 BLOCKING - Core features broken |
| **Not Implemented** | 1 | P0 | 🔴 Missing feature |
| **Dev Tools** | 2 | P0 | 🟡 Dev experience degraded |
| **Validation** | 9 | P1 | 🟢 Expected errors (test data issue) |
| **Auth** | 3 | P1 | 🟢 Expected errors (test data issue) |

---

## Recommended Actions

### Immediate (P0 - Critical)
1. **Run database migrations**
   ```bash
   cd backend && .venv/bin/alembic upgrade head
   ```
   
2. **If migrations don't exist, create them:**
   ```bash
   # Add parquet columns to datasets table
   cd backend && .venv/bin/alembic revision --autogenerate -m "add parquet storage columns"
   
   # Add ocel_storage_key to ocel_logs
   cd backend && .venv/bin/alembic revision --autogenerate -m "add ocel storage key"
   ```

3. **Fix dev data inspector** (backend/src/api/routers/dev_data.py:XX)
   - Change `inspect(db)` to `inspect(db.bind)`

4. **Fix password reset endpoint**
   - Either implement or return HTTP 501

5. **Fix log streaming timeout**
   - Add initial response or exclude from tests

### Short-term (P1 - High)
1. **Improve E2E test data generation**
   - Generate valid UUIDs for dataset_id, model_id, etc.
   - Use test fixtures from `backend/tests/conftest.py`
   - Support multipart/form-data for file uploads

2. **API Design Review**
   - Consider if query params should be body params (BUG-E2E-007)
   - Review parameter placement consistency

---

## Test Coverage Analysis

**Endpoints Tested:** 61  
**Endpoints Skipped:** 109 (require path parameters like `{dataset_id}`)

### Skipped Endpoints Requiring Integration Tests:
- All `GET/DELETE /api/v1/datasets/{dataset_id}` variants (13 endpoints)
- All `GET/DELETE /api/v1/ocpm/datasets/{dataset_id}` variants (8 endpoints)  
- All analytics endpoints with `{dataset_id}` (8 endpoints)
- Model-specific endpoints `{model_id}` (10+ endpoints)

**Recommendation:** Implement multi-step test flows:
1. Create dataset → Get dataset_id → Test dependent endpoints
2. Upload file → Ingest → Discover model → Test model endpoints

---

## Next Steps

1. ✅ **Fix P0 database issues** (estimated 1-2 hours)
2. ✅ **Fix P0 dev tools** (estimated 30 mins)
3. 🔄 **Enhance E2E test suite** to create test data (estimated 2-4 hours)
4. 🔄 **Add multi-step user flow tests** (estimated 4-8 hours)
5. 📊 **Re-run tests** to verify fixes

---

## Appendix: Full Test Output

**Test Duration:** ~60 seconds  
**Success Rate:** 70.5% (43/61 passed)  
**Test Report:** `backend/tests/e2e/bug_reports/report_20260107_141717.md`

### Domains with Issues:
- ❌ **Datasets** (3 P0, 2 P1) - Most critical
- ❌ **OCPM** (2 P0, 2 P1) - Broken feature
- ❌ **DevData/DevLogs** (2 P0) - Dev tools broken
- ⚠️ **Auth** (1 P0, 3 P1) - Partial issues
- ⚠️ **Conformance** (2 P1) - Validation only
- ⚠️ **Discovery** (1 P1) - Validation only

### Domains Working Well:
- ✅ **Audit** (2/2 passed)
- ✅ **Organizations** (2/2 passed)
- ✅ **DAGs** (4/6 passed)
- ✅ **Jobs** (1/1 passed)
- ✅ **Workflows** (2/3 passed)

