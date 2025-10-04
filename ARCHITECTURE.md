# 🏗️ System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Frontend / Mobile App / API Consumer)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │     API      │  │   Services   │  │    Utils     │          │
│  │              │  │              │  │              │          │
│  │ - Auth       │  │ - LangChain  │  │ - Context    │          │
│  │ - Brainstorm │  │ - Supabase   │  │   Manager    │          │
│  │ - Planning   │  │ - External   │  │ - Validators │          │
│  │ - Support    │  │   APIs       │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────────────────────────────────────────┐           │
│  │           Prompt Management (YAML)               │           │
│  │  system.yaml | brainstorm.yaml | planning.yaml  │           │
│  └──────────────────────────────────────────────────┘           │
└────────────┬─────────────────┬─────────────────┬────────────────┘
             │                 │                 │
             ▼                 ▼                 ▼
    ┌────────────────┐  ┌─────────────┐  ┌──────────────────┐
    │   Supabase     │  │  LLM APIs   │  │  External APIs   │
    │  (PostgreSQL)  │  │             │  │                  │
    │                │  │ - OpenAI    │  │ - Flights        │
    │ - User Profiles│  │ - Anthropic │  │ - Weather        │
    │ - Conversations│  │             │  │ - Events         │
    │ - Trips        │  │             │  │ - Maps           │
    └────────────────┘  └─────────────┘  └──────────────────┘
```

---

## Request Flow

### 1. Brainstorm Session Flow

```
User Request
    │
    ▼
┌────────────────────────────────────────────────────┐
│ 1. POST /api/brainstorm/start                      │
│    - Create conversation in Supabase               │
│    - Return conversation_id                        │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ 2. POST /api/brainstorm/{id}/message               │
│    - Get conversation from Supabase                │
│    - Load user profile from Supabase               │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ 3. Context Manager                                 │
│    - Build context with user profile as Prompt #1  │
│    - Add conversation history                      │
│    - Check token limits                            │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ 4. Prompt Loader                                   │
│    - Load prompt from YAML (brainstorm.yaml)       │
│    - Format with context variables                 │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ 5. LangChain Service                               │
│    - Send to LLM (OpenAI/Anthropic)                │
│    - Get AI response                               │
└────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────┐
│ 6. Save & Return                                   │
│    - Save messages to Supabase                     │
│    - Return AI response to client                  │
└────────────────────────────────────────────────────┘
    │
    ▼
User receives personalized destination suggestions
```

---

## Data Flow

### User Profile → AI Context

```
Supabase
   │
   │ Fetch user_profile
   ▼
┌──────────────────────────────────────┐
│ User Profile JSON                    │
│ {                                    │
│   "preferences": {...},              │
│   "constraints": {...},              │
│   "past_destinations": [...]         │
│ }                                    │
└──────────────────────────────────────┘
   │
   │ Format as system prompt
   ▼
┌──────────────────────────────────────┐
│ System Prompt                        │
│ "Our user has a profile containing:  │
│  {profile_json}                      │
│  Use this to personalize responses"  │
└──────────────────────────────────────┘
   │
   │ Becomes first message in context
   ▼
┌──────────────────────────────────────┐
│ LangChain Context                    │
│ [                                    │
│   {role: "system", content: profile},│
│   {role: "user", content: "..."},    │
│   {role: "assistant", content: "..."} │
│ ]                                    │
└──────────────────────────────────────┘
   │
   │ Sent to LLM
   ▼
Personalized AI Response
```

---

## Module Architecture

### Brainstorm Module

```
Client Request → API Endpoint
                     │
                     ▼
              ┌──────────────┐
              │ Brainstorm   │
              │ Endpoint     │
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
  ┌─────────┐  ┌─────────┐  ┌─────────┐
  │ Profile │  │ Context │  │ Prompt  │
  │ Service │  │ Manager │  │ Loader  │
  └─────────┘  └─────────┘  └─────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
              ┌──────────────┐
              │  LangChain   │
              │   Service    │
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │OpenAI/ │  │External│  │ Tools  │
    │Claude  │  │  APIs  │  │ (TODO) │
    └────────┘  └────────┘  └────────┘
                     │
                     ▼
              Response to Client
```

### Planning Module

```
Trip Creation Request
        │
        ▼
┌─────────────────┐
│ Planning Chain  │
│                 │
│ 1. Get Weather  │──→ Weather API
│ 2. Get Flights  │──→ Flight API
│ 3. Get POIs     │──→ LLM + Maps
│ 4. Get Events   │──→ Events API
│ 5. Build Plan   │──→ LLM
│                 │
└─────────────────┘
        │
        ▼
Complete Trip Plan
```

---

## Database Schema

### Tables

```
user_profiles
├── user_id (PK)
├── preferences (JSONB)
├── constraints (JSONB)
├── past_destinations (TEXT[])
└── wishlist_regions (TEXT[])

conversations
├── conversation_id (PK)
├── user_id (FK)
├── module (brainstorm/planning/support)
├── mode (solo/group)
├── messages (JSONB[])
└── group_participants (UUID[])

destination_recommendations
├── recommendation_id (PK)
├── user_id (FK)
├── destination (JSONB)
├── reasoning (TEXT)
└── status (suggested/saved/booked/visited)

trip_plans
├── trip_id (PK)
├── user_id (FK)
├── destination (JSONB)
├── dates (TIMESTAMP)
├── weather_forecast (JSONB[])
├── points_of_interest (JSONB[])
└── daily_itinerary (JSONB[])
```

---

## Service Layer

### LangChain Service

```python
class LangChainService:
    - chat(messages) → AI response
    - chat_with_system_prompt() → AI response
    - extract_structured_data() → JSON
    - count_tokens() → int
    - stream_response() → AsyncGenerator
