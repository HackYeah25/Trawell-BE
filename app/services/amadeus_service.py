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

        result = await self._make_request(
            "GET", "/v2/shopping/flight-offers", params=params
        )

        offers = result.get("data", []) or []
        summary: List[Dict[str, Any]] = []
        for offer in offers:
            price_info = offer.get("price", {}) or {}
            itineraries_out: List[Dict[str, Any]] = []
            for itin in offer.get("itineraries", []) or []:
                seg_out: List[Dict[str, Any]] = []
                for seg in itin.get("segments", []) or []:
                    dep = seg.get("departure", {}) or {}
                    arr = seg.get("arrival", {}) or {}
                    seg_out.append({
                        "from": dep.get("iataCode"),
                        "to": arr.get("iataCode"),
                        "departureAt": dep.get("at"),
                        "arrivalAt": arr.get("at"),
                        "duration": seg.get("duration"),
                    })
                itineraries_out.append({
                    "totalDuration": itin.get("duration"),
                    "segments": seg_out,
                })
            summary.append({
                "price": price_info.get("total"),
                "currency": price_info.get("currency") or price_info.get("currencyCode"),
                "itineraries": itineraries_out,
            })

        def _price_to_float(p):
            try:
                return float(p)
            except Exception:
                return float("inf")

        summary_sorted = sorted(summary, key=lambda x: _price_to_float(x.get("price")))
        result["summary"] = summary_sorted
        if summary_sorted:
            result["cheapest"] = summary_sorted[0]
        return result

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

    async def get_hotel_offers_for_city(
        self,
        city_code: str,
        check_in_date: str,
        check_out_date: str,
        adults: int = 1,
        room_quantity: int = 1,
        radius: int = 5,
        radius_unit: str = "KM",
        max_hotels: int = 10,
    ) -> Dict[str, Any]:
        """Fetch hotels by city, then retrieve offers for those hotels and return a summary.

        Summary format:
        {
          "count": number,
          "results": [
            { "hotelId": str, "name": str | None, "offers": [ { "price": str | None, "currency": str | None, "checkInDate": str | None, "checkOutDate": str | None } ] }
          ]
        }
        """
        hotels_resp = await self.search_hotels_by_city(
            city_code=city_code, radius=radius, radius_unit=radius_unit
        )

        hotel_rows = hotels_resp.get("data", []) or []
        hotel_ids: List[str] = []

        for h in hotel_rows:
            hid = h.get("hotelId") or (h.get("hotel", {}) or {}).get("hotelId")
            if isinstance(hid, str):
                hotel_ids.append(hid)

        # Deduplicate and cap
        seen = set()
        unique_ids: List[str] = []
        for hid in hotel_ids:
            if hid not in seen:
                seen.add(hid)
                unique_ids.append(hid)
            if len(unique_ids) >= max_hotels:
                break

        if not unique_ids:
            return {"count": 0, "results": []}

        offers_resp = await self.search_hotel_offers(
            hotel_ids=unique_ids,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
            room_quantity=room_quantity,
        )

        results = []
        for item in offers_resp.get("data", []) or []:
            hotel = item.get("hotel", {}) or {}
            offers_list = item.get("offers", []) or []
            simplified_offers = []
            for off in offers_list:
                price = (off.get("price", {}) or {}).get("total")
                currency = (off.get("price", {}) or {}).get("currency")
                simplified_offers.append({
                    "price": price,
                    "currency": currency,
                    "checkInDate": off.get("checkInDate"),
                    "checkOutDate": off.get("checkOutDate"),
                })
            # Sort offers for each hotel by cheapest first
            def _offer_price_to_float(x):
                try:
                    return float(x.get("price")) if x.get("price") is not None else float("inf")
                except Exception:
                    return float("inf")

            simplified_offers_sorted = sorted(simplified_offers, key=_offer_price_to_float)

            results.append({
                "hotelId": hotel.get("hotelId"),
                "name": hotel.get("name"),
                "offers": simplified_offers_sorted,
                "cheapest": simplified_offers_sorted[0] if simplified_offers_sorted else None,
            })

        # Sort hotels by their cheapest offer price and expose overall cheapest
        def _hotel_min_price(h):
            ch = h.get("cheapest") or {}
            try:
                return float(ch.get("price")) if ch.get("price") is not None else float("inf")
            except Exception:
                return float("inf")

        results_sorted = sorted(results, key=_hotel_min_price)
        return {
            "count": len(results_sorted),
            "results": results_sorted,
            "cheapest": results_sorted[0] if results_sorted else None,
        }

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


if __name__ == "__main__":
    import asyncio
    import json

    async def _test_search_flights():
        """Basic manual test for search_flights()."""
        try:
            svc = AmadeusService()  # uses settings for credentials
            dep_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            result = await svc.search_flights(
                origin="JFK",
                destination="LAX",
                departure_date=dep_date,
                adults=1,
                nonstop=True,
                max_results=5,
            )
            print(json.dumps({
                "cheapest": result.get("cheapest"),
                "count": len(result.get("summary", [])),
            }, indent=2))
        except Exception as e:
            print({
                "status": "error",
                "error": str(e),
            })

    async def _test_search_hotels_by_city():
        """Basic manual test for fetching hotel offers by city."""
        try:
            svc = AmadeusService()  # uses settings for credentials
            check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            check_out = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")
            result = await svc.get_hotel_offers_for_city(
                city_code="PAR",
                check_in_date=check_in,
                check_out_date=check_out,
                adults=2,
                room_quantity=1,
                radius=3,
                radius_unit="KM",
                max_hotels=5,
            )
            print(json.dumps(result, indent=2))
        except Exception as e:
            print({
                "status": "error",
                "error": str(e),
            })

    async def _main():
        await _test_search_flights()
        await _test_search_hotels_by_city()

    asyncio.run(_main())
