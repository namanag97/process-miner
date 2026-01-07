"""Projects Router.

Endpoints for managing projects (folders for organizing datasets/event logs).

## Business Context
Projects are organizational containers for process mining analyses:
- Each project belongs to a workspace and can contain multiple datasets (event logs)
- Datasets are uploaded to projects, then mapped and ingested for analysis
- Process discovery, conformance checking, and analytics are performed on datasets

## Testing Instructions

### Prerequisites
1. Create a workspace: `POST /api/v1/workspaces?org_id={org_id}`
2. Have the workspace_id ready for project creation

### Test Flow
1. **Create Project**: `POST /api/v1/projects?workspace_id={workspace_id}`
   ```json
   {"name": "Order Process Analysis", "description": "P2P process mining"}
   ```
2. **List Projects**: `GET /api/v1/projects` or `GET /api/v1/projects?workspace_id={id}`
3. **Get Project**: `GET /api/v1/projects/{project_id}` → Returns project with datasets
4. **Update Project**: `PUT /api/v1/projects/{project_id}`
5. **Add Dataset**: `POST /api/v1/projects/{project_id}/files/{dataset_id}`
6. **Archive/Restore**: `POST /api/v1/projects/{project_id}/archive` or `/restore`
7. **Delete Project**: `DELETE /api/v1/projects/{project_id}`

### Common Errors
- **401**: Missing or invalid JWT token
- **403**: User doesn't have permission (not a workspace member)
- **404**: Project or Workspace not found
- **409**: Conflict (dataset already in project, project already archived)
- **422**: Invalid UUID format
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Path, Query
from sqlalchemy import func, select, update

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import Dataset
from src.features.process_mining.schemas import DatasetResponse
from src.platform.core.exceptions import ConflictError
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.core.validation import (
    calculate_total_pages,
    sanitize_search_query,
    validate_uuid,
)
from src.platform.models import Project, Workspace, WorkspaceMember
from src.platform.schemas import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)
from src.platform.workspaces.authorization import AuthorizationService

logger = get_logger(__name__)

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
    workspace_id: str = Query(..., description="Workspace ID to associate project with (required)"),
) -> ProjectResponse:
    """
    Create a new project within a workspace.

    Projects are containers for organizing event logs (datasets) and their
    process mining analyses. All projects must belong to a workspace.

    Requires PROJECT_CREATE permission in the workspace.
    """
    # Validate workspace_id format
    validate_uuid(workspace_id, "workspace_id")

    # Verify user has PROJECT_CREATE permission in workspace
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.PROJECT_CREATE)

    # Create project
    project = Project(
        workspace_id=workspace_id,
        name=request.name,
        description=request.description,
        tags_json=json.dumps(request.tags) if request.tags else None,
        total_files=0,
        total_analyses=0,
        created_at=datetime.now(timezone.utc),
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    logger.info(
        "project_created", project_id=project.id, workspace_id=workspace_id, user_id=user.id
    )

    return _project_to_response(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    search: str | None = Query(None, max_length=255, description="Search by project name"),
    workspace_id: str | None = Query(None, description="Filter by workspace ID"),
) -> ProjectListResponse:
    """
    List projects accessible to the current user.

    Projects are automatically filtered by workspace membership (row-level security).
    Optionally filter by workspace or search by project name.

    Requires PROJECT_READ permission.
    """
    # Validate and sanitize inputs
    if workspace_id:
        validate_uuid(workspace_id, "workspace_id")
        # Verify user has access to this specific workspace
        auth_service = AuthorizationService(db)
        await auth_service.verify_workspace_access(workspace_id, user, Permission.PROJECT_READ)

    # Sanitize search query to prevent SQL injection via LIKE
    sanitized_search = sanitize_search_query(search)

    # Build query with RLS filtering (user's workspaces only)
    query = (
        select(Project)
        .join(Workspace, Project.workspace_id == Workspace.id)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user.id)
    )

    # Apply workspace filter
    if workspace_id:
        query = query.filter(Project.workspace_id == workspace_id)

    # Apply search filter (case-insensitive, using sanitized input)
    if sanitized_search:
        query = query.filter(func.lower(Project.name).contains(sanitized_search.lower()))

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
    if sanitized_search:
        count_query = count_query.filter(
            func.lower(Project.name).contains(sanitized_search.lower())
        )
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
        pages=calculate_total_pages(total, page_size),
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    db: DBSession,
    user: CurrentUser,
    project_id: str = Path(..., description="Project ID (UUID format)"),
) -> ProjectDetailResponse:
    """
    Get a project by ID with its datasets (event logs).

    Returns project details including all associated datasets for process mining.
    Requires PROJECT_READ permission in the workspace.
    """
    from src.platform.workspaces.authorization import require_project_permission

    # Validate UUID format
    validate_uuid(project_id, "project_id")

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
    request: ProjectUpdateRequest,
    user: CurrentUser,
    project_id: str = Path(..., description="Project ID (UUID format)"),
) -> ProjectResponse:
    """
    Update a project's name, description, or tags.

    Requires PROJECT_UPDATE permission in the workspace.
    """
    from src.platform.workspaces.authorization import require_project_permission

    # Validate UUID format
    validate_uuid(project_id, "project_id")

    # Check permission (also validates project exists)
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_UPDATE)

    # Apply updates
    if request.name is not None:
        project.name = request.name
    if request.description is not None:
        project.description = request.description
    if request.tags is not None:
        project.tags_json = json.dumps(request.tags)

    project.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(project)

    logger.info("project_updated", project_id=project_id, user_id=user.id)

    return _project_to_response(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    db: DBSession,
    user: CurrentUser,
    project_id: str = Path(..., description="Project ID (UUID format)"),
) -> None:
    """
    Delete a project.

    Datasets (event logs) in this project are unlinked but not deleted.
    They can be re-associated with another project.

    Requires PROJECT_DELETE permission in the workspace.
    """
    from src.platform.workspaces.authorization import require_project_permission

    # Validate UUID format
    validate_uuid(project_id, "project_id")

    # Check permission (also validates project exists)
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_DELETE)

    # Unlink datasets (they remain, just not in a project)
    await db.execute(
        update(Dataset).where(Dataset.project_id == project_id).values(project_id=None)
    )

    await db.delete(project)
    await db.commit()

    logger.info("project_deleted", project_id=project_id, user_id=user.id)


# =============================================================================
# File Management
# =============================================================================


@router.post("/{project_id}/files/{dataset_id}", response_model=ProjectDetailResponse)
async def add_file_to_project(
    db: DBSession,
    user: CurrentUser,
    project_id: str = Path(..., description="Project ID (UUID format)"),
    dataset_id: str = Path(..., description="Dataset ID (UUID format)"),
) -> ProjectDetailResponse:
    """
    Add an existing dataset (event log) to a project.

    Moves the dataset into this project for organization.
    Requires PROJECT_UPDATE permission on the project
    and DATASET_UPDATE permission on the dataset.
    """
    from src.platform.workspaces.authorization import (
        require_dataset_permission,
        require_project_permission,
    )

    # Validate UUID formats
    validate_uuid(project_id, "project_id")
    validate_uuid(dataset_id, "dataset_id")

    # Check permission on project (also validates project exists)
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_UPDATE)

    # Check permission on dataset (user must have access to move it)
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_UPDATE)

    # Check if already in this project
    if dataset.project_id == project_id:
        raise ConflictError(message="Dataset is already in this project")

    dataset.project_id = project_id

    # Update total_files count
    count_result = await db.execute(
        select(func.count(Dataset.id)).filter(Dataset.project_id == project_id)
    )
    project.total_files = count_result.scalar() or 0
    project.updated_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info(
        "dataset_added_to_project", dataset_id=dataset_id, project_id=project_id, user_id=user.id
    )

    return await get_project(db, user, project_id)


@router.delete("/{project_id}/files/{dataset_id}", status_code=204)
async def remove_file_from_project(
    db: DBSession,
    user: CurrentUser,
    project_id: str = Path(..., description="Project ID (UUID format)"),
    dataset_id: str = Path(..., description="Dataset ID (UUID format)"),
) -> None:
    """
    Remove a dataset (event log) from a project.

    The dataset is unlinked but not deleted - it can be re-associated
    with another project later.

    Requires PROJECT_UPDATE permission in the workspace.
    """
    from src.platform.workspaces.authorization import (
        require_dataset_permission,
        require_project_permission,
    )

    # Validate UUID formats
    validate_uuid(project_id, "project_id")
    validate_uuid(dataset_id, "dataset_id")

    # Check permission on project (also validates project exists)
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_UPDATE)

    # Check permission on dataset (user must have access to modify it)
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_UPDATE)

    if dataset.project_id != project_id:
        raise ConflictError(message="Dataset is not in this project")

    dataset.project_id = None

    # Update total_files count
    count_result = await db.execute(
        select(func.count(Dataset.id)).filter(Dataset.project_id == project_id)
    )
    project.total_files = count_result.scalar() or 0
    project.updated_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info(
        "dataset_removed_from_project",
        dataset_id=dataset_id,
        project_id=project_id,
        user_id=user.id,
    )


# =============================================================================
# Archive/Restore
# =============================================================================


@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    db: DBSession,
    user: CurrentUser,
    project_id: str = Path(..., description="Project ID (UUID format)"),
) -> ProjectResponse:
    """
    Archive a project.

    Archived projects are hidden from default list views but still accessible.
    Requires PROJECT_UPDATE permission (editor+).
    """
    from src.platform.workspaces.authorization import require_project_permission

    # Validate UUID format
    validate_uuid(project_id, "project_id")

    # Check permission
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_UPDATE)

    # Check if already archived
    if getattr(project, "archived", False):
        raise ConflictError(message="Project is already archived")

    # Archive project (set archived flag or update status)
    # Note: If Project model doesn't have 'archived' field, we store in tags_json
    try:
        project.archived = True
    except AttributeError:
        # Fallback: store in tags_json
        import json

        tags = json.loads(project.tags_json) if project.tags_json else []
        if "_archived" not in tags:
            tags.append("_archived")
            project.tags_json = json.dumps(tags)

    project.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(project)

    logger.info("project_archived", project_id=project_id, user_id=user.id)

    return _project_to_response(project)


@router.post("/{project_id}/restore", response_model=ProjectResponse)
async def restore_project(
    db: DBSession,
    user: CurrentUser,
    project_id: str = Path(..., description="Project ID (UUID format)"),
) -> ProjectResponse:
    """
    Restore an archived project.

    Restores a previously archived project back to active status.
    Requires PROJECT_UPDATE permission (editor+).
    """
    from src.platform.workspaces.authorization import require_project_permission

    # Validate UUID format
    validate_uuid(project_id, "project_id")

    # Check permission
    _, project = await require_project_permission(db, project_id, user, Permission.PROJECT_UPDATE)

    # Restore project
    try:
        if not getattr(project, "archived", False):
            raise ConflictError(message="Project is not archived")
        project.archived = False
    except AttributeError:
        # Fallback: remove from tags_json
        import json

        tags = json.loads(project.tags_json) if project.tags_json else []
        if "_archived" not in tags:
            raise ConflictError(message="Project is not archived")
        tags = [t for t in tags if t != "_archived"]
        project.tags_json = json.dumps(tags) if tags else None

    project.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(project)

    logger.info("project_restored", project_id=project_id, user_id=user.id)

    return _project_to_response(project)
