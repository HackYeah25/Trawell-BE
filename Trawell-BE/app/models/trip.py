"""
Trip planning data models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from app.models.destination import DestinationInfo, Coordinates


class TripStatus(str, Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    BOOKED = "booked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Weather(BaseModel):
    """Weather forecast"""
    date: datetime
    temperature_high: float
    temperature_low: float
    conditions: str
    precipitation_chance: float
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None


class PointOfInterest(BaseModel):
    """Point of interest / attraction"""
    name: str
    category: str  # museum, restaurant, landmark, etc.
    coordinates: Optional[Coordinates] = None
    description: Optional[str] = None
    opening_hours: Optional[str] = None
    ticket_price: Optional[float] = None
    estimated_duration: Optional[str] = None  # "2-3 hours"
    rating: Optional[float] = None
    tips: List[str] = Field(default_factory=list)


class LocalEvent(BaseModel):
    """Local event (concert, festival, etc.)"""
    name: str
    type: str  # concert, festival, sports, etc.
    date: datetime
    location: str
    coordinates: Optional[Coordinates] = None
    description: Optional[str] = None
    ticket_price: Optional[float] = None
    url: Optional[str] = None


class CulturalInfo(BaseModel):
    """Cultural considerations"""
    dress_code: List[str] = Field(default_factory=list)
    customs: List[str] = Field(default_factory=list)
    vaccination_requirements: List[str] = Field(default_factory=list)
    visa_requirements: Optional[str] = None
    language_tips: List[str] = Field(default_factory=list)
    emergency_numbers: Dict[str, str] = Field(default_factory=dict)


class DayItinerary(BaseModel):
    """Single day itinerary"""
    day: int
    date: datetime
    activities: List[PointOfInterest] = Field(default_factory=list)
    weather: Optional[Weather] = None
    notes: Optional[str] = None


class TripPlan(BaseModel):
    """Complete trip plan"""
    trip_id: str
    user_id: str
    destination: DestinationInfo
    start_date: datetime
    end_date: datetime
    status: TripStatus = TripStatus.DRAFT

    # Planning details
    weather_forecast: List[Weather] = Field(default_factory=list)
    cultural_info: Optional[CulturalInfo] = None
    points_of_interest: List[PointOfInterest] = Field(default_factory=list)
    local_events: List[LocalEvent] = Field(default_factory=list)
    daily_itinerary: List[DayItinerary] = Field(default_factory=list)

    # Metadata
    estimated_budget: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "trip_id": "trip_123",
                "user_id": "user_456",
                "destination": {
                    "name": "Lisbon",
                    "country": "Portugal"
                },
                "start_date": "2024-05-01T00:00:00Z",
                "end_date": "2024-05-07T00:00:00Z",
                "status": "planned"
            }
        }


class TripCreate(BaseModel):
    """Create new trip plan"""
    user_id: str
    destination: DestinationInfo
    start_date: datetime
    end_date: datetime
    budget: Optional[float] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)


class FlightSearch(BaseModel):
    """Flight search request"""
    origin: str
    destination: str
    departure_date: datetime
    return_date: Optional[datetime] = None
    passengers: int = 1
    cabin_class: str = "economy"


class FlightResult(BaseModel):
    """Flight search result"""
    airline: str
    flight_number: str
    departure: datetime
    arrival: datetime
    duration: str
    price: float
    currency: str = "USD"
    stops: int = 0
    booking_url: Optional[str] = None
