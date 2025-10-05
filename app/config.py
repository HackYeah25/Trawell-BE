"""
Application configuration management using Pydantic Settings
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "Travel AI Assistant"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    port: int = 8000
    host: str = "0.0.0.0"

    # API Keys
    openai_api_key: str = Field(default="", description="OpenAI API key")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")

    # Supabase
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon key")
    supabase_service_key: str = Field(default="", description="Supabase service key")

    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/travel_ai",
        description="PostgreSQL connection string"
    )

    # Authentication
    secret_key: str = Field(..., description="Secret key for JWT encoding")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # External APIs
    amadeus_api_key: str = Field(default="", description="Amadeus API key")
    amadeus_api_secret: str = Field(default="", description="Amadeus API secret")
    skyscanner_api_key: str = Field(default="", description="Skyscanner API key")
    weather_api_key: str = Field(default="", description="Weather API key")
    google_maps_api_key: str = Field(default="", description="Google Maps API key")
    google_flights_api_key: str = Field(default="", description="Google Flights API key")
    google_places_api_key: str = Field(default="", description="Google Places API key")

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LangChain
    langchain_tracing_v2: bool = False
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str = Field(default="", description="LangSmith API key")
    langchain_project: str = "travel-ai-assistant"

    # LLM Configuration
    default_llm_model: str = "gpt-4-turbo-preview"
    generic_llm_model: str = "gpt-4o-2024-08-06"
    profiling_llm_model: str = "gpt-4o-2024-08-06"
    claude_model: str = "claude-3-sonnet-20240229"
    default_llm_temperature: float = 0.7
    max_tokens_context: int = 8000
    max_tokens_response: int = 2000

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"

    # Logging
    log_level: str = "INFO"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()
