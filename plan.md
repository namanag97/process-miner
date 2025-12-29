# Implementation Plan: TypeScript SDK + Structlog Logging + Frontend Prep

## Overview

Package the Process Mining API for frontend development through:

1. **TypeScript SDK** - Generate type-safe SDK from OpenAPI spec, published as npm package
2. **Structlog Logging** - Comprehensive JSON logging for production observability
3. **Frontend Preparation** - Documentation and integration guides

**User Preferences:**

- SDK: `openapi-typescript-codegen` in `backend/sdk/` as npm package
- Logging: Structlog with JSON output, all operations logged (requests, services, DB, performance)
- Log levels: DEBUG in dev (colored console), INFO/JSON in production

**Implementation Order:** SDK → Logging Infrastructure → Router/Service Logging → Frontend Docs
**Estimated Time:** 14-18 hours total

---

## Task 1: TypeScript SDK Package (2-3 hours)

### Goal

Generate type-safe TypeScript SDK from OpenAPI spec for frontend consumption.

### Directory Structure

```
backend/sdk/
├── package.json              # NPM config
├── tsconfig.json             # TypeScript config
├── .gitignore
├── README.md                 # SDK documentation
├── FRONTEND_INTEGRATION.md   # Integration guide
├── scripts/generate.sh       # Code generation script
├── examples/
│   ├── react-upload.tsx
│   └── react-query-hooks.ts
└── src/                      # Generated code (gitignored)
```

### Implementation Steps

**1. Create SDK Structure**

```bash
mkdir -p backend/sdk/{scripts,examples}
cd backend/sdk
```

**2. Create Configuration Files**

`package.json`:

```json
{
  "name": "@process-mining-saas/sdk",
  "version": "0.1.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "generate": "bash scripts/generate.sh",
    "build": "tsc",
    "clean": "rm -rf dist src .openapi-generator",
    "prebuild": "npm run clean && npm run generate"
  },
  "devDependencies": {
    "openapi-typescript-codegen": "^0.27.0",
    "typescript": "^5.3.0"
  },
  "dependencies": {
    "axios": "^1.6.0"
  }
}
```

`tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "declaration": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true
  }
}
```

`scripts/generate.sh` (chmod +x):

```bash
#!/bin/bash
set -e
API_URL="http://localhost:8001"
curl -s "${API_URL}/openapi.json" -o openapi.json
npx openapi-typescript-codegen \
    --input openapi.json \
    --output ./src \
    --client axios \
    --useOptions \
    --useUnionTypes
rm openapi.json
```

`.gitignore`:

```
node_modules/
dist/
src/
.openapi-generator/
openapi.json
```

**3. Install & Generate**

```bash
npm install
# Start backend: uvicorn src.api.main:app --reload --port 8001
npm run generate
npm run build
```

**4. Create Documentation**

- `README.md` - SDK usage, installation, examples
- `FRONTEND_INTEGRATION.md` - React patterns, React Query integration, error handling
- `examples/react-upload.tsx` - File upload component
- `examples/react-query-hooks.ts` - React Query hooks for all services

**5. Test SDK**

```bash
# Local test
npm link
# Verify dist/ contains: index.js, index.d.ts, models/, services/
```

### Success Criteria

- ✅ SDK generates successfully from OpenAPI spec
- ✅ 6 service classes exported (Processes, Discovery, Visualization, Conformance, OCPM, Workflows)
- ✅ 42+ TypeScript interfaces from Pydantic schemas
- ✅ `npm run build` compiles without errors
- ✅ Documentation complete with examples

---

## Task 2: Structlog Logging Infrastructure (3-4 hours)

### Goal

Set up comprehensive structured logging with JSON output for production.

### Dependencies to Install

```bash
pip install structlog python-json-logger asgi-correlation-id
```

### New Files to Create

**1. `src/core/logging_config.py`** - Core logging setup

- Dual output: colored console (dev), JSON (prod)
- Context processors: app name, version, timestamp, request_id
- Log level configuration from settings
- Third-party library noise reduction

Key functions:

