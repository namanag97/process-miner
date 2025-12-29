# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup
```bash
# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Running the Application
```bash
# Start development server (default port 8001)
uvicorn src.api.main:app --reload --port 8001

# Access points:
# - API docs: http://localhost:8001/docs
# - ReDoc: http://localhost:8001/redoc
# - Health: http://localhost:8001/health
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v
```

### Code Quality
```bash
# Format code
ruff format src/

# Lint and auto-fix
ruff check src/ --fix

# Type checking
mypy src/
```

### TypeScript SDK
```bash
# Generate TypeScript SDK from OpenAPI schema
# (requires backend running on http://localhost:8001)
cd sdk
npm install
npm run generate  # Generates client from OpenAPI
npm run build     # Builds the SDK package

# Install in frontend project
npm install @process-mining-saas/sdk
```

## Architecture Overview

This is a **clean, simplified** process mining backend with minimal abstractions.

### Project Structure

```
src/
├── api/                    # FastAPI application
│   ├── main.py             # Entry point, app factory with logging
│   ├── dependencies.py     # Dependency injection
│   └── routers/            # 6 API routers (all with structured logging)
│       ├── processes.py    # Upload, CRUD, stats, cases, variants
│       ├── discovery.py    # Mining algorithms, models CRUD
│       ├── visualization.py# DFG, Petri net, SVG, footprints
│       ├── conformance.py  # Token replay, alignments, diagnostics
│       ├── ocpm.py         # OCEL 2.0 support
│       └── workflows.py    # Pipeline automation
├── services/               # 5 business logic services (with timing logs)
│   ├── ingestion.py        # CSV/XES parsing
│   ├── mining.py           # PM4Py wrapper
│   ├── conformance.py      # Conformance checking
│   ├── ocpm.py             # Object-centric PM
│   └── workflow.py         # Pipeline execution
├── models/
│   ├── orm.py              # 10 SQLAlchemy tables
│   ├── schemas.py          # Pydantic request/response models
│   └── database.py         # Async database setup with logging
├── core/
│   ├── config.py           # Pydantic settings (includes log config)
│   ├── enums.py            # MinerType, ModelFormat enums
│   ├── exceptions.py       # AppException hierarchy
│   ├── logging_config.py   # Structlog configuration
│   └── middleware.py       # Request logging middleware
└── storage/
    └── files.py            # File storage utilities

sdk/                        # TypeScript SDK package
├── package.json            # NPM package @process-mining-saas/sdk
├── tsconfig.json           # TypeScript configuration
├── scripts/
│   └── generate.sh         # OpenAPI code generation
├── README.md               # SDK usage documentation
├── FRONTEND_INTEGRATION.md # React integration guide
└── examples/
    ├── react-upload.tsx    # File upload component
    └── react-query-hooks.ts# React Query hooks for all services
```

### Database Schema (10 tables)

```
event_logs          # Uploaded event log metadata
process_cases       # Individual cases/traces
process_events      # Events within cases
process_models      # Discovered models (Petri nets, DFG)
conformance_results # Conformance checking results
workflows           # Pipeline definitions
workflow_runs       # Pipeline execution records
ocel_logs           # Object-centric event logs
ocel_object_types   # Object types in OCEL
oc_petri_nets       # Object-centric Petri nets
```

### API Endpoints (51 total)

| Router | Tag | Endpoints |
|--------|-----|-----------|
| `/api/v1/processes` | Event Logs | Upload, list, get, delete, stats, cases, variants |
| `/api/v1/discovery` | Discovery | List miners, discover model, models CRUD |
| `/api/v1/visualization` | Visualization | DFG, Petri net, SVG export, footprints |
| `/api/v1/conformance` | Conformance | Check conformance, results, diagnostics, deviations |
| `/api/v1/ocpm` | OCPM | OCEL upload, logs, object-types, OC-PN discovery |
| `/api/v1/workflows` | Workflows | Templates, CRUD, run, execution history |

### Configuration

Settings in `src/core/config.py` use Pydantic settings with `.env` file support:

```env
# Application
DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///./data/db/process_mining.db
AUTH_ENABLED=false

# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
LOG_JSON=false              # true for production JSON logs, false for dev console logs
```

All data directories (`./data/db/`, `./data/uploads/`, `./data/models/`) are auto-created on startup.

## Key Coding Conventions

### API Design

1. **Simple error handling**: Raise `AppException` subclasses (NotFoundError, ValidationError, etc.)
2. **Async/Await**: All database operations use async SQLAlchemy
3. **OpenAPI tags**: Each router has a tag for grouping in docs
4. **CORS enabled**: Frontend origins configurable via settings

### Error Handling

```python
from src.core.exceptions import NotFoundError, ValidationError

# Not found
raise NotFoundError("Event log", log_id)

# Validation error
raise ValidationError("Invalid file format")
```

### Database Access

```python
from src.api.dependencies import get_db

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Model))
    return result.scalars().all()
```

### Services Pattern

Services wrap PM4Py functionality and handle business logic:

```python
from src.services.mining import MiningService

mining_service = MiningService()
model = mining_service.discover_model(event_log, miner_type="alpha")
```

### Structured Logging

All routers and services use **structlog** for structured logging:

```python
import structlog

