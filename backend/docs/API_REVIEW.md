# API Review & Stabilization Document

**Last Updated:** 2026-01-07
**Status:** Deep domain analysis complete - Critical security gaps identified
**Reviewer:** API Stabilization Agent
**Handoff Status:** Ready for implementation agent

---

## Executive Summary

### Critical Security Findings

| Priority | Issue | Endpoints Affected | Location |
|----------|-------|-------------------|----------|
| P0 | **Conformance router missing auth** | 13 endpoints | `conformance/router.py` |
| P0 | **Visualization router missing auth** | 8 endpoints | `visualization/router.py` |
| P0 | **Analyses router missing auth** | 5 endpoints | `analyses/router.py` |
| P0 | **Business Use Cases router missing auth** | 5 endpoints | `business_use_cases/router.py` |
| P1 | **OCPM router missing authz** | 11 endpoints | `ocpm/router.py` |
| P2 | **Organizational router incomplete** | 5 of 6 endpoints not exposed | `organizational/router.py` |
| P2 | **Simulation router incomplete** | 3 of 3 endpoints not exposed | `simulation/router.py` |

### Already Fixed (Verified)
- Discovery authentication and authorization
- Analytics authentication and caching
- OCPM race condition in lookup tables

### Well-Protected Domains
- Datasets (full auth/authz)
- Filtering (full auth/authz)
- Statistics (full auth/authz)
- Platform (Auth, Orgs, Workspaces, Projects, Jobs)

---

## API Domain Structure

```
backend/src/
├── platform/users/api/          # Admin Domain - SECURE
│   ├── auth.py                  # Authentication (JWT)
│   ├── organizations.py         # Multi-tenant orgs
│   ├── workspaces.py            # Workspace RBAC
│   └── projects.py              # Project management
│
├── features/process_mining/     # Process Mining Domain
│   ├── datasets/api/            # SECURE - Event log management
│   │   ├── crud.py              # CRUD operations
│   │   ├── upload.py            # File upload
│   │   ├── mapping.py           # Column mapping
│   │   ├── ingest.py            # Data ingestion
│   │   └── export.py            # Data export
│   ├── discovery/               # FIXED - Process discovery
│   ├── analytics/               # FIXED - Performance analytics
│   ├── statistics/              # SECURE - Dataset statistics
│   ├── filtering/               # SECURE - Event log filtering
│   ├── conformance/             # NO AUTH - Conformance checking
│   ├── visualization/           # NO AUTH - Graph data
│   ├── analyses/                # NO AUTH - Saved analyses
│   ├── business_use_cases/      # NO AUTH - P2P, O2C, etc.
│   ├── ocpm/                    # NO AUTHZ - Object-centric PM
│   ├── organizational/          # INCOMPLETE - Social networks
│   ├── simulation/              # INCOMPLETE - What-if analysis
│   ├── predictions/             # INCOMPLETE - ML predictions
│   └── workflows/               # DEPRECATED - Use DAGs
│
└── platform/                    # Infrastructure - SECURE
    ├── jobs/                    # Async job tracking
    ├── dag/                     # DAG orchestration
    └── health/                  # Health checks
```

---

## Detailed Domain Analysis

### 1. Auth Domain (`/api/v1/auth/*`) - SECURE

| Endpoint | Method | Auth | Status | Notes |
|----------|--------|------|--------|-------|
| `/login` | POST | - | OK | Public endpoint |
| `/register` | POST | - | OK | Public endpoint |
| `/logout` | POST | Yes | OK | |
| `/refresh` | POST | - | OK | Uses refresh token |
| `/me` | GET | Yes | OK | |
| `/me` | PUT | Yes | OK | |
| `/forgot-password` | POST | - | OK | Prevents email enumeration |
| `/reset-password` | POST | - | STUB | Returns 501 |
| `/change-password` | POST | Yes | OK | Requires current password |
| `/oauth/*` | GET | - | STUB | Returns 501 |

**Notes:**
- OAuth endpoints return 501 (acceptable for MVP)
- Password reset not implemented

---

### 2. Organizations Domain (`/api/v1/organizations/*`) - SECURE

