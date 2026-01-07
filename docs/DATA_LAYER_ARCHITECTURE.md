# Data Layer Architecture - Audit & Migration Plan

## PHASE 1: AUDIT FINDINGS

### Current Data Write Paths

| Data Type | Destination | Trigger | File/Function |
|-----------|-------------|---------|---------------|
| Raw CSV/XES files | S3 `raw` bucket | Upload API | `object_storage.py:upload_fileobj()` |
| Parsed events (Parquet) | S3 `cache` bucket | Ingestion workflow | `activities/dataset.py:parse_to_parquet_activity()` |
| Parsed events (SQLite) | `process_events` table | Ingestion workflow | `activities/dataset.py:bulk_copy_to_db_activity()` |
| Parsed cases (SQLite) | `process_cases` table | Ingestion workflow | `activities/dataset.py:bulk_copy_to_db_activity()` |
| Dataset metadata | `datasets` table | Throughout lifecycle | Multiple services |
| Process models | `process_models` table + S3 `models` bucket | Discovery | `writer.py`, serialization |

### Current Data Read Paths

| Data Type | Source | Reader | File/Function |
|-----------|--------|--------|---------------|
| Event data for analytics | SQLite via DuckDB ATTACH | `EventLogLoader` | `loader.py:load_as_dataframe()` |
| DFG computation | SQLite via DuckDB ATTACH | `EventLogLoader` | `loader.py:load_dfg()` |
| Variants | SQLite via DuckDB ATTACH | `EventLogLoader` | `loader.py:load_variants()` |
| Statistics | SQLite via DuckDB ATTACH | `EventLogLoader` | `loader.py:load_statistics()` |
| PM4Py logs | SQLite via DuckDB → DataFrame → PM4Py | `EventLogLoader` | `loader.py:load_as_pm4py_log()` |

### CRITICAL ISSUE: Dual Write with Unused Parquet

```
CSV Upload → DuckDB Parse → Arrow Tables
                              │
          ┌───────────────────┴───────────────────┐
          ↓                                       ↓
    S3 Parquet (cache)                  SQLite (process_events/cases)
    "parsed/{id}/events.parquet"        bulk_copy_to_db_activity()
          │                                       │
          │ (WRITE SUCCESS = optional)            │ (WRITE = required)
          │ (NEVER READ!)                         │ (ALWAYS READ!)
          ↓                                       ↓
       UNUSED                              loader.py reads this
```

**Problems:**
1. **Dual write overhead** - Every ingestion writes to both S3 and SQLite
2. **Parquet never read** - `parquet_s3_key` stored in `datasets` table but analytics don't use it
3. **SQLite bottleneck** - All reads go through SQLite, limiting scalability
4. **Non-atomic** - Parquet failure logged as warning, SQLite write is required
5. **Wrong bucket** - Parquet in "cache" bucket (meant for ephemeral data)

### Files Involved in Writes

```
WRITES TO SQLITE (process_events, process_cases):
- backend/src/platform/temporal/activities/dataset.py:388-491  (bulk_copy_to_db_activity)
- backend/src/features/process_mining/ingestion/service.py:391-432 (_create_dataset)

WRITES TO S3 PARQUET:
- backend/src/platform/temporal/activities/dataset.py:315-351 (parse_to_parquet_activity)

STORES parquet_s3_key BUT NEVER READS:
- backend/src/features/process_mining/models/dataset.py:77 (Dataset.parquet_s3_key)
- backend/src/platform/temporal/activities/dataset.py:543-546 (compute_statistics_activity)
```

### Files Involved in Reads

```
ALL READS GO THROUGH loader.py:
- backend/src/features/process_mining/services/loader.py

SERVICES THAT USE loader.py:
- MiningService.discover() → loader.load_as_pm4py_log()
- MiningService.discover_fast() → loader.load_as_dataframe()
- MiningService.get_dfg_fast() → loader.load_dfg()
- MiningService.get_variants_fast() → loader.load_variants()
- AnalyticsService.* → receives PM4PyLog from caller (which came from loader)
```

---

## PHASE 2: TARGET OWNERSHIP MODEL

### Clear Data Ownership

