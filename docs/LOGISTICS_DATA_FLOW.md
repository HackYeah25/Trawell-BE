# Logistics Data Flow Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React)                           │
│                                                                      │
│  ┌────────────────┐        ┌──────────────────┐                    │
│  │  Planning Page │───────▶│  WebSocket       │                    │
│  │                │        │  Connection      │                    │
│  └────────────────┘        └──────────────────┘                    │
│         │                           │                               │
│         │                           ▼                               │
│         │                  ┌──────────────────┐                    │
│         │                  │ Logistics Cards  │                    │
│         │                  │ - Flights Card   │                    │
│         │                  │ - Hotels Card    │                    │
│         │                  │ - Weather Card   │                    │
│         │                  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket Messages
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              planning.py - WebSocket Endpoint                 │  │
│  │                                                               │  │
│  │  1. Client Connects                                          │  │
│  │  2. Fetch Recommendation from DB                             │  │
│  │  3. Extract Logistics Data (url, flights, hotels, weather)   │  │
│  │  4. Create Planning Agent with Logistics Context             │  │
│  │  5. Send logistics_data message to frontend                  │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                    │                    │
│                           │                    │                    │
│                           ▼                    ▼                    │
│  ┌─────────────────────────────┐   ┌──────────────────────────┐   │
│  │    planning_agent.py        │   │  apply_trip_updates()    │   │
│  │                             │   │                          │   │
│  │  - Receives logistics_data  │   │  When destination info   │   │
│  │  - Builds system prompt     │   │  is available:           │   │
│  │  - Includes logistics       │   │                          │   │
│  │    context for AI           │   │  1. GooglePlaces API     │   │
│  │  - AI references real       │   │  2. Amadeus API          │   │
│  │    prices/options           │   │  3. Weather API          │   │
│  │                             │   │  4. Store in DB          │   │
│  └─────────────────────────────┘   └──────────────────────────┘   │
│                                              │                      │
└──────────────────────────────────────────────│──────────────────────┘
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                                │
│                                                                      │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────────┐   │
│  │ Google Places │  │ Amadeus API   │  │ WeatherAPI.com       │   │
│  │               │  │               │  │                      │   │
│  │ - Photo URL   │  │ - Flights     │  │ - Forecast (7 days)  │   │
│  │               │  │ - Hotels      │  │ - Temperature        │   │
│  │               │  │               │  │ - Conditions         │   │
│  └───────────────┘  └───────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATABASE (Supabase)                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         destination_recommendations table                     │  │
│  │                                                               │  │
│  │  - recommendation_id (PK)                                    │  │
│  │  - user_id                                                   │  │
│  │  - destination (JSONB)                                       │  │
│  │  - url (TEXT)              ← NEW: Place photo URL           │  │
│  │  - flights (JSONB)         ← NEW: Flight options            │  │
│  │  - hotels (JSONB)          ← NEW: Hotel options             │  │
│  │  - weather (JSONB)         ← NEW: Weather forecast          │  │
│  │  - estimated_budget                                          │  │
│  │  - optimal_season                                            │  │
│  │  - highlights                                                │  │
│  │  ...                                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Message Flow Sequence

```
User                 Frontend            Backend             External APIs      Database
  │                     │                    │                      │              │
  │  Open Planning      │                    │                      │              │
  ├────────────────────▶│                    │                      │              │
  │                     │  WS Connect        │                      │              │
  │                     ├───────────────────▶│                      │              │
  │                     │                    │  Query Recommendation│              │
  │                     │                    ├─────────────────────────────────────▶│
  │                     │                    │                      │     Return    │
  │                     │                    │◀─────────────────────────────────────┤
  │                     │                    │                      │              │
  │                     │                    │  Extract logistics:  │              │
  │                     │                    │  - url, flights,     │              │
  │                     │                    │    hotels, weather   │              │
  │                     │                    │                      │              │
  │                     │                    │  Create Agent with   │              │
  │                     │                    │  logistics context   │              │
  │                     │                    │                      │              │
  │                     │  logistics_data    │                      │              │
  │                     │◀───────────────────┤                      │              │
  │                     │                    │                      │              │
  │  Display Cards      │                    │                      │              │
  │  - Flights          │                    │                      │              │
  │  - Hotels           │                    │                      │              │
  │  - Weather          │                    │                      │              │
  │◀────────────────────┤                    │                      │              │
  │                     │                    │                      │              │
  │  User Message       │                    │                      │              │
  ├────────────────────▶│  WS message        │                      │              │
  │                     ├───────────────────▶│                      │              │
  │                     │                    │  AI processes with   │              │
  │                     │                    │  logistics context   │              │
  │                     │                    │  (can reference      │              │
  │                     │                    │   real prices)       │              │
  │                     │                    │                      │              │
  │                     │  Stream response   │                      │              │
  │  AI Response        │◀───────────────────┤                      │              │
  │◀────────────────────┤                    │                      │              │
  │  (mentions          │                    │                      │              │
  │   specific hotels/  │                    │                      │              │
  │   flight prices)    │                    │                      │              │
```

