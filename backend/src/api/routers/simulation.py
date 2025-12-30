"""Simulation Router - Process Simulation API.

Provides endpoints for model play-out, what-if simulation, and capacity planning.
"""

import json
import pickle
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.core.logging_config import get_logger
from src.models.orm import EventLog, ProcessCase, ProcessEvent, ProcessModel
from src.models.schemas import (
    PlayOutRequest,
    PlayOutResponse,
    SimulationRequest,
    SimulationResponse,
)
from src.services.filtering import filtering_service
from src.services.simulation import simulation_service

logger = get_logger(__name__)

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/models/{model_id}/play-out", response_model=PlayOutResponse)
async def play_out_model(
    model_id: str,
    request: PlayOutRequest,
    db: AsyncSession = Depends(get_db),
) -> PlayOutResponse:
    """Generate synthetic event log from a process model."""
    logger.info("playing_out_model", model_id=model_id, num_traces=request.num_traces)

    query = select(ProcessModel).where(ProcessModel.id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

    if not model.serialized_model:
        raise HTTPException(status_code=400, detail="Model has no serialized data")

    model_data = pickle.loads(model.serialized_model)
    pm4py_log = simulation_service.play_out(model_data, model.model_format, request.num_traces)

    activities = set()
    for trace in pm4py_log:
        for event in trace:
            activities.add(event.get("concept:name", ""))

    new_log = EventLog(
        name=f"Simulated from {model.name}",
        source_format="simulated",
        total_cases=len(pm4py_log),
        total_events=sum(len(t) for t in pm4py_log),
        total_activities=len(activities),
        activities_json=json.dumps(sorted(list(activities))),
    )
    db.add(new_log)
    await db.flush()

    for trace in pm4py_log:
        case_id = trace.attributes.get("concept:name", f"case_{hash(str(trace))}")
        case = ProcessCase(log_id=new_log.id, case_id=case_id)
        db.add(case)
        await db.flush()

        for event in trace:
            process_event = ProcessEvent(
                case_ref_id=case.id,
                activity=event.get("concept:name", ""),
                timestamp=event.get("time:timestamp"),
            )
            db.add(process_event)

    await db.commit()

    return PlayOutResponse(
        model_id=model_id,
        generated_log_id=new_log.id,
        traces_generated=new_log.total_cases,
        events_generated=new_log.total_events,
    )


@router.post("/logs/{log_id}/simulate", response_model=SimulationResponse)
async def simulate_scenario(
    log_id: str,
    request: SimulationRequest,
    db: AsyncSession = Depends(get_db),
) -> SimulationResponse:
    """Run what-if simulation on an event log."""
    logger.info("simulating_scenario", log_id=log_id, modifications=len(request.modifications))

    query = select(EventLog).where(EventLog.id == log_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log {log_id} not found")

    pm4py_log = filtering_service.to_pm4py_log(event_log)
    simulation_result = simulation_service.simulate_scenario(pm4py_log, request.modifications)

    return SimulationResponse(
        log_id=log_id,
        scenario=simulation_result["scenario"],
        original_metrics=simulation_result["original_metrics"],
        simulated_metrics=simulation_result["simulated_metrics"],
        impact=simulation_result["impact"],
    )


@router.post("/logs/{log_id}/capacity-plan")
async def estimate_capacity(
    log_id: str,
    target_throughput: float,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Estimate resource requirements for target throughput."""
    logger.info("estimating_capacity", log_id=log_id, target_throughput=target_throughput)

    query = select(EventLog).where(EventLog.id == log_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log {log_id} not found")

    pm4py_log = filtering_service.to_pm4py_log(event_log)
    capacity_result = simulation_service.estimate_capacity(pm4py_log, target_throughput)

    return {"log_id": log_id, **capacity_result}
