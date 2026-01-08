# Process Mining SaaS Backend

A FastAPI-based Process Mining SaaS platform built with PM4Py, following a layered architecture with feature modules.

## Quick Start

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package with all dependencies
pip install -e ".[dev]"
```

### 2. Run the Server

```bash
cd src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001
```

### 3. Access the API

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health/live
- **OpenAPI Spec**: http://localhost:8001/openapi.json

### 4. Dev Credentials

```
Email:    analyst@example.com
Password: TestPass123
```

Pre-seeded IDs: `mvp-org-001`, `mvp-ws-001`, `mvp-proj-001`, `mvp-user-001`

---

## Development Tooling

Run all quality checks with a single command:

```bash
make check   # Runs lint + typecheck + security
make all     # Runs check + tests (full CI)
```

### Individual Commands

| Command          | Description                    |
| ---------------- | ------------------------------ |
| `make lint`      | Run Ruff linter                |
| `make format`    | Format code with Ruff          |
| `make typecheck` | Run mypy type checker          |
| `make security`  | Run Bandit security scanner    |
| `make test`      | Run pytest tests               |
| `make test-cov`  | Run tests with coverage report |
| `make run`       | Start development server       |

---

## Architecture

```
backend/src/
├── api/                      # FastAPI application entry point
│   ├── main.py              # App factory, middleware, exception handlers
│   └── routers/             # Router imports and registration
├── application/              # CQRS application layer
│   ├── commands/            # Command handlers
│   ├── queries/             # Query handlers
│   └── projections/         # Read model projections
├── features/                 # Process mining feature modules
│   └── process_mining/
│       ├── models/          # SQLAlchemy models (Dataset, etc.)
│       ├── schemas/         # Pydantic schemas for API
│       ├── datasets/        # Dataset management (upload, ingest, CRUD)
│       ├── ingestion/       # DuckDB-based data ingestion
│       ├── discovery/       # Process discovery algorithms
│       ├── conformance/     # Conformance checking
│       ├── analytics/       # Performance analytics
│       ├── visualization/   # Graph visualization (DFG, Petri)
│       ├── predictions/     # ML predictions
│       ├── organizational/  # Organizational mining
│       ├── simulation/      # What-if simulation
│       ├── ocpm/            # Object-Centric PM (OCEL)
│       ├── ai/              # AI chat assistant
│       └── statistics/      # Dataset statistics
├── infra/                    # Infrastructure layer
│   ├── core/                # Config, logging, middleware, exceptions
│   ├── infrastructure/      # Database, storage, cache
│   ├── auth/                # JWT authentication
│   ├── users/               # User management + API routers
│   ├── organizations/       # Organization management
│   ├── workspaces/          # Workspace RBAC
│   ├── projects/            # Project management
│   ├── temporal/            # Temporal workflows and activities
│   ├── jobs/                # Background job tracking
│   ├── health/              # Health check endpoints
│   ├── audit/               # Audit logging
│   └── devconsole/          # Developer tools (SSE logs)
└── shared/                   # Shared utilities, types, constants
```

### Layer Dependencies

```
API Layer (src/api/)
    ↓
Features Layer (src/features/)  ←→  Infrastructure Layer (src/infra/)
    ↓                                    ↓
                Shared Layer (src/shared/)
