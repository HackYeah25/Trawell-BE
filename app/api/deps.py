"""
API dependencies and dependency injection
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import settings
from app.services.supabase_service import get_supabase, SupabaseService
from app.services.langchain_service import get_langchain_service, LangChainService
from app.utils.context_manager import get_context_manager, ContextManager
from app.prompts.loader import get_prompt_loader, PromptLoader
from app.models.user import TokenData

# Security
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Validate JWT token and return current user data

    Args:
        credentials: HTTP Bearer token

    Returns:
        Token data with user information

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id, email=email)
        return token_data

    except JWTError:
        raise credentials_exception


def get_supabase_dep() -> SupabaseService:
    """Dependency for Supabase service"""
    return get_supabase()


def get_langchain_dep() -> LangChainService:
    """Dependency for LangChain service"""
    return get_langchain_service()


def get_context_manager_dep() -> ContextManager:
    """Dependency for Context Manager"""
    return get_context_manager()


def get_prompt_loader_dep() -> PromptLoader:
    """Dependency for Prompt Loader"""
    return get_prompt_loader()


# Optional user dependency (for public endpoints)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenData]:
    """
    Get current user if authenticated, None otherwise

    Args:
        credentials: Optional HTTP Bearer token

    Returns:
        Token data if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
