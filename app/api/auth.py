"""
Authentication endpoints
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from app.config import settings
from app.models.user import User, UserCreate, UserLogin, Token
from app.services.supabase_service import SupabaseService
from app.api.deps import get_supabase_dep

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Register a new user

    Args:
        user_data: User registration data
        supabase: Supabase service

    Returns:
        Access token and user data
    """
    # TODO: Implement user registration with Supabase Auth
    # For now, returning placeholder response

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Registration endpoint not yet implemented"
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Login user and return access token

    Args:
        credentials: Login credentials
        supabase: Supabase service

    Returns:
        Access token and user data
    """
    # TODO: Implement login with Supabase Auth
    # For now, returning placeholder response

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login endpoint not yet implemented"
    )


@router.post("/logout")
async def logout():
    """Logout user (invalidate token)"""
    # TODO: Implement token invalidation
    return {"message": "Logged out successfully"}