- `configure_logging()` - Initialize structlog
- `get_logger(name: str)` - Get logger instance
- `add_app_context()` - Add app metadata to logs

**2. `src/core/middleware.py`** - Request tracking middleware

Two middleware classes:

- `RequestLoggingMiddleware`:

  - Generate/capture request_id from header
  - Bind request context (method, path, client_ip) to all logs
  - Log request start and completion with timing
  - Add request_id to response headers

- `PerformanceLoggingMiddleware`:
  - Warn on slow requests (>1s)
  - Track duration_ms for all requests

### Files to Modify

**1. `src/api/main.py`**

```python
# Add imports
from src.core.logging_config import configure_logging, get_logger
from src.core.middleware import RequestLoggingMiddleware, PerformanceLoggingMiddleware

# After settings initialization
configure_logging()
logger = get_logger(__name__)

# In create_app(), after CORSMiddleware
app.add_middleware(PerformanceLoggingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Update lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_starting", debug=settings.debug)
    await init_database()
    logger.info("database_initialized")
    yield
    logger.info("application_shutting_down")
    await close_database()
    logger.info("database_closed")

# Update exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.warning("application_exception",
                   exception_type=type(exc).__name__,
                   message=exc.message,
                   status_code=exc.status_code)
    return JSONResponse(...)
```

**2. `src/models/database.py`**

- Add logging to `get_session()`: log session start, commit, rollback, errors
- Add logging to `init_database()`: log initialization steps
- Optional: SQLAlchemy event listeners for query logging (DEBUG level)

**3. `src/core/config.py`**
Add settings:

```python
log_level: str = "DEBUG"
log_json: bool = False  # Force JSON even in dev
```

### Testing

```bash
# Dev mode (colored console)
uvicorn src.api.main:app --reload --port 8001
curl http://localhost:8001/health

# Prod mode (JSON output)
LOG_JSON=true uvicorn src.api.main:app --port 8001
```

### Success Criteria

- ✅ All requests logged with request_id, method, path, status, duration_ms
- ✅ Startup/shutdown events logged
- ✅ Dev: colored console output
- ✅ Prod: valid JSON output
- ✅ Slow requests (>1s) trigger warnings

---

## Task 3: Router Logging (4-5 hours)

### Goal

Add comprehensive logging to all API endpoints.

### Pattern to Follow

Example for `src/api/routers/processes.py`:

```python
from src.core.logging_config import get_logger
import time

logger = get_logger(__name__)

@router.post("/upload", response_model=ProcessResponse)
async def upload_process(...):
    """Upload and ingest an event log file."""
    logger.info("upload_started", filename=file.filename, name=name)

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    logger.info("file_read", size_mb=round(file_size_mb, 2))

    try:
        start_time = time.time()
        event_log = await ingestion_service.ingest_file(...)
        duration_ms = (time.time() - start_time) * 1000

        logger.info("upload_completed",
                    log_id=event_log.id,
                    total_events=event_log.total_events,
                    duration_ms=round(duration_ms, 2))
        return ProcessResponse(...)

    except ValidationError as e:
        logger.warning("upload_validation_error", error=e.message)
        raise HTTPException(...)
    except Exception as e:
        logger.error("upload_error", error=str(e), exc_info=True)
        raise HTTPException(...)
```

### Files to Modify (in order)

1. **`src/api/routers/processes.py`** (9 endpoints)

   - upload_process, detect_columns, list_processes, get_process
   - delete_process, get_statistics, list_cases, get_variants

2. **`src/api/routers/discovery.py`** (6 endpoints)

   - list_miners, discover_model, list_models, get_model, delete_model

3. **`src/api/routers/visualization.py`** (5 endpoints)

   - generate_dfg, get_petri_net, get_svg, get_dfg_svg, get_footprints

4. **`src/api/routers/conformance.py`** (7 endpoints)

   - check_conformance, list_results, get_result, delete_result
   - get_diagnostics, get_deviations, list_methods

