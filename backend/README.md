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

Backend API Exploration Summary

       1. Available API Endpoints (11 Routers)

       File: /Users/namanagarwal/system/backend/src/api/routers/init.py

       The backend has 11 FastAPI routers:
       - processes - Event log management and ingestion
       - discovery - Process model discovery (Alpha, Inductive, Heuristics miners)
       - visualization - Process model visualization
       - conformance - Conformance checking (token replay, alignments)
       - ocpm - Object-Centric Process Mining
       - workflows - Workflow automation
       - analytics ⭐ - Performance analytics and bottleneck detection
       - filtering - Event log filtering
       - organizational - Social network analysis
       - predictions ⭐ - ML-based predictions
       - simulation - Process simulation and what-if analysis

       ---
       2. AI/Analytics Capabilities

       Analytics Router (/Users/namanagarwal/system/backend/src/api/routers/analytics.py)

       Endpoints:
       - GET /analytics/logs/{log_id}/bottlenecks - Detect process bottlenecks based on waiting times
       - GET /analytics/logs/{log_id}/rework - Analyze rework (repeated activities)
       - GET /analytics/logs/{log_id}/service-times - Service time statistics per activity
       - GET /analytics/logs/{log_id}/cycle-time - Cycle time (case duration) statistics
       - GET /analytics/logs/{log_id}/throughput - Throughput metrics (cases per day/week/month)
       - GET /analytics/logs/{log_id}/patterns - Frequent activity patterns/subsequences
       - GET /analytics/logs/{log_id}/performance - Comprehensive performance dashboard

       Implementation: Uses PM4Py for statistical analysis, includes caching (1 hour TTL)

       Predictions Router (/Users/namanagarwal/system/backend/src/api/routers/predictions.py)

       Endpoints:
       - POST /predictions/logs/{log_id}/train - Train ML prediction model (async/sync modes)
       - GET /predictions/jobs/{job_id} - Get async training job status
       - GET /predictions/logs/{log_id}/predictors - List all predictors for a log
       - GET /predictions/predictors/{predictor_id} - Get predictor details
       - POST /predictions/predictors/{predictor_id}/predict - Make single prediction
       - POST /predictions/predictors/{predictor_id}/predict-batch - Batch predictions
       - DELETE /predictions/predictors/{predictor_id} - Delete predictor

       ML Capabilities:
       - Target Types: next_activity, remaining_time
       - Algorithms: Random Forest (default), XGBoost
       - Features: Activity sequences (one-hot encoded), prefix length, position ratio
       - Training: 80/20 train/test split, supports async via Celery
       - Metrics: Accuracy (classification), MAE/RMSE (regression)
       - Predictions: Returns confidence scores and top-3 alternatives

       Implementation Details:
       # Feature extraction: last 5 activities + prefix metadata
       prefix_encoded = [0] * len(activity_list)  # One-hot encoding
       features = prefix_encoded + [len(prefix), position_ratio]

       Simulation Router (/Users/namanagarwal/system/backend/src/api/routers/simulation.py)

       Endpoints:
       - POST /simulation/models/{model_id}/play-out - Generate synthetic event log from model
       - POST /simulation/logs/{log_id}/simulate - Run what-if simulation scenario
       - POST /simulation/logs/{log_id}/capacity-plan - Estimate resource requirements

       Organizational Router (/Users/namanagarwal/system/backend/src/api/routers/organizational.py)

       Social Network Analysis Endpoints:
       - GET /organizational/logs/{log_id}/handover-network - Handover of work network
       - GET /organizational/logs/{log_id}/collaboration-network - Working together network
       - GET /organizational/logs/{log_id}/resource-similarity - Resource similarity graph
       - GET /organizational/logs/{log_id}/roles - Role discovery
       - GET /organizational/logs/{log_id}/resources/{resource}/profile - Resource profiling
       - GET /organizational/logs/{log_id}/workload - Workload distribution

       Filtering Router (/Users/namanagarwal/system/backend/src/api/routers/filtering.py)

       Advanced Filtering:
       - Time-based, variant-based (top-k, coverage), activity-based, performance-based
       - Filter preview (no-save mode) and templates
       - Creates new filtered event logs (non-destructive)

       ---
       3. SDK Client Capabilities

       File: /Users/namanagarwal/system/sdk/src/index.ts

       All 11 routers have corresponding TypeScript SDK clients:

       Key AI/Analytics Clients:

       AnalyticsClient (sdk/src/clients/analytics.client.ts)
       analytics.getBottlenecks(logId)
       analytics.getRework(logId)
       analytics.getServiceTimes(logId)
       analytics.getCycleTime(logId)
       analytics.getThroughput(logId)
       analytics.getPatterns(logId, minSupport)
       analytics.getPerformanceDashboard(logId)  // Combined metrics

       PredictionsClient (sdk/src/clients/predictions.client.ts)
       predictions.trainPredictor(logId, request, asyncMode)
       predictions.getTrainingJob(jobId)
       predictions.listPredictors(logId)
       predictions.predict(predictorId, request)
       predictions.predictBatch(predictorId, request)
       predictions.deletePredictor(predictorId)

       SimulationClient (sdk/src/clients/simulation.client.ts)
       simulation.playOut(modelId, request)
       simulation.simulate(logId, request)
       simulation.capacityPlan(logId, targetThroughput)

       FilteringClient (sdk/src/clients/filtering.client.ts)
       filtering.applyFilter(logId, request)
       filtering.previewFilter(logId, request)
       filtering.getFilterOptions(logId)
       filtering.getTemplates()

       DiscoveryClient (sdk/src/clients/discovery.client.ts)
       discovery.discover(options)
       discovery.buildDFG(logId)
       discovery.extractPetriNet(modelId)
       discovery.visualize(modelId, format)

       ---
       4. Existing AI/Analysis Features for Ultrathink

       What Exists and Can Be Leveraged:

       1. ML Prediction Infrastructure ✅
         - Training pipeline (sync/async)
         - Feature extraction from event logs
         - Model persistence (pickle serialization)
         - Scikit-learn/XGBoost integration
         - Batch prediction support
       2. Performance Analytics ✅
         - Bottleneck detection algorithm
         - Rework pattern analysis
         - Statistical aggregations (cycle time, throughput)
         - Frequent pattern mining
       3. Process Discovery ✅
         - Multiple mining algorithms
         - Quality metrics (fitness, precision)
         - Petri net representations
       4. Conformance Checking ✅
         - Deviation detection
         - Trace-level diagnostics
         - Alignment-based analysis
       5. Organizational Mining ✅
         - Social network extraction
         - Resource profiling
         - Role discovery
       6. Simulation ✅
         - What-if scenario analysis
         - Capacity planning
         - Model play-out

       What's Missing for Ultrathink:

       1. No LLM/AI Analysis Endpoints ❌
         - No natural language insights generation
         - No AI-powered recommendations
         - No conversational interface
       2. No Advanced AI Features ❌
         - No anomaly detection (beyond basic stats)
         - No causal analysis
         - No process optimization suggestions
         - No automatic insight discovery
       3. No Multi-Model Analysis ❌
         - Can't compare multiple logs
         - No cross-process analysis
         - No enterprise-wide insights
       4. Limited Explanation ❌
         - Predictions lack explainability (no SHAP/LIME)
         - No "why" behind bottlenecks
         - No actionable recommendations

       ---
       5. Architecture Notes

       Clean Architecture:
       - Routers → Services (1:1 mapping)
       - Services wrap PM4Py functionality
       - Async database (SQLAlchemy async)
       - Caching (in-memory, configurable TTL)
       - Async jobs (Celery for long-running tasks)

       Key Files:
       - /Users/namanagarwal/system/backend/src/api/routers/ - All API endpoints
       - /Users/namanagarwal/system/backend/src/services/ - Business logic
       - /Users/namanagarwal/system/backend/src/models/schemas.py - 926 lines of Pydantic models
       - /Users/namanagarwal/system/sdk/src/clients/ - TypeScript SDK clients

       Technology Stack:
       - Backend: FastAPI, PM4Py, scikit-learn, XGBoost, Celery
       - Database: SQLAlchemy (async), 10 tables
       - SDK: TypeScript, auto-generated from OpenAPI spec

       ---
       Key Insight for Ultrathink

       The backend has excellent foundation for process mining but lacks AI-powered insights. Ultrathink could:

       1. Leverage existing prediction infrastructure to add LLM-enhanced explanations
       2. Wrap analytics endpoints with AI insight generation
       3. Add new /ultrathink router that orchestrates multiple existing endpoints
       4. Use SDK clients to build a conversational UI that queries backend data

       The prediction service already extracts features and trains models - you just need to add the AI reasoning layer on top!
