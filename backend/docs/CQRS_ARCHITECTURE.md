# CQRS Architecture

Command Query Responsibility Segregation (CQRS) implementation for read/write separation.

## Overview

```
Write Path: POST/PUT/DELETE → CommandBusDep → WriteDBSession → PostgreSQL Primary
Read Path:  GET → QueryBusDep → ReadDBSession/DuckDB → Parquet/PostgreSQL Replica
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Routes                                │
│  (features/process_mining/*, platform/*)                            │
└────────┬────────────────────────────────┬───────────────────────────┘
         │                                │
    COMMANDS                          QUERIES
    (POST/PUT/DELETE)                 (GET)
         │                                │
         ▼                                ▼
┌─────────────────────┐        ┌─────────────────────┐
│   CommandBusDep     │        │    QueryBusDep      │
│ (request-scoped)    │        │  (request-scoped)   │
└─────────┬───────────┘        └─────────┬───────────┘
          │                              │
          ▼                              ▼
┌─────────────────────┐        ┌─────────────────────┐
│  CommandHandlers    │        │   QueryHandlers     │
│  - IngestDataset    │        │   - GetBottlenecks  │
│  - DeleteDataset    │        │   - GetCycleTime    │
│  - CreateDataset    │        │   - GetVariants     │
│  - UpdateMapping    │        │   - GetRework       │
└─────────┬───────────┘        └─────────┬───────────┘
          │                              │
          ▼                              ├──────────────┐
┌─────────────────────┐        ┌────────▼─────┐ ┌─────▼──────┐
│  WriteDBSession     │        │ ReadDBSession │ │  DuckDB    │
│  (PostgreSQL)       │        │ (PostgreSQL)  │ │ (Parquet)  │
└─────────────────────┘        └──────────────┘ └────────────┘
          │
          ▼
┌─────────────────────┐
│   EventPublisher    │ ──────▶ AnalyticsCacheProjection
│  (Domain Events)    │           (cache invalidation)
└─────────────────────┘
```

## Components

### Database Sessions

| Type | Usage | Connection |
|------|-------|------------|
| `WriteDBSession` | Commands (POST, PUT, DELETE) | PostgreSQL Primary |
| `ReadDBSession` | Queries (GET) | PostgreSQL Replica (optional) |
| `AnalyticsDB` | OLAP queries | DuckDB in-memory |

### CQRS Bus Dependencies

```python
from src.api.dependencies import CommandBusDep, QueryBusDep

# Command example
@router.post("/datasets/{id}/ingest")
async def ingest_dataset(
    dataset_id: str,
    command_bus: CommandBusDep,
):
    result = await command_bus.dispatch(
        IngestDatasetCommand(dataset_id=dataset_id)
    )
    return result

# Query example
@router.get("/analytics/datasets/{id}/bottlenecks")
async def get_bottlenecks(
    dataset_id: str,
    query_bus: QueryBusDep,
):
    result = await query_bus.dispatch(
        GetBottlenecksQuery(dataset_id=dataset_id)
    )
    return result
```

### Commands (`src/application/commands/`)

| Command | Handler | Description |
|---------|---------|-------------|
| `IngestDatasetCommand` | `IngestDatasetHandler` | Trigger dataset ingestion |
| `DeleteDatasetCommand` | `DeleteDatasetHandler` | Delete with cache cleanup |
| `CreateDatasetCommand` | `CreateDatasetHandler` | Create new dataset |
| `UpdateMappingCommand` | `UpdateMappingHandler` | Update column mapping |
| `TriggerIngestionCommand` | `TriggerIngestionHandler` | Start ingestion workflow |

### Queries (`src/application/queries/`)

| Query | Handler | Data Source |
|-------|---------|-------------|
| `GetBottlenecksQuery` | `GetBottlenecksHandler` | DuckDB → Parquet |
| `GetCycleTimeQuery` | `GetCycleTimeHandler` | DuckDB → Parquet |
| `GetVariantsQuery` | `GetVariantsHandler` | DuckDB → Parquet |
| `GetReworkQuery` | `GetReworkHandler` | DuckDB → Parquet |

### Domain Events (`src/platform/core/domain_events.py`)

| Event | Trigger | Effect |
|-------|---------|--------|
| `DatasetIngestedEvent` | Ingestion complete | Cache population |
| `DatasetDeletedEvent` | Dataset deleted | Cache invalidation |

### Projection (`src/application/projections/`)

- `AnalyticsCacheProjection` - Pre-computes analytics on events

## Configuration

```env
# Primary database (required)
DATABASE_URL=sqlite+aiosqlite:///./data/db/process_mining.db

# Optional read replica (defaults to primary)
READ_DATABASE_URL=sqlite+aiosqlite:///./data/db/process_mining.db

# Connection pool sizes
WRITE_POOL_SIZE=10
READ_POOL_SIZE=50
```

## Key Files

| File | Purpose |
|------|---------|
| `src/application/bootstrap.py` | CQRS initialization and bus factories |
| `src/application/commands/base.py` | Command infrastructure |
| `src/application/queries/base.py` | Query infrastructure |
| `src/api/dependencies.py` | FastAPI dependency injection |
| `src/platform/infrastructure/database.py` | Session separation |
| `src/platform/infrastructure/duckdb.py` | DuckDB manager |
| `src/platform/core/domain_events.py` | Event infrastructure |
| `src/application/projections/analytics_cache.py` | Event projections |

## Best Practices

1. **Use CommandBusDep for writes**: All POST/PUT/PATCH/DELETE operations
2. **Use QueryBusDep for reads**: All GET operations with analytics
3. **Use ReadDBSession for simple reads**: GET operations that don't need DuckDB
4. **Never mix read/write sessions**: Each operation should use one session type
5. **Emit events after successful commands**: For read model synchronization

## Migration Guide

### Before (Legacy)
```python
from src.api.dependencies import DBSession, ServiceContainer

@router.get("/bottlenecks")
async def get_bottlenecks(db: DBSession, container: ServiceContainer):
    return container.analytics.detect_bottlenecks(...)
```

### After (CQRS)
```python
from src.api.dependencies import QueryBusDep

@router.get("/bottlenecks")
async def get_bottlenecks(query_bus: QueryBusDep):
    return await query_bus.dispatch(GetBottlenecksQuery(...))
```
