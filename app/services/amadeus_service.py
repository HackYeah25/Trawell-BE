"""
Amadeus API Service for flight and hotel bookings
https://developers.amadeus.com/self-service/apis-docs
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import re
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

        self._credentials_configured = bool(self.api_key and self.api_secret)

        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def _get_access_token(self) -> str:
        """
        Get OAuth access token using client credentials flow

        Returns:
            Access token string
        """
        if not self._credentials_configured:
            raise AmadeusAPIError("Amadeus API credentials not configured")
            
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
        # Helper to format ISO8601 durations like 'PT6H19M' or 'P1DT2H'
        def _format_duration(iso: Any) -> Any:
            if not isinstance(iso, str):
                return iso
            pattern = re.compile(r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?$")
            m = pattern.match(iso)
            if not m:
                return iso
            days = m.group("days")
            hours = m.group("hours")
            minutes = m.group("minutes")
            seconds = m.group("seconds")
            parts: List[str] = []
            if days:
                parts.append(f"{int(days)}d")
            if hours:
                parts.append(f"{int(hours)}h")
            if minutes:
                parts.append(f"{int(minutes)}m")
            if seconds:
                parts.append(f"{int(seconds)}s")
            return " ".join(parts) if parts else "0m"
        simplified_offers: List[Dict[str, Any]] = []
        for offer in offers:
            price_info = offer.get("price", {}) or {}
            itineraries = offer.get("itineraries", []) or []

            def build_itin(itin_obj: Dict[str, Any]) -> Dict[str, Any]:
                seg_out: List[Dict[str, Any]] = []
                for seg in itin_obj.get("segments", []) or []:
                    dep = seg.get("departure", {}) or {}
                    arr = seg.get("arrival", {}) or {}
                    seg_out.append({
                        "from": dep.get("iataCode"),
                        "to": arr.get("iataCode"),
                        "departureAt": dep.get("at"),
                        "arrivalAt": arr.get("at"),
                        "duration": _format_duration(seg.get("duration")),
                    })
                return {
                    "totalDuration": _format_duration(itin_obj.get("duration")),
                    "segments": seg_out,
                }

            outbound = build_itin(itineraries[0]) if len(itineraries) >= 1 else None
            inbound = build_itin(itineraries[1]) if len(itineraries) >= 2 else None

            simplified_offers.append({
                "price": price_info.get("total"),
                "currency": price_info.get("currency") or price_info.get("currencyCode"),
                "outbound": outbound,
                "return": inbound,
            })

        def _price_to_float(p):
            try:
                return float(p)
            except Exception:
                return float("inf")

        cheapest = min(simplified_offers, key=lambda x: _price_to_float(x.get("price"))) if simplified_offers else {}
        return cheapest

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

        # Deduplicate (search full set from response; no artificial limit)
        seen = set()
        unique_ids: List[str] = []
        for hid in hotel_ids:
            if hid not in seen:
                seen.add(hid)
                unique_ids.append(hid)

        if not unique_ids:
            return []

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

            hotel_id = hotel.get("hotelId")
            # Skip sandbox test properties like HNPARSPC
            if hotel_id == "HNPARSPC":
                continue

            cheapest_offer = simplified_offers_sorted[0] if simplified_offers_sorted else None
            if not cheapest_offer:
                continue

            # Flatten output: only name, price, currency, checkInDate, checkOutDate
            results.append({
                "name": hotel.get("name"),
                "price": cheapest_offer.get("price"),
                "currency": cheapest_offer.get("currency"),
                "checkInDate": cheapest_offer.get("checkInDate"),
                "checkOutDate": cheapest_offer.get("checkOutDate"),
            })

        # Sort hotels by their cheapest offer price and expose overall cheapest
        def _hotel_min_price(h):
            try:
                return float(h.get("price")) if h.get("price") is not None else float("inf")
            except Exception:
                return float("inf")

        results_sorted = sorted(results, key=_hotel_min_price)
        # Return just the results list (no count)
        return results_sorted

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
    # TRIP AGGREGATION
    # ============================================================================

    def get_trip_details_sync(
        self,
        destination: str,
        origin: str = "JFK",
        departure_date: Optional[str] = None,
        return_date: Optional[str] = None,
        adults: int = 1,
        travel_class: Optional[str] = None,
        nonstop: bool = True,
        hotel_radius: int = 5,
        hotel_radius_unit: str = "KM",
        room_quantity: int = 1,
    ) -> Dict[str, Any]:
        """Synchronous wrapper for get_trip_details. Returns flights and hotels."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.get_trip_details(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=adults,
                travel_class=travel_class,
                nonstop=nonstop,
                hotel_radius=hotel_radius,
                hotel_radius_unit=hotel_radius_unit,
                room_quantity=room_quantity,
            )
        )

    async def get_trip_details(
        self,
        origin: str,
        destination: str,
        departure_date: Optional[str] = None,
        return_date: Optional[str] = None,
        adults: int = 1,
        travel_class: Optional[str] = None,
        nonstop: bool = True,
        hotel_radius: int = 5,
        hotel_radius_unit: str = "KM",
        room_quantity: int = 1,
    ) -> Dict[str, Any]:
        """Get cheapest flights in both directions and hotels for those dates.

        Returns structure:
        {
          "flights": {
             "outbound": { "price", "currency", "itinerary" },
             "return": { "price", "currency", "itinerary" }
          },
          "hotels": [ { name, price, currency, checkInDate, checkOutDate }, ... ]
        }
        """
        # Pick cheapest dates using flight-dates endpoints
        def _pick_cheapest_date(dates_resp: Dict[str, Any]) -> Optional[str]:
            try:
                items = dates_resp.get("data", []) or []
                def _price_total(item: Dict[str, Any]) -> float:
                    try:
                        return float(((item.get("price") or {}).get("total")) or float("inf"))
                    except Exception:
                        return float("inf")
                best = min(items, key=_price_total) if items else None
                if not best:
                    return None
                # Prefer explicit departureDate, fallback to date keys
                date_val = best.get("departureDate") or best.get("date") or best.get("departure_date")
                return str(date_val) if date_val else None
            except Exception:
                return None

        # Helpers for resilient lookups
        def _date_str(d: datetime) -> str:
            return d.strftime("%Y-%m-%d")

        def _parse_date(d: str) -> Optional[datetime]:
            try:
                return datetime.strptime(d, "%Y-%m-%d")
            except Exception:
                return None

        async def _safe_search_flight_dates(o: str, d: str) -> Dict[str, Any]:
            try:
                return await self.search_flight_dates(origin=o, destination=d)
            except Exception:
                return {}

        async def _find_one_way_cheapest_offer(
            o: str,
            d: str,
            seed_date: str,
            pax: int,
            cls: Optional[str],
            prefer_nonstop: bool,
        ) -> Dict[str, Any]:
            """Try seed date, then nearby +/- days, and relax nonstop if needed."""
            candidate_dates: List[str] = []
            parsed = _parse_date(seed_date)
            if parsed:
                # Window: -2..+3 days
                for delta in [-2, -1, 0, 1, 2, 3]:
                    candidate_dates.append(_date_str(parsed + timedelta(days=delta)))
            else:
                candidate_dates.append(seed_date)

            async def _try_dates(nonstop_flag: bool) -> Dict[str, Any]:
                best: Dict[str, Any] = {}
                best_price = float("inf")
                for cd in candidate_dates:
                    try:
                        offer = await self.search_flights(
                            origin=o,
                            destination=d,
                            departure_date=cd,
                            adults=pax,
                            return_date=None,
                            travel_class=cls,
                            nonstop=nonstop_flag,
                        )
                        price = offer.get("price") if isinstance(offer, dict) else None
                        if price is None:
                            continue
                        try:
                            p = float(price)
                        except Exception:
                            p = float("inf")
                        if p < best_price:
                            best = offer
                            best_price = p
                    except Exception:
                        continue
                return best

            # Prefer requested nonstop, then relax
            offer = await _try_dates(prefer_nonstop)
            if not offer:
                offer = await _try_dates(False)
            return offer

        out_dates = await _safe_search_flight_dates(origin, destination)
        ret_dates = await _safe_search_flight_dates(destination, origin)

        today = datetime.now()
        default_dep = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        default_ret = (today + timedelta(days=14)).strftime("%Y-%m-%d")
        seed_departure = departure_date or default_dep
        seed_return = return_date or default_ret

        cheapest_out_date = _pick_cheapest_date(out_dates) or seed_departure
        cheapest_ret_date = _pick_cheapest_date(ret_dates) or seed_return

        # Outbound offer on cheapest date (with fallbacks)
        out_offer = await _find_one_way_cheapest_offer(
            origin, destination, cheapest_out_date, adults, travel_class, nonstop
        )

        # Return offer on cheapest date (with fallbacks)
        ret_offer = await _find_one_way_cheapest_offer(
            destination, origin, cheapest_ret_date, adults, travel_class, nonstop
        )

        # Extract dates: check-in = outbound arrival date; check-out = return departure date
        def _first_segment_departure_date(itin: Optional[Dict[str, Any]]) -> Optional[str]:
            try:
                if not itin or not itin.get("segments"):
                    return None
                dep_at = itin["segments"][0].get("departureAt")
                return dep_at.split("T")[0] if isinstance(dep_at, str) and "T" in dep_at else dep_at
            except Exception:
                return None

        def _last_segment_arrival_date(itin: Optional[Dict[str, Any]]) -> Optional[str]:
            try:
                if not itin or not itin.get("segments"):
                    return None
                arr_at = itin["segments"][-1].get("arrivalAt")
                return arr_at.split("T")[0] if isinstance(arr_at, str) and "T" in arr_at else arr_at
            except Exception:
                return None

        out_itin = out_offer.get("outbound") if isinstance(out_offer, dict) else None
        ret_itin = ret_offer.get("outbound") if isinstance(ret_offer, dict) else None

        check_in_date = _last_segment_arrival_date(out_itin) or cheapest_out_date
        check_out_date = _first_segment_departure_date(ret_itin) or cheapest_ret_date
        # If we still failed to get a return leg, ensure a sane hotel window (2 nights)
        if not ret_itin:
            parsed_in = _parse_date(check_in_date)
            if parsed_in:
                check_out_date = _date_str(parsed_in + timedelta(days=2))

        # Hotels in destination city using dates
        # Use airport service for proper city code mapping
        from app.services.airport_service import get_airport_service
        airport_service = get_airport_service()
        city_code = airport_service.get_airport_code(destination)
        
        hotels = await self.get_hotel_offers_for_city(
            city_code=city_code,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
            room_quantity=room_quantity,
            radius=hotel_radius,
            radius_unit=hotel_radius_unit,
        )

        flights_payload = {
            "outbound": {
                "price": out_offer.get("price") if isinstance(out_offer, dict) else None,
                "currency": out_offer.get("currency") if isinstance(out_offer, dict) else None,
                "itinerary": out_itin,
            },
            "return": {
                "price": ret_offer.get("price") if isinstance(ret_offer, dict) else None,
                "currency": ret_offer.get("currency") if isinstance(ret_offer, dict) else None,
                "itinerary": ret_itin,
            },
        }

        return {
            "flights": flights_payload,
            "hotels": hotels,
        }

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

    async def _test_get_trip_details():
        """End-to-end test for two one-way legs + hotels (round trip)."""
        try:
            svc = AmadeusService()  # uses settings for credentials
            result = await svc.get_trip_details(
                origin="JFK",
                destination="LAX",
                adults=1,
                travel_class=None,
                nonstop=True,
                hotel_radius=5,
                hotel_radius_unit="KM",
                room_quantity=1,
            )
            print(json.dumps(result, indent=2))
        except Exception as e:
            print({"status": "error", "error": str(e)})

    async def _main():
        # Demonstrate two-leg search producing a non-null return itinerary
        await _test_get_trip_details()

    asyncio.run(_main())
