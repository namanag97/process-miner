"""
Analysis router - Serves processed analysis results.

After processing, this router provides:
- DFG (Directly-Follows Graph) in React Flow format
- Variants list
- Statistics summary  
- Activity statistics
- Deviations

Uses helper functions to eliminate duplicate deserialization code.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    Dataset,
    DFGResponse,
    VariantsResponse,
    DatasetSummary,
    ActivityStat,
    Deviation,
)
from ..database import get_db
from ..services.repository import BaseRepository
from ..core import (
    get_logger,
    deserialize_dfg,
    deserialize_variants,
    deserialize_stats,
    deserialize_deviations,
    parse_dataset_json,
)

log = get_logger(__name__)
router = APIRouter(prefix="/datasets", tags=["analysis"])


async def get_dataset_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[Dataset]:
    """Dependency for Dataset repository."""
    return BaseRepository(Dataset, db)


@router.get("/{dataset_id}/dfg", response_model=DFGResponse)
async def get_dfg(
    dataset_id: str,
    dataset_repo: BaseRepository[Dataset] = Depends(get_dataset_repo),
):
    """Get the Directly-Follows Graph for a dataset."""
    dataset = await dataset_repo.get_or_404(dataset_id)
    data = parse_dataset_json(dataset)
    
    if not data["dfg"]:
        raise HTTPException(status_code=404, detail="DFG not found")
    
    return deserialize_dfg(data["dfg"])


@router.get("/{dataset_id}/variants", response_model=VariantsResponse)
async def get_variants(
    dataset_id: str,
    limit: int = 50,
    offset: int = 0,
    dataset_repo: BaseRepository[Dataset] = Depends(get_dataset_repo),
):
    """Get process variants for a dataset."""
    dataset = await dataset_repo.get_or_404(dataset_id)
    data = parse_dataset_json(dataset)
    
    if not data["variants"]:
        raise HTTPException(status_code=404, detail="Variants not found")
    
    variants = deserialize_variants(data["variants"])
    
    # Apply pagination
    paginated_variants = variants.variants[offset:offset + limit]
    
    return VariantsResponse(
        total=variants.total,
        variants=paginated_variants,
    )


@router.get("/{dataset_id}/summary", response_model=DatasetSummary)
async def get_summary(
    dataset_id: str,
    dataset_repo: BaseRepository[Dataset] = Depends(get_dataset_repo),
):
    """Get overall statistics summary for a dataset."""
    dataset = await dataset_repo.get_or_404(dataset_id)
    data = parse_dataset_json(dataset)
    
    if not data["stats"]:
        raise HTTPException(status_code=404, detail="Stats not found")
    
    return DatasetSummary(
        dataset_id=dataset_id,
        stats=deserialize_stats(data["stats"]),
        created_at=data["created_at"],
    )


@router.get("/{dataset_id}/activities")
async def get_activities(
    dataset_id: str,
    dataset_repo: BaseRepository[Dataset] = Depends(get_dataset_repo),
):
    """Get per-activity statistics."""
    dataset = await dataset_repo.get_or_404(dataset_id)
    data = parse_dataset_json(dataset)
    
    return {
        "dataset_id": dataset_id,
        "activities": [ActivityStat(**a) for a in data["activity_stats"] or []],
    }


@router.get("/{dataset_id}/deviations")
async def get_deviations(
    dataset_id: str,
    dataset_repo: BaseRepository[Dataset] = Depends(get_dataset_repo),
):
    """Get detected process deviations."""
    dataset = await dataset_repo.get_or_404(dataset_id)
    data = parse_dataset_json(dataset)
    
    return {
        "dataset_id": dataset_id,
        "deviations": deserialize_deviations(data["deviations"]),
    }


@router.get("/{dataset_id}/full")
async def get_full_analysis(
    dataset_id: str,
    dataset_repo: BaseRepository[Dataset] = Depends(get_dataset_repo),
):
    """Get the complete analysis in one request."""
    dataset = await dataset_repo.get_or_404(dataset_id)
    data = parse_dataset_json(dataset)
    
    if not data["dfg"] or not data["variants"] or not data["stats"]:
        raise HTTPException(status_code=404, detail="Analysis data incomplete")
    
    # Use helpers - no more duplicate conversion code!
    return {
        "dataset_id": dataset_id,
        "dfg": deserialize_dfg(data["dfg"]),
        "variants": VariantsResponse(
            total=data["variants"]["total"],
            variants=deserialize_variants(data["variants"]).variants[:50],
        ),
        "stats": deserialize_stats(data["stats"]),
        "deviations": deserialize_deviations(data["deviations"]),
        "created_at": data["created_at"],
    }
