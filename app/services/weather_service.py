"""
Weather API service using WeatherAPI.com
"""
import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.config import settings

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for weather data from WeatherAPI.com"""

    def __init__(self):
        self.api_key = settings.weather_api_key
        self.base_url = "http://api.weatherapi.com/v1"
        
    async def get_forecast(
        self, 
        latitude: float, 
        longitude: float, 
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get weather forecast for specific coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate  
            days: Number of days to forecast (1-10)
            
        Returns:
            Weather forecast data
        """
        if not self.api_key:
            raise ValueError("Weather API key not configured")
            
        if not (1 <= days <= 10):
            raise ValueError("Days must be between 1 and 10")
            
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/forecast.json"
                params = {
                    "key": self.api_key,
                    "q": f"{latitude},{longitude}",
                    "days": days,
                    "aqi": "yes",  # Air quality index
                    "alerts": "yes"  # Weather alerts
                }
                
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                
                # Transform the response to our format
                return self._transform_forecast_data(data)
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise ValueError(f"Invalid request: {e.response.text}")
            elif e.response.status_code == 401:
                raise ValueError("Invalid API key")
            elif e.response.status_code == 403:
                raise ValueError("API key quota exceeded")
            else:
                raise ValueError(f"Weather API error: {e.response.status_code}")
        except httpx.TimeoutException:
            raise ValueError("Weather API request timed out")
        except Exception as e:
            logger.error(f"Weather API request failed: {e}")
            raise ValueError(f"Failed to fetch weather data: {str(e)}")
    
    def _transform_forecast_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform WeatherAPI response to our format"""
        
        location = data.get("location", {})
        current = data.get("current", {})
        forecast = data.get("forecast", {})
        
        return {
            "location": {
                "name": location.get("name"),
                "region": location.get("region"),
                "country": location.get("country"),
                "latitude": location.get("lat"),
                "longitude": location.get("lon"),
                "timezone": location.get("tz_id")
            },
            "current": {
                "temperature_c": current.get("temp_c"),
                "temperature_f": current.get("temp_f"),
                "condition": {
                    "text": current.get("condition", {}).get("text"),
                    "icon": current.get("condition", {}).get("icon"),
                    "code": current.get("condition", {}).get("code")
                },
                "humidity": current.get("humidity"),
                "wind_kph": current.get("wind_kph"),
                "wind_mph": current.get("wind_mph"),
                "wind_direction": current.get("wind_dir"),
                "pressure_mb": current.get("pressure_mb"),
                "pressure_in": current.get("pressure_in"),
                "precipitation_mm": current.get("precip_mm"),
                "uv_index": current.get("uv"),
                "feels_like_c": current.get("feelslike_c"),
                "feels_like_f": current.get("feelslike_f"),
                "visibility_km": current.get("vis_km"),
                "last_updated": current.get("last_updated")
            },
            "forecast": {
                "days": [
                    {
                        "date": day.get("date"),
                        "max_temp_c": day.get("day", {}).get("maxtemp_c"),
                        "max_temp_f": day.get("day", {}).get("maxtemp_f"),
                        "min_temp_c": day.get("day", {}).get("mintemp_c"),
                        "min_temp_f": day.get("day", {}).get("mintemp_f"),
                        "avg_temp_c": day.get("day", {}).get("avgtemp_c"),
                        "avg_temp_f": day.get("day", {}).get("avgtemp_f"),
                        "condition": {
                            "text": day.get("day", {}).get("condition", {}).get("text"),
                            "icon": day.get("day", {}).get("condition", {}).get("icon"),
                            "code": day.get("day", {}).get("condition", {}).get("code")
                        },
                        "humidity": day.get("day", {}).get("avghumidity"),
                        "wind_kph": day.get("day", {}).get("maxwind_kph"),
                        "wind_mph": day.get("day", {}).get("maxwind_mph"),
                        "precipitation_mm": day.get("day", {}).get("totalprecip_mm"),
                        "precipitation_in": day.get("day", {}).get("totalprecip_in"),
                        "uv_index": day.get("day", {}).get("uv"),
                        "chance_of_rain": day.get("day", {}).get("daily_chance_of_rain"),
                        "chance_of_snow": day.get("day", {}).get("daily_chance_of_snow"),
                        "hourly": [
                            {
                                "time": hour.get("time"),
                                "temperature_c": hour.get("temp_c"),
                                "temperature_f": hour.get("temp_f"),
                                "condition": {
                                    "text": hour.get("condition", {}).get("text"),
                                    "icon": hour.get("condition", {}).get("icon"),
                                    "code": hour.get("condition", {}).get("code")
                                },
                                "humidity": hour.get("humidity"),
                                "wind_kph": hour.get("wind_kph"),
                                "wind_mph": hour.get("wind_mph"),
                                "precipitation_mm": hour.get("precip_mm"),
                                "chance_of_rain": hour.get("chance_of_rain"),
                                "chance_of_snow": hour.get("chance_of_snow")
                            }
                            for hour in day.get("hour", [])
                        ]
                    }
                    for day in forecast.get("forecastday", [])
                ]
            },
            "alerts": data.get("alerts", {}).get("alert", []),
            "air_quality": current.get("air_quality", {}),
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_current_weather(
        self, 
        latitude: float, 
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get current weather for specific coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Current weather data
        """
        if not self.api_key:
            raise ValueError("Weather API key not configured")
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/current.json"
                params = {
                    "key": self.api_key,
                    "q": f"{latitude},{longitude}",
                    "aqi": "yes"
                }
                
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract just current weather
                location = data.get("location", {})
                current = data.get("current", {})
                
                return {
                    "location": {
                        "name": location.get("name"),
                        "region": location.get("region"),
                        "country": location.get("country"),
                        "latitude": location.get("lat"),
                        "longitude": location.get("lon"),
                        "timezone": location.get("tz_id")
                    },
                    "current": {
                        "temperature_c": current.get("temp_c"),
                        "temperature_f": current.get("temp_f"),
                        "condition": {
                            "text": current.get("condition", {}).get("text"),
                            "icon": current.get("condition", {}).get("icon"),
                            "code": current.get("condition", {}).get("code")
                        },
                        "humidity": current.get("humidity"),
                        "wind_kph": current.get("wind_kph"),
                        "wind_mph": current.get("wind_mph"),
                        "wind_direction": current.get("wind_dir"),
                        "pressure_mb": current.get("pressure_mb"),
                        "pressure_in": current.get("pressure_in"),
                        "precipitation_mm": current.get("precip_mm"),
                        "uv_index": current.get("uv"),
                        "feels_like_c": current.get("feelslike_c"),
                        "feels_like_f": current.get("feelslike_f"),
                        "visibility_km": current.get("vis_km"),
                        "last_updated": current.get("last_updated")
                    },
                    "air_quality": current.get("air_quality", {}),
                    "last_updated": datetime.now().isoformat()
                }
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise ValueError(f"Invalid request: {e.response.text}")
            elif e.response.status_code == 401:
                raise ValueError("Invalid API key")
            elif e.response.status_code == 403:
                raise ValueError("API key quota exceeded")
            else:
                raise ValueError(f"Weather API error: {e.response.status_code}")
        except httpx.TimeoutException:
            raise ValueError("Weather API request timed out")
        except Exception as e:
            logger.error(f"Weather API request failed: {e}")
            raise ValueError(f"Failed to fetch weather data: {str(e)}")


# Global instance
weather_service = WeatherService()


def get_weather_service() -> WeatherService:
    """Get weather service instance"""
    return weather_service