```
┌─────────────────────────────────────────────────────────────────────┐
│                     POSTGRESQL/SQLITE                                │
│                (Source of Truth for Business Entities)               │
├─────────────────────────────────────────────────────────────────────┤
│  • Organizations, Workspaces, Projects, Users                        │
│  • Datasets (metadata ONLY):                                         │
│    - id, name, status, config                                        │
│    - parquet_s3_key (pointer to S3)                                  │
│    - total_cases, total_events (cached stats)                        │
│  • ProcessModels (metadata + serialized_model BLOB)                  │
│  • AsyncJobs, audit logs, etc.                                       │
│                                                                      │
│  NEVER STORE: process_events, process_cases                          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          S3/PARQUET                                  │
│                (Source of Truth for Event Data)                      │
├─────────────────────────────────────────────────────────────────────┤
│  RAW BUCKET (pm-raw-{env}):                                          │
│  • Original uploaded files: {org_id}/{dataset_id}/raw/{filename}     │
│                                                                      │
│  EVENTS BUCKET (pm-events-{env}) - NEW:                              │
│  • Parquet event files: {org_id}/{dataset_id}/events.parquet         │
│  • Parquet case files:  {org_id}/{dataset_id}/cases.parquet          │
│  • Immutable - new ingestion = new version                           │
│                                                                      │
│  MODELS BUCKET (pm-models-{env}):                                    │
│  • Serialized process models                                         │
│                                                                      │
│  CACHE BUCKET (pm-cache-{env}):                                      │
│  • DFG cache, computed graphs                                        │
│  • TTL-managed, not authoritative                                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        DUCKDB (Compute Layer)                        │
│                    (NEVER writes persistent state)                   │
├─────────────────────────────────────────────────────────────────────┤
│  READS FROM:                                                         │
│  • S3 Parquet (events) via read_parquet('s3://...')                  │
│  • PostgreSQL (metadata) when needed                                 │
│                                                                      │
│  WRITES TO:                                                          │
│  • NOTHING persistent                                                │
│  • Returns computed results in-memory                                │
│                                                                      │
│  USE FOR:                                                            │
│  • Analytics queries, aggregations, joins                            │
│  • DFG computation, variant analysis                                 │
│  • Filtering, sampling                                               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        REDIS (Cache Layer)                           │
├─────────────────────────────────────────────────────────────────────┤
│  • Session data                                                      │
│  • Rate limiting                                                     │
│  • Computed DFG cache (with TTL)                                     │
│  • NEVER authoritative                                               │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow After Migration

```
INGESTION:
CSV Upload → S3 raw bucket
         → DuckDB Parse
         → Parquet to S3 events bucket (ONLY destination for events)
         → Update datasets table (metadata + parquet_s3_key)

ANALYTICS:
Request → Load datasets metadata from DB
       → DuckDB read_parquet() from S3
       → Compute analytics
       → Return results

FAILURE MODES:
- S3 write fails → Ingestion fails (atomic, no partial state)
- DB metadata update fails → Ingestion fails (transaction rollback)
- DuckDB query fails → Return error (no state change)
```

---

## PHASE 3: MIGRATION IMPLEMENTATION

### Step 1: Create Parquet-Only Ingestion Pipeline

**New file: `backend/src/features/process_mining/ingestion/parquet_ingestion.py`**

```python
"""Parquet-Only Ingestion - Events stored exclusively in S3 Parquet."""

import io
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from temporalio import activity

