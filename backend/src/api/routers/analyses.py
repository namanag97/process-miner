"""Analyses Router.

Endpoints for managing saved analyses (discovery, conformance, variants, etc.).
"""

import json

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.api.dependencies import DBSession
from src.core.logging_config import get_logger
from src.models.orm import Analysis, AnalysisStatus, Dataset
from src.models.schemas import (
    AnalysisCreateRequest,
    AnalysisDetailResponse,
    AnalysisListResponse,
    AnalysisResponse,
    DFGResponse,
    StatisticsResponse,
    VariantResponse,
)
from src.services.analysis_registry import analysis_registry

logger = get_logger(__name__)

router = APIRouter(prefix="/analyses", tags=["Analyses"])


# =============================================================================
# Metadata Endpoint (BUG-007: Dynamic Analysis Discovery)
# =============================================================================


@router.get("/metadata")
async def get_analysis_metadata() -> dict:
    """
    Get metadata for all available analysis types.

    This endpoint enables dynamic UI generation - the frontend can discover
    all available analysis types, their configuration schemas, and result types
    without hardcoding them.

    Returns a registry of 70+ analysis types with their schemas.
    """
    return analysis_registry.get_metadata()


# =============================================================================
# Helper Functions
# =============================================================================


def _analysis_to_response(analysis: Analysis) -> AnalysisResponse:
    """Convert Analysis ORM to AnalysisResponse using Pydantic model_validate."""
    return AnalysisResponse.model_validate(analysis)


# =============================================================================
# CRUD Endpoints
# =============================================================================


@router.post("", response_model=AnalysisResponse, status_code=202)
async def create_analysis(
    db: DBSession,
    log_id: str,
    request: AnalysisCreateRequest,
) -> AnalysisResponse:
    """
    Create a new analysis for an event log.

    The analysis will be queued for processing and status updated when complete.
    """
    logger.info(
        "create_analysis_started",
        log_id=log_id,
        name=request.name,
        analysis_type=request.analysis_type,
    )

    # Verify log exists
    log_result = await db.execute(select(Dataset).where(Dataset.id == log_id))
    event_log = log_result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log not found: {log_id}")

    analysis = Analysis(
        dataset_id=log_id,  # BUG-001 FIX: ORM uses dataset_id
        name=request.name,
        analysis_type=request.analysis_type,
        config_json=json.dumps(request.config) if request.config else None,
        status=AnalysisStatus.PENDING.value,
    )
    db.add(analysis)
    await db.flush()

    # Queue async background task
    from src.infrastructure.tasks import perform_analysis_task

    task = perform_analysis_task.delay(
        analysis_id=analysis.id,
        log_id=log_id,
        analysis_type=request.analysis_type,
        config=request.config or {},
    )

    logger.info(
        "analysis_task_queued",
        analysis_id=analysis.id,
        task_id=task.id,
        log_id=log_id,
    )

    await db.commit()
    await db.refresh(analysis)

    logger.info(
        "create_analysis_completed",
        analysis_id=analysis.id,
        status=analysis.status,
    )

    return _analysis_to_response(analysis)


@router.get("", response_model=AnalysisListResponse)
async def list_analyses(
    db: DBSession,
    log_id: str | None = Query(None, description="Filter by event log ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> AnalysisListResponse:
    """
    List analyses, optionally filtered by event log.
    """
    query = select(Analysis).order_by(Analysis.created_at.desc())

    if log_id:
        query = query.where(Analysis.dataset_id == log_id)  # BUG-001 FIX

    # Count total
    count_query = select(func.count()).select_from(Analysis)
    if log_id:
        count_query = count_query.where(Analysis.dataset_id == log_id)  # BUG-001 FIX
    total = await db.scalar(count_query) or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    analyses = result.scalars().all()

    return AnalysisListResponse(
        items=[_analysis_to_response(a) for a in analyses],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )


@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
async def get_analysis(
    db: DBSession,
    analysis_id: str,
    include_results: bool = Query(True, description="Include full DFG/variants/statistics"),
) -> AnalysisDetailResponse:
    """
    Get analysis details with optional full results.
    """
    result = await db.execute(
        select(Analysis)
        .options(selectinload(Analysis.process_model))
        .where(Analysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    response = _analysis_to_response(analysis)

    # Convert to detail response with results
    detail = AnalysisDetailResponse(
        **response.model_dump(),
        dfg=None,
        variants=None,
        statistics=None,
    )

    if include_results and analysis.status == AnalysisStatus.COMPLETED.value:
        try:
            # Use cached results from result_json (BUG-003 fix)
            if analysis.result_json:
                result_data = json.loads(analysis.result_json)

                # Extract DFG if present
                if "dfg" in result_data:
                    detail.dfg = DFGResponse(**result_data["dfg"])

                # Extract variants if present
                if "variants" in result_data:
                    variants_data = result_data["variants"]
                    detail.variants = [
                        VariantResponse(
                            variant_key=v["variant"],
                            activity_trace=v["variant"],
                            activities=v["variant"].split(" -> "),
                            case_count=v["count"],
                            frequency_percent=0,  # Would need total cases to calculate
                        )
                        for v in variants_data.get("top_variants", [])
                    ]

                # Extract statistics if present
                if "statistics" in result_data:
                    stats_data = result_data["statistics"]
                    detail.statistics = StatisticsResponse(
                        total_events=stats_data.get("total_events", 0),
                        total_cases=stats_data.get("total_cases", 0),
                        total_activities=stats_data.get("total_activities", 0),
                        total_variants=stats_data.get("total_variants", 0),
                        activities=stats_data.get("activities", []),
                        start_activities=stats_data.get("start_activities", {}),
                        end_activities=stats_data.get("end_activities", {}),
                        avg_case_duration_seconds=stats_data.get("avg_case_duration_seconds"),
                        min_case_duration_seconds=stats_data.get("min_case_duration_seconds"),
                        max_case_duration_seconds=stats_data.get("max_case_duration_seconds"),
                        date_range=stats_data.get("date_range"),
                    )
        except Exception as e:
            logger.warning("get_analysis_results_failed", error=str(e), analysis_id=analysis_id)

    return detail


@router.delete("/{analysis_id}", status_code=204)
async def delete_analysis(
    db: DBSession,
    analysis_id: str,
) -> None:
    """
    Delete an analysis.
    """
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    await db.delete(analysis)
    await db.commit()

    logger.info("delete_analysis_completed", analysis_id=analysis_id)


# =============================================================================
# Convenience Endpoints
# =============================================================================


@router.get("/log/{log_id}", response_model=list[AnalysisResponse])
async def list_analyses_for_log(
    db: DBSession,
    log_id: str,
) -> list[AnalysisResponse]:
    """
    Get all analyses for a specific event log.
    """
    # Verify log exists
    log_result = await db.execute(select(Dataset).where(Dataset.id == log_id))
    if not log_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Event log not found: {log_id}")

    result = await db.execute(
        select(Analysis)
        .where(Analysis.dataset_id == log_id)  # BUG-001 FIX
        .order_by(Analysis.created_at.desc())
    )
    analyses = result.scalars().all()

    return [_analysis_to_response(a) for a in analyses]
