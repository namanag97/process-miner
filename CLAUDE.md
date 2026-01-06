# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A full-stack **Process Mining SaaS Platform** built with:
- **Backend**: FastAPI (Python 3.10+) with PM4Py for process mining algorithms
- **Frontend**: React 19 + Nx monorepo with Rspack bundling
- **Database**: SQLite (async via aiosqlite) with Alembic migrations
- **Data Processing**: DuckDB for high-performance data ingestion and analytics
- **Storage**: S3/MinIO for event log files
- **Task Queue**: Celery with Redis for async background jobs

## Essential Commands

### Backend Development

```bash
# Start backend dev server (auto-reload on port 8001)
cd backend/src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

# Alternative using Makefile
cd backend && make dev

# Run all quality checks (lint + typecheck + security)
make check

# Run tests
make test
cd backend && .venv/bin/python -m pytest tests/ -v

# Run single test file
cd backend && .venv/bin/python -m pytest tests/api/test_datasets.py -v

# Database migrations
cd backend && .venv/bin/alembic upgrade head        # Apply migrations
cd backend && .venv/bin/alembic revision --autogenerate -m "description"  # Create migration
cd backend && .venv/bin/alembic current             # Check current version
cd backend && .venv/bin/alembic history             # View migration history
```

### Frontend Development

```bash
# Start frontend dev server (port 4200)
cd frontend-new && npm run start

# Build for production
cd frontend-new && npm run build

# Run tests
cd frontend-new && npm run test

# Regenerate API client from OpenAPI spec
cd frontend-new && npm run generate:sdk
```

### Full Stack Development

```bash
# Install all dependencies
make install

# Run full CI suite (lint + typecheck + security + tests)
make all

# Run both backend and frontend
make dev-full
```

## Architecture

### Backend: Domain-Driven Design + Hexagonal Architecture

The backend follows a **layered architecture** with strict dependency rules enforced by `import-linter`:

```
┌─────────────────────────────────────────────────────┐
│  API Layer (src/api/)                               │
│  - FastAPI routers, DTOs, request/response schemas │
│  - Depends on: all layers                           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Domain Layer (src/domains/, src/features/)         │
│  - Business logic, services, schemas                │
│  - Depends on: platform.infrastructure only         │
│  - NEVER depends on: api                            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Platform Layer (src/platform/)                     │
│  - Infrastructure: DB, storage, tasks, cache        │
│  - Core: Auth, config, exceptions, middleware       │
│  - NEVER depends on: features, domains              │
└─────────────────────────────────────────────────────┘
```

**Key Principles:**
- **Domain Independence**: Domain layer (`src/domain`) must be pure - no dependencies on infrastructure or API layers
- **Services Independence**: Services cannot depend on API/presentation layer
- **Platform/Feature Separation**: Platform (generic SaaS infra) NEVER depends on Features (process mining logic)

### Domain Boundaries

The application is organized into three primary domains:

#### 1. **Admin Domain** (`src/domains/admin/`)
Multi-tenant authentication and organization management:
- Organizations (billing plans, usage tracking)
- Workspaces (collaborative containers with RBAC)
- Projects (dataset/analysis organization)
- Users (JWT auth with access/refresh tokens)

**Authorization Hierarchy:**
```
Organization (owner)
  └── Workspace (owner/admin/editor/viewer)
        └── Project (inherits workspace permissions)
              └── Dataset (inherits project permissions)
```

#### 2. **Datasets Domain** (`src/domains/datasets/`)
Complete data lifecycle for event logs:
- File upload (direct + presigned S3 URLs)
- Column detection (automatic schema inference)
- Column mapping (user-defined process semantics)
- DuckDB-based ingestion pipeline
- Metadata computation and storage

**Dataset Status Flow:**
```
PENDING → UPLOADING → UPLOADED → MAPPING → MAPPED → INGESTING → READY
                                                         ↓
                                                    FAILED/ERROR
```

#### 3. **Analysis Domain** (`src/domains/analysis/`)
All process mining and analytics capabilities:
- **Discovery**: Alpha, Inductive, Heuristics, Split miners
- **Conformance**: Token replay, alignments, footprint comparison
- **Analytics**: Bottlenecks, cycle times, throughput, wait times
- **Visualization**: DFG, Petri nets, BPMN layouts
- **Predictions**: ML-based next activity and remaining time
- **Organizational**: Social network analysis, resource handovers
- **Simulation**: What-if analysis
- **OCPM**: Object-Centric Process Mining (OCEL 2.0)

### Backend Code Organization

