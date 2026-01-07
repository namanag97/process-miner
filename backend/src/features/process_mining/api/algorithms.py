"""Algorithm Registry Router.

API endpoints for querying algorithm metadata and recommendations.
"""

from fastapi import APIRouter, Query

from src.api.dependencies import DBSession
from src.features.process_mining.services.algorithm_registry_service import AlgorithmRegistryService
from src.platform.core.exceptions import ResourceNotFoundError
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/algorithms", tags=["Algorithms"])


@router.get("")
async def list_algorithms(
    db: DBSession,
    category: str | None = Query(
        None, description="Filter by category (discovery, conformance, declarative, enhancement)"
    ),
    include_disabled: bool = Query(False, description="Include disabled algorithms"),
):
    """List all available mining algorithms with metadata.

    Returns algorithms sorted by display order with:
    - Speed and noise tolerance ratings
    - Recommended event/activity limits
    - Soundness guarantees
    - External dependency requirements
    """
    service = AlgorithmRegistryService(db)
    algorithms = await service.list_algorithms(
        category=category,
        include_disabled=include_disabled,
    )

    return {
        "algorithms": algorithms,
        "total": len(algorithms),
    }


@router.get("/recommend")
async def recommend_algorithm(
    db: DBSession,
    dataset_id: str = Query(..., description="Dataset to analyze for recommendation"),
    use_case: str | None = Query(
        None, description="Optimization goal: quick, quality, noisy, declarative"
    ),
):
    """Get algorithm recommendation based on dataset characteristics.

    Analyzes the dataset's:
    - Event count
    - Activity count
    - Variant ratio

    Returns a primary recommendation with alternatives and reasoning.
    """
    service = AlgorithmRegistryService(db)
    return await service.recommend_algorithm(
        dataset_id=dataset_id,
        use_case=use_case,
    )


@router.get("/{algorithm_id}")
async def get_algorithm(
    db: DBSession,
    algorithm_id: str,
):
    """Get detailed information about a specific algorithm.

    Returns:
    - Full metadata
    - All configurable parameters with types, ranges, defaults
    - Parameter descriptions for UI tooltips
    """
    service = AlgorithmRegistryService(db)
    algorithm = await service.get_algorithm(algorithm_id)

    if not algorithm:
        raise ResourceNotFoundError(f"Algorithm not found: {algorithm_id}")

    return algorithm


@router.get("/{algorithm_id}/parameters")
async def get_algorithm_parameters(
    db: DBSession,
    algorithm_id: str,
):
    """Get parameters for a specific algorithm.

    Useful for building dynamic parameter forms in the UI.
    """
    service = AlgorithmRegistryService(db)
    parameters = await service.get_algorithm_parameters(algorithm_id)

    return {
        "algorithm_id": algorithm_id,
        "parameters": parameters,
    }
