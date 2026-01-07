# API Endpoint MVP Readiness — Implementation Plan

> **For: Backend Developer**
> **Priority: Fix by severity (500 → 404 → 400/422)**
> **Scope: Backend only**

---

## Context

Process Mining SaaS MVP. The codebase has gone through multiple refactors and AI-assisted merges, resulting in **141 HTTPException instances across 21 files** that need standardization.

**Core Domain Flow:**
```
Upload CSV → User Maps Columns → Ingest → Dataset Ready → Discovery/Analytics
```

**Already Fixed (per BUG_FIXES_REPORT.md):**
- Health check startup probe
- Database session isolation
- Authentication override for tests
- HTTP redirect handling
- Dataset model field migration
- Missing telemetry router (commented out)
- Missing environment configuration
- Missing CQRS database aliases

**Fixed During This Session:**
- `ReadDBSession` imports added to 16 router files
- Model imports migrated from `src.platform.models` to `src.platform.users` in 15 files
- App now loads without import errors

**Remaining Import Cleanup (26 files):**
Some files still import models from `src.platform.models` using deferred imports inside functions.
These work but should be cleaned up for consistency. Non-blocking.

---

## Issue 1: HTTPException → AppException Conversion

### The Problem

141 endpoints use raw `HTTPException` instead of our standardized `AppException` hierarchy. This breaks RFC 7807 error response format.

### Exception Classes

**Location:** `src/platform/core/exceptions.py`

```python
from src.platform.core.exceptions import (
    # Base
    AppException,              # Base class with RFC 7807 format

    # Client errors (4xx)
    BadRequestError,           # 400 - malformed request
    UnauthorizedError,         # 401 - not authenticated
    AuthenticationError,       # 401 - auth failed
    ForbiddenError,            # 403 - not authorized
    AuthorizationError,        # 403 - permission denied
    NotFoundError,             # 404 - resource not found
    ProjectNotFoundError,      # 404 - specific to projects
    ProcessNotFoundError,      # 404 - specific to processes
    ModelNotFoundError,        # 404 - specific to models
    ConflictError,             # 409 - resource conflict
    ConcurrencyError,          # 409 - optimistic locking
    ValidationError,           # 422 - invalid input
    InvalidInputError,         # 422 - invalid data
    InvalidFileError,          # 422 - file issues
    RateLimitError,            # 429 - too many requests

    # Server errors (5xx)
    InternalError,             # 500 - server error
    ProcessingError,           # 500 - operation failed
    DiscoveryError,            # 500 - discovery specific
    ConformanceError,          # 500 - conformance specific
    IngestionError,            # 500 - ingestion specific
    TimeoutError,              # 504 - operation timeout
    ServiceUnavailableError,   # 503 - dependency down
    ExternalServiceError,      # 502 - external service failed
    PM4PyError,                # 500 - PM4Py specific
    DatabaseError,             # 500 - database error
)
```

### Conversion Rules

