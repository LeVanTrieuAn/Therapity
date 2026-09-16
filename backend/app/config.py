"""
Therapity — Application Configuration
Centralized settings loaded from environment variables.
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from .env file and environment variables."""

    # --- App ---
    APP_NAME: str = "Therapity"
    APP_VERSION: str = "4.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://therapity:therapity_dev@db:5432/therapity"
    DATABASE_ECHO: bool = False

    # --- JWT ---
    JWT_SECRET_KEY: str = "change-me-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # --- LLM (OpenRouter) ---
    OPENROUTER_API_KEY: str = ""
    LLM_MODEL: str = "google/gemini-2.0-flash-exp:free"

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # --- Rate Limiting ---
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once on first call."""
    return Settings()
