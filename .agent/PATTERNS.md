# Patterns — The "Do It This Way" Guide

> These patterns are established in this codebase. Don't invent new ones.

---

## 1. Error Handling

### ❌ DON'T (AI Default)

```python
try:
    result = await do_something()
except Exception as e:
    print(f"Error: {e}")
    return {"error": str(e)}
```

### ✅ DO (Our Pattern)

```python
from src.core.exceptions import ValidationError, NotFoundError, ProcessingError

# For validation failures
if not valid_input:
    raise ValidationError("Invalid input format", field="case_id")

# For missing resources
log = await db.get(EventLog, log_id)
if not log:
    raise NotFoundError("EventLog", log_id)

# For processing errors
try:
    result = pm4py.discover_petri_net_inductive(log)
except PM4PyException as e:
    raise ProcessingError(f"Discovery failed: {e}")
```

**Why**: Centralized error handling in `main.py`, consistent API responses, automatic logging.

---

## 2. Database Access

### ❌ DON'T

```python
# In router - synchronous, no session management
from sqlalchemy import create_engine
engine = create_engine("sqlite:///db.sqlite")
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM event_logs")
```

### ✅ DO

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.api.dependencies import get_db
from src.models.orm import EventLog

@router.get("/logs/{log_id}")
async def get_log(log_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EventLog).where(EventLog.id == log_id))
    log = result.scalar_one_or_none()
    if not log:
        raise NotFoundError("EventLog", log_id)
    return log
```

**Why**: Async for performance, dependency injection for testing, ORM for type safety.

---

## 3. Logging

### ❌ DON'T

```python
print(f"Processing log {log_id}")
import logging
logging.info("Done")
```

### ✅ DO

```python
import structlog
import time

logger = structlog.get_logger(__name__)

async def process_log(log_id: str):
    logger.info("processing_started", log_id=log_id)

    start = time.time()
    result = await expensive_operation()
    duration = time.time() - start

    logger.info("processing_completed", log_id=log_id, duration_ms=duration*1000)
```

**Why**: Structured JSON logging in production, correlation IDs, performance tracking.

---

## 4. API Responses

### ❌ DON'T

```python
@router.get("/logs/{log_id}")
async def get_log(log_id: str):
    return {"id": log_id, "name": "test", "events": 100}  # Plain dict
```

### ✅ DO

```python
from src.models.schemas import ProcessResponse

@router.get("/logs/{log_id}", response_model=ProcessResponse)
async def get_log(log_id: str, db: AsyncSession = Depends(get_db)):
    log = await _fetch_log(log_id, db)
    return ProcessResponse(
        id=log.id,
        name=log.name,
        total_events=log.total_events,
        # ...all required fields
    )
```

**Why**: Type safety, automatic OpenAPI generation, consistent response shape.

---

## 5. PM4Py Integration

### ❌ DON'T

```python
# In router - mixing HTTP concerns with PM4Py
@router.post("/discover")
async def discover(log_id: str):
    import pm4py
    # Load data, convert, process all in router
    net, im, fm = pm4py.discover_petri_net_inductive(log)
    return {"places": len(net.places)}
```

### ✅ DO

```python
# In router - thin, delegates to service
@router.post("/discover")
async def discover(log_id: str, request: DiscoverRequest, db: AsyncSession = Depends(get_db)):
    pm4py_log, event_log = await _get_pm4py_log(log_id, db)
    result = mining_service.discover_model(pm4py_log, request.miner_type)
    return DiscoveryResponse(**result)

# In services/mining.py - all PM4Py logic
class MiningService:
    def discover_model(self, pm4py_log, miner_type: MinerType) -> dict:
        if miner_type == MinerType.INDUCTIVE:
            net, im, fm = pm4py.discover_petri_net_inductive(pm4py_log)
        # ... transform and return
```

**Why**: Separation of concerns, testable services, reusable PM4Py wrappers.

---

## 6. Service Pattern

### ❌ DON'T

```python
# Stateless functions scattered everywhere
def analyze_bottlenecks(log):
    ...

def get_statistics(log):
    ...
```

### ✅ DO

```python
# Singleton service instance
class AnalyticsService:
    """Bottleneck detection and performance analytics."""

    def detect_bottlenecks(self, pm4py_log) -> dict:
        ...

    def get_statistics(self, pm4py_log) -> dict:
        ...

# Export singleton
analytics_service = AnalyticsService()

# In router
from src.services.analytics import analytics_service
result = analytics_service.detect_bottlenecks(log)
```

**Why**: Grouped related logic, easier testing, consistent naming.

---

## 7. File Uploads

### ❌ DON'T

```python
@router.post("/upload")
async def upload(file: UploadFile):
    with open(f"/tmp/{file.filename}", "wb") as f:
        f.write(await file.read())
```

### ✅ DO

```python
from src.storage.file_storage import file_storage

@router.post("/upload")
async def upload(file: UploadFile, db: AsyncSession = Depends(get_db)):
    # Validate file type
    if not file.filename.endswith(('.csv', '.xes')):
        raise InvalidFileError("Only CSV and XES files are supported")

    # Use storage service
    file_path = await file_storage.save_upload(file)

    # Process via ingestion service
    result = await ingestion_service.process_file(file_path, db)
    return ProcessResponse.from_orm(result)
```

**Why**: Proper file handling, validation, storage abstraction.