```python
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 500 ERRORS (Fix First - Most Severe)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ❌ BEFORE
raise HTTPException(status_code=500, detail="Processing failed")
raise HTTPException(status_code=500, detail="Internal server error")
raise HTTPException(status_code=500, detail=f"Discovery failed: {e}")
raise HTTPException(status_code=500, detail="PM4Py error occurred")

# ✅ AFTER
raise InternalError(message="Processing failed", details={"step": "transformation"})
raise InternalError(message="Unexpected error occurred")
raise DiscoveryError(message=f"Discovery failed: {e}", details={"miner": miner_type})
raise PM4PyError(message="PM4Py operation failed", details={"operation": "alpha_miner"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 503 ERRORS (Service Unavailable)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ❌ BEFORE
raise HTTPException(status_code=503, detail="Temporal service unavailable")
raise HTTPException(status_code=503, detail="Redis unavailable")

# ✅ AFTER
raise ServiceUnavailableError(service="Temporal", message="Workflow service unavailable")
raise ServiceUnavailableError(service="Redis", message="Cache service unavailable")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 404 ERRORS (Fix Second)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ❌ BEFORE
raise HTTPException(status_code=404, detail="Dataset not found")
raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
raise HTTPException(status_code=404, detail="Model not found")
raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
raise HTTPException(status_code=404, detail="Resource not found")

# ✅ AFTER
raise NotFoundError(resource="Dataset", resource_id=dataset_id)
raise NotFoundError(resource="Dataset", resource_id=dataset_id)
raise ModelNotFoundError(model_id=model_id)
raise ProjectNotFoundError(project_id=project_id)
raise NotFoundError(resource="Resource", resource_id=resource_id)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 400/422 ERRORS (Fix Third)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ❌ BEFORE
raise HTTPException(status_code=400, detail="Invalid file format")
raise HTTPException(status_code=400, detail="Bad request")
raise HTTPException(status_code=422, detail="Missing required field: name")
raise HTTPException(status_code=422, detail="Invalid column mapping")

# ✅ AFTER
raise BadRequestError(message="Invalid file format", details={"accepted": ["csv", "xes", "parquet"]})
raise BadRequestError(message="Malformed request")
raise ValidationError(message="Missing required field", details={"field": "name"})
raise ValidationError(message="Invalid column mapping", details={"issue": "case_id column not found"})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 401/403 ERRORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ❌ BEFORE
raise HTTPException(status_code=401, detail="Not authenticated")
raise HTTPException(status_code=401, detail="Invalid token")
raise HTTPException(status_code=403, detail="Not authorized")
raise HTTPException(status_code=403, detail="Permission denied")

# ✅ AFTER
raise AuthenticationError(message="Authentication required")
raise AuthenticationError(message="Invalid or expired token")
raise AuthorizationError(message="Insufficient permissions", details={"required": "editor"})
raise ForbiddenError(message="Access denied to this resource")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 409 ERRORS (Conflicts)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ❌ BEFORE
raise HTTPException(status_code=409, detail="Dataset already exists")
raise HTTPException(status_code=409, detail="Concurrent modification detected")

# ✅ AFTER
raise ConflictError(resource="Dataset", message="Dataset with this name already exists")
raise ConcurrencyError(message="Resource was modified by another request")
```

### Files to Fix (By Severity)

**Severity 1: 500/503 errors (Fix First)**
```
src/features/process_mining/conformance/router.py       # Check for 500s
src/features/process_mining/predictions/router.py       # Check for 500s
src/features/process_mining/ocpm/router.py              # Check for 500s
src/features/process_mining/simulation/router.py        # Check for 500s
src/features/process_mining/visualization/router.py     # Check for 500s
src/api/routers/operations.py                           # Service errors
```

**Severity 2: 404 errors (Fix Second)**
```
src/features/process_mining/datasets/api/crud.py        # Dataset not found
src/features/process_mining/discovery/router.py         # Model not found
src/features/process_mining/analyses/router.py          # Analysis not found
src/platform/projects/api.py                            # Project not found (12 instances)
src/platform/workspaces/api.py                          # Workspace not found (11 instances)
src/api/routers/jobs.py                                 # Job not found
```

**Severity 3: 400/422 errors (Fix Third)**
```
src/features/process_mining/datasets/api/upload.py      # File validation
src/features/process_mining/datasets/api/mapping.py     # Mapping validation
src/features/process_mining/filtering/router.py         # Filter validation
src/features/process_mining/business_use_cases/router.py # Input validation
src/api/routers/workflows.py                            # Request validation
```

### Execution Steps Per File

```bash
# 1. Find all HTTPException in a file
grep -n "raise HTTPException" src/features/process_mining/conformance/router.py

# 2. Check current imports
head -30 src/features/process_mining/conformance/router.py

# 3. Add missing imports at top of file
from src.platform.core.exceptions import (
    NotFoundError,
    ValidationError,
    ProcessingError,
    # ... others as needed
)

# 4. Convert each HTTPException
# 5. Remove HTTPException import if no longer used
# 6. Run type checker
cd backend && .venv/bin/python -m mypy src/features/process_mining/conformance/router.py
```

---

## Issue 2: Verify IngestionService Session Management

### Current State

The ingestion router (`src/features/process_mining/datasets/api/ingestion.py`) uses dependency injection correctly:

```python
async def trigger_ingestion(
    db: ReadDBSession,  # ✅ Session injected via DI
    dataset_id: str,
    user: CurrentUser,
) -> JobStatusResponse:
```

### What to Verify

Check if there's a standalone `IngestionService` class being used as a singleton:

```bash
# Find IngestionService usage
grep -rn "IngestionService" backend/src/
grep -rn "ingestion_service" backend/src/
```

**If singleton pattern found:**

```python
# ❌ BROKEN: Module-level singleton with no session
ingestion_service = IngestionService()  # session=None!

# In some router:
async def some_endpoint():
    await ingestion_service.process(...)  # 💥 No session!
```

**Fix with Option A (Preferred): Create per-request**
```python
# In router:
async def some_endpoint(db: DBSession):
    service = IngestionService(session=db)
    await service.process(...)
```

