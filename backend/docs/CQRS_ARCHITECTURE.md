# CQRS Architecture

Command Query Responsibility Segregation (CQRS) implementation separating read and write paths.

## Architecture

```
Write Path: POST/PUT/DELETE → WriteDBSession → PostgreSQL → EventPublisher
Read Path:  GET → ReadDBSession (replica) + AnalyticsDB (DuckDB/Parquet)
```

## Components

### Database Pools
- `WriteDBSession`: Transactional writes to primary
- `ReadDBSession`: Read-only queries (can use replica)
- `AnalyticsDB`: DuckDB for OLAP on Parquet files

### Commands (`src/application/commands/`)
- `IngestDatasetCommand`: Trigger dataset ingestion
- `DeleteDatasetCommand`: Delete with cache cleanup

### Queries (`src/application/queries/`)
- `GetBottlenecksQuery`: DuckDB bottleneck analysis
- `GetCycleTimeQuery`: DuckDB cycle time stats  
- `GetVariantsQuery`: DuckDB process variants

### Events (`src/platform/core/domain_events.py`)
- `DatasetIngestedEvent`: Triggers cache population
- `DatasetDeletedEvent`: Triggers cache invalidation

### Projection (`src/application/projections/`)
- `AnalyticsCacheProjection`: Pre-compute analytics on events

## Usage

```python
# Write operation
@router.delete("/datasets/{id}")
async def delete_dataset(id: str, db: WriteDBSession):
    handler = DeleteDatasetHandler(db)
    return await handler.handle(DeleteDatasetCommand(dataset_id=id))

# Read operation (DuckDB)
@router.get("/analytics/bottlenecks")
async def get_bottlenecks(id: str, db: ReadDBSession, duckdb: AnalyticsDB):
    handler = GetBottlenecksHandler(db, duckdb)
    return await handler.handle(GetBottlenecksQuery(dataset_id=id))
```

## Configuration

```env
# Optional read replica (defaults to primary)
READ_DATABASE_URL=postgresql+asyncpg://user:pass@replica:5432/db
WRITE_POOL_SIZE=10
READ_POOL_SIZE=50
```
