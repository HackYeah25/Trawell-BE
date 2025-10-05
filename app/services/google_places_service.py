"""
Google Places Service
Handles place search and photo retrieval using Google Places API
"""
import httpx
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from app.config import settings


@dataclass
class PlacePhoto:
    """Represents a place photo with metadata"""
    name: str
    photo_uri: str
    width_px: Optional[int] = None
    height_px: Optional[int] = None


@dataclass
class PlaceInfo:
    """Represents place information"""
    place_id: str
    name: str
    formatted_address: str
    location: Dict[str, float]  # lat, lng
    rating: Optional[float] = None
    user_rating_count: Optional[int] = None
    photos: Optional[List[PlacePhoto]] = None


class GooglePlacesService:
    """Service for interacting with Google Places API"""
    
    def __init__(self):
        self.api_key = settings.google_maps_api_key
        self.base_url = "https://places.googleapis.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.photos"
        }
    
    async def search_place(self, query: str) -> Optional[PlaceInfo]:
        """
        Search for a place using text query
        
        Args:
            query: Text query to search for
            location_bias: Optional location bias dict with 'latitude' and 'longitude'
            
        Returns:
            PlaceInfo object or None if not found
        """
        try:
            # Prepare request payload
            payload = {
                "textQuery": query,
                "maxResultCount": 1,
                "languageCode": "en"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/places:searchText",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                if not data.get("places"):
                    return None
                
                place_data = data["places"][0]
                return self._parse_place_data(place_data)
                
        except httpx.HTTPError as e:
            print(f"HTTP error in place search: {e}")
            return None
        except Exception as e:
            print(f"Error in place search: {e}")
            return None
    
    async def get_place_photo(self, photo_name: str, max_width: int = 800, max_height: int = 1600) -> Optional[PlacePhoto]:
        """
        Get photo information and URI

        Args:
            photo_name: Name of the photo from place data
            max_width: Maximum width for the photo
            max_height: Maximum height for the photo

        Returns:
            PlacePhoto object with direct photo URL
        """
        try:
            params = {
                "key": self.api_key,
                "maxWidthPx": max_width,
                "maxHeightPx": max_height
            }

            # Follow redirects to get the actual photo URL
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(
                    f"{self.base_url}/{photo_name}/media",
                    params=params,
                    timeout=30.0
                )

                # The final URL after redirects IS the photo URL
                photo_url = str(response.url)

                return PlacePhoto(
                    name=photo_name,
                    photo_uri=photo_url,
                    width_px=max_width,
                    height_px=max_height,
                )

        except httpx.HTTPError as e:
            print(f"HTTP error getting photo: {e}")
            return None
        except Exception as e:
            print(f"Error getting photo: {e}")
            return None
    
    async def search_place_with_photo(self, query: str) -> Optional[PlaceInfo]:
        """
        Search for a place and get its first photo
        
        Args:
            query: Text query to search for
            location_bias: Optional location bias dict with 'latitude' and 'longitude'
            
        Returns:
            PlaceInfo object with photo or None if not found
        """
        # First, search for the place
        place_info = await self.search_place(query)
        
        if not place_info or not place_info.photos:
            return place_info
        
        # Get the first photo
        first_photo = place_info.photos[0]
        photo_details = await self.get_place_photo(first_photo.name)
        
        if photo_details:
            # Update the photo with detailed information
            place_info.photos[0] = photo_details
        
        return place_info
    
    def _parse_place_data(self, place_data: Dict[str, Any]) -> PlaceInfo:
        """Parse place data from API response"""
        photos = []
        if "photos" in place_data:
            for photo_data in place_data["photos"]:
                photos.append(PlacePhoto(
                    name=photo_data.get("name", ""),
                    photo_uri="",  # Will be filled when we get photo details
                    width_px=photo_data.get("widthPx"),
                    height_px=photo_data.get("heightPx"),
                ))
        
        location = {}
        if "location" in place_data:
            location = {
                "latitude": place_data["location"].get("latitude", 0.0),
                "longitude": place_data["location"].get("longitude", 0.0)
            }
        
        return PlaceInfo(
            place_id=place_data.get("id", ""),
            name=place_data.get("displayName", {}).get("text", ""),
            formatted_address=place_data.get("formattedAddress", ""),
            location=location,
            rating=place_data.get("rating"),
            user_rating_count=place_data.get("userRatingCount"),
            photos=photos if photos else None
        )


# Convenience function for easy usage
async def search_place_with_photo(query: str) -> Optional[PlaceInfo]:
    """
    Convenience function to search for a place and get its photo
    
    Args:
        query: Text query to search for
        location_bias: Optional location bias dict with 'latitude' and 'longitude'
        
    Returns:
        PlaceInfo object with photo or None if not found
    """
    service = GooglePlacesService()
    return await service.search_place_with_photo(query)
