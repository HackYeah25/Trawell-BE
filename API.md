# API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.travelai.com`

## Interactive Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

Most endpoints require JWT Bearer token authentication.

### Get Token

1. Register or login to get access token
2. Include token in `Authorization` header: `Bearer <token>`

```bash
# Example with curl
curl -H "Authorization: Bearer your_token_here" \
  http://localhost:8000/api/brainstorm/start
```

## API Endpoints

### System

#### `GET /`
Get API status and version

**Response**
```json
{
  "name": "Travel AI Assistant",
  "version": "1.0.0",
  "status": "running",
  "environment": "development",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

#### `GET /health`
Health check endpoint

**Response**
```json
{
  "status": "healthy",
  "service": "travel-ai-backend",
  "version": "1.0.0"
}
```

---

### Authentication

#### `POST /api/auth/register`
Register a new user

**Request Body**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response**
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe"
  }
}
```

#### `POST /api/auth/login`
Login user

**Request Body**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response**
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "user": {...}
}
```

---

### Brainstorm (Destination Discovery)

#### `POST /api/brainstorm/start`
Start a new brainstorming session

**Headers**
- `Authorization: Bearer <token>`

**Request Body**
```json
{
  "user_id": "user_uuid",
  "budget_range": [1000, 3000],
  "travel_dates": ["2024-06-01T00:00:00Z", "2024-06-15T00:00:00Z"],
  "constraints": {},
  "group_mode": false,
  "group_participants": []
}
```

**Response**
```json
{
  "conversation_id": "conv_abc123",
  "mode": "solo",
  "message": "Brainstorm session started! Tell me what kind of trip you're dreaming about."
}
```

#### `POST /api/brainstorm/{conversation_id}/message`
Send a message in a brainstorm session

**Headers**
- `Authorization: Bearer <token>`

**Request Body**
```json
{
  "message": "I'd like a relaxing beach vacation with good food"
}
```

**Response**
```json
{
  "conversation_id": "conv_abc123",
  "message": {
    "role": "user",
    "content": "I'd like a relaxing beach vacation with good food",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "ai_response": {
    "role": "assistant",
    "content": "Based on your profile and preferences, I have some perfect destinations...",
    "timestamp": "2024-01-15T10:30:05Z"
  }
}
```

#### `GET /api/brainstorm/{conversation_id}/suggestions`
Get AI destination suggestions

**Headers**
- `Authorization: Bearer <token>`

**Response**
```json
{
  "recommendations": [
    {
      "destination": {
        "name": "Bali",
        "country": "Indonesia"
      },
      "reasoning": "Perfect for relaxation with world-class beaches and cuisine",
      "optimal_season": "April-October",
      "estimated_budget": 1500,
      "highlights": [
        "Beautiful beaches in Seminyak and Uluwatu",
        "Amazing local and international cuisine",
        "Relaxing spa culture"
      ]
    }
  ]
}
```

#### `POST /api/brainstorm/{conversation_id}/group/invite`
Invite users to group brainstorm

**Headers**
- `Authorization: Bearer <token>`

**Request Body**
```json
{
  "user_ids": ["user_uuid_1", "user_uuid_2"]
}
```

---

### Planning (Trip Planning)

#### `POST /api/planning/create`
Create a new trip plan

**Headers**
- `Authorization: Bearer <token>`

**Request Body**
```json
{
  "user_id": "user_uuid",
  "destination": {
    "name": "Lisbon",
    "country": "Portugal",
    "coordinates": {
      "lat": 38.7223,
      "lng": -9.1393
    }
  },
  "start_date": "2024-05-01T00:00:00Z",
  "end_date": "2024-05-07T00:00:00Z",
  "budget": 2000
}
```

**Response**
```json
{
  "trip_id": "trip_xyz789",
  "user_id": "user_uuid",
  "destination": {...},
  "status": "draft",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### `GET /api/planning/{trip_id}`
Get trip plan details

**Headers**
- `Authorization: Bearer <token>`

**Response**
```json
{
  "trip_id": "trip_xyz789",
  "destination": {...},
  "weather_forecast": [...],
  "points_of_interest": [...],
  "local_events": [...],
  "daily_itinerary": [...]
}
```

#### `POST /api/planning/{trip_id}/flights`
Search flights for trip

**Headers**
- `Authorization: Bearer <token>`

**Request Body**
```json
{
  "origin": "JFK",
  "destination": "LIS",
  "departure_date": "2024-05-01T00:00:00Z",
  "return_date": "2024-05-07T00:00:00Z",
  "passengers": 1,
  "cabin_class": "economy"
}
```

#### `POST /api/planning/{trip_id}/weather`
Get weather forecast

**Headers**
- `Authorization: Bearer <token>`

**Response**
```json
{
  "forecast": [
    {
      "date": "2024-05-01T00:00:00Z",
      "temperature_high": 22,
      "temperature_low": 15,
      "conditions": "Partly cloudy",
      "precipitation_chance": 0.2
    }
  ]
}
```

#### `POST /api/planning/{trip_id}/poi`
Get points of interest

**Headers**
- `Authorization: Bearer <token>`

**Response**
```json
{
  "points_of_interest": [
    {
      "name": "Belém Tower",
      "category": "landmark",
      "opening_hours": "10:00-18:00",
      "ticket_price": 6,
      "rating": 4.6
    }
  ]
}
```

#### `POST /api/planning/{trip_id}/events`
Get local events

**Headers**
- `Authorization: Bearer <token>`

**Response**
```json
{
  "events": [
    {
      "name": "Lisbon Jazz Festival",
      "type": "concert",
      "date": "2024-05-03T20:00:00Z",
      "location": "Gulbenkian Foundation"
    }
  ]
}
```

#### `PUT /api/planning/{trip_id}/customize`
Customize itinerary

**Headers**
- `Authorization: Bearer <token>`

**Request Body**
```json
{
  "customization_type": "add_activity",
  "details": {...}
}
```

---

### Support (On-site Support)

#### `POST /api/support/{trip_id}/chat`
Chat with AI for on-site support

**Headers**
- `Authorization: Bearer <token>`

**Request Body**
```json
{
  "message": "Where can I find good seafood restaurants nearby?"
}
```

**Response**
```json
{
  "ai_response": "Here are some excellent seafood restaurants within walking distance..."
}
```

#### `GET /api/support/{trip_id}/nearby`
Get nearby recommendations

**Headers**
- `Authorization: Bearer <token>`

**Query Parameters**
- `location`: Current location
- `category`: Optional category (restaurant, attraction, etc.)

**Response**
```json
{
  "recommendations": [
    {
      "name": "Ramiro",
      "category": "restaurant",
      "distance": "0.3 km",
      "rating": 4.7
    }
  ]
}
```

#### `POST /api/support/{trip_id}/emergency`
Get emergency information

**Headers**
- `Authorization: Bearer <token>`

**Response**
```json
{
  "emergency_numbers": {
    "police": "112",
    "ambulance": "112",
    "fire": "112"
  },
  "nearest_hospital": {...},
  "embassy_info": {...}
}
```

---

### WebSocket

#### `WS /api/ws/{conversation_id}/stream`
WebSocket for streaming AI responses

**Connection**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/conv_123/stream');

ws.onmessage = (event) => {
  console.log('AI response:', event.data);
};

ws.send('Tell me about Lisbon');
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message",
  "error": "Detailed error (only in debug mode)"
}
```

### Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
- `501` - Not Implemented

---

## Rate Limiting

(To be implemented)

- Default: 100 requests per minute
- Authenticated: 1000 requests per minute

---

## Pagination

(To be implemented)

List endpoints support pagination:

```
GET /api/endpoint?page=1&limit=20
```

Response includes:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "pages": 5
}
```
