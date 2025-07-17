"""
Core configuration settings for the Sistema Mayra API.
"""
import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    """Database configuration."""
    url: str = Field(..., env="DATABASE_URL")
    echo: bool = Field(False, env="DATABASE_ECHO")
    pool_size: int = Field(10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(20, env="DATABASE_MAX_OVERFLOW")


class ChromaSettings(BaseModel):
    """ChromaDB configuration."""
    persist_directory: str = Field("./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    collection_name: str = Field("nutrition_recipes", env="CHROMA_COLLECTION_NAME")


class RedisSettings(BaseModel):
    """Redis configuration."""
    url: str = Field("redis://localhost:6379", env="REDIS_URL")
    ttl: int = Field(3600, env="REDIS_TTL")  # 1 hour default


class OpenAISettings(BaseModel):
    """OpenAI API configuration."""
    api_key: str = Field(..., env="OPENAI_API_KEY")
    model: str = Field("gpt-4", env="OPENAI_MODEL")
    temperature: float = Field(0.7, env="OPENAI_TEMPERATURE")
    max_tokens: int = Field(4000, env="OPENAI_MAX_TOKENS")
    timeout: int = Field(60, env="OPENAI_TIMEOUT")


class TelegramSettings(BaseModel):
    """Telegram bot configuration."""
    bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    webhook_url: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_URL")
    webhook_path: str = Field("/telegram/webhook", env="TELEGRAM_WEBHOOK_PATH")


class APISettings(BaseModel):
    """API server configuration."""
    host: str = Field("0.0.0.0", env="API_HOST")
    port: int = Field(8000, env="API_PORT")
    debug: bool = Field(False, env="API_DEBUG")
    reload: bool = Field(False, env="API_RELOAD")
    workers: int = Field(1, env="API_WORKERS")


class SecuritySettings(BaseModel):
    """Security configuration."""
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    
    # Core settings
    project_name: str = Field("Sistema Mayra API", env="PROJECT_NAME")
    version: str = Field("1.0.0", env="VERSION")
    description: str = Field(
        "API for Sistema Mayra - Nutrition Plan Generation System",
        env="DESCRIPTION"
    )
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    chroma: ChromaSettings = ChromaSettings()
    redis: RedisSettings = RedisSettings()
    openai: OpenAISettings = OpenAISettings()
    telegram: TelegramSettings = TelegramSettings()
    api: APISettings = APISettings()
    security: SecuritySettings = SecuritySettings()
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(None, env="LOG_FILE")
    
    # CORS
    cors_origins: list[str] = Field(
        ["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    # PDF Generation
    pdf_template_path: str = Field("./static/templates/", env="PDF_TEMPLATE_PATH")
    pdf_output_path: str = Field("./static/pdfs/", env="PDF_OUTPUT_PATH")
    
    # N8N Integration
    n8n_webhook_url: Optional[str] = Field(None, env="N8N_WEBHOOK_URL")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()