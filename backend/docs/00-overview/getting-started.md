# Getting Started

> **Time to First API Call:** ~5 minutes
> **Prerequisites:** Python 3.11+, Redis (optional)

## Quick Start (3 Steps)

```bash
# 1. Setup environment
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,observability]"

# 2. Run server
uvicorn src.api.main:app --reload --port 8001

# 3. Open browser
open http://localhost:8001/docs
```

**That's it!** You now have:
- ✅ FastAPI server running on port 8001
- ✅ SQLite database auto-created at `./data/db/process_mining.db`
- ✅ Swagger UI at `/docs` for interactive API testing
- ✅ Hot reload enabled (code changes auto-restart server)

---

## Detailed Setup Guide

### 1. Prerequisites

#### Required
- **Python 3.11+** (recommended: 3.12)
- **pip** (comes with Python)
- **virtualenv** or **venv**

#### Optional (for full features)
- **Redis** ≥5.0 (for caching & Celery)
- **Node.js** ≥18 (for SDK generation)
- **Docker** (for containerized deployment)
- **Make** (for convenience commands)

**Check Prerequisites:**
```bash
python --version    # Should be 3.11+
pip --version       # Should be 23+
redis-server --version  # Optional
node --version      # Optional, for SDK
```

---

### 2. Clone & Environment Setup

```bash
# Clone repository (adjust if using your own repo)
cd /path/to/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Verify activation (should show .venv path)
which python
```

---

### 3. Install Dependencies

#### Option A: Development Install (Recommended)
```bash
# Install with dev tools + observability
pip install -e ".[dev,observability]"

# This includes:
# - Core dependencies (FastAPI, SQLAlchemy, PM4Py)
# - Dev tools (pytest, ruff, mypy)
# - Observability (prometheus, OpenTelemetry)
```

#### Option B: Production Install
```bash
# Minimal install (no dev tools)
pip install -e .

# Or from requirements.txt
pip install -r requirements.txt
```

#### Verify Installation
```bash
# Check installed packages
pip list | grep -E "(fastapi|pm4py|sqlalchemy|duckdb)"

# Expected output:
# fastapi          0.109.0
# pm4py            2.7.11
# sqlalchemy       2.0.25
# duckdb           1.0.0
```

---

### 4. Configuration (.env)

Create a `.env` file in the root directory:

```bash
# Copy example config
cat > .env << 'EOF'
# Application
DEBUG=true
APP_NAME="Process Mining API"
LOG_LEVEL=DEBUG
LOG_JSON=false

# Database (auto-created if SQLite)
DATABASE_URL=sqlite+aiosqlite:///./data/db/process_mining.db

# Storage (auto-created)
UPLOAD_DIR=./data/uploads
MODELS_DIR=./data/models

# Authentication (disabled for development)
AUTH_ENABLED=false
JWT_SECRET=dev-secret-change-in-production

# Redis (optional - caching disabled if unavailable)
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_ENABLED=false

# Celery (optional - for background jobs)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
EOF
```

> [!TIP]
> **No Redis?** Set `CACHE_ENABLED=false` - the app works without it (caching layer gracefully degrades)

---

### 5. Database Initialization

The database is automatically created on first run. To manually initialize:

```bash
# Create data directories
mkdir -p data/{db,uploads,models}

# Run migrations (optional - auto-runs on startup)
alembic upgrade head

# Verify database
ls -lh data/db/
# Should show: process_mining.db
```

---

### 6. Start the Server

#### Development Mode (with auto-reload)
```bash
uvicorn src.api.main:app --reload --port 8001

# Expected output:
# INFO:     Will watch for changes in these directories: ['/path/to/backend']
# INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
# INFO:     Started reloader process [12345] using StatReload
# INFO:     Started server process [12346]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

#### Production Mode (with Gunicorn)
```bash
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --access-logfile - \
  --error-logfile -
