"""Workspaces Router.

Endpoints for managing workspaces within an organization.
"""

from datetime import datetime

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from src.api.dependencies import ReadDBSession
from src.infra.core.exceptions import (
    BadRequestError,
    NotFoundError,
    ProcessingError,
    ProjectNotFoundError,
)
from src.infra.core.logging_config import get_logger
from src.infra.devconsole import log_error, log_info
from src.infra.schemas import (
    ProjectResponse,
    WorkspaceCreateRequest,
    WorkspaceDetailResponse,
    WorkspaceListResponse,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)
from src.infra.users import Project, Workspace

logger = get_logger(__name__)
router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

# =============================================================================
# Helper Functions
# =============================================================================


def _workspace_to_response(workspace: Workspace) -> WorkspaceResponse:
    """Convert Workspace ORM to WorkspaceResponse."""
    return WorkspaceResponse(
        id=workspace.id,
        org_id=workspace.org_id,
        name=workspace.name,
        description=workspace.description,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )


def _project_to_response(project: Project) -> ProjectResponse:
    """Convert Project ORM to ProjectResponse using Pydantic model_validate."""
    return ProjectResponse.model_validate(project)


# =============================================================================
# CRUD Endpoints
# =============================================================================


@router.get("", response_model=WorkspaceListResponse)
async def list_workspaces(
    db: ReadDBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    org_id: str | None = Query(None, description="Filter by organization ID"),
) -> WorkspaceListResponse:
    """
    List all workspaces, optionally filtered by organization.
    """
    # Build base query
    query = select(Workspace)

    # Apply organization filter
    if org_id:
        query = query.filter(Workspace.org_id == org_id)

    # Get total count
    count_query = select(func.count()).select_from(Workspace)
    if org_id:
        count_query = count_query.filter(Workspace.org_id == org_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = (
        query.order_by(Workspace.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    result = await db.execute(query)
    workspaces = result.scalars().all()

    return WorkspaceListResponse(
        items=[_workspace_to_response(w) for w in workspaces],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )


@router.get("/{workspace_id}", response_model=WorkspaceDetailResponse)
async def get_workspace(
    db: ReadDBSession,
    workspace_id: str,
) -> WorkspaceDetailResponse:
    """
    Get a workspace by ID with its projects.
    """
    logger.info("fetching_workspace", workspace_id=workspace_id)

    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        logger.warning("workspace_not_found", workspace_id=workspace_id)
        log_error(
            "Workspace",
            "Workspace not found",
            error_code="WS_NOT_FOUND",
            workspace_id=workspace_id,
        )
        raise NotFoundError(resource='Workspace', resource_id=workspace_id)

    # Get projects for this workspace
    projects_result = await db.execute(select(Project).filter(Project.workspace_id == workspace_id))
    projects = projects_result.scalars().all()

    logger.info(
        "workspace_fetched",
        workspace_id=workspace_id,
        workspace_name=workspace.name,
        project_count=len(projects),
    )
    log_info(
        "Workspace",
        "Workspace fetched successfully",
        workspace_id=workspace_id,
        name=workspace.name,
        projects=len(projects),
    )

    return WorkspaceDetailResponse(
        id=workspace.id,
        org_id=workspace.org_id,
        name=workspace.name,
        description=workspace.description,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
        projects=[_project_to_response(p) for p in projects],
    )


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    db: ReadDBSession,
    request: WorkspaceCreateRequest,
    org_id: str = Query(..., description="Organization ID for the workspace"),
) -> WorkspaceResponse:
    """
    Create a new workspace within an organization.
    """
    logger.info("creating_workspace", org_id=org_id, name=request.name)

    workspace = Workspace(
        org_id=org_id,
        name=request.name,
        description=request.description,
    )

    try:
        db.add(workspace)
        await db.commit()
        await db.refresh(workspace)

        logger.info(
            "workspace_created",
            workspace_id=workspace.id,
            org_id=org_id,
            name=workspace.name,
        )
        log_info(
            "Workspace",
            "Workspace created successfully",
            workspace_id=workspace.id,
            name=workspace.name,
            org_id=org_id,
        )

        return _workspace_to_response(workspace)
    except Exception as e:
        logger.error("workspace_creation_failed", org_id=org_id, error=str(e), exc_info=True)
        log_error(
            "Workspace",
            "Failed to create workspace",
            error_code="WS_CREATE_FAILED",
            org_id=org_id,
            name=request.name,
            reason=str(e),
        )
        raise ProcessingError(message="Failed to create workspace")


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    db: ReadDBSession,
    workspace_id: str,
    request: WorkspaceUpdateRequest,
) -> WorkspaceResponse:
    """
    Update a workspace.
    """
    logger.info(
        "updating_workspace",
        workspace_id=workspace_id,
        updates=request.model_dump(exclude_unset=True),
    )

    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        logger.warning("workspace_not_found_for_update", workspace_id=workspace_id)
        log_error(
            "Workspace",
            "Cannot update - workspace not found",
            error_code="WS_NOT_FOUND",
            workspace_id=workspace_id,
        )
        raise NotFoundError(resource='Workspace', resource_id=workspace_id)

    if request.name is not None:
        workspace.name = request.name
    if request.description is not None:
        workspace.description = request.description

    workspace.updated_at = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(workspace)

        logger.info(
            "workspace_updated",
            workspace_id=workspace_id,
            name=workspace.name,
        )
        log_info(
            "Workspace",
            "Workspace updated successfully",
            workspace_id=workspace_id,
            name=workspace.name,
        )

        return _workspace_to_response(workspace)
    except Exception as e:
        logger.error(
            "workspace_update_failed", workspace_id=workspace_id, error=str(e), exc_info=True
        )
        log_error(
            "Workspace",
            "Failed to update workspace",
            error_code="WS_UPDATE_FAILED",
            workspace_id=workspace_id,
            reason=str(e),
        )
        raise ProcessingError(message="Failed to update workspace")


@router.delete("/{workspace_id}", status_code=204)
async def delete_workspace(
    db: ReadDBSession,
    workspace_id: str,
) -> None:
    """
    Delete a workspace and all its projects.

    BUG-036 FIX: Now deletes projects instead of orphaning them.
    """
    logger.info("deleting_workspace", workspace_id=workspace_id)

    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        logger.warning("workspace_not_found_for_deletion", workspace_id=workspace_id)
        log_error(
            "Workspace",
            "Cannot delete - workspace not found",
            error_code="WS_NOT_FOUND",
            workspace_id=workspace_id,
        )
        raise NotFoundError(resource='Workspace', resource_id=workspace_id)

    # BUG-036 FIX: Delete projects instead of orphaning
    from sqlalchemy import delete

    # Get project count for logging
    projects_result = await db.execute(
        select(func.count()).select_from(Project).where(Project.workspace_id == workspace_id)
    )
    project_count = projects_result.scalar() or 0

    try:
        await db.execute(delete(Project).where(Project.workspace_id == workspace_id))
        await db.delete(workspace)
        await db.commit()

        logger.info(
            "workspace_deleted",
            workspace_id=workspace_id,
            workspace_name=workspace.name,
            projects_deleted=project_count,
        )
        log_info(
            "Workspace",
            "Workspace and projects deleted successfully",
            workspace_id=workspace_id,
            name=workspace.name,
            projects_deleted=project_count,
        )
    except Exception as e:
        logger.error(
            "workspace_deletion_failed", workspace_id=workspace_id, error=str(e), exc_info=True
        )
        log_error(
            "Workspace",
            "Failed to delete workspace",
            error_code="WS_DELETE_FAILED",
            workspace_id=workspace_id,
            reason=str(e),
        )
        raise ProcessingError(message="Failed to delete workspace")


# =============================================================================
# Project Association
# =============================================================================


@router.post("/{workspace_id}/projects/{project_id}", response_model=WorkspaceDetailResponse)
async def add_project_to_workspace(
    db: ReadDBSession,
    workspace_id: str,
    project_id: str,
) -> WorkspaceDetailResponse:
    """
    Add an existing project to a workspace.
    """
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise NotFoundError(resource='Workspace', resource_id='unknown')

    project_result = await db.execute(select(Project).filter(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise ProjectNotFoundError(project_id='unknown')

    project.workspace_id = workspace_id
    workspace.updated_at = datetime.utcnow()

    await db.commit()

    return await get_workspace(db, workspace_id)


@router.delete("/{workspace_id}/projects/{project_id}", status_code=204)
async def remove_project_from_workspace(
    db: ReadDBSession,
    workspace_id: str,
    project_id: str,
) -> None:
    """
    Remove a project from a workspace (doesn't delete the project).
    """
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise NotFoundError(resource='Workspace', resource_id='unknown')

    project_result = await db.execute(select(Project).filter(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise ProjectNotFoundError(project_id='unknown')

    if project.workspace_id != workspace_id:
        raise BadRequestError(message="Project is not in this workspace")

    project.workspace_id = None
    workspace.updated_at = datetime.utcnow()

    await db.commit()
