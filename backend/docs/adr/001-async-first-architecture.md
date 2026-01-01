# ADR-001: Async-First Architecture

## Status

Accepted

## Context

The Process Mining backend needs to handle:

- Large file uploads (event logs with millions of events)
- Long-running process discovery algorithms
- Concurrent API requests from multiple users
- Database queries that may take several seconds

Traditional synchronous Python web frameworks block threads during I/O operations, limiting concurrency and wasting resources.

## Decision

We adopt an **async-first architecture** using:

1. **FastAPI** - Native async support with high-performance automatic validation
2. **async/await** - Throughout the codebase for all I/O operations
3. **aiosqlite** - Async SQLite driver for development
4. **Celery** - For truly long-running tasks that exceed request timeouts

### Key Patterns

```python
# All database operations are async
async def get_process(db: AsyncSession, process_id: str) -> EventLog:
    result = await db.get(EventLog, process_id)
    return result

# All service layer methods are async
async def discover_model(log_id: str, miner_type: str) -> ProcessModel:
    async with get_session() as db:
        log = await get_process(db, log_id)
        # PM4Py operations run in thread pool
        model = await asyncio.to_thread(pm4py.discover, log.to_df())
        return model
```

### Sync/Async Boundary

PM4Py operations are CPU-bound and synchronous. We bridge this with:

- `asyncio.to_thread()` for short operations
- Celery tasks for long operations (> 30 seconds)

## Consequences

### Positive

- **High concurrency** - Single process handles thousands of concurrent connections
- **Efficient resource usage** - No thread-per-request overhead
- **Modern Python** - Uses latest language features
- **Better performance** - 3-5x faster than sync for I/O-bound workloads

### Negative

- **Learning curve** - Developers must understand async patterns
- **Sync/async boundary** - PM4Py integration requires careful handling
- **Debugging complexity** - Async stack traces can be harder to read
- **Testing** - Requires pytest-asyncio and async test fixtures

### Neutral

- Integration with sync libraries (PM4Py, pandas) requires explicit bridging
- Some ecosystem tools don't support async yet
