# Travel AI Assistant - Backend

An AI-powered travel planning application that helps users discover destinations, plan trips, and get on-site support through conversational AI.

## 🚀 Features

- **User Profiling**: Conversational AI-based user profiling (not sliders!)
- **Destination Discovery**: AI-powered destination suggestions based on user profiles
- **Trip Planning**: Comprehensive trip plans with weather, POIs, events, and cultural info
- **Group Brainstorming**: Collaborative destination discovery with multiple users
- **On-site Support**: Real-time AI assistance while traveling
- **Deal Monitoring**: Automated flight deal detection and notifications

## 🏗️ Tech Stack

- **Framework**: FastAPI (Python)
- **LLM**: LangChain (OpenAI/Anthropic)
- **Database**: Supabase (PostgreSQL)
- **Background Jobs**: Celery + Redis
- **Deployment**: Docker (ready)

## 📁 Project Structure

```
travel-ai-backend/
├── app/
│   ├── api/              # API endpoints
│   ├── chains/           # LangChain chains
│   ├── prompts/          # YAML prompt files
│   ├── models/           # Pydantic models
│   ├── services/         # External services
│   ├── agents/           # LangChain agents
│   ├── utils/            # Utilities
│   ├── background/       # Background jobs
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app
├── tests/                # Test suite
├── requirements.txt      # Dependencies
└── .env.example         # Environment template
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
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: LLM API key
- `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)

### 5. Set up Supabase

Create the following tables in your Supabase project:

```sql
-- User profiles
CREATE TABLE user_profiles (
  user_id UUID PRIMARY KEY,
  preferences JSONB,
  constraints JSONB,
  past_destinations TEXT[],
  wishlist_regions TEXT[],
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
  conversation_id TEXT PRIMARY KEY,
  user_id UUID REFERENCES user_profiles(user_id),
  module TEXT,
  mode TEXT,
  messages JSONB[],
  group_participants UUID[],
  context_summary TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Destination recommendations
CREATE TABLE destination_recommendations (
  recommendation_id TEXT PRIMARY KEY,
  user_id UUID REFERENCES user_profiles(user_id),
  destination JSONB,
  reasoning TEXT,
  optimal_season TEXT,
  estimated_budget NUMERIC,
  currency TEXT DEFAULT 'USD',
  highlights TEXT[],
  deals_found JSONB[],
  status TEXT,
  confidence_score NUMERIC,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Trip plans
CREATE TABLE trip_plans (
  trip_id TEXT PRIMARY KEY,
  user_id UUID REFERENCES user_profiles(user_id),
  destination JSONB,
  start_date TIMESTAMP,
  end_date TIMESTAMP,
  status TEXT,
  weather_forecast JSONB[],
  cultural_info JSONB,
  points_of_interest JSONB[],
  local_events JSONB[],
  daily_itinerary JSONB[],
  estimated_budget NUMERIC,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

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

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Brainstorm
- `POST /api/brainstorm/start` - Start brainstorm session
- `POST /api/brainstorm/{id}/message` - Send message
- `GET /api/brainstorm/{id}/suggestions` - Get suggestions
- `POST /api/brainstorm/{id}/group/invite` - Invite to group

### Planning
- `POST /api/planning/create` - Create trip plan
- `GET /api/planning/{id}` - Get trip details
- `POST /api/planning/{id}/flights` - Search flights
- `POST /api/planning/{id}/weather` - Get weather
- `POST /api/planning/{id}/poi` - Get points of interest
- `POST /api/planning/{id}/events` - Get local events

### Support
- `POST /api/support/{trip_id}/chat` - On-site chat
- `GET /api/support/{trip_id}/nearby` - Nearby recommendations
- `POST /api/support/{trip_id}/emergency` - Emergency info

### WebSocket
- `WS /api/ws/{conversation_id}/stream` - Streaming responses

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t travel-ai-backend .

# Run container
docker run -p 8000:8000 --env-file .env travel-ai-backend
```

## 📝 Development Phases

- [x] Phase 1: Foundation (FastAPI, Supabase, LangChain)
- [ ] Phase 2: Brainstorm Module
- [ ] Phase 3: Planning Module
- [ ] Phase 4: Group Features
- [ ] Phase 5: On-site Support & Background Jobs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

[Your License Here]

## 🙋 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, LangChain, and Supabase