5. **`src/api/routers/ocpm.py`** (14 endpoints)

   - upload_ocel, list_logs, get_log, delete_log, get_object_types
   - get_statistics, discover_ocpn, list_models, etc.

6. **`src/api/routers/workflows.py`** (9 endpoints)
   - list_templates, create_workflow, list_workflows, run_workflow, etc.

### Log Points for Each Endpoint

- **Start**: Log operation intent with key parameters
- **Validation**: Log validation failures
- **Service call**: Log before calling service layer
- **Completion**: Log result summary with timing
- **Errors**: Log with error type and full context

### Success Criteria

- ✅ All 50+ endpoints log operations
- ✅ Each log includes relevant context (IDs, filenames, counts)
- ✅ Errors logged before raising exceptions
- ✅ Performance timing on expensive operations

---

## Task 4: Service Logging (3-4 hours)

### Goal

Add logging to business logic services.

### Pattern to Follow

Example for `src/services/mining.py`:

```python
from src.core.logging_config import get_logger
import time

logger = get_logger(__name__)

def discover(self, event_log: EventLog, miner_type: MinerType):
    """Discover a process model from an event log."""
    logger.info("discovery_started",
                log_id=event_log.id,
                miner_type=miner_type.value,
                total_cases=event_log.total_cases)

    start_time = time.time()
    pm4py_log = self._to_pm4py_log(event_log)
    conversion_ms = (time.time() - start_time) * 1000

    logger.debug("pm4py_conversion_complete",
                 duration_ms=round(conversion_ms, 2))

    start_time = time.time()
    # ... mining logic
    mining_ms = (time.time() - start_time) * 1000

    logger.info("discovery_completed",
                miner_type=miner_type.value,
                mining_duration_ms=round(mining_ms, 2))
    return result
```

### Files to Modify (in order)

1. **`src/services/ingestion.py`**

   - `ingest_file()` - Log file processing start/completion
   - `_ingest_csv()` - Log parsing progress, row counts
   - `_ingest_xes()` - Log XES parsing
   - `_parse_timestamp()` - Log failed parse attempts (DEBUG)

2. **`src/services/mining.py`**

   - `discover()` - Log algorithm execution with timing
   - `evaluate_fitness()` - Log evaluation metrics
   - `evaluate_precision()` - Log precision calculation
   - `_to_pm4py_log()` - Log conversion (DEBUG)

3. **`src/services/conformance.py`**

   - `check_conformance()` - Log conformance checking start/completion
   - `detect_deviations()` - Log deviation detection
   - Performance timing for long operations

4. **`src/services/ocpm.py`**

   - `ingest_ocel()` - Log OCEL processing
   - `discover_oc_petri_net()` - Log OC-PN discovery
   - Object type extraction logging

5. **`src/services/workflow.py`**
   - `execute_workflow()` - Log workflow execution
   - `_run_step()` - Log each step execution

### Log Levels Strategy

- **DEBUG**: DB queries, conversions, internal operations
- **INFO**: Service operations, results, normal flow
- **WARNING**: Validation errors, potential issues
- **ERROR**: Failures, exceptions

### Success Criteria

- ✅ All 5 services log major operations
- ✅ Long-running operations logged with timing
- ✅ PM4Py algorithm calls tracked
- ✅ Errors logged with context

---

## Task 5: Frontend Documentation (2 hours)

### Goal

Create comprehensive frontend integration documentation.

### Files to Create

**1. `backend/sdk/FRONTEND_INTEGRATION.md`** (Primary reference)

Sections:

- Quick Start (Installation, Configuration)
- Common Patterns (React Hooks, File Upload, Error Handling)
- React Query Integration (recommended approach)
- Environment Setup (.env files, Vite config)
- Type Safety Examples (enum usage, response types)
- Testing Strategies
- Common Issues & Solutions (CORS, request IDs, type mismatches)
- Best Practices

**2. `backend/sdk/examples/react-upload.tsx`**
Complete file upload component with:

- File input handling
- Upload progress
- Error display
- Type-safe SDK usage

**3. `backend/sdk/examples/react-query-hooks.ts`**
React Query hooks for all services:

