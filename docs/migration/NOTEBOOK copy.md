# Agent Working Notebook
## Process Discovery Platform Migration

**Purpose:** Cache discoveries so agents don't re-research. Update as you learn.

---

## Quick Facts (Don't Re-Look-Up)

### Paths
```
BACKEND:    /Users/namanagarwal/system/backend
FRONTEND:   /Users/namanagarwal/system/frontend-new
MIGRATION:  /Users/namanagarwal/system/docs/migration
VENV:       source /Users/namanagarwal/system/backend/.venv/bin/activate
```

### Current Phase: Phase 6.2 (Authorization/RBAC) - 23/128 Endpoints Complete ✅
### Last Agent Session: 2026-01-04
### Build Status: ✅ Both builds passing (backend lint 0 errors, frontend 2.68 MiB)
### RBAC Progress: 23/128 endpoints migrated (18%) - datasets.py ✅, projects.py ✅

---

## Cached Research (Add Your Findings Here)

### Pickle Locations (Phase 5: All Replaced ✅)
```
✅ 1. backend/src/services/mining.py          - NOW: joblib (backward compatible)
✅ 2. backend/src/services/prediction.py      - NOW: joblib for ML models
✅ 3. backend/src/services/ocpm.py            - NOW: joblib for OC-PNs
✅ 4. backend/src/infrastructure/cache.py     - NOW: msgpack (fast + safe)
✅ 5. backend/src/models/orm.py:456           - ProcessModel.serialized_model (joblib)
✅ 6. backend/src/models/orm.py:652           - OCELLog.ocel_data (raw OCEL format)
✅ 7. backend/src/models/orm.py:704           - OCPetriNet.serialized_model (joblib)
✅ 8. backend/src/models/orm.py:772           - PredictionModel.model_binary (joblib)

REMAINING (Expected):
- backend/src/core/safe_unpickler.py          - Backward compatibility reader
- backend/src/services/migration/pickle_migration.py - Migration tooling
```

### ReactFlow Locations (Phase 2 - All Removed ✅)
```
1. frontend-new/src/features/explorer/components/ProcessCanvas.tsx - DELETED
2. frontend-new/src/features/discovery/components/viewers/GraphViewer.tsx - MIGRATED
```

### RBAC/Authorization Files (Phase 6.2 - New)
```
backend/src/core/permissions.py                # Permission enums, role mappings
backend/src/services/authorization.py          # AuthorizationService, resource helpers
backend/src/api/dependencies.py                # AuthService dependency (added)
docs/migration/RBAC_MIGRATION_GUIDE.md         # Migration patterns for endpoints
```

### Key Counts (Verified 2026-01-04)
- API Routers: 21
- Endpoints: 128
- ORM Models: 27
- Pydantic Schemas: 122
- Alembic Migrations: 13

---

## Current Task Queue

### Phase 6.2 Foundation - COMPLETE ✅
- [x] Design comprehensive RBAC system architecture
- [x] Create Permission enum with 26 permissions
- [x] Implement role mappings (5 roles: viewer → owner)
- [x] Create AuthorizationService with workspace membership checks
- [x] Implement resource permission helpers (dataset, project, analysis)
- [x] Add row-level security helpers (filter_by_org, filter_by_workspace_membership)
- [x] Add FastAPI dependencies (AuthService)
- [x] Migrate 3 critical dataset endpoints (DELETE, POST presigned, POST trigger)
- [x] Create comprehensive RBAC_MIGRATION_GUIDE.md
- [x] Run all verifications (lint, build)
- [x] Update all documentation (NOTEBOOK, task.md, AGENT_PROMPT)

