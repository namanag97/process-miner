# Data Layer Architecture Change

**Date**: 2026-01-07  
**Status**: Complete

## What Changed (Summary)

**Before:** Events were stored TWICE - in PostgreSQL tables (`process_cases`, `process_events`) AND as Parquet files in S3. Analytics read from PostgreSQL, making Parquet unused.

**After:** Events are stored ONLY as Parquet files. Analytics reads directly from Parquet via DuckDB. PostgreSQL stores only metadata (dataset info, user data). Supports both local filesystem and S3/MinIO.

---

## Architecture

| Before | After |
|--------|-------|
| CSV → PostgreSQL + S3 (dual-write) | CSV → Parquet only |
| Analytics reads PostgreSQL | Analytics reads Parquet via DuckDB |
| `bulk_copy_to_db_activity` | Removed |

## Storage Paths

| Mode | Path |
|------|------|
| Local MVP | `./data/storage/pm-cache-dev/parsed/{id}/events.parquet` |
| S3/MinIO | `s3://pm-cache-dev/parsed/{id}/events.parquet` |

## Files Changed

| File | Change |
|------|--------|
| `workflows/ingestion.py` | Removed bulk_copy step |
| `activities/dataset.py` | Mandatory Parquet write |
| `services/loader.py` | Reads Parquet (local + S3) |
| `tests/...test_ingestion_workflow.py` | Updated expectations |

---

## Data Ownership Matrix

| Entity | Authoritative Store | Writes To | Reads From |
|--------|---------------------|-----------|------------|
| Organizations | PostgreSQL | PostgreSQL | PostgreSQL |
| Workspaces | PostgreSQL | PostgreSQL | PostgreSQL |
| Datasets (metadata) | PostgreSQL | PostgreSQL | PostgreSQL |
| **Events** | **Parquet** | **Parquet only** | Parquet via DuckDB |
| **Cases** | **Parquet** | **Parquet only** | Parquet via DuckDB |
| Process Models | PostgreSQL | PostgreSQL | PostgreSQL |
| DFG Cache | Redis | Redis | Redis |
| DuckDB | N/A (ephemeral) | Never | Parquet, PostgreSQL |

---

## Automated Testing

Run the ownership verification tests:
```bash
cd backend
pytest tests/integration/test_data_ownership.py -v
```

**What it tests:**
- ✓ Ingestion creates Parquet, NOT PostgreSQL events
- ✓ Loader reads from Parquet
- ✓ DuckDB connections are ephemeral (in-memory)
- ✓ `bulk_copy_to_db_activity` is removed from workflow
- ✓ Parquet write is mandatory (no fallback)

---

## Next Steps

1. **Run migration** (for existing datasets):
   ```bash
   python scripts/migrate_events_to_parquet.py --dry-run
   python scripts/migrate_events_to_parquet.py
   ```

2. **Delete legacy code** (after migration):
   - `ProcessCase` and `ProcessEvent` models
   - `process_cases` and `process_events` tables (Alembic migration)

3. **Remove fallback** (after verification):
   - Remove `_load_from_sqlite_legacy()` methods from loader
