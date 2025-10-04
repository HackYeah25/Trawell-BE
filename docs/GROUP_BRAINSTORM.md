# Group Brainstorm - Collaborative Travel Planning

## Overview

Group Brainstorm mode enables multiple users to collaboratively plan trips with AI-powered moderation. The AI analyzes group compatibility, detects conflicts, and provides suggestions that work for everyone.

## Architecture

```
┌─────────────┐
│   User 1    │───┐
└─────────────┘   │
                  │    ┌──────────────────┐
┌─────────────┐   ├───→│  WebSocket Hub   │
│   User 2    │───┤    └──────────────────┘
└─────────────┘   │            │
                  │            ↓
┌─────────────┐   │    ┌──────────────────┐     ┌─────────────────┐
│   User 3    │───┘    │ Group Moderator  │────→│ Supabase (DB)   │
└─────────────┘        │      Agent       │     └─────────────────┘
                       └──────────────────┘
                                │
                                ↓
                       ┌──────────────────┐
                       │ Compatibility    │
                       │ Analysis Engine  │
                       └──────────────────┘
```

## Key Features

### 1. **Compatibility Analysis**
- Automatic analysis when participants join
- Identifies common ground and conflicts
- Scores individual vs. group compatibility
- Triggers appropriate AI response strategy

### 2. **AI Moderation**
- **Smart Triggers**: AI responds when:
  - Everyone has spoken at least once
  - Direct question to AI
  - Extended discussion (6+ messages)
  - Manual invocation

- **Context-Aware Responses**:
  - High compatibility → Enthusiastic suggestions
  - Low compatibility → Diplomatic conflict resolution

### 3. **Streaming Responses**
- Token-by-token streaming for low latency
- Thinking indicators
- Progressive disclosure

### 4. **Conflict Resolution**
- Identifies conflicting preferences
- Suggests compromise destinations
- Proposes split itinerary approaches
- Maintains group cohesion

## API Flow

### 1. Create Conversation

```bash
POST /api/brainstorm/group/create
```

**Request:**
```json
{
  "user_name": "Alice",
  "user_profile": {
    "traveler_type": "explorer",
    "activity_level": "moderate",
    "accommodation_style": "boutique",
    "environment": "urban",
    "budget_sensitivity": "medium"
  }
}
```

**Response:**
```json
{
  "conversation": {
    "id": "uuid",
    "room_code": "ABC123",
    "status": "profiling",
    ...
  },
  "participants": [...],
  "recent_messages": []
}
```

### 2. Join Conversation

```bash
POST /api/brainstorm/group/join
```

**Request:**
```json
{
  "room_code": "ABC123",
  "user_name": "Bob",
  "user_profile": {
    "traveler_type": "relaxer",
    "activity_level": "low",
    ...
  }
}
```

### 3. WebSocket Connection

```javascript
const ws = new WebSocket(
  `ws://localhost:8000/api/brainstorm/group/ws/${conversationId}?user_id=${userId}&user_name=${userName}`
);

// Send message
ws.send(JSON.stringify({
  type: "user_message",
  message: "I'd love to go somewhere with beaches",
  ai_invoked: false
}));

// Receive messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case "user_message":
      // Display user message
      break;
    case "ai_thinking":
      // Show thinking indicator
      break;
    case "ai_token":
      // Append streaming token
      break;
    case "ai_message":
      // Complete AI response
      break;
    case "compatibility_update":
      // Update compatibility UI
      break;
    case "system_message":
      // Show system notification
      break;
  }
};
```

## Message Types

### User Messages
```json
{
  "type": "user_message",
  "conversation_id": "uuid",
  "user_id": "uuid",
  "user_name": "Alice",
  "message": "I prefer mountains over beaches",
  "timestamp": "2025-10-04T..."
}
```

### AI Thinking
```json
{
  "type": "ai_thinking",
  "conversation_id": "uuid",
  "message": "💭 Analyzing everyone's preferences...",
  "timestamp": "2025-10-04T..."
}
```

### AI Streaming Token
```json
{
  "type": "ai_token",
  "conversation_id": "uuid",
  "token": "Based ",
  "timestamp": "2025-10-04T..."
}
```

### AI Complete Message
```json
{
  "type": "ai_message",
  "conversation_id": "uuid",
  "message": "Based on your discussion, I suggest...",
  "message_type": "ai_suggestion",
  "timestamp": "2025-10-04T..."
}
```

### Compatibility Update
```json
{
  "type": "compatibility_update",
  "conversation_id": "uuid",
  "analysis": {
    "compatibility_level": "medium",
    "compatibility_score": 0.65,
    "common_ground": ["culture", "food"],
    "conflicts": [
      {
        "aspect": "activity_level",
        "users": ["Alice", "Bob"],
        "issue": "Alice wants active adventures, Bob prefers relaxation",
        "severity": 0.7
      }
    ],
    "compromise_needed": true,
    "suggested_approach": "Focus on destinations with variety...",
    "participant_scores": {
      "Alice": 0.8,
      "Bob": 0.5
    }
  },
  "timestamp": "2025-10-04T..."
}
```

### System Message
```json
{
  "type": "system_message",
  "conversation_id": "uuid",
  "message": "⚠️ Heads up! Your group has different preferences in: activity_level, accommodation_style...",
  "timestamp": "2025-10-04T..."
}
```

## Compatibility Scoring

### Individual Compatibility Score
```python
weights = {
    'traveler_type': 0.3,      # explorer, relaxer, culture_seeker, etc.
    'activity_level': 0.25,    # high, moderate, low
    'accommodation_style': 0.15, # luxury, boutique, budget, hostel
    'environment': 0.2,        # urban, nature, beach, mountains
    'budget_sensitivity': 0.1  # low, medium, high
}
```

### Compatibility Levels
- **High** (0.8-1.0): Strong alignment, enthusiastic suggestions
- **Medium** (0.5-0.79): Some differences, balanced approach
- **Low** (0.3-0.49): Significant conflicts, compromise needed
- **Conflicted** (<0.3): Fundamental differences, split itinerary recommended

## AI Response Triggers

### 1. All Participants Spoke
```python
users_who_spoke == all_active_participants
and len(recent_messages) >= len(participants)
```

### 2. Direct Question
```python
message.lower() contains ["ai", "suggest", "what do you think", "any ideas", "recommend"]
```

### 3. Impasse
```python
6+ consecutive user messages without AI response
```

### 4. Manual Invocation
```python
message.metadata.ai_invoked == True
```

## Example Scenarios

### Scenario 1: High Compatibility
```
User1: "I'd love somewhere with great food and culture"
User2: "Same! And maybe some history too?"
User3: "Perfect, I'm all about food and museums"

