# Travel AI Assistant - Backend Architecture Kickoff Brief

## Project Overview
An AI-powered travel planning application that helps users discover destinations, plan trips, and get on-site support through conversational AI. The system uses user profiling to provide personalized recommendations and handles both individual and group brainstorming sessions.

---

## Core Modules

### 1. **BRAINSTORM** - Destination Discovery
- **User profiling** through conversational AI (text-based, not sliders)
- **Destination suggestions** based on user profile
- **Seasonality & deals** - automated detection of cheap flights and optimal seasons
- **Cron job monitoring** - periodic checking for deals matching user profile
- **Group brainstorming** mode - multiple users collaborate with AI as 5th team member
  - Each user has their own chat thread
  - System stores all conversations ("Kasia said X, Michał said Y")
  - Manual trigger to invoke AI with full backlog
  - AI analyzes all participants and suggests destinations
  - Iterative process with AI responding to group discussion

### 2. **PLANNING** - Trip Preparation
- **Flight search & comparison** (Skyscanner/Google Flights API integration)
- **Weather forecast** for destination
- **Cultural considerations** (dress code, customs, vaccination requirements)
- **Practical info:**
  - Opening hours of attractions
  - Ticket prices (free days in museums)
  - Tourist traffic intensity
  - Local events (concerts, strikes, marathons)
  - Climate hazards/natural disasters
- **Points of interest** - highlights without excessive detail
- **Optional:** Google Maps integration with pins

