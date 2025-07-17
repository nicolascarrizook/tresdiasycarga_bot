"""
Sistema Mayra - Logging Configuration
Comprehensive logging configuration for structured logging across all components.
"""

import logging
import logging.handlers
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


@dataclass
class LogRecord:
    """Structured log record for JSON logging."""
    timestamp: str
    level: str
    message: str
    logger_name: str
    module: str
    function: str
    line_number: int
    process_id: int
    thread_id: int
    extra: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        
        # Extract extra fields
        extra = {}
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage',
                          'message']:
                extra[key] = value
        
        # Create structured log record
        log_record = LogRecord(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            message=record.getMessage(),
            logger_name=record.name,
            module=record.module,
            function=record.funcName,
            line_number=record.lineno,
            process_id=record.process,
            thread_id=record.thread,
            extra=extra if extra else None
        )
        
        # Add exception information if present
        if record.exc_info:
            log_record.extra = log_record.extra or {}
            log_record.extra['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_record.to_dict(), default=str, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if HAS_COLORLOG:
            self.color_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                },
                style='%'
            )
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors if available."""
        if HAS_COLORLOG:
            return self.color_formatter.format(record)
        else:
            return super().format(record)


class StructuredLogger:
    """Structured logger with context management."""
    
    def __init__(self, name: str, extra_context: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(name)
        self.extra_context = extra_context or {}
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method with context."""
        extra = {**self.extra_context, **kwargs}
        getattr(self.logger, level.lower())(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log('CRITICAL', message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        extra = {**self.extra_context, **kwargs}
        self.logger.exception(message, extra=extra)
    
    def bind(self, **kwargs) -> 'StructuredLogger':
        """Create new logger with additional context."""
        new_context = {**self.extra_context, **kwargs}
        return StructuredLogger(self.logger.name, new_context)


class LoggingConfig:
    """Main logging configuration class."""
    
    def __init__(self, 
                 log_level: str = 'INFO',
                 log_format: str = 'json',
                 log_file: Optional[str] = None,
                 log_dir: Optional[str] = None,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 rotation_size: str = '10MB',
                 retention_days: int = 30,
                 sentry_dsn: Optional[str] = None):
        
        self.log_level = log_level.upper()
        self.log_format = log_format.lower()
        self.log_file = log_file
        self.log_dir = Path(log_dir) if log_dir else Path('./logs')
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.rotation_size = rotation_size
        self.retention_days = retention_days
        self.sentry_dsn = sentry_dsn
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        self.configure_root_logger()
        
        # Configure component loggers
        self.configure_component_loggers()
        
        # Configure external integrations
        self.configure_external_loggers()
    
    def configure_root_logger(self):
        """Configure the root logger."""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.log_level))
            
            if self.log_format == 'json':
                console_handler.setFormatter(JSONFormatter())
            else:
                console_handler.setFormatter(ColoredFormatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            
            root_logger.addHandler(console_handler)
        
        # File handler
        if self.enable_file:
            log_file_path = self.log_dir / (self.log_file or 'app.log')
            
            # Use rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file_path,
                maxBytes=self._parse_size(self.rotation_size),
                backupCount=self.retention_days,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, self.log_level))
            
            if self.log_format == 'json':
                file_handler.setFormatter(JSONFormatter())
            else:
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            
            root_logger.addHandler(file_handler)
    
    def configure_component_loggers(self):
        """Configure specific component loggers."""
        
        # API Logger
        api_logger = logging.getLogger('api')
        api_file_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / 'api.log',
            maxBytes=self._parse_size(self.rotation_size),
            backupCount=self.retention_days,
            encoding='utf-8'
        )
        api_file_handler.setFormatter(JSONFormatter())
        api_logger.addHandler(api_file_handler)
        
        # Bot Logger
        bot_logger = logging.getLogger('telegram_bot')
        bot_file_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / 'bot.log',
            maxBytes=self._parse_size(self.rotation_size),
            backupCount=self.retention_days,
            encoding='utf-8'
        )
        bot_file_handler.setFormatter(JSONFormatter())
        bot_logger.addHandler(bot_file_handler)
        
        # Database Logger
        db_logger = logging.getLogger('database')
        db_file_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / 'database.log',
            maxBytes=self._parse_size(self.rotation_size),
            backupCount=self.retention_days,
            encoding='utf-8'
        )
        db_file_handler.setFormatter(JSONFormatter())
        db_logger.addHandler(db_file_handler)
        
        # AI/OpenAI Logger
        ai_logger = logging.getLogger('ai')
        ai_file_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / 'ai.log',
            maxBytes=self._parse_size(self.rotation_size),
            backupCount=self.retention_days,
            encoding='utf-8'
        )
        ai_file_handler.setFormatter(JSONFormatter())
        ai_logger.addHandler(ai_file_handler)
        
        # Data Processor Logger
        processor_logger = logging.getLogger('data_processor')
        processor_file_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / 'processor.log',
            maxBytes=self._parse_size(self.rotation_size),
            backupCount=self.retention_days,
            encoding='utf-8'
        )
        processor_file_handler.setFormatter(JSONFormatter())
        processor_logger.addHandler(processor_file_handler)
    
    def configure_external_loggers(self):
        """Configure external library loggers."""
        
        # Reduce SQLAlchemy logging
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
        
        # Reduce urllib3 logging
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        # Reduce requests logging
        logging.getLogger('requests').setLevel(logging.WARNING)
        
        # Configure OpenAI logging
        logging.getLogger('openai').setLevel(logging.INFO)
        
        # Configure Telegram Bot logging
        logging.getLogger('telegram').setLevel(logging.INFO)
        
        # Configure Sentry if available
        if self.sentry_dsn:
            try:
                import sentry_sdk
                from sentry_sdk.integrations.logging import LoggingIntegration
                from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
                
                sentry_logging = LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                )
                
                sentry_sdk.init(
                    dsn=self.sentry_dsn,
                    integrations=[sentry_logging, SqlalchemyIntegration()],
                    traces_sample_rate=0.1,
                    send_default_pii=False
                )
            except ImportError:
                logging.warning("Sentry SDK not available, skipping Sentry integration")
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes."""
        size_str = size_str.upper().strip()
        
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def get_logger(self, name: str, **context) -> StructuredLogger:
        """Get a structured logger with context."""
        return StructuredLogger(name, context)


# Convenience functions for common logging tasks
def setup_logging(log_level: str = 'INFO', 
                 log_format: str = 'json',
                 log_dir: str = './logs',
                 sentry_dsn: Optional[str] = None) -> LoggingConfig:
    """Setup logging configuration."""
    return LoggingConfig(
        log_level=log_level,
        log_format=log_format,
        log_dir=log_dir,
        sentry_dsn=sentry_dsn
    )


def get_logger(name: str, **context) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name, context)


def log_function_call(func):
    """Decorator to log function calls."""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.info(f"Calling function: {func.__name__}", 
                   function=func.__name__, 
                   args=str(args)[:100], 
                   kwargs=str(kwargs)[:100])
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"Function completed: {func.__name__}", 
                       function=func.__name__, 
                       success=True)
            return result
        except Exception as e:
            logger.error(f"Function failed: {func.__name__}", 
                        function=func.__name__, 
                        error=str(e), 
                        success=False)
            raise
    
    return wrapper


def log_api_request(request_id: str, method: str, path: str, **context):
    """Log API request details."""
    logger = get_logger('api')
    logger.info("API request received", 
               request_id=request_id, 
               method=method, 
               path=path, 
               **context)


def log_api_response(request_id: str, status_code: int, duration: float, **context):
    """Log API response details."""
    logger = get_logger('api')
    logger.info("API response sent", 
               request_id=request_id, 
               status_code=status_code, 
               duration=duration, 
               **context)


def log_bot_message(user_id: str, message_type: str, **context):
    """Log bot message details."""
    logger = get_logger('telegram_bot')
    logger.info("Bot message processed", 
               user_id=user_id, 
               message_type=message_type, 
               **context)


def log_ai_request(model: str, prompt_tokens: int, completion_tokens: int, **context):
    """Log AI request details."""
    logger = get_logger('ai')
    logger.info("AI request completed", 
               model=model, 
               prompt_tokens=prompt_tokens, 
               completion_tokens=completion_tokens, 
               **context)


def log_database_operation(operation: str, table: str, duration: float, **context):
    """Log database operation details."""
    logger = get_logger('database')
    logger.info("Database operation completed", 
               operation=operation, 
               table=table, 
               duration=duration, 
               **context)


def log_plan_generation(patient_id: str, motor_type: str, success: bool, **context):
    """Log nutrition plan generation details."""
    logger = get_logger('nutrition_plans')
    logger.info("Nutrition plan generation", 
               patient_id=patient_id, 
               motor_type=motor_type, 
               success=success, 
               **context)


# Context managers for structured logging
class LoggingContext:
    """Context manager for structured logging."""
    
    def __init__(self, logger: StructuredLogger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation}", 
                        operation=self.operation, 
                        **self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation}", 
                           operation=self.operation, 
                           duration=duration, 
                           success=True, 
                           **self.context)
        else:
            self.logger.error(f"Failed {self.operation}", 
                            operation=self.operation, 
                            duration=duration, 
                            success=False, 
                            error=str(exc_val), 
                            **self.context)


# Performance monitoring
class PerformanceLogger:
    """Logger for performance monitoring."""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str, **context):
        """Log performance metric."""
        self.logger.info("Performance metric", 
                        metric_name=metric_name, 
                        value=value, 
                        unit=unit, 
                        **context)
    
    def log_memory_usage(self, process_name: str, memory_mb: float, **context):
        """Log memory usage."""
        self.log_performance_metric("memory_usage", memory_mb, "MB", 
                                  process_name=process_name, **context)
    
    def log_response_time(self, endpoint: str, response_time_ms: float, **context):
        """Log response time."""
        self.log_performance_metric("response_time", response_time_ms, "ms", 
                                  endpoint=endpoint, **context)
    
    def log_database_query_time(self, query_type: str, duration_ms: float, **context):
        """Log database query time."""
        self.log_performance_metric("db_query_time", duration_ms, "ms", 
                                  query_type=query_type, **context)