- `useProcesses()` - Fetch processes list
- `useProcess(id)` - Fetch single process
- `useUploadProcess()` - Upload mutation
- `useDiscoverModel()` - Discovery mutation
- Proper cache invalidation patterns

**4. `.env.example` for frontend**

```env
VITE_API_URL=http://localhost:8001
VITE_API_VERSION=v1
VITE_DEBUG_API=true
```

**5. Update `backend/sdk/README.md`**
Add examples section linking to integration guide.

### Success Criteria

- ✅ Complete integration guide with all patterns
- ✅ Working React examples
- ✅ React Query integration documented
- ✅ Error handling patterns shown
- ✅ Type safety benefits explained

---

## Critical Files Reference

### SDK Files (New)

- `/Users/namanagarwal/system/backend/sdk/package.json`
- `/Users/namanagarwal/system/backend/sdk/tsconfig.json`
- `/Users/namanagarwal/system/backend/sdk/scripts/generate.sh`
- `/Users/namanagarwal/system/backend/sdk/README.md`
- `/Users/namanagarwal/system/backend/sdk/FRONTEND_INTEGRATION.md`
- `/Users/namanagarwal/system/backend/sdk/examples/react-upload.tsx`
- `/Users/namanagarwal/system/backend/sdk/examples/react-query-hooks.ts`

### Logging Files (New)

- `/Users/namanagarwal/system/backend/src/core/logging_config.py`
- `/Users/namanagarwal/system/backend/src/core/middleware.py`

### Backend Files to Modify

- `/Users/namanagarwal/system/backend/src/api/main.py`
- `/Users/namanagarwal/system/backend/src/models/database.py`
- `/Users/namanagarwal/system/backend/src/core/config.py`
- `/Users/namanagarwal/system/backend/src/api/routers/processes.py`
- `/Users/namanagarwal/system/backend/src/api/routers/discovery.py`
- `/Users/namanagarwal/system/backend/src/api/routers/visualization.py`
- `/Users/namanagarwal/system/backend/src/api/routers/conformance.py`
- `/Users/namanagarwal/system/backend/src/api/routers/ocpm.py`
- `/Users/namanagarwal/system/backend/src/api/routers/workflows.py`
- `/Users/namanagarwal/system/backend/src/services/ingestion.py`
- `/Users/namanagarwal/system/backend/src/services/mining.py`
- `/Users/namanagarwal/system/backend/src/services/conformance.py`
- `/Users/namanagarwal/system/backend/src/services/ocpm.py`
- `/Users/namanagarwal/system/backend/src/services/workflow.py`

---

## Final Verification

### SDK

```bash
cd backend/sdk
npm run generate && npm run build
ls -la dist/  # Verify output
npm link  # Test local linking
```

### Logging

```bash
# Dev mode
uvicorn src.api.main:app --reload --port 8001
curl http://localhost:8001/api/v1/processes

# Verify logs show:
# - Colored console output
# - request_id in every log
# - request_started → request_completed
# - duration_ms timing

# Prod mode
LOG_JSON=true uvicorn src.api.main:app --port 8001
# Verify JSON format
```

### Integration Test

```bash
# Upload test file and check logs
curl -X POST http://localhost:8001/api/v1/processes/upload \
  -F "file=@sample.csv" \
  -F "name=Test"

# Should see complete log chain:
# request_started → upload_started → file_read →
# discovery_started → db_session_committed →
# upload_completed → request_completed
```

---

## Success Criteria Summary

**SDK Package:**

- [x] Generated from OpenAPI spec
- [x] 6 service classes with full type safety
- [x] Build & publish workflow documented
- [x] Frontend integration guide complete

**Logging:**

- [x] All requests logged with timing
- [x] All 6 routers log operations
- [x] All 5 services log operations
- [x] Dev: colored console, Prod: JSON
- [x] Request IDs throughout

**Frontend Prep:**

- [x] Integration guide with React examples
- [x] React Query patterns documented
- [x] Type safety examples shown
- [x] Error handling patterns provided

**Ready for Frontend Development!**
