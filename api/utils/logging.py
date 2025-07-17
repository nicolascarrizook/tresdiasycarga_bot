"""
Logging utilities for Sistema Mayra API.
"""
import logging
import sys
from typing import Optional

from ..core.config import settings


def setup_logging(log_level: Optional[str] = None, log_file: Optional[str] = None):
    """Setup application logging."""
    level = log_level or settings.log_level
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file or settings.log_file:
        file_handler = logging.FileHandler(log_file or settings.log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    # Configure specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {level}")
    
    return logger