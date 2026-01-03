"""Predictions Router - ML Predictions API.

Provides endpoints for training prediction models and making predictions
for next activity, remaining time, and process outcomes.
"""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.core.logging_config import get_logger
from src.infrastructure.tasks import get_task_status, train_prediction_model_task
from src.models.orm import AsyncJob, Dataset, PredictionModel
from src.models.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
    PredictionResponse,
    PredictorListResponse,
    PredictorResponse,
    TrainPredictorRequest,
)
from src.services.filtering import filtering_service
from src.services.prediction import prediction_service

logger = get_logger(__name__)

router = APIRouter(prefix="/predictions", tags=["Predictions"])


async def _get_pm4py_log(log_id: str, db: AsyncSession):
    """Helper to get PM4Py log from log_id."""
    query = select(Dataset).where(Dataset.id == log_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log {log_id} not found")
    return filtering_service.to_pm4py_log(event_log), event_log


@router.post("/logs/{log_id}/train")
async def train_predictor(
    log_id: str,
    request: TrainPredictorRequest,
    db: AsyncSession = Depends(get_db),
    async_mode: bool = True,
) -> dict[str, Any]:
    """Train a prediction model for an event log.

    Args:
        log_id: Event log ID
        request: Training request with target_type and algorithm
        async_mode: If True, train asynchronously via Celery (default)

    Returns:
        - If async_mode=True: {"job_id": "...", "status": "pending"}
        - If async_mode=False: PredictorResponse with trained model
    """
    logger.info(
        "training_predictor",
        log_id=log_id,
        target=request.target_type,
        algorithm=request.algorithm,
        async_mode=async_mode,
    )

    # Verify log exists
    query = select(Dataset).where(Dataset.id == log_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log {log_id} not found")

    if async_mode:
        # Train asynchronously via Celery
        task = train_prediction_model_task.delay(
            log_id=log_id,
            target_type=request.target_type,
            algorithm=request.algorithm,
        )

        # Create async job record
        async_job = AsyncJob(
            task_id=task.id,
            job_type="train_prediction",
            status="pending",
            parameters_json=json.dumps(
                {
                    "log_id": log_id,
                    "target_type": request.target_type,
                    "algorithm": request.algorithm,
                }
            ),
        )
        db.add(async_job)
        await db.commit()

        logger.info("async_training_started", job_id=task.id, log_id=log_id)

        return {
            "job_id": task.id,
            "status": "pending",
            "message": "Training started asynchronously. Use /jobs/{job_id} to check status.",
        }
    else:
        # Train synchronously (original behavior)
        pm4py_log = filtering_service.to_pm4py_log(event_log)

        if request.target_type == "next_activity":
            model_bytes, metrics = prediction_service.train_next_activity_model(
                pm4py_log, request.algorithm
            )
        elif request.target_type == "remaining_time":
            model_bytes, metrics = prediction_service.train_remaining_time_model(
                pm4py_log, request.algorithm
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported target type: {request.target_type}"
            )

        activities = prediction_service.get_activities_from_log(pm4py_log)
        metrics["activities"] = activities

        prediction_model = PredictionModel(
            dataset_id=log_id,  # BUG-001 FIX
            target_type=request.target_type,
            algorithm=request.algorithm,
            model_binary=model_bytes,
            metrics_json=json.dumps(metrics),
        )
        db.add(prediction_model)
        await db.commit()

        logger.info("predictor_trained", predictor_id=prediction_model.id, metrics=metrics)

        return {
            "id": prediction_model.id,
            "log_id": log_id,
            "target_type": request.target_type,
            "algorithm": request.algorithm,
            "metrics": metrics,
            "trained_at": prediction_model.trained_at.isoformat()
            if prediction_model.trained_at
            else None,
        }


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Get status of an async training job.

    Args:
        job_id: Celery task ID

    Returns:
        Job status with progress information
    """
    logger.info("getting_job_status", job_id=job_id)

    # Get task status from Celery
    task_status = get_task_status(job_id)

    # Get job record from database - query by task_id (Celery task ID), not internal id
    query = select(AsyncJob).where(AsyncJob.task_id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if job:
        task_status["job_type"] = job.job_type
        task_status["created_at"] = job.created_at.isoformat() if job.created_at else None
        task_status["started_at"] = job.started_at.isoformat() if job.started_at else None
        task_status["completed_at"] = job.completed_at.isoformat() if job.completed_at else None

    return task_status


@router.get("/logs/{log_id}/predictors", response_model=PredictorListResponse)
async def list_predictors(log_id: str, db: AsyncSession = Depends(get_db)) -> PredictorListResponse:
    """List all predictors for an event log."""
    logger.info("listing_predictors", log_id=log_id)

    query = select(PredictionModel).where(PredictionModel.dataset_id == log_id)  # BUG-001 FIX
    result = await db.execute(query)
    predictors = result.scalars().all()

    items = []
    for p in predictors:
        metrics = json.loads(p.metrics_json) if p.metrics_json else {}
        items.append(
            PredictorResponse(
                id=p.id,
                log_id=p.log_id,
                target_type=p.target_type,
                algorithm=p.algorithm,
                metrics=metrics,
                trained_at=p.trained_at,
            )
        )

    return PredictorListResponse(log_id=log_id, predictors=items, total=len(items))


@router.get("/predictors/{predictor_id}", response_model=PredictorResponse)
async def get_predictor(predictor_id: str, db: AsyncSession = Depends(get_db)) -> PredictorResponse:
    """Get predictor details."""
    logger.info("getting_predictor", predictor_id=predictor_id)

    query = select(PredictionModel).where(PredictionModel.id == predictor_id)
    result = await db.execute(query)
    predictor = result.scalar_one_or_none()

    if not predictor:
        raise HTTPException(status_code=404, detail=f"Predictor {predictor_id} not found")

    metrics = json.loads(predictor.metrics_json) if predictor.metrics_json else {}

    return PredictorResponse(
        id=predictor.id,
        log_id=predictor.log_id,
        target_type=predictor.target_type,
        algorithm=predictor.algorithm,
        metrics=metrics,
        trained_at=predictor.trained_at,
    )


@router.post("/predictors/{predictor_id}/predict", response_model=PredictionResponse)
async def predict(
    predictor_id: str,
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
) -> PredictionResponse:
    """Make a prediction for a case prefix."""
    logger.info("making_prediction", predictor_id=predictor_id, prefix_len=len(request.case_prefix))

    query = select(PredictionModel).where(PredictionModel.id == predictor_id)
    result = await db.execute(query)
    predictor = result.scalar_one_or_none()

    if not predictor:
        raise HTTPException(status_code=404, detail=f"Predictor {predictor_id} not found")

    metrics = json.loads(predictor.metrics_json) if predictor.metrics_json else {}
    activities = metrics.get("activities", [])

    if not predictor.model_binary:
        raise HTTPException(status_code=400, detail="Predictor model data is missing")

    if predictor.target_type == "next_activity":
        prediction_result = prediction_service.predict_next_activity(
            predictor.model_binary, request.case_prefix, activities
        )
        return PredictionResponse(
            predictor_id=predictor_id,
            case_prefix=request.case_prefix,
            prediction=prediction_result["prediction"],
            confidence=prediction_result["confidence"],
            alternatives=prediction_result.get("alternatives"),
        )
    elif predictor.target_type == "remaining_time":
        prediction_result = prediction_service.predict_remaining_time(
            predictor.model_binary, request.case_prefix, activities
        )
        return PredictionResponse(
            predictor_id=predictor_id,
            case_prefix=request.case_prefix,
            prediction=prediction_result["prediction_seconds"],
            confidence=prediction_result["confidence"],
        )
    else:
        raise HTTPException(
            status_code=400, detail=f"Unsupported target type: {predictor.target_type}"
        )


@router.post("/predictors/{predictor_id}/predict-batch", response_model=BatchPredictionResponse)
async def predict_batch(
    predictor_id: str,
    request: BatchPredictionRequest,
    db: AsyncSession = Depends(get_db),
) -> BatchPredictionResponse:
    """Make batch predictions."""
    logger.info("making_batch_prediction", predictor_id=predictor_id, batch_size=len(request.cases))

    query = select(PredictionModel).where(PredictionModel.id == predictor_id)
    result = await db.execute(query)
    predictor = result.scalar_one_or_none()

    if not predictor:
        raise HTTPException(status_code=404, detail=f"Predictor {predictor_id} not found")

    metrics = json.loads(predictor.metrics_json) if predictor.metrics_json else {}
    activities = metrics.get("activities", [])

    if not predictor.model_binary:
        raise HTTPException(status_code=400, detail="Predictor model data is missing")

    predictions = []
    for case in request.cases:
        if predictor.target_type == "next_activity":
            pred_result = prediction_service.predict_next_activity(
                predictor.model_binary, case.case_prefix, activities
            )
            predictions.append(
                PredictionResponse(
                    predictor_id=predictor_id,
                    case_prefix=case.case_prefix,
                    prediction=pred_result["prediction"],
                    confidence=pred_result["confidence"],
                )
            )
        else:
            pred_result = prediction_service.predict_remaining_time(
                predictor.model_binary, case.case_prefix, activities
            )
            predictions.append(
                PredictionResponse(
                    predictor_id=predictor_id,
                    case_prefix=case.case_prefix,
                    prediction=pred_result["prediction_seconds"],
                    confidence=pred_result["confidence"],
                )
            )

    return BatchPredictionResponse(predictor_id=predictor_id, predictions=predictions)


@router.delete("/predictors/{predictor_id}")
async def delete_predictor(predictor_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Delete a predictor."""
    logger.info("deleting_predictor", predictor_id=predictor_id)

    query = select(PredictionModel).where(PredictionModel.id == predictor_id)
    result = await db.execute(query)
    predictor = result.scalar_one_or_none()

    if not predictor:
        raise HTTPException(status_code=404, detail=f"Predictor {predictor_id} not found")

    await db.delete(predictor)
    await db.commit()

    return {"message": f"Predictor {predictor_id} deleted"}