### 3. **ON-SITE SUPPORT** (Optional/Nice-to-have)
- **On-the-fly AI chat** - "today I'd like to walk around" / "today museum"
- **Local transport suggestions**
- **Useful local apps**
- Delegates navigation to Google Maps (don't duplicate functionality)

---

## Tech Stack

### Backend Framework
- **FastAPI** (Python)
  - Port: 8000
  - RESTful endpoints
  - WebSocket support for streaming responses (UX boost)
  
### LLM Framework
- **LangChain**
  - Built-in connectors
  - Chain prompts together
  - Prompt library management
  - **Automatic conversation context management** (intelligent truncation when context window exceeded)
  - Sugar coating for easier LLM operations

### Database
- **Supabase** (PostgreSQL)
  - Store user profiles (JSON format)
  - Store conversation histories
  - Easy MCP integration
  - Instance already available

### External APIs (to evaluate)
- Skyscanner API or Google Flights API
- Weather API (multiple free options available)
- Google Maps API (optional for pins/POIs)
- Event APIs (concerts, sports, local events)

---

## Architecture Principles

### 1. User Profile = System Prompt #1
```
CRITICAL: User profile must be the FIRST prompt in EVERY conversation

Structure:
"Our user has a profile containing the following information:
[JSON from Supabase]"

This profile is:
- Fetched from Supabase at the start of every new conversation
- Placed at the beginning of context/history
- Applied to ALL modules: brainstorm, planning, on-site support
```

### 2. Prompt Management
- **Store ALL prompts in YAML files** (NOT hardcoded in code)
- Easier editing without refactoring
- Version control friendly
- Same prompt infrastructure for solo & group modes
- Different prompt sets for different modes, same codebase

### 3. Context Flow Between Stages
```
Stage 1: User Profile Creation
↓ (profile stored in Supabase)
Stage 2: Brainstorm (profile loaded as Prompt #1)
↓ (destination + preferences context)
Stage 3: Planning (profile + destination context)
↓ (itinerary context)
Stage 4: On-site Support (profile + itinerary context)
```

### 4. LangChain Integration Points
- Conversation memory management
- Multi-step reasoning chains
- Tool/API orchestration (flights, weather, events)
- Prompt template library
- Agent-based architecture for complex queries

---

## Data Models

### User Profile (Supabase - JSON)
```json
{
  "user_id": "uuid",
  "preferences": {
    "traveler_type": "explorer|relaxer|mixed",
    "activity_level": "low|medium|high",
    "accommodation_style": "all_inclusive|boutique|hostel|mixed",
    "environment": "city|nature|beach|mountains|mixed",
    "budget_sensitivity": "low|medium|high",
    "culture_interest": "low|medium|high",
    "food_importance": "low|medium|high"
  },
  "constraints": {
    "dietary_restrictions": [],
    "mobility_limitations": [],
    "climate_preferences": []
  },
  "past_destinations": [],
  "wishlist_regions": [],
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Conversation History (Supabase)
```json
{
  "conversation_id": "uuid",
  "user_id": "uuid",
  "module": "brainstorm|planning|support",
  "mode": "solo|group",
  "messages": [
    {
      "role": "user|assistant|system",
      "content": "string",
      "timestamp": "timestamp",
      "metadata": {}
    }
  ],
  "group_participants": ["user_id1", "user_id2"],
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Destination Recommendation
```json
{
  "recommendation_id": "uuid",
  "user_id": "uuid",
  "destination": {
    "name": "string",
    "country": "string",
    "coordinates": {"lat": 0, "lng": 0}
  },
  "reasoning": "string",
  "optimal_season": "string",
  "estimated_budget": "number",
  "highlights": [],
  "deals_found": [],
  "status": "suggested|saved|booked|visited",
  "created_at": "timestamp"
}
```

---

## API Endpoints Structure

### Authentication & Users
```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/users/profile
PUT    /api/users/profile
```

### Brainstorm Module
```
POST   /api/brainstorm/start              # Create new brainstorm session
POST   /api/brainstorm/{id}/message       # Send message in session
GET    /api/brainstorm/{id}/suggestions   # Get AI suggestions
POST   /api/brainstorm/{id}/group/invite  # Invite users to group session
WS     /api/brainstorm/{id}/stream        # WebSocket for streaming responses
```

### Planning Module
```
POST   /api/planning/create                    # Create trip plan for destination
GET    /api/planning/{id}                      # Get trip plan details
POST   /api/planning/{id}/flights              # Search flights
POST   /api/planning/{id}/weather              # Get weather forecast
POST   /api/planning/{id}/poi                  # Get points of interest
POST   /api/planning/{id}/events               # Get local events
PUT    /api/planning/{id}/customize            # Customize itinerary
```

### On-site Support Module
```
POST   /api/support/{trip_id}/chat        # Chat with AI on-site
GET    /api/support/{trip_id}/nearby      # Get nearby recommendations
POST   /api/support/{trip_id}/emergency   # Emergency info & contacts
```

### Cron Jobs (Background Tasks)
```
/api/jobs/deal-monitor     # Monitor flight deals for user profiles
/api/jobs/seasonal-alerts  # Alert users about optimal seasons
```

---

## LangChain Architecture

### Chain Structure

#### 1. Profile Builder Chain
```python
ProfileBuilderChain:
  - Input: User responses to conversational questions
  - Process: Extract preferences, validate completeness
  - Output: Structured user profile JSON
  - Store: Supabase user_profiles table
```

#### 2. Destination Discovery Chain
```python
DestinationDiscoveryChain:
  - Input: User profile + current date + budget constraints
  - Tools: 
    - Flight price checker (Skyscanner API)
    - Weather API
    - Seasonality knowledge base
  - Process: Multi-step reasoning about destinations
  - Output: Ranked list of destinations with reasoning
```

#### 3. Trip Planning Chain
```python
TripPlanningChain:
  - Input: User profile + chosen destination + dates
  - Tools:
    - Flight search
    - Weather forecast
    - POI database
    - Event APIs
    - Cultural guidelines DB
  - Process: Build comprehensive trip plan
  - Output: Structured itinerary with all details
```

#### 4. Group Brainstorm Orchestrator
```python
GroupBrainstormChain:
  - Input: Multiple user profiles + all conversation histories
  - Process:
    1. Aggregate all user preferences
    2. Find common ground
    3. Identify conflicts
    4. Suggest destinations satisfying most criteria
  - Output: Ranked destinations with reasoning per participant
```

---

## File Structure Proposal

```
travel-ai-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Environment variables, settings
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependency injection
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── brainstorm.py          # Brainstorm module endpoints
│   │   ├── planning.py            # Planning module endpoints
│   │   ├── support.py             # On-site support endpoints
│   │   └── websocket.py           # WebSocket handlers
│   │
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── base.py                # Base chain classes
│   │   ├── profile_builder.py    # User profile creation chain
│   │   ├── destination_discovery.py
│   │   ├── trip_planner.py
│   │   └── group_orchestrator.py
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── loader.py              # YAML prompt loader
│   │   ├── brainstorm.yaml        # Brainstorm prompts
│   │   ├── planning.yaml          # Planning prompts
│   │   ├── support.yaml           # Support prompts
│   │   └── system.yaml            # System prompts (user profile template)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User & profile models
│   │   ├── conversation.py        # Conversation models
│   │   ├── destination.py         # Destination models
│   │   └── trip.py                # Trip planning models
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── supabase.py            # Supabase client & operations
│   │   ├── langchain_service.py   # LangChain wrapper
│   │   ├── flights.py             # Flight API integration
│   │   ├── weather.py             # Weather API integration
│   │   ├── events.py              # Events API integration
│   │   └── maps.py                # Maps API integration
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_agent.py      # Deep research for destinations
│   │   └── orchestrator_agent.py  # Multi-tool orchestration
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── context_manager.py     # Conversation context handling
│   │   ├── validators.py          # Input validation
│   │   └── helpers.py             # General utilities
│   │
│   └── background/
│       ├── __init__.py
│       ├── deal_monitor.py        # Cron job for flight deals
│       └── seasonal_alerts.py     # Seasonal opportunity alerts
│
├── tests/
│   ├── test_chains/
│   ├── test_api/
│   └── test_services/
│
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Development Phases

### Phase 1: Foundation (Day 1 Morning)
- [ ] FastAPI app skeleton
- [ ] Supabase connection & models
- [ ] User profile CRUD operations
- [ ] Basic LangChain integration
- [ ] YAML prompt loader
- [ ] User profile creation chain

### Phase 2: Brainstorm Module (Day 1 Afternoon)
- [ ] Conversational profile builder
- [ ] Destination discovery chain
- [ ] Flight API integration (basic)
- [ ] Weather API integration
- [ ] REST endpoints for brainstorm
- [ ] WebSocket streaming (optional)

### Phase 3: Planning Module (Day 2 Morning)
- [ ] Trip planning chain
- [ ] POI discovery
- [ ] Event API integration
- [ ] Cultural guidelines database
- [ ] Itinerary generation
- [ ] Planning endpoints

### Phase 4: Group Features (Day 2 Afternoon - if time allows)
- [ ] Group brainstorm orchestrator
- [ ] Multi-user conversation handling
- [ ] Aggregation logic
- [ ] Group-specific endpoints

### Phase 5: Polish & Extras (Day 2 Evening - if time allows)
- [ ] On-site support module
- [ ] Background jobs (deal monitoring)
- [ ] Frontend integration testing
- [ ] Performance optimization

---

## Key Implementation Details

### 1. User Profile as Prompt #1
```python
# In every chain initialization:

def build_conversation_context(user_id: str, conversation_history: list):
    # Fetch user profile
    profile = supabase.get_user_profile(user_id)
    
    # Build system message with profile
    system_prompt = f"""
    Our user has a profile containing the following information:
    {json.dumps(profile, indent=2)}
    
    Use this profile to personalize all recommendations and responses.
    """
    
    # Construct full context
    messages = [
        {"role": "system", "content": system_prompt},
        *conversation_history
    ]
    
    return messages
```

### 2. Prompt Management with YAML
```python
# prompts/loader.py

import yaml
from pathlib import Path

class PromptLoader:
    def __init__(self, prompts_dir: Path):
        self.prompts_dir = prompts_dir
        self._cache = {}
    
    def load(self, module: str, prompt_name: str) -> str:
        cache_key = f"{module}.{prompt_name}"
        
        if cache_key not in self._cache:
            file_path = self.prompts_dir / f"{module}.yaml"
            with open(file_path, 'r') as f:
                prompts = yaml.safe_load(f)
                self._cache[cache_key] = prompts[prompt_name]
        
        return self._cache[cache_key]
```

```yaml
# prompts/brainstorm.yaml

destination_discovery:
  system: |
    You are a travel expert helping users discover their perfect destination.
    Consider seasonality, budget, and user preferences.
  
  user_query: |
    Based on my profile, suggest 3-5 destinations that would be perfect for me.
    For each destination, explain:
    - Why it matches my preferences
    - Best time to visit
    - Estimated budget
    - Key highlights
    - Current deals (if any)

group_orchestrator:
  system: |
    You are facilitating a group travel planning session.
    You have access to all participants' profiles and conversation history.
    Your goal is to find destinations that satisfy the group's diverse preferences.
  
  analysis: |
    Analyze the following group conversation and individual profiles:
    
    Participants: {participant_count}
    {participant_profiles}
    
    Conversation history:
    {conversation_history}
    
    Suggest destinations that would work for this group, explaining how each
    destination addresses different participants' needs.
```

### 3. Streaming Responses
```python
# api/websocket.py

from fastapi import WebSocket
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

@app.websocket("/api/brainstorm/{session_id}/stream")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    class WebSocketCallback(StreamingStdOutCallbackHandler):
        async def on_llm_new_token(self, token: str, **kwargs):
            await websocket.send_text(token)
    
    # Use callback in LangChain
    chain = get_chain(callbacks=[WebSocketCallback()])
    response = await chain.arun(user_input)
```

### 4. Context Management with LangChain
```python
# utils/context_manager.py

from langchain.memory import ConversationBufferWindowMemory
from langchain.memory import ConversationSummaryMemory

class AdaptiveContextManager:
    """
    Manages conversation context with automatic truncation
    when approaching token limits
    """
    
    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        self.summary_memory = ConversationSummaryMemory(llm=llm)
        self.window_memory = ConversationBufferWindowMemory(k=10)
    
    def get_context(self, conversation_id: str) -> list:
        # Get full conversation from Supabase
        messages = supabase.get_conversation(conversation_id)
        
        # Estimate token count
        estimated_tokens = estimate_tokens(messages)
        
        if estimated_tokens > self.max_tokens:
            # Use summary for older messages
            summary = self.summary_memory.summarize(messages[:-10])
            recent = messages[-10:]
            return [{"role": "system", "content": summary}, *recent]
        
        return messages
```

---

## Team Division Suggestions

### Developer 1: Backend Core + LangChain
- FastAPI setup
- LangChain chains (profile builder, destination discovery)
- Prompt management system
- Context management
- Core conversation logic

### Developer 2: Database + External APIs
- Supabase integration
- Data models
- Flight API integration
- Weather API integration
- Event API integration
- Background jobs (cron)

### Developer 3: Frontend Integration + Advanced Features
- REST endpoints implementation
- WebSocket streaming
- Group brainstorm orchestrator
- Frontend-backend integration
- Testing & polish

---

## Success Criteria for MVP

### Must Have:
- ✅ User profile creation through conversation
- ✅ Destination suggestions based on profile
- ✅ Flight search integration
- ✅ Weather forecast
- ✅ Basic trip planning
- ✅ User profile persisted as Prompt #1
- ✅ All prompts in YAML

### Nice to Have:
- ✅ Group brainstorming mode
- ✅ WebSocket streaming
- ✅ On-site support chat
- ✅ Deal monitoring cron job
- ✅ Google Maps integration

---

## Questions to Resolve

1. **Flight API**: Skyscanner vs Google Flights vs other? (check pricing & availability)
2. **LLM Model**: GPT-4o vs Claude vs other?
3. **Deployment**: Where will this run? (Docker, cloud, serverless?)
4. **Rate limiting**: How to handle API rate limits?
5. **Caching**: Should we cache flight/weather data?
6. **Authentication**: JWT, OAuth, or simple token-based?

---

## Next Steps

1. Set up development environment
2. Create Supabase schema
3. Initialize FastAPI project with structure above
4. Implement Phase 1 (Foundation)
5. Test basic user profile flow end-to-end
6. Iterate based on findings

Let's build something awesome! 🚀