| Endpoint | Method | Auth | Authz | Status | Notes |
|----------|--------|------|-------|--------|-------|
| `/` | GET | Yes | - | OK | |
| `/` | POST | Yes | - | OK | |
| `/{org_id}` | GET | Yes | member | OK | |
| `/{org_id}` | PUT | Yes | admin | OK | |
| `/{org_id}` | DELETE | Yes | owner | OK | Blocks if workspaces exist |
| `/{org_id}/members` | GET | Yes | member | OK | |
| `/{org_id}/members/invite` | POST | Yes | admin | ISSUE | Creates passwordless users |
| `/{org_id}/members/{user_id}` | DELETE | Yes | admin | OK | |
| `/{org_id}/members/{user_id}/role` | PUT | Yes | owner | OK | |
| `/{org_id}/billing` | GET | Yes | admin | STUB | |
| `/{org_id}/usage` | GET | Yes | admin | OK | |

**Functional Issues:**
- **FN-001**: `invite_member` creates users without password hash
  - Location: `organizations.py:302-311`
  - Impact: Invited users cannot log in
  - Fix: Implement proper invite flow with email verification

---

### 3. Workspaces Domain (`/api/v1/workspaces/*`) - SECURE

| Endpoint | Method | Auth | Authz | Status | Notes |
|----------|--------|------|-------|--------|-------|
| `/` | GET | Yes | RLS | OK | Filtered by membership |
| `/{workspace_id}` | GET | Yes | viewer+ | OK | |
| `/` | POST | Yes | org_member | OK | |
| `/{workspace_id}` | PUT | Yes | admin+ | OK | |
| `/{workspace_id}` | DELETE | Yes | owner | ISSUE | Unsafe cascade |
| `/{workspace_id}/projects/{project_id}` | POST | Yes | admin+ | OK | |
| `/{workspace_id}/projects/{project_id}` | DELETE | Yes | admin+ | OK | |
| `/{workspace_id}/members` | GET | Yes | viewer+ | OK | |
| `/{workspace_id}/members` | POST | Yes | admin+ | OK | |
| `/{workspace_id}/members/{user_id}` | PUT | Yes | admin+ | OK | |
| `/{workspace_id}/members/{user_id}` | DELETE | Yes | admin+ | OK | |

**Functional Issues:**
- **FN-002**: Workspace delete cascades without checking datasets
  - Location: `workspaces.py:314`
  - Impact: Potential data loss - datasets orphaned or deleted
  - Fix: Add dataset count check before delete

---

### 4. Projects Domain (`/api/v1/projects/*`) - SECURE

| Endpoint | Method | Auth | Authz | Status | Notes |
|----------|--------|------|-------|--------|-------|
| `/` | POST | Yes | editor+ | OK | |
| `/` | GET | Yes | RLS | OK | |
| `/{project_id}` | GET | Yes | viewer+ | OK | |
| `/{project_id}` | PUT | Yes | editor+ | OK | |
| `/{project_id}` | DELETE | Yes | editor+ | OK | Unlinks datasets |
| `/{project_id}/files/{dataset_id}` | POST | Yes | editor+ | OK | |
| `/{project_id}/files/{dataset_id}` | DELETE | Yes | editor+ | OK | |
| `/{project_id}/archive` | POST | Yes | editor+ | ISSUE | Schema fallback |
| `/{project_id}/restore` | POST | Yes | editor+ | ISSUE | Schema fallback |

**Functional Issues:**
- **FN-003**: Archive/restore uses try/except for missing `archived` field
  - Location: `projects.py:442-451, 484-496`
  - Impact: Schema inconsistency, code smell
  - Fix: Add `archived` field to Project model or remove feature

---

### 5. Datasets Domain (`/api/v1/datasets/*`) - SECURE

| Endpoint | Method | Auth | Authz | Status |
|----------|--------|------|-------|--------|
| `/` | GET | Yes | project | OK |
| `/` | POST | Yes | project | OK |
| `/{id}` | GET | Yes | dataset | OK |
| `/{id}` | DELETE | Yes | dataset | OK |
| `/presign` | POST | Yes | project | OK |
| `/{id}/uploaded` | POST | Yes | dataset | OK |
| `/{id}/columns` | GET | Yes | dataset | OK |
| `/{id}/mapping` | GET/POST/PUT | Yes | dataset | OK |
| `/{id}/preview` | POST | Yes | dataset | OK |
| `/{id}/ingest` | POST | Yes | dataset | OK |
| `/{id}/reingest` | POST | Yes | dataset | OK |
| `/{id}/export` | POST | Yes | dataset | OK |
| `/{id}/download` | GET | Yes | dataset | OK |
| `/{id}/sheets` | GET | Yes | dataset | OK |

