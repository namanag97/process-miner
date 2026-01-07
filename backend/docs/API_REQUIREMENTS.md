# FastAPI Best Practices & Requirements

## 1. Async/Sync Decision Matrix

### Use `async def` when:
- Database operations (SQLAlchemy async sessions)
- External HTTP calls (httpx)
- File I/O with aiofiles
- Redis/cache operations
- S3/MinIO operations
- Any I/O-bound operation

### Use `def` (sync) when:
- CPU-bound computations (PM4Py algorithms, ML inference)
- Operations that call sync-only libraries
- Simple request validation without I/O

```python
# ✅ GOOD: Async for I/O
@router.get("/datasets/{id}")
async def get_dataset(id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dataset).where(Dataset.id == id))
    return result.scalar_one_or_none()

# ✅ GOOD: Sync for CPU-bound (FastAPI runs in threadpool)
@router.post("/discover")
def discover_process(data: DiscoveryRequest):
    # PM4Py is CPU-bound, sync is fine
    return pm4py.discover_petri_net_inductive(event_log)

# ❌ BAD: Blocking call in async function
@router.get("/data")
async def get_data():
    result = requests.get(url)  # Blocks the event loop!
```

---

## 2. Temporal Workflows - When to Use

### Use Temporal for:
- **Long-running operations** (>30 seconds): Data ingestion, ML training
- **Multi-step pipelines**: ETL, batch processing
- **Operations requiring retry/resume**: External API calls, file processing
- **Scheduled/recurring jobs**: Daily reports, data sync
- **Saga patterns**: Multi-service transactions with compensation

### DON'T use Temporal for:
- Simple CRUD operations
- Quick queries (<1 second)
- Real-time user interactions
- Simple async background tasks (use Celery instead)

```python
# ✅ GOOD: Temporal for complex data pipeline
@workflow.defn
class DataIngestionWorkflow:
    @workflow.run
    async def run(self, dataset_id: str) -> IngestionResult:
        # Step 1: Validate file
        validation = await workflow.execute_activity(
            validate_file,
            dataset_id,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # Step 2: Parse and transform (long-running)
        parsed = await workflow.execute_activity(
            parse_event_log,
            dataset_id,
            start_to_close_timeout=timedelta(hours=1),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        # Step 3: Load into DuckDB
        return await workflow.execute_activity(
            load_to_duckdb,
            parsed,
            start_to_close_timeout=timedelta(minutes=30),
        )

# ❌ BAD: Temporal for simple operation
@workflow.defn
class GetUserWorkflow:  # Overkill!
    @workflow.run
    async def run(self, user_id: str):
        return await workflow.execute_activity(get_user, user_id)
```

### Temporal Activity Best Practices:
```python
@activity.defn
async def process_large_file(file_id: str) -> ProcessResult:
    # 1. Use heartbeats for long operations
    for chunk in chunks:
        activity.heartbeat(f"Processing chunk {i}")
        await process_chunk(chunk)

    # 2. Make activities idempotent
    # 3. Keep activities focused (single responsibility)
    # 4. Use appropriate timeouts
```

---

## 3. Parquet & DuckDB - When to Use

### Use Parquet/DuckDB for:
- **Large datasets** (>10MB, >100K rows)
- **Columnar analytics**: Aggregations, filtering, grouping
- **Event log storage**: Process mining data
- **Batch data export**: Reports, data downloads
- **OCEL 2.0 data**: Object-centric event logs

### Use SQLite/PostgreSQL for:
- **Transactional data**: Users, projects, settings
- **Frequent updates**: Status changes, metadata
- **Relational queries**: Joins across entities
- **Small datasets**: Configuration, audit logs

```python
# ✅ GOOD: DuckDB for analytics on large event logs
async def get_activity_statistics(dataset_id: UUID) -> ActivityStats:
    conn = duckdb.connect()
    result = conn.execute("""
        SELECT
            activity,
            COUNT(*) as frequency,
            AVG(duration_seconds) as avg_duration
        FROM read_parquet(?)
        GROUP BY activity
        ORDER BY frequency DESC
    """, [f"data/{dataset_id}/events.parquet"]).fetchdf()
    return ActivityStats.from_dataframe(result)

# ✅ GOOD: Parquet for data export
async def export_dataset(dataset_id: UUID, format: str) -> str:
    if format == "parquet":
        # Efficient columnar format
        df.to_parquet(f"exports/{dataset_id}.parquet", compression="snappy")
    elif format == "csv":
        # For compatibility
        df.to_csv(f"exports/{dataset_id}.csv")

# ❌ BAD: Parquet for small config data
def save_user_preferences(user_id: str, prefs: dict):
    df = pd.DataFrame([prefs])
    df.to_parquet(f"prefs/{user_id}.parquet")  # Overkill!
```