**Fix with Option B: Pass session to methods**
```python
# Service becomes stateless
class IngestionService:
    async def process(self, session: AsyncSession, ...):
        session.add(record)
        await session.flush()

# Singleton is now safe:
ingestion_service = IngestionService()

# In router:
async def some_endpoint(db: DBSession):
    await ingestion_service.process(session=db, ...)
```

### Files to Check

```
src/features/process_mining/datasets/services/ingestion/service.py
src/features/process_mining/datasets/services/ingestion/__init__.py
src/features/process_mining/datasets/api/upload.py
src/features/process_mining/datasets/api/ingestion.py
```

---

## Issue 3: Temporal Workflow Error Handling

### Files

```
src/platform/temporal/workflows_v2/ingestion.py      # Workflow definition
src/features/process_mining/datasets/api/ingestion.py # Trigger endpoint
```

### Verify Workflow Error Handling

The workflow must update dataset status to ERROR on any failure:

```python
# In workflow (src/platform/temporal/workflows_v2/ingestion.py):
@workflow.defn
class DatasetIngestionWorkflowV2:
    @workflow.run
    async def run(self, dataset_id: str, storage_key: str, mapping: dict):
        try:
            # ... activities ...
            await workflow.execute_activity(
                update_dataset_status,
                args=[dataset_id, DatasetStatus.READY.value],
                ...
            )
        except Exception as e:
            # ✅ MUST: Update dataset status to ERROR
            await workflow.execute_activity(
                update_dataset_status,
                args=[dataset_id, DatasetStatus.ERROR.value, str(e)],
                ...
            )
            raise  # Re-raise so Temporal marks workflow as failed
```

### Verify Trigger Endpoint Error Handling

The trigger endpoint must handle Temporal client failures:

```python
# In ingestion.py trigger_ingestion():
try:
    handle = await client.start_workflow(...)
except Exception as e:
    # ✅ MUST: Update dataset to ERROR state
    dataset.status = DatasetStatus.ERROR.value
    dataset.error_message = f"Failed to start ingestion: {e}"
    await db.commit()
    raise ServiceUnavailableError(service="Temporal", message="Failed to start ingestion workflow")
```

### Current Implementation Status

The current `trigger_ingestion` handles `WorkflowAlreadyStartedError` but may not handle other Temporal client exceptions. Verify and add catch-all handling if missing.

---

## Issue 4: Response Schema Consistency

### Standard Schemas

**Job Status Response** (`src/features/process_mining/schemas/analyses.py`):
```python
class JobStatusResponse(BaseModel):
    id: str                          # workflow_id or job_id
    job_type: JobType                # INGESTION, DISCOVERY, CONFORMANCE, etc.
    status: JobStatus                # PENDING, QUEUED, RUNNING, COMPLETED, FAILED
    progress: int                    # 0-100
    stage: Optional[str] = None      # Current step description
    created_at: datetime
    updated_at: Optional[datetime] = None
    result: Optional[dict] = None    # Present when completed
    error: Optional[str] = None      # Present when failed
```

**Error Response (RFC 7807)** - Automatically generated by AppException:
```python
{
    "type": "https://api.example.com/errors/NOT_FOUND",
    "title": "Resource Not Found",
    "status": 404,
    "detail": "Dataset with id 'abc123' not found",
    "instance": "/api/v1/datasets/abc123",
    "error_code": "ERR_201",
    "correlation_id": "req-uuid-here"
}
```

### Endpoints to Audit

| Endpoint | Expected Response | Schema File |
|----------|-------------------|-------------|
| `POST /datasets/` | `DatasetResponse` | `schemas/datasets.py` |
| `POST /datasets/{id}/ingest` | `JobStatusResponse` | `schemas/analyses.py` |
| `GET /jobs/{id}` | `JobStatusResponse` | `schemas/analyses.py` |
| `POST /discovery/discover` | `JobStatusResponse` or `DiscoveryResponse` | `schemas/discovery.py` |
| `GET /discovery/models/{id}` | `ModelResponse` | `schemas/discovery.py` |
| Any 404/500 error | RFC 7807 format | Auto via `AppException` |

### Audit Command

```bash
# Check return type annotations match actual returns
grep -A 20 "async def " src/features/process_mining/datasets/api/crud.py | grep -E "(->|return)"
```

---

## Issue 5: ReadDBSession Import Fix

### The Problem

The file `src/features/process_mining/datasets/api/ingestion.py` was modified to use `ReadDBSession` but the import is missing.

### The Fix

