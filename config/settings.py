"""
Sistema Mayra - Main Settings Configuration
Loads environment variables and provides configuration classes for the application.
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv


class BaseSettings:
    """Base configuration class with common settings."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize settings with optional environment file."""
        if env_file:
            load_dotenv(env_file, override=True)
        else:
            load_dotenv()
    
    @classmethod
    def get_env_bool(cls, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        return os.getenv(key, str(default)).lower() in ('true', '1', 'yes', 'on')
    
    @classmethod
    def get_env_int(cls, key: str, default: int = 0) -> int:
        """Get integer environment variable."""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @classmethod
    def get_env_float(cls, key: str, default: float = 0.0) -> float:
        """Get float environment variable."""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @classmethod
    def get_env_list(cls, key: str, default: List[str] = None, separator: str = ',') -> List[str]:
        """Get list environment variable."""
        if default is None:
            default = []
        value = os.getenv(key, '')
        if not value:
            return default
        return [item.strip() for item in value.split(separator) if item.strip()]


@dataclass
class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    # PostgreSQL
    postgres_host: str = field(default_factory=lambda: os.getenv('POSTGRES_HOST', 'localhost'))
    postgres_port: int = field(default_factory=lambda: BaseSettings.get_env_int('POSTGRES_PORT', 5432))
    postgres_user: str = field(default_factory=lambda: os.getenv('POSTGRES_USER', 'postgres'))
    postgres_password: str = field(default_factory=lambda: os.getenv('POSTGRES_PASSWORD', 'password'))
    postgres_db: str = field(default_factory=lambda: os.getenv('POSTGRES_DB', 'nutrition_db'))
    postgres_ssl: bool = field(default_factory=lambda: BaseSettings.get_env_bool('POSTGRES_SSL', False))
    
    # Redis
    redis_host: str = field(default_factory=lambda: os.getenv('REDIS_HOST', 'localhost'))
    redis_port: int = field(default_factory=lambda: BaseSettings.get_env_int('REDIS_PORT', 6379))
    redis_password: str = field(default_factory=lambda: os.getenv('REDIS_PASSWORD', ''))
    redis_db: int = field(default_factory=lambda: BaseSettings.get_env_int('REDIS_DB', 0))
    
    # ChromaDB
    chroma_persist_directory: str = field(default_factory=lambda: os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db'))
    chroma_collection_name: str = field(default_factory=lambda: os.getenv('CHROMA_COLLECTION_NAME', 'nutrition_recipes'))
    
    # Database URLs
    database_url: str = field(default='')
    redis_url: str = field(default='')
    
    def __post_init__(self):
        """Generate database URLs after initialization."""
        if not self.database_url:
            ssl_param = '?sslmode=require' if self.postgres_ssl else ''
            self.database_url = f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}{ssl_param}"
        
        if not self.redis_url:
            if self.redis_password:
                self.redis_url = f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
            else:
                self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@dataclass
class APISettings(BaseSettings):
    """API configuration settings."""
    
    # FastAPI
    api_host: str = field(default_factory=lambda: os.getenv('API_HOST', '0.0.0.0'))
    api_port: int = field(default_factory=lambda: BaseSettings.get_env_int('API_PORT', 8000))
    debug: bool = field(default_factory=lambda: BaseSettings.get_env_bool('DEBUG', False))
    reload: bool = field(default_factory=lambda: BaseSettings.get_env_bool('RELOAD', False))
    
    # Security
    secret_key: str = field(default_factory=lambda: os.getenv('SECRET_KEY', 'your-secret-key-change-in-production'))
    algorithm: str = field(default_factory=lambda: os.getenv('ALGORITHM', 'HS256'))
    access_token_expire_minutes: int = field(default_factory=lambda: BaseSettings.get_env_int('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    
    # CORS
    allowed_origins: List[str] = field(default_factory=lambda: BaseSettings.get_env_list('ALLOWED_ORIGINS', ['http://localhost:3000']))
    allowed_methods: List[str] = field(default_factory=lambda: BaseSettings.get_env_list('ALLOWED_METHODS', ['GET', 'POST', 'PUT', 'DELETE']))
    allowed_headers: List[str] = field(default_factory=lambda: BaseSettings.get_env_list('ALLOWED_HEADERS', ['*']))
    
    # Rate limiting
    rate_limit_requests: int = field(default_factory=lambda: BaseSettings.get_env_int('RATE_LIMIT_REQUESTS', 100))
    rate_limit_window: int = field(default_factory=lambda: BaseSettings.get_env_int('RATE_LIMIT_WINDOW', 60))


@dataclass
class AISettings(BaseSettings):
    """AI and ML configuration settings."""
    
    # OpenAI
    openai_api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    openai_model: str = field(default_factory=lambda: os.getenv('OPENAI_MODEL', 'gpt-4'))
    openai_max_tokens: int = field(default_factory=lambda: BaseSettings.get_env_int('OPENAI_MAX_TOKENS', 4000))
    openai_temperature: float = field(default_factory=lambda: BaseSettings.get_env_float('OPENAI_TEMPERATURE', 0.7))
    openai_timeout: int = field(default_factory=lambda: BaseSettings.get_env_int('OPENAI_TIMEOUT', 30))
    
    # Embeddings
    embedding_model: str = field(default_factory=lambda: os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'))
    embedding_dimension: int = field(default_factory=lambda: BaseSettings.get_env_int('EMBEDDING_DIMENSION', 384))
    
    # RAG
    rag_top_k: int = field(default_factory=lambda: BaseSettings.get_env_int('RAG_TOP_K', 10))
    rag_similarity_threshold: float = field(default_factory=lambda: BaseSettings.get_env_float('RAG_SIMILARITY_THRESHOLD', 0.7))
    rag_max_context_length: int = field(default_factory=lambda: BaseSettings.get_env_int('RAG_MAX_CONTEXT_LENGTH', 2000))


@dataclass
class TelegramSettings(BaseSettings):
    """Telegram bot configuration settings."""
    
    # Bot credentials
    bot_token: str = field(default_factory=lambda: os.getenv('TELEGRAM_BOT_TOKEN', ''))
    webhook_url: str = field(default_factory=lambda: os.getenv('TELEGRAM_WEBHOOK_URL', ''))
    webhook_secret: str = field(default_factory=lambda: os.getenv('TELEGRAM_WEBHOOK_SECRET', ''))
    
    # Bot behavior
    max_message_length: int = field(default_factory=lambda: BaseSettings.get_env_int('TELEGRAM_MAX_MESSAGE_LENGTH', 4096))
    session_timeout: int = field(default_factory=lambda: BaseSettings.get_env_int('TELEGRAM_SESSION_TIMEOUT', 1800))
    max_file_size: int = field(default_factory=lambda: BaseSettings.get_env_int('TELEGRAM_MAX_FILE_SIZE', 20971520))
    
    # Admin settings
    admin_user_ids: List[str] = field(default_factory=lambda: BaseSettings.get_env_list('TELEGRAM_ADMIN_USER_IDS', []))
    allowed_user_ids: List[str] = field(default_factory=lambda: BaseSettings.get_env_list('TELEGRAM_ALLOWED_USER_IDS', []))


@dataclass
class NutritionSettings(BaseSettings):
    """Nutrition-specific configuration settings."""
    
    # Plan generation
    default_plan_days: int = field(default_factory=lambda: BaseSettings.get_env_int('DEFAULT_PLAN_DAYS', 3))
    calorie_tolerance: float = field(default_factory=lambda: BaseSettings.get_env_float('CALORIE_TOLERANCE', 0.05))
    macro_tolerance: float = field(default_factory=lambda: BaseSettings.get_env_float('MACRO_TOLERANCE', 0.05))
    
    # Meal options
    meals_per_day: int = field(default_factory=lambda: BaseSettings.get_env_int('MEALS_PER_DAY', 4))
    options_per_meal: int = field(default_factory=lambda: BaseSettings.get_env_int('OPTIONS_PER_MEAL', 3))
    
    # Weight types
    weight_types: List[str] = field(default_factory=lambda: BaseSettings.get_env_list('WEIGHT_TYPES', ['crudo', 'cocido']))
    default_weight_type: str = field(default_factory=lambda: os.getenv('DEFAULT_WEIGHT_TYPE', 'crudo'))
    
    # Economic levels
    economic_levels: List[str] = field(default_factory=lambda: BaseSettings.get_env_list('ECONOMIC_LEVELS', ['bajo', 'medio', 'alto']))
    default_economic_level: str = field(default_factory=lambda: os.getenv('DEFAULT_ECONOMIC_LEVEL', 'medio'))


@dataclass
class N8NSettings(BaseSettings):
    """n8n workflow configuration settings."""
    
    # n8n instance
    n8n_webhook_url: str = field(default_factory=lambda: os.getenv('N8N_WEBHOOK_URL', ''))
    n8n_api_key: str = field(default_factory=lambda: os.getenv('N8N_API_KEY', ''))
    n8n_base_url: str = field(default_factory=lambda: os.getenv('N8N_BASE_URL', ''))
    
    # Workflow IDs
    patient_registration_workflow_id: str = field(default_factory=lambda: os.getenv('N8N_PATIENT_REGISTRATION_WORKFLOW_ID', ''))
    plan_generation_workflow_id: str = field(default_factory=lambda: os.getenv('N8N_PLAN_GENERATION_WORKFLOW_ID', ''))
    notification_workflow_id: str = field(default_factory=lambda: os.getenv('N8N_NOTIFICATION_WORKFLOW_ID', ''))


@dataclass
class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    # General logging
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    log_format: str = field(default_factory=lambda: os.getenv('LOG_FORMAT', 'json'))
    log_file: str = field(default_factory=lambda: os.getenv('LOG_FILE', './logs/app.log'))
    
    # Specific loggers
    database_log_level: str = field(default_factory=lambda: os.getenv('DATABASE_LOG_LEVEL', 'WARNING'))
    api_log_level: str = field(default_factory=lambda: os.getenv('API_LOG_LEVEL', 'INFO'))
    bot_log_level: str = field(default_factory=lambda: os.getenv('BOT_LOG_LEVEL', 'INFO'))
    
    # Log rotation
    log_rotation_size: str = field(default_factory=lambda: os.getenv('LOG_ROTATION_SIZE', '10 MB'))
    log_retention_days: int = field(default_factory=lambda: BaseSettings.get_env_int('LOG_RETENTION_DAYS', 30))
    
    # External logging
    sentry_dsn: str = field(default_factory=lambda: os.getenv('SENTRY_DSN', ''))
    enable_sentry: bool = field(default_factory=lambda: BaseSettings.get_env_bool('ENABLE_SENTRY', False))


@dataclass
class AppSettings:
    """Main application settings that combines all configuration classes."""
    
    # Environment
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'development'))
    app_name: str = field(default_factory=lambda: os.getenv('APP_NAME', 'Sistema Mayra'))
    app_version: str = field(default_factory=lambda: os.getenv('APP_VERSION', '1.0.0'))
    
    # Component settings
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    api: APISettings = field(default_factory=APISettings)
    ai: AISettings = field(default_factory=AISettings)
    telegram: TelegramSettings = field(default_factory=TelegramSettings)
    nutrition: NutritionSettings = field(default_factory=NutritionSettings)
    n8n: N8NSettings = field(default_factory=N8NSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    
    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / 'data')
    logs_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / 'logs')
    static_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / 'static')
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Create necessary directories
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.static_dir.mkdir(exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == 'production'
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == 'development'
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == 'testing'


# Global settings instance
settings = AppSettings()


def get_settings() -> AppSettings:
    """Get application settings instance."""
    return settings


def load_settings(env_file: Optional[str] = None) -> AppSettings:
    """Load settings from environment file."""
    global settings
    
    if env_file:
        load_dotenv(env_file, override=True)
    
    settings = AppSettings()
    return settings


def validate_settings() -> Dict[str, Any]:
    """Validate all settings and return validation results."""
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Validate required settings
    required_settings = [
        ('OpenAI API Key', settings.ai.openai_api_key),
        ('Telegram Bot Token', settings.telegram.bot_token),
        ('Secret Key', settings.api.secret_key),
    ]
    
    for setting_name, setting_value in required_settings:
        if not setting_value or setting_value in ['', 'your-secret-key-change-in-production']:
            validation_results['errors'].append(f"{setting_name} is required but not set")
            validation_results['valid'] = False
    
    # Validate database connection
    if not settings.database.database_url:
        validation_results['errors'].append("Database URL is not properly configured")
        validation_results['valid'] = False
    
    # Validate paths
    if not settings.base_dir.exists():
        validation_results['errors'].append(f"Base directory does not exist: {settings.base_dir}")
        validation_results['valid'] = False
    
    # Warnings for development settings
    if settings.is_production:
        if settings.api.debug:
            validation_results['warnings'].append("Debug mode is enabled in production")
        
        if settings.api.secret_key == 'your-secret-key-change-in-production':
            validation_results['warnings'].append("Using default secret key in production")
    
    return validation_results