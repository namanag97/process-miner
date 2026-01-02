# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,observability]"  # or just ".[dev]"

# Run server (port 8001)
uvicorn src.api.main:app --reload --port 8001

# Endpoints: /docs (Swagger), /redoc, /health, /metrics

# Quality checks
make check          # All checks (lint, format, typecheck, security)
make test           # Run tests
make test-cov       # Tests with coverage

# SDK (requires server running)
cd sdk && npm run generate && npm run build
```

## Architecture

Process mining backend wrapping PM4Py. Simplified clean architecture with minimal abstractions.

**Core Structure:**

- `src/api/routers/` - 17 FastAPI routers
- `src/services/` - 16 PM4Py wrapper services
- `src/models/orm.py` - SQLAlchemy ORM with enterprise hierarchy
- `src/models/schemas.py` - Pydantic request/response models
- `src/core/` - config, exceptions, logging, middleware
- `sdk/` - TypeScript SDK (auto-generated from OpenAPI)

**17 Routers:**
auth, workspaces, projects, datasets, analyses, discovery, visualization, conformance, analytics, filtering, organizational, predictions, simulation, ocpm, workflows, health, dev_log

**DB Tables (Enterprise Hierarchy):**
organizations, workspaces, users, workspace_members, projects, datasets, uploaded_files, analyses, async_jobs, process_models, conformance_results, ocel_logs, ocel_object_types, oc_petri_nets

## Patterns

**Error handling:** Raise `AppException` subclasses (`NotFoundError`, `ValidationError`)

```python
raise NotFoundError("Event log", log_id)
```

**Database:** Async SQLAlchemy via `get_db` dependency

```python
@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    return await db.execute(select(Model)).scalars().all()
```

**Logging:** Structlog in all routers/services

```python
logger = structlog.get_logger(__name__)
logger.info("event_log_uploaded", log_id=log_id, filename=file.filename)
```

**Services:** Instantiate directly or inject

```python
from src.services.mining import MiningService
model = MiningService().discover_model(log, miner_type="alpha")
```

## Config (.env)

```env
DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///./data/db/process_mining.db
AUTH_ENABLED=false
LOG_LEVEL=INFO
LOG_JSON=false  # true for prod (JSON), false for dev (colored console)
```

## Adding Features

**New endpoint:**

1. Add Pydantic schema to `src/models/schemas.py`
2. Add route in appropriate router
3. Use service layer for PM4Py logic
4. Raise `AppException` for errors

**New service:**
Create in `src/services/`, wrap PM4Py functionality

**Regenerate SDK (v2.0+):**
Backend must be running on 8001, then: `cd sdk && npm install && npm run generate && npm run build`

The SDK uses @openapitools/openapi-generator-cli to generate TypeScript clients from OpenAPI spec. See `sdk/package.json` for the generate script configuration.

**Logging:**
Add structlog to new code with timing for expensive operations:

```python
start = time.time()
result = await operation()
logger.info("op_done", duration=time.time()-start)
```

## Process Mining

**PM4Py Algorithms:** Alpha, Inductive, Heuristics miners | Token Replay, Alignments | OCEL 2.0

**Event Log Format:** Case ID, Activity, Timestamp, Resource (optional) | Formats: CSV, XES

**Variant:** Unique activity sequence (e.g., A→B→C vs A→C→B)
