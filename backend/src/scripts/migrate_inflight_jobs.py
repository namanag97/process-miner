"""In-Flight Job Migration Script.

Migrates existing AsyncJob records to the new Temporal-native system.
Run this during Week 3 of the Temporal Architecture Reset.

Steps:
1. Find all pending/running AsyncJob records
2. For each job with a workflow_id, check Temporal for actual status
3. Update AsyncJob status to match Temporal
4. Mark orphaned jobs (no workflow_id or Temporal not found) as failed

Usage:
    python -m src.scripts.migrate_inflight_jobs --dry-run  # Preview changes
    python -m src.scripts.migrate_inflight_jobs            # Apply changes
"""

import argparse
import asyncio
from datetime import datetime

import structlog

logger = structlog.get_logger(__name__)


async def migrate_jobs(dry_run: bool = True) -> dict:
    """Migrate in-flight AsyncJob records.

    Args:
        dry_run: If True, only preview changes without applying

    Returns:
        dict with migration statistics
    """
    from sqlalchemy import select
    from temporalio.client import WorkflowExecutionStatus

    from src.platform.infrastructure.database import async_session_maker
    from src.platform.models import AsyncJob
    from src.platform.temporal.client import get_temporal_client

    stats = {
        "total_jobs": 0,
        "already_completed": 0,
        "updated_to_completed": 0,
        "updated_to_failed": 0,
        "orphaned_jobs": 0,
        "still_running": 0,
        "errors": [],
    }

    logger.info("migration_started", dry_run=dry_run)

    async with async_session_maker() as db:
        # Find all pending/running jobs
        result = await db.execute(
            select(AsyncJob).where(
                AsyncJob.status.in_(
                    ["pending", "running", "queued", "PENDING", "RUNNING", "QUEUED"]
                )
            )
        )
        jobs = result.scalars().all()

        stats["total_jobs"] = len(jobs)
        logger.info("found_inflight_jobs", count=len(jobs))

        if len(jobs) == 0:
            logger.info("no_jobs_to_migrate")
            return stats

        # Get Temporal client
        try:
            client = await get_temporal_client()
        except Exception as e:
            logger.error("temporal_client_failed", error=str(e))
            stats["errors"].append(f"Failed to connect to Temporal: {e}")
            return stats

        for job in jobs:
            job_log = logger.bind(job_id=job.id, job_type=job.job_type)

            # Check if already completed in our records
            if job.status in ("completed", "COMPLETED"):
                stats["already_completed"] += 1
                continue

            # Get workflow ID (may be in task_id or workflow_id field)
            workflow_id = getattr(job, "workflow_id", None) or job.task_id

            if not workflow_id:
                # Orphaned job - no workflow ID
                job_log.warning("orphaned_job", reason="no_workflow_id")
                stats["orphaned_jobs"] += 1

                if not dry_run:
                    job.status = "failed"
                    job.error_message = "Orphaned during migration - no workflow ID"
                    job.completed_at = datetime.utcnow()
                continue

            # Query Temporal for actual status
            try:
                handle = client.get_workflow_handle(workflow_id)
                desc = await handle.describe()
                temporal_status = desc.status

                job_log.info(
                    "temporal_status_found",
                    workflow_id=workflow_id,
                    temporal_status=temporal_status.name if temporal_status else "UNKNOWN",
                )

                if temporal_status == WorkflowExecutionStatus.COMPLETED:
                    stats["updated_to_completed"] += 1
                    if not dry_run:
                        job.status = "completed"
                        job.progress = 100
                        job.completed_at = desc.close_time or datetime.utcnow()

                elif temporal_status == WorkflowExecutionStatus.FAILED:
                    stats["updated_to_failed"] += 1
                    if not dry_run:
                        job.status = "failed"
                        job.error_message = "Workflow failed in Temporal"
                        job.completed_at = desc.close_time or datetime.utcnow()

                elif temporal_status == WorkflowExecutionStatus.CANCELED:
                    stats["updated_to_failed"] += 1
                    if not dry_run:
                        job.status = "cancelled"
                        job.completed_at = desc.close_time or datetime.utcnow()

                elif temporal_status == WorkflowExecutionStatus.TIMED_OUT:
                    stats["updated_to_failed"] += 1
                    if not dry_run:
                        job.status = "failed"
                        job.error_message = "Workflow timed out"
                        job.completed_at = desc.close_time or datetime.utcnow()

                elif temporal_status == WorkflowExecutionStatus.RUNNING:
                    stats["still_running"] += 1
                    job_log.info("workflow_still_running")
                    # Leave as-is, let it complete

                else:
                    # Unknown status
                    job_log.warning("unknown_temporal_status", status=str(temporal_status))

            except Exception as e:
                # Workflow not found in Temporal
                job_log.warning("temporal_query_failed", error=str(e))
                stats["orphaned_jobs"] += 1

                if not dry_run:
                    job.status = "failed"
                    job.error_message = f"Workflow not found in Temporal: {e}"
                    job.completed_at = datetime.utcnow()

        if not dry_run:
            await db.commit()
            logger.info("migration_committed")
        else:
            logger.info("dry_run_complete", message="No changes applied")

    logger.info(
        "migration_completed",
        **stats,
    )

    return stats


async def main():
    parser = argparse.ArgumentParser(description="Migrate in-flight AsyncJob records")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying",
    )
    args = parser.parse_args()

    stats = await migrate_jobs(dry_run=args.dry_run)

    if args.dry_run:
        pass
    else:
        pass

    if stats["errors"]:
        for _error in stats["errors"]:
            pass


if __name__ == "__main__":
    asyncio.run(main())
