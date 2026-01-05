"""Maintenance Tasks.

Celery tasks for system maintenance and cleanup.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

import structlog
from celery.result import AsyncResult

from .base import AsyncSessionLocal, celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, name="reap_zombie_jobs")
def reap_zombie_jobs(self, timeout_minutes: int = 10) -> dict[str, Any]:
    """Reap zombie jobs that are stuck in RUNNING/ANALYZING state.

    BUG-057/031/040/022 FIX: Cross-references multiple tables with Celery's actual task status.
    Should be scheduled via Celery Beat every 5 minutes.

    Handles:
    - AsyncJob records stuck in RUNNING
    - Dataset records stuck in ANALYZING (BUG-022)
    - Analysis records stuck in RUNNING (BUG-040)

    Args:
        timeout_minutes: Consider jobs zombie if stuck for longer than this

    Returns:
        Summary of reaped items across all tables
    """
    from src.features.process_mining.models import Analysis, AnalysisStatus, Dataset, DatasetStatus
    from src.platform.core.enums import JobStatus
    from src.platform.models import AsyncJob

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _reap():
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select

            try:
                cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
                results = {"async_jobs": [], "datasets": [], "analyses": []}

                # === 1. Reap zombie AsyncJobs ===
                job_result = await db.execute(
                    select(AsyncJob).where(
                        AsyncJob.status == JobStatus.RUNNING.value,
                        AsyncJob.updated_at < cutoff_time,
                    )
                )
                stuck_jobs = job_result.scalars().all()

                for job in stuck_jobs:
                    if not job.task_id:
                        job.status = JobStatus.FAILED.value
                        job.error = "No task ID - orphaned job"
                        job.completed_at = datetime.utcnow()
                        results["async_jobs"].append(job.id)
                        continue

                    celery_result = AsyncResult(job.task_id, app=celery_app)
                    celery_state = celery_result.state

                    if celery_state in ("FAILURE", "REVOKED"):
                        job.status = JobStatus.FAILED.value
                        job.error = f"Celery state: {celery_state}"
                        job.completed_at = datetime.utcnow()
                        results["async_jobs"].append(job.id)
                    elif celery_state == "SUCCESS":
                        job.status = JobStatus.COMPLETED.value
                        job.completed_at = datetime.utcnow()
                        results["async_jobs"].append(job.id)
                    elif celery_state == "PENDING" and job.started_at:
                        job.status = JobStatus.FAILED.value
                        job.error = "Task lost - worker likely crashed"
                        job.completed_at = datetime.utcnow()
                        results["async_jobs"].append(job.id)

                # === 2. BUG-022 FIX: Reap zombie Datasets stuck in ANALYZING ===
                dataset_result = await db.execute(
                    select(Dataset).where(
                        Dataset.status == DatasetStatus.ANALYZING.value,
                        Dataset.updated_at < cutoff_time,
                    )
                )
                stuck_datasets = dataset_result.scalars().all()

                for dataset in stuck_datasets:
                    dataset.status = DatasetStatus.ERROR.value
                    dataset.error_message = f"Ingestion timed out after {timeout_minutes} minutes"
                    results["datasets"].append(dataset.id)

                # === 2.5. Phase 4 FIX: Reap zombie Datasets stuck in PENDING ===
                pending_cutoff = datetime.utcnow() - timedelta(hours=2)
                pending_result = await db.execute(
                    select(Dataset).where(
                        Dataset.status == DatasetStatus.PENDING.value,
                        Dataset.created_at < pending_cutoff,
                    )
                )
                pending_datasets = pending_result.scalars().all()

                for dataset in pending_datasets:
                    dataset.status = DatasetStatus.ERROR.value
                    dataset.error_message = "Upload timed out (presigned URL expired)"
                    results["datasets"].append(dataset.id)

                # === 3. BUG-040 FIX: Reap zombie Analyses stuck in RUNNING ===
                analysis_result = await db.execute(
                    select(Analysis).where(
                        Analysis.status == AnalysisStatus.RUNNING.value,
                        Analysis.completed_at.is_(None),
                    )
                )
                stuck_analyses = [
                    a
                    for a in analysis_result.scalars().all()
                    if a.created_at and a.created_at < cutoff_time
                ]

                for analysis in stuck_analyses:
                    analysis.status = AnalysisStatus.FAILED.value
                    analysis.error_message = f"Analysis timed out after {timeout_minutes} minutes"
                    analysis.completed_at = datetime.utcnow()
                    results["analyses"].append(analysis.id)

                await db.commit()

                total_reaped = sum(len(v) for v in results.values())
                logger.info(
                    "zombie_jobs_reaped",
                    async_jobs_reaped=len(results["async_jobs"]),
                    datasets_reaped=len(results["datasets"]),
                    analyses_reaped=len(results["analyses"]),
                    total_reaped=total_reaped,
                )

                return {
                    "async_jobs": results["async_jobs"],
                    "datasets": results["datasets"],
                    "analyses": results["analyses"],
                    "total_reaped": total_reaped,
                }

            except Exception as e:
                logger.error("zombie_reaper_error", error=str(e), exc_info=True)
                raise

    return loop.run_until_complete(_reap())
