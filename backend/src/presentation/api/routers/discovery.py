"""Process Discovery API Router."""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.core.discovery_service import discovery_service
from src.domain.value_objects import MinerType
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository, ProcessModelRepository
from src.presentation.api.routers.auth import User, require_auth
from src.domain.constants import HttpStatus, DisplayLimits, PaginationDefaults

router = APIRouter(prefix="/discovery")


class DiscoverRequest(BaseModel):
    log_id: str
    miner_type: str = "inductive"
    model_name: Optional[str] = None


class DiscoverResponse(BaseModel):
    model_id: str
    model_name: str
    miner_type: str
    model_format: str
    source_log_id: str


class MinerInfo(BaseModel):
    id: str
    name: str
    description: str
    output_format: str


# =============================================================================
# FLOW 2 RESPONSE MODELS - Detailed DFG, Petri Net, Process Tree
# =============================================================================


class DFGNodeResponse(BaseModel):
    """A node in the DFG (activity)."""

    name: str
    frequency: int
    is_start: bool = False
    is_end: bool = False


class DFGEdgeResponse(BaseModel):
    """An edge in the DFG (transition between activities)."""

    source: str
    target: str
    frequency: int
    probability: float
    avg_duration_seconds: Optional[float] = None


class DetailedDFGResponse(BaseModel):
    """Detailed Directly-Follows Graph response."""

    log_id: str
    nodes: List[DFGNodeResponse]
    edges: List[DFGEdgeResponse]
    start_activities: Dict[str, int]
    end_activities: Dict[str, int]
    total_cases: int
    total_events: int


class PetriNetPlaceResponse(BaseModel):
    """A place in a Petri net."""

    id: str
    name: str
    is_initial: bool = False
    is_final: bool = False


class PetriNetTransitionResponse(BaseModel):
    """A transition in a Petri net."""

    id: str
    label: Optional[str]
    is_silent: bool = False


class PetriNetArcResponse(BaseModel):
    """An arc in a Petri net."""

    source: str
    target: str
    source_type: str  # "place" or "transition"
    target_type: str  # "place" or "transition"


class PetriNetResponse(BaseModel):
    """Structured Petri Net response."""

    model_id: str
    model_name: str
    places: List[PetriNetPlaceResponse]
    transitions: List[PetriNetTransitionResponse]
    arcs: List[PetriNetArcResponse]
    initial_marking: Dict[str, int]
    final_marking: Dict[str, int]


class ProcessTreeNodeResponse(BaseModel):
    """A node in a process tree."""

    operator: Optional[str] = None  # ->, X, +, * or None for leaf
    label: Optional[str] = None  # Activity name for leaf nodes
    children: List["ProcessTreeNodeResponse"] = []


ProcessTreeNodeResponse.model_rebuild()


class ProcessTreeResponse(BaseModel):
    """Process Tree response."""

    model_id: str
    model_name: str
    root: ProcessTreeNodeResponse
    tree_string: str


class ModelQualityResponse(BaseModel):
    """Model quality metrics (the 4 quality dimensions)."""

    model_id: str
    log_id: str
    fitness: float
    precision: Optional[float]
    generalization: Optional[float]
    simplicity: Optional[float]
    overall_quality: float  # Weighted average


@router.get("/miners", response_model=List[MinerInfo])
async def list_miners():
    """
    List available mining algorithms.
    """
    miners = discovery_service.get_available_miners()
    return [MinerInfo(**m) for m in miners]


