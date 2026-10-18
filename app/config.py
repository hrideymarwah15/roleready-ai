"""
Application settings and configuration.
Uses Pydantic Settings for environment management.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    api_title: str = "AI-Adaptive Onboarding Engine"
    api_version: str = "1.0.0"

    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # CORS Configuration
    cors_origins: str = "*"

    # OpenAI Configuration
    openai_api_key: str = ""

    # Feature Flags
    enable_openai: bool = True
    enable_caching: bool = True

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
