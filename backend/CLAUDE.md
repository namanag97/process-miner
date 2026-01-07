# Backend CLAUDE.md

## Overview
FastAPI-based Python backend for the Process Mining SaaS platform. Uses PM4Py for process mining algorithms, SQLite/DuckDB for data storage, and Celery for async tasks.

## Quick Commands

```bash
# Start dev server (port 8001)
cd backend/src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

# Run tests
.venv/bin/python -m pytest tests/ -v

# Run quality checks
make check

# Database migrations
.venv/bin/alembic upgrade head
.venv/bin/alembic revision --autogenerate -m "description"
```

## Directory Structure

```
backend/
├── src/                 # Source code (see src/CLAUDE.md)
├── tests/               # Test suite
├── alembic/             # Database migrations
├── scripts/             # Utility scripts
├── data/                # Local data storage
├── docs/                # Backend-specific docs
└── pyproject.toml       # Python dependencies & config
```

## Key Files

- `src/api/main.py` - FastAPI app entry point
- `pyproject.toml` - Dependencies, linting config, import-linter rules
- `alembic.ini` - Migration configuration
- `Makefile` - Common development tasks
- `.env` - Environment variables (copy from `.env.example`)

## Architecture Rules

1. **Domain Independence**: `src/domain` must be pure - no infrastructure dependencies
2. **Services Independence**: Services cannot depend on API layer
3. **Platform/Feature Separation**: Platform (generic infra) never depends on Features (process mining)

## Testing

```bash
# All tests
.venv/bin/python -m pytest tests/ -v

# Single file
.venv/bin/python -m pytest tests/api/test_datasets.py -v

# With coverage
.venv/bin/python -m pytest tests/ --cov=src --cov-report=html
```

## API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI Spec: http://localhost:8001/openapi.json