```python
# At top of ingestion.py, change:
from src.api.dependencies import CurrentUser, DBSession

# To:
from src.api.dependencies import CurrentUser, ReadDBSession

# OR if ReadDBSession doesn't exist, use DBSession:
from src.api.dependencies import CurrentUser, DBSession as ReadDBSession
```

**Note:** Check `src/api/dependencies.py` for available session types:
- `DBSession` - Standard write session
- `ReadDBSession` - Read-optimized session (may be alias to DBSession)
- `WriteDBSession` - Write-optimized session (may be alias to DBSession)

---

## Execution Order

### Phase 1: Critical Path (Day 1)

1. **Fix ReadDBSession import** in `ingestion.py`
2. **Convert 500/503 HTTPExceptions** - Start with:
   - `conformance/router.py`
   - `predictions/router.py`
   - `operations.py`
3. **Verify Temporal error handling** in workflow and trigger

### Phase 2: Resource Errors (Day 2)

1. **Convert 404 HTTPExceptions** - Start with:
   - `datasets/api/crud.py`
   - `discovery/router.py`
   - `projects/api.py`
   - `workspaces/api.py`

### Phase 3: Validation Errors (Day 3)

1. **Convert 400/422 HTTPExceptions** - Start with:
   - `datasets/api/upload.py`
   - `datasets/api/mapping.py`
   - `filtering/router.py`

### Phase 4: Validation (Day 4)

1. Run type checker on all modified files
2. Run tests
3. Manual E2E test

---

## Validation Commands

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Type check modified files
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cd backend
.venv/bin/python -m mypy src/features/process_mining/conformance/router.py
.venv/bin/python -m mypy src/features/process_mining/datasets/api/

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Run tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cd backend
.venv/bin/python -m pytest tests/api/ -v

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Count remaining HTTPExceptions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
grep -r "raise HTTPException" backend/src/ | wc -l
# Target: 0 (or only in platform/core for re-export)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Manual API tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Health check
curl http://localhost:8001/health/ready

# Test 404 error format (MUST return RFC 7807)
curl -s http://localhost:8001/api/v1/datasets/nonexistent-id | jq .

# Expected RFC 7807 response:
# {
#   "type": "https://...",
#   "title": "Resource Not Found",
#   "status": 404,
#   "detail": "Dataset with id 'nonexistent-id' not found",
#   "instance": "/api/v1/datasets/nonexistent-id",
#   "error_code": "ERR_201"
# }

# NOT this (raw HTTPException):
# {
#   "detail": "Dataset not found"
# }
```

---

## Summary Checklist

### Phase 1 (Critical)
- [ ] Fix `ReadDBSession` import in `ingestion.py`
- [ ] Convert 500/503 HTTPExceptions (6 files)
- [ ] Verify Temporal workflow error handling
- [ ] Verify trigger endpoint error handling

### Phase 2 (Resource Errors)
- [ ] Convert 404 HTTPExceptions in `datasets/api/crud.py`
- [ ] Convert 404 HTTPExceptions in `discovery/router.py`
- [ ] Convert 404 HTTPExceptions in `projects/api.py` (12)
- [ ] Convert 404 HTTPExceptions in `workspaces/api.py` (11)
- [ ] Convert 404 HTTPExceptions in `analyses/router.py`
- [ ] Convert 404 HTTPExceptions in `jobs.py`

### Phase 3 (Validation Errors)
- [ ] Convert 400/422 in `datasets/api/upload.py`
- [ ] Convert 400/422 in `datasets/api/mapping.py`
- [ ] Convert 400/422 in remaining routers

### Phase 4 (Validation)
- [ ] All modified files pass mypy
- [ ] All API tests pass
- [ ] 404 responses return RFC 7807 format
- [ ] 500 responses return RFC 7807 format
- [ ] No raw `{"detail": "..."}` responses

---

## File Reference

| File | HTTPException Count | Priority |
|------|---------------------|----------|
| `conformance/router.py` | 21 | P1 |
| `ocpm/router.py` | 19 | P1 |
| `predictions/router.py` | 17 | P1 |
| `visualization/router.py` | 14 | P1 |
| `projects/api.py` | 12 | P2 |
| `workspaces/api.py` | 11 | P2 |
| `business_use_cases/router.py` | 10 | P2 |
| `operations.py` | 6 | P1 |
| `workflows.py` | 5 | P3 |
| `simulation/router.py` | 4 | P2 |
| `analyses/router.py` | 4 | P2 |
| Others | ~18 | P3 |
| **Total** | **141** | |

---

*Generated: 2026-01-07*
