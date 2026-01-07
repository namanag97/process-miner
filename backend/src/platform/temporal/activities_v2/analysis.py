"""Analysis Activities v2 - Stateless and Idempotent.

Activities for process discovery and conformance checking.
Each activity is self-contained and can be retried safely.
"""

import json
import time
from datetime import datetime

import structlog
from temporalio import activity

from src.platform.temporal.activities_v2.types import (
    EventLogInfo,
    DiscoveryResult,
    ConformanceResult,
    ModelMetrics,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Event Log Activities
# =============================================================================


@activity.defn
async def load_event_log(dataset_id: str) -> dict:
    """Load and verify event log is ready for analysis.
    
    Idempotent - just reads data.
    
    Args:
        dataset_id: UUID of the dataset
    
    Returns:
        dict with is_ready, total_cases, total_events
    """
    logger.info("load_event_log_started", dataset_id=dataset_id)
    activity.heartbeat("loading_event_log")
    
    try:
        from sqlalchemy import select, func
        from src.features.process_mining.models import Dataset, DatasetStatus, ProcessCase, ProcessEvent
        from src.platform.infrastructure.tasks.base import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            dataset = await db.get(Dataset, dataset_id)
            
            if not dataset:
                return {"is_ready": False, "error": "Dataset not found"}
            
            if dataset.status != DatasetStatus.READY.value:
                return {"is_ready": False, "error": f"Dataset status is {dataset.status}, expected READY"}
            
            # Get counts
            case_count = await db.scalar(
                select(func.count()).select_from(ProcessCase).where(
                    ProcessCase.dataset_id == dataset_id
                )
            ) or 0
            
            event_count = await db.scalar(
                select(func.count())
                .select_from(ProcessEvent)
                .join(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
            ) or 0
            
            activity_count = await db.scalar(
                select(func.count(func.distinct(ProcessEvent.activity)))
                .select_from(ProcessEvent)
                .join(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
            ) or 0
        
        logger.info(
            "load_event_log_completed",
            dataset_id=dataset_id,
            total_cases=case_count,
            total_events=event_count,
        )
        
        return {
            "is_ready": True,
            "total_cases": case_count,
            "total_events": event_count,
            "total_activities": activity_count,
        }
        
    except Exception as e:
        logger.error("load_event_log_failed", dataset_id=dataset_id, error=str(e))
        raise


# =============================================================================
# Process Discovery Activities
# =============================================================================


@activity.defn
async def discover_process_model(dataset_id: str, miner_type: str) -> DiscoveryResult:
    """Discover process model using specified mining algorithm.
    
    Long-running operation with heartbeats.
    
    Args:
        dataset_id: UUID of the dataset
        miner_type: Mining algorithm (alpha, inductive, heuristic, ilp)
    
    Returns:
        DiscoveryResult with model_data and initial metrics
    """
    logger.info("discover_process_model_started", dataset_id=dataset_id, miner_type=miner_type)
    activity.heartbeat("starting_discovery")
    
    start_time = time.perf_counter()
    
    try:
        from sqlalchemy import select
        from src.features.process_mining.models import ProcessCase, ProcessEvent
        from src.features.process_mining.services.analysis.pm4py_wrapper import pm4py_discovery_service
        from src.platform.infrastructure.tasks.base import AsyncSessionLocal
        
        # Load event log data
        activity.heartbeat("loading_events")
        
        async with AsyncSessionLocal() as db:
            # Get all events for dataset
            result = await db.execute(
                select(ProcessEvent, ProcessCase.case_id)
                .join(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
                .order_by(ProcessCase.case_id, ProcessEvent.timestamp)
            )
            rows = result.all()
        
        # Convert to PM4Py format
        activity.heartbeat("converting_to_pm4py")
        
        events = []
        for event, case_id in rows:
            events.append({
                "case:concept:name": case_id,
                "concept:name": event.activity,
                "time:timestamp": event.timestamp,
                "org:resource": event.resource,
            })
        
        if not events:
            raise ValueError("No events found in dataset")
        
        # Run discovery algorithm
        activity.heartbeat(f"running_{miner_type}_miner")
        
        model_data, fitness, precision = await pm4py_discovery_service.discover(
            events=events,
            miner_type=miner_type,
            heartbeat_callback=lambda msg: activity.heartbeat(msg),
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        logger.info(
            "discover_process_model_completed",
            dataset_id=dataset_id,
            miner_type=miner_type,
            fitness=fitness,
            precision=precision,
            duration_ms=round(duration_ms, 2),
        )
        
        return DiscoveryResult(
            model_data=model_data,
            model_format="pnml",
            fitness=fitness,
            precision=precision,
        )
        
    except Exception as e:
        logger.error(
            "discover_process_model_failed",
            dataset_id=dataset_id,
            miner_type=miner_type,
            error=str(e),
        )
        raise


@activity.defn
async def compute_model_metrics(dataset_id: str, model_data: bytes) -> dict:
    """Compute quality metrics for a process model.
    
    Args:
        dataset_id: UUID of the dataset
        model_data: Serialized model (PNML)
    
    Returns:
        dict with fitness, precision, generalization, simplicity
    """
    logger.info("compute_model_metrics_started", dataset_id=dataset_id)
    activity.heartbeat("computing_metrics")
    
    try:
        from src.features.process_mining.services.analysis.pm4py_wrapper import pm4py_metrics_service
        
        metrics = await pm4py_metrics_service.compute_metrics(
            dataset_id=dataset_id,
            model_data=model_data,
        )
        
        logger.info(
            "compute_model_metrics_completed",
            dataset_id=dataset_id,
            fitness=metrics.get("fitness"),
            precision=metrics.get("precision"),
        )
        
        return metrics
        
    except Exception as e:
        logger.error("compute_model_metrics_failed", dataset_id=dataset_id, error=str(e))
        # Return partial metrics on failure
        return {"fitness": None, "precision": None}


@activity.defn
async def save_process_model(
    dataset_id: str,
    model_name: str,
    model_data: bytes,
    metrics: dict,
) -> str:
    """Save process model to database.
    
    Idempotent via upsert on (dataset_id, model_name).
    
    Args:
        dataset_id: UUID of the dataset
        model_name: Name for the model
        model_data: Serialized model
        metrics: Quality metrics
    
    Returns:
        model_id (UUID string)
    """
    logger.info("save_process_model_started", dataset_id=dataset_id, model_name=model_name)
    
    try:
        from sqlalchemy import select
        from sqlalchemy.dialects.postgresql import insert
        from src.features.process_mining.models import ProcessModel
        from src.platform.infrastructure.tasks.base import AsyncSessionLocal
        from uuid import uuid4
        
        async with AsyncSessionLocal() as db:
            # Check for existing model with same name
            existing = await db.execute(
                select(ProcessModel).where(
                    ProcessModel.dataset_id == dataset_id,
                    ProcessModel.name == model_name,
                )
            )
            model = existing.scalar_one_or_none()
            
            if model:
                # Update existing
                model.pnml_content = model_data.decode("utf-8") if isinstance(model_data, bytes) else model_data
                model.fitness = metrics.get("fitness")
                model.precision = metrics.get("precision")
                model.updated_at = datetime.utcnow()
                model_id = model.id
            else:
                # Create new
                model_id = str(uuid4())
                model = ProcessModel(
                    id=model_id,
                    dataset_id=dataset_id,
                    name=model_name,
                    pnml_content=model_data.decode("utf-8") if isinstance(model_data, bytes) else model_data,
                    fitness=metrics.get("fitness"),
                    precision=metrics.get("precision"),
                )
                db.add(model)
            
            await db.commit()
        
        logger.info("save_process_model_completed", model_id=model_id)
        return model_id
        
    except Exception as e:
        logger.error("save_process_model_failed", dataset_id=dataset_id, error=str(e))
        raise


@activity.defn
async def load_process_model(model_id: str) -> dict:
    """Load process model from database.
    
    Idempotent - just reads data.
    
    Args:
        model_id: UUID of the process model
    
    Returns:
        dict with model_data and metadata
    """
    logger.info("load_process_model_started", model_id=model_id)
    
    try:
        from src.features.process_mining.models import ProcessModel
        from src.platform.infrastructure.tasks.base import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            model = await db.get(ProcessModel, model_id)
            
            if not model:
                raise ValueError(f"Process model not found: {model_id}")
            
            return {
                "model_id": model.id,
                "model_data": model.pnml_content.encode("utf-8") if model.pnml_content else b"",
                "model_format": "pnml",
                "name": model.name,
            }
            
    except Exception as e:
        logger.error("load_process_model_failed", model_id=model_id, error=str(e))
        raise


# =============================================================================
# Conformance Checking Activities
# =============================================================================


@activity.defn
async def check_conformance(
    dataset_id: str,
    model_data: dict,
    method: str,
) -> ConformanceResult:
    """Run conformance checking between event log and model.
    
    Args:
        dataset_id: UUID of the dataset
        model_data: dict with model_data bytes and format
        method: Conformance method (token_replay or alignment)
    
    Returns:
        ConformanceResult with fitness, precision, etc.
    """
    logger.info(
        "check_conformance_started",
        dataset_id=dataset_id,
        method=method,
    )
    activity.heartbeat("starting_conformance_check")
    
    start_time = time.perf_counter()
    
    try:
        from sqlalchemy import select
        from src.features.process_mining.models import ProcessCase, ProcessEvent
        from src.features.process_mining.services.analysis.pm4py_wrapper import pm4py_conformance_service
        from src.platform.infrastructure.tasks.base import AsyncSessionLocal
        
        # Load event log
        activity.heartbeat("loading_events")
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ProcessEvent, ProcessCase.case_id)
                .join(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
                .order_by(ProcessCase.case_id, ProcessEvent.timestamp)
            )
            rows = result.all()
        
        # Convert to PM4Py format
        events = []
        for event, case_id in rows:
            events.append({
                "case:concept:name": case_id,
                "concept:name": event.activity,
                "time:timestamp": event.timestamp,
            })
        
        # Run conformance check
        activity.heartbeat(f"running_{method}")
        
        conformance = await pm4py_conformance_service.check_conformance(
            events=events,
            model_data=model_data["model_data"],
            method=method,
            heartbeat_callback=lambda msg: activity.heartbeat(msg),
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        logger.info(
            "check_conformance_completed",
            dataset_id=dataset_id,
            fitness=conformance["fitness"],
            duration_ms=round(duration_ms, 2),
        )
        
        return ConformanceResult(
            fitness=conformance["fitness"],
            precision=conformance["precision"],
            is_conformant=conformance["fitness"] >= 0.8,
            fitting_traces=conformance["fitting_traces"],
            total_traces=conformance["total_traces"],
            deviations=conformance.get("deviations", []),
        )
        
    except Exception as e:
        logger.error("check_conformance_failed", dataset_id=dataset_id, error=str(e))
        raise


@activity.defn
async def save_conformance_result(
    dataset_id: str,
    model_id: str,
    result: ConformanceResult,
) -> str:
    """Save conformance result to database.
    
    Idempotent via upsert on (dataset_id, model_id).
    
    Args:
        dataset_id: UUID of the dataset
        model_id: UUID of the process model
        result: ConformanceResult
    
    Returns:
        conformance_id (UUID string)
    """
    logger.info(
        "save_conformance_result_started",
        dataset_id=dataset_id,
        model_id=model_id,
    )
    
    try:
        from sqlalchemy import select
        from src.features.process_mining.models import ConformanceResult as ConformanceModel
        from src.platform.infrastructure.tasks.base import AsyncSessionLocal
        from uuid import uuid4
        
        async with AsyncSessionLocal() as db:
            # Check for existing result
            existing = await db.execute(
                select(ConformanceModel).where(
                    ConformanceModel.dataset_id == dataset_id,
                    ConformanceModel.model_id == model_id,
                )
            )
            conformance = existing.scalar_one_or_none()
            
            if conformance:
                # Update existing
                conformance.fitness = result.fitness
                conformance.precision = result.precision
                conformance.fitting_traces = result.fitting_traces
                conformance.total_traces = result.total_traces
                conformance.updated_at = datetime.utcnow()
                conformance_id = conformance.id
            else:
                # Create new
                conformance_id = str(uuid4())
                conformance = ConformanceModel(
                    id=conformance_id,
                    dataset_id=dataset_id,
                    model_id=model_id,
                    fitness=result.fitness,
                    precision=result.precision,
                    fitting_traces=result.fitting_traces,
                    total_traces=result.total_traces,
                )
                db.add(conformance)
            
            await db.commit()
        
        logger.info("save_conformance_result_completed", conformance_id=conformance_id)
        return conformance_id
        
    except Exception as e:
        logger.error(
            "save_conformance_result_failed",
            dataset_id=dataset_id,
            model_id=model_id,
            error=str(e),
        )
        raise
