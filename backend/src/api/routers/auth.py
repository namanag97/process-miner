"""Auth Router.

MVP authentication endpoints - mock auth for development.
In production, replace with proper OAuth/JWT implementation.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.api.dependencies import DBSession
from src.models.orm import Organization, User, Workspace, WorkspaceMember
from src.models.schemas import (
    CurrentUserResponse,
    OrganizationResponse,
    UserResponse,
    WorkspaceResponse,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# =============================================================================
# Helper Functions
# =============================================================================


def _user_to_response(user: User) -> UserResponse:
    """Convert User ORM to UserResponse."""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )


def _org_to_response(org: Organization) -> OrganizationResponse:
    """Convert Organization ORM to OrganizationResponse."""
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        created_at=org.created_at,
        updated_at=org.updated_at,
    )


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


# =============================================================================
# MVP Endpoints
# =============================================================================


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    db: DBSession,
    email: Optional[str] = Query(None, description="Email to identify user (MVP mode)"),
) -> CurrentUserResponse:
    """
    Get current user context.
    
    MVP Mode: Creates a default user/org/workspace if none exists.
    In production, this would use JWT/session auth.
    """
    # For MVP, use email param or default to demo user
    user_email = email or "demo@processminer.io"
    
    # Try to find existing user
    result = await db.execute(select(User).filter(User.email == user_email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create default setup for MVP
        user, org, workspace = await _create_default_setup(db, user_email)
    else:
        # Get organization
        org = None
        if user.org_id:
            org_result = await db.execute(select(Organization).filter(Organization.id == user.org_id))
            org = org_result.scalar_one_or_none()
    
    # Get user's workspaces via memberships (single query with join)
    workspaces_result = await db.execute(
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user.id)
    )
    workspaces: list[Workspace] = list(workspaces_result.scalars().all())
    
    # If no memberships but org has workspaces, use those
    if not workspaces and org:
        ws_result = await db.execute(
            select(Workspace).filter(Workspace.org_id == org.id)
        )
        workspaces = list(ws_result.scalars().all())
    
    return CurrentUserResponse(
        user=_user_to_response(user),
        organization=_org_to_response(org) if org else None,
        workspaces=[_workspace_to_response(w) for w in workspaces],
        current_workspace_id=workspaces[0].id if workspaces else None,
    )


async def _create_default_setup(
    db: DBSession, 
    email: str
) -> tuple[User, Organization, Workspace]:
    """Create default org, workspace, and user for MVP."""
    
    # Check if demo org already exists
    org_result = await db.execute(select(Organization).filter(Organization.slug == "demo-org"))
    org = org_result.scalar_one_or_none()
    
    if not org:
        # Create organization
        org = Organization(
            id=str(uuid4()),
            name="Demo Organization",
            slug="demo-org",
            plan="free",
            created_at=datetime.utcnow(),
        )
        db.add(org)
    
    # Check if default workspace already exists for this org
    # (Assuming we want to reuse it too, or create new one? 
    #  For MVP simpler to reuse if we are reusing Org)
    # But for now, let's just make sure we don't crash on Org unique slug.
    # Workspace names are not unique usually, but let's see model.
    
    # Create workspace
    workspace_result = await db.execute(
        select(Workspace)
        .filter(Workspace.org_id == org.id)
        .filter(Workspace.name == "Default Workspace")
    )
    workspace = workspace_result.scalar_one_or_none()
    
    if not workspace:
        workspace = Workspace(
            id=str(uuid4()),
            org_id=org.id,
            name="Default Workspace",
            description="Your default process mining workspace",
            created_at=datetime.utcnow(),
        )
        db.add(workspace)
    
    # Create user
    user = User(
        id=str(uuid4()),
        org_id=org.id,
        email=email,
        name="Demo User",
        auth_provider="local",
        role="admin",
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow(),
    )
    db.add(user)
    
    # Create membership
    membership = WorkspaceMember(
        id=str(uuid4()),
        workspace_id=workspace.id,
        user_id=user.id,
        role="owner",
        joined_at=datetime.utcnow(),
    )
    db.add(membership)
    
    await db.commit()
    await db.refresh(user)
    if org not in db.dirty and org not in db.new:
         # Refresh might fail if not attached? 
         # Just proceed, we have the object.
         pass
    else:
        await db.refresh(org)
        
    if workspace not in db.dirty and workspace not in db.new:
        pass
    else:
        await db.refresh(workspace)
    
    return user, org, workspace


@router.post("/login")
async def login(
    db: DBSession,
    email: str = Query(..., description="User email"),
    password: str = Query(default="", description="Password (ignored in MVP)"),
) -> CurrentUserResponse:
    """
    Login endpoint (MVP mode - accepts any credentials).
    
    In production, replace with proper authentication.
    """
    # MVP: Just return the user context
    return await get_current_user(db, email=email)


@router.post("/logout")
async def logout() -> dict[str, str]:
    """
    Logout endpoint (MVP mode - no-op).
    
    In production, invalidate session/token.
    """
    return {"status": "logged_out", "message": "MVP mode - no session to invalidate"}
