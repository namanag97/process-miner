"""DAG API Router.

Endpoints for managing DAG workflow definitions and runs.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.api.dependencies import CurrentUser, ReadDBSession
from src.infra.core.logging_config import get_logger
from src.infra.dag.service import DAGService
from src.infra.dag.templates import get_template, list_templates
from src.shared.base_schemas import BaseSchema, BaseTaskResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/dags", tags=["DAGs"])


# =============================================================================
# Pydantic Schemas
# =============================================================================


class StepConfig(BaseModel):
    """Step configuration for DAG definition."""

    name: str = Field(..., description="Unique step name within the DAG")
    task_name: str = Field(..., description="Registered task function name")
    default_params: dict[str, Any] = Field(
        default_factory=dict, description="Default parameters for the task"
    )
    retry_policy: dict[str, Any] | None = Field(
        None, description="Retry configuration (max_retries, backoff)"
    )
    timeout_seconds: int = Field(3600, description="Task timeout in seconds")


class EdgeConfig(BaseModel):
    """Edge configuration for DAG definition."""

    from_step: str = Field(..., description="Source step name")
    to_step: str = Field(..., description="Target step name")
    condition: dict[str, Any] | None = Field(
        None, description="Optional condition for edge execution"
    )


class CreateDefinitionRequest(BaseModel):
    """Request to create a DAG definition."""

    name: str = Field(..., description="Human-readable DAG name")
    description: str | None = Field(None, description="Optional description")
    steps: list[StepConfig] = Field(..., min_length=1, description="List of steps")
    edges: list[EdgeConfig] = Field(default_factory=list, description="Dependencies between steps")


class TriggerRunRequest(BaseModel):
    """Request to trigger a DAG run."""

    definition_id: str | None = Field(None, description="DAG definition ID")
    definition_name: str | None = Field(None, description="DAG definition name (alternative to ID)")
    context: dict[str, Any] = Field(
        default_factory=dict, description="Shared context for all steps"
    )
    step_params: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Per-step parameter overrides"
    )


class StepResponse(BaseModel):
    """DAG step in a definition."""

    id: str
    name: str
    task_name: str
    default_params: dict[str, Any] | None = None
    position: int


class EdgeResponse(BaseModel):
    """DAG edge in a definition."""

    id: str
    from_step_id: str
    to_step_id: str


class DefinitionResponse(BaseSchema):
    """DAG definition response.

    Uses BaseSchema for ORM compatibility. Note: Does not extend
    BaseEntityResponse since we only need created_at, not updated_at.
    """

    id: str
    name: str
    description: str | None = None
    version: int
    is_active: bool
    steps: list[StepResponse]
    edges: list[EdgeResponse]
    created_at: datetime


class DefinitionListResponse(BaseModel):
    """Paginated list of definitions."""

    items: list[DefinitionResponse]
    total: int


class RunStepResponse(BaseSchema):
    """Step status within a run.

    Similar to BaseTaskResponse but without created_at/updated_at since
    step timing is tracked via started_at/completed_at relative to the run.
    """

    id: str
    name: str
    task_name: str
    status: str = Field(..., description="Step status (pending/running/completed/failed)")
    started_at: datetime | None = Field(None, description="Step start time")
    completed_at: datetime | None = Field(None, description="Step completion time")
    error_message: str | None = Field(None, description="Error details if failed")


class RunResponse(BaseTaskResponse):
    """DAG run response.

    Extends BaseTaskResponse which provides:
    - id, created_at, updated_at (from BaseEntityResponse)
    - status, started_at, completed_at, error_message (from BaseTaskResponse)
    """

    definition_id: str = Field(..., description="ID of the DAG definition")
    trigger_type: str | None = Field(None, description="How the run was triggered")
    steps: list[RunStepResponse] = Field(default_factory=list, description="Step statuses")


class RunListResponse(BaseModel):
    """Paginated list of runs."""

    items: list[RunResponse]
    total: int
    page: int
    page_size: int


class TemplateInfo(BaseModel):
    """Predefined template info."""

    name: str
    display_name: str
    description: str
    step_count: int
    edge_count: int


# =============================================================================
# Template Endpoints
# =============================================================================


@router.get("/templates", response_model=list[TemplateInfo])
async def get_templates():
    """List predefined DAG templates.

    Returns all available workflow templates that can be used
    to trigger DAG runs without creating custom definitions.
    """
    templates = []
    for name in list_templates():
        template = get_template(name)
        if template:
            templates.append(
                TemplateInfo(
                    name=name,
                    display_name=template.get("name", name),
                    description=template.get("description", ""),
                    step_count=len(template.get("steps", [])),
                    edge_count=len(template.get("edges", [])),
                )
            )
    return templates


# =============================================================================
# Definition Endpoints
# =============================================================================


@router.post("/definitions", status_code=201)
async def create_definition(
    db: ReadDBSession,
    user: CurrentUser,
    request: CreateDefinitionRequest,
):
    """Create a new DAG definition.

    Validates the DAG structure (no cycles, valid edges) and
    stores it for later execution.
    """
    service = DAGService(db)

    try:
        dag_def = await service.create_definition(
            name=request.name,
            steps=[s.model_dump() for s in request.steps],
            edges=[e.model_dump() for e in request.edges],
            description=request.description,
        )
        await db.commit()

        logger.info(
            "dag_definition_created_via_api",
            definition_id=dag_def.id,
            name=dag_def.name,
            user_id=user.id,
        )

        return _definition_to_response(dag_def)

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"detail": str(e), "error_code": "INVALID_DAG"},
        )


@router.get("/definitions", response_model=DefinitionListResponse)
async def list_definitions(
    db: ReadDBSession,
    active_only: bool = Query(True, description="Only return active definitions"),
):
    """List all DAG definitions.

    Returns all stored DAG definitions, optionally filtered to
    only active (non-archived) ones.
    """
    service = DAGService(db)
    definitions = await service.list_definitions(active_only=active_only)

    items = [_definition_to_response(d) for d in definitions]
    return DefinitionListResponse(items=items, total=len(items))


@router.get("/definitions/{definition_id}", response_model=DefinitionResponse)
async def get_definition(
    db: ReadDBSession,
    definition_id: str,
):
    """Get a DAG definition by ID.

    Returns the full definition including all steps and edges.
    """
    service = DAGService(db)
    dag_def = await service.get_definition(definition_id)

    if not dag_def:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Definition not found: {definition_id}"},
        )

    return _definition_to_response(dag_def)


# =============================================================================
# Run Endpoints
# =============================================================================


@router.post("/runs", status_code=202)
async def trigger_run(
    db: ReadDBSession,
    user: CurrentUser,
    request: TriggerRunRequest,
):
    """Trigger a new DAG run.

    Starts execution of a DAG definition. The run will execute
    asynchronously with steps processed by Celery workers.

    Provide either definition_id or definition_name.
    """
    service = DAGService(db)

    try:
        # Resolve definition
        if request.definition_name:
            # Check if it's a predefined template
            template = get_template(request.definition_name)
            if template:
                # Create temporary definition from template
                dag_def = await service.create_definition(
                    name=f"_template_{request.definition_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    steps=template.get("steps", []),
                    edges=template.get("edges", []),
                    description=f"Auto-created from template: {request.definition_name}",
                )
                await db.flush()
                definition_id = dag_def.id
            else:
                # Look up existing definition by name
                dag_def = await service.get_definition_by_name(request.definition_name)
                if not dag_def:
                    return JSONResponse(
                        status_code=404,
                        content={"detail": f"Definition not found: {request.definition_name}"},
                    )
                definition_id = dag_def.id
        elif request.definition_id:
            definition_id = request.definition_id
        else:
            return JSONResponse(
                status_code=400,
                content={"detail": "Either definition_id or definition_name is required"},
            )

        dag_run = await service.trigger_run(
            definition_id=definition_id,
            user_id=user.id,
            context=request.context,
            step_params=request.step_params,
        )
        await db.commit()

        logger.info(
            "dag_run_triggered_via_api",
            run_id=dag_run.id,
            definition_id=definition_id,
            user_id=user.id,
        )

        return _run_to_response(dag_run)

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"detail": str(e)},
        )


@router.get("/runs", response_model=RunListResponse)
async def list_runs(
    db: ReadDBSession,
    user: CurrentUser,
    status: str | None = Query(None, description="Filter by status"),
    definition_id: str | None = Query(None, description="Filter by definition"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List DAG runs.

    Returns runs for the current user with optional filtering
    by status and definition.
    """
    service = DAGService(db)
    offset = (page - 1) * page_size

    runs = await service.list_runs(
        user_id=user.id,
        status=status,
        definition_id=definition_id,
        limit=page_size,
        offset=offset,
    )

    items = [_run_to_response(r) for r in runs]
    return RunListResponse(
        items=items,
        total=len(items),  # TODO: proper count query
        page=page,
        page_size=page_size,
    )


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(
    db: ReadDBSession,
    run_id: str,
):
    """Get DAG run status.

    Returns the current status of a run including all step
    statuses and timing information.
    """
    service = DAGService(db)
    dag_run = await service.get_run(run_id)

    if not dag_run:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Run not found: {run_id}"},
        )

    return _run_to_response(dag_run)


