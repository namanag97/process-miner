"""Workspaces Router.

Endpoints for managing workspaces within an organization.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from src.api.dependencies import DBSession
from src.platform.models import Project, Workspace
from src.models.schemas import (
    ProjectResponse,
    WorkspaceCreateRequest,
    WorkspaceDetailResponse,
    WorkspaceListResponse,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)

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
    db: DBSession,
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
    db: DBSession,
    workspace_id: str,
) -> WorkspaceDetailResponse:
    """
    Get a workspace by ID with its projects.
    """
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Get projects for this workspace
    projects_result = await db.execute(select(Project).filter(Project.workspace_id == workspace_id))
    projects = projects_result.scalars().all()

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
    db: DBSession,
    request: WorkspaceCreateRequest,
    org_id: str = Query(..., description="Organization ID for the workspace"),
) -> WorkspaceResponse:
    """
    Create a new workspace within an organization.
    """
    workspace = Workspace(
        org_id=org_id,
        name=request.name,
        description=request.description,
    )

    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)

    return _workspace_to_response(workspace)


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    db: DBSession,
    workspace_id: str,
    request: WorkspaceUpdateRequest,
) -> WorkspaceResponse:
    """
    Update a workspace.
    """
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if request.name is not None:
        workspace.name = request.name
    if request.description is not None:
        workspace.description = request.description

    workspace.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workspace)

    return _workspace_to_response(workspace)


@router.delete("/{workspace_id}", status_code=204)
async def delete_workspace(
    db: DBSession,
    workspace_id: str,
) -> None:
    """
    Delete a workspace and all its projects.

    BUG-036 FIX: Now deletes projects instead of orphaning them.
    """
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # BUG-036 FIX: Delete projects instead of orphaning
    from sqlalchemy import delete

    await db.execute(delete(Project).where(Project.workspace_id == workspace_id))

    await db.delete(workspace)
    await db.commit()


# =============================================================================
# Project Association
# =============================================================================


@router.post("/{workspace_id}/projects/{project_id}", response_model=WorkspaceDetailResponse)
async def add_project_to_workspace(
    db: DBSession,
    workspace_id: str,
    project_id: str,
) -> WorkspaceDetailResponse:
    """
    Add an existing project to a workspace.
    """
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    project_result = await db.execute(select(Project).filter(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.workspace_id = workspace_id
    workspace.updated_at = datetime.utcnow()

    await db.commit()

    return await get_workspace(db, workspace_id)


@router.delete("/{workspace_id}/projects/{project_id}", status_code=204)
async def remove_project_from_workspace(
    db: DBSession,
    workspace_id: str,
    project_id: str,
) -> None:
    """
    Remove a project from a workspace (doesn't delete the project).
    """
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    project_result = await db.execute(select(Project).filter(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.workspace_id != workspace_id:
        raise HTTPException(status_code=400, detail="Project is not in this workspace")

    project.workspace_id = None
    workspace.updated_at = datetime.utcnow()

    await db.commit()