**Assessment:** Well-architected with consistent auth/authz patterns.

---

### 6. Discovery Domain (`/api/v1/discovery/*`) - FIXED

| Endpoint | Method | Auth | Authz | Status |
|----------|--------|------|-------|--------|
| `/miners` | GET | - | - | OK (public) |
| `/discover` | POST | Yes | - | OK |
| `/models` | GET | Yes | - | OK |
| `/models/{id}` | GET | Yes | - | OK |
| `/models/{id}` | DELETE | Yes | dataset | FIXED |

**Notes:**
- Authentication added to all endpoints
- Authorization check on delete (requires dataset permission)

---

### 7. Analytics Domain (`/api/v1/analytics/*`) - FIXED

| Endpoint | Method | Auth | Authz | Status |
|----------|--------|------|-------|--------|
| `/datasets/{id}/bottlenecks` | GET | Yes | - | OK |
| `/datasets/{id}/rework` | GET | Yes | - | OK |
| `/datasets/{id}/service-times` | GET | Yes | - | OK |
| `/datasets/{id}/cycle-time` | GET | Yes | - | FIXED (caching) |
| `/datasets/{id}/throughput` | GET | Yes | - | FIXED (caching) |
| `/datasets/{id}/patterns` | GET | Yes | - | OK |
| `/datasets/{id}/rework-chains` | GET | Yes | - | OK |
| `/datasets/{id}/performance` | GET | Yes | - | OK |

**Notes:**
- Authentication added to all endpoints
- Caching now consistent across all endpoints

---

### 8. Statistics Domain (`/api/v1/datasets/{id}/*`) - SECURE

| Endpoint | Method | Auth | Authz | Status |
|----------|--------|------|-------|--------|
| `/{id}/statistics` | GET | Yes | dataset | OK |
| `/{id}/cases` | GET | Yes | dataset | OK |
| `/{id}/variants` | GET | Yes | dataset | OK |
| `/{id}/activities` | GET | Yes | dataset | OK |
| `/{id}/events` | GET | Yes | dataset | OK |
| `/{id}/metadata` | GET | Yes | dataset | OK |

**Assessment:** Well-protected with `require_dataset_permission` on all endpoints.

---

### 9. Filtering Domain (`/api/v1/filtering/*`) - SECURE

| Endpoint | Method | Auth | Authz | Status |
|----------|--------|------|-------|--------|
| `/datasets/{id}/apply` | POST | Yes | dataset | OK |
| `/datasets/{id}/preview` | POST | Yes | dataset | OK |
| `/datasets/{id}/options` | GET | Yes | dataset | OK |
| `/datasets/{id}/results` | GET | Yes | dataset | OK |
| `/datasets/{id}/results/{fid}` | DELETE | Yes | dataset | OK |
| `/templates` | GET | - | - | OK (public) |

**Assessment:** Well-protected with `require_dataset_permission` on dataset endpoints.

---

### 10. Conformance Domain (`/api/v1/conformance/*`) - CRITICAL

| Endpoint | Method | Auth | Authz | Status |
|----------|--------|------|-------|--------|
| `/check` | POST | NO | NO | **CRITICAL** |
| `/results` | GET | NO | NO | **CRITICAL** |
| `/results/{id}` | GET | NO | NO | **CRITICAL** |
| `/results/{id}` | DELETE | NO | NO | **CRITICAL** |
| `/diagnostics/{ds}/{model}` | GET | NO | NO | **CRITICAL** |
| `/deviations/{ds}/{model}` | GET | NO | NO | **CRITICAL** |
| `/alignments/{ds}/{model}` | GET | NO | NO | **CRITICAL** |
| `/methods` | GET | - | - | OK (public) |
| `/quality/{ds}/{model}` | GET | NO | NO | **CRITICAL** |
| `/import-model` | POST | NO | NO | **CRITICAL** |
| `/root-cause/{ds}/{model}` | GET | NO | NO | **CRITICAL** |
| `/deviations/by-activity/{ds}/{model}` | GET | NO | NO | **CRITICAL** |
| `/deviations/by-position/{ds}/{model}` | GET | NO | NO | **CRITICAL** |
| `/deviations/attribute-correlation/{ds}/{model}` | GET | NO | NO | **CRITICAL** |

