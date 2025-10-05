# Travel AI Assistant - Backend

An AI-powered travel planning application that helps users discover destinations, plan trips, and get on-site support through conversational AI.

## 🚀 Features

- **User Profiling**: Conversational AI-based user profiling with LangChain
- **Destination Discovery**: AI-powered destination suggestions based on user profiles
- **Trip Planning**: Comprehensive trip plans with weather, POIs, events, and cultural info
- **Group Brainstorming**: Collaborative destination discovery with multiple users
- **On-site Support**: Real-time AI assistance while traveling
- **Technical Details**: Location-specific technical information (weather, timezone, currency, etc.)
- **Google Places Integration**: Photo retrieval and place information
- **Amadeus Flight API**: Flight search and booking integration

## 🏗️ Tech Stack

- **Framework**: FastAPI (Python 3.13)
- **LLM**: LangChain with OpenAI/Anthropic integration
- **Database**: Supabase (PostgreSQL)
- **Background Jobs**: Celery + Redis
- **External APIs**: Google Places, Amadeus, Weather services
- **Deployment**: Docker + Docker Compose
- **Testing**: pytest with comprehensive test suite

## 📁 Project Structure

```
Trawell-BE/
├── app/
│   ├── api/                    # API endpoints (auth, brainstorm, planning, etc.)
│   ├── agents/                 # LangChain agents (brainstorm, planning, profiling)
│   ├── models/                 # Pydantic models (user, destination, trip, etc.)
│   ├── services/               # External services (Supabase, Google Places, Amadeus)
│   ├── prompts/                # YAML prompt files (brainstorm, planning, profiling)
│   ├── utils/                  # Utilities (context manager)
│   ├── background/             # Background jobs (Celery)
│   ├── config.py               # Configuration management
│   └── main.py                 # FastAPI application
├── tests/                      # Test suite (integration tests)
├── supabase/                   # Database migrations and seeds
├── docs/                       # Additional documentation
├── examples/                    # Example clients and usage
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── Makefile                    # Development commands
└── run.sh                      # Quick start script
```

## 🛠️ Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Trawell-BE
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `SUPABASE_SERVICE_KEY`: Your Supabase service key (for admin operations)
- `OPENAI_API_KEY`: OpenAI API key for LLM
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)
- `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)
- `GOOGLE_MAPS_API_KEY`: Google Maps/Places API key
- `AMADEUS_API_KEY`: Amadeus API key for flight data
- `AMADEUS_API_SECRET`: Amadeus API secret
- `WEATHER_API_KEY`: Weather service API key

### 5. Set up Supabase

The project includes database migrations in the `supabase/migrations/` directory. Run the migrations:

```bash
# Using the migration script
python run_migration.py

# Or manually run the SQL files
# 001_group_conversations.sql
# 002_profiling_sessions.sql  
# 003_add_logistics_data.sql
```

Key tables created:
- `user_profiles` - User preferences and constraints
- `conversations` - Chat sessions and messages
- `destination_recommendations` - AI-generated destination suggestions
- `trip_plans` - Detailed trip planning data
- `group_conversations` - Multi-user brainstorming sessions
- `profiling_sessions` - User profiling conversation data

### 6. Run the application

#### Option A: Local Development

```bash
# Development mode
uvicorn app.main:app --reload --port 8000

# Or using the main script
python -m app.main

# Or using the run script
./run.sh
```

#### Option B: Docker (Recommended)

```bash
# Using docker-compose
docker-compose up -d

# Or using Makefile
make docker-up

# View logs
docker-compose logs -f backend
```

The API will be available at `http://localhost:8000`

