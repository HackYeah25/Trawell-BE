"""
On-site support module endpoints
"""
from fastapi import APIRouter, Depends, HTTPException

from app.models.user import TokenData
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/{trip_id}/chat")
async def on_site_chat(
    trip_id: str,
    message: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Chat with AI for on-site support

    Args:
        trip_id: Trip ID
        message: User message
        current_user: Authenticated user

    Returns:
        AI response
    """
    # TODO: Implement on-site chat
    raise HTTPException(
        status_code=501,
        detail="On-site chat not yet implemented"
    )


@router.get("/{trip_id}/nearby")
async def get_nearby_recommendations(
    trip_id: str,
    location: str,
    category: str = None,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get nearby recommendations

    Args:
        trip_id: Trip ID
        location: Current location
        category: Optional category filter
        current_user: Authenticated user

    Returns:
        Nearby recommendations
    """
    # TODO: Implement nearby recommendations
    raise HTTPException(
        status_code=501,
        detail="Nearby recommendations not yet implemented"
    )


@router.post("/{trip_id}/emergency")
async def get_emergency_info(
    trip_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get emergency information for destination

    Args:
        trip_id: Trip ID
        current_user: Authenticated user

    Returns:
        Emergency information
    """
    # TODO: Implement emergency info
    raise HTTPException(
        status_code=501,
        detail="Emergency info not yet implemented"
    )
