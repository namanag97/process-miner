"""ML Tasks.

Celery tasks for machine learning model training.
"""

import time
from datetime import datetime
from typing import Any

import structlog
from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .base import AsyncSessionLocal, AsyncTask, celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="train_prediction_model",
    autoretry_for=(SQLAlchemyError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
async def train_prediction_model_task(
    self,
    dataset_id: str,
    target_type: str,
    algorithm: str = "random_forest",
    **params: Any,
) -> dict[str, Any]:
    """Async task for training ML prediction models.

    Args:
        dataset_id: Event log ID to train on
        target_type: Type of prediction ('next_activity' or 'remaining_time')
        algorithm: ML algorithm to use
        **params: Additional training parameters

    Returns:
        dict with model_id, metrics, and training info
    """
    logger.info(
        "prediction_training_started",
        dataset_id=dataset_id,
        target_type=target_type,
        algorithm=algorithm,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "status": "Loading event log",
                "progress": 10,
                "started_at": datetime.utcnow().isoformat(),
            },
        )

        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, PredictionModel
            from src.features.process_mining.services.loader import event_log_loader
            from src.features.process_mining.services.prediction import prediction_service
            from src.platform.models import AsyncJob

            # Verify dataset exists
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()

            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")

            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Converting to PM4Py format",
                    "progress": 20,
                },
            )

            # Convert to PM4Py log
            pm4py_log = event_log_loader.load_as_pm4py_log(dataset_id)

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

            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Saving model to database",
                    "progress": 80,
                },
            )

            # Save model to database
            db_model = PredictionModel(
                dataset_id=dataset_id,
                target_type=target_type,
                algorithm=algorithm,
                model_binary=model_info["model_binary"],
                metrics_json=model_info.get("metrics_json"),
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
                "dataset_id": dataset_id,
                "target_type": target_type,
                "algorithm": algorithm,
                "metrics": model_info.get("metrics", {}),
                "duration_ms": round(duration, 2),
            }

    except SoftTimeLimitExceeded:
        logger.warning(
            "prediction_training_soft_timeout",
            dataset_id=dataset_id,
            target_type=target_type,
            task_id=self.request.id,
        )
        async with AsyncSessionLocal() as db:
            from src.platform.models import AsyncJob

            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error_message = "Task exceeded soft time limit - clean shutdown initiated"
                job.completed_at = datetime.utcnow()
                await db.commit()
        
        raise

    except Exception as e:
        logger.error(
            "prediction_training_failed",
            error=str(e),
            dataset_id=dataset_id,
            target_type=target_type,
            task_id=self.request.id,
        )

        async with AsyncSessionLocal() as db:
            from src.platform.models import AsyncJob

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
