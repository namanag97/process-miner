# Deferred Ingestion - Implementation Complete

## Flow
```
Upload → UNSTRUCTURED → /ingest (with mapping) → ANALYZING → READY → Analysis
```

## Status Enum
```python
UNSTRUCTURED | ANALYZING | READY | ERROR | ARCHIVED
```

## Completed Changes

| File | Status |
|------|--------|
| `src/models/orm.py` | ✅ DatasetStatus enum + mapping_json field |
| `src/models/schemas.py` | ✅ IngestRequest + status field in DatasetResponse |
| `src/services/ingestion.py` | ✅ store_only() method |
| `src/services/duckdb_ingestion.py` | ✅ _get_manager() method added |
| `src/api/routers/datasets.py` | ✅ async_store param + POST /{id}/ingest |
| `src/infrastructure/tasks.py` | ✅ ingest_dataset_task |
| `alembic/versions/008_*.py` | ✅ Migration for mapping_json |
| `tests/test_deferred_ingestion.py` | ✅ Test suite |

## API Endpoints

### Upload (async)
```bash
POST /datasets/upload
Form: file, name, project_id, async_store=true
Response: {id, status: "unstructured", ...}
```

### Trigger Ingestion
```bash
POST /datasets/{id}/ingest
Body: {"case_id_column": "X", "activity_column": "Y", "timestamp_column": "Z"}
Response: {job_id, status: "pending", ...}
```

## Run Migration
```bash
alembic upgrade head
```

## Start Celery Worker
```bash
celery -A src.infrastructure.tasks worker --loglevel=info
```
