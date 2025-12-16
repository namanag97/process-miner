"""
Analysis router - Serves processed analysis results.

After processing, this router provides:
- DFG (Directly-Follows Graph) in React Flow format
- Variants list
- Statistics summary
- Activity statistics
- Deviations

All responses are optimized for direct use by the React frontend.
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from ..models.schemas import (
    DFGResponse,
    DFGNode,
    DFGEdge,
    DFGSummary,
    ActivityNodeData,
    NodePosition,
    EdgeData,
    VariantsResponse,
    VariantItem,
    DatasetSummary,
    ProcessStats,
    ActivityStat,
    Deviation,
)
from .processing import get_dataset_info

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets", tags=["analysis"])


@router.get("/{dataset_id}/dfg", response_model=DFGResponse)
async def get_dfg(dataset_id: str):
    """
    Get the Directly-Follows Graph for a dataset.
    
    Returns nodes and edges in React Flow format, ready for direct use
    by the ProcessMapViewer component.
    
    Query params (future):
    - min_frequency: Filter edges below threshold
    - activities: Filter to specific activities
    - start_date, end_date: Time range filter
    """
    dataset = get_dataset_info(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dfg = dataset["dfg"]
    
    # Convert stored dict back to Pydantic models
    return DFGResponse(
        nodes=[
            DFGNode(
                id=n["id"],
                type=n["type"],
                position=NodePosition(**n["position"]),
                data=ActivityNodeData(**n["data"]),
            )
            for n in dfg["nodes"]
        ],
        edges=[
            DFGEdge(
                id=e["id"],
                source=e["source"],
                target=e["target"],
                type=e["type"],
                data=EdgeData(**e["data"]),
            )
            for e in dfg["edges"]
        ],
        summary=DFGSummary(**dfg["summary"]),
    )


@router.get("/{dataset_id}/variants", response_model=VariantsResponse)
async def get_variants(
    dataset_id: str,
    limit: int = 50,
    offset: int = 0,
):
    """
    Get process variants for a dataset.
    
    Variants are sorted by frequency (most common first).
    The first variant is marked as the "happy path".
    """
    dataset = get_dataset_info(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    variants = dataset["variants"]
    all_items = [VariantItem(**v) for v in variants["variants"]]
    
    # Apply pagination
    paginated = all_items[offset:offset + limit]
    
    return VariantsResponse(
        total=variants["total"],
        variants=paginated,
    )


@router.get("/{dataset_id}/summary", response_model=DatasetSummary)
async def get_summary(dataset_id: str):
    """
    Get overall statistics summary for a dataset.
    
    Includes:
    - Total cases, events, activities, variants
    - Average and median case duration
    - Start and end activities
    """
    dataset = get_dataset_info(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    stats = dataset["stats"]
    
    return DatasetSummary(
        dataset_id=dataset_id,
        stats=ProcessStats(
            total_cases=stats["total_cases"],
            total_events=stats["total_events"],
            total_activities=stats["total_activities"],
            total_variants=stats["total_variants"],
            avg_case_duration_ms=stats["avg_case_duration_ms"],
            median_case_duration_ms=stats["median_case_duration_ms"],
            start_activities=stats["start_activities"],
            end_activities=stats["end_activities"],
        ),
        created_at=dataset["created_at"],
    )


@router.get("/{dataset_id}/activities")
async def get_activities(dataset_id: str):
    """
    Get per-activity statistics.
    
    Returns frequency, start/end flags, and duration for each activity.
    """
    dataset = get_dataset_info(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return {
        "dataset_id": dataset_id,
        "activities": [
            ActivityStat(**a) for a in dataset["activity_stats"]
        ],
    }


@router.get("/{dataset_id}/deviations")
async def get_deviations(dataset_id: str):
    """
    Get detected process deviations.
    
    Includes:
    - Rework (repeated activities)
    - Skips (missing expected activities)
    - Unusual paths (low-frequency variants)
    """
    dataset = get_dataset_info(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return {
        "dataset_id": dataset_id,
        "deviations": [
            Deviation(**d) for d in dataset["deviations"]
        ],
    }


@router.get("/{dataset_id}/full")
async def get_full_analysis(dataset_id: str):
    """
    Get the complete analysis in one request.
    
    Useful for initial load - returns DFG, variants, stats, and deviations.
    """
    dataset = get_dataset_info(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dfg = dataset["dfg"]
    variants = dataset["variants"]
    stats = dataset["stats"]
    
    return {
        "dataset_id": dataset_id,
        "dfg": DFGResponse(
            nodes=[
                DFGNode(
                    id=n["id"],
                    type=n["type"],
                    position=NodePosition(**n["position"]),
                    data=ActivityNodeData(**n["data"]),
                )
                for n in dfg["nodes"]
            ],
            edges=[
                DFGEdge(
                    id=e["id"],
                    source=e["source"],
                    target=e["target"],
                    type=e["type"],
                    data=EdgeData(**e["data"]),
                )
                for e in dfg["edges"]
            ],
            summary=DFGSummary(**dfg["summary"]),
        ),
        "variants": VariantsResponse(
            total=variants["total"],
            variants=[VariantItem(**v) for v in variants["variants"][:50]],
        ),
        "stats": ProcessStats(
            total_cases=stats["total_cases"],
            total_events=stats["total_events"],
            total_activities=stats["total_activities"],
            total_variants=stats["total_variants"],
            avg_case_duration_ms=stats["avg_case_duration_ms"],
            median_case_duration_ms=stats["median_case_duration_ms"],
            start_activities=stats["start_activities"],
            end_activities=stats["end_activities"],
        ),
        "deviations": [Deviation(**d) for d in dataset["deviations"]],
        "created_at": dataset["created_at"],
    }
