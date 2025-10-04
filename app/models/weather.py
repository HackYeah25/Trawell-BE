"""
Weather data models
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class WeatherCondition(BaseModel):
    """Weather condition details"""
    text: str
    icon: str
    code: int


class WeatherLocation(BaseModel):
    """Location information"""
    name: str
    region: str
    country: str
    latitude: float
    longitude: float
    timezone: str


class CurrentWeather(BaseModel):
    """Current weather data"""
    temperature_c: float
    temperature_f: float
    condition: WeatherCondition
    humidity: int
    wind_kph: float
    wind_mph: float
    wind_direction: str
    pressure_mb: float
    pressure_in: float
    precipitation_mm: float
    uv_index: float
    feels_like_c: float
    feels_like_f: float
    visibility_km: float
    last_updated: str


class HourlyWeather(BaseModel):
    """Hourly weather forecast"""
    time: str
    temperature_c: float
    temperature_f: float
    condition: WeatherCondition
    humidity: int
    wind_kph: float
    wind_mph: float
    precipitation_mm: float
    chance_of_rain: int
    chance_of_snow: int


class DailyWeather(BaseModel):
    """Daily weather forecast"""
    date: str
    max_temp_c: float
    max_temp_f: float
    min_temp_c: float
    min_temp_f: float
    avg_temp_c: float
    avg_temp_f: float
    condition: WeatherCondition
    humidity: int
    wind_kph: float
    wind_mph: float
    precipitation_mm: float
    precipitation_in: float
    uv_index: float
    chance_of_rain: int
    chance_of_snow: int
    hourly: List[HourlyWeather] = []


class WeatherForecast(BaseModel):
    """Complete weather forecast"""
    location: WeatherLocation
    current: CurrentWeather
    forecast: Dict[str, List[DailyWeather]]
    alerts: List[Dict[str, Any]] = []
    air_quality: Dict[str, Any] = {}
    last_updated: str


class WeatherRequest(BaseModel):
    """Weather API request parameters"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    days: int = Field(default=7, ge=1, le=10, description="Number of days to forecast (1-10)")
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v


class WeatherResponse(BaseModel):
    """Weather API response"""
    success: bool
    data: Optional[WeatherForecast] = None
    error: Optional[str] = None
    location: Optional[WeatherLocation] = None
    coordinates: Optional[Dict[str, float]] = None
    forecast_days: Optional[int] = None
