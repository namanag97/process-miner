"""
Organizations router - Manage organizations.

Organizations are the top-level container for multi-tenancy.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models import (
    Organization,
    OrganizationCreate,
    OrganizationResponse,
    User,
    Process,
)
from ..database import get_db
from ..services import audit_service
from ..core import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/organizations", tags=["organizations"])


def generate_slug(name: str) -> str:
    """Generate URL-safe slug from name."""
    import re
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug


@router.post("", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new organization."""
    # Generate slug
    slug = generate_slug(org_data.name)
    
    # Check for duplicate slug
    result = await db.execute(
        select(Organization).where(Organization.slug == slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Organization with this name already exists")
    
    # Create organization
    org = Organization(
        name=org_data.name,
        slug=slug,
        description=org_data.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    db.add(org)
    await db.commit()
    await db.refresh(org)
    
    # Log action
    await audit_service.log_action(
        db=db,
        entity_type="organization",
        entity_id=org.id,
        action="create",
        details={"name": org.name, "slug": org.slug},
    )
    
    log.info("organization_created", org_id=org.id, name=org.name)
    
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        created_at=org.created_at,
        user_count=0,
        process_count=0,
    )


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
):
    """List all organizations."""
    # Subquery for user counts per org
    user_counts = (
        select(User.org_id, func.count().label("count"))
        .group_by(User.org_id)
        .subquery()
    )
    
    # Subquery for process counts per org
    process_counts = (
        select(Process.org_id, func.count().label("count"))
        .group_by(Process.org_id)
        .subquery()
    )
    
    # Single query with left joins to get all data at once
    query = (
        select(
            Organization,
            func.coalesce(user_counts.c.count, 0).label("user_count"),
            func.coalesce(process_counts.c.count, 0).label("process_count")
        )
        .outerjoin(user_counts, Organization.id == user_counts.c.org_id)
        .outerjoin(process_counts, Organization.id == process_counts.c.org_id)
        .order_by(Organization.created_at.desc())
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            description=org.description,
            created_at=org.created_at,
            user_count=user_count,
            process_count=process_count,
        )
        for org, user_count, process_count in rows
    ]


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get organization by ID."""
    # Subqueries for counts
    user_counts = (
        select(User.org_id, func.count().label("count"))
        .where(User.org_id == org_id)
        .group_by(User.org_id)
        .subquery()
    )
    process_counts = (
        select(Process.org_id, func.count().label("count"))
        .where(Process.org_id == org_id)
        .group_by(Process.org_id)
        .subquery()
    )
    
    query = (
        select(
            Organization,
            func.coalesce(user_counts.c.count, 0).label("user_count"),
            func.coalesce(process_counts.c.count, 0).label("process_count")
        )
        .where(Organization.id == org_id)
        .outerjoin(user_counts, Organization.id == user_counts.c.org_id)
        .outerjoin(process_counts, Organization.id == process_counts.c.org_id)
    )
    
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    org, user_count, process_count = row
    
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        created_at=org.created_at,
        user_count=user_count,
        process_count=process_count,
    )


@router.delete("/{org_id}")
async def delete_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete an organization and all its data."""
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Log before delete
    await audit_service.log_action(
        db=db,
        entity_type="organization",
        entity_id=org.id,
        action="delete",
        details={"name": org.name},
    )
    
    await db.delete(org)
    await db.commit()
    
    log.info("organization_deleted", org_id=org_id)
    
    return {"message": "Organization deleted", "org_id": org_id}
