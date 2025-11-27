"""
Core Configuration Module
AI Language Tutor App - Personal Family Educational Tool
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Basic app settings
    DEBUG: bool = Field(default=True, description="Debug mode")
    HOST: str = Field(default="localhost", description="Host to bind to")
    PORT: int = Field(default=8000, description="Port for FastAPI backend")
    FRONTEND_PORT: int = Field(default=3000, description="Port for FastHTML frontend")
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for sessions",
    )

    # Database settings
    DATABASE_URL: str = Field(
        default="sqlite:///./data/local/app.db",
        description="Primary database connection URL (SQLite)",
    )
    CHROMADB_PATH: str = Field(
        default="./data/chromadb", description="ChromaDB storage path"
    )
    DUCKDB_PATH: str = Field(
        default="./data/local/app.duckdb", description="DuckDB local storage path"
    )

    # API Keys (loaded from environment)
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None, description="Anthropic Claude API key"
    )
    MISTRAL_API_KEY: Optional[str] = Field(
        default=None, description="Mistral AI API key"
    )
    DEEPSEEK_API_KEY: Optional[str] = Field(
        default=None, description="DeepSeek AI API key (primary Chinese AI service)"
    )
    QWEN_API_KEY: Optional[str] = Field(
        default=None,
        description="[DEPRECATED] Alibaba Qwen API key - use DEEPSEEK_API_KEY instead",
    )
    # IBM Watson configuration removed in Phase 2A Migration
    # Replaced by Mistral STT + Piper TTS for 99.8% cost reduction

    # Ollama settings for local LLMs
    OLLAMA_HOST: str = Field(
        default="http://localhost:11434", description="Ollama server URL"
    )

    # Budget management
    MONTHLY_BUDGET_USD: float = Field(
        default=30.0, description="Monthly API budget in USD"
    )
    COST_TRACKING_ENABLED: bool = Field(
        default=True, description="Enable cost tracking"
    )

    # Security settings
    JWT_SECRET_KEY: str = Field(
        default="jwt-secret-key-change-in-production", description="JWT signing key"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration"
    )

    # File upload settings
    MAX_UPLOAD_SIZE: int = Field(
        default=50 * 1024 * 1024, description="Max file upload size (50MB)"
    )
    UPLOAD_DIR: str = Field(default="./data/uploads", description="Upload directory")

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create directories if they don't exist
def ensure_directories():
    """Ensure required directories exist"""
    get_settings()
    directories = [
        "./data",
        "./data/local",
        "./data/uploads",
        "./data/chromadb",
        "./logs",
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Initialize directories on import
ensure_directories()