@router.post("/runs/{run_id}/cancel")
async def cancel_run(
    db: ReadDBSession,
    user: CurrentUser,
    run_id: str,
):
    """Cancel a DAG run.

    Stops execution and marks all pending steps as cancelled.
    Already completed steps are not affected.
    """
    service = DAGService(db)
    dag_run = await service.get_run(run_id)

    if not dag_run:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Run not found: {run_id}"},
        )

    success = await service.cancel_run(run_id)
    await db.commit()

    if success:
        logger.info("dag_run_cancelled_via_api", run_id=run_id, user_id=user.id)
        return {"status": "cancelled", "run_id": run_id}
    return JSONResponse(
        status_code=400,
        content={"detail": "Failed to cancel run"},
    )


# =============================================================================
# Helpers
# =============================================================================


def _definition_to_response(dag_def) -> DefinitionResponse:
    """Convert DAGDefinition to response schema."""
    import json

    steps = []
    for step in dag_def.steps:
        default_params = None
        if step.default_params_json:
            try:
                default_params = json.loads(step.default_params_json)
            except (json.JSONDecodeError, TypeError):
                default_params = {}

        steps.append(
            StepResponse(
                id=step.id,
                name=step.name,
                task_name=step.task_name,
                default_params=default_params,
                position=step.position,
            )
        )

    edges = [
        EdgeResponse(
            id=edge.id,
            from_step_id=edge.from_step_id,
            to_step_id=edge.to_step_id,
        )
        for edge in dag_def.edges
    ]

    return DefinitionResponse(
        id=dag_def.id,
        name=dag_def.name,
        description=dag_def.description,
        version=dag_def.version,
        is_active=dag_def.is_active,
        steps=steps,
        edges=edges,
        created_at=dag_def.created_at,
    )


def _run_to_response(dag_run) -> RunResponse:
    """Convert DAGRun to response schema."""
    steps = [
        RunStepResponse(
            id=step.id,
            name=step.step_name,
            task_name=step.task_name,
            status=step.status,
            started_at=step.started_at,
            completed_at=step.completed_at,
            error_message=step.error_message,
        )
        for step in dag_run.steps
    ]

    return RunResponse(
        id=dag_run.id,
        definition_id=dag_run.dag_definition_id,
        status=dag_run.status,
        trigger_type=dag_run.trigger_type,
        created_at=dag_run.created_at,
        updated_at=None,  # DAGRun doesn't track updates
        started_at=dag_run.started_at,
        completed_at=dag_run.completed_at,
        error_message=dag_run.error_message,
        steps=steps,
    )