```

**Key Principles:**
- Features cannot import from API layer
- Infrastructure should not import from features
- Shared layer has no internal dependencies
- Enforced via `import-linter` contracts in `pyproject.toml`

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user

### Datasets
- `POST /api/v1/datasets/presign` - Get presigned upload URL
- `POST /api/v1/datasets/{id}/uploaded` - Confirm upload complete
- `GET /api/v1/datasets/{id}/columns` - Get detected columns
- `POST /api/v1/datasets/{id}/mapping` - Set column mappings
- `POST /api/v1/datasets/{id}/ingest` - Start ingestion (returns workflow_id)
- `GET /api/v1/datasets/{id}/statistics` - Get dataset statistics

### Process Discovery
- `GET /api/v1/discovery/miners` - List available mining algorithms
- `POST /api/v1/discovery/discover` - Discover process model
- `GET /api/v1/discovery/models` - List discovered models

### Conformance Checking
- `GET /api/v1/conformance/methods` - List conformance methods
- `POST /api/v1/conformance/check` - Run conformance check
- `GET /api/v1/conformance/deviations/{dataset_id}/{model_id}` - Get deviations

### Analytics
- `GET /api/v1/analytics/datasets/{id}/bottlenecks` - Detect bottlenecks
- `GET /api/v1/analytics/datasets/{id}/cycle-time` - Cycle time analysis
- `GET /api/v1/analytics/datasets/{id}/throughput` - Throughput metrics
- `GET /api/v1/analytics/datasets/{id}/rework` - Rework patterns

### Visualization
- `GET /api/v1/visualization/{id}/dfg` - Get DFG graph data (JSON)
- `GET /api/v1/visualization/{id}/dfg/svg` - Get DFG as SVG image
- `GET /api/v1/visualization/models/{id}/petri` - Get Petri net structure

### Operations (Real-Time Progress)
- `GET /api/v1/operations/{workflow_id}/stream` - SSE progress events
- `GET /api/v1/operations/{workflow_id}` - Get operation status
- `POST /api/v1/operations/{workflow_id}/cancel` - Cancel operation

### Health
- `GET /health/live` - Kubernetes liveness probe
- `GET /health/ready` - Kubernetes readiness probe

---

## User Flow Example

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' \
  | jq -r '.access_token')

# 2. Get presigned URL for upload
PRESIGN=$(curl -s -X POST http://localhost:8001/api/v1/datasets/presign \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename":"events.csv","project_id":"mvp-proj-001"}')

# 3. Upload file to presigned URL
curl -X PUT "$(echo $PRESIGN | jq -r '.upload_url')" --upload-file events.csv

# 4. Confirm upload
DATASET_ID=$(echo $PRESIGN | jq -r '.dataset_id')
curl -X POST "http://localhost:8001/api/v1/datasets/$DATASET_ID/uploaded" \
  -H "Authorization: Bearer $TOKEN"

# 5. Map columns
curl -X POST "http://localhost:8001/api/v1/datasets/$DATASET_ID/mapping" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_id_column":"case_id","activity_column":"activity","timestamp_column":"timestamp"}'

# 6. Start ingestion
WORKFLOW=$(curl -s -X POST "http://localhost:8001/api/v1/datasets/$DATASET_ID/ingest" \
  -H "Authorization: Bearer $TOKEN")
WORKFLOW_ID=$(echo $WORKFLOW | jq -r '.workflow_id')

# 7. Stream progress (SSE)
curl -N "http://localhost:8001/api/v1/operations/$WORKFLOW_ID/stream" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Testing

```bash
# Run all tests
.venv/bin/python -m pytest tests/ -v

# Run specific test file
.venv/bin/python -m pytest tests/api/test_datasets.py -v

# Run with coverage
.venv/bin/python -m pytest tests/ --cov=src --cov-report=html
```

---

## Configuration

Create a `.env` file in the `backend` directory:

```env
DEBUG=true
AUTH_ENABLED=true
DATABASE_URL=sqlite+aiosqlite:///./data/db/process_mining.db
STORAGE_TYPE=local
```

---

## Key Technologies

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Web Framework** | FastAPI | Async REST API |
| **Database** | SQLite + SQLAlchemy | Async data persistence |
| **Process Mining** | PM4Py 2.7+ | Discovery, conformance, analytics |
| **Data Ingestion** | DuckDB | High-performance CSV parsing |
| **Workflows** | Temporal | Long-running async operations |
| **Auth** | JWT (PyJWT) | Token-based authentication |
| **Logging** | Structlog | Structured JSON logging |
| **Rate Limiting** | SlowAPI | Request rate limiting |

---

## License

MIT