from src.platform.infrastructure.object_storage import get_storage_client
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class ParquetIngestionService:
    """Ingestion service that writes events ONLY to S3 Parquet."""

    def __init__(self):
        self.storage = get_storage_client()

    async def ingest_to_parquet(
        self,
        dataset_id: str,
        org_id: str,
        events_arrow: pa.Table,
        cases_arrow: pa.Table,
    ) -> dict[str, Any]:
        """
        Ingest parsed events to S3 Parquet ONLY.

        NO SQLite writes. All event data goes to Parquet.
        """
        events_key = f"{org_id}/{dataset_id}/events.parquet"
        cases_key = f"{org_id}/{dataset_id}/cases.parquet"

        # Write events parquet
        events_buffer = io.BytesIO()
        pq.write_table(events_arrow, events_buffer, compression='snappy')
        events_bytes = events_buffer.getvalue()

        self.storage.upload_fileobj(
            bucket_type="events",  # NEW bucket for event data
            key=events_key,
            file_obj=io.BytesIO(events_bytes),
            content_type="application/vnd.apache.parquet",
        )

        # Write cases parquet
        cases_buffer = io.BytesIO()
        pq.write_table(cases_arrow, cases_buffer, compression='snappy')
        cases_bytes = cases_buffer.getvalue()

        self.storage.upload_fileobj(
            bucket_type="events",
            key=cases_key,
            file_obj=io.BytesIO(cases_bytes),
            content_type="application/vnd.apache.parquet",
        )

        # Compute statistics from Arrow tables (not from DB!)
        stats = self._compute_statistics(events_arrow, cases_arrow)

        logger.info(
            "parquet_ingestion_complete",
            dataset_id=dataset_id,
            events_key=events_key,
            events_size_mb=len(events_bytes) / (1024 * 1024),
            total_events=stats["total_events"],
            total_cases=stats["total_cases"],
        )

        return {
            "events_parquet_key": events_key,
            "cases_parquet_key": cases_key,
            "events_size_bytes": len(events_bytes),
            "cases_size_bytes": len(cases_bytes),
            **stats,
        }

    def _compute_statistics(
        self, events_arrow: pa.Table, cases_arrow: pa.Table
    ) -> dict[str, Any]:
        """Compute statistics from Arrow tables."""
        return {
            "total_events": events_arrow.num_rows,
            "total_cases": cases_arrow.num_rows,
            "total_activities": len(events_arrow.column("activity").unique()),
        }


parquet_ingestion_service = ParquetIngestionService()
```

### Step 2: Create Parquet-Reading Analytics Layer

**New file: `backend/src/features/process_mining/services/parquet_loader.py`**

```python
"""Parquet-based Event Log Loader - Reads directly from S3 Parquet."""

from typing import Any

import pandas as pd
import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog

from src.platform.core.config import get_settings
from src.platform.core.logging_config import get_logger
from src.platform.infrastructure.duckdb import duckdb_manager

logger = get_logger(__name__)
settings = get_settings()


