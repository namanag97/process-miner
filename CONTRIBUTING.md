# Contributing to Process Mining SaaS

## Quick Start

```bash
# 1. Clone and setup
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,observability]"
cd ../frontend-new && npm install

# 2. Install pre-commit hooks
make pre-commit

# 3. Start development servers
make dev-full
```

## Development Workflow

### Before Committing

```bash
make check          # Runs lint + typecheck + security
make test           # Runs all tests
```

### Common Commands

| Command | Description |
|---------|-------------|
| `make dev-full` | Start backend + frontend |
| `make check` | Run all quality checks |
| `make lint-all` | Full static analysis |
| `make quick-commit` | Commit after checks pass |
| `make checkpoint` | Quick save without checks |

### Using Agent Workflows

This repo has agent workflows you can invoke:

- `/start_servers` - Start dev servers
- `/full_stack` - Start everything including Temporal
- `/check_backend` - Run backend quality checks
- `/check_frontend` - Run frontend quality checks
- `/fix_lint` - Auto-fix linting issues
- `/db_migrate` - Database migrations
- `/debug_api` - API debugging tools

## Code Standards

### Backend (Python)

- **Formatter**: Ruff
- **Linter**: Ruff  
- **Type Checker**: mypy
- **Architecture**: import-linter enforces boundaries

### Frontend (TypeScript)

- **Formatter**: Prettier
- **Linter**: ESLint
- **Type Checker**: TypeScript strict mode

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design.

### Key Boundaries

```
backend/src/
├── api/           # HTTP layer (FastAPI routers)
├── features/      # Business logic (isolated domains)
├── platform/      # Infrastructure (Temporal, DB, storage)
└── shared/        # Cross-cutting utilities
```

**Rule**: Features cannot import from each other directly.

## Testing

```bash
# Backend
cd backend && make test      # All tests
cd backend && make test-cov  # With coverage

# Frontend  
cd frontend-new && npm test
```

## Database

```bash
# Apply migrations
cd backend && make db-migrate

# Create new migration
alembic revision --autogenerate -m "description"
```

## Troubleshooting

### Port already in use

```bash
lsof -ti:8001 | xargs kill -9  # Kill backend
lsof -ti:4200 | xargs kill -9  # Kill frontend
```

### Reset dev environment

```bash
cd backend && make reset-dev
```