## Data Fetching Flow (apply_trip_updates)

```
apply_trip_updates() called
        │
        ├─ Check if 'name' or 'city' in update_data
        │
        ├─ Yes ─┬─ Try GooglePlaces API ─┬─ Success ─▶ update_data['url'] = photo_url
        │       │                         └─ Fail ────▶ update_data['url'] = None
        │       │
        │       ├─ Try Amadeus API ───────┬─ Success ─▶ update_data['flights'] = {...}
        │       │                         │             update_data['hotels'] = [...]
        │       │                         └─ Fail ────▶ update_data['flights'] = {}
        │       │                                       update_data['hotels'] = []
        │       │
        │       └─ Try Weather API ────────┬─ Success ─▶ update_data['weather'] = {...}
        │                                  └─ Fail ────▶ update_data['weather'] = {}
        │
        └─ Update Database with all data
                │
                └─ Log success/failure
```

## AI Agent Context Building

```
PlanningAgent.__init__(logistics_data)
        │
        ├─ Store logistics_data
        │
        └─ _build_system_prompt()
                │
                ├─ Base Prompt
                │
                ├─ Destination Context
                │
                ├─ Logistics Context ◀───────┐
                │   │                        │
                │   ├─ Flights Summary        │ From logistics_data
                │   │   - Outbound price      │ passed to agent
                │   │   - Return price        │
                │   │   - Duration            │
                │   │   - Route               │
                │   │                         │
                │   ├─ Hotels Summary         │
                │   │   - Top 3 options       │
                │   │   - Prices              │
                │   │   - Names               │
                │   │                         │
                │   └─ Weather Summary        │
                │       - Forecast info       │
                │                             │
                ├─ User Profile Context       │
                │                             │
                ├─ Constraints Context        │
                │                             │
                └─ Structured Extraction Rules
```

## WebSocket Message Types

### Sent from Backend to Frontend

1. **logistics_data** (NEW)
```json
{
  "type": "logistics_data",
  "recommendation_id": "rec_xxx",
  "data": {
    "url": "https://...",
    "flights": { "outbound": {...}, "return": {...} },
    "hotels": [...],
    "weather": {...}
  }
}
```

2. **thinking**
```json
{
  "type": "thinking",
  "recommendation_id": "rec_xxx"
}
```

3. **token** (streaming)
```json
{
  "type": "token",
  "recommendation_id": "rec_xxx",
  "token": "text..."
}
```

4. **complete**
```json
{
  "type": "complete",
  "recommendation_id": "rec_xxx",
  "content": "full message"
}
```

5. **trip_updated**
```json
{
  "type": "trip_updated",
  "recommendation_id": "rec_xxx",
  "updates": [...]
}
```

6. **error**
```json
{
  "type": "error",
  "message": "error description"
}
```

## Database Schema (destination_recommendations)

```sql
CREATE TABLE destination_recommendations (
  recommendation_id TEXT PRIMARY KEY,
  user_id UUID NOT NULL,
  destination JSONB NOT NULL,
  
  -- Existing fields
  reasoning TEXT,
  optimal_season TEXT,
  estimated_budget NUMERIC,
  currency TEXT DEFAULT 'USD',
  highlights TEXT[],
  deals_found JSONB[],
  status TEXT DEFAULT 'suggested',
  confidence_score NUMERIC,
  
  -- NEW: Logistics fields
  url TEXT,                    -- Google Places photo
  flights JSONB DEFAULT '{}'::jsonb,   -- Flight options
  hotels JSONB DEFAULT '[]'::jsonb,    -- Hotel options  
  weather JSONB DEFAULT '{}'::jsonb,   -- Weather forecast
  
  -- Metadata
  source_conversation_id TEXT,
  location_proposal_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_destination_recommendations_user_id 
  ON destination_recommendations(user_id);
  
CREATE INDEX idx_destination_recommendations_status 
  ON destination_recommendations(status);
```

## Key Files Modified

### Backend
- ✅ `app/api/planning.py` - WebSocket endpoint, logistics fetching
- ✅ `app/agents/planning_agent.py` - Agent with logistics context
- ✅ `app/services/amadeus_service.py` - Sync wrapper method
- ✅ `app/services/weather_service.py` - Sync wrapper method
- ✅ `app/prompts/planning.yaml` - Updated system prompt

### Database
- ✅ Migration: `add_trip_logistics_data` - New columns

### Documentation
- ✅ `docs/adr/add-logistics-data-to-planning.md` - ADR
- ✅ `LOGISTICS_INTEGRATION_SUMMARY.md` - Implementation summary
- ✅ `docs/LOGISTICS_DATA_FLOW.md` - This file

### Frontend (TO DO)
- ⏳ WebSocket message handler for `logistics_data`
- ⏳ Flight card component
- ⏳ Hotel card component
- ⏳ Weather card component
- ⏳ Card container/layout
- ⏳ State management for logistics data
