"""Celery task configuration and async task definitions.

Provides background task execution for:
- ML model training (predictions)
- Long-running analytics operations
- Batch processing workflows
"""

import asyncio
import time
from datetime import datetime
from typing import Any

import structlog
from celery import Celery, Task
from celery.result import AsyncResult
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Celery app configuration
celery_app = Celery(
    "process_mining",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time
    task_acks_late=True,  # Acknowledge after completion
    task_reject_on_worker_lost=True,
)


# Async database session for tasks
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class AsyncTask(Task):
    """Base task class with async support."""

    def __call__(self, *args, **kwargs):
        """Run async function in event loop."""
        return asyncio.run(self.run_async(*args, **kwargs))

    async def run_async(self, *args, **kwargs):
        """Override this in subclasses."""
        raise NotImplementedError


@celery_app.task(bind=True, base=AsyncTask, name="train_prediction_model")
async def train_prediction_model_task(
    self,
    log_id: str,
    target_type: str,
    algorithm: str = "random_forest",
    **params: Any,
) -> dict[str, Any]:
    """Async task for training ML prediction models.

    Args:
        log_id: Event log ID to train on
        target_type: Type of prediction ('next_activity' or 'remaining_time')
        algorithm: ML algorithm to use
        **params: Additional training parameters

    Returns:
        dict with model_id, metrics, and training info
    """
    logger.info(
        "prediction_training_started",
        log_id=log_id,
        target_type=target_type,
        algorithm=algorithm,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        # Update task state to PROGRESS
        self.update_state(
            state="PROGRESS",
            meta={
                "status": "Loading event log",
                "progress": 10,
                "started_at": datetime.utcnow().isoformat(),
            },
        )

        async with AsyncSessionLocal() as db:
            # Import here to avoid circular dependencies
            from src.models.orm import AsyncJob, EventLog, PredictionModel
            from src.services.ingestion import ingestion_service
            from src.services.prediction import prediction_service

            # Load event log
            result = await db.execute(select(EventLog).where(EventLog.id == log_id))
            event_log = result.scalar_one_or_none()

            if not event_log:
                raise ValueError(f"Event log not found: {log_id}")

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Converting to PM4Py format",
                    "progress": 20,
                },
            )

            # Convert to PM4Py log
            pm4py_log = await ingestion_service.get_pm4py_log(db, log_id)

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": f"Training {algorithm} model",
                    "progress": 40,
                },
            )

            # Train model based on target type
            if target_type == "next_activity":
                model_info = prediction_service.train_next_activity_model(
                    pm4py_log=pm4py_log,
                    algorithm=algorithm,
                    **params,
                )
            elif target_type == "remaining_time":
                model_info = prediction_service.train_remaining_time_model(
                    pm4py_log=pm4py_log,
                    algorithm=algorithm,
                    **params,
                )
            else:
                raise ValueError(f"Unknown target type: {target_type}")

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Saving model to database",
                    "progress": 80,
                },
            )

            # Save model to database
            db_model = PredictionModel(
                log_id=log_id,
                model_type=target_type,
                algorithm=algorithm,
                model_binary=model_info["model_binary"],
                feature_columns_json=model_info.get("feature_columns_json"),
                metrics_json=model_info.get("metrics_json"),
                config_json=model_info.get("config_json"),
                trained_at=datetime.utcnow(),
            )
            db.add(db_model)

            # Update async job status
            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "completed"
                job.result_json = str({"model_id": db_model.id})
                job.completed_at = datetime.utcnow()

            await db.commit()
            await db.refresh(db_model)

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "prediction_training_completed",
                model_id=db_model.id,
                target_type=target_type,
                algorithm=algorithm,
                duration_ms=round(duration, 2),
                task_id=self.request.id,
            )

            return {
                "model_id": db_model.id,
                "log_id": log_id,
                "target_type": target_type,
                "algorithm": algorithm,
                "metrics": model_info.get("metrics", {}),
                "duration_ms": round(duration, 2),
            }

    except Exception as e:
        logger.error(
            "prediction_training_failed",
            error=str(e),
            log_id=log_id,
            target_type=target_type,
            task_id=self.request.id,
        )

        # Update async job status
        async with AsyncSessionLocal() as db:
            from src.models.orm import AsyncJob

            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                await db.commit()

        raise


def get_task_status(task_id: str) -> dict[str, Any]:
    """Get status of a Celery task.

    Args:
        task_id: Celery task ID

    Returns:
        dict with status, result, and progress info
    """
    task_result = AsyncResult(task_id, app=celery_app)

    result = {
        "task_id": task_id,
        "status": task_result.state,
        "ready": task_result.ready(),
        "successful": task_result.successful() if task_result.ready() else None,
    }

    if task_result.state == "PROGRESS":
        result["progress"] = task_result.info
    elif task_result.ready():
        if task_result.successful():
            result["result"] = task_result.result
        else:
            result["error"] = str(task_result.info)

    return result
