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
    Register a new user (mock implementation)

    Args:
        user_data: User registration data
        supabase: Supabase service

    Returns:
        Access token and user data
    """
    if not supabase.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )

    try:
        # Check if user already exists
        existing = supabase.client.table("users").select("id").eq("email", user_data.email).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        password_hash = get_password_hash(user_data.password)

        # Create user in database
        user_record = {
            "email": user_data.email,
            "name": user_data.full_name or user_data.username,
            "password_hash": password_hash,
        }

        result = supabase.client.table("users").insert(user_record).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        created_user = result.data[0]
        user_id = created_user["id"]

        # Create access token
        access_token = create_access_token(
            data={"sub": user_id, "email": user_data.email}
        )

        # Return token and user data
        user = User(
            id=user_id,
            email=user_data.email,
            name=created_user.get("name"),
            onboardingCompleted=False
        )

        return Token(access_token=access_token, user=user)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Login user and return access token (mock implementation)

    Args:
        credentials: Login credentials
        supabase: Supabase service

    Returns:
        Access token and user data
    """
    if not supabase.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )

    try:
        # Find user by email
        result = supabase.client.table("users").select("*").eq("email", credentials.email).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        user_data = result.data[0]

        # Verify password
        if not user_data.get("password_hash"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(credentials.password, user_data["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        user_id = user_data["id"]

        # Check if user has completed profiling
        profile_check = supabase.client.table("profiling_sessions").select("id").eq(
            "user_id", user_id
        ).eq(
            "status", "completed"
        ).limit(1).execute()

        onboarding_completed = bool(profile_check.data)

        # Create access token
        access_token = create_access_token(
            data={"sub": user_id, "email": credentials.email}
        )

        # Return token and user data
        user = User(
            id=user_id,
            email=user_data["email"],
            name=user_data.get("name"),
            onboardingCompleted=onboarding_completed
        )

        return Token(access_token=access_token, user=user)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """Logout user (invalidate token)"""
    # TODO: Implement token invalidation
    return {"message": "Logged out successfully"}