AI: "🎉 Awesome! You're all aligned on culture and food.
     I suggest:
     1. Rome - ancient history + incredible food
     2. Barcelona - Gaudí's architecture + tapas culture
     3. Istanbul - rich history + diverse cuisine

     All three offer world-class museums and dining!"
```

### Scenario 2: Conflicted Group
```
User1: "I want adventure sports and hiking"
User2: "I prefer relaxing on a beach"
User3: "Budget is tight for me, max $1000"

AI: "I see different preferences here - that's okay!
     Here's how we can make everyone happy:

     Compromise Destinations:
     1. Croatia - Beaches for User2, hiking in Plitvice for User1,
        and very affordable for User3
     2. Portugal - Algarve beaches + mountain trails in Madeira,
        budget-friendly outside peak season

     Flexible Approach:
     - Morning/afternoon: Split activities (hiking vs beach)
     - Evenings: Group dinners and exploration together
     - Base yourselves in one location with day trip options"
```

## Database Schema

### group_conversations
```sql
id UUID PRIMARY KEY
room_code VARCHAR(10) UNIQUE
status VARCHAR(20) -- 'profiling', 'active', 'converged', 'conflicted'
compatibility_data JSONB
metadata JSONB
created_at TIMESTAMP
updated_at TIMESTAMP
```

### group_participants
```sql
id UUID PRIMARY KEY
conversation_id UUID REFERENCES group_conversations(id)
user_id UUID
user_name VARCHAR(100)
user_profile JSONB
compatibility_score FLOAT
is_active BOOLEAN
joined_at TIMESTAMP
last_active_at TIMESTAMP
```

### group_messages
```sql
id UUID PRIMARY KEY
conversation_id UUID REFERENCES group_conversations(id)
user_id UUID -- NULL for AI messages
user_name VARCHAR(100)
message TEXT
message_type VARCHAR(20) -- 'user', 'ai_analysis', 'ai_suggestion', 'system'
metadata JSONB
created_at TIMESTAMP
```

## Performance Considerations

### Latency Optimization
1. **Streaming**: Token-by-token response (perceived latency ~500ms)
2. **Async Processing**: AI analysis runs in background
3. **Caching**: Compatibility cached per conversation
4. **Supabase Realtime**: Zero-latency message sync

### Scalability
1. **WebSocket Pooling**: One connection per user per conversation
2. **Database Indexes**: On conversation_id, user_id, created_at
3. **Message Pagination**: Default 50 messages, load more on demand
4. **Cleanup**: Auto-archive inactive conversations (configurable)

## Error Handling

### WebSocket Disconnection
```python
try:
    await websocket.receive_json()
except WebSocketDisconnect:
    manager.disconnect(websocket, conversation_id)
    # Broadcast participant left
    await manager.broadcast(conversation_id, {
        "type": "participant_update",
        "action": "left",
        "participant": participant_data
    })
```

### AI Failure Fallback
```python
try:
    response = await ai_chain.ainvoke(prompt)
except Exception as e:
    # Fallback to simpler response
    response = "I'm having trouble analyzing this. Let me know what you're thinking!"
```

## Testing

### Unit Tests
```bash
pytest tests/test_group_moderator.py
```

### Integration Tests
```bash
pytest tests/test_group_brainstorm_api.py
```

### WebSocket Testing
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

with client.websocket_connect(f"/api/brainstorm/group/ws/{conv_id}") as ws:
    ws.send_json({"type": "user_message", "message": "Hello"})
    data = ws.receive_json()
    assert data["type"] == "user_message"
```

## Future Enhancements

1. **Voting System**: Poll participants on destinations
2. **Itinerary Merging**: Combine individual preferences into group itinerary
3. **Budget Calculator**: Real-time group budget estimation
4. **Calendar Integration**: Find common available dates
5. **Booking Integration**: Direct booking from group decision
6. **Voice Chat**: Real-time voice with AI transcription
