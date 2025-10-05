# ADR: Add Logistics Data to Trip Planning Flow

**Status:** Accepted  
**Date:** 2025-10-05  
**Decision Makers:** AI Assistant, Development Team

## Context

The trip planning flow previously lacked real-time logistics information (flights, hotels, weather) that would be crucial for users to make informed decisions during the planning conversation. While the system had services to fetch this data (AmadeusService, WeatherService, GooglePlacesService), the data was not being:

1. Persisted in the database
2. Passed to the AI planning agent for context-aware recommendations
3. Delivered to the frontend for display
4. Integrated into the planning prompts

## Decision

We have decided to integrate logistics data throughout the entire trip planning flow:

### Database Schema Changes
- Added `url` (TEXT) - destination photo from Google Places
- Added `flights` (JSONB) - flight options with outbound/return itineraries
- Added `hotels` (JSONB) - hotel options array with prices
- Added `weather` (JSONB) - weather forecast data

### Backend Changes
1. **Planning API (`planning.py`)**
   - Fetch logistics data when trip updates are applied
   - Pass logistics data to PlanningAgent on initialization
   - Send logistics data to frontend via WebSocket as initial cards
   - Include logistics in trip summary endpoint

2. **Planning Agent (`planning_agent.py`)**
   - Accept logistics_data parameter in constructor
   - Include logistics context in system prompt
   - Enable AI to reference specific flights/hotels/weather in recommendations

3. **Service Layer**
   - Added `get_trip_details_sync()` to AmadeusService for synchronous calls
   - Added `get_forecast_sync()` to WeatherService for synchronous calls
   - Improved error handling and fallbacks

4. **Prompts (`planning.yaml`)**
   - Updated system prompt to guide AI on using logistics data
   - Added context about referencing flights/hotels in budget discussions
   - Added guidance for weather-based packing suggestions

## Rationale

### Why Persist in Database?
- Reduces API calls and costs
- Enables historical tracking
- Provides data for frontend display even when agent is not active
- Allows for caching and optimization

### Why Pass to Planning Agent?
- Enables context-aware recommendations
- AI can reference specific prices and options
- More accurate budget calculations
- Better user experience with real data

### Why JSONB Format?
- Flexible schema for varying API responses
- Efficient querying capabilities in PostgreSQL
- Easy to update and extend
- Natural fit for nested data structures

### Why Synchronous Wrappers?
- Simplifies calling from non-async contexts
- Maintains backward compatibility
- Reduces complexity in planning.py
- Properly handles event loop management

## Consequences

### Positive
- ✅ Users see real flight/hotel prices during planning
- ✅ AI provides more accurate, data-driven recommendations
- ✅ Weather data enables better packing/timing advice
- ✅ Reduced need for users to check external sites
- ✅ Better budget planning with actual prices

### Negative
- ⚠️ Increased database storage (JSONB columns)
- ⚠️ Additional API calls to external services
- ⚠️ Potential for stale data (prices change)
- ⚠️ More complex error handling
- ⚠️ Sync wrappers may block if APIs are slow

### Mitigations
- Implement caching strategy for logistics data
- Add TTL (time-to-live) for refreshing stale data
- Graceful degradation when APIs fail
- Background jobs for non-critical updates
- Consider async/await throughout if performance becomes issue

## Implementation Notes

### Data Flow
```
User Planning Request
  ↓
Planning WebSocket Connected
  ↓
Fetch Destination from DB
  ↓
Extract Logistics Data (flights, hotels, weather, url)
  ↓
Create Planning Agent with Logistics Context
  ↓
Send logistics_data message to Frontend
  ↓
AI Uses Logistics in Recommendations
  ↓
Updates Applied & Persisted
```

### Frontend Integration Required
- Add handlers for `logistics_data` WebSocket message type
- Create mini card components for flights, hotels, weather
- Display cards inline at start of planning conversation
- Update UI when new logistics data arrives

### API Response Format
```json
{
  "url": "https://places.googleapis.com/...",
  "flights": {
    "outbound": {
      "price": "196.89",
      "currency": "EUR",
      "itinerary": {
        "totalDuration": "6h 3m",
        "segments": [...]
      }
    },
    "return": { ... }
  },
  "hotels": [
    {
      "name": "Hotel Name",
      "price": "2825.07",
      "currency": "USD",
      "checkInDate": "2025-10-08",
      "checkOutDate": "2025-10-21"
    }
  ],
  "weather": { ... }
}
```

## Future Enhancements
- Add booking capabilities
- Implement price alerts
- Add more logistics options (car rentals, activities)
- ML-based price prediction
- User preference learning for accommodations
- Integration with more travel APIs

## References
- [Amadeus API Documentation](https://developers.amadeus.com/)
- [WeatherAPI Documentation](https://www.weatherapi.com/docs/)
- [Google Places API](https://developers.google.com/maps/documentation/places/web-service)
