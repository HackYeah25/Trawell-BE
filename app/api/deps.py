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
security_optional = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
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
    # If no Authorization header provided, allow anonymous access
    if credentials is None:
        return TokenData(user_id="anonymous", email="anonymous@example.com")

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: Optional[str] = payload.get("sub")
        email: Optional[str] = payload.get("email")

        if not user_id or not email:
            return TokenData(user_id="anonymous", email="anonymous@example.com")

        return TokenData(user_id=user_id, email=email)

    except JWTError:
        # For invalid tokens, degrade gracefully to anonymous
        return TokenData(user_id="anonymous", email="anonymous@example.com")


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
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional)
) -> Optional[dict]:
    """
    Get current user if authenticated, None otherwise

    Args:
        credentials: Optional HTTP Bearer token

    Returns:
        User dict with id and email if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        token_data = await get_current_user(credentials)
        # Return dict format for consistency with profiling endpoints
        return {"id": token_data.user_id, "email": token_data.email}
    except HTTPException:
        return None