**Security Issue:**
- **SEC-001**: All endpoints missing `user: CurrentUser` dependency
- Location: `conformance/router.py`
- Impact: Any unauthenticated user can access conformance checking

---

### 11. Visualization Domain (`/api/v1/visualization/*`) - CRITICAL

| Endpoint | Method | Auth | Authz | Status |
|----------|--------|------|-------|--------|
| `/{id}/dfg` | GET | NO | NO | **CRITICAL** |
| `/{id}/dfg/svg` | GET | NO | NO | **CRITICAL** |
| `/models/{id}/petri` | GET | NO | NO | **CRITICAL** |
| `/models/{id}/svg` | GET | NO | NO | **CRITICAL** |
| `/{id}/footprints` | GET | NO | NO | **CRITICAL** |
| `/{id}/explorer-data` | GET | NO | NO | **CRITICAL** |

**Security Issue:**
- **SEC-002**: All endpoints missing `user: CurrentUser` dependency
- Location: `visualization/router.py`
- Impact: Any unauthenticated user can access process visualizations

---

### 12. Analyses Domain (`/api/v1/analyses/*`) - CRITICAL

| Endpoint | Method | Auth | Authz | Status |
|----------|--------|------|-------|--------|
| `/metadata` | GET | - | - | OK (public) |
| `/` | POST | NO | NO | **CRITICAL** |
| `/` | GET | NO | NO | **CRITICAL** |
| `/{id}` | GET | NO | NO | **CRITICAL** |
| `/{id}` | DELETE | NO | NO | **CRITICAL** |
| `/log/{dataset_id}` | GET | NO | NO | **CRITICAL** |

**Security Issue:**
- **SEC-003**: All CRUD endpoints missing `user: CurrentUser` dependency
- Location: `analyses/router.py`
- Impact: Any unauthenticated user can create/read/delete analyses

---

### 13. Business Use Cases Domain (`/api/v1/business/*`) - CRITICAL

| Endpoint | Method | Auth | Authz | Status |
|----------|--------|------|-------|--------|
| `/p2p/mavericks/{ds}/{model}` | GET | NO | NO | **CRITICAL** |
| `/p2p/audit-report/{ds}/{model}` | GET | NO | NO | **CRITICAL** |
| `/o2c/split-log/{id}` | GET | NO | NO | **CRITICAL** |
| `/o2c/compare/{id1}/{id2}` | GET | NO | NO | **CRITICAL** |
| `/supply-chain/simulate/{id}` | POST | NO | NO | **CRITICAL** |
| `/customer-journey/dropoffs/{id}` | GET | NO | NO | **CRITICAL** |

**Security Issue:**
- **SEC-004**: All endpoints missing `user: CurrentUser` dependency
- Location: `business_use_cases/router.py`
- Impact: Any unauthenticated user can run business analyses

---

### 14. OCPM Domain (`/api/v1/ocpm/*`) - PARTIAL

| Endpoint | Method | Auth | Authz | Status |
|----------|--------|------|-------|--------|
| `/upload` | POST | Yes | NO | Missing project perm |
| `/logs` | GET | Yes | - | OK |
| `/datasets/{id}` | GET | Yes | NO | Missing dataset perm |
| `/datasets/{id}` | DELETE | Yes | NO | Missing dataset perm |
| `/datasets/{id}/object-types` | GET | Yes | NO | Missing dataset perm |
| `/datasets/{id}/statistics` | GET | Yes | NO | Missing dataset perm |
| `/discover` | POST | Yes | NO | Missing dataset perm |
| `/models` | GET | Yes | - | OK |
| `/models/{id}` | GET | Yes | NO | Missing model perm |
| `/models/{id}` | DELETE | Yes | NO | Missing model perm |
| `/datasets/{id}/relationships` | GET | Yes | NO | Missing dataset perm |
| `/datasets/{id}/oc-dfg` | GET | Yes | NO | Missing dataset perm |
| `/formats` | GET | - | - | OK (public) |
| `/datasets/{id}/flatten` | POST | Yes | NO | Missing dataset perm |

