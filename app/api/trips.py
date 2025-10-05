"""
Trips API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_current_user_optional
from app.models.user import TokenData
from app.services.supabase_service import get_supabase

router = APIRouter(prefix="/api/trips", tags=["Trips"])

# Test user ID for development
TEST_USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"


class TripResponse(BaseModel):
    """Trip response model matching frontend expectations"""
    id: str
    title: str
    destination: Optional[str] = None
    locationName: Optional[str] = None
    imageUrl: Optional[str] = None
    createdAt: str
    updatedAt: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[float] = None


@router.get("", response_model=List[TripResponse])
async def list_trips(
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    List all trips for the current user.
    
    Combines destination_recommendations (brainstormed destinations) 
    and trip_plans (planned trips) into a unified list.
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()
    
    if not supabase.client:
        raise HTTPException(status_code=500, detail="Database not available")
    
    trips = []
    
    try:
        # Fetch destination recommendations
        recommendations_result = supabase.client.table("destination_recommendations").select(
            "*"
        ).eq("user_id", user_id).order("created_at", desc=True).execute()
        
        # Transform recommendations to Trip format
        for rec in recommendations_result.data:
            destination_data = rec.get("destination", {})
            
            # Handle both dict and potential string formats
            if isinstance(destination_data, str):
                destination_name = destination_data
                image_url = None
            else:
                destination_name = (
                    destination_data.get("name") or 
                    destination_data.get("city") or 
                    "Unknown Destination"
                )
                image_url = destination_data.get("imageUrl")
            
            trips.append(TripResponse(
                id=rec["recommendation_id"],
                title=destination_name,
                destination=destination_name,
                locationName=destination_name,
                imageUrl=image_url,
                createdAt=rec["created_at"],
                updatedAt=rec.get("updated_at"),
                status=rec.get("status", "suggested"),
                rating=None
            ))
        
        # Fetch trip plans
        trip_plans_result = supabase.client.table("trip_plans").select(
            "*"
        ).eq("user_id", user_id).order("created_at", desc=True).execute()
        
        # Transform trip plans to Trip format
        for plan in trip_plans_result.data:
            destination_data = plan.get("destination", {})
            
            if isinstance(destination_data, str):
                destination_name = destination_data
                image_url = None
            else:
                destination_name = (
                    destination_data.get("name") or 
                    destination_data.get("city") or 
                    "Unknown Destination"
                )
                image_url = destination_data.get("imageUrl")
            
            trips.append(TripResponse(
                id=plan["trip_id"],
                title=destination_name,
                destination=destination_name,
                locationName=destination_name,
                imageUrl=image_url,
                createdAt=plan["created_at"],
                updatedAt=plan.get("updated_at"),
                status=plan.get("status", "draft"),
                rating=None
            ))
        
        # Sort by created_at descending
        trips.sort(key=lambda x: x.createdAt, reverse=True)
        
        return trips
        
    except Exception as e:
        print(f"ERROR fetching trips: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: str,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    """
    Get details of a specific trip.
    
    Tries to fetch from destination_recommendations first, 
    then falls back to trip_plans.
    """
    user_id = current_user.user_id if current_user else TEST_USER_ID
    supabase = get_supabase()
    
    if not supabase.client:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Try destination_recommendations first
        rec_result = supabase.client.table("destination_recommendations").select(
            "*"
        ).eq("recommendation_id", trip_id).eq("user_id", user_id).execute()
        
        if rec_result.data and len(rec_result.data) > 0:
            rec = rec_result.data[0]
            destination_data = rec.get("destination", {})
            
            if isinstance(destination_data, str):
                destination_name = destination_data
                image_url = None
            else:
                destination_name = (
                    destination_data.get("name") or 
                    destination_data.get("city") or 
                    "Unknown Destination"
                )
                image_url = destination_data.get("imageUrl")
            
            return TripResponse(
                id=rec["recommendation_id"],
                title=destination_name,
                destination=destination_name,
                locationName=destination_name,
                imageUrl=image_url,
                createdAt=rec["created_at"],
                updatedAt=rec.get("updated_at"),
                status=rec.get("status", "suggested"),
                rating=None
            )
        
        # Try trip_plans
        plan_result = supabase.client.table("trip_plans").select(
            "*"
        ).eq("trip_id", trip_id).eq("user_id", user_id).execute()
        
        if plan_result.data and len(plan_result.data) > 0:
            plan = plan_result.data[0]
            destination_data = plan.get("destination", {})
            
            if isinstance(destination_data, str):
                destination_name = destination_data
                image_url = None
            else:
                destination_name = (
                    destination_data.get("name") or 
                    destination_data.get("city") or 
                    "Unknown Destination"
                )
                image_url = destination_data.get("imageUrl")
            
            return TripResponse(
                id=plan["trip_id"],
                title=destination_name,
                destination=destination_name,
                locationName=destination_name,
                imageUrl=image_url,
                createdAt=plan["created_at"],
                updatedAt=plan.get("updated_at"),
                status=plan.get("status", "draft"),
                rating=None
            )
        
        raise HTTPException(status_code=404, detail="Trip not found")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR fetching trip {trip_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