@router.post("/discover", response_model=DiscoverResponse)
async def discover_process(
    request: DiscoverRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Discover a process model from an event log.
    """
    # Get event log
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(UUID(request.log_id))

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    # Validate miner type
    try:
        miner_type = MinerType(request.miner_type)
    except ValueError:
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail=f"Invalid miner type. Valid options: {[m.value for m in MinerType]}",
        )

    try:
        # Discover model
        aggregate = discovery_service.discover_process_model(
            event_log=log,
            miner_type=miner_type,
            model_name=request.model_name,
        )

        # Save model
        model_repo = ProcessModelRepository(session)
        await model_repo.save(aggregate.model)

        return DiscoverResponse(
            model_id=str(aggregate.model.id),
            model_name=aggregate.model.name,
            miner_type=miner_type.value,
            model_format=aggregate.model.format.value,
            source_log_id=request.log_id,
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Discovery failed: {str(e)}")


@router.get("/dfg/{log_id}")
async def get_dfg(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get Directly-Follows Graph for an event log.
    Returns the graph as JSON.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(log_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    try:
        aggregate = discovery_service.discover_process_model(
            event_log=log,
            miner_type=MinerType.DFG,
        )

        dfg, start_activities, end_activities = aggregate.model.model_data

        # Convert to JSON serializable format
        edges = [
            {"source": edge[0], "target": edge[1], "frequency": freq} for edge, freq in dfg.items()
        ]

        return {
            "nodes": list(log.activities),
            "edges": edges,
            "start_activities": dict(start_activities),
            "end_activities": dict(end_activities),
        }
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"DFG generation failed: {str(e)}")


@router.get("/visualize/{model_id}")
async def visualize_model(
    model_id: UUID,
    format: str = "svg",
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get visualization of a process model.
    Returns SVG image.
    """
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)

    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        svg_bytes = discovery_service.visualize_model(model)

        return Response(
            content=svg_bytes,
            media_type="image/svg+xml",
            headers={"Content-Disposition": f"inline; filename=model_{model_id}.svg"},
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Visualization failed: {str(e)}")


# =============================================================================
# FLOW 2 ENHANCED ENDPOINTS - Detailed DFG, Petri Net, Process Tree, Quality
# =============================================================================


@router.get("/dfg/{log_id}/detailed", response_model=DetailedDFGResponse)
async def get_detailed_dfg(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get detailed Directly-Follows Graph with all edge data.
    Includes frequencies, probabilities, and duration statistics.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(log_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    try:
        aggregate = discovery_service.discover_process_model(
            event_log=log,
            miner_type=MinerType.DFG,
        )

        dfg, start_activities, end_activities = aggregate.model.model_data

        # Calculate activity frequencies
        activity_freq: Dict[str, int] = {}
        for case in log.cases:
            for event in case.events:
                act = str(event.activity)
                activity_freq[act] = activity_freq.get(act, 0) + 1

        # Build nodes
        start_acts = dict(start_activities)
        end_acts = dict(end_activities)
        nodes = [
            DFGNodeResponse(
                name=act,
                frequency=activity_freq.get(act, 0),
                is_start=act in start_acts,
                is_end=act in end_acts,
            )
            for act in log.activities
        ]

        # Build edges with probabilities
        # Calculate outgoing totals for probability
        outgoing_totals: Dict[str, int] = {}
        for (src, _), freq in dfg.items():
            outgoing_totals[src] = outgoing_totals.get(src, 0) + freq

        edges = [
            DFGEdgeResponse(
                source=edge[0],
                target=edge[1],
                frequency=freq,
                probability=round(freq / outgoing_totals.get(edge[0], 1), 3),
                avg_duration_seconds=None,  # Would require timing analysis
            )
            for edge, freq in dfg.items()
        ]

        return DetailedDFGResponse(
            log_id=str(log_id),
            nodes=nodes,
            edges=edges,
            start_activities=start_acts,
            end_activities=end_acts,
            total_cases=log.total_cases,
            total_events=log.total_events,
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Detailed DFG generation failed: {str(e)}")


@router.get("/petri-net/{model_id}", response_model=PetriNetResponse)
async def get_petri_net(
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get structured Petri Net representation of a process model.
    Includes places, transitions, arcs, and markings.
    """
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)

    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        # Get Petri net from model
        from pm4py.objects.petri_net.obj import PetriNet

        net, im, fm = discovery_service._get_petri_net(model)

        # Build places
        places = []
        for place in net.places:
            places.append(
                PetriNetPlaceResponse(
                    id=str(place.name),
                    name=str(place.name),
                    is_initial=place in im,
                    is_final=place in fm,
                )
            )

        # Build transitions
        transitions = []
        for trans in net.transitions:
            transitions.append(
                PetriNetTransitionResponse(
                    id=str(trans.name),
                    label=trans.label,
                    is_silent=trans.label is None,
                )
            )

        # Build arcs
        arcs = []
        for arc in net.arcs:
            source = arc.source
            target = arc.target

            if isinstance(source, PetriNet.Place):
                source_type = "place"
            else:
                source_type = "transition"

            if isinstance(target, PetriNet.Place):
                target_type = "place"
            else:
                target_type = "transition"

            arcs.append(
                PetriNetArcResponse(
                    source=str(source.name),
                    target=str(target.name),
                    source_type=source_type,
                    target_type=target_type,
                )
            )

        # Build markings
        initial_marking = {str(p.name): im[p] for p in im if im[p] > 0}
        final_marking = {str(p.name): fm[p] for p in fm if fm[p] > 0}

        return PetriNetResponse(
            model_id=str(model_id),
            model_name=model.name,
            places=places,
            transitions=transitions,
            arcs=arcs,
            initial_marking=initial_marking,
            final_marking=final_marking,
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Petri net extraction failed: {str(e)}")


@router.get("/process-tree/{model_id}", response_model=ProcessTreeResponse)
async def get_process_tree(
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get structured Process Tree representation of a process model.
    Shows hierarchical structure with operators and activities.
    """
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)

    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        from pm4py.objects.process_tree.obj import ProcessTree

        # If model is not a process tree, we need to convert or return error
        if model.model_data is None:
            raise HTTPException(status_code=HttpStatus.BAD_REQUEST, detail="Model data not available")

        def tree_to_response(node) -> ProcessTreeNodeResponse:
            """Recursively convert process tree to response model."""
            if hasattr(node, "operator") and node.operator is not None:
                # Internal node with operator
                op_str = str(node.operator).split(".")[-1] if node.operator else None
                children = [tree_to_response(child) for child in node.children]
                return ProcessTreeNodeResponse(
                    operator=op_str,
                    label=None,
                    children=children,
                )
            else:
                # Leaf node
                return ProcessTreeNodeResponse(
                    operator=None,
                    label=node.label if hasattr(node, "label") else str(node),
                    children=[],
                )

        # Try to get process tree
        tree_data = model.model_data
        if isinstance(tree_data, ProcessTree):
            root = tree_to_response(tree_data)
            tree_string = str(tree_data)
        else:
            # Return minimal response
            root = ProcessTreeNodeResponse(operator=None, label="Model", children=[])
            tree_string = "Unable to extract process tree"

        return ProcessTreeResponse(
            model_id=str(model_id),
            model_name=model.name,
            root=root,
            tree_string=tree_string,
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Process tree extraction failed: {str(e)}")


@router.get("/model/{model_id}/quality", response_model=ModelQualityResponse)
async def get_model_quality(
    model_id: UUID,
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get quality metrics for a process model.
    Calculates fitness, precision, generalization, and simplicity.
    """
    from src.application.core.conformance_service import conformance_service
    from src.application.core.pm4py_service import pm4py_service

    log_repo = EventLogRepository(session)
    model_repo = ProcessModelRepository(session)

    log = await log_repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        # Calculate fitness
        fitness = conformance_service.calculate_fitness(log, model)

        # Calculate precision
        try:
            precision = conformance_service.calculate_precision(log, model)
        except Exception:
            precision = None

        # Calculate generalization and simplicity
        generalization = None
        simplicity = None
        try:
            net, im, fm = discovery_service._get_petri_net(model)
            generalization = pm4py_service.evaluate_generalization(log, net, im, fm)
            simplicity = pm4py_service.evaluate_simplicity(net)
        except Exception:
            pass

        # Calculate overall quality (weighted average of available metrics)
        metrics = [fitness]
        if precision is not None:
            metrics.append(precision)
        if generalization is not None:
            metrics.append(generalization)
        if simplicity is not None:
            metrics.append(simplicity)

        overall_quality = sum(metrics) / len(metrics)

        return ModelQualityResponse(
            model_id=str(model_id),
            log_id=str(log_id),
            fitness=round(fitness, 4),
            precision=round(precision, 4) if precision else None,
            generalization=round(generalization, 4) if generalization else None,
            simplicity=round(simplicity, 4) if simplicity else None,
            overall_quality=round(overall_quality, 4),
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Quality evaluation failed: {str(e)}")
