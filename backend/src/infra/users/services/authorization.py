"""Authorization service - workspace membership and permission checking.

Provides:
- Workspace membership verification
- Permission checks based on workspace roles
- Row-level security helpers for org_id filtering
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.core.exceptions import ForbiddenError, NotFoundError
from src.infra.core.logging_config import get_logger
from src.infra.core.permissions import Permission, has_permission

if TYPE_CHECKING:
    from src.infra.models import User, Workspace, WorkspaceMember

logger = get_logger(__name__)


class AuthorizationService:
    """Service for authorization and permission checking."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def get_workspace_membership(
        self, workspace_id: str, user_id: str
    ) -> "WorkspaceMember | None":
        """Get user's workspace membership.

        Args:
            workspace_id: Workspace ID
            user_id: User ID

        Returns:
            WorkspaceMember if user is member, None otherwise
        """
        from src.infra.models import WorkspaceMember

        result = await self.db.execute(
            select(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def require_workspace_membership(
        self, workspace_id: str, user_id: str
    ) -> "WorkspaceMember":
        """Require user to be member of workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID

        Returns:
            WorkspaceMember

        Raises:
            ForbiddenError: If user is not a member
        """
        membership = await self.get_workspace_membership(workspace_id, user_id)
        if not membership:
            logger.warning(
                "workspace_access_denied",
                workspace_id=workspace_id,
                user_id=user_id,
            )
            raise ForbiddenError(f"Access denied: not a member of workspace {workspace_id}")
        return membership

    async def check_permission(
        self,
        workspace_id: str,
        user_id: str,
        permission: Permission,
    ) -> None:
        """Check if user has permission in workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            permission: Required permission

        Raises:
            ForbiddenError: If user lacks permission
        """
        membership = await self.require_workspace_membership(workspace_id, user_id)

        if not has_permission(membership.role, permission):
            logger.warning(
                "permission_denied",
                workspace_id=workspace_id,
                user_id=user_id,
                role=membership.role,
                required_permission=permission,
            )
            raise ForbiddenError(f"Insufficient permissions: requires {permission.value}")

        logger.debug(
            "permission_granted",
            workspace_id=workspace_id,
            user_id=user_id,
            role=membership.role,
            permission=permission,
        )

    async def get_user_workspaces(self, user_id: str) -> list["Workspace"]:
        """Get all workspaces user has access to.

        Args:
            user_id: User ID

        Returns:
            List of workspaces
        """
        from src.infra.models import Workspace, WorkspaceMember

        result = await self.db.execute(
            select(Workspace).join(WorkspaceMember).filter(WorkspaceMember.user_id == user_id)
        )
        return list(result.scalars().all())

    async def verify_org_access(self, user: "User", org_id: str) -> None:
        """Verify user belongs to organization.

        Args:
            user: User object
            org_id: Organization ID

        Raises:
            ForbiddenError: If user doesn't belong to org
        """
        if user.org_id != org_id:
            logger.warning(
                "org_access_denied",
                user_id=user.id,
                user_org=user.org_id,
                requested_org=org_id,
            )
            raise ForbiddenError(f"Access denied: not a member of org {org_id}")

    async def get_workspace_by_id(self, workspace_id: str) -> "Workspace":
        """Get workspace by ID with validation.

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace object

        Raises:
            NotFoundError: If workspace doesn't exist
        """
        from src.infra.models import Workspace

        result = await self.db.execute(select(Workspace).filter(Workspace.id == workspace_id))
        workspace = result.scalar_one_or_none()

        if not workspace:
            raise NotFoundError("Workspace", workspace_id)

        return workspace

    async def verify_workspace_access(
        self,
        workspace_id: str,
        user: "User",
        permission: Permission,
    ) -> "WorkspaceMember":
        """Verify user has access to workspace with required permission.

        This is the main authorization method for workspace-scoped resources.

        Args:
            workspace_id: Workspace ID
            user: User object
            permission: Required permission

        Returns:
            WorkspaceMember

        Raises:
            NotFoundError: If workspace doesn't exist
            ForbiddenError: If user lacks access or permission
        """
        # Verify workspace exists
        workspace = await self.get_workspace_by_id(workspace_id)

        # Verify user is in same org
        await self.verify_org_access(user, workspace.org_id)

        # Check workspace membership and permission
        await self.check_permission(workspace_id, user.id, permission)

        # Return membership for convenience
        membership = await self.get_workspace_membership(workspace_id, user.id)
        assert membership is not None  # Already checked above
        return membership


# =============================================================================
# Row-Level Security Helpers
# =============================================================================


async def filter_by_org(
    query,
    user: "User",
    model_class,
) -> tuple:
    """Apply org_id filter to query for row-level security.

    Args:
        query: SQLAlchemy query
        user: Current user
        model_class: ORM model class to filter

    Returns:
        Filtered query

    Example:
        query = select(Project)
        query = filter_by_org(query, user, Project)
        results = await db.execute(query)
    """
    if not user.org_id:
        logger.warning("user_without_org", user_id=user.id)
        # Return empty results for users without org
        return query.filter(model_class.org_id == "INVALID")

    return query.filter(model_class.org_id == user.org_id)


async def filter_by_workspace_membership(
    db: AsyncSession,
    user: "User",
    workspace_model,
) -> list[str]:
    """Get list of workspace IDs user has access to.

    Use this for filtering queries by workspace_id.

    Args:
        db: Database session
        user: Current user
        workspace_model: Workspace ORM class (for type checking)

    Returns:
        List of workspace IDs

    Example:
        workspace_ids = await filter_by_workspace_membership(db, user, Workspace)
        query = select(Project).filter(Project.workspace_id.in_(workspace_ids))
    """
    from src.infra.models import WorkspaceMember

    result = await db.execute(
        select(WorkspaceMember.workspace_id).filter(WorkspaceMember.user_id == user.id)
    )
    return list(result.scalars().all())


# =============================================================================
# Resource Permission Helpers
# =============================================================================


async def require_dataset_permission(
    db: AsyncSession,
    dataset_id: str,
    user: "User",
    permission: Permission,
) -> tuple[str, Any]:
    """Verify user has permission to access dataset.

    Args:
        db: Database session
        dataset_id: Dataset ID
        user: Current user
        permission: Required permission

    Returns:
        Tuple of (workspace_id, dataset)

    Raises:
        NotFoundError: If dataset doesn't exist
        ForbiddenError: If user lacks permission
    """
    from src.features.process_mining.models import Dataset
    from src.infra.models import Project

    # Get dataset with project
    result = await db.execute(select(Dataset).filter(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise NotFoundError("Dataset", dataset_id)

    # Get project to find workspace_id
    project_result = await db.execute(select(Project).filter(Project.id == dataset.project_id))
    project = project_result.scalar_one_or_none()

    if not project or not project.workspace_id:
        raise NotFoundError("Project", dataset.project_id or "unknown")

    # Check workspace access and permission
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(project.workspace_id, user, permission)

    return project.workspace_id, dataset


async def require_project_permission(
    db: AsyncSession,
    project_id: str,
    user: "User",
    permission: Permission,
) -> tuple[str, Any]:
    """Verify user has permission to access project.

    Args:
        db: Database session
        project_id: Project ID
        user: Current user
        permission: Required permission

    Returns:
        Tuple of (workspace_id, project)

    Raises:
        NotFoundError: If project doesn't exist
        ForbiddenError: If user lacks permission
    """
    from src.infra.models import Project

    # Get project
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise NotFoundError("Project", project_id)

    # Check workspace access and permission
    if not project.workspace_id:
        raise NotFoundError("Project", project_id)
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(project.workspace_id, user, permission)

    return project.workspace_id, project


async def require_analysis_permission(
    db: AsyncSession,
    analysis_id: str,
    user: "User",
    permission: Permission,
) -> tuple[str, Any]:
    """Verify user has permission to access analysis.

    Args:
        db: Database session
        analysis_id: Analysis ID
        user: Current user
        permission: Required permission

    Returns:
        Tuple of (workspace_id, analysis)

    Raises:
        NotFoundError: If analysis doesn't exist
        ForbiddenError: If user lacks permission
    """
    from src.features.process_mining.models import Analysis, Dataset
    from src.infra.models import Project

    # Get analysis
    result = await db.execute(select(Analysis).filter(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise NotFoundError("Analysis", analysis_id)

    # Get dataset to find project
    dataset_result = await db.execute(select(Dataset).filter(Dataset.id == analysis.dataset_id))
    dataset = dataset_result.scalar_one_or_none()

    if not dataset or not dataset.project_id:
        raise NotFoundError("Dataset", analysis.dataset_id)

    # Get project to find workspace_id
    project_result = await db.execute(select(Project).filter(Project.id == dataset.project_id))
    project = project_result.scalar_one_or_none()

    if not project:
        raise NotFoundError("Project", dataset.project_id or "unknown")

    # Check workspace access and permission
    auth_service = AuthorizationService(db)
    if not project.workspace_id:
        raise NotFoundError("Project", dataset.project_id or "unknown")
    await auth_service.verify_workspace_access(project.workspace_id, user, permission)

    return project.workspace_id, analysis


async def require_model_permission(
    db: AsyncSession,
    model_id: str,
    user: "User",
    permission: Permission,
) -> tuple[str, Any]:
    """Verify user has permission to access process model.

    Args:
        db: Database session
        model_id: Process model ID
        user: Current user
        permission: Required permission

    Returns:
        Tuple of (workspace_id, model)

    Raises:
        NotFoundError: If model doesn't exist
        ForbiddenError: If user lacks permission
    """
    from src.features.process_mining.models import Dataset, ProcessModel
    from src.infra.models import Project

    # Get model
    result = await db.execute(select(ProcessModel).filter(ProcessModel.id == model_id))
    model = result.scalar_one_or_none()

    if not model:
        raise NotFoundError("ProcessModel", model_id)

    # Get dataset to find project
    dataset_result = await db.execute(select(Dataset).filter(Dataset.id == model.dataset_id))
    dataset = dataset_result.scalar_one_or_none()

    if not dataset or not dataset.project_id:
        raise NotFoundError("Dataset", model.dataset_id or "unknown")

    # Get project to find workspace
    project_result = await db.execute(select(Project).filter(Project.id == dataset.project_id))
    project = project_result.scalar_one_or_none()

    if not project or not project.workspace_id:
        raise NotFoundError("Project", dataset.project_id or "unknown")

    # Check workspace access and permission
    auth_service = AuthorizationService(db)
    await auth_service.verify_workspace_access(project.workspace_id, user, permission)

    return project.workspace_id, model
