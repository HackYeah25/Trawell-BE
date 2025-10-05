"""
Travel AI Assistant - FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api import auth, brainstorm, planning, support, websocket, group_brainstorm, profiling, users, trips

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Initialize FastAPI app with enhanced Swagger documentation
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Travel AI Assistant Backend API

    An AI-powered travel planning application that helps users discover destinations, plan trips,
    and get on-site support through conversational AI.

    ### Features

    * 🧭 **Brainstorm**: AI-powered destination discovery based on user profiles
    * 📋 **Planning**: Comprehensive trip planning with weather, POIs, and events
    * 👥 **Group Mode**: Collaborative destination discovery
    * 📱 **On-site Support**: Real-time AI assistance while traveling
    * 💰 **Deal Monitoring**: Automated flight deal detection

    ### Architecture

    - **LLM**: LangChain with OpenAI/Anthropic
    - **Database**: Supabase (PostgreSQL)
    - **Framework**: FastAPI
    - **User Profile as Prompt #1**: Every conversation starts with user profile context
    - **YAML-based Prompts**: All prompts stored in YAML files for easy management

    ### Authentication

    Most endpoints require JWT Bearer token authentication.
    Get your token from `/api/auth/login` endpoint.
    """,
    debug=settings.debug,
    lifespan=lifespan,
    contact={
        "name": "Travel AI Team",
        "email": "support@travelai.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints"
        },
        {
            "name": "Brainstorm",
            "description": "Destination discovery and brainstorming sessions. Start here to find your perfect destination!"
        },
        {
            "name": "Group Brainstorm",
            "description": "Collaborative group travel planning with AI moderation and conflict resolution"
        },
        {
            "name": "Planning",
            "description": "Trip planning endpoints - flights, weather, POIs, events, and itinerary"
        },
        {
            "name": "Support",
            "description": "On-site support for travelers - real-time help and recommendations"
        },
        {
            "name": "WebSocket",
            "description": "WebSocket connections for streaming AI responses"
        },
        {
            "name": "Profiling",
            "description": "Interactive user profiling with AI-guided questions and validation"
        },
        {
            "name": "Trips",
            "description": "Trip management endpoints - view and manage user trips and destination recommendations"
        }
    ],
    servers=[
        {
            "url": "http://localhost:5000",
            "description": "Development server"
        },
        {
            "url": "https://api.travelai.com",
            "description": "Production server"
        }
    ]
)

# CORS Middleware
# In development, allow all localhost ports
if settings.is_development:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://localhost:\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )


# Health check endpoint
@app.get(
    "/",
    tags=["System"],
    summary="API Status",
    description="Get the API status and version information"
)
async def root():
    """Root endpoint - API status"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    description="Health check endpoint for monitoring and load balancers"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "travel-ai-backend",
        "version": settings.app_version
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profiling.router, tags=["Profiling"])
app.include_router(brainstorm.router, tags=["Brainstorm"])  # Router already has /api/brainstorm prefix
app.include_router(group_brainstorm.router, tags=["Group Brainstorm"])
app.include_router(planning.router, prefix="/api/planning", tags=["Planning"])
app.include_router(support.router, prefix="/api/support", tags=["Support"])
app.include_router(websocket.router, prefix="/api/ws", tags=["WebSocket"])
app.include_router(users.router, tags=["User"])  # Provides /api/me endpoints
app.include_router(trips.router, tags=["Trips"])  # Provides /api/trips endpoints


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
