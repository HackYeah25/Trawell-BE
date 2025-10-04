"""
Amadeus API Service for flight and hotel bookings
https://developers.amadeus.com/self-service/apis-docs
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
from app.config import settings


class AmadeusAPIError(Exception):
    """Custom exception for Amadeus API errors"""
    pass


class AmadeusService:
    """Service for interacting with Amadeus Travel APIs"""

    # API Base URLs
    TEST_BASE_URL = "https://test.api.amadeus.com"
    PROD_BASE_URL = "https://api.amadeus.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        test_mode: bool = True
    ):
        """
        Initialize Amadeus service

        Args:
            api_key: Amadeus API key (defaults to settings)
            api_secret: Amadeus API secret (defaults to settings)
            test_mode: Use test environment (default: True)
        """
        self.api_key = api_key or settings.amadeus_api_key
        self.api_secret = api_secret or settings.amadeus_api_secret
        self.base_url = self.TEST_BASE_URL if test_mode else self.PROD_BASE_URL

        if not self.api_key or not self.api_secret:
            raise AmadeusAPIError("Amadeus API credentials not configured")

        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def _get_access_token(self) -> str:
        """
        Get OAuth access token using client credentials flow

        Returns:
            Access token string
        """
        # Return cached token if still valid
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token

        # Request new token
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/security/oauth2/token",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.api_key,
                        "client_secret": self.api_secret,
                    },
                )
                response.raise_for_status()
                data = response.json()

                self._access_token = data["access_token"]
                # Token expires in seconds, set expiry with 60s buffer
                expires_in = data.get("expires_in", 1799)
                self._token_expires_at = datetime.now() + timedelta(
                    seconds=expires_in - 60
                )

                return self._access_token

            except httpx.HTTPStatusError as e:
                raise AmadeusAPIError(
                    f"Failed to get access token: {e.response.status_code} - {e.response.text}"
                )
            except Exception as e:
                raise AmadeusAPIError(f"Authentication error: {str(e)}")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Amadeus API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body data

        Returns:
            Response data as dictionary
        """
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=f"{self.base_url}{endpoint}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    params=params,
                    json=json_data,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise AmadeusAPIError(
                    f"API request failed: {e.response.status_code} - {e.response.text}"
                )
            except Exception as e:
                raise AmadeusAPIError(f"Request error: {str(e)}")

    # ============================================================================
    # FLIGHT APIs
    # ============================================================================

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        adults: int = 1,
        return_date: Optional[str] = None,
        travel_class: Optional[str] = None,
        nonstop: bool = False,
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """
        Search for flight offers

        Args:
            origin: Origin airport code (e.g., 'JFK')
            destination: Destination airport code (e.g., 'LAX')
            departure_date: Departure date in YYYY-MM-DD format
            adults: Number of adult passengers (default: 1)
            return_date: Return date for round-trip (optional)
            travel_class: Travel class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
            nonstop: Only return nonstop flights
            max_results: Maximum number of results (default: 10)

        Returns:
            Flight offers data
        """
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "max": max_results,
        }

        if return_date:
            params["returnDate"] = return_date

        if travel_class:
            params["travelClass"] = travel_class

        if nonstop:
            params["nonStop"] = "true"

        return await self._make_request(
            "GET", "/v2/shopping/flight-offers", params=params
        )

    async def get_flight_price(
        self, flight_offers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Confirm pricing for flight offers

        Args:
            flight_offers: List of flight offer objects from search

        Returns:
            Confirmed pricing data
        """
        return await self._make_request(
            "POST",
            "/v1/shopping/flight-offers/pricing",
            json_data={"data": {"type": "flight-offers-pricing", "flightOffers": flight_offers}},
        )

    async def search_flight_destinations(
        self, origin: str, max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Find the cheapest destinations from an origin

        Args:
            origin: Origin airport code
            max_results: Maximum number of results

        Returns:
            Flight destination data
        """
        return await self._make_request(
            "GET",
            "/v1/shopping/flight-destinations",
            params={"origin": origin, "max": max_results},
        )

    async def search_flight_dates(
        self, origin: str, destination: str
    ) -> Dict[str, Any]:
        """
        Find cheapest flight dates for a route

        Args:
            origin: Origin airport code
            destination: Destination airport code

        Returns:
            Flight date pricing data
        """
        return await self._make_request(
            "GET",
            "/v1/shopping/flight-dates",
            params={"origin": origin, "destination": destination},
        )

    # ============================================================================
    # HOTEL APIs
    # ============================================================================

    async def search_hotels_by_city(
        self, city_code: str, radius: int = 5, radius_unit: str = "KM"
    ) -> Dict[str, Any]:
        """
        Search for hotels in a city

        Args:
            city_code: IATA city code (e.g., 'PAR' for Paris)
            radius: Search radius (default: 5)
            radius_unit: Unit of radius (KM or MILE, default: KM)

        Returns:
            Hotel list data
        """
        return await self._make_request(
            "GET",
            "/v1/reference-data/locations/hotels/by-city",
            params={"cityCode": city_code, "radius": radius, "radiusUnit": radius_unit},
        )

    async def search_hotel_offers(
        self,
        hotel_ids: List[str],
        check_in_date: str,
        check_out_date: str,
        adults: int = 1,
        room_quantity: int = 1,
    ) -> Dict[str, Any]:
        """
        Search for hotel offers

        Args:
            hotel_ids: List of Amadeus hotel IDs
            check_in_date: Check-in date (YYYY-MM-DD)
            check_out_date: Check-out date (YYYY-MM-DD)
            adults: Number of adults (default: 1)
            room_quantity: Number of rooms (default: 1)

        Returns:
            Hotel offers data
        """
        return await self._make_request(
            "GET",
            "/v3/shopping/hotel-offers",
            params={
                "hotelIds": ",".join(hotel_ids),
                "checkInDate": check_in_date,
                "checkOutDate": check_out_date,
                "adults": adults,
                "roomQuantity": room_quantity,
            },
        )

    async def get_hotel_offer(self, offer_id: str) -> Dict[str, Any]:
        """
        Get detailed hotel offer by ID

        Args:
            offer_id: Hotel offer ID

        Returns:
            Hotel offer details
        """
        return await self._make_request("GET", f"/v3/shopping/hotel-offers/{offer_id}")

    # ============================================================================
    # LOCATION APIs
    # ============================================================================

    async def search_locations(
        self,
        keyword: str,
        subtype: Optional[str] = None,
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """
        Search for locations (airports, cities, etc.)

        Args:
            keyword: Search keyword
            subtype: Location subtype (AIRPORT, CITY, etc.)
            max_results: Maximum results (default: 10)

        Returns:
            Location search results
        """
        params = {"keyword": keyword, "page[limit]": max_results}

        if subtype:
            params["subType"] = subtype

        return await self._make_request(
            "GET", "/v1/reference-data/locations", params=params
        )

    async def get_airport_info(self, airport_code: str) -> Dict[str, Any]:
        """
        Get airport information by IATA code

        Args:
            airport_code: IATA airport code (e.g., 'JFK')

        Returns:
            Airport details
        """
        return await self._make_request(
            "GET", f"/v1/reference-data/locations/{airport_code}"
        )

    # ============================================================================
    # TRIP PURPOSE PREDICTION
    # ============================================================================

    async def predict_trip_purpose(
        self, origin: str, destination: str, departure_date: str, return_date: str
    ) -> Dict[str, Any]:
        """
        Predict if trip is for business or leisure

        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date (YYYY-MM-DD)

        Returns:
            Trip purpose prediction
        """
        return await self._make_request(
            "GET",
            "/v1/travel/predictions/trip-purpose",
            params={
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": departure_date,
                "returnDate": return_date,
            },
        )


# Global service instance
amadeus_service = AmadeusService()
