# Travel AI Assistant - Backend

## Overview

An AI-powered travel planning application that helps users discover destinations, plan trips, and get on-site support through conversational AI. The system uses LangChain for AI orchestration, Supabase for data persistence, and FastAPI for the REST/WebSocket API layer.

The application features a multi-stage user journey: profiling (conversational questionnaire), brainstorming (destination discovery), planning (trip preparation), and on-site support (real-time assistance while traveling).

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architectural Pattern

**Agent-Based Conversational System**: The application uses specialized LangChain agents for different stages of the travel planning journey. Each agent maintains conversation context and interacts with external services (LLMs, databases, APIs).

**Why this approach?**: Separating concerns by travel planning stage allows for specialized prompting, different LLM configurations, and independent scaling of each module.

### Data Flow Architecture

```
Client Request → FastAPI Endpoint → Specialized Agent → LLM Provider
                                   ↓
                              Supabase DB ← Context Manager
```

**Conversation Persistence**: All conversations are stored in Supabase with full message history. Agents can be rehydrated from database state, allowing users to resume sessions across connections.

**Context Management**: Token-aware context manager automatically truncates conversation history when approaching LLM token limits, preserving user profile and recent messages.

### Module Architecture

#### 1. Profiling System (`/api/profiling`)
- **Purpose**: Conversational user profiling through 13 structured questions
- **Design Pattern**: Question-driven state machine with AI validation
- **Key Decision**: YAML-based question configuration for non-technical prompt editing
- **Storage**: `profiling_sessions`, `profiling_responses`, `profiling_messages` tables
- **WebSocket**: Real-time streaming responses for better UX

**Flow**: WebSocket connection → Question presented → User answers → AI validates → Follow-up or next question → Session saved when ≥80% complete

#### 2. Brainstorm System (`/api/brainstorm`)
- **Purpose**: AI-powered destination discovery based on user profile
- **Design Pattern**: Conversation chain with LangChain memory buffer
- **Key Decision**: Each session creates a `conversation` record with full message history
- **Modes**: Solo (individual) and Group (collaborative with AI moderator)

**Solo Flow**: Start session → Load user profile → Build context → Stream AI suggestions → Save to DB

**Group Flow**: Create room → Multiple users join → Each user has thread → AI analyzes compatibility → Moderates discussion → Suggests destinations for group

#### 3. Planning System (`/api/planning`)
- **Purpose**: Comprehensive trip planning with weather, POIs, flights
- **Design Pattern**: Data aggregation from multiple external APIs
- **Key Integrations**:
  - Amadeus API (flights, hotels)
  - WeatherAPI.com (forecasts)
  - Google Places (POIs, photos)
- **Storage**: `trips` table with denormalized JSON for POIs/weather

#### 4. Group Brainstorm (`/api/brainstorm/group`)
- **Purpose**: Multi-user collaborative planning with AI moderation
- **Design Pattern**: WebSocket hub with compatibility analysis engine
- **Key Decision**: AI triggers based on conversation patterns (everyone spoke, direct question, extended discussion)
- **Compatibility Scoring**: Analyzes user profiles to detect conflicts and common ground
- **Storage**: `group_conversations`, `group_participants`, `group_messages`

### Authentication & Authorization

**JWT-Based Auth**: Uses python-jose for token generation/validation. Tokens contain `user_id` and `email`.

**Optional Auth Pattern**: Most endpoints accept optional authentication via `get_current_user_optional` dependency. This allows anonymous exploration with session-based tracking.

**Key Decision**: Service key authentication for internal operations, anon key for client operations. All RLS policies enforced at Supabase level.

### Prompt Management

**YAML-Based System**: All prompts stored in `app/prompts/*.yaml` files, loaded via `PromptLoader` service.

**Why YAML?**: 
- Non-developers can edit prompts
- Version control friendly
- Supports templating with variable substitution
- Centralized prompt management

**Structure**: Each module has dedicated YAML (system.yaml, brainstorm.yaml, profiling.yaml, planning.yaml)

### Session Management

**Redis for Ephemeral State**: Active profiling/brainstorm sessions stored in Redis with TTL.

**Supabase for Persistence**: Completed sessions automatically saved to Supabase.

**Key Decision**: Redis for speed during active sessions, Supabase for durability and historical queries.

### WebSocket Architecture

**Connection Managers**: Each module has dedicated WebSocket manager (`ProfilingConnectionManager`, `GroupConnectionManager`).

**Message Types**: Structured message protocol with types: `user`, `ai_response`, `system`, `thinking`, `token` (streaming), `progress`, `validation`.

**Streaming Responses**: LLM responses streamed token-by-token for perceived performance improvement.

### Background Jobs (Celery)

**Purpose**: Asynchronous processing of expensive operations (flight deal monitoring, batch recommendations).

**Architecture**: Celery with Redis broker/backend.

**Current Status**: Infrastructure in place, tasks not yet implemented (marked as TODO).

## External Dependencies

### LLM Providers
- **OpenAI** (primary): GPT-4o for brainstorming, GPT-4o-mini for profiling
- **Anthropic** (fallback): Claude 3 Sonnet
- **LangChain**: Abstraction layer for LLM interactions, memory management, streaming

### Database & Storage
- **Supabase**: PostgreSQL database with REST API, real-time subscriptions, RLS policies
- **Redis**: Session storage, Celery broker/backend
- **Key Tables**: 
  - `users`, `profiling_sessions`, `profiling_responses`, `conversations`, `messages`
  - `group_conversations`, `group_participants`, `group_messages`
  - `trips`, `destinations`

### External APIs
- **Amadeus Travel API**: Flight search, hotel bookings (test mode implemented)
- **WeatherAPI.com**: Weather forecasts (7-day), air quality
- **Google Places API**: Place search, photos, POI details

### Infrastructure
- **FastAPI**: ASGI web framework with automatic OpenAPI docs
- **Uvicorn**: ASGI server with WebSocket support
- **Docker**: Containerization with multi-stage builds
- **Pydantic**: Data validation and settings management

### Authentication & Security
- **python-jose**: JWT token handling
- **passlib + bcrypt**: Password hashing
- **python-dotenv**: Environment configuration

### Utilities
- **PyYAML**: Prompt configuration loading
- **httpx**: Async HTTP client for external APIs
- **unidecode**: Text normalization for location queries
- **python-dateutil**: Date/time parsing