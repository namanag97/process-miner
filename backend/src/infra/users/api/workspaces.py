"""Workspaces Router.

Endpoints for managing workspaces within an organization.
Workspaces provide multi-tenant isolation for process mining projects.

## Business Context
Workspaces are collaboration containers within an organization:
- Each workspace can have multiple members with different roles (owner, admin, editor, viewer)
- Projects (containing datasets/event logs) are organized within workspaces
- Authorization is enforced at the workspace level

## Testing Instructions

### Prerequisites
1. Register a user: `POST /api/v1/auth/register` → Get `access_token`
2. Add `Authorization: Bearer {access_token}` header to all requests

### Test Flow
1. **List Workspaces**: `GET /api/v1/workspaces` → Returns user's workspaces
2. **Create Workspace**: `POST /api/v1/workspaces?org_id={org_id}` with `{"name": "Test Workspace"}`
3. **Get Workspace**: `GET /api/v1/workspaces/{workspace_id}` → Returns workspace with projects
4. **Update Workspace**: `PUT /api/v1/workspaces/{workspace_id}` with `{"name": "Updated Name"}`
5. **Manage Members**: `GET/POST/PUT/DELETE /api/v1/workspaces/{workspace_id}/members`
6. **Delete Workspace**: `DELETE /api/v1/workspaces/{workspace_id}` (owner only)

### Common Errors
- **401**: Missing or invalid JWT token
- **403**: User doesn't have required permission (check workspace membership)
- **404**: Workspace or Organization not found (verify UUID is correct)
- **422**: Invalid UUID format or missing required fields
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Path, Query
from sqlalchemy import delete, func, select

from src.api.dependencies import CurrentUser, ReadDBSession
from src.infra.core.error_messages import ErrorMessages
from src.infra.core.exceptions import ConflictError, NotFoundError
from src.infra.core.logging_config import get_logger
from src.infra.core.permissions import Permission
from src.infra.core.validation import calculate_total_pages, validate_uuid
from src.infra.schemas import (
    ProjectResponse,
    WorkspaceCreateRequest,
    WorkspaceDetailResponse,
    WorkspaceListResponse,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)
from src.infra.users import Organization, Project, Workspace, WorkspaceMember
from src.infra.workspaces.authorization import AuthorizationService
from src.infra.workspaces.schemas import (
    AddMemberRequest,
    UpdateMemberRoleRequest,
    WorkspaceMemberListResponse,
)
from src.infra.workspaces.schemas import (
    WorkspaceMemberResponseInline as WorkspaceMemberResponse,
)

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
        name=workspace.name or "",
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
    user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    org_id: str | None = Query(None, description="Filter by organization ID"),
) -> WorkspaceListResponse:
    """
    List workspaces accessible to the current user.

    In multi-tenant SaaS mode, returns only workspaces where user is a member.
    Optionally filter by organization ID.
    """
    # Build query with user membership filter (Row-Level Security)
    query = (
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user.id)
    )

    # Apply organization filter if provided
    if org_id:
        validate_uuid(org_id, "org_id")
        query = query.filter(Workspace.org_id == org_id)

    # Get total count with same filters
    count_query = (
        select(func.count())
        .select_from(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user.id)
    )
    if org_id:
        count_query = count_query.filter(Workspace.org_id == org_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate results
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
        pages=calculate_total_pages(total, page_size),
    )


@router.get("/{workspace_id}", response_model=WorkspaceDetailResponse)
async def get_workspace(
    db: ReadDBSession,
    user: CurrentUser,
    workspace_id: str = Path(..., description="Workspace ID (UUID format)"),
) -> WorkspaceDetailResponse:
    """
    Get a workspace by ID with its projects.

    Requires WORKSPACE_READ permission (membership in the workspace).
    """
    # Validate UUID format
    validate_uuid(workspace_id, "workspace_id")

    # Authorization: verify user has access to this workspace
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.WORKSPACE_READ)

    # Fetch workspace
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise NotFoundError(resource="Workspace", resource_id=workspace_id)

    # Get projects for this workspace
    projects_result = await db.execute(
        select(Project)
        .filter(Project.workspace_id == workspace_id)
        .order_by(Project.created_at.desc())
    )
    projects = projects_result.scalars().all()

    return WorkspaceDetailResponse(
        id=workspace.id,
        org_id=workspace.org_id,
        name=workspace.name or "",
        description=workspace.description,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
        projects=[_project_to_response(p) for p in projects],
    )


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    db: ReadDBSession,
    request: WorkspaceCreateRequest,
    user: CurrentUser,
    org_id: str = Query(..., description="Organization ID for the workspace"),
) -> WorkspaceResponse:
    """
    Create a new workspace within an organization.

    The creating user automatically becomes the workspace owner.
    Requires user to be a member of the organization.
    """
    # Validate org_id format
    validate_uuid(org_id, "org_id")

    # Verify organization exists
    org_result = await db.execute(select(Organization).filter(Organization.id == org_id))
    org = org_result.scalar_one_or_none()
    if not org:
        raise NotFoundError(resource="Organization", resource_id=org_id)

    # Verify user belongs to this organization
    if user.org_id != org_id:
        raise ConflictError(
            message=ErrorMessages.permission_denied("create a workspace", "Organization"),
        )

    # Create workspace
    workspace = Workspace(
        org_id=org_id,
        name=request.name or "",
        description=request.description,
        created_at=datetime.now(timezone.utc),
    )
    db.add(workspace)
    await db.flush()  # Get workspace.id

    # Add creator as workspace owner
    from uuid import uuid4

    membership = WorkspaceMember(
        id=str(uuid4()),
        workspace_id=workspace.id,
        user_id=user.id,
        role="owner",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(membership)

    await db.commit()
    await db.refresh(workspace)

    logger.info("workspace_created", workspace_id=workspace.id, user_id=user.id, org_id=org_id)

    return _workspace_to_response(workspace)


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    db: ReadDBSession,
    request: WorkspaceUpdateRequest,
    user: CurrentUser,
    workspace_id: str = Path(..., description="Workspace ID (UUID format)"),
) -> WorkspaceResponse:
    """
    Update a workspace's name or description.

    Requires WORKSPACE_UPDATE permission (admin or owner role).
    """
    # Validate UUID format
    validate_uuid(workspace_id, "workspace_id")

    # Authorization: verify user has update permission
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.WORKSPACE_UPDATE)

    # Fetch workspace
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise NotFoundError(resource="Workspace", resource_id=workspace_id)

    # Apply updates
    if request.name is not None:
        workspace.name = request.name
    if request.description is not None:
        workspace.description = request.description

    workspace.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(workspace)

    logger.info("workspace_updated", workspace_id=workspace_id, user_id=user.id)

    return _workspace_to_response(workspace)


@router.delete("/{workspace_id}", status_code=204)
async def delete_workspace(
    db: ReadDBSession,
    user: CurrentUser,
    workspace_id: str = Path(..., description="Workspace ID (UUID format)"),
) -> None:
    """
    Delete a workspace and all its projects.

    Requires WORKSPACE_DELETE permission (owner role only).
    WARNING: This permanently deletes all projects in the workspace.
    Fails if any projects contain datasets (delete datasets first).
    """
    # Validate UUID format
    validate_uuid(workspace_id, "workspace_id")

    # Authorization: verify user has delete permission (owner only)
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.WORKSPACE_DELETE)

    # Fetch workspace
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise NotFoundError(resource="Workspace", resource_id=workspace_id)

    # Check for datasets in workspace projects (prevent data loss)
    from src.features.process_mining.models import Dataset

    dataset_count_result = await db.execute(
        select(func.count())
        .select_from(Dataset)
        .join(Project, Project.id == Dataset.project_id)
        .where(Project.workspace_id == workspace_id)
    )
    dataset_count = dataset_count_result.scalar() or 0

    if dataset_count > 0:
        raise ConflictError(
            message=f"Cannot delete workspace with {dataset_count} dataset(s). Delete all datasets first.",
        )

    # Delete all projects in this workspace
    await db.execute(delete(Project).where(Project.workspace_id == workspace_id))

    # Delete all workspace memberships
    await db.execute(delete(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id))

    # Delete workspace
    await db.delete(workspace)
    await db.commit()

    logger.info("workspace_deleted", workspace_id=workspace_id, user_id=user.id)


# =============================================================================
# Project Association
# =============================================================================


@router.post("/{workspace_id}/projects/{project_id}", response_model=WorkspaceDetailResponse)
async def add_project_to_workspace(
    db: ReadDBSession,
    user: CurrentUser,
    workspace_id: str = Path(..., description="Workspace ID (UUID format)"),
    project_id: str = Path(..., description="Project ID (UUID format)"),
) -> WorkspaceDetailResponse:
    """
    Move an existing project into this workspace.

    Requires WORKSPACE_UPDATE permission on the target workspace
    and PROJECT_UPDATE permission on the project.
    """
    # Validate UUID formats
    validate_uuid(workspace_id, "workspace_id")
    validate_uuid(project_id, "project_id")

    # Authorization: verify user has access to workspace
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.WORKSPACE_UPDATE)

    # Fetch workspace
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise NotFoundError(resource="Workspace", resource_id=workspace_id)

    # Fetch project
    project_result = await db.execute(select(Project).filter(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise NotFoundError(resource="Project", resource_id=project_id)

    # Check if project is already in this workspace
    if project.workspace_id == workspace_id:
        raise ConflictError(
            message=ErrorMessages.resource_conflict("Project", "already in this workspace"),
        )

    # Move project to workspace
    project.workspace_id = workspace_id
    workspace.updated_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info("project_added_to_workspace", project_id=project_id, workspace_id=workspace_id)

    return await get_workspace(db, user, workspace_id)


@router.delete("/{workspace_id}/projects/{project_id}", status_code=204)
async def remove_project_from_workspace(
    db: ReadDBSession,
    user: CurrentUser,
    workspace_id: str = Path(..., description="Workspace ID (UUID format)"),
    project_id: str = Path(..., description="Project ID (UUID format)"),
) -> None:
    """
    Remove a project from a workspace (doesn't delete the project).

    The project becomes unassigned and can be re-associated with another workspace.
    Requires WORKSPACE_UPDATE permission.
    """
    # Validate UUID formats
    validate_uuid(workspace_id, "workspace_id")
    validate_uuid(project_id, "project_id")

    # Authorization: verify user has access to workspace
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.WORKSPACE_UPDATE)

    # Fetch workspace
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise NotFoundError(resource="Workspace", resource_id=workspace_id)

    # Fetch project
    project_result = await db.execute(select(Project).filter(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise NotFoundError(resource="Project", resource_id=project_id)

    # Verify project is in this workspace
    if project.workspace_id != workspace_id:
        raise ConflictError(
            message=ErrorMessages.resource_conflict("Project", "not in this workspace"),
        )

    # Remove project from workspace
    project.workspace_id = None
    workspace.updated_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info("project_removed_from_workspace", project_id=project_id, workspace_id=workspace_id)


# =============================================================================
# Member Management
# =============================================================================


@router.get("/{workspace_id}/members", response_model=WorkspaceMemberListResponse)
async def list_workspace_members(
    db: ReadDBSession,
    user: CurrentUser,
    workspace_id: str = Path(..., description="Workspace ID (UUID format)"),
) -> WorkspaceMemberListResponse:
    """List workspace members."""
    validate_uuid(workspace_id, "workspace_id")

    # Verify user has access
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.WORKSPACE_READ)

    # Get members with user info
    from src.infra.models import User

    result = await db.execute(
        select(WorkspaceMember, User)
        .join(User, User.id == WorkspaceMember.user_id)
        .where(WorkspaceMember.workspace_id == workspace_id)
    )
    rows = result.all()

    members = [
        WorkspaceMemberResponse(
            user_id=member.user_id,
            email=u.email,
            name=u.name or "",
            role=member.role,
            joined_at=member.joined_at,
        )
        for member, u in rows
    ]

    return WorkspaceMemberListResponse(items=members, total=len(members))


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse, status_code=201)
async def add_workspace_member(
    request: AddMemberRequest,
    db: ReadDBSession,
    user: CurrentUser,
    workspace_id: str = Path(..., description="Workspace ID (UUID format)"),
) -> WorkspaceMemberResponse:
    """Add member to workspace (admin only)."""
    validate_uuid(workspace_id, "workspace_id")
    validate_uuid(request.user_id, "user_id")

    # Verify user has admin access
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.WORKSPACE_UPDATE)

    # Check workspace exists
    ws_result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise NotFoundError(resource="Workspace", resource_id=workspace_id)

    # Check target user exists
    from src.infra.models import User

    user_result = await db.execute(select(User).where(User.id == request.user_id))
    target_user = user_result.scalar_one_or_none()
    if not target_user:
        raise NotFoundError(resource="User", resource_id=request.user_id)

    # Check if already a member
    existing = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == request.user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(
            message=ErrorMessages.resource_already_exists("Member", request.user_id),
        )

    # Add member
    from uuid import uuid4

    member = WorkspaceMember(
        id=str(uuid4()),
        workspace_id=workspace_id,
        user_id=request.user_id,
        role=request.role,
        joined_at=datetime.now(timezone.utc),
    )
    db.add(member)
    await db.commit()

    logger.info(
        "workspace_member_added",
        workspace_id=workspace_id,
        user_id=request.user_id,
        role=request.role,
        by_user=user.id,
    )

    return WorkspaceMemberResponse(
        user_id=target_user.id,
        email=target_user.email,
        name=target_user.name or "",
        role=request.role,
        joined_at=member.joined_at,
    )


@router.put("/{workspace_id}/members/{user_id}", response_model=WorkspaceMemberResponse)
async def update_workspace_member_role(
    request: UpdateMemberRoleRequest,
    db: ReadDBSession,
    user: CurrentUser,
    workspace_id: str = Path(..., description="Workspace ID (UUID format)"),
    user_id: str = Path(..., description="User ID"),
) -> WorkspaceMemberResponse:
    """Update member role (admin only)."""
    validate_uuid(workspace_id, "workspace_id")
    validate_uuid(user_id, "user_id")

    # Verify user has admin access
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.WORKSPACE_UPDATE)

    # Get membership
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise NotFoundError(resource="WorkspaceMember", resource_id=user_id)

    # Get user info
    from src.infra.models import User

    user_result = await db.execute(select(User).where(User.id == user_id))
    target_user = user_result.scalar_one_or_none()

    # Update role
    member.role = request.role
    await db.commit()

    logger.info(
        "workspace_member_role_updated",
        workspace_id=workspace_id,
        user_id=user_id,
        new_role=request.role,
        by_user=user.id,
    )

    return WorkspaceMemberResponse(
        user_id=user_id,
        email=target_user.email if target_user else "",
        name=(target_user.name or "") if target_user else "",
        role=request.role,
        joined_at=member.joined_at,
    )


@router.delete("/{workspace_id}/members/{user_id}", status_code=204)
async def remove_workspace_member(
    db: ReadDBSession,
    user: CurrentUser,
    workspace_id: str = Path(..., description="Workspace ID (UUID format)"),
    user_id: str = Path(..., description="User ID"),
) -> None:
    """Remove member from workspace (admin only)."""
    validate_uuid(workspace_id, "workspace_id")
    validate_uuid(user_id, "user_id")

    # Verify user has admin access
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(workspace_id, user, Permission.WORKSPACE_UPDATE)

    # Get membership
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise NotFoundError(resource="WorkspaceMember", resource_id=user_id)

    # Cannot remove self
    if user_id == user.id:
        raise ConflictError(
            message="You cannot remove yourself from the workspace. Please ask another admin.",
        )

    # Delete membership
    await db.delete(member)
    await db.commit()

    logger.info(
        "workspace_member_removed",
        workspace_id=workspace_id,
        user_id=user_id,
        by_user=user.id,
    )
