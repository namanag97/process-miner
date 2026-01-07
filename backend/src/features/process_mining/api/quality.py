"""Quality Metrics Router.

API endpoints for computing and retrieving process model quality metrics.
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from src.api.dependencies import CurrentUser
from src.features.process_mining.services.quality_service import QualityService
from src.platform.core.exceptions import ResourceNotFoundError
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/models", tags=["Quality Metrics"])


@router.post("/{model_id}/evaluate")
async def evaluate_model(
    db: ReadDBSession,
    user: CurrentUser,
    model_id: str,
    dataset_id: str = Query(..., description="Dataset to evaluate against"),
    metrics: str | None = Query(
        None, description="Comma-separated metrics: fitness,precision,generalization,simplicity"
    ),
):
    """Trigger quality evaluation for a process model.

    Computes quality metrics:
    - **Fitness**: How well the model can replay the log (token-based replay)
    - **Precision**: How much behavior in the model is in the log (ETC precision)
    - **Generalization**: How well the model generalizes beyond the log
    - **Simplicity**: Structural simplicity (arc-to-node ratio)

    Results are stored in the database and cached for future retrieval.
    """
    service = QualityService(db)

    # Parse metrics list
    metrics_list = None
    if metrics:
        metrics_list = [m.strip() for m in metrics.split(",")]

    try:
        return await service.evaluate_model(
            model_id=model_id,
            dataset_id=dataset_id,
            metrics=metrics_list,
        )
    except ValueError as e:
        # Determine which resource wasn't found from the error message
        error_msg = str(e).lower()
        if "model" in error_msg:
            raise ResourceNotFoundError("Model", model_id)
        elif "dataset" in error_msg:
            raise ResourceNotFoundError("Dataset", dataset_id)
        else:
            raise ResourceNotFoundError("Resource", model_id)


@router.get("/{model_id}/metrics")
async def get_model_metrics(
    db: ReadDBSession,
    model_id: str,
):
    """Get stored quality metrics for a process model.

    Returns previously computed metrics without recomputation.
    If no metrics have been computed, returns 404.

    To trigger computation, use POST /models/{id}/evaluate.
    """
    service = QualityService(db)
    metrics = await service.get_metrics(model_id)

    if not metrics:
        return JSONResponse(
            status_code=404,
            content={
                "detail": f"No metrics computed for model {model_id}. Use POST /models/{model_id}/evaluate to compute.",
                "model_id": model_id,
            },
        )

    return metrics