class ParquetEventLogLoader:
    """
    High-performance event log loading from S3 Parquet.

    Uses DuckDB to read Parquet files directly from S3,
    bypassing the database entirely for event data.
    """

    def __init__(self):
        self.s3_endpoint = settings.s3_endpoint_url
        self.s3_region = settings.s3_region
        self.events_bucket = f"pm-events-{settings.environment}"

    def _get_parquet_url(self, parquet_key: str) -> str:
        """Get S3 URL for Parquet file."""
        if self.s3_endpoint:
            # MinIO/LocalStack
            return f"s3://{self.events_bucket}/{parquet_key}"
        else:
            # AWS S3
            return f"s3://{self.events_bucket}/{parquet_key}"

    def load_as_dataframe(
        self,
        parquet_key: str,
        max_events: int = 500000,
    ) -> pd.DataFrame:
        """Load events from S3 Parquet as PM4Py DataFrame."""
        logger.info("parquet_loader_started", parquet_key=parquet_key)

        conn = duckdb_manager.get_connection()

        try:
            # Configure S3 credentials for DuckDB
            conn.execute(f"""
                SET s3_region='{self.s3_region}';
                SET s3_access_key_id='{settings.s3_access_key_id}';
                SET s3_secret_access_key='{settings.s3_secret_access_key}';
            """)

            if self.s3_endpoint:
                conn.execute(f"SET s3_endpoint='{self.s3_endpoint}';")
                conn.execute("SET s3_url_style='path';")

            parquet_url = self._get_parquet_url(parquet_key)
            limit_clause = f"LIMIT {max_events}" if max_events > 0 else ""

            # Read directly from S3 Parquet
            df = conn.execute(f"""
                SELECT
                    case_id AS "case:concept:name",
                    activity AS "concept:name",
                    timestamp AS "time:timestamp",
                    resource AS "org:resource"
                FROM read_parquet('{parquet_url}')
                ORDER BY case_id, timestamp
                {limit_clause}
            """).df()

            # Format for PM4Py
            df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
            df = pm4py.format_dataframe(
                df,
                case_id="case:concept:name",
                activity_key="concept:name",
                timestamp_key="time:timestamp",
            )

            logger.info(
                "parquet_loader_completed",
                parquet_key=parquet_key,
                total_events=len(df),
            )

            return df

        finally:
            conn.close()

    def load_as_pm4py_log(self, parquet_key: str) -> PM4PyLog:
        """Load from Parquet and convert to PM4Py EventLog."""
        df = self.load_as_dataframe(parquet_key)
        if df.empty:
            return PM4PyLog()
        return pm4py.convert_to_event_log(df)

    def load_dfg(self, parquet_key: str) -> tuple[dict, dict[str, int], dict[str, int]]:
        """Compute DFG directly from Parquet using SQL."""
        conn = duckdb_manager.get_connection()

        try:
            self._configure_s3(conn)
            parquet_url = self._get_parquet_url(parquet_key)

            # DFG edges
            dfg_result = conn.execute(f"""
                WITH ordered_events AS (
                    SELECT
                        case_id,
                        activity,
                        LEAD(activity) OVER (
                            PARTITION BY case_id ORDER BY timestamp
                        ) as next_activity
                    FROM read_parquet('{parquet_url}')
                )
                SELECT activity, next_activity, COUNT(*) as freq
                FROM ordered_events
                WHERE next_activity IS NOT NULL
                GROUP BY activity, next_activity
            """).fetchall()

            dfg = {(row[0], row[1]): row[2] for row in dfg_result}

            # Start activities
            start_result = conn.execute(f"""
                WITH first_events AS (
                    SELECT
                        case_id,
                        activity,
                        ROW_NUMBER() OVER (PARTITION BY case_id ORDER BY timestamp) as rn
                    FROM read_parquet('{parquet_url}')
                )
                SELECT activity, COUNT(*) as freq
                FROM first_events WHERE rn = 1
                GROUP BY activity
            """).fetchall()

            start_activities = {row[0]: row[1] for row in start_result}

            # End activities
            end_result = conn.execute(f"""
                WITH last_events AS (
                    SELECT
                        case_id,
                        activity,
                        ROW_NUMBER() OVER (PARTITION BY case_id ORDER BY timestamp DESC) as rn
                    FROM read_parquet('{parquet_url}')
                )
                SELECT activity, COUNT(*) as freq
                FROM last_events WHERE rn = 1
                GROUP BY activity
            """).fetchall()

            end_activities = {row[0]: row[1] for row in end_result}

            return dfg, start_activities, end_activities

        finally:
            conn.close()

    def load_statistics(self, parquet_key: str) -> dict[str, Any]:
        """Load statistics directly from Parquet."""
        conn = duckdb_manager.get_connection()

        try:
            self._configure_s3(conn)
            parquet_url = self._get_parquet_url(parquet_key)

            stats = conn.execute(f"""
                SELECT
                    COUNT(*) as total_events,
                    COUNT(DISTINCT case_id) as total_cases,
                    COUNT(DISTINCT activity) as total_activities,
                    COUNT(DISTINCT resource) FILTER (WHERE resource IS NOT NULL) as total_resources,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time
                FROM read_parquet('{parquet_url}')
            """).fetchone()

            return {
                "total_events": stats[0],
                "total_cases": stats[1],
                "total_activities": stats[2],
                "total_resources": stats[3],
                "start_time": stats[4].isoformat() if stats[4] else None,
                "end_time": stats[5].isoformat() if stats[5] else None,
            }

        finally:
            conn.close()

    def _configure_s3(self, conn):
        """Configure DuckDB S3 credentials."""
        conn.execute(f"SET s3_region='{self.s3_region}';")
        conn.execute(f"SET s3_access_key_id='{settings.s3_access_key_id}';")
        conn.execute(f"SET s3_secret_access_key='{settings.s3_secret_access_key}';")
        if self.s3_endpoint:
            conn.execute(f"SET s3_endpoint='{self.s3_endpoint}';")
            conn.execute("SET s3_url_style='path';")


parquet_event_log_loader = ParquetEventLogLoader()
```

### Step 3: Migration Script

**New file: `backend/scripts/migrate_events_to_parquet.py`**

```python
"""
Migration Script: SQLite Events → S3 Parquet

Migrates existing event data from SQLite process_events/process_cases
tables to S3 Parquet files.

Usage:
    python scripts/migrate_events_to_parquet.py --dry-run
    python scripts/migrate_events_to_parquet.py --execute
"""

