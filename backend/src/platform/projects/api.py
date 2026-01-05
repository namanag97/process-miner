"""Projects Router.

Endpoints for managing projects (folders for organizing datasets).
"""

import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import Dataset
from src.features.process_mining.schemas import (
    DatasetResponse,
)
from src.platform.models import Project, Workspace, WorkspaceMember
from src.platform.schemas import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)

router = APIRouter(prefix="/projects", tags=["Projects"])

# =============================================================================
# Helper Functions
# =============================================================================


def _project_to_response(project: Project) -> ProjectResponse:
    """Convert Project ORM to ProjectResponse using Pydantic model_validate."""
    return ProjectResponse.model_validate(project)


def _dataset_to_response(dataset: Dataset) -> DatasetResponse:
    """Convert Dataset ORM to DatasetResponse using Pydantic model_validate."""
    return DatasetResponse.model_validate(dataset)


# =============================================================================
# CRUD Endpoints
# =============================================================================


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    db: DBSession,
    request: ProjectCreateRequest,
    user: CurrentUser,
    workspace_id: str | None = Query(None, description="Workspace ID to associate project with"),
) -> ProjectResponse:
    """
    Create a new project, optionally within a workspace.

    Requires PROJECT_CREATE permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import AuthorizationService

    # Workspace_id is required for RBAC
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    # Verify user has PROJECT_CREATE permission in workspace
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.PROJECT_CREATE)

    project = Project(
        workspace_id=workspace_id,
        name=request.name,
        description=request.description,
        tags_json=json.dumps(request.tags) if request.tags else None,
        total_files=0,
        total_analyses=0,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    return _project_to_response(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Search by project name"),
    workspace_id: str | None = Query(None, description="Filter by workspace ID"),
) -> ProjectListResponse:
    """
    List all projects with pagination, optionally filtered by workspace.

    Requires PROJECT_READ permission.
    Automatically filtered by workspace membership (RLS).
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import AuthorizationService

    # Build query with RLS filtering (user's workspaces only)
    query = (
        select(Project)
        .join(Workspace, Project.workspace_id == Workspace.id)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user.id)
    )

    # Apply workspace filter (verify access if specified)
    if workspace_id:
        auth_service = AuthorizationService(db)
        await auth_service.verify_workspace_access(workspace_id, user, Permission.PROJECT_READ)
        query = query.filter(Project.workspace_id == workspace_id)

    # Apply search filter (case-insensitive for all databases)
    if search:
        query = query.filter(func.lower(Project.name).contains(search.lower()))

    # Get total count with RLS
    count_query = (
        select(func.count())
        .select_from(Project)
        .join(Workspace, Project.workspace_id == Workspace.id)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user.id)
    )
    if workspace_id:
        count_query = count_query.filter(Project.workspace_id == workspace_id)
    if search:
        count_query = count_query.filter(func.lower(Project.name).contains(search.lower()))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = (
        query.order_by(Project.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    result = await db.execute(query)
    projects = result.scalars().all()

    return ProjectListResponse(
        items=[_project_to_response(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, (total + page_size - 1) // page_size) if total > 0 else 0,
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    db: DBSession,
    project_id: str,
    user: CurrentUser,
) -> ProjectDetailResponse:
    """
    Get a project by ID with its datasets.

    Requires PROJECT_READ permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_project_permission

    # Check permission (also validates project exists)
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_READ)

    # Get datasets for this project
    datasets_result = await db.execute(select(Dataset).filter(Dataset.project_id == project_id))
    datasets = datasets_result.scalars().all()

    # Use model_validate to handle tags_json parsing
    base_response = ProjectResponse.model_validate(project)

    return ProjectDetailResponse(
        id=base_response.id,
        name=base_response.name,
        description=base_response.description,
        tags=base_response.tags,
        total_files=len(datasets),
        total_analyses=base_response.total_analyses,
        created_at=base_response.created_at,
        updated_at=base_response.updated_at,
        datasets=[_dataset_to_response(ds) for ds in datasets],
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    db: DBSession,
    project_id: str,
    request: ProjectUpdateRequest,
    user: CurrentUser,
) -> ProjectResponse:
    """
    Update a project.

    Requires PROJECT_UPDATE permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_project_permission

    # Check permission (also validates project exists)
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_UPDATE)

    if request.name is not None:
        project.name = request.name
    if request.description is not None:
        project.description = request.description
    if request.tags is not None:
        project.tags_json = json.dumps(request.tags)

    project.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(project)

    return _project_to_response(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    db: DBSession,
    project_id: str,
    user: CurrentUser,
) -> None:
    """
    Delete a project.

    Note: Event logs in this project will have their project_id set to NULL
    (they won't be deleted).

    Requires PROJECT_DELETE permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_project_permission

    # Check permission (also validates project exists)
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_DELETE)

    # Unlink datasets (they remain, just not in a project)
    from sqlalchemy import update

    await db.execute(
        update(Dataset).where(Dataset.project_id == project_id).values(project_id=None)
    )

    await db.delete(project)
    await db.commit()


# =============================================================================
# File Management
# =============================================================================


@router.post("/{project_id}/files/{dataset_id}", response_model=ProjectDetailResponse)
async def add_file_to_project(
    db: DBSession,
    project_id: str,
    dataset_id: str,
    user: CurrentUser,
) -> ProjectDetailResponse:
    """
    Add an existing dataset to a project.

    Requires PROJECT_UPDATE permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission, require_project_permission

    # Check permission on project (also validates project exists)
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_UPDATE)

    # Check permission on dataset (user must have access to move it)
    # Helper already fetches the dataset, so we reuse it
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_UPDATE)

    dataset.project_id = project_id

    # Update total_files count
    count_result = await db.execute(
        select(func.count(Dataset.id)).filter(Dataset.project_id == project_id)
    )
    project.total_files = count_result.scalar() or 0
    project.updated_at = datetime.utcnow()

    await db.commit()

    return await get_project(db, project_id, user)


@router.delete("/{project_id}/files/{dataset_id}", status_code=204)
async def remove_file_from_project(
    db: DBSession,
    project_id: str,
    dataset_id: str,
    user: CurrentUser,
) -> None:
    """
    Remove a dataset from a project (doesn't delete the dataset).

    Requires PROJECT_UPDATE permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission, require_project_permission

    # Check permission on project (also validates project exists)
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_UPDATE)

    # Check permission on dataset (user must have access to modify it)
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_UPDATE)

    if dataset.project_id != project_id:
        raise HTTPException(status_code=400, detail="Dataset is not in this project")

    dataset.project_id = None

    # Update total_files count
    count_result = await db.execute(
        select(func.count(Dataset.id)).filter(Dataset.project_id == project_id)
    )
    project.total_files = count_result.scalar() or 0
    project.updated_at = datetime.utcnow()

    await db.commit()
