#!/usr/bin/env python3
"""
Example script showing how to use the Weather API endpoint
"""
import asyncio
import httpx
import json
from typing import Dict, Any


async def test_weather_api():
    """Test the weather API endpoint"""
    
    # API endpoint
    base_url = "http://localhost:8000"
    weather_endpoint = f"{base_url}/api/planning/weather"
    
    # Example coordinates (New York City)
    weather_request = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "days": 7
    }
    
    # Headers (you'll need a valid JWT token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"  # Replace with actual token
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("🌤️  Testing Weather API...")
            print(f"📍 Coordinates: {weather_request['latitude']}, {weather_request['longitude']}")
            print(f"📅 Days: {weather_request['days']}")
            print("-" * 50)
            
            response = await client.post(
                weather_endpoint,
                json=weather_request,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Weather API Response:")
                print(json.dumps(data, indent=2))
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
    except httpx.TimeoutException:
        print("⏰ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")


def print_usage_examples():
    """Print usage examples for the weather API"""
    
    print("🌤️  Weather API Usage Examples")
    print("=" * 50)
    
    print("\n1. Standalone Weather Endpoint:")
    print("POST /api/planning/weather")
    print("""
{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "days": 7
}
    """)
    
    print("\n2. Trip-specific Weather Endpoint:")
    print("POST /api/planning/{trip_id}/weather")
    print("""
{
    "latitude": 51.5074,
    "longitude": -0.1278,
    "days": 5
}
    """)
    
    print("\n3. Example Response:")
    print("""
{
    "success": true,
    "data": {
        "location": {
            "name": "New York",
            "region": "New York",
            "country": "United States of America",
            "latitude": 40.71,
            "longitude": -74.01,
            "timezone": "America/New_York"
        },
        "current": {
            "temperature_c": 22.0,
            "temperature_f": 71.6,
            "condition": {
                "text": "Partly cloudy",
                "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png",
                "code": 1003
            },
            "humidity": 65,
            "wind_kph": 15.0,
            "wind_mph": 9.3,
            "wind_direction": "NW",
            "pressure_mb": 1013.0,
            "pressure_in": 29.91,
            "precipitation_mm": 0.0,
            "uv_index": 6.0,
            "feels_like_c": 24.0,
            "feels_like_f": 75.2,
            "visibility_km": 10.0,
            "last_updated": "2024-01-15 14:30"
        },
        "forecast": {
            "days": [
                {
                    "date": "2024-01-15",
                    "max_temp_c": 25.0,
                    "min_temp_c": 18.0,
                    "avg_temp_c": 21.5,
                    "condition": {
                        "text": "Sunny",
                        "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                        "code": 1000
                    },
                    "humidity": 60,
                    "wind_kph": 12.0,
                    "precipitation_mm": 0.0,
                    "uv_index": 7.0,
                    "chance_of_rain": 0,
                    "chance_of_snow": 0,
                    "hourly": [...]
                }
            ]
        },
        "alerts": [],
        "air_quality": {
            "co": 0.0,
            "no2": 0.0,
            "o3": 0.0,
            "pm2_5": 0.0,
            "pm10": 0.0,
            "so2": 0.0
        },
        "last_updated": "2024-01-15T14:30:00"
    },
    "location": {...},
    "coordinates": {
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    "forecast_days": 7
}
    """)
    
    print("\n4. Required Environment Variables:")
    print("WEATHER_API_KEY=your_weatherapi_key_here")
    
    print("\n5. Error Responses:")
    print("""
400 Bad Request:
{
    "detail": "Latitude must be between -90 and 90"
}

401 Unauthorized:
{
    "detail": "Could not validate credentials"
}

500 Internal Server Error:
{
    "detail": "Weather API key not configured"
}
    """)


if __name__ == "__main__":
    print_usage_examples()
    
    # Uncomment to test the API (requires valid JWT token)
    # asyncio.run(test_weather_api())
