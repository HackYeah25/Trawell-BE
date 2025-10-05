"""
Destination and recommendation data models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class RecommendationStatus(str, Enum):
    SUGGESTED = "suggested"
    DETAILS_GENERATED = "details_generated"
    DETAILS_COMPLETED = "details_completed"

class Rating(str, Enum):
    ZERO_STARS = "0"
    ONE_STAR = "1"
    TWO_STARS = "2"
    THREE_STARS = "3"

class DealType(str, Enum):
    """Types of deals available"""
    FLIGHT = "flight"
    HOTEL = "hotel"
    PACKAGE = "package"
    TRANSPORT = "transport"

class ActivityCategory(str, Enum):
    """Categories of activities"""
    CULTURAL = "cultural"
    OUTDOOR = "outdoor"
    FOOD = "food"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    RELAXATION = "relaxation"
    ADVENTURE = "adventure"
    HISTORICAL = "historical"

class Coordinates(BaseModel):
    """Geographic coordinates"""
    lat: float
    lng: float

class DestinationInfo(BaseModel):
    """Destination information"""
    name: str # highlight activity in this destination
    city: str
    country: str
    region: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    description: Optional[str] = None

class Deal(BaseModel):
    """Flight or accommodation deal"""
    deal_id: str
    type: str  # "flight", "hotel", "package"
    price: float
    currency: str = "USD"
    provider: str
    highlighted: bool = False
    valid_from: datetime
    valid_until: datetime
    url: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class WeatherInformation(BaseModel):
    """Weather information"""
    temperature: float
    weather_description: str
    humidity: float
    wind_speed: float
    optimal_season: Optional[str] = None

class Activity(BaseModel):
    """Activity"""
    name: str
    description: str
    category: ActivityCategory = Field(..., description="Activity category")
    location: Optional[Coordinates] = None
    highlighted: bool = False
    url: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class DestinationDetails(BaseModel):
    """Destination details"""
    reasoning: str
    weather: Optional[WeatherInformation] = None
    estimated_cost: Optional[float] = None # null when no deals found
    currency: str = "USD"
    deals_found: List[Deal] = Field(default_factory=list)
    activities: List[Activity] = Field(default_factory=list)
    status: RecommendationStatus = RecommendationStatus.SUGGESTED
    confidence_score: Optional[float] = None
    travel_tips: List[str] = Field(default_factory=list)

class DestinationRecommendation(BaseModel):
    """AI-generated destination recommendation"""
    recommendation_id: UUID
    user_id: str
    destination: DestinationInfo
    rating: Optional[Rating] = None
    details: Optional[DestinationDetails] = None # this is filled when we want to go there
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "recommendation_id": "rec_123",
                "user_id": "user_456",
                "destination": {
                    "name": "Lisbon",
                    "country": "Portugal",
                    "region": "Western Europe",
                    "coordinates": {"lat": 38.7223, "lng": -9.1393}
                },
                "reasoning": "Perfect match for your love of culture, food, and city exploration",
                "optimal_season": "April-June, September-October",
                "estimated_budget": 1500,
                "currency": "USD",
                "highlights": [
                    "Historic neighborhoods like Alfama and Belém",
                    "World-class seafood and pastéis de nata",
                    "Vibrant street art and music scene"
                ],
                "status": "suggested"
            }
        }


class BrainstormRequest(BaseModel):
    """Request for destination brainstorming"""
    user_id: str
    budget_range: Optional[tuple[float, float]] = None
    travel_dates: Optional[tuple[datetime, datetime]] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)
    group_mode: bool = False
    group_participants: List[str] = Field(default_factory=list)


class BrainstormResponse(BaseModel):
    """Response from brainstorm endpoint"""
    session_id: str
    recommendations: List[DestinationRecommendation]
    conversation_id: str
    message: str
