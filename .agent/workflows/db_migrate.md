---
description: Run database migrations with Alembic
---
Apply pending database migrations or create new ones.

### Apply all pending migrations
// turbo
```bash
cd backend && .venv/bin/python -m alembic upgrade head
```

### Check current migration status
```bash
cd backend && .venv/bin/python -m alembic current
```

### Create a new migration
```bash
cd backend && .venv/bin/python -m alembic revision --autogenerate -m "description_here"
```

### Rollback last migration
```bash
cd backend && .venv/bin/python -m alembic downgrade -1
```