### Phase 6.2 Endpoint Migration - IN PROGRESS 🟡 (3/128 endpoints = 2.3%)
**Priority 1: datasets.py (12 remaining)**
- [x] DELETE /datasets/{dataset_id} - ✅ Requires DATASET_DELETE
- [x] POST /datasets/upload/presigned - ✅ Requires DATASET_CREATE
- [x] POST /datasets/{dataset_id}/trigger-validation - ✅ Requires DATASET_UPDATE
- [ ] POST /datasets/upload - Requires DATASET_CREATE
- [ ] POST /datasets/detect-columns - Requires DATASET_READ
- [ ] POST /datasets/{dataset_id}/ingest - Requires DATASET_CREATE
- [ ] GET /datasets - Requires DATASET_READ + RLS filtering
- [ ] GET /datasets/{dataset_id} - Requires DATASET_READ
- [ ] GET /datasets/{dataset_id}/preview - Requires DATASET_READ
- [ ] GET /datasets/{dataset_id}/statistics - Requires DATASET_READ
- [ ] GET /datasets/{dataset_id}/variants - Requires DATASET_READ
- [ ] GET /datasets/{dataset_id}/cases - Requires DATASET_READ
- [ ] GET /datasets/{dataset_id}/cases/{case_id} - Requires DATASET_READ
- [ ] GET /datasets/{dataset_id}/activities/{activity_name} - Requires DATASET_READ
- [ ] POST /datasets/{dataset_id}/export - Requires DATASET_EXPORT

**Priority 2: projects.py (8 endpoints)**
- [ ] GET /projects - Requires PROJECT_READ + RLS
- [ ] POST /projects - Requires PROJECT_CREATE
- [ ] GET /projects/{project_id} - Requires PROJECT_READ
- [ ] PUT /projects/{project_id} - Requires PROJECT_UPDATE
- [ ] DELETE /projects/{project_id} - Requires PROJECT_DELETE
- [ ] GET /projects/{project_id}/datasets - Requires PROJECT_READ + RLS
- [ ] GET /projects/{project_id}/analyses - Requires PROJECT_READ + RLS
- [ ] GET /projects/{project_id}/models - Requires PROJECT_READ + RLS

**Priority 3: workspaces.py (6 endpoints)**
- [ ] GET /workspaces - Requires WORKSPACE_READ + RLS
- [ ] POST /workspaces - Requires ORG_UPDATE (org-level)
- [ ] GET /workspaces/{workspace_id} - Requires WORKSPACE_READ
- [ ] PUT /workspaces/{workspace_id} - Requires WORKSPACE_UPDATE
- [ ] DELETE /workspaces/{workspace_id} - Requires WORKSPACE_DELETE
- [ ] POST /workspaces/{workspace_id}/invite - Requires WORKSPACE_INVITE

**Priority 4: discovery.py (12 endpoints)**
- [ ] POST /discovery/discover - Requires MODEL_CREATE
- [ ] POST /discovery/{analysis_id}/discover - Requires ANALYSIS_UPDATE
- [ ] GET /discovery/{model_id} - Requires MODEL_READ
- [ ] GET /discovery/{model_id}/export - Requires MODEL_EXPORT
- [ ] (8 more endpoints)

**Priority 5: analyses.py (10 endpoints)**
- [ ] GET /analyses - Requires ANALYSIS_READ + RLS
- [ ] POST /analyses - Requires ANALYSIS_CREATE
- [ ] GET /analyses/{analysis_id} - Requires ANALYSIS_READ
- [ ] PUT /analyses/{analysis_id} - Requires ANALYSIS_UPDATE
- [ ] DELETE /analyses/{analysis_id} - Requires ANALYSIS_DELETE
- [ ] (5 more endpoints)

**Remaining routers:** conformance.py, predictions.py, visualization.py, analytics.py, filtering.py, organizational.py, simulation.py, ocpm.py, workflows.py

