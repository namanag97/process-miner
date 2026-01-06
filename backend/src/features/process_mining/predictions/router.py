"""Predictions Router - ML Predictions API.

Machine learning for predictive process monitoring.

## Business Context
Predictions enable proactive process management:
- **Next Activity**: What activity is likely to come next?
- **Remaining Time**: How long until case completion?
- Use for SLA monitoring, resource planning, and interventions

## Testing Instructions

### Train a Predictor
```
POST /api/v1/predictions/datasets/{dataset_id}/train
{"target_type": "next_activity", "algorithm": "decision_tree"}
```
→ Returns job_id (training runs async by default)

### Test Flow
1. **Train Model**: `POST /api/v1/predictions/datasets/{id}/train`
2. **Check Job**: `GET /api/v1/predictions/jobs/{job_id}` until completed
3. **List Predictors**: `GET /api/v1/predictions/datasets/{id}/predictors`
4. **Get Predictor**: `GET /api/v1/predictions/predictors/{predictor_id}`
5. **Predict**:
   ```
   POST /api/v1/predictions/predictors/{id}/predict
   {"case_prefix": ["Activity A", "Activity B"]}
   ```
6. **Batch Predict**: `POST /api/v1/predictions/predictors/{id}/predict-batch`

### Target Types
`next_activity`, `remaining_time`

### Algorithms
`decision_tree`, `random_forest`, `gradient_boosting`

### Common Errors
- **404**: Dataset or Predictor not found
- **400**: Model has no data (retrain)
"""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.features.process_mining.filtering.service import filtering_service
from src.features.process_mining.models import Dataset, PredictionModel
from src.features.process_mining.predictions.service import prediction_service
from src.features.process_mining.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
    PredictionResponse,
    PredictorListResponse,
    PredictorResponse,
    TrainPredictorRequest,
)
from src.platform.core.logging_config import get_logger
from src.platform.infrastructure.tasks import get_task_status, train_prediction_model_task
from src.platform.models import AsyncJob

logger = get_logger(__name__)

router = APIRouter(prefix="/predictions", tags=["Predictions"])


async def _get_pm4py_log(dataset_id: str, db: AsyncSession):
    """Helper to get PM4Py log from dataset_id."""
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()
    if not event_log:
        logger.error("predictions_dataset_not_found", dataset_id=dataset_id)
        raise HTTPException(
            status_code=404,
            detail=f"Dataset not found: {dataset_id}. Verify the dataset ID exists."
        )

    try:
        pm4py_log = filtering_service.to_pm4py_log(event_log)
        return pm4py_log, event_log
    except Exception as e:
        logger.error(
            "predictions_pm4py_conversion_failed",
            dataset_id=dataset_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to convert dataset {dataset_id} to PM4Py log: {str(e)}"
        )


@router.post("/datasets/{dataset_id}/train")
async def train_predictor(
    dataset_id: str,
    request: TrainPredictorRequest,
    db: AsyncSession = Depends(get_db),
    async_mode: bool = True,
    user_id: str | None = None,  # BUG-046: Optional user_id for job ownership
) -> dict[str, Any]:
    """Train a prediction model for an event log.

    Args:
        dataset_id: Event log ID
        request: Training request with target_type and algorithm
        async_mode: If True, train asynchronously via Celery (default)

    Returns:
        - If async_mode=True: {"job_id": "...", "status": "pending"}
        - If async_mode=False: PredictorResponse with trained model
    """
    logger.info(
        "training_predictor",
        dataset_id=dataset_id,
        target=request.target_type,
        algorithm=request.algorithm,
        async_mode=async_mode,
    )

    # Verify log exists
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    if async_mode:
        # Train asynchronously via Celery
        task = train_prediction_model_task.delay(
            dataset_id=dataset_id,
            target_type=request.target_type,
            algorithm=request.algorithm,
        )

        # Create async job record with user ownership (BUG-046 FIX)
        async_job = AsyncJob(
            task_id=task.id,
            job_type="train_prediction",
            status="pending",
            user_id=user_id,  # BUG-046: Track job owner for security
            parameters_json=json.dumps(
                {
                    "dataset_id": dataset_id,
                    "target_type": request.target_type,
                    "algorithm": request.algorithm,
                }
            ),
        )
        db.add(async_job)
        await db.commit()

        logger.info("async_training_started", job_id=task.id, dataset_id=dataset_id)

        return {
            "job_id": task.id,
            "status": "pending",
            "message": "Training started asynchronously. Use /jobs/{job_id} to check status.",
        }
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
        dataset_id=dataset_id,  # BUG-001 FIX
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
        "dataset_id": dataset_id,
        "target_type": request.target_type,
        "algorithm": request.algorithm,
        "metrics": metrics,
        "trained_at": prediction_model.trained_at.isoformat()
        if prediction_model.trained_at
        else None,
    }


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str | None = None,  # BUG-046: Optional user_id for ownership validation
) -> dict[str, Any]:
    """Get status of an async training job.

    Args:
        job_id: Celery task ID
        user_id: Optional user ID for ownership validation (BUG-046)

    Returns:
        Job status with progress information
    """
    logger.info("getting_job_status", job_id=job_id, user_id=user_id)

    # Get task status from Celery
    task_status = get_task_status(job_id)

    # BUG-046 FIX: Filter by user_id if provided for security
    query = select(AsyncJob).where(AsyncJob.task_id == job_id)
    if user_id:
        query = query.where(AsyncJob.user_id == user_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    # BUG-046: Return 404 if job not found (either doesn't exist or user doesn't own it)
    if not job and user_id:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found or access denied")

    if job:
        task_status["job_type"] = job.job_type
        task_status["created_at"] = job.created_at.isoformat() if job.created_at else None
        task_status["started_at"] = job.started_at.isoformat() if job.started_at else None
        task_status["completed_at"] = job.completed_at.isoformat() if job.completed_at else None

    return task_status


@router.get("/datasets/{dataset_id}/predictors", response_model=PredictorListResponse)
async def list_predictors(
    dataset_id: str, db: AsyncSession = Depends(get_db)
) -> PredictorListResponse:
    """List all predictors for an event log."""
    logger.info("listing_predictors", dataset_id=dataset_id)

    query = select(PredictionModel).where(PredictionModel.dataset_id == dataset_id)  # BUG-001 FIX
    result = await db.execute(query)
    predictors = result.scalars().all()

    items = [PredictorResponse.model_validate(p) for p in predictors]

    return PredictorListResponse(dataset_id=dataset_id, predictors=items, total=len(items))


@router.get("/predictors/{predictor_id}", response_model=PredictorResponse)
async def get_predictor(predictor_id: str, db: AsyncSession = Depends(get_db)) -> PredictorResponse:
    """Get predictor details."""
    logger.info("getting_predictor", predictor_id=predictor_id)

    query = select(PredictionModel).where(PredictionModel.id == predictor_id)
    result = await db.execute(query)
    predictor = result.scalar_one_or_none()

    if not predictor:
        raise HTTPException(status_code=404, detail=f"Predictor {predictor_id} not found")

    return PredictorResponse.model_validate(predictor)


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
    if predictor.target_type == "remaining_time":
        prediction_result = prediction_service.predict_remaining_time(
            predictor.model_binary, request.case_prefix, activities
        )
        return PredictionResponse(
            predictor_id=predictor_id,
            case_prefix=request.case_prefix,
            prediction=prediction_result["prediction_seconds"],
            confidence=prediction_result["confidence"],
        )
    raise HTTPException(status_code=400, detail=f"Unsupported target type: {predictor.target_type}")


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