```

#### Using Makefile
```bash
make dev    # Start dev server with reload
make prod   # Start prod server with Gunicorn
```

---

### 7. Verify Installation

#### Test Health Endpoint
```bash
curl http://localhost:8001/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2026-01-02T10:30:00Z",
#   "version": "1.0.0"
# }
```

#### Access Swagger UI
Open in browser: **http://localhost:8001/docs**

You should see:
- 19 API endpoint groups
- Interactive "Try it out" buttons
- Auto-generated schemas

#### Test API Call
```bash
# Upload a sample event log
curl -X POST http://localhost:8001/api/v1/datasets/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_log.csv" \
  -F "case_id_column=case_id" \
  -F "activity_column=activity" \
  -F "timestamp_column=timestamp"

# Expected response:
# {
#   "id": "abc-123-def",
#   "name": "sample_log",
#   "status": "ready",
#   "total_cases": 100,
#   "total_events": 523
# }
```

---

## Project Structure Walkthrough

```
backend/
├── src/
│   ├── api/                    # 🌐 API Layer
│   │   ├── main.py            # ← START HERE: FastAPI app factory
│   │   ├── dependencies.py    # Dependency injection
│   │   └── routers/           # 19 API routers
│   │       ├── datasets.py    # ← Try uploading here first
│   │       ├── discovery.py
│   │       └── ...
│   │
│   ├── services/              # ⚙️ Business Logic
│   │   ├── ingestion.py       # ← CSV/XES upload
│   │   ├── mining.py          # ← Process discovery
│   │   ├── conformance.py     # ← Conformance checking
│   │   └── ...
│   │
│   ├── domain/                # 🏛️ Domain Models
│   │   ├── entities.py        # DDD entities
│   │   ├── repositories.py    # Repository interfaces
│   │   └── value_objects.py
│   │
│   ├── models/                # 💾 Data Layer
│   │   ├── orm.py             # SQLAlchemy models (23 tables)
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── repositories.py    # Repository implementations
│   │
│   ├── core/                  # 🔧 Infrastructure
│   │   ├── config.py          # Settings & env vars
│   │   ├── exceptions.py      # Exception hierarchy
│   │   ├── logging_config.py  # Structlog setup
│   │   └── middleware.py      # HTTP middleware
│   │
│   └── infrastructure/        # 📦 External Services
│       ├── cache.py           # Redis caching
│       ├── metrics.py         # Prometheus
│       └── tasks.py           # Celery tasks
│
├── tests/                     # 🧪 Test Suite
│   ├── conftest.py            # Pytest fixtures
│   ├── test_*.py              # Unit tests
│   └── integration_test.py
│
├── alembic/                   # 📊 DB Migrations
│   └── versions/
│
├── data/                      # 💿 Data Storage
│   ├── db/                    # SQLite database
│   ├── uploads/               # Uploaded files
│   └── models/                # Serialized models
│
├── docs/                      # 📚 Documentation
│   ├── 00-overview/
│   ├── 01-features/
│   └── ...
│
├── sdk/                       # 📦 TypeScript SDK
│   └── src/
│
├── pyproject.toml             # Python project config
├── Makefile                   # Convenience commands
├── .env                       # Environment variables
├── CLAUDE.md                  # AI assistant guide
└── README.md                  # Project overview
```

---

## First API Calls (Tutorial)

### Step 1: Upload an Event Log

**Create a sample CSV:**
```csv
case_id,activity,timestamp,resource
case_1,Start,2024-01-01T10:00:00,Alice
case_1,Process,2024-01-01T10:15:00,Bob
case_1,End,2024-01-01T10:30:00,Alice
case_2,Start,2024-01-01T11:00:00,Charlie
case_2,Process,2024-01-01T11:20:00,Bob
case_2,End,2024-01-01T11:40:00,Charlie
```

**Upload via Swagger UI:**
1. Go to http://localhost:8001/docs
2. Find `POST /api/v1/datasets/upload`
3. Click "Try it out"
4. Upload `sample_log.csv`
5. Fill in column mappings:
   - `case_id_column`: `case_id`
   - `activity_column`: `activity`
   - `timestamp_column`: `timestamp`
6. Click "Execute"
7. **Copy the `id` from the response** (e.g., `abc-123-def`)

### Step 2: Discover a Process Model

1. Find `POST /api/v1/discovery/discover`
2. Fill in request body:
   ```json
   {
     "dataset_id": "abc-123-def",
     "miner_type": "inductive"
   }
   ```
3. Click "Execute"
4. **Copy the `model_id` from the response**

### Step 3: Visualize the Model

1. Find `GET /api/v1/visualization/petri-net/{model_id}`
2. Enter your model ID
3. Click "Execute"
4. You'll get a Petri net visualization in DOT format

### Step 4: Check Conformance

1. Find `POST /api/v1/conformance/check`
2. Fill in:
   ```json
   {
     "dataset_id": "abc-123-def",
     "model_id": "xyz-789-ghi",
     "method": "token_replay"
   }
   ```
3. View fitness, precision, and deviation metrics

---

## Development Workflow

### Makefile Commands

```bash
# Development
make dev            # Start dev server with reload
make check          # Run all checks (lint, format, typecheck, security)
make test           # Run tests
make test-cov       # Tests with coverage report