logger = structlog.get_logger(__name__)

# In routers
logger.info("event_log_uploaded", log_id=log_id, filename=file.filename, size=len(content))

# In services with timing
import time
start_time = time.time()
result = await some_operation()
duration = time.time() - start_time
logger.info("operation_completed", operation="some_operation", duration_seconds=duration)
```

**Log output modes:**
- Development (`LOG_JSON=false`): Colored console logs with timestamps
- Production (`LOG_JSON=true`): JSON structured logs for log aggregation

**Middleware logging:**
- All HTTP requests logged with method, path, status, duration
- Database session lifecycle tracked
- Correlation IDs via `asgi-correlation-id`

## Process Mining Domain Knowledge

### PM4Py Integration

This platform wraps **PM4Py** (Python process mining library). Key algorithms:

- **Discovery**: Alpha Miner, Inductive Miner, Heuristics Miner, DFG
- **Conformance**: Token Replay, Alignments, Fitness/Precision
- **OCEL**: Object-Centric Event Logs (OCEL 2.0 format)

### Event Log Structure

Standard process mining format:
- **Case ID**: Unique identifier for process instance
- **Activity**: Activity name (e.g., "Create Order", "Ship Package")
- **Timestamp**: When activity occurred
- **Resource** (optional): Who performed the activity

Supported formats: CSV, XES

### Variants

A **variant** is a unique sequence of activities. Example:
- Variant 1: `A → B → C → D` (60% of cases)
- Variant 2: `A → B → D` (30% of cases)
- Variant 3: `A → C → B → D` (10% of cases)

## TypeScript SDK

The `sdk/` directory contains a fully-typed TypeScript client for frontend integration.

### SDK Features

- **Auto-generated**: Generated from OpenAPI schema via `openapi-typescript-codegen`
- **Type-safe**: Full TypeScript types for all endpoints and models
- **React Query ready**: Pre-built hooks in `examples/react-query-hooks.ts`
- **File uploads**: Multipart form-data support for event log uploads

### SDK Usage Example

```typescript
import { ProcessesService } from '@process-mining-saas/sdk';

// Upload event log
const file = new File([csvContent], 'events.csv');
const formData = new FormData();
formData.append('file', file);

const eventLog = await ProcessesService.uploadEventLog({
  formData: { file }
});

// List event logs
const logs = await ProcessesService.listEventLogs({
  skip: 0,
  limit: 10
});
```

### React Query Integration

Pre-built React Query hooks available in `sdk/examples/react-query-hooks.ts`:

```typescript
import { useEventLogs, useUploadEventLog } from './hooks';

function EventLogsPage() {
  const { data: logs, isLoading } = useEventLogs();
  const uploadMutation = useUploadEventLog();

  const handleUpload = (file: File) => {
    uploadMutation.mutate(file);
  };

  // ... component logic
}
```

See `sdk/FRONTEND_INTEGRATION.md` for complete React integration guide.

## Common Development Tasks

### Adding a New API Endpoint

1. Define Pydantic schemas in `src/models/schemas.py`
2. Add route handler in appropriate router (e.g., `src/api/routers/processes.py`)
3. Use service layer for business logic
4. Raise `AppException` subclasses for errors

### Adding a New Service

1. Create service in `src/services/`
2. Implement methods that wrap PM4Py functionality
3. Inject via dependency or instantiate directly in router

### Extending Process Mining Features

1. Add PM4Py algorithm call in appropriate service
2. Add Pydantic schema for response
3. Create API endpoint in relevant router
4. Add tests

### Regenerating TypeScript SDK

When you add/modify API endpoints:

1. Ensure backend is running on http://localhost:8001
2. Run `cd sdk && npm run generate`
3. Review generated types in `sdk/src/`
4. Update React Query hooks in `sdk/examples/react-query-hooks.ts` if needed
5. Rebuild: `npm run build`

### Adding Logging to New Code

All new routers and services should include structured logging:

```python
import structlog
import time

logger = structlog.get_logger(__name__)

# Router example
@router.post("/items")
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    logger.info("creating_item", item_name=item.name)
    result = await service.create_item(item)
    logger.info("item_created", item_id=result.id)
    return result

# Service with timing
async def expensive_operation(self, data):
    start_time = time.time()
    logger.info("starting_operation", data_size=len(data))

    result = await self._process(data)

    duration = time.time() - start_time
    logger.info("operation_completed", duration_seconds=duration, result_count=len(result))
    return result
```

## Important Files

| Purpose | Location |
|---------|----------|
| Application entry point | `src/api/main.py` |
| Configuration | `src/core/config.py` |
| Logging configuration | `src/core/logging_config.py` |
| Request logging middleware | `src/core/middleware.py` |
| ORM models | `src/models/orm.py` |
| Pydantic schemas | `src/models/schemas.py` |
| API routers | `src/api/routers/*.py` |
| Services | `src/services/*.py` |
| Exceptions | `src/core/exceptions.py` |
| TypeScript SDK | `sdk/` |
| SDK generation script | `sdk/scripts/generate.sh` |
| React Query hooks | `sdk/examples/react-query-hooks.ts` |
| Frontend integration guide | `sdk/FRONTEND_INTEGRATION.md` |
