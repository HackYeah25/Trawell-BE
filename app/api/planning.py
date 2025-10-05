"""
Planning module endpoints - Trip planning
"""
from fastapi import APIRouter, Depends, HTTPException
import uuid

from app.models.trip import TripCreate, TripPlan, FlightSearch
from app.models.weather import WeatherRequest, WeatherResponse
from app.models.user import TokenData
from app.services.supabase_service import SupabaseService
from app.services.weather_service import get_weather_service, WeatherService
from app.api.deps import get_current_user, get_supabase_dep

router = APIRouter()


@router.post("/create")
async def create_trip_plan(
    trip_data: TripCreate,
    current_user: TokenData = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Create a new trip plan

    Args:
        trip_data: Trip creation data
        current_user: Authenticated user
        supabase: Supabase service

    Returns:
        Created trip plan
    """
    # Create trip plan
    trip = TripPlan(
        trip_id=f"trip_{uuid.uuid4().hex[:12]}",
        user_id=current_user.user_id,
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        estimated_budget=trip_data.budget
    )

    # Save to database
    created_trip = await supabase.create_trip_plan(trip)

    return created_trip


@router.get("/{trip_id}")
async def get_trip_plan(
    trip_id: str,
    current_user: TokenData = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Get trip plan details

    Args:
        trip_id: Trip ID
        current_user: Authenticated user
        supabase: Supabase service

    Returns:
        Trip plan details
    """
    trip = await supabase.get_trip_plan(trip_id)

    if not trip:
        raise HTTPException(status_code=404, detail="Trip plan not found")

    # Verify ownership
    if trip.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this trip")

    return trip


@router.post("/{trip_id}/flights")
async def search_flights(
    trip_id: str,
    flight_search: FlightSearch,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Search for flights for a trip

    Args:
        trip_id: Trip ID
        flight_search: Flight search parameters
        current_user: Authenticated user

    Returns:
        Flight search results
    """
    # TODO: Implement flight search integration
    raise HTTPException(
        status_code=501,
        detail="Flight search not yet implemented"
    )


@router.post("/{trip_id}/weather", response_model=WeatherResponse)
async def get_weather_forecast(
    trip_id: str,
    weather_request: WeatherRequest,
    current_user: TokenData = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_dep),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get weather forecast for specific coordinates

    Args:
        trip_id: Trip ID
        weather_request: Weather request with coordinates and days
        current_user: Authenticated user
        supabase: Supabase service
        weather_service: Weather service

    Returns:
        Weather forecast data
    """
    try:
        # Verify trip ownership
        trip = await supabase.get_trip_plan(trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip plan not found")
        
        if trip.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this trip")

        # Get weather forecast
        weather_data = await weather_service.get_forecast(
            city=weather_request.city,
            days=weather_request.days
        )
        return WeatherResponse(
            success=True,
            data=weather_data,
            location=weather_data.get("location"),
            forecast_days=weather_request.days
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")


@router.post("/weather", response_model=WeatherResponse)
async def get_weather_forecast_standalone(
    weather_request: WeatherRequest,
    # current_user: TokenData = Depends(get_current_user),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get weather forecast for specific coordinates (standalone endpoint)

    Args:
        weather_request: Weather request with coordinates and days
        current_user: Authenticated user
        weather_service: Weather service

    Returns:
        Weather forecast data
    """
    try:
        # Get weather forecast
        weather_data = await weather_service.get_forecast(
            city=weather_request.city,
            days=weather_request.days
        )

        return WeatherResponse(
            success=True,
            data=weather_data,
            location=weather_data.get("location"),
            forecast_days=weather_request.days
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")


@router.post("/{trip_id}/poi")
async def get_points_of_interest(
    trip_id: str,
    current_user: TokenData = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Get points of interest for trip destination

    Args:
        trip_id: Trip ID
        current_user: Authenticated user
        supabase: Supabase service

    Returns:
        List of points of interest
    """
    # TODO: Implement POI discovery
    raise HTTPException(
        status_code=501,
        detail="POI discovery not yet implemented"
    )


@router.post("/{trip_id}/events")
async def get_local_events(
    trip_id: str,
    current_user: TokenData = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Get local events during trip dates

    Args:
        trip_id: Trip ID
        current_user: Authenticated user
        supabase: Supabase service

    Returns:
        List of local events
    """
    # TODO: Implement events API integration
    raise HTTPException(
        status_code=501,
        detail="Events search not yet implemented"
    )


@router.put("/{trip_id}/customize")
async def customize_itinerary(
    trip_id: str,
    customization: dict,
    current_user: TokenData = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_dep)
):
    """
    Customize trip itinerary

    Args:
        trip_id: Trip ID
        customization: Customization request
        current_user: Authenticated user
        supabase: Supabase service

    Returns:
        Updated trip plan
    """
    # TODO: Implement itinerary customization
    raise HTTPException(
        status_code=501,
        detail="Itinerary customization not yet implemented"
    )
from app.prompts.loader import get_prompt_loader

@router.get("/technical-details")
async def get_technical_details(
    destination: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get technical details for a destination
    """
    print(f"Getting technical details for {destination}")
    prompt_loader = get_prompt_loader()

    return prompt_loader.load_template(
        module="planning",
        prompt_name="location_technical_details",
        destination=destination
    )