See [DOCKER.md](DOCKER.md) for detailed Docker documentation.

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs (Interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (Beautiful documentation)
- **API Reference**: [API.md](API.md) (Detailed endpoint documentation)

## 🔑 Key Architecture Principles

### 1. User Profile as Prompt #1
Every conversation starts with the user profile loaded from Supabase and injected as the first system prompt.

### 2. YAML-based Prompts
All prompts are stored in YAML files (`app/prompts/`) for easy editing without code changes.

### 3. Context Flow
```
Profile Creation → Brainstorm → Planning → On-site Support
(Each stage uses profile + previous context)
```

### 4. LangChain Integration
- Conversation memory management
- Multi-step reasoning chains
- Tool/API orchestration
- Automatic context truncation

## 🎯 API Endpoints

### Authentication & Users
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user  
- `GET /api/me` - Get current user profile
- `PATCH /api/me` - Update user profile

### Profiling
- `POST /api/profiling/start` - Start user profiling session
- `POST /api/profiling/{session_id}/message` - Send profiling message
- `GET /api/profiling/{session_id}/status` - Get profiling status
- `POST /api/profiling/{session_id}/complete` - Complete profiling

### Brainstorm
- `GET /api/brainstorm/sessions` - List brainstorm sessions
- `POST /api/brainstorm/sessions` - Create new session
- `GET /api/brainstorm/sessions/{session_id}` - Get session details
- `POST /api/brainstorm/sessions/{session_id}/recommendations` - Create recommendation
- `GET /api/brainstorm/sessions/{session_id}/recommendations` - Get recommendations
- `DELETE /api/brainstorm/sessions/{session_id}` - Delete session

### Group Brainstorm
- `POST /api/group-brainstorm/create` - Create group session
- `POST /api/group-brainstorm/{session_id}/join` - Join group session
- `POST /api/group-brainstorm/{session_id}/message` - Send group message

### Planning
- `GET /api/planning/technical-details` - Get location technical details
- `GET /api/planning/recommendations/{recommendation_id}/summary` - Get trip summary
- `WS /api/planning/ws/{recommendation_id}` - Real-time planning WebSocket

### Support
- `POST /api/support/{trip_id}/chat` - On-site chat
- `GET /api/support/{trip_id}/nearby` - Nearby recommendations
- `POST /api/support/{trip_id}/emergency` - Emergency info

### WebSocket
- `WS /api/ws/{conversation_id}/stream` - Streaming responses

## 🧪 Testing

```bash
# Run all tests
python tests/test_supabase_connection.py
python tests/test_amadeus_integration.py  
python tests/test_google_places_service.py
python tests/test_get_technical_details.py
```

Available test suites:
- **Supabase Connection** - Database connectivity and operations
- **Amadeus Integration** - Flight API authentication and search
- **Google Places** - Place search and photo retrieval
- **Technical Details** - Planning API prompt system

## 🐳 Docker Deployment

```bash
# Build image
docker build -t travel-ai-backend .

# Run container
docker run -p 8000:8000 --env-file .env travel-ai-backend
```

## 📝 Development Status

- [x] **Foundation** - FastAPI, Supabase, LangChain integration
- [x] **User Profiling** - Conversational AI-based user profiling system
- [x] **Brainstorm Module** - AI-powered destination discovery
- [x] **Group Brainstorm** - Collaborative destination discovery
- [x] **Planning Module** - Trip planning with technical details
- [x] **External APIs** - Google Places, Amadeus, Weather integration
- [x] **Testing Suite** - Comprehensive integration tests
- [x] **Docker Setup** - Production-ready containerization
- [ ] **On-site Support** - Real-time travel assistance
- [ ] **Background Jobs** - Automated deal monitoring

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd Trawell-BE
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run migrations
python run_migration.py



## 📚 Additional Documentation

- [QUICKSTART.md](QUICKSTART.md) - Detailed quick start guide
- [API.md](API.md) - Complete API reference
- [DOCKER.md](DOCKER.md) - Docker deployment guide
- [PROFILING_SYSTEM.md](PROFILING_SYSTEM.md) - User profiling system
- [GROUP_BRAINSTORM.md](docs/GROUP_BRAINSTORM.md) - Group features


## 🙋 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, LangChain, and Supabase
