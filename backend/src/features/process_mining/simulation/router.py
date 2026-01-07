"""Simulation Router - Process Simulation API.

What-if analysis and synthetic log generation.

## Business Context
Simulation enables experimentation without real process changes:
- **Play-Out**: Generate synthetic logs from discovered models
- **What-If**: Test process modifications and see predicted impact
- **Capacity Planning**: Estimate resources for target throughput

## Testing Instructions

### Prerequisites
1. Have a discovered process model (from discovery endpoints)
2. Or have a dataset in READY status

### Test Flow
1. **Play-Out Model**:
   ```
   POST /api/v1/simulation/models/{model_id}/play-out
   {"num_traces": 100}
   ```
   → Creates new dataset with synthetic events
2. **What-If Simulation**:
   ```
   POST /api/v1/simulation/datasets/{id}/simulate
   {"modifications": [{"activity": "Review", "duration_delta": -0.5}]}
   ```
   → Returns original vs simulated metrics
3. **Capacity Plan**: `POST /api/v1/simulation/datasets/{id}/capacity-plan?target_throughput=100`

### Common Errors
- **404**: Model or Dataset not found
- **400**: Model has no serialized data
"""

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from src.api.dependencies import CurrentUser, ReadDBSession, WriteDBSession, ServiceContainer
from src.features.process_mining.models import Dataset, ProcessCase, ProcessEvent, ProcessModel
from src.features.process_mining.schemas import (
    PlayOutRequest,
    PlayOutResponse,
    SimulationRequest,
    SimulationResponse,
)
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.core.safe_unpickler import safe_loads
from src.platform.workspaces.authorization import require_dataset_permission
from src.platform.core.exceptions import BadRequestError, ModelNotFoundError, NotFoundError

logger = get_logger(__name__)

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/models/{model_id}/play-out", response_model=PlayOutResponse)
async def play_out_model(
    model_id: str,
    request: PlayOutRequest,
    db: ReadDBSession,
    user: CurrentUser,
    container: ServiceContainer,
) -> PlayOutResponse:
    """Generate synthetic event log from a process model."""
    logger.info("playing_out_model", model_id=model_id, num_traces=request.num_traces)

    query = select(ProcessModel).where(ProcessModel.id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise ModelNotFoundError(model_id=model_id)

    # Check permission on source dataset if exists
    if model.dataset_id:
        await require_dataset_permission(db, model.dataset_id, user, Permission.DATASET_READ)

    if not model.serialized_model:
        raise BadRequestError(message="Model has no serialized data")

    # BUG-028 FIX: Use safe_loads instead of pickle.loads to prevent RCE
    model_data = safe_loads(model.serialized_model)
    pm4py_log = container.simulation.play_out(model_data, model.model_format, request.num_traces)

    activities = set()
    for trace in pm4py_log:
        for event in trace:
            activities.add(event.get("concept:name", ""))

    new_log = Dataset(
        name=f"Simulated from {model.name}",
        source_format="simulated",
        total_cases=len(pm4py_log),
        total_events=sum(len(t) for t in pm4py_log),
        total_activities=len(activities),
        activities_json=json.dumps(sorted(activities)),
    )
    db.add(new_log)
    await db.flush()

    # BUG-029 FIX: Batch all cases and events, then flush once (not per-loop)
    cases = []
    for trace in pm4py_log:
        case_id = trace.attributes.get("concept:name", f"case_{hash(str(trace))}")
        case = ProcessCase(dataset_id=new_log.id, case_id=case_id)
        cases.append(case)

    db.add_all(cases)
    await db.flush()  # Single flush for all cases

    # Now create events with the flushed case IDs
    events = []
    for case, trace in zip(cases, pm4py_log, strict=False):
        for event in trace:
            process_event = ProcessEvent(
                case_ref_id=case.id,
                activity=event.get("concept:name", ""),
                timestamp=event.get("time:timestamp"),
            )
            events.append(process_event)

    db.add_all(events)  # Single add_all for all events
    await db.commit()

    return PlayOutResponse(
        model_id=model_id,
        generated_dataset_id=new_log.id,
        traces_generated=new_log.total_cases,
        events_generated=new_log.total_events,
    )


@router.post("/datasets/{dataset_id}/simulate", response_model=SimulationResponse)
async def simulate_scenario(
    dataset_id: str,
    request: SimulationRequest,
    db: ReadDBSession,
    user: CurrentUser,
    container: ServiceContainer,
) -> SimulationResponse:
    """Run what-if simulation on an event log."""
    await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
    logger.info(
        "simulating_scenario", dataset_id=dataset_id, modifications=len(request.modifications)
    )

    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise NotFoundError(resource='Dataset', resource_id=dataset_id)

    pm4py_log = container.filtering.to_pm4py_log(event_log)
    simulation_result = container.simulation.simulate_scenario(pm4py_log, request.modifications)

    return SimulationResponse(
        dataset_id=dataset_id,
        scenario=simulation_result["scenario"],
        original_metrics=simulation_result["original_metrics"],
        simulated_metrics=simulation_result["simulated_metrics"],
        impact=simulation_result["impact"],
    )


@router.post("/datasets/{dataset_id}/capacity-plan")
async def estimate_capacity(
    dataset_id: str,
    db: ReadDBSession,
    user: CurrentUser,
    container: ServiceContainer,
    target_throughput: float = Query(..., description="Target throughput"),
) -> dict[str, Any]:
    """Estimate resource requirements for target throughput."""
    await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
    logger.info("estimating_capacity", dataset_id=dataset_id, target_throughput=target_throughput)

    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise NotFoundError(resource='Dataset', resource_id=dataset_id)

    pm4py_log = container.filtering.to_pm4py_log(event_log)
    capacity_result = container.simulation.estimate_capacity(pm4py_log, target_throughput)

    return {"dataset_id": dataset_id, **capacity_result}
