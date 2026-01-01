# ADR-004: SQLite for Simplicity

## Status

Accepted

## Context

The backend needs a database for:

- Storing event log metadata
- Persisting discovered process models
- Tracking analyses and results
- User sessions and preferences

Options considered:

1. **PostgreSQL** - Full-featured, production-ready
2. **SQLite** - Lightweight, zero-configuration
3. **DuckDB** - Columnar, analytics-optimized
4. **MongoDB** - Document-oriented, flexible schema

## Decision

Use **SQLite** as the primary database for MVP development.

### Rationale

1. **Zero configuration** - No separate server, embedded in application
2. **Development speed** - Instant setup, easy testing
3. **Portability** - Single file, easy backup and migration
4. **SQLAlchemy compatible** - Same ORM code works with PostgreSQL

### Architecture

```
┌─────────────────────────────────────────┐
│             SQLAlchemy ORM              │
│  (Abstraction layer, dialect-agnostic)  │
├─────────────────────────────────────────┤
│   Development: SQLite + aiosqlite       │
│   Production:  PostgreSQL + asyncpg     │
└─────────────────────────────────────────┘
```

### DuckDB Augmentation

For analytics-heavy operations, we use DuckDB alongside SQLite:

- **DuckDB** - Fast columnar queries for event data analysis
- **SQLite** - OLTP operations (CRUD on metadata)

```python
class EventLogLoader:
    """High-performance data loading using DuckDB."""

    @staticmethod
    async def load(log_id: str) -> pd.DataFrame:
        # DuckDB for fast analytical queries
        return await asyncio.to_thread(
            duckdb.query,
            f"SELECT * FROM events WHERE log_id = '{log_id}'"
        )
```

## Consequences

### Positive

- **Fast development** - No database server to manage
- **Easy testing** - In-memory databases for tests
- **Simple deployment** - Single container deployment
- **Low resource usage** - Minimal memory/CPU overhead

### Negative

- **Concurrency limits** - SQLite handles fewer concurrent writes
- **No advanced features** - Missing PostgreSQL extensions
- **Migration required** - Production will need PostgreSQL

### Migration Path

1. SQLAlchemy abstracts database details
2. Same model definitions work with PostgreSQL
3. Environment variable switches database URL
4. Alembic migrations portable across dialects

```python
# Development
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# Production
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```
