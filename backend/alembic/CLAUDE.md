# Alembic Migrations CLAUDE.md

## Overview
Database migration management using Alembic. Migrations are auto-generated from SQLAlchemy models.

## Commands

```bash
cd backend

# Apply all pending migrations
.venv/bin/alembic upgrade head

# Create new migration (auto-detect changes)
.venv/bin/alembic revision --autogenerate -m "description"

# Rollback one migration
.venv/bin/alembic downgrade -1

# Rollback to specific revision
.venv/bin/alembic downgrade <revision_id>

# View migration history
.venv/bin/alembic history

# Show current revision
.venv/bin/alembic current
```

## Directory Structure

```
alembic/
├── env.py           # Migration environment configuration
├── versions/        # Migration files
└── script.py.mako   # Template for new migrations
```

## Workflow

### Adding a New Table
1. Add SQLAlchemy model in `src/infra/models.py` or domain models
2. Run: `.venv/bin/alembic revision --autogenerate -m "add xyz table"`
3. Review generated migration in `alembic/versions/`
4. Apply: `.venv/bin/alembic upgrade head`

### Modifying a Column
1. Update model in source code
2. Generate migration with descriptive message
3. Review for data safety (especially for production)
4. Apply migration

## Best Practices

- Always review auto-generated migrations before applying
- Use descriptive migration names
- Test migrations with `upgrade` and `downgrade`
- Avoid data loss - add new columns as nullable first
- For production, consider data migration separately
