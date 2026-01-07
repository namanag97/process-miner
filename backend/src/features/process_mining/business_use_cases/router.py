"""Business Use Cases API Router - P2P, O2C, Supply Chain, Customer Journey.

Industry-specific process mining templates.

## Business Context
Pre-built analyses for common business scenarios:
- **P2P (Procure-to-Pay)**: Maverick detection, audit reports
- **O2C (Order-to-Cash)**: Cross-region comparison, log splitting
- **Supply Chain**: Monte Carlo simulation of process changes
- **Customer Journey**: Drop-off funnel analysis
"""

import time

from fastapi import APIRouter, Query
from sqlalchemy import select

from src.api.dependencies import ReadDBSession
from src.features.process_mining.business_use_cases.service import business_use_cases
from src.features.process_mining.models import Dataset, ProcessModel
from src.infra.core.exceptions import ModelNotFoundError, NotFoundError, ProcessingError
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/business", tags=["Business Use Cases"])


async def _get_dataset_or_404(db: ReadDBSession, dataset_id: str) -> Dataset:
    """Get dataset or raise 404."""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise NotFoundError(resource='Dataset', resource_id=dataset_id)
    return dataset


async def _get_model_or_404(db: ReadDBSession, model_id: str) -> ProcessModel:
    """Get process model or raise 404."""
    result = await db.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise ModelNotFoundError(model_id=model_id)
    return model


# =============================================================================
# 9.1 Procure-to-Pay (P2P) Audit
# =============================================================================


@router.get("/p2p/mavericks/{dataset_id}/{reference_model_id}")
async def detect_p2p_mavericks(
    dataset_id: str,
    reference_model_id: str,
    db: ReadDBSession,
    threshold: float = Query(0.8, description="Fitness threshold (0-1)"),
):
    """Detect maverick purchasing behavior in P2P process."""
    event_log = await _get_dataset_or_404(db, dataset_id)
    reference_model = await _get_model_or_404(db, reference_model_id)

    try:
        return business_use_cases.detect_mavericks(event_log, reference_model, threshold)
    except Exception as e:
        logger.error("p2p_maverick_detection_failed", error=str(e), exc_info=True)
        raise ProcessingError(message=f"Maverick detection failed: {e!s}") from e


@router.get("/p2p/audit-report/{dataset_id}/{reference_model_id}")
async def generate_p2p_audit_report(
    dataset_id: str,
    reference_model_id: str,
    db: ReadDBSession,
):
    """Generate comprehensive P2P audit report."""
    start_time = time.perf_counter()

    event_log = await _get_dataset_or_404(db, dataset_id)
    reference_model = await _get_model_or_404(db, reference_model_id)

    try:
        report = business_use_cases.generate_p2p_audit_report(event_log, reference_model)
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("p2p_audit_report_completed", duration_ms=round(duration_ms, 2))
        return report
    except Exception as e:
        logger.error("p2p_audit_report_failed", error=str(e), exc_info=True)
        raise ProcessingError(message=f"Audit report generation failed: {e!s}") from e


# =============================================================================
# 9.2 Order-to-Cash (O2C) Optimization
# =============================================================================


@router.get("/o2c/split-log/{dataset_id}")
async def split_log_by_attribute(
    dataset_id: str,
    db: ReadDBSession,
    attribute: str = Query(..., description="Attribute to split on"),
    value: str = Query(..., description="Value to filter for"),
):
    """Split event log by attribute for comparative analysis."""
    event_log = await _get_dataset_or_404(db, dataset_id)

    try:
        return business_use_cases.split_log_by_attribute(event_log, attribute, value)
    except Exception as e:
        logger.error("log_split_failed", error=str(e), exc_info=True)
        raise ProcessingError(message=f"Log split failed: {e!s}") from e


@router.get("/o2c/compare/{dataset_id1}/{dataset_id2}")
async def compare_process_variants(
    dataset_id1: str,
    dataset_id2: str,
    db: ReadDBSession,
    log1_name: str = Query("Group A"),
    log2_name: str = Query("Group B"),
):
    """Compare process variants between two logs."""
    event_log1 = await _get_dataset_or_404(db, dataset_id1)
    event_log2 = await _get_dataset_or_404(db, dataset_id2)

    try:
        return business_use_cases.compare_process_variants(
            event_log1, event_log2, log1_name, log2_name
        )
    except Exception as e:
        logger.error("process_comparison_failed", error=str(e), exc_info=True)
        raise ProcessingError(message=f"Process comparison failed: {e!s}") from e


# =============================================================================
# 9.3 Supply Chain Simulation
# =============================================================================


@router.post("/supply-chain/simulate/{dataset_id}")
async def simulate_process_changes(
    dataset_id: str,
    db: ReadDBSession,
    activity_duration_reduction: float = Query(0, description="Activity duration reduction (0-1)"),
    capacity_increase: float = Query(0, description="Capacity increase (0-1)"),
    num_simulations: int = Query(1000, description="Number of Monte Carlo iterations"),
):
    """Simulate process changes using Monte Carlo simulation."""
    event_log = await _get_dataset_or_404(db, dataset_id)

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
        raise ProcessingError(message=f"Simulation failed: {e!s}") from e


# =============================================================================
# 9.4 Customer Journey Mapping
# =============================================================================


@router.get("/customer-journey/dropoffs/{dataset_id}")
async def detect_journey_dropoffs(
    dataset_id: str,
    db: ReadDBSession,
    expected_path: str | None = Query(None, description="Expected journey path (comma-separated)"),
):
    """Detect drop-offs in customer journey funnel."""
    event_log = await _get_dataset_or_404(db, dataset_id)

    try:
        expected_path_list = (
            [s.strip() for s in expected_path.split(",")] if expected_path else None
        )
        return business_use_cases.detect_journey_dropoffs(event_log, expected_path_list)
    except Exception as e:
        logger.error("journey_dropoff_detection_failed", error=str(e), exc_info=True)
        raise ProcessingError(message=f"Drop-off detection failed: {e!s}") from e