# Database
make db-upgrade     # Run migrations
make db-downgrade   # Rollback migration
make db-revision    # Create new migration

# SDK
make sdk-generate   # Generate TypeScript SDK (requires server running)

# Cleanup
make clean          # Remove cache files, test artifacts
```

### Testing Your Changes

```bash
# 1. Run tests
pytest tests/ -v

# 2. Run specific test
pytest tests/test_mining_service.py::test_discover_model -v

# 3. Run with coverage
pytest --cov=src --cov-report=html

# 4. View coverage report
open htmlcov/index.html
```

### Code Quality Checks

```bash
# Lint & format
ruff check src/
ruff format src/

# Type checking
mypy src/

# Security scan
bandit -r src/

# All at once
make check
```

---

## Common Issues & Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution:** Install in editable mode
```bash
pip install -e .
```

### Issue: "Connection refused" when connecting to Redis

**Solution:** Disable caching or start Redis
```bash
# Option 1: Disable caching
echo "CACHE_ENABLED=false" >> .env

# Option 2: Start Redis
# macOS (with Homebrew):
brew services start redis
# Linux:
sudo systemctl start redis
# Docker:
docker run -d -p 6379:6379 redis:7-alpine
```

### Issue: "Database is locked" (SQLite)

**Solution:** SQLite doesn't handle concurrent writes well
```bash
# Short-term: Restart server
# Long-term: Migrate to PostgreSQL
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/pmdb"
alembic upgrade head
```

### Issue: PM4Py operation times out

**Solution:** Circuit breaker triggered, reduce event log size
```bash
# Check logs for circuit breaker messages
tail -f logs/app.log | grep circuit_breaker

# Reduce log size via filtering
curl -X POST http://localhost:8001/api/v1/filtering/time-range \
  -d '{"dataset_id": "abc-123", "start_date": "2024-01-01", "end_date": "2024-01-07"}'
