# Process Mining SaaS Platform

A comprehensive Process Mining platform powered by **PM4Py** with a FastAPI backend, React frontend, and TypeScript API client.

## Quick Start

```bash
# Install backend dependencies
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"

# Start the backend (Terminal 1)
cd backend/src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

# Start the frontend (Terminal 2)
cd frontend-new && npm install && npm run start

# Run quality checks
make check
```

## Dev Credentials

```
Email:    analyst@example.com
Password: TestPass123
```

Pre-seeded IDs: `mvp-org-001`, `mvp-ws-001`, `mvp-proj-001`, `mvp-user-001`

## Project Structure

```
system/
├── backend/              # FastAPI backend (Python)
│   ├── src/
│   │   ├── api/          # FastAPI app and routers
│   │   ├── features/     # Process mining features
│   │   ├── infra/        # Infrastructure (auth, db, temporal)
│   │   └── shared/       # Shared utilities
│   └── tests/            # Pytest test suite
├── frontend-new/         # React frontend (TypeScript)
│   ├── src/
│   │   ├── features/     # Feature modules
│   │   ├── shared/       # Shared components/hooks
│   │   └── api/          # API integration
│   └── libs/             # OpenAPI SDK
└── docs/                 # Documentation
```

## Development Commands

### Backend

| Command           | Description                    |
| ----------------- | ------------------------------ |
| `make install`    | Install backend dependencies   |
| `make lint`       | Run Ruff linter                |
| `make typecheck`  | Run mypy type checker          |
| `make security`   | Run Bandit security scanner    |
| `make test`       | Run pytest tests               |
| `make check`      | Run lint + typecheck + security |
| `make all`        | Run check + test (full CI)     |

### Frontend

```bash
cd frontend-new
npm run start     # Dev server (port 4200)
npm run build     # Production build
npm run test      # Jest tests
npm run typecheck # TypeScript check
npm run generate:sdk  # Regenerate API client
```

## Server URLs

### Backend API (Port 8001)

| Endpoint                           | Description        |
| ---------------------------------- | ------------------ |
| http://localhost:8001/docs         | Swagger UI         |
| http://localhost:8001/redoc        | ReDoc              |
| http://localhost:8001/health/live  | Liveness probe     |
| http://localhost:8001/health/ready | Readiness probe    |

### Frontend (Port 4200)

| Endpoint               | Description    |
| ---------------------- | -------------- |
| http://localhost:4200/ | React Frontend |

## Key Features

- **Event Log Management**: Upload CSV/XES files, column mapping, DuckDB ingestion
- **Process Discovery**: Alpha, Heuristic, Inductive, Split miners
- **Conformance Checking**: Token replay, alignments, fitness metrics
- **Performance Analytics**: Bottleneck detection, cycle time, throughput
- **Visualization**: Interactive DFG graphs with Cytoscape
- **Object-Centric PM**: OCEL 2.0 support
- **Organizational Mining**: Social network analysis, resource profiling
- **Real-Time Progress**: SSE streaming for long-running operations

## Architecture

### Backend Layers

```
API Layer (src/api/)
    ↓
Features Layer (src/features/)  ←→  Infrastructure Layer (src/infra/)
    ↓                                    ↓
                Shared Layer (src/shared/)
```

### Frontend Features

- **platform/** - Workspace, projects, upload wizard
- **explorer/** - Process visualization (DFG, variants)
- **analytics/** - Performance dashboards
- **discovery/** - Process discovery UI
- **ai/** - AI predictions and chat

## Technology Stack

### Backend
- **FastAPI** - Async REST API
- **PM4Py** - Process mining algorithms
- **SQLAlchemy** - Async ORM with SQLite
- **DuckDB** - High-performance data ingestion
- **Temporal** - Workflow orchestration

### Frontend
- **React 19** - UI framework
- **TanStack Query** - Server state management
- **Ant Design** - UI components
- **Cytoscape** - Graph visualization
- **Rspack** - Fast bundling

## License

MIT
