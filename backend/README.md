# Process Mining SaaS

A local-first Process Mining SaaS built with FastAPI and PM4Py, following Domain-Driven Design principles.

## Features

- **Event Log Management**: Upload CSV/XES files, view variants, activities
- **Process Discovery**: Alpha, Inductive, Heuristics miners, DFG visualization
- **Conformance Checking**: Token replay, fitness, precision, deviation detection
- **Process Enhancement**: Performance analysis, bottleneck detection, KPIs
- **Analytics**: Dashboards, variant analysis, resource statistics, anomaly detection

## Quick Start

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package with all dependencies
pip install -e ".[dev,observability]"
```

### 2. Run the Server

```bash
uvicorn src.main:app --reload --port 8001
```

### 3. Access the API

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health
- **Prometheus Metrics**: http://localhost:8001/metrics

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

### Pre-commit Hooks

Install pre-commit hooks to run checks on every commit:

```bash
# From project root
make pre-commit
```

---

## Observability

### Metrics

Prometheus metrics are exposed at `/metrics`.

### Health Probes

- `/health/live` - Kubernetes liveness probe
- `/health/ready` - Kubernetes readiness probe
- `/health/detailed` - Full health status with component checks

---

## API Endpoints

### Event Logs

- `POST /api/v1/logs/upload` - Upload event log
- `GET /api/v1/logs` - List logs
- `GET /api/v1/logs/{id}` - Get log details
- `GET /api/v1/logs/{id}/variants` - Get variants
- `DELETE /api/v1/logs/{id}` - Delete log

### Process Discovery

- `GET /api/v1/discovery/miners` - List available miners
- `POST /api/v1/discovery/discover` - Discover process model
- `GET /api/v1/discovery/dfg/{log_id}` - Get DFG
- `GET /api/v1/discovery/visualize/{model_id}` - Visualize model

### Conformance Checking

- `POST /api/v1/conformance/check` - Check conformance
- `GET /api/v1/conformance/fitness` - Calculate fitness
- `GET /api/v1/conformance/precision` - Calculate precision
- `GET /api/v1/conformance/diagnostics` - Get diagnostics
- `GET /api/v1/conformance/deviations` - Detect deviations

### Enhancement

- `GET /api/v1/enhancement/performance/{log_id}` - Performance analysis
- `GET /api/v1/enhancement/kpis/{log_id}` - KPIs
- `GET /api/v1/enhancement/bottlenecks/{log_id}` - Bottleneck detection

### Analytics

- `GET /api/v1/analytics/dashboard/{log_id}` - Dashboard data
- `GET /api/v1/analytics/variants/{log_id}` - Variant statistics
- `GET /api/v1/analytics/anomalies/{log_id}` - Anomaly detection

## Architecture

```
backend/
├── src/
│   ├── domain/           # Domain Layer (DDD)
│   │   ├── entities.py   # Core entities (EventLog, ProcessCase, etc.)
│   │   ├── value_objects.py  # Value objects (Timestamp, Duration, etc.)
│   │   ├── aggregates.py # Aggregate roots
│   │   └── events.py     # Domain events
│   ├── application/      # Application Layer
│   │   ├── core/         # Core services (Discovery, Conformance, etc.)
│   │   ├── support/      # Support services (Ingestion, Analytics)
│   │   └── generic/      # Generic services (Auth)
│   ├── infrastructure/   # Infrastructure Layer
│   │   ├── persistence/  # SQLite + SQLAlchemy
│   │   ├── storage/      # File storage
│   │   ├── messaging/    # Event bus
│   │   └── workers/      # Background tasks
│   └── presentation/     # Presentation Layer
│       └── api/routers/  # FastAPI routers
└── data/
    ├── db/               # SQLite database
    ├── uploads/          # Uploaded files
    └── models/           # Process models
```

## Configuration

Create a `.env` file in the `backend` directory:

```env
DEBUG=true
AUTH_ENABLED=false
DATABASE_URL=sqlite+aiosqlite:///./data/db/process_mining.db
```

## Sample Usage

```python
import httpx

# Upload a log
with open("event_log.csv", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/api/v1/logs/upload",
        files={"file": f},
    )
log_id = response.json()["id"]

# Discover a process model
response = httpx.post(
    "http://localhost:8000/api/v1/discovery/discover",
    json={"log_id": log_id, "miner_type": "inductive"}
)
model_id = response.json()["model_id"]

# Check conformance
response = httpx.post(
    "http://localhost:8000/api/v1/conformance/check",
    json={"log_id": log_id, "model_id": model_id}
)
print(f"Fitness: {response.json()['fitness']}")
```

## License

MIT