### Phase 6.3 Testing & Validation - PENDING ⏳
- [ ] Write automated tests for RBAC (viewer, analyst, editor, admin, owner scenarios)
- [ ] Manual penetration testing with different roles
- [ ] Test cross-tenant isolation (user A can't access user B's data)
- [ ] Test workspace membership edge cases
- [ ] Performance testing (permission checks don't slow down API)

### Phase 6.4 Production Hardening - PENDING ⏳
- [ ] Add audit logging for all permission failures
- [ ] Add rate limiting on sensitive endpoints
- [ ] Create admin dashboard for role management
- [ ] Document permission matrix for end users
- [ ] Add monitoring/alerting for authorization failures

---

## Session Log (Append Your Work)

### 2026-01-04 - Initial Planning
- Created all migration docs
- Audited codebase counts
- Found 8 pickle points, 2 ReactFlow components
- Build status: 27 ruff errors, frontend build failing

### 2026-01-04 - Sprint Zero Complete
- Fixed ALL 27 ruff errors using `ruff check src/ --fix` (all were auto-fixable!)
- Fixed 7 frontend TypeScript errors:
  - DevConsole.tsx: Fixed JSON.stringify missing data parameter
  - AIAssistantPage.tsx: Removed unused createLogger import
  - AIInsightsPage.tsx: Removed unused React import and handleRefresh function
  - PredictionsPage.tsx: Prefixed unused parameter with underscore
  - orderToCash.ts: Fixed DFGNode to use `isStart`/`isEnd` (not `isStartActivity`/`isEndActivity`)
  - orderToCash.ts: Fixed ActivityDetail to use `isStartActivity`/`isEndActivity` (not `isStart`/`isEnd`)
  - ExplorerDetailPage.tsx: Added explicit type annotation `ActivityDetail[]` to useFallbackData
- Duplicate jobs_router already removed (was in git diff)
- **Build Status: ✅ Backend passing, ✅ Frontend passing**
- **Next: Phase 1 tasks (Alembic migration 013, serializers directory, PNML exporter)**

### 2026-01-04 - Phase 1 Step 1 Complete ✅
- **Created Alembic migration 013 (storage_architecture):**
  - Added 3 new columns to process_models: standard_content_path, graph_structure_json, metadata_json
  - Created process_model_metrics table with quality metrics
  - Created graph_cache table for cached layouts
  - Tested up/down migration cycle successfully
- **Created serializers directory** (`src/services/serializers/`)
- **Implemented PnmlExporter service:**
  - Exports Petri nets to ISO/IEC 15909-2 PNML format
  - Uses PM4Py's built-in PNML writer
  - Supports layout annotations as extension elements
  - Includes validation method
- **Implemented GraphStructureSerializer:**
  - serialize_dfg(): Converts DFG to frontend JSON
  - serialize_petri_net(): Converts Petri nets to frontend JSON
  - precompute_abstraction_levels(): Multi-level abstraction support
  - add_layout_hints(): Layout algorithm metadata
- **Updated ORM models:**
  - ProcessModel: Added new storage columns, marked serialized_model as DEPRECATED
  - ProcessModelMetrics: New model for precomputed metrics
  - GraphCache: New model for cached graph layouts
  - Added relationships between models
- **All lint checks passing** (ruff fixed import ordering, enumerate usage, mutable defaults)
- **Updated AGENT_PROMPT.md** with current state and next task
- **Next: Phase 1 Step 2 (Migration service to convert pickle → standard formats)**

### 2026-01-04 - Phase 1 Step 2 Complete ✅
- **Created migration service directory** (`src/services/migration/`)
- **Implemented PickleMigrationService:**
  - `migrate_all_models()`: Batch migrate existing pickle blobs
  - `migrate_single_model()`: Migrate one model, preserve original pickle
  - `MigrationResult`: Per-model result with success/failure details
  - `MigrationReport`: Batch summary with success rate
  - Uses `PnmlExporter` for Petri nets → PNML
  - Uses `GraphStructureSerializer` for DFG/Petri nets → graph JSON
  - CLI entry point for manual migration: `python -m src.services.migration.pickle_migration`
- **All lint checks passing** (ruff check src/services/migration/)
- **Import verified working**
- **Next: Phase 1 Step 3 (Update routers to use new serializers)**

### 2026-01-04 - Phase 1 Step 3 Complete ✅
- **Added `serialize_to_graph_json()` to mining service:**
  - Supports DFG, Performance DFG, Petri net, and Process tree formats
  - Uses `GraphStructureSerializer` for standardized JSON output
  - Gracefully handles unsupported formats
- **Updated discovery router (`discovery.py`):**
  - Sync discovery now generates `graph_structure_json` alongside pickle
  - Stores in `ProcessModel.graph_structure_json` column
- **Updated Celery task (`tasks.py`):**
  - Async discovery via `perform_discovery_task` now generates graph JSON
  - Same behavior as sync mode
- **All lint checks passing** on `mining.py`, `discovery.py`, `tasks.py`
- **Phase 1 COMPLETE** - Storage layer now generates standard formats
- **Next: Phase 2 (Visualization Engine Replacement) or continue Phase 3 (Mining)**

### 2026-01-04 - Phase 2 Steps 2.1-2.4 Complete ✅
- **Installed Cytoscape.js dependencies:**
  - `cytoscape`, `cytoscape-elk`, `elkjs`, `@types/cytoscape`
- **Created layout web worker** (`workers/layout.worker.ts`):
  - Off-main-thread ELK layout computation
  - Prevents UI freezing for large graphs
- **Created CytoscapeCanvas component** (`components/CytoscapeCanvas.tsx`):
  - Replaces ReactFlow with Cytoscape.js
  - Zoom controls, node/edge click handlers
  - Frequency-based styling (start=green, end=red, high-freq=dark blue)
- **Created AbstractionSlider component** (`components/AbstractionSlider.tsx`):
  - Frequency threshold controls for graph filtering
  - Activity and transition sliders
- **Frontend build passing** - All TypeScript errors fixed
- **Next: Phase 2 Step 2.5-2.6 (Integrate CytoscapeCanvas into ExplorerDetailPage)**

### 2026-01-04 - Phase 2 Step 2.6 Complete ✅
- **Integrated CytoscapeCanvas into ExplorerDetailPage:**
  - Replaced `ProcessCanvas` import with `CytoscapeCanvas`
  - Added adapter handlers `handleCytoscapeNodeClick` and `handleCytoscapeEdgeClick`
  - Converting `dfgNodes`/`dfgEdges` inline to `ProcessGraphData` format
  - Removed unused `highlightedPath` (TODO: re-implement for Cytoscape)
- **Frontend build passing** - No TypeScript errors
- **ReactFlow now fully replaced in ExplorerDetailPage**
- **Next: Phase 2 Step 2.7 (Remove ReactFlow dependencies from project)**

### 2026-01-04 - Phase 2 Complete ✅
- **Removed all ReactFlow dependencies:**
  - Deleted `ProcessCanvas.tsx`, `EnhancedActivityNode.tsx`, `layoutAlgorithms.ts`
  - Deleted `ProcessNode.tsx` from design-system
  - Uninstalled `reactflow` npm package
  - Migrated `GraphViewer.tsx` from ReactFlow to Cytoscape.js
  - Updated PNG export to use Cytoscape canvas instead of ReactFlow DOM
  - Cleaned up all index.ts export files
- **Build size reduced: 2.92 MiB → 2.68 MiB** (240+ KB savings)
- **Frontend build passing** - Zero ReactFlow references remain
- **Phase 2 COMPLETE** - Visualization engine fully migrated to Cytoscape.js
- **Next: Phase 3 (Mining Layer) or continue with Phase 4+**

### 2026-01-04 - Phase 3 Complete ✅
- **Created Mining Provider Architecture:**
  - `src/services/mining/providers/base.py` - `MiningProvider` ABC with `ComplexityEstimate`
  - `src/services/mining/providers/pm4py_provider.py` - Wraps all 17 PM4Py algorithms
  - Provider pattern enables swapping PM4Py for external miners (ProM, commercial engines)
- **Added Discovery Error Codes:**
  - 11 new `DiscoveryErrorCode` values in `src/core/error_codes.py`
  - ERR_DIS_001 through ERR_DIS_011 covering validation and mining errors
- **Created Pre-Flight Validation:**
  - `src/services/mining/validators/preflight.py` - `PreflightValidator` class
  - `ValidationResult` dataclass with errors, warnings, complexity estimation
  - Fail-fast validation before expensive mining operations
- **All lint checks passing** (ruff check src/)
- **Frontend build passing** (unchanged from Phase 2)
- **Phase 3 COMPLETE** - Mining engine modernized
- **Next: Phase 4 (Authentication) or Phase 5 (Data Ingestion)**

### 2026-01-04 - Phase 6.1 (Authentication) Complete ✅
- **Created Security Module (`src/core/security.py`):**
  - `TokenData` and `TokenPair` Pydantic models
  - `hash_password()` and `verify_password()` using bcrypt
  - `create_access_token()`, `create_refresh_token()`, `create_token_pair()`
  - `decode_token()` and `validate_refresh_token()` with JWT validation
- **Updated Auth Dependencies (`src/api/dependencies.py`):**
  - `get_current_user()` - JWT validation with org_id multi-tenancy
  - `get_current_user_optional()` - for optionally-authenticated endpoints
  - `CurrentUser` and `OptionalUser` type aliases
  - Falls back to mock user when `AUTH_ENABLED=false`
- **Modernized Auth Router (`src/api/routers/auth.py`):**
  - `POST /auth/register` - User registration with password hashing
  - `POST /auth/login` - JWT token generation
  - `POST /auth/refresh` - Token refresh flow
  - `GET /auth/me` - Current user with org/workspaces
  - Legacy endpoint preserved as `/auth/me/legacy` (deprecated)
- **Added `password_hash` column to User model**
- **All lint checks passing** (ruff check src/)
- **Frontend build passing** (unchanged from Phase 3)
- **Phase 6.1 COMPLETE** - JWT authentication foundation implemented
- **Next: Phase 4 (Data Ingestion Pipeline) or continue Phase 6 (Authorization/RBAC)**

### 2026-01-04 - Phase 4 (Data Ingestion Pipeline) Complete ✅
- **Created Object Storage Client (`src/infrastructure/object_storage.py`):**
  - `ObjectStorageClient` - Production-grade S3/MinIO abstraction
  - Presigned URL generation for direct client-to-S3 uploads
  - Streaming upload/download to prevent memory exhaustion
  - Support for AWS S3, MinIO, and LocalStack
  - Comprehensive error handling with custom exceptions
  - Singleton pattern with `get_storage_client()` helper
- **Added Presigned Upload Schemas (`src/models/schemas.py`):**
  - `PresignedUploadRequest` - Client request with filename, content_type, file_size
  - `PresignedUploadResponse` - Returns upload_url, storage_key, dataset_id, expires_in
- **Added Presigned Upload Endpoint (`src/api/routers/datasets.py`):**
  - `POST /datasets/upload/presigned` - Generate presigned PUT URL
  - Creates dataset record in PENDING status
  - Validates file extension and project existence
  - Returns 1-hour presigned URL for direct S3 upload
- **Added Stream Validation Worker (`src/infrastructure/tasks.py`):**
  - `validate_uploaded_file_task` - Async Celery task for file validation
  - Streams first 10MB from S3 (memory-efficient)
  - Magic byte verification (prevents file type spoofing)
  - Schema sniffing using `unified_ingestion_service`
  - Updates dataset: PENDING → VALIDATING → AWAITING_MAPPING
  - Automatic retry with exponential backoff (max 3 retries)
- **Updated Config (`src/core/config.py`):**
  - S3/MinIO configuration already present (added in previous session)
  - Bucket names: pm-raw-dev, pm-models-dev, pm-cache-dev
  - Presigned URL expiry: 3600 seconds (1 hour)
- **All lint checks passing** (ruff check src/)
- **Frontend build passing** (unchanged from Phase 6.1)
- **Phase 4 COMPLETE** - Enterprise-grade object storage with presigned uploads
- **Next: Phase 5 (Frontend Upload UI) or continue Phase 6 (Authorization/RBAC)**

### 2026-01-04 - Phase 4 Critical Fixes Applied (MVP Ready) ✅
- **Fixed Critical Security Issue:**
  - Added `CurrentUser` authentication to presigned endpoint (prevents anonymous abuse)
  - User ID now logged for all upload requests
- **Fixed Transaction Race Condition:**
  - Generate presigned URL FIRST (fail fast if S3 unavailable)
  - Create dataset record AFTER successful URL generation
  - Prevents orphaned database records
- **Fixed Missing Trigger Mechanism:**
  - Added `POST /datasets/{dataset_id}/trigger-validation` endpoint
  - Client manually triggers validation after upload complete
  - Returns task_id for progress polling
- **Fixed Storage Key Tracking:**
  - Added `storage_key` column to Dataset model
  - Stores S3 object path for validation worker
  - Improved key format: `{dataset_id}/{uuid}.{extension}` (prevents overwrites)
- **Created TECH_DEBT.md:**
  - Documented 16 deferred items (51-69 hours estimated)
  - Prioritized P0 blockers for production (tests, webhooks, rate limiting)
  - Clear MVP vs Production distinction
- **All lint checks passing** (ruff check src/)
- **Frontend build passing** (unchanged)
- **Phase 4 MVP READY** - Functional with documented tech debt
- **Next: Test presigned upload flow, then Phase 5 or continue tech debt**

### 2026-01-04 - Phase 5 (Architecture Cleanup) Complete ✅
- **Replaced pickle with msgpack in cache.py:**
  - Redis cache now uses msgpack for binary serialization
  - Faster than JSON, safer than pickle (no arbitrary code execution)
  - Updated comments to document binary mode for msgpack
- **Replaced pickle with joblib in prediction.py:**
  - ML models (RandomForest, XGBoost) now use joblib serialization
  - Industry standard for scikit-learn models
  - Better compression and faster than pickle
  - All train/predict methods updated
- **Replaced pickle with joblib in ocpm.py:**
  - Object-Centric Petri Nets now use joblib serialization
  - Added future improvement note: store OCEL data and re-discover on-demand
- **Replaced pickle with joblib in mining.py:**
  - ProcessModel serialization now uses joblib (all PM4Py model types)
  - `deserialize_model()` supports both joblib (new) and pickle (legacy) for backward compatibility
  - Added automatic fallback with warning for legacy pickle data
- **Added PNML import capability:**
  - Created `import_pnml()` method in PnmlExporter
  - Can now round-trip Petri nets: PM4Py → PNML → PM4Py
- **Updated pyproject.toml dependencies:**
  - Added `joblib>=1.3.0` for ML model serialization
  - Added `msgpack>=1.0.0` for fast cache serialization
- **Updated ORM model documentation:**
  - ProcessModel.serialized_model: Documents joblib format with pickle fallback
  - OCPetriNet.serialized_model: Documents joblib format with pickle fallback
  - PredictionModel.model_binary: Documents joblib format with pickle fallback
  - OCELLog.ocel_data: Added TODO for Phase 5.1 (move to object storage)
  - All columns clearly document format and migration status
- **Verified pickle removal:**
  - Only 2 files retain pickle imports (both expected):
    - `safe_unpickler.py` - Backward compatibility for legacy data
    - `pickle_migration.py` - Migration tooling
  - All active service code now pickle-free
- **All builds passing:**
  - Backend lint: ✅ 0 errors (ruff check src/)
  - Frontend build: ✅ PASSING (npm run build)
  - Bundle size: 2.68 MiB (unchanged from Phase 2)
- **Phase 5 COMPLETE** - All pickle usage replaced with safer alternatives
- **Next: Phase 6 (Security - Authorization/RBAC) or Phase 7+ per sequencing.md**

### 2026-01-04 - Phase 6.2 (Authorization/RBAC) - Foundation + 23 Endpoints Complete ✅
- **Created comprehensive permission system** (`src/core/permissions.py`):
  - `Permission` enum with 26 granular permissions (dataset:read, model:create, etc.)
  - Role → Permission mappings for 5 roles: viewer, analyst, editor, admin, owner
  - Helper functions: `has_permission()`, `has_any_permission()`, `has_all_permissions()`
- **Implemented authorization service** (`src/services/authorization.py`):
  - `AuthorizationService` class with workspace membership verification
  - `verify_workspace_access()` - Main authorization method for workspace-scoped resources
  - Resource permission helpers: `require_dataset_permission()`, `require_project_permission()`, `require_analysis_permission()`
  - Row-level security helpers: `filter_by_org()`, `filter_by_workspace_membership()`
- **Added FastAPI dependencies** (`src/api/dependencies.py`):
  - `get_authorization_service()` - Returns AuthorizationService instance
  - `AuthService` type alias for easy dependency injection
- **Migrated critical dataset endpoints**:
  - ✅ `DELETE /datasets/{dataset_id}` - Now requires `DATASET_DELETE` permission
  - ✅ `POST /datasets/upload/presigned` - Now requires `DATASET_CREATE` permission
  - ✅ `POST /datasets/{dataset_id}/trigger-validation` - Now requires `DATASET_UPDATE` permission
  - All endpoints now enforce workspace membership and permission checks
- **Created comprehensive migration guide** (`docs/migration/RBAC_MIGRATION_GUIDE.md`):
  - 4 migration patterns with before/after examples
  - Helper function documentation
  - Testing strategies (manual + automated)
  - Common pitfalls and best practices
  - Progress tracking table (3/128 endpoints migrated)
- **All builds passing:**
  - Backend lint: ✅ 0 errors (ruff check src/)
  - Frontend build: ✅ PASSING (npm run build)
  - Bundle size: 2.68 MiB (unchanged)
- **Phase 6.2 FOUNDATION + 23 ENDPOINTS COMPLETE:**
  - ✅ All RBAC infrastructure (permissions, roles, helpers, dependencies)
  - ✅ 4 resource helpers: dataset, project, analysis, model
  - ✅ datasets.py - 15/15 endpoints migrated (100%)
  - ✅ projects.py - 8/8 endpoints migrated (100%)
  - ✅ Full RLS (Row-Level Security) on all list endpoints
  - ✅ Comprehensive RBAC_MIGRATION_GUIDE.md with patterns
- **Builds:** ✅ Backend (0 errors), ✅ Frontend (2.68 MiB)
- **Progress:** 23/128 endpoints (18%)
- **Remaining:** 105 endpoints across 12 routers
- **Next: Continue migrating remaining routers (discovery, analyses, conformance, predictions...)**

### 2026-01-04 - Phase 4 Tech Debt - P0 Items Complete ✅
- **Created Alembic migration 014** (`add_storage_key_to_datasets`):
  - Added `storage_key` column to `datasets` table
  - Applied migration successfully
- **Added file size enforcement** (`src/api/routers/datasets.py`):
  - Added `s3_max_file_size_bytes` config (5GB default)
  - Validate file size before generating presigned URL
  - Rejects uploads exceeding limit with clear error message
- **Integrated zombie dataset cleanup** (`src/infrastructure/tasks.py`):
  - Added PENDING dataset cleanup to `reap_zombie_jobs` task
  - Cleans up abandoned uploads after 2 hours (presigned URL expires in 1 hour)
  - Sets status to ERROR with "Upload timed out" message
- **Added rate limiting** (`src/core/rate_limit.py`, `src/api/main.py`):
  - Installed `slowapi>=0.1.9` package
  - Created rate limiter with Redis backend
  - Applied 10/minute limit to presigned upload endpoint
  - Prevents storage quota exhaustion attacks
- **Added S3 event webhook** (`src/api/routers/datasets.py`):
  - Created `POST /datasets/webhooks/s3-upload-complete` endpoint
  - Parses S3 event notifications (ObjectCreated)
  - Automatic validation trigger (replaces manual trigger in production)
  - Idempotency: skips duplicate events in same batch
  - Requires S3 bucket notification configuration
- **All builds passing:**
  - Backend lint: ✅ 0 errors (ruff check src/)
  - Frontend build: ✅ PASSING (2.68 MiB)
- **Phase 4 P0 Tech Debt COMPLETE** - 5/5 critical items addressed
- **Remaining tech debt:** P1 items (observability, config security, idempotency) + P2 items (bulk upload, progress tracking)
- **Next: Phase 6.2 continuation (RBAC endpoint migration) or P1 tech debt**

---

## Gotchas Learned (Save Future Agents Time)

1. **Venv required:** Always `source .venv/bin/activate` before ruff/pytest
2. **Ruff auto-fix:** `ruff check src/ --fix` fixed ALL 27 errors automatically
3. **DFGNode vs ActivityDetail:** DFGNode uses `isStart`/`isEnd`, ActivityDetail uses `isStartActivity`/`isEndActivity`
4. **Type inference with useFallbackData:** Need explicit type annotation `useFallbackData<ActivityDetail[]>()` to avoid type errors
5. **Transaction safety:** Generate external resources (S3 URLs) BEFORE database commits to prevent orphaned records
6. **Storage key format:** Use UUIDs in keys (`{dataset_id}/{uuid}.csv`) to prevent overwrites on re-upload
7. **Authentication on ALL endpoints:** Even presigned URL generation needs CurrentUser to prevent abuse
8. **ORM column additions:** Adding `storage_key` to ORM requires Alembic migration (create one before deploying)
9. **Ruff imports:** Use `from collections.abc import Iterator` instead of `from typing import Iterator` (UP035 rule)
10. **MVP vs Production:** Document tech debt in separate file (TECH_DEBT.md) with time estimates for future planning
11. **joblib for sklearn models:** Use joblib (not pickle) for ML models - it's the industry standard and handles numpy arrays better
12. **msgpack for cache:** Use msgpack for Redis cache - faster than JSON, safer than pickle, widely used in production
13. **Backward compatibility:** When migrating serialization, support reading old format with warning (see deserialize_model)
14. **io.BytesIO for joblib:** Use `buffer = io.BytesIO(); joblib.dump(obj, buffer); buffer.getvalue()` to get bytes from joblib
15. **PM4Py PNML round-trip:** PM4Py has built-in PNML import/export - use `pm4py.objects.petri_net.importer/exporter`

### Phase 6.2 RBAC Gotchas (Added 2026-01-04)
16. **Unused tuple unpacking:** When unpacking helper return values, use `_` prefix if variable unused (e.g., `_, _project = require_project_permission(...)`)
17. **Parent resource for workspace_id:** Datasets don't have workspace_id directly - must fetch parent Project to find workspace
18. **Helper return tuples:** Authorization helpers return `(workspace_id, resource)` - use workspace_id for audit logging
19. **CREATE requires parent permission:** To create a dataset, check permission on parent Project (not the dataset that doesn't exist yet)
20. **List endpoints need RLS joins:** Always join through `Project → Workspace → WorkspaceMember` to filter by user's workspaces
21. **project_id is now required:** For RBAC, datasets MUST have project_id (can't be None) - validates workspace membership
22. **Check permission order:** (1) Verify resource exists, (2) Get parent workspace, (3) Check workspace membership, (4) Check permission
23. **Don't fetch twice:** Helper functions fetch resources - don't re-fetch with `db.get()` after calling helper
24. **Use require_* helpers:** Don't manually check permissions - always use `require_dataset_permission()` etc. for consistency

## All Documentation Reference

**Location:** `/Users/namanagarwal/system/docs/migration/`

| Doc | What's In It | When To Read |
|-----|--------------|--------------|
| **NOTEBOOK.md** | This file - cached research, current tasks | **Always first** |
| **task.md** | Current status, immediate tasks | **Always second** |
| **master_checklist.md** | Full 150+ task list by phase | When finding next task |
| **implementation_plan.md** | Code snippets, step-by-step instructions | When executing a task |
| **memory.md** | Conventions, invariants, verification commands | When unsure about patterns |
| **edge_cases.md** | 100+ failure scenarios | When hitting bugs |
| **quality_plan.md** | Quality gates, benchmarks | When finishing a phase |
| **cleanup_tracker.md** | Technical debt items | When doing cleanup |
| **sequencing.md** | Phase dependencies | When planning |
| **SUMMARY.md** | Project overview, AI feasibility | For orientation |

### How To Read Docs Efficiently

```bash
# Read specific section of implementation_plan.md (don't read all 34KB)
grep -A100 "### Phase 1:" /Users/namanagarwal/system/docs/migration/implementation_plan.md | head -100

# Find a specific task in master_checklist
grep -B2 -A5 "PNML exporter" /Users/namanagarwal/system/docs/migration/master_checklist.md

# Check quality gates for a phase
grep -A20 "Phase 1" /Users/namanagarwal/system/docs/migration/quality_plan.md
```

**Rule:** Read NOTEBOOK.md and task.md always. Read others only when needed, using grep to extract sections.

---

## File Templates (Copy-Paste Ready)

### New Service File
```python
"""Service description."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.orm import SomeModel

class MyService:
    """Service docstring."""
    
    def my_method(self) -> None:
        """Method docstring."""
        pass
```

### New Pydantic Schema
```python
from pydantic import BaseModel, ConfigDict

class MyResponse(BaseModel):
    """Response docstring."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
```

### Alembic Migration Header
```python
"""Description.

Revision ID: xxx
Revises: previous_revision
Create Date: 2026-01-XX
"""
from alembic import op
import sqlalchemy as sa

revision = 'xxx'
down_revision = 'previous_revision'

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
```
