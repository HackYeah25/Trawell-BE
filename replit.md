# Travel AI Assistant - Replit Project

## Overview

This is a Travel AI Assistant backend built with FastAPI, LangChain, and Supabase. The application provides AI-powered travel planning, destination discovery, and trip management features through conversational AI.

**Version:** 1.0.0  
**Status:** Running in development mode on Replit  
**Last Updated:** October 5, 2025

## Project Architecture

### Tech Stack
- **Framework:** FastAPI (Python 3.11)
- **LLM Integration:** LangChain with OpenAI
- **Database:** Supabase (PostgreSQL)
- **Background Jobs:** Celery + Redis (optional)
- **Deployment:** Replit Autoscale

### Key Features
- 🧭 **User Profiling:** Conversational AI-based user profiling system
- 🌍 **Destination Discovery:** AI-powered brainstorming for travel destinations
- 📋 **Trip Planning:** Comprehensive trip plans with weather, POIs, and events
- 👥 **Group Brainstorming:** Collaborative destination discovery
- 📱 **On-site Support:** Real-time AI assistance while traveling
- 💰 **Deal Monitoring:** Automated flight deal detection

## Replit Configuration

### Environment Variables
The following secrets are configured in Replit Secrets:
- `OPENAI_API_KEY` - Required for AI features
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `SECRET_KEY` - JWT authentication secret

### Optional API Keys
These can be added later for enhanced features:
- `AMADEUS_API_KEY` / `AMADEUS_API_SECRET` - For flight search
- `GOOGLE_PLACES_API_KEY` - For POI data
- `WEATHER_API_KEY` - For weather forecasts

### Port Configuration
- **Development:** Port 5000 (configured for Replit)
- **Production:** Port 5000 (autoscale deployment)

### CORS Settings
- Development: Allows all origins without credentials
- Production: Should be restricted to specific domains

## Running the Application

### Development Mode
The application automatically runs via the configured workflow:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

### API Documentation
Once running, access the interactive API documentation at:
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

### Health Check
- **Root Endpoint:** `/` - Returns API status
- **Health Check:** `/health` - Returns service health status

## Project Structure

```
travel-ai-backend/
├── app/
│   ├── api/              # API endpoints (auth, brainstorm, planning, etc.)
│   ├── agents/           # LangChain agents for different modules
│   ├── chains/           # LangChain chain configurations
│   ├── prompts/          # YAML prompt files
│   ├── models/           # Pydantic data models
│   ├── services/         # External service integrations
│   │   ├── supabase_service.py
│   │   ├── amadeus_service.py
│   │   ├── langchain_service.py
│   │   └── weather_service.py
│   ├── utils/            # Utility functions
│   ├── background/       # Celery background tasks
│   ├── config.py         # Application configuration
│   └── main.py           # FastAPI application entry point
├── tests/                # Test suite
├── supabase/            # Database migrations and seeds
├── requirements.txt      # Python dependencies
└── replit.md            # This file
```

## Recent Changes (Replit Setup)

### October 5, 2025
1. **Environment Setup**
   - Installed Python 3.11
   - Installed all dependencies from requirements.txt
   
2. **Port Configuration**
   - Changed default port from 8000 to 5000 for Replit compatibility
   - Updated server URLs in API documentation
   - Fixed deployment configuration to explicitly specify port 5000
   
3. **CORS Configuration**
   - Set to allow all origins without credentials for development
   - Configured for Replit's iframe preview environment
   
4. **Service Fixes**
   - Implemented lazy initialization for Supabase service
   - Removed blocking database initialization from application startup
   - Fixed AmadeusService initialization to allow lazy credential validation
   - Prevents import errors when optional API credentials are not configured
   
5. **Deployment**
   - Configured autoscale deployment for production: `uvicorn app.main:app --host 0.0.0.0 --port 5000`
   - Set up workflow for automatic server startup with hot reload
   - Fast startup with no blocking operations for instant health checks

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Profiling
- `POST /api/profiling/start` - Start profiling session
- `POST /api/profiling/{session_id}/answer` - Submit answer
- `GET /api/profiling/{session_id}/status` - Get session status

### Brainstorming
- `POST /api/brainstorm/start` - Start brainstorm session
- `POST /api/brainstorm/{id}/message` - Send message
- `GET /api/brainstorm/{id}/suggestions` - Get suggestions

### Group Brainstorming
- `POST /api/group-brainstorm/create` - Create group session
- `POST /api/group-brainstorm/{id}/join` - Join session
- `WS /api/group-brainstorm/{id}/ws` - WebSocket connection

### Trip Planning
- `POST /api/planning/create` - Create trip plan
- `GET /api/planning/{id}` - Get trip details
- `POST /api/planning/{id}/flights` - Search flights
- `POST /api/planning/{id}/weather` - Get weather forecast

### Support
- `POST /api/support/{trip_id}/chat` - On-site chat support
- `GET /api/support/{trip_id}/nearby` - Nearby recommendations

## Database Setup

This application uses Supabase for data persistence. The following tables are required:

1. **user_profiles** - User travel preferences and history
2. **conversations** - Conversation history
3. **destination_recommendations** - AI-generated recommendations
4. **trip_plans** - Planned trips and itineraries
5. **group_conversations** - Group brainstorming sessions
6. **profiling_sessions** - User profiling data

Migration files are available in `supabase/migrations/`.

## Development Guidelines

### Adding New Features
1. Create API endpoints in `app/api/`
2. Add business logic in `app/services/`
3. Define data models in `app/models/`
4. Update prompts in `app/prompts/` (YAML files)

### Testing
Run tests using pytest:
```bash
pytest tests/
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function signatures
- Document all public functions and classes

## Troubleshooting

### Common Issues

**Server won't start:**
- Check that all required secrets are configured
- Verify Supabase credentials are correct
- Review workflow logs for error messages

**Import errors:**
- Ensure all dependencies are installed
- Check Python version (should be 3.11)

**Database connection errors:**
- Verify SUPABASE_URL and SUPABASE_KEY are set
- Check Supabase project status
- Ensure database tables are created

## Deployment

The application is configured for Replit Autoscale deployment:
- Automatically scales based on traffic
- Uses port 5000
- Runs: `uvicorn app.main:app --host 0.0.0.0 --port 5000`

## Resources

- **Main Documentation:** See README.md for detailed setup instructions
- **API Documentation:** See API.md for endpoint details
- **Architecture:** See ARCHITECTURE.md for system design
- **Docker:** See DOCKER.md for containerization options

## Support

For issues specific to this Replit deployment, check:
1. Workflow logs for server errors
2. Supabase dashboard for database issues
3. Replit Secrets for missing credentials

For general application issues, refer to the project documentation in the root directory.