```

### Issue: "OSError: [Errno 28] No space left on device"

**Solution:** Clean up old uploads and models
```bash
# Find large files
du -sh data/* | sort -h

# Remove old uploads (be careful!)
find data/uploads -type f -mtime +30 -delete

# Remove old models
find data/models -type f -mtime +30 -delete
```

---

## Optional Components

### Redis Setup

#### macOS (Homebrew)
```bash
brew install redis
brew services start redis

# Verify
redis-cli ping
# Should output: PONG
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verify
redis-cli ping
```

#### Docker
```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine

# Verify
docker exec redis redis-cli ping
```

### Celery Workers (Background Jobs)

```bash
# Start worker
celery -A src.infrastructure.tasks worker \
  --loglevel=info \
  --concurrency=4 \
  --pool=prefork

# Start Flower (monitoring UI)
celery -A src.infrastructure.tasks flower \
  --port=5555

# Access Flower
open http://localhost:5555
```

### PostgreSQL Migration

```bash
# 1. Install PostgreSQL
brew install postgresql@15  # macOS
sudo apt install postgresql-15  # Linux

# 2. Create database
createdb process_mining

# 3. Update .env
echo "DATABASE_URL=postgresql+asyncpg://user:pass@localhost/process_mining" >> .env

# 4. Install asyncpg driver
pip install asyncpg

# 5. Run migrations
alembic upgrade head
```

---

## IDE Setup

### VS Code

**Recommended Extensions:**
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- Docker (ms-azuretools.vscode-docker)

**Settings (.vscode/settings.json):**
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

### PyCharm

1. **Open Project:** File → Open → Select `backend/`
2. **Configure Interpreter:**
   - File → Settings → Project → Python Interpreter
   - Add Interpreter → Existing → Select `.venv/bin/python`
3. **Enable Type Checking:**
   - Settings → Editor → Inspections → Python → Type Checker
   - Check "Enable type checking"
4. **Run Configuration:**
   - Add Configuration → Python
   - Script: `uvicorn`
   - Parameters: `src.api.main:app --reload --port 8001`

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode (verbose logging) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_JSON` | `false` | Output logs as JSON (true for production) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/db/process_mining.db` | Database connection string |
| `UPLOAD_DIR` | `./data/uploads` | Directory for uploaded files |
| `MODELS_DIR` | `./data/models` | Directory for serialized models |
| `AUTH_ENABLED` | `false` | Enable JWT authentication |
| `JWT_SECRET` | `dev-secret-change-in-production` | JWT signing secret |
| `JWT_EXPIRE_MINUTES` | `1440` | JWT expiration (24 hours) |
| `REDIS_HOST` | `localhost` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `CACHE_ENABLED` | `false` | Enable Redis caching |
| `CACHE_DEFAULT_TTL` | `3600` | Cache TTL in seconds (1 hour) |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/1` | Celery result backend |

---

## Next Steps

Now that you have the server running:

1. **Explore API Documentation:**
   - [Feature Guides](../01-features/README.md) - Learn about each API feature
   - [API Reference](http://localhost:8001/docs) - Interactive Swagger UI

2. **Understand Architecture:**
   - [Architecture Overview](./architecture.md) - System design and C4 diagrams
   - [Layer Documentation](../02-layers/README.md) - Deep dive into each layer

3. **Read Cross-Cutting Concerns:**
   - [Authentication](../03-cross-cutting/auth.md) - JWT setup and RBAC
   - [Error Handling](../03-cross-cutting/error-handling.md) - RFC 7807 standard
   - [Logging](../03-cross-cutting/logging.md) - Structured logging with structlog

4. **Write Your First Feature:**
   - [Development Guide](../03-cross-cutting/development-guide.md) - Best practices
   - [Testing Guide](../03-cross-cutting/testing.md) - Writing tests

5. **Deploy to Production:**
   - [Deployment Guide](../03-cross-cutting/deployment.md) - Docker, Kubernetes, cloud providers

---

## Getting Help

- **Documentation:** You're reading it! Check [docs/README.md](../README.md) for the full index
- **API Reference:** http://localhost:8001/docs (Swagger UI)
- **Code Examples:** See `tests/` directory for usage examples
- **Issues:** Check existing issues or create a new one
- **Architecture Questions:** Read [architecture.md](./architecture.md) first

**Quick Links:**
- [CLAUDE.md](../../CLAUDE.md) - Quick reference for AI assistants
- [README.md](../../README.md) - Project overview
- [pyproject.toml](../../pyproject.toml) - Dependencies and metadata
