# CQRS Architecture

Command Query Responsibility Segregation (CQRS) implementation for read/write separation.

## Overview

```
Write Path: POST/PUT/DELETE → WriteDBSession → PostgreSQL Primary
Read Path:  GET → ReadDBSession → PostgreSQL (replica optional) + AnalyticsDB → DuckDB/Parquet
```

## Components

### Database Sessions
| Type | Use Case |
|------|----------|
| `WriteDBSession` | Mutations (POST, PUT, DELETE) |
| `ReadDBSession` | Queries (GET) - can use read replica |
| `AnalyticsDB` | DuckDB for OLAP on Parquet files |

### Commands (`src/application/commands/`)
- `IngestDatasetCommand` - Trigger dataset ingestion
- `DeleteDatasetCommand` - Delete with cache cleanup

### Queries (`src/application/queries/`)
- `GetBottlenecksQuery` - DuckDB bottleneck analysis
- `GetCycleTimeQuery` - DuckDB cycle time stats
- `GetVariantsQuery` - DuckDB process variants

### Events (`src/platform/core/domain_events.py`)
- `DatasetIngestedEvent` - Triggers cache population
- `DatasetDeletedEvent` - Triggers cache invalidation

### Projection
- `AnalyticsCacheProjection` - Pre-computes analytics on events

## Configuration

```env
# Optional read replica (defaults to primary)
READ_DATABASE_URL=postgresql+asyncpg://user:pass@replica:5432/db
WRITE_POOL_SIZE=10
READ_POOL_SIZE=50
```

## Migration Status

### ✅ Completed
- Base infrastructure (commands, queries, buses)
- Separate database connection pools
- Domain events for read model sync
- All routers migrated to CQRS sessions (~130 usages)
- Command and query handlers implemented
- Analytics cache projection

### Files Modified
- 44 router files migrated from `DBSession` → `ReadDBSession`/`WriteDBSession`
- All process_mining and platform routers updated
