"""
Users router - Simple user management.

Creates and verifies users for session tracking (no auth, just ID-based).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import User, UserResponse
from ..services.repository import BaseRepository
from ..core import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


async def get_user_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[User]:
    return BaseRepository(User, db)


@router.post("", response_model=UserResponse)
async def create_user(
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user and return their ID.
    Clients should store this ID and send it with future requests.
    """
    new_user = User()
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    log.info("user_created", user_id=new_user.id)
    
    return UserResponse(
        id=new_user.id,
        created_at=new_user.created_at,
        last_active_at=new_user.last_active_at,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user_id: str,
    user_repo: BaseRepository[User] = Depends(get_user_repo),
):
    """Verify if a user exists."""
    user = await user_repo.get_or_404(user_id)
    return UserResponse(
        id=user.id,
        created_at=user.created_at,
        last_active_at=user.last_active_at,
    )

