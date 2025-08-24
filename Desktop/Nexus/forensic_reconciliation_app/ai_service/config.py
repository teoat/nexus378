"""
AI Service Configuration Management
This module provides a centralized and type-safe way to manage
configuration for the AI service, using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class DatabaseSettings(BaseSettings):
    """Database connection settings."""
    url: str = "sqlite:///./test.db"
    pool_size: int = 5
    pool_recycle: int = 3600

class RedisSettings(BaseSettings):
    """Redis connection settings."""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None

class RabbitMQSettings(BaseSettings):
    """RabbitMQ connection settings."""
    url: str = "amqp://guest:guest@localhost:5672/"

class MinioSettings(BaseSettings):
    """MinIO connection settings."""
    endpoint: str = "localhost:9000"
    access_key: str
    secret_key: str

class AIServiceSettings(BaseSettings):
    """Settings for the AI models and services."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm: str = "openai"
    model_cache_size: int = 100

class AppSettings(BaseSettings):
    """
    Main application settings.
    Settings are loaded from environment variables and .env files.
    Environment variables have higher precedence.
    """
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        extra='ignore'
    )

    # General settings
    app_name: str = "Forensic AI Service"
    debug: bool = False
    log_level: str = "INFO"

    # Service-specific settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    minio: MinioSettings
    ai: AIServiceSettings = AIServiceSettings()


# Global instance of the settings
settings = AppSettings()

# You can now import `settings` from this module anywhere in the ai_service
# and access configuration like:
#
# from ai_service.config import settings
#
# db_url = settings.database.url
# if settings.debug:
#     print("Running in debug mode")
