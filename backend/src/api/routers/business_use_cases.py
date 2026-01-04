"""Business Use Cases API Router - P2P, O2C, Supply Chain, Customer Journey.

Phase 9 - Business Use Cases Layer.
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_session
from src.core.logging_config import get_logger
from src.models.orm import Dataset, ProcessModel
from src.services.business_use_cases import business_use_cases

logger = get_logger(__name__)

router = APIRouter(prefix="/business", tags=["Business Use Cases"])


# =============================================================================
# 9.1 Procure-to-Pay (P2P) Audit
# =============================================================================


@router.get("/p2p/mavericks/{log_id}/{reference_model_id}")
async def detect_p2p_mavericks(
    log_id: str,
    reference_model_id: str,
    threshold: float = Query(0.8, description="Fitness threshold (0-1)"),
    session: AsyncSession = Depends(get_session),
):
    """
    Detect maverick purchasing behavior in P2P process.

    Mavericks are purchase orders that don't follow the approved process model.

    Args:
        log_id: Purchase order event log ID
        reference_model_id: Approved P2P process model ID
        threshold: Fitness threshold (default 0.8). Cases below this are mavericks.

    Returns:
        Maverick cases and statistics
    """
    logger.info(
        "p2p_maverick_detection_started",
        log_id=log_id,
        model_id=reference_model_id,
        threshold=threshold,
    )

    # Get event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == log_id))
    event_log = log_result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get reference model
    model_result = await session.execute(
        select(ProcessModel).where(ProcessModel.id == reference_model_id)
    )
    reference_model = model_result.scalar_one_or_none()
    if not reference_model:
        raise HTTPException(status_code=404, detail="Reference model not found")

    try:
        return business_use_cases.detect_mavericks(event_log, reference_model, threshold)

    except Exception as e:
        logger.error("p2p_maverick_detection_failed", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to detect mavericks: {e!s}"
        ) from e


@router.get("/p2p/audit-report/{log_id}/{reference_model_id}")
async def generate_p2p_audit_report(
    log_id: str,
    reference_model_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Generate comprehensive P2P audit report.

    Includes:
    - Conformance overview
    - Maverick analysis
    - Root cause analysis
    - Recommendations

    Args:
        log_id: Purchase order event log ID
        reference_model_id: Approved P2P process model ID

    Returns:
        Comprehensive audit report
    """
    logger.info(
        "p2p_audit_report_started",
        log_id=log_id,
        model_id=reference_model_id,
    )
    start_time = time.perf_counter()

    # Get event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == log_id))
    event_log = log_result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get reference model
    model_result = await session.execute(
        select(ProcessModel).where(ProcessModel.id == reference_model_id)
    )
    reference_model = model_result.scalar_one_or_none()
    if not reference_model:
        raise HTTPException(status_code=404, detail="Reference model not found")

    try:
        report = business_use_cases.generate_p2p_audit_report(event_log, reference_model)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "p2p_audit_report_completed",
            duration_ms=round(duration_ms, 2),
        )

        return report

    except Exception as e:
        logger.error("p2p_audit_report_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate audit report: {e!s}"
        ) from e


# =============================================================================
# 9.2 Order-to-Cash (O2C) Optimization
# =============================================================================


@router.get("/o2c/split-log/{log_id}")
async def split_log_by_attribute(
    log_id: str,
    attribute: str = Query(..., description="Attribute to split on (e.g., region, product)"),
    value: str = Query(..., description="Value to filter for"),
    session: AsyncSession = Depends(get_session),
):
    """
    Split event log by attribute for comparative analysis.

    Useful for comparing processes across regions, products, or customer segments.

    Args:
        log_id: Event log ID
        attribute: Attribute to split on
        value: Specific value to filter for

    Returns:
        Statistics about filtered subset
    """
    logger.info("log_split_started", log_id=log_id, attribute=attribute, value=value)

    # Get event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == log_id))
    event_log = log_result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    try:
        return business_use_cases.split_log_by_attribute(event_log, attribute, value)

    except Exception as e:
        logger.error("log_split_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to split log: {e!s}") from e


