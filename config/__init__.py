"""
Sistema Mayra - Configuration Package
Provides comprehensive configuration management for the nutrition system.
"""

from .settings import (
    AppSettings,
    DatabaseSettings,
    APISettings,
    AISettings,
    TelegramSettings,
    NutritionSettings,
    N8NSettings,
    LoggingSettings,
    settings,
    get_settings,
    load_settings,
    validate_settings
)

from .prompts import (
    MotorType,
    PlanType,
    ActivityType,
    SystemPrompts,
    get_system_prompt_for_motor,
    build_complete_prompt,
    format_rag_context
)

from .logging import (
    LoggingConfig,
    StructuredLogger,
    setup_logging,
    get_logger,
    log_function_call,
    log_api_request,
    log_api_response,
    log_bot_message,
    log_ai_request,
    log_database_operation,
    log_plan_generation,
    LoggingContext,
    PerformanceLogger
)

from .security import (
    SecurityLevel,
    PermissionLevel,
    SecurityConfig,
    SecurityManager,
    RateLimiter,
    SecurityAuditLogger,
    get_security_manager,
    get_rate_limiter,
    get_security_audit_logger,
    initialize_security
)

__all__ = [
    # Settings
    'AppSettings',
    'DatabaseSettings',
    'APISettings',
    'AISettings',
    'TelegramSettings',
    'NutritionSettings',
    'N8NSettings',
    'LoggingSettings',
    'SecurityConfig',
    'settings',
    'get_settings',
    'load_settings',
    'validate_settings',
    
    # Prompts
    'MotorType',
    'PlanType',
    'ActivityType',
    'SystemPrompts',
    'get_system_prompt_for_motor',
    'build_complete_prompt',
    'format_rag_context',
    
    # Logging
    'LoggingConfig',
    'StructuredLogger',
    'setup_logging',
    'get_logger',
    'log_function_call',
    'log_api_request',
    'log_api_response',
    'log_bot_message',
    'log_ai_request',
    'log_database_operation',
    'log_plan_generation',
    'LoggingContext',
    'PerformanceLogger',
    
    # Security
    'SecurityLevel',
    'PermissionLevel',
    'SecurityConfig',
    'SecurityManager',
    'RateLimiter',
    'SecurityAuditLogger',
    'get_security_manager',
    'get_rate_limiter',
    'get_security_audit_logger',
    'initialize_security'
]

# Package version
__version__ = '1.0.0'

# Package metadata
__author__ = 'Sistema Mayra Team'
__email__ = 'sistema@mayra.com'
__description__ = 'Configuration management package for Sistema Mayra nutrition planning system'