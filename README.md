# Process Mining SaaS Platform

A comprehensive Process Mining platform powered by **PM4Py** with a FastAPI backend, React frontend, and TypeScript SDK.

## 🚀 Quick Start

```bash
# Install backend dependencies
make install

# Start the backend (Terminal 1)
cd backend/src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

# Start the frontend (Terminal 2)
cd frontend-new && npm run start

# Run strict code checks
make check
```

## Project Structure

```
system/
├── backend/          # FastAPI backend (Python)
│   ├── src/          # Application code
│   └── tests/        # Test suite (pytest)
├── frontend-new/     # React frontend (TypeScript)
│   ├── src/          # Application code
│   └── libs/         # Shared libraries
├── sdk/              # TypeScript SDK
│   └── src/          # SDK source
└── docs/             # Documentation
```

## Development Commands

### Unified Commands (Backend + SDK)

| Command           | Description                     |
| ----------------- | ------------------------------- |
| `make install`    | Install all dependencies        |
| `make lint`       | Run linters (Ruff + ESLint)     |
| `make typecheck`  | Run type checkers (mypy + tsc)  |
| `make security`   | Run security scans (Bandit)     |
| `make test`       | Run all tests (pytest + vitest) |
| `make check`      | Run lint + typecheck + security |
| `make all`        | Run check + test (full CI)      |
| `make pre-commit` | Install pre-commit hooks        |

### Frontend Commands

```bash
cd frontend-new && npm run start  # Start dev server (port 4200)
cd frontend-new && npm run build  # Production build
cd frontend-new && npm run test   # Run Jest tests
```

## Testing Tools

- **Backend:** `pytest` with async support + coverage (`pytest-cov`)
  - 16 test files in `backend/tests/`
  - Run: `make backend-test` or `make backend-test-cov`
- **Frontend:** `Jest` + React Testing Library
  - Run: `cd frontend-new && npm test`
- **SDK:** `Vitest`
  - Run: `make sdk-test`

## Server URLs

### Backend API (Port 8001)

| Endpoint                           | Description        |
| ---------------------------------- | ------------------ |
| http://localhost:8001/docs         | Swagger UI         |
| http://localhost:8001/redoc        | ReDoc              |
| http://localhost:8001/metrics      | Prometheus metrics |
| http://localhost:8001/health/live  | Liveness probe     |
| http://localhost:8001/health/ready | Readiness probe    |

### Frontend (Port 4200)

| Endpoint               | Description    |
| ---------------------- | -------------- |
| http://localhost:4200/ | React Frontend |

## Key Features

- **Event Log Management**: Upload CSV/XES files, quality assessment
- **Process Discovery**: Alpha, Heuristic, Inductive miners
- **Conformance Checking**: Fitness, precision, alignments
- **Performance Analysis**: Bottleneck detection, KPIs
- **Object-Centric PM**: OCEL 2.0 support
- **Organizational Mining**: SNA, role discovery

## Components

### [Backend](./backend/)

FastAPI application with 17 API routers and 150+ endpoints.

### [SDK](./sdk/)

TypeScript SDK with 13 domain-specific clients following business-verb naming.

## License

MIT
