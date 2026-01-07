"""Workflows Router.

Legacy workflow API - redirects to DAG system.

## Migration Notice
Workflows have been superceded by DAGs (Directed Acyclic Graphs).
Use `/api/v1/dags/*` endpoints for new workflow orchestration.

This router is maintained for backward compatibility.
"""

from fastapi import APIRouter, HTTPException

from src.features.process_mining.schemas.workflows import (
    WorkflowCreateRequest,
    WorkflowResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowTemplate,
)
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


# =============================================================================
# Template Endpoints
# =============================================================================


@router.get("/templates", response_model=list[WorkflowTemplate])
async def list_templates() -> list[WorkflowTemplate]:
    """List predefined workflow templates.

    Note: Consider using DAG templates via GET /api/v1/dags/templates instead.
    """
    # Return basic templates that map to DAG templates
    return [
        WorkflowTemplate(
            id="ingest-discover",
            name="Ingest & Discover",
            description="Upload dataset, ingest, and run process discovery",
            steps=[],
        ),
        WorkflowTemplate(
            id="full-analysis",
            name="Full Analysis Pipeline",
            description="Ingest → Discover → Conformance → Analytics",
            steps=[],
        ),
        WorkflowTemplate(
            id="conformance-check",
            name="Conformance Check",
            description="Run conformance checking against a model",
            steps=[],
        ),
    ]


# =============================================================================
# Workflow CRUD
# =============================================================================


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows() -> list[WorkflowResponse]:
    """List all workflows.

    Note: Workflows have been migrated to DAGs. Use GET /api/v1/dags instead.
    """
    logger.warning("legacy_workflow_list_called", msg="Use /api/v1/dags instead")
    return []


@router.post("", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowCreateRequest,
) -> WorkflowResponse:
    """Create a new workflow.

    Note: Consider using POST /api/v1/dags instead for new workflows.
    """
    raise HTTPException(
        status_code=501,
        detail="Workflows have been migrated to DAGs. Use POST /api/v1/dags instead.",
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str) -> WorkflowResponse:
    """Get workflow by ID.

    Note: Use GET /api/v1/dags/{id} instead.
    """
    raise HTTPException(
        status_code=501,
        detail="Workflows have been migrated to DAGs. Use GET /api/v1/dags/{id} instead.",
    )


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str) -> dict:
    """Delete a workflow.

    Note: Use DELETE /api/v1/dags/{id} instead.
    """
    raise HTTPException(
        status_code=501,
        detail="Workflows have been migrated to DAGs. Use DELETE /api/v1/dags/{id} instead.",
    )


# =============================================================================
# Workflow Execution
# =============================================================================


@router.post("/{workflow_id}/run", response_model=WorkflowRunResponse)
async def run_workflow(
    workflow_id: str,
    request: WorkflowRunRequest,
) -> WorkflowRunResponse:
    """Execute a workflow.

    Note: Use POST /api/v1/dags/{id}/trigger instead.
    """
    raise HTTPException(
        status_code=501,
        detail="Workflows have been migrated to DAGs. Use POST /api/v1/dags/trigger instead.",
    )


@router.get("/{workflow_id}/runs", response_model=list[WorkflowRunResponse])
async def list_workflow_runs(workflow_id: str) -> list[WorkflowRunResponse]:
    """List runs for a workflow.

    Note: Use GET /api/v1/dags/runs instead.
    """
    logger.warning("legacy_workflow_runs_called", msg="Use /api/v1/dags/runs instead")
    return []


@router.get("/runs/{run_id}", response_model=WorkflowRunResponse)
async def get_workflow_run(run_id: str) -> WorkflowRunResponse:
    """Get a specific workflow run.

    Note: Use GET /api/v1/dags/runs/{id} instead.
    """
    raise HTTPException(
        status_code=501,
        detail="Workflows have been migrated to DAGs. Use GET /api/v1/dags/runs/{id} instead.",
    )
