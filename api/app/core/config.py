"""
Configuration management for the API
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_VERSION: str = Field(default="v1", env="API_VERSION")
    PROJECT_NAME: str = "MarketingIQ Google Ads API"
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Database - Connected to marketing_warehouse.db
    # On Render, database is copied to api directory during build
    DATABASE_URL: str = Field(
        default="sqlite:///./marketing_warehouse.db",
        env="DATABASE_URL"
    )

    # CORS - Can be set as comma-separated string or JSON array
    # Example: "https://frontend.onrender.com,https://www.example.com"
    # Or: ["https://frontend.onrender.com", "https://www.example.com"]
    CORS_ORIGINS: Optional[str] = Field(
        default=None,
        env="CORS_ORIGINS"
    )

    # Pagination
    PAGINATION_DEFAULT_LIMIT: int = Field(default=100, env="PAGINATION_DEFAULT_LIMIT")
    PAGINATION_MAX_LIMIT: int = Field(default=1000, env="PAGINATION_MAX_LIMIT")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'  # Ignore extra fields from .env file
    )

settings = Settings()