```
backend/src/
├── api/                      # FastAPI application entry point
│   ├── main.py              # App factory, middleware, exception handlers
│   └── routers/             # API route definitions
├── domains/                  # NEW: Domain-driven design structure
│   ├── admin/               # Authentication, organizations, workspaces
│   ├── datasets/            # Event log upload, ingestion, storage
│   └── analysis/            # Process mining algorithms and analytics
├── features/                 # LEGACY: Being migrated to domains/
│   └── process_mining/      # Original process mining features
├── platform/                 # Generic SaaS infrastructure
│   ├── core/                # Config, exceptions, security, middleware
│   ├── infrastructure/      # DB, storage, tasks, cache, resilience
│   ├── auth/                # JWT authentication
│   ├── organizations/       # Multi-tenant org management
│   ├── workspaces/          # Workspace RBAC
│   ├── projects/            # Project management
│   ├── jobs/                # Unified async job tracking
│   └── health/              # Health checks for k8s
└── shared/                   # Shared utilities, types, constants
```

### Frontend: Nx Monorepo with Domain-Driven Structure

```
frontend-new/
├── apps/
│   └── frontend-new/        # Main React application
│       └── src/
│           ├── domains/     # Feature modules by domain
│           │   ├── datasets/       # Event log management UI
│           │   ├── discovery/      # Process discovery UI
│           │   ├── analytics/      # Analytics dashboards
│           │   └── projects/       # Project management UI
│           ├── core/        # Shared core functionality
│           └── App.tsx
└── libs/
    ├── openapi-sdk/         # Auto-generated TypeScript API client
    ├── ui/                  # Shared UI components (Ant Design)
    └── process-graph/       # Process visualization (Cytoscape)
```

**Frontend Tech Stack:**
- React 19 with React Router v6
- Ant Design for UI components
- TanStack Query for API state management
- Cytoscape for process graph visualization
- Nx for monorepo tooling, Rspack for fast builds

## Database Schema

**Key Tables:**
- `organizations`: Multi-tenant root entities
- `workspaces`: Collaborative work contexts
- `workspace_members`: Many-to-many with RBAC roles
- `projects`: Organizational containers
- `datasets`: Event log metadata and status
- `dataset_columns`: Detected schema from uploads
- `dataset_column_mappings`: User-defined process semantics
- `process_cases`: Trace/case representations
- `process_events`: Individual events in traces
- `process_models`: Discovered models (Petri nets, BPMN)
- `analyses`: Stored analysis results
- `jobs`: Async background job tracking

**Migration Workflow:**
```bash
# Create new migration after modifying models
cd backend && .venv/bin/alembic revision --autogenerate -m "add new field"

# Review generated migration in alembic/versions/
# Apply migration
cd backend && .venv/bin/alembic upgrade head

# Rollback one migration
cd backend && .venv/bin/alembic downgrade -1
```

## Testing Strategy

### Backend Tests (`backend/tests/`)
- **Framework**: pytest with pytest-asyncio for async support
- **Test Organization**: Mirrors `src/` structure
- **Fixtures**: `conftest.py` files provide shared test fixtures
- **Coverage**: Use `make test-cov` for coverage reports

**Test Categories:**
```python
tests/
├── api/              # API endpoint tests (integration)
├── domain/           # Domain logic tests (unit)
├── services/         # Service layer tests (unit + integration)
└── conftest.py       # Global fixtures (test client, test DB)
```

**Running Tests:**
```bash
# All tests
cd backend && .venv/bin/python -m pytest tests/ -v

# Specific test file
cd backend && .venv/bin/python -m pytest tests/api/test_datasets.py -v

# Specific test function
cd backend && .venv/bin/python -m pytest tests/api/test_datasets.py::test_upload_dataset -v

# With coverage
cd backend && .venv/bin/python -m pytest tests/ --cov=src --cov-report=html
```

### Frontend Tests (`frontend-new/`)
- **Framework**: Jest with React Testing Library
- **Run**: `cd frontend-new && npm run test`

## API Documentation

- **Swagger UI**: http://localhost:8001/docs (interactive API testing)
- **ReDoc**: http://localhost:8001/redoc (clean documentation)
- **OpenAPI Spec**: http://localhost:8001/openapi.json

**Key Endpoints:**
- `/api/v1/auth/login` - JWT authentication
- `/api/v1/datasets/` - Event log upload and management
- `/api/v1/discovery/discover` - Process model discovery
- `/api/v1/analytics/bottlenecks` - Performance analytics
- `/health/live` - Liveness probe (k8s)
- `/health/ready` - Readiness probe (k8s)

## Code Quality Standards

### Python (Backend)

**Linting & Formatting:**
- **Ruff**: Fast linter and formatter (replaces Black, isort, flake8)
- **Configuration**: `backend/pyproject.toml`
- **Auto-fix**: `cd backend && .venv/bin/python -m ruff check src/ tests/ --fix`

**Type Checking:**
- **mypy**: Static type checker
- **Run**: `cd backend && .venv/bin/python -m mypy src/`
- **Note**: Process mining feature modules have relaxed rules due to PM4Py's dynamic nature

**Security:**
- **Bandit**: Security vulnerability scanner
- **Run**: `cd backend && .venv/bin/python -m bandit -r src/`