**Security Issue:**
- **SEC-005**: Authentication present but no authorization checks
- Location: `ocpm/router.py`
- Impact: Any authenticated user can access any OCEL data

---

### 15. Organizational Mining Domain (`/api/v1/organizational/*`) - INCOMPLETE

| Function | Decorated | Auth | Status |
|----------|-----------|------|--------|
| `get_handover_network` | NO | NO | **NOT EXPOSED** |
| `get_collaboration_network` | NO | NO | **NOT EXPOSED** |
| `get_resource_similarity` | NO | NO | **NOT EXPOSED** |
| `get_roles` | NO | NO | **NOT EXPOSED** |
| `get_resource_profile` | YES | NO | No auth |
| `get_workload` | NO | NO | **NOT EXPOSED** |

**Functional Issue:**
- **FN-004**: 5 of 6 functions missing `@router.get` decorators
- Location: `organizational/router.py:60-138`
- Impact: API not accessible - dead code

---

### 16. Simulation Domain (`/api/v1/simulation/*`) - INCOMPLETE

| Function | Decorated | Auth | Status |
|----------|-----------|------|--------|
| `play_out_model` | NO | NO | **NOT EXPOSED** |
| `simulate_scenario` | NO | NO | **NOT EXPOSED** |
| `estimate_capacity` | NO | NO | **NOT EXPOSED** |

**Functional Issue:**
- **FN-005**: All 3 functions missing `@router.post/@router.get` decorators
- Location: `simulation/router.py:59-179`
- Impact: API not accessible - dead code

---

### 17. Workflows Domain (`/api/v1/workflows/*`) - DEPRECATED

All endpoints return 501 with message to use `/api/v1/dags` instead.
**Action:** Consider removing or documenting deprecation timeline.

---

### 18. Jobs Domain (`/api/v1/jobs/*`) - SECURE

| Endpoint | Method | Auth | Status |
|----------|--------|------|--------|
| `/{job_id}` | GET | Yes | OK |
| `/` | GET | Yes | OK |
| `/{job_id}/cancel` | POST | Yes | OK |

---

## Issue Summary

### Security Issues (Require Immediate Fix)

| ID | Severity | Domain | Issue | Endpoints |
|----|----------|--------|-------|-----------|
| SEC-001 | P0 | Conformance | Missing authentication | 13 |
| SEC-002 | P0 | Visualization | Missing authentication | 6 |
| SEC-003 | P0 | Analyses | Missing authentication | 5 |
| SEC-004 | P0 | Business Use Cases | Missing authentication | 6 |
| SEC-005 | P1 | OCPM | Missing authorization | 11 |

### Functional Issues (MVP Priority)

| ID | Severity | Domain | Issue | Location |
|----|----------|--------|-------|----------|
| FN-001 | **P0** | Organizations | **Passwordless invite - users can't log in** | `organizations.py:302-311` |
| FN-002 | **P0** | Workspaces | **Cascade delete causes data loss** | `workspaces.py:314` |
| FN-003 | **P0** | Statistics | **`total_variants` always returns 0** | `statistics/router.py:73,462` |
| FN-004 | **P1** | Organizational | 5 of 6 endpoints not exposed (dead code) | `organizational/router.py:60-138` |
| FN-005 | **P1** | Simulation | All 3 endpoints not exposed (dead code) | `simulation/router.py:59-179` |
| FN-006 | P2 | Projects | Schema fallback logic for `archived` field | `projects.py:442-496` |
| FN-007 | P2 | Temporal | Workflow args passed incorrectly in compat layer | `temporal/compat.py:153` |

---

## Detailed Functional Bug Analysis

### FN-001: Passwordless Invite (P0 - Blocking)

**Problem:** `invite_member` creates users without password hash - invited users cannot log in.

**Location:** `src/platform/users/api/organizations.py:302-311`

**Code:**
```python
new_user = User(
    id=str(uuid4()),
    email=request.email,
    name=request.email.split("@")[0],
    role=request.role,
    organization_id=org_id,
    # NO password_hash!
)
```

**Impact:** Any invited user is stuck - they have an account but no way to authenticate.

**Fix:** Either:
1. Generate invite token + email flow
2. Generate temporary password and force reset on first login

---

### FN-002: Cascade Delete Data Loss (P0 - Blocking)