```

### Supabase Service

```python
class SupabaseService:
    # User Profiles
    - get_user_profile(user_id)
    - create_user_profile(profile)
    - update_user_profile(user_id, profile)

    # Conversations
    - get_conversation(conversation_id)
    - create_conversation(conversation)
    - add_message(conversation_id, message)

    # Recommendations
    - save_recommendation(recommendation)
    - get_user_recommendations(user_id)

    # Trips
    - create_trip_plan(trip)
    - get_trip_plan(trip_id)
    - update_trip_plan(trip_id, trip)
```

### Context Manager

```python
class ContextManager:
    - build_user_profile_prompt(profile) → str
    - build_conversation_context(...) → List[Message]
    - truncate_if_needed(messages) → List[Message]
    - estimate_remaining_tokens(context) → int
```

---

## Prompt System

### YAML Structure

```yaml
# brainstorm.yaml
destination_discovery_system: |
  You are a travel expert...

destination_discovery_prompt: |
  Based on: {user_profile}
  Suggest destinations...

# Template usage
prompt = loader.load_template(
    "brainstorm",
    "destination_discovery_prompt",
    user_profile=profile_json
)
```

### Prompt Flow

```
YAML File
    │
    │ load()
    ▼
Prompt Loader
    │
    │ format()
    ▼
Formatted Prompt
    │
    │ combine with context
    ▼
LangChain Message
    │
    │ send to LLM
    ▼
AI Response
```

---

## Deployment Architecture

### Docker Compose Services

```
┌─────────────────────────────────────────┐
│            Docker Network               │
│                                         │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │   Backend    │  │     Redis       │ │
│  │   (FastAPI)  │  │  (Message Queue)│ │
│  │   Port 8000  │  │   Port 6379     │ │
│  └──────────────┘  └─────────────────┘ │
│         │                    │          │
│         ▼                    ▼          │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │Celery Worker │  │  Celery Beat    │ │
│  │(Background)  │  │  (Scheduler)    │ │
│  └──────────────┘  └─────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
         │
         │ External connections
         ▼
┌─────────────────────────────────────────┐
│  Supabase | OpenAI | External APIs     │
└─────────────────────────────────────────┘
```

---

## Security Architecture

### Authentication Flow

```
Client Request
    │
    │ Include: Authorization: Bearer <token>
    ▼
┌────────────────────────────────────┐
│ FastAPI Dependency                 │
│ get_current_user()                 │
│                                    │
│ 1. Extract token from header       │
│ 2. Decode JWT                      │
│ 3. Verify signature                │
│ 4. Extract user_id                 │
└────────────────────────────────────┘
    │
    │ Token valid?
    ▼
┌────────────────────────────────────┐
│ Return TokenData(user_id, email)   │
│ Inject into endpoint               │
└────────────────────────────────────┘
    │
    ▼
Endpoint executes with user context
```

### Row Level Security (RLS)

```sql
-- Supabase RLS ensures users only access their data
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid() = user_id);
```

---

## Scaling Strategy

### Horizontal Scaling

```
Load Balancer
    │
    ├─→ Backend Instance 1
    ├─→ Backend Instance 2
    └─→ Backend Instance 3
         │
         ▼
    Shared Redis & Supabase
```

### Caching Strategy (Future)

```
Request
    │
    ▼
Check Redis Cache
    │
    ├─→ Hit: Return cached
    │
    └─→ Miss:
         │
         ▼
      Query Database
         │
         ▼
      Cache Result
         │
         ▼
      Return to Client
```

---

## Performance Optimizations

1. **Async Operations**: All I/O operations are async
2. **Connection Pooling**: Database connection pooling
3. **Caching**: Redis for frequently accessed data
4. **Token Management**: Smart context truncation
5. **Batch Operations**: Process multiple requests together
6. **Streaming**: WebSocket for real-time responses

---

## Monitoring & Observability (Planned)

```
Application
    │
    ├─→ Logs → CloudWatch/ELK
    ├─→ Metrics → Prometheus
    ├─→ Traces → Jaeger
    └─→ Errors → Sentry
```

---

## Development Workflow

```
Developer
    │
    │ Edit code
    ▼
Hot Reload (FastAPI)
    │
    │ Test locally
    ▼
Git Commit
    │
    │ Push to GitHub
    ▼
CI/CD Pipeline
    │
    ├─→ Run Tests
    ├─→ Build Docker Image
    ├─→ Push to Registry
    └─→ Deploy to Production
```

---

## Key Design Patterns

1. **Dependency Injection**: FastAPI's DI for services
2. **Repository Pattern**: Supabase service abstracts DB
3. **Strategy Pattern**: Different LLM providers
4. **Factory Pattern**: Prompt loader creates prompts
5. **Chain of Responsibility**: Context management
6. **Singleton**: Service instances

---

## Technology Stack

```
┌─────────────────────────────────────┐
│          Application Layer          │
│         FastAPI + Pydantic          │
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│           Service Layer             │
│  LangChain | Supabase | External    │
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│         Infrastructure              │
│  Docker | Redis | PostgreSQL        │
└─────────────────────────────────────┘
```

---

This architecture is designed to be:
- ✅ **Scalable**: Easy to add instances
- ✅ **Maintainable**: Clean separation of concerns
- ✅ **Testable**: Dependency injection enables testing
- ✅ **Observable**: Logging and monitoring ready
- ✅ **Secure**: JWT auth, RLS, environment variables
