#!/usr/bin/env python
"""Migration Script: Move Events from PostgreSQL to S3 Parquet.

This script migrates existing datasets from the dual-write pattern
(events in both PostgreSQL and S3) to Parquet-only storage.

Usage:
    python scripts/migrate_events_to_parquet.py [--dataset-id <id>] [--dry-run]

Options:
    --dataset-id <id>  Migrate specific dataset (default: all)
    --dry-run          Preview migration without writing
"""

import argparse
import asyncio
import io
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


async def migrate_dataset(dataset_id: str, dry_run: bool = False) -> dict:
    """Migrate a single dataset from PostgreSQL to S3 Parquet."""
    import pyarrow.parquet as pq
    from sqlalchemy import select

    from src.features.process_mining.models import Dataset
    from src.features.process_mining.services.loader import event_log_loader
    from src.platform.infrastructure.object_storage import get_storage_client
    from src.platform.infrastructure.database import async_session_maker

    result = {
        "dataset_id": dataset_id,
        "status": "pending",
        "events_migrated": 0,
        "parquet_key": None,
        "error": None,
    }

    async with async_session_maker() as session:
        # Get dataset
        query = select(Dataset).where(Dataset.id == dataset_id)
        db_result = await session.execute(query)
        dataset = db_result.scalar_one_or_none()

        if not dataset:
            result["status"] = "not_found"
            result["error"] = f"Dataset {dataset_id} not found"
            return result

        # Skip if already has Parquet
        if dataset.parquet_s3_key:
            result["status"] = "already_migrated"
            result["parquet_key"] = dataset.parquet_s3_key
            return result

        # Load events from PostgreSQL (legacy path)
        try:
            df = event_log_loader._load_from_sqlite_legacy(dataset_id, max_events=0)
        except Exception as e:
            result["status"] = "load_failed"
            result["error"] = str(e)
            return result

        if df.empty:
            result["status"] = "empty"
            return result

        # Rename columns for Parquet storage
        df_parquet = df.rename(columns={
            "case:concept:name": "case_id",
            "concept:name": "activity",
            "time:timestamp": "timestamp",
            "org:resource": "resource",
        })

        result["events_migrated"] = len(df_parquet)

        if dry_run:
            result["status"] = "dry_run"
            return result

        # Write to S3 as Parquet
        import pyarrow as pa

        table = pa.Table.from_pandas(df_parquet)
        buffer = io.BytesIO()
        pq.write_table(table, buffer, compression="snappy")
        parquet_bytes = buffer.getvalue()

        parquet_key = f"parsed/{dataset_id}/events.parquet"
        storage_client = get_storage_client()

        storage_client.upload_fileobj(
            bucket_type="cache",
            key=parquet_key,
            file_obj=io.BytesIO(parquet_bytes),
            content_type="application/octet-stream",
        )

        # Update dataset metadata
        dataset.parquet_s3_key = parquet_key
        dataset.parquet_size_bytes = len(parquet_bytes)
        dataset.parquet_row_count = len(df_parquet)
        await session.commit()

        result["status"] = "success"
        result["parquet_key"] = parquet_key
        return result


async def migrate_all(dry_run: bool = False):
    """Migrate all datasets without Parquet files."""
    from sqlalchemy import select

    from src.features.process_mining.models import Dataset
    from src.platform.infrastructure.database import async_session_maker

    async with async_session_maker() as session:
        # Find datasets without parquet_s3_key
        query = select(Dataset.id).where(Dataset.parquet_s3_key.is_(None))
        result = await session.execute(query)
        dataset_ids = [row[0] for row in result.fetchall()]

    print(f"Found {len(dataset_ids)} datasets to migrate")

    results = []
    for i, dataset_id in enumerate(dataset_ids):
        print(f"[{i+1}/{len(dataset_ids)}] Migrating {dataset_id}...")
        result = await migrate_dataset(dataset_id, dry_run)
        results.append(result)
        print(f"  → {result['status']}: {result.get('events_migrated', 0)} events")

    # Summary
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] in ("load_failed", "not_found"))
    skipped = sum(1 for r in results if r["status"] in ("already_migrated", "empty"))

    print(f"\n=== Migration Complete ===")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Migrate events to S3 Parquet")
    parser.add_argument("--dataset-id", help="Specific dataset ID to migrate")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if args.dataset_id:
        result = asyncio.run(migrate_dataset(args.dataset_id, args.dry_run))
        print(f"Result: {result}")
    else:
        asyncio.run(migrate_all(args.dry_run))


if __name__ == "__main__":
    main()