**Problem:** Workspace delete cascades to projects without checking if projects have datasets.

**Location:** `src/platform/users/api/workspaces.py:314`

**Code:**
```python
# Deletes workspace and all projects - BUT what about datasets?
await db.delete(workspace)
```

**Impact:** User deletes workspace -> projects deleted -> datasets orphaned or deleted -> **data loss**

**Fix:** Add check before delete:
```python
dataset_count = await db.execute(
    select(func.count()).select_from(Dataset)
    .join(Project).where(Project.workspace_id == workspace_id)
)
if dataset_count.scalar() > 0:
    raise ValidationError("Cannot delete workspace with datasets. Delete datasets first.")
```

---

### FN-003: total_variants Always Returns 0 (P0 - Broken Feature)

**Problem:** `total_variants` is hardcoded to `0` in multiple places instead of being computed.

**Locations:**
- `statistics/router.py:73` - `get_statistics()` fallback
- `statistics/router.py:462` - `get_metadata()`
- `api/datasets/analytics.py:61,446`

**Code:**
```python
return StatisticsResponse(
    total_events=dataset.total_events,
    total_cases=dataset.total_cases,
    total_variants=0,  # <-- HARDCODED!
    ...
)
```

**Impact:** Frontend always shows "0 variants" even when dataset has variants.

**Fix:** Compute from ProcessCase:
```python
variant_count = await db.execute(
    select(func.count(func.distinct(ProcessCase.variant_key)))
    .where(ProcessCase.dataset_id == dataset_id)
)
total_variants = variant_count.scalar() or 0
```

---

### FN-004: Organizational Endpoints Dead Code (P1)

**Problem:** 5 of 6 functions in organizational router have no `@router.get` decorator.

**Location:** `src/features/process_mining/organizational/router.py:60-138`

**Dead Functions:**
- `get_handover_network()` - no decorator
- `get_collaboration_network()` - no decorator
- `get_resource_similarity()` - no decorator
- `get_roles()` - no decorator
- `get_workload()` - no decorator

**Only exposed:** `get_resource_profile()` (line 47)

**Impact:** Organizational mining features are **completely inaccessible** via API.

**Fix:** Add decorators:
```python
@router.get("/datasets/{dataset_id}/handover-network")
async def get_handover_network(...):
```

---

### FN-005: Simulation Endpoints Dead Code (P1)

**Problem:** All 3 functions in simulation router have no decorators.

**Location:** `src/features/process_mining/simulation/router.py:59-179`

**Dead Functions:**
- `play_out_model()` - no decorator
- `simulate_scenario()` - no decorator
- `estimate_capacity()` - no decorator

**Impact:** Simulation features are **completely inaccessible** via API.

---

### FN-007: Temporal Workflow Args Passed Incorrectly (P2)

**Problem:** `_dispatch_temporal` slices args incorrectly when calling workflow.

**Location:** `src/platform/temporal/compat.py:153`

**Code:**
```python
handle = await client.start_workflow(
    mapping["workflow"].run,
    args=[args.get("dataset_id", args.get("entity_id"))] + list(args.values())[1:],
    # ^^ This assumes dict ordering and drops first value
)
```

**Impact:** Workflows may receive wrong arguments if dict key order changes.

**Fix:** Pass args explicitly:
```python
if workflow_type == "dataset_ingestion":
    handle = await client.start_workflow(
        DatasetIngestionWorkflow.run,
        args.get("dataset_id"),
        args.get("storage_key"),
        args.get("case_id_column"),
        ...
    )
```

---

## State Machine Analysis

### Dataset Status Flow

**Expected:**
```
PENDING -> UPLOADED -> VALIDATING -> AWAITING_MAPPING -> MAPPED -> INGESTING -> READY
                                                                       |
                                                                       v
                                                                     ERROR
```

**Issues Found:**

1. **Missing VALIDATING transition:** Upload confirms `UPLOADED` but validation workflow should set `VALIDATING`. Currently jumps straight to `AWAITING_MAPPING`.

2. **No rollback on failure:** If ingestion fails mid-way, dataset stays in `INGESTING` forever. No automatic rollback to `MAPPED`.

3. **Re-ingest from READY:** Allowed but doesn't clear old events before re-ingesting (potential duplicates).

---