### Data Ingestion Pipeline Pattern:
```python
async def ingest_event_log(file_path: str, dataset_id: UUID):
    # 1. Use DuckDB for fast CSV/Excel parsing
    conn = duckdb.connect()

    # 2. Detect schema automatically
    schema = conn.execute(f"DESCRIBE SELECT * FROM '{file_path}'").fetchall()

    # 3. Transform to standardized format
    conn.execute(f"""
        COPY (
            SELECT
                case_id,
                activity,
                timestamp,
                resource
            FROM '{file_path}'
        ) TO 'data/{dataset_id}/events.parquet' (FORMAT PARQUET)
    """)

    # 4. Compute statistics
    stats = conn.execute(f"""
        SELECT
            COUNT(DISTINCT case_id) as cases,
            COUNT(*) as events,
            COUNT(DISTINCT activity) as activities
        FROM 'data/{dataset_id}/events.parquet'
    """).fetchone()

    return IngestionResult(cases=stats[0], events=stats[1], activities=stats[2])
```

---

## 4. API Design Requirements

### Response Standards
```python
# Use RFC 7807 Problem Details for errors
class ProblemDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None

# Consistent success responses
class ApiResponse(BaseModel, Generic[T]):
    data: T
    meta: Optional[ResponseMeta] = None

class ResponseMeta(BaseModel):
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None
```

### Pagination (Cursor-based for large datasets)
```python
@router.get("/events")
async def list_events(
    dataset_id: UUID,
    cursor: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
) -> PaginatedResponse[Event]:
    # Use cursor-based for performance with large datasets
    events, next_cursor = await event_service.list_paginated(
        dataset_id, cursor=cursor, limit=limit
    )
    return PaginatedResponse(data=events, next_cursor=next_cursor)
```

### Background Job Pattern
```python
# For operations 5-30 seconds: Return job ID, poll for status
@router.post("/datasets/{id}/analyze", status_code=202)
async def start_analysis(id: UUID) -> JobResponse:
    job = await job_service.create(
        job_type="analysis",
        payload={"dataset_id": str(id)}
    )
    # Submit to Celery (short) or Temporal (long)
    if estimated_duration < timedelta(minutes=5):
        celery_app.send_task("run_analysis", args=[str(job.id)])
    else:
        await temporal_client.start_workflow(AnalysisWorkflow.run, str(job.id))

    return JobResponse(job_id=job.id, status="pending")

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: UUID) -> JobStatus:
    return await job_service.get_status(job_id)
```

---

## 5. Dependency Injection Patterns

```python
# Database sessions
async def get_read_db() -> AsyncGenerator[AsyncSession, None]:
    """Read-only session for queries."""
    async with async_session_factory() as session:
        yield session

async def get_write_db() -> AsyncGenerator[AsyncSession, None]:
    """Write session with auto-commit."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Service injection
def get_dataset_service(
    db: AsyncSession = Depends(get_write_db),
    storage: StorageService = Depends(get_storage),
) -> DatasetService:
    return DatasetService(db=db, storage=storage)

# Use in routes
@router.post("/datasets")
async def create_dataset(
    request: CreateDatasetRequest,
    service: DatasetService = Depends(get_dataset_service),
) -> DatasetResponse:
    return await service.create(request)
```

---

## 6. Error Handling

```python
# Custom exceptions
class AppException(Exception):
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 400,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

# Global exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": f"/errors/{exc.error_code.value}",
            "title": exc.error_code.name,
            "status": exc.status_code,
            "detail": exc.message,
            "instance": str(request.url),
            **exc.details,
        },
    )

# Service-level error handling
async def get_dataset(id: UUID) -> Dataset:
    dataset = await repo.get(id)
    if not dataset:
        raise AppException(
            message=f"Dataset {id} not found",
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            status_code=404,
        )
    return dataset
```

---

## 7. Performance Checklist

- [ ] Use `async def` for all I/O operations
- [ ] Use connection pooling for databases
- [ ] Implement response caching (Redis) for expensive queries
- [ ] Use streaming responses for large data exports
- [ ] Implement rate limiting (slowapi)
- [ ] Use background tasks for operations >1 second
- [ ] Use Temporal for operations >5 minutes
- [ ] Use Parquet/DuckDB for datasets >10MB
- [ ] Implement pagination for list endpoints
- [ ] Use appropriate indexes on database queries

---

## 8. Security Requirements

- [ ] Validate all inputs with Pydantic
- [ ] Use parameterized queries (SQLAlchemy ORM)
- [ ] Implement authentication on all endpoints
- [ ] Use RBAC for authorization
- [ ] Rate limit sensitive endpoints
- [ ] Sanitize file uploads
- [ ] Never expose internal errors to clients
- [ ] Use HTTPS in production
- [ ] Implement CORS properly
