"""
User endpoints: GET /api/me
"""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import TokenData, User
from app.services.supabase_service import get_supabase


router = APIRouter(prefix="/api", tags=["user"])


@router.get("/me", response_model=User)
async def get_me(current_user: TokenData = Depends(get_current_user)) -> User:
    """Return current user from Supabase mapped to User model.

    Falls back to minimal construction if Supabase is unavailable.
    """
    user_id = current_user.user_id

    try:
        supabase = get_supabase()
        if supabase.client and user_id:
            db_user = await supabase.get_user(user_id)
            if db_user:
                return db_user
    except Exception:
        pass

    # Fallback minimal user using token data
    return User(
        id=user_id,
        email=current_user.email,
        username=(current_user.email.split("@")[0] if current_user.email and "@" in current_user.email else "user"),
        is_active=True,
        is_verified=False,
    )


class APIUserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


@router.patch("/me", response_model=User)
async def patch_me(update: APIUserUpdate, current_user: TokenData = Depends(get_current_user)) -> User:
    """Update allowed User fields in Supabase and return updated User."""
    supabase = get_supabase()

    try:
        if supabase.client and current_user.user_id:
            updated = await supabase.update_user(current_user.user_id, update.model_dump())
            return updated
    except Exception:
        pass

    # If update failed or Supabase not available, return current view
    return await get_me(current_user)