## Error Handling Issues

### Pattern: Bare `except Exception` swallows details

**Locations:**
- `filtering/router.py:332-341` - `except Exception: pass` (silent failure)
- `statistics/router.py:55-66` - JSON parse failures logged but returned empty
- `conformance/router.py:283,310,343,386` - `except Exception` returns 500

**Impact:** Debugging is difficult; errors are hidden.

---

## Data Integrity Issues

### 1. Orphaned Records on Delete

**Project Delete:** Unlinks datasets but doesn't null out `project_id` in Dataset table.
- Location: `projects.py:181-195`

**Workspace Delete:** Cascades to projects but datasets may reference deleted projects.

### 2. Duplicate Mapping Records

**Problem:** Both `DatasetColumnMapping` table AND `dataset.mapping_json` store mapping.
- Location: `mapping.py:224-232`
- Causes: Inconsistency if one is updated and other isn't

---

## Implementation Roadmap for Next Agent

### Phase 1: Critical Security (Immediate)

**Task 1.1: Fix Conformance Router**
```
File: src/features/process_mining/conformance/router.py
Changes:
1. Import CurrentUser: from src.api.dependencies import CurrentUser
2. Import permission check: from src.platform.workspaces.authorization import require_dataset_permission
3. Add user: CurrentUser to all 13 endpoint signatures
4. Add await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ) to each endpoint
```

**Task 1.2: Fix Visualization Router**
```
File: src/features/process_mining/visualization/router.py
Changes:
1. Import CurrentUser and permission check
2. Add user: CurrentUser to all 6 endpoints
3. Add dataset permission checks
```

**Task 1.3: Fix Analyses Router**
```
File: src/features/process_mining/analyses/router.py
Changes:
1. Import CurrentUser and permission check
2. Add user: CurrentUser to 5 endpoints (not /metadata)
3. Add dataset permission checks
```

**Task 1.4: Fix Business Use Cases Router**
```
File: src/features/process_mining/business_use_cases/router.py
Changes:
1. Import CurrentUser and permission check
2. Add user: CurrentUser to all 6 endpoints
3. Add dataset permission checks
```

### Phase 2: Authorization (Short-term)

**Task 2.1: Add Authorization to OCPM Router**
```
File: src/features/process_mining/ocpm/router.py
Changes:
1. Add require_dataset_permission to all dataset endpoints
2. Add require_project_permission to upload endpoint
3. Add model ownership checks to model endpoints
```

### Phase 3: Completeness (Medium-term)

**Task 3.1: Complete Organizational Router**
- Determine if endpoints should be exposed
- Add @router.get decorators to 5 functions
- Add authentication and authorization

**Task 3.2: Complete Simulation Router**
- Add @router.post/@router.get decorators to 3 functions
- Add authentication and authorization

### Phase 4: Functional Fixes

**Task 4.1: Fix Passwordless Invite**
- Implement proper invite flow with email token
- OR generate temporary password and require change on first login

**Task 4.2: Fix Cascade Delete**
- Add dataset count check before workspace delete
- Return error if datasets exist

**Task 4.3: Fix Schema Inconsistency**
- Add `archived` column to Project model
- Create Alembic migration
- Remove try/except fallback logic

---

## Code Examples for Fix Implementation

### Example: Adding Auth to Conformance Router

**Before:**
```python
@router.post("/check", response_model=ConformanceResponse)
async def check_conformance(
    request: ConformanceCheckRequest,
    db: DBSession,
    container: ServiceContainer,
):
    # ... implementation
```

**After:**
```python
from src.api.dependencies import CurrentUser
from src.platform.workspaces.authorization import require_dataset_permission
from src.platform.core.permissions import Permission

@router.post("/check", response_model=ConformanceResponse)
async def check_conformance(
    request: ConformanceCheckRequest,
    db: DBSession,
    user: CurrentUser,  # ADDED
    container: ServiceContainer,
):
    # ADDED: Permission check
    await require_dataset_permission(
        db, request.dataset_id, user, Permission.DATASET_READ
    )
    # ... rest of implementation
```

### Example: Adding Decorator to Organizational Router

**Before:**
```python
async def get_handover_network(
    dataset_id: str, db: DBSession, container: ServiceContainer
) -> SocialNetworkResponse:
    # ... implementation
```