import argparse
import asyncio
import io
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import select, text

from src.features.process_mining.models import Dataset
from src.platform.infrastructure.database import AsyncSessionLocal
from src.platform.infrastructure.object_storage import get_storage_client
from src.platform.infrastructure.duckdb import duckdb_manager
from src.platform.core.config import get_settings

settings = get_settings()


async def get_datasets_to_migrate() -> list[dict[str, Any]]:
    """Get all datasets that have SQLite data but no Parquet."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Dataset).where(
                Dataset.status == "READY",
                Dataset.parquet_s3_key.is_(None),  # No Parquet yet
            )
        )
        datasets = result.scalars().all()
        return [
            {
                "id": d.id,
                "name": d.name,
                "project_id": d.project_id,
                "total_events": d.total_events,
                "total_cases": d.total_cases,
            }
            for d in datasets
        ]


def export_to_parquet(dataset_id: str) -> tuple[bytes, bytes, dict]:
    """Export SQLite events to Parquet bytes."""
    conn = duckdb_manager.get_connection()
    sqlite_path = settings.database_url.split("///")[-1]

    try:
        conn.execute(f"ATTACH '{sqlite_path}' AS db (TYPE SQLITE)")

        # Export events
        events_arrow = conn.execute(f"""
            SELECT
                pc.case_id,
                pe.activity,
                pe.timestamp,
                pe.resource
            FROM db.process_events pe
            INNER JOIN db.process_cases pc ON pe.case_ref_id = pc.id
            WHERE pc.dataset_id = '{dataset_id}'
            ORDER BY pc.case_id, pe.timestamp
        """).arrow()

        # Export cases
        cases_arrow = conn.execute(f"""
            SELECT
                case_id,
                variant_key,
                start_time,
                end_time
            FROM db.process_cases
            WHERE dataset_id = '{dataset_id}'
        """).arrow()

        # Get counts
        stats = conn.execute(f"""
            SELECT COUNT(*) FROM db.process_events pe
            INNER JOIN db.process_cases pc ON pe.case_ref_id = pc.id
            WHERE pc.dataset_id = '{dataset_id}'
        """).fetchone()

        # Convert to bytes
        events_buffer = io.BytesIO()
        pq.write_table(events_arrow, events_buffer, compression='snappy')

        cases_buffer = io.BytesIO()
        pq.write_table(cases_arrow, cases_buffer, compression='snappy')

        return (
            events_buffer.getvalue(),
            cases_buffer.getvalue(),
            {"events_count": stats[0], "cases_count": cases_arrow.num_rows},
        )

    finally:
        conn.close()


async def migrate_dataset(dataset_id: str, org_id: str, dry_run: bool) -> dict:
    """Migrate a single dataset to Parquet."""
    print(f"  Exporting dataset {dataset_id}...")

    events_bytes, cases_bytes, counts = export_to_parquet(dataset_id)

    events_key = f"{org_id}/{dataset_id}/events.parquet"
    cases_key = f"{org_id}/{dataset_id}/cases.parquet"

    result = {
        "dataset_id": dataset_id,
        "events_count": counts["events_count"],
        "cases_count": counts["cases_count"],
        "events_size_mb": len(events_bytes) / (1024 * 1024),
        "cases_size_mb": len(cases_bytes) / (1024 * 1024),
        "events_key": events_key,
        "cases_key": cases_key,
    }

    if dry_run:
        print(f"    [DRY RUN] Would upload {events_key} ({result['events_size_mb']:.2f} MB)")
        return result

    # Upload to S3
    storage = get_storage_client()

    storage.upload_fileobj(
        bucket_type="events",
        key=events_key,
        file_obj=io.BytesIO(events_bytes),
        content_type="application/vnd.apache.parquet",
    )

    storage.upload_fileobj(
        bucket_type="events",
        key=cases_key,
        file_obj=io.BytesIO(cases_bytes),
        content_type="application/vnd.apache.parquet",
    )

    # Update dataset metadata
    async with AsyncSessionLocal() as db:
        await db.execute(
            text("""
                UPDATE datasets
                SET parquet_s3_key = :events_key,
                    parquet_size_bytes = :size
                WHERE id = :dataset_id
            """),
            {
                "events_key": events_key,
                "size": len(events_bytes),
                "dataset_id": dataset_id,
            }
        )
        await db.commit()

    print(f"    Migrated {dataset_id}: {counts['events_count']} events")
    return result


async def main(dry_run: bool):
    print("=" * 60)
    print("Event Data Migration: SQLite → S3 Parquet")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print()

    datasets = await get_datasets_to_migrate()
    print(f"Found {len(datasets)} datasets to migrate")

    if not datasets:
        print("Nothing to migrate!")
        return

    # For now, use a placeholder org_id
    # In production, join with projects/workspaces to get real org_id
    org_id = "default-org"

    total_events = 0
    total_size = 0

    for dataset in datasets:
        result = await migrate_dataset(dataset["id"], org_id, dry_run)
        total_events += result["events_count"]
        total_size += result["events_size_mb"]

    print()
    print("=" * 60)
    print(f"Migration Summary:")
    print(f"  Datasets migrated: {len(datasets)}")
    print(f"  Total events: {total_events:,}")
    print(f"  Total size: {total_size:.2f} MB")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--execute", action="store_true", help="Actually migrate")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Must specify --dry-run or --execute")
        exit(1)

    asyncio.run(main(dry_run=args.dry_run))
```

### Step 4: Code to Delete

After migration is complete and verified, delete:

```
FILES TO DELETE:
- backend/src/features/process_mining/models/events_models.py (ProcessCase, ProcessEvent classes)

CODE TO REMOVE FROM:
- backend/src/platform/temporal/activities/dataset.py
  - Remove: bulk_copy_to_db_activity() function entirely

- backend/src/platform/temporal/workflows/ingestion.py
  - Remove: call to bulk_copy_to_db_activity

- backend/src/features/process_mining/ingestion/service.py
  - Remove: _create_dataset() method (writes to SQLite)
  - Remove: ProcessCase/ProcessEvent ORM usage

DATABASE MIGRATION:
- Create Alembic migration to DROP tables:
  - process_events
  - process_cases
  - process_variants (if exists)
```

---

## PHASE 4: VERIFICATION CHECKLIST

### Test Matrix

- [ ] New ingestion writes Parquet only (no SQLite events)
- [ ] Analytics reads Parquet via DuckDB `read_parquet()`
- [ ] Metadata stored in PostgreSQL/SQLite only
- [ ] No dual-writes anywhere
- [ ] S3 failure = ingestion failure (atomic)
- [ ] PostgreSQL failure = metadata failure (not data loss)
- [ ] Migration script correctly exports all existing data
- [ ] Row counts match before/after migration
- [ ] Performance: Parquet reads faster than SQLite for large datasets

### Performance Benchmarks

Run before and after migration:

```bash
# Time to load 100k events
python -c "
from src.features.process_mining.services.loader import event_log_loader
import time
start = time.time()
df = event_log_loader.load_as_dataframe('DATASET_ID')
print(f'SQLite: {time.time() - start:.2f}s, {len(df)} rows')
"

# After migration
python -c "
from src.features.process_mining.services.parquet_loader import parquet_event_log_loader
import time
start = time.time()
df = parquet_event_log_loader.load_as_dataframe('org/dataset/events.parquet')
print(f'Parquet: {time.time() - start:.2f}s, {len(df)} rows')
"
```

---

## OUTPUT INVENTORY

After completing this migration:

1. **Data Ownership Diagram**: Above in Phase 2
2. **Migrated Ingestion Pipeline**: `parquet_ingestion.py`
3. **Migrated Analytics Service**: `parquet_loader.py`
4. **Migration Script**: `migrate_events_to_parquet.py`
5. **Deleted Code Inventory**: Listed in Step 4

---

## RISKS & ROLLBACK

### Risks
1. S3 access/credentials issues in DuckDB
2. Large datasets may have long migration times
3. Parquet file corruption possibilities

### Rollback Plan
1. Keep SQLite tables until migration verified (don't delete immediately)
2. Keep old `loader.py` as fallback
3. Feature flag to switch between SQLite and Parquet readers
