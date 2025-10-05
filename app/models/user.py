"""
User and Profile data models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class TravelerType(str, Enum):
    EXPLORER = "explorer"
    RELAXER = "relaxer"
    MIXED = "mixed"


class ActivityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AccommodationStyle(str, Enum):
    ALL_INCLUSIVE = "all_inclusive"
    BOUTIQUE = "boutique"
    HOSTEL = "hostel"
    MIXED = "mixed"


class Environment(str, Enum):
    CITY = "city"
    NATURE = "nature"
    BEACH = "beach"
    MOUNTAINS = "mountains"
    MIXED = "mixed"


class InterestLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserPreferences(BaseModel):
    """User travel preferences"""
    traveler_type: TravelerType = TravelerType.MIXED
    activity_level: ActivityLevel = ActivityLevel.MEDIUM
    accommodation_style: AccommodationStyle = AccommodationStyle.MIXED
    environment: Environment = Environment.MIXED
    budget_sensitivity: InterestLevel = InterestLevel.MEDIUM
    culture_interest: InterestLevel = InterestLevel.MEDIUM
    food_importance: InterestLevel = InterestLevel.MEDIUM


class UserConstraints(BaseModel):
    """User constraints and requirements"""
    dietary_restrictions: List[str] = Field(default_factory=list)
    mobility_limitations: List[str] = Field(default_factory=list)
    climate_preferences: List[str] = Field(default_factory=list)
    language_preferences: List[str] = Field(default_factory=list)


class UserProfile(BaseModel):
    """Complete user profile"""
    user_id: str
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    constraints: UserConstraints = Field(default_factory=UserConstraints)
    past_destinations: List[str] = Field(default_factory=list)
    wishlist_regions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "preferences": {
                    "traveler_type": "explorer",
                    "activity_level": "high",
                    "accommodation_style": "boutique",
                    "environment": "mixed",
                    "budget_sensitivity": "medium",
                    "culture_interest": "high",
                    "food_importance": "high"
                },
                "constraints": {
                    "dietary_restrictions": ["vegetarian"],
                    "mobility_limitations": [],
                    "climate_preferences": ["warm", "temperate"]
                },
                "past_destinations": ["Paris", "Tokyo", "Barcelona"],
                "wishlist_regions": ["Southeast Asia", "South America"]
            }
        }


class User(BaseModel):
    """API User model aligned with frontend needs and Supabase schema"""
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    onboardingCompleted: bool = False


class UserCreate(BaseModel):
    """User registration model"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT Token model"""
    access_token: str
    token_type: str = "bearer"
    user: User


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str