**After:**
```python
@router.get("/datasets/{dataset_id}/handover-network", response_model=SocialNetworkResponse)
async def get_handover_network(
    dataset_id: str,
    db: DBSession,
    user: CurrentUser,  # ADDED
    container: ServiceContainer,
) -> SocialNetworkResponse:
    # ADDED: Permission check
    await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
    # ... rest of implementation
```

---

## Testing Notes

### MVP Test Credentials
- Email: `analyst@example.com`
- Password: `password123`
- User ID: `mvp-user-001`
- Org ID: `mvp-org-001`
- Workspace ID: `mvp-ws-001`
- Project ID: `mvp-proj-001`

### Security Test Cases to Add
1. Unauthenticated access to each fixed endpoint -> Should return 401
2. Authenticated access without dataset permission -> Should return 403
3. Authenticated access with permission -> Should succeed

### Health Check
```bash
curl http://localhost:8001/health/live
curl http://localhost:8001/health/ready
```

### Get Token
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"password123"}'
```

---

## Architecture Notes

### Error Handling Pattern
All endpoints should use `AppException` from `src.platform.core.exceptions`:
```python
from src.platform.core.exceptions import AppException, ErrorCode

raise AppException(
    message="Resource not found",
    error_code=ErrorCode.RESOURCE_NOT_FOUND,
    status_code=404,
    details={"resource_id": id}
)
```

### Logging Pattern
Use structured logging with `get_logger`:
```python
from src.platform.core.logging_config import get_logger
logger = get_logger(__name__)

logger.info("operation_completed", resource_id=id, duration_ms=elapsed)
logger.error("operation_failed", error=str(e), exc_info=True)
```

### Authorization Pattern
```python
from src.platform.workspaces.authorization import require_dataset_permission
from src.platform.core.permissions import Permission

await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
```

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-07 | Initial document, fixed email validation | Claude |
| 2026-01-07 | Complete API review with bugs and observations | Claude |
| 2026-01-07 | Deep domain analysis - identified 30+ unauthenticated endpoints | API Stabilization Agent |
| 2026-01-07 | **Deep functional analysis** - state machines, data integrity, error handling | API Stabilization Agent |

---

## Handoff Summary for Implementation Agent

### MVP-Critical Functional Bugs (Fix First)

| Bug | What's Broken | Quick Fix |
|-----|---------------|-----------|
| **FN-001** | Invited users can't log in | Add temp password + force reset |
| **FN-002** | Workspace delete = data loss | Add dataset count check |
| **FN-003** | Variants always show 0 | Query `ProcessCase.variant_key` |

### Features That Don't Work (Dead Code)

| Router | Problem | Fix |
|--------|---------|-----|
| `organizational/router.py` | 5 functions have no `@router.get` | Add decorators |
| `simulation/router.py` | 3 functions have no decorators | Add decorators |

### State Machine Issues

| Issue | Impact | Fix |
|-------|--------|-----|
| No `VALIDATING` status set | Status jumps | Set status in validation workflow |
| Stuck in `INGESTING` on failure | Dataset unusable | Add error handler to rollback |
| Re-ingest doesn't clear events | Duplicates | Clear events before re-ingest |

---

## Handoff Checklist

- [x] All 18+ routers analyzed for auth/authz
- [x] Security issues documented (P4 per user - defer)
- [x] **Functional bugs identified with code locations**
- [x] **State machine violations documented**
- [x] **Data integrity issues documented**
- [x] **Error handling gaps identified**
- [x] Implementation roadmap with code examples
- [x] Testing notes for verification
- [ ] **READY FOR IMPLEMENTATION AGENT**

---

## Quick Reference: Files to Fix

### P0 Functional (MVP Blocking)
1. `src/platform/users/api/organizations.py:302-311` - passwordless invite
2. `src/platform/users/api/workspaces.py:314` - cascade delete
3. `src/features/process_mining/statistics/router.py:73,462` - total_variants=0

### P1 Dead Code
4. `src/features/process_mining/organizational/router.py:60-138` - add decorators
5. `src/features/process_mining/simulation/router.py:59-179` - add decorators

### P2 Data Integrity
6. `src/features/process_mining/datasets/api/mapping.py:224-232` - dual mapping storage
7. `src/platform/temporal/compat.py:153` - workflow args