@router.get("/o2c/compare/{log_id1}/{log_id2}")
async def compare_process_variants(
    log_id1: str,
    log_id2: str,
    log1_name: str = Query("Group A", description="Display name for first group"),
    log2_name: str = Query("Group B", description="Display name for second group"),
    session: AsyncSession = Depends(get_session),
):
    """
    Compare process variants between two logs.

    Useful for comparing performance across regions, before/after improvements, etc.

    Args:
        log_id1: First event log ID
        log_id2: Second event log ID
        log1_name: Display name for first group
        log2_name: Display name for second group

    Returns:
        Comparison metrics (durations, variants, differences)
    """
    logger.info(
        "process_comparison_started",
        log_id1=log_id1,
        log_id2=log_id2,
    )

    # Get both event logs
    log1_result = await session.execute(select(Dataset).where(Dataset.id == log_id1))
    event_log1 = log1_result.scalar_one_or_none()
    if not event_log1:
        raise HTTPException(status_code=404, detail=f"Event log {log_id1} not found")

    log2_result = await session.execute(select(Dataset).where(Dataset.id == log_id2))
    event_log2 = log2_result.scalar_one_or_none()
    if not event_log2:
        raise HTTPException(status_code=404, detail=f"Event log {log_id2} not found")

    try:
        return business_use_cases.compare_process_variants(
            event_log1, event_log2, log1_name, log2_name
        )

    except Exception as e:
        logger.error("process_comparison_failed", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to compare processes: {e!s}"
        ) from e


# =============================================================================
# 9.3 Supply Chain Simulation
# =============================================================================


@router.post("/supply-chain/simulate/{log_id}")
async def simulate_process_changes(
    log_id: str,
    activity_duration_reduction: float = Query(
        0, description="Activity duration reduction (0-1, e.g., 0.2 for 20% faster)"
    ),
    capacity_increase: float = Query(
        0, description="Capacity increase (0-1, e.g., 0.3 for 30% more capacity)"
    ),
    num_simulations: int = Query(1000, description="Number of Monte Carlo iterations"),
    session: AsyncSession = Depends(get_session),
):
    """
    Simulate process changes using Monte Carlo simulation.

    Estimates impact of process improvements on cycle time and throughput.

    Args:
        log_id: Historical event log ID
        activity_duration_reduction: Percentage reduction in activity durations (0-1)
        capacity_increase: Percentage increase in resource capacity (0-1)
        num_simulations: Number of simulation runs (default 1000)

    Returns:
        Simulation results with baseline, simulated metrics, and impact analysis
    """
    logger.info(
        "simulation_started",
        log_id=log_id,
        activity_duration_reduction=activity_duration_reduction,
        capacity_increase=capacity_increase,
    )

    # Get event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == log_id))
    event_log = log_result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    try:
        parameter_changes = {
            "activity_duration_reduction": activity_duration_reduction,
            "capacity_increase": capacity_increase,
        }

        return business_use_cases.simulate_process_changes(
            event_log, parameter_changes, num_simulations
        )

    except Exception as e:
        logger.error("simulation_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to run simulation: {e!s}"
        ) from e


# =============================================================================
# 9.4 Customer Journey Mapping
# =============================================================================


@router.get("/customer-journey/dropoffs/{log_id}")
async def detect_journey_dropoffs(
    log_id: str,
    expected_path: str | None = Query(
        None,
        description="Expected journey path (comma-separated activities). If None, uses most common path.",
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Detect drop-offs in customer journey funnel.

    Identifies at which stage customers are dropping out of the process.

    Args:
        log_id: Customer journey event log ID
        expected_path: Expected journey path (comma-separated), or None for auto-detect

    Returns:
        Drop-off analysis by stage with completion rates
    """
    logger.info("journey_dropoff_detection_started", log_id=log_id)

    # Get event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == log_id))
    event_log = log_result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    try:
        # Parse expected path if provided
        expected_path_list = None
        if expected_path:
            expected_path_list = [s.strip() for s in expected_path.split(",")]

        return business_use_cases.detect_journey_dropoffs(event_log, expected_path_list)

    except Exception as e:
        logger.error("journey_dropoff_detection_failed", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to detect drop-offs: {e!s}"
        ) from e
