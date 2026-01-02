"""Analyses Router.

Endpoints for managing saved analyses (discovery, conformance, variants, etc.).
"""

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.api.dependencies import DBSession
from src.core.logging_config import get_logger
from src.models.orm import Analysis, AnalysisStatus, AnalysisType, Dataset, ProcessModel
from src.models.schemas import (
    AnalysisCreateRequest,
    AnalysisDetailResponse,
    AnalysisListResponse,
    AnalysisResponse,
    DFGResponse,
    StatisticsResponse,
    VariantResponse,
)
from src.services.mining import mining_service

logger = get_logger(__name__)

router = APIRouter(prefix="/analyses", tags=["Analyses"])


# =============================================================================
# Helper Functions
# =============================================================================


def _analysis_to_response(analysis: Analysis) -> AnalysisResponse:
    """Convert Analysis ORM to AnalysisResponse."""
    config = None
    if analysis.config_json:
        try:
            config = json.loads(analysis.config_json)
        except json.JSONDecodeError:
            config = {}

    result_summary = None
    if analysis.result_summary_json:
        try:
            result_summary = json.loads(analysis.result_summary_json)
        except json.JSONDecodeError:
            result_summary = {}

    return AnalysisResponse(
        id=analysis.id,
        log_id=analysis.log_id,
        name=analysis.name,
        analysis_type=analysis.analysis_type,
        status=analysis.status,
        config=config,
        result_summary=result_summary,
        model_id=analysis.model_id,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
        error_message=analysis.error_message,
    )


# =============================================================================
# CRUD Endpoints
# =============================================================================


@router.post("", response_model=AnalysisResponse, status_code=201)
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

    # Create analysis record
    analysis = Analysis(
        log_id=log_id,
        name=request.name,
        analysis_type=request.analysis_type,
        config_json=json.dumps(request.config) if request.config else None,
        status=AnalysisStatus.PENDING.value,
    )
    db.add(analysis)
    await db.flush()

    # For now, run inline (future: queue async job)
    try:
        analysis.status = AnalysisStatus.RUNNING.value
        await db.flush()

        if request.analysis_type == AnalysisType.DISCOVERY.value:
            # Run discovery and save model
            miner_type = request.config.get("miner_type", "inductive")
            from src.core.enums import MinerType
            miner = MinerType(miner_type) if miner_type else MinerType.INDUCTIVE
            
            # Get DFG for summary
            dfg_data = mining_service.get_dfg_fast(log_id)
            
            analysis.result_summary_json = json.dumps({
                "nodes_count": len(dfg_data.get("nodes", [])),
                "edges_count": len(dfg_data.get("edges", [])),
                "start_activities": list(dfg_data.get("start_activities", {}).keys()),
                "end_activities": list(dfg_data.get("end_activities", {}).keys()),
            })

        elif request.analysis_type == AnalysisType.VARIANTS.value:
            # Get variants
            variants_data = mining_service.get_variants_fast(log_id, top_n=50)
            analysis.result_summary_json = json.dumps({
                "total_variants": variants_data.get("total_variants", 0),
                "top_variant": variants_data.get("top_variants", [{}])[0] if variants_data.get("top_variants") else None,
            })

        else:
            # Generic: just get statistics
            stats = mining_service.get_statistics_fast(log_id)
            analysis.result_summary_json = json.dumps(stats)

        analysis.status = AnalysisStatus.COMPLETED.value
        analysis.completed_at = datetime.utcnow()

    except Exception as e:
        logger.error("create_analysis_failed", error=str(e), log_id=log_id)
        analysis.status = AnalysisStatus.FAILED.value
        analysis.error_message = str(e)

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
    log_id: Optional[str] = Query(None, description="Filter by event log ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> AnalysisListResponse:
    """
    List analyses, optionally filtered by event log.
    """
    query = select(Analysis).order_by(Analysis.created_at.desc())

    if log_id:
        query = query.where(Analysis.log_id == log_id)

    # Count total
    count_query = select(func.count()).select_from(Analysis)
    if log_id:
        count_query = count_query.where(Analysis.log_id == log_id)
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
            # Load live data for the analysis
            dfg_data = mining_service.get_dfg_fast(analysis.log_id)
            detail.dfg = DFGResponse(**dfg_data)

            variants_data = mining_service.get_variants_fast(analysis.log_id, top_n=20)
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

            stats_data = mining_service.get_statistics_fast(analysis.log_id)
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
        .where(Analysis.log_id == log_id)
        .order_by(Analysis.created_at.desc())
    )
    analyses = result.scalars().all()

    return [_analysis_to_response(a) for a in analyses]
