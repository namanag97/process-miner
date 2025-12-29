"""Processes Discovery Sub-Router.

Provides discovery endpoints nested under /processes/{process_id}/discovery.
This sub-router is included by the main processes router.
"""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.core.discovery_service import discovery_service
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import (
    EventLogRepository,
    ProcessModelRepository,
)
from src.presentation.api.routers.auth import User, require_auth
from src.domain.constants import HttpStatus, DisplayLimits, PaginationDefaults

# =============================================================================
# SUB-ROUTER DEFINITION
# =============================================================================
router = APIRouter()


# =============================================================================
# RESPONSE MODELS
# =============================================================================


class DiscoverRequest(BaseModel):
    """Request to discover a process model."""

    miner_type: str = "inductive"
    model_name: Optional[str] = None


class DiscoverResponse(BaseModel):
    """Response from process discovery."""

    model_id: str
    model_name: str
    miner_type: str
    model_format: str
    source_log_id: str
    _links: Dict[str, Dict[str, str]] = {}


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

    process_id: str
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
    source_type: str
    target_type: str


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

    operator: Optional[str] = None
    label: Optional[str] = None
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
    process_id: str
    fitness: float
    precision: Optional[float]
    generalization: Optional[float]
    simplicity: Optional[float]
    overall_quality: float


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post(
    "",
    response_model=DiscoverResponse,
    summary="Discover Process Model",
    description="""
    Discover a process model from the event log.

    **Miner Types:**
    - inductive: Inductive Miner (balanced fitness/precision)
    - alpha: Alpha Miner (classic algorithm)
    - alpha_plus: Alpha+ Miner (handles loops)
    - heuristic: Heuristic Miner (handles noise)
    """,
)
async def discover_process_model(
    process_id: UUID,
    request: DiscoverRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Discover a process model from the event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")

    try:
        net, im, fm = discovery_service.discover_model(log, request.miner_type)

        # Create a model and save
        model_repo = ProcessModelRepository(session)
        model = await model_repo.create(
            {
                "name": request.model_name or f"{log.name} - {request.miner_type.title()} Model",
                "miner_type": request.miner_type,
                "model_format": "petri_net",
                "source_log_id": str(process_id),
            }
        )
        await session.commit()

        return DiscoverResponse(
            model_id=str(model.id),
            model_name=model.name,
            miner_type=request.miner_type,
            model_format="petri_net",
            source_log_id=str(process_id),
            _links={
                "self": {"href": f"/api/v1/models/{model.id}"},
                "visualize": {"href": f"/api/v1/models/{model.id}/visualize"},
                "petri_net": {
                    "href": f"/api/v1/processes/{process_id}/discovery/petri-net/{model.id}"
                },
                "quality": {"href": f"/api/v1/processes/{process_id}/discovery/quality/{model.id}"},
            },
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Discovery failed: {str(e)}")


@router.get(
    "/dfg",
    response_model=DetailedDFGResponse,
    summary="Get Directly-Follows Graph",
    description="""
    Get the DFG (Directly-Follows Graph) for the process.

    The DFG shows activities as nodes and transitions as edges,
    with frequency and probability information.
    """,
)
async def get_dfg(
    process_id: UUID,
    min_frequency: int = Query(1, ge=1, description="Minimum edge frequency to include"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get Directly-Follows Graph for the process.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")

    try:
        dfg_data = discovery_service.get_dfg(log)

        # Filter edges by min_frequency
        edges = [
            DFGEdgeResponse(**edge)
            for edge in dfg_data.get("edges", [])
            if edge.get("frequency", 0) >= min_frequency
        ]

        # Get unique activities from filtered edges
        activity_set = set()
        for edge in dfg_data.get("edges", []):
            if edge.get("frequency", 0) >= min_frequency:
                activity_set.add(edge["source"])
                activity_set.add(edge["target"])

        nodes = [
            DFGNodeResponse(
                name=node["name"],
                frequency=node.get("frequency", 0),
                is_start=node.get("is_start", False),
                is_end=node.get("is_end", False),
            )
            for node in dfg_data.get("nodes", [])
            if node["name"] in activity_set or not activity_set
        ]

        return DetailedDFGResponse(
            process_id=str(process_id),
            nodes=nodes,
            edges=edges,
            start_activities=dfg_data.get("start_activities", {}),
            end_activities=dfg_data.get("end_activities", {}),
            total_cases=dfg_data.get("total_cases", 0),
            total_events=dfg_data.get("total_events", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"DFG generation failed: {str(e)}")


@router.get(
    "/dfg/visualize",
    summary="Get DFG Visualization",
    description="Get an SVG visualization of the DFG.",
    responses={200: {"content": {"image/svg+xml": {}}}},
)
async def get_dfg_visualization(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get SVG visualization of the DFG.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")

    try:
        svg_data = discovery_service.visualize_dfg(log)
        return Response(content=svg_data, media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Visualization failed: {str(e)}")


@router.get(
    "/petri-net/{model_id}",
    response_model=PetriNetResponse,
    summary="Get Petri Net Representation",
    description="""
    Get structured Petri Net representation of a process model.

    Includes places, transitions, arcs, and markings.
    """,
)
async def get_petri_net(
    process_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get structured Petri Net representation.
    """
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)

    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Model not found")

    if str(model.source_log_id) != str(process_id):
        raise HTTPException(status_code=HttpStatus.BAD_REQUEST, detail="Model does not belong to this process")

    try:
        petri_data = discovery_service.get_petri_net_structure(model)
        return PetriNetResponse(
            model_id=str(model_id),
            model_name=model.name,
            places=[PetriNetPlaceResponse(**p) for p in petri_data.get("places", [])],
            transitions=[
                PetriNetTransitionResponse(**t) for t in petri_data.get("transitions", [])
            ],
            arcs=[PetriNetArcResponse(**a) for a in petri_data.get("arcs", [])],
            initial_marking=petri_data.get("initial_marking", {}),
            final_marking=petri_data.get("final_marking", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Petri net extraction failed: {str(e)}")


@router.get(
    "/process-tree/{model_id}",
    response_model=ProcessTreeResponse,
    summary="Get Process Tree Representation",
    description="""
    Get Process Tree representation of a model.

    Only available for models discovered with the Inductive Miner.
    """,
)
async def get_process_tree(
    process_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get Process Tree representation.
    """
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)

    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Model not found")

    if str(model.source_log_id) != str(process_id):
        raise HTTPException(status_code=HttpStatus.BAD_REQUEST, detail="Model does not belong to this process")

    try:
        tree_data = discovery_service.get_process_tree_structure(model)
        return ProcessTreeResponse(
            model_id=str(model_id),
            model_name=model.name,
            root=ProcessTreeNodeResponse(**tree_data.get("root", {})),
            tree_string=tree_data.get("tree_string", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Process tree extraction failed: {str(e)}")


@router.get(
    "/quality/{model_id}",
    response_model=ModelQualityResponse,
    summary="Get Model Quality Metrics",
    description="""
    Get quality metrics for a process model against the event log.

    **Quality Dimensions:**
    - **Fitness**: How much of the log behavior can the model replay
    - **Precision**: How much extra behavior does the model allow
    - **Generalization**: How well does the model generalize beyond the log
    - **Simplicity**: Structural simplicity of the model
    """,
)
async def get_model_quality(
    process_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get model quality metrics.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(process_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")

    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)

    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Model not found")

    if str(model.source_log_id) != str(process_id):
        raise HTTPException(status_code=HttpStatus.BAD_REQUEST, detail="Model does not belong to this process")

    try:
        quality = discovery_service.calculate_quality_metrics(log, model)
        return ModelQualityResponse(
            model_id=str(model_id),
            process_id=str(process_id),
            fitness=quality.get("fitness", 0.0),
            precision=quality.get("precision"),
            generalization=quality.get("generalization"),
            simplicity=quality.get("simplicity"),
            overall_quality=quality.get("overall_quality", 0.0),
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Quality calculation failed: {str(e)}")