**Import Linting:**
- **import-linter**: Enforces architectural boundaries
- **Run**: `cd backend && .venv/bin/lint-imports`
- **Config**: `[tool.importlinter]` in `backend/pyproject.toml`

### TypeScript (Frontend)

**Linting:**
- **ESLint**: TypeScript and React linting
- **Run**: `cd frontend-new && npx nx lint`

**Type Checking:**
- **TypeScript**: Strict type checking
- **Run**: `cd frontend-new && npx nx typecheck`

## Development Workflows

### Adding a New API Endpoint

1. Define schema in `src/domains/{domain}/schemas/`
2. Add model if needed in `src/domains/{domain}/models/`
3. Create service logic in `src/domains/{domain}/services/`
4. Add router endpoint in `src/domains/{domain}/api/`
5. Register router in `src/api/main.py`
6. Write tests in `backend/tests/api/`
7. Regenerate frontend SDK: `cd frontend-new && npm run generate:sdk`

### Adding a New Process Mining Algorithm

1. Implement in `src/domains/analysis/services/{category}/`
2. Add schemas to `src/domains/analysis/schemas/`
3. Expose via `src/domains/analysis/api/`
4. Add tests in `backend/tests/domain/analysis/`

### Modifying Database Schema

1. Update SQLAlchemy models in `src/platform/models.py` or domain-specific models
2. Create migration: `cd backend && .venv/bin/alembic revision --autogenerate -m "description"`
3. Review and edit generated migration in `alembic/versions/`
4. Test migration: `alembic upgrade head` and `alembic downgrade -1`
5. Commit migration file with code changes

## Key Dependencies

### Backend
- **fastapi**: Web framework
- **pm4py**: Process mining algorithms
- **sqlalchemy**: ORM with async support
- **pydantic**: Data validation and serialization
- **duckdb**: High-performance analytics engine
- **celery**: Distributed task queue
- **redis**: Caching and message broker
- **structlog**: Structured logging

### Frontend
- **react**: UI framework
- **@tanstack/react-query**: Server state management
- **antd**: UI component library
- **cytoscape**: Graph visualization
- **react-router-dom**: Client-side routing

## Environment Setup

### First-Time Setup

```bash
# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate  # or `.venv/bin/activate` on macOS/Linux
pip install -e ".[dev]"
alembic upgrade head

# Frontend
cd frontend-new
npm install

# Start both (two terminals)
# Terminal 1: Backend
cd backend/src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

# Terminal 2: Frontend
cd frontend-new && npm run start
```

### MVP Development Data

On startup, the backend automatically seeds:
- **Organization**: `mvp-org-001` (Demo Organization)
- **Workspace**: `mvp-ws-001` (Default Workspace)
- **User**: `mvp-user-001` (analyst@company.local)

Frontend hardcodes these IDs for rapid development.

## Important Patterns

### Async Background Tasks

Long-running operations (data ingestion, model training) use Celery:

```python
from src.platform.infrastructure.tasks import submit_job

# Submit job
job = await submit_job("ingest_dataset", dataset_id=dataset_id)

# Poll status via /api/v1/jobs/{job_id}
```

### Event Log Loading Pattern

```python
# Standard pattern for accessing event logs
from src.domains.datasets.services.ingestion import load_event_log

event_log = await load_event_log(dataset_id)  # Returns PM4Py EventLog
```

### Error Handling

Backend uses **RFC 7807 Problem Details** for consistent error responses:

```python
from src.platform.core.exceptions import AppException, ErrorCode

raise AppException(
    message="Dataset not found",
    error_code=ErrorCode.RESOURCE_NOT_FOUND,
    status_code=404,
    details={"dataset_id": dataset_id}
)
```

### Authorization Pattern

```python
from src.platform.core.permissions import require_workspace_permission

# In route handler
await require_workspace_permission(db, user_id, workspace_id, "editor")
```

## Debugging

### Backend Logs
- **Structured logging**: All logs use structlog with JSON output in production
- **Dev Console**: http://localhost:8001/api/v1/dev/logs/stream for real-time logs (debug mode only)

### Frontend
- **React DevTools**: Browser extension for component inspection
- **Network Tab**: Inspect API calls (CORS configured for localhost:4200)

### Database Inspection
```bash
# SQLite CLI
sqlite3 backend/data/db/process_mining.db

# Check tables
.tables

# Query data
SELECT * FROM datasets;
```

## Performance Considerations

- **DuckDB**: Used for large-scale data ingestion (vectorized processing, columnar storage)
- **Celery**: Offload heavy computations (process discovery, ML training)
- **Redis Caching**: Cache expensive queries (process models, analytics results)
- **Pagination**: All list endpoints support cursor-based pagination
- **Rate Limiting**: 100 req/min standard, 10 req/min for uploads

## Git Workflow

The repository uses feature branches and merge commits:

```bash
# Current branch
git branch  # You're on: polish-refactor-fixes

# Main branch
git checkout main  # Main branch for PRs
```

When creating PRs, target the `main` branch.
