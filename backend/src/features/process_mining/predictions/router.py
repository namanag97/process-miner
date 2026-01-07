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
→ Returns predictor info (sync training)

### Test Flow
1. **Train Model**: `POST /api/v1/predictions/datasets/{id}/train`
2. **List Predictors**: `GET /api/v1/predictions/datasets/{id}/predictors`
3. **Get Predictor**: `GET /api/v1/predictions/predictors/{predictor_id}`
4. **Predict**:
   ```
   POST /api/v1/predictions/predictors/{id}/predict
   {"case_prefix": ["Activity A", "Activity B"]}
   ```
5. **Batch Predict**: `POST /api/v1/predictions/predictors/{id}/predict-batch`

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

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from src.api.dependencies import ReadDBSession, WriteDBSession, ServiceContainer
from src.features.process_mining.models import Dataset, PredictionModel
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

logger = get_logger(__name__)

router = APIRouter(prefix="/predictions", tags=["Predictions"])


async def _get_pm4py_log(dataset_id: str, db: ReadDBSession, container: ServiceContainer):
    """Helper to get PM4Py log from dataset_id."""
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()
    if not event_log:
        logger.error("predictions_dataset_not_found", dataset_id=dataset_id)
        raise HTTPException(
            status_code=404,
            detail=f"Dataset not found: {dataset_id}. Verify the dataset ID exists.",
        )

    try:
        pm4py_log = container.filtering.to_pm4py_log(event_log)
        return pm4py_log, event_log
    except Exception as e:
        logger.error(
            "predictions_pm4py_conversion_failed",
            dataset_id=dataset_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to convert dataset {dataset_id} to PM4Py log: {e!s}"
        )


async def train_predictor(
    dataset_id: str,
    request: TrainPredictorRequest,
    db: WriteDBSession,  # CQRS: Write pool for training
    container: ServiceContainer,
    async_mode: bool = False,  # Sync by default (Celery removed)
    user_id: str | None = None,
) -> dict[str, Any]:
    """Train a prediction model for an event log.

    Args:
        dataset_id: Event log ID
        request: Training request with target_type and algorithm
        async_mode: Not currently supported (Temporal workflow TODO)

    Returns:
        PredictorResponse with trained model
    """
    logger.info(
        "training_predictor",
        dataset_id=dataset_id,
        target=request.target_type,
        algorithm=request.algorithm,
    )

    # Verify log exists
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    if async_mode:
        # TODO: Implement Temporal v2 workflow for async training
        raise HTTPException(
            status_code=501, detail="Async training not yet implemented. Use async_mode=false."
        )

    # Train synchronously
    pm4py_log = container.filtering.to_pm4py_log(event_log)

    if request.target_type == "next_activity":
        model_bytes, metrics = container.predictions.train_next_activity_model(
            pm4py_log, request.algorithm
        )
    elif request.target_type == "remaining_time":
        model_bytes, metrics = container.predictions.train_remaining_time_model(
            pm4py_log, request.algorithm
        )
    else:
        raise HTTPException(
            status_code=400, detail=f"Unsupported target type: {request.target_type}"
        )

    activities = container.predictions.get_activities_from_log(pm4py_log)
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


async def get_job_status(
    job_id: str,
    db: ReadDBSession,  # CQRS: Read-only job status lookup
    user_id: str | None = None,
) -> dict[str, Any]:
    """Get status of an async training job.

    Note: Async training now uses Temporal. Use /operations/{workflow_id} endpoint.

    Args:
        job_id: Workflow ID

    Returns:
        Redirect message to operations endpoint
    """
    logger.info("getting_job_status", job_id=job_id, user_id=user_id)

    # Redirect to unified operations endpoint
    return {
        "message": "Use /api/v1/operations/{workflow_id} for job status",
        "workflow_id": job_id,
        "redirect_url": f"/api/v1/operations/{job_id}",
    }


async def list_predictors(dataset_id: str, db: ReadDBSession) -> PredictorListResponse:
    """List all predictors for an event log."""
    logger.info("listing_predictors", dataset_id=dataset_id)

    query = select(PredictionModel).where(PredictionModel.dataset_id == dataset_id)  # BUG-001 FIX
    result = await db.execute(query)
    predictors = result.scalars().all()

    items = [PredictorResponse.model_validate(p) for p in predictors]

    return PredictorListResponse(dataset_id=dataset_id, predictors=items, total=len(items))


async def get_predictor(predictor_id: str, db: ReadDBSession) -> PredictorResponse:
    """Get predictor details."""
    logger.info("getting_predictor", predictor_id=predictor_id)

    query = select(PredictionModel).where(PredictionModel.id == predictor_id)
    result = await db.execute(query)
    predictor = result.scalar_one_or_none()

    if not predictor:
        raise HTTPException(status_code=404, detail=f"Predictor {predictor_id} not found")

    return PredictorResponse.model_validate(predictor)


async def predict(
    predictor_id: str,
    request: PredictionRequest,
    db: ReadDBSession,  # CQRS: Read-only prediction
    container: ServiceContainer,
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
        prediction_result = container.predictions.predict_next_activity(
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
        prediction_result = container.predictions.predict_remaining_time(
            predictor.model_binary, request.case_prefix, activities
        )
        return PredictionResponse(
            predictor_id=predictor_id,
            case_prefix=request.case_prefix,
            prediction=prediction_result["prediction_seconds"],
            confidence=prediction_result["confidence"],
        )
    raise HTTPException(status_code=400, detail=f"Unsupported target type: {predictor.target_type}")


async def predict_batch(
    predictor_id: str,
    request: BatchPredictionRequest,
    db: ReadDBSession,  # CQRS: Read-only batch prediction
    container: ServiceContainer,
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
            pred_result = container.predictions.predict_next_activity(
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
            pred_result = container.predictions.predict_remaining_time(
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


async def delete_predictor(predictor_id: str, db: WriteDBSession) -> dict[str, Any]:
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
