"""
Logging middleware for Sistema Mayra API.
"""
import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log information."""
        start_time = time.time()
        
        # Log request
        if self.log_requests:
            logger.info(
                f"Request: {request.method} {request.url.path} "
                f"from {request.client.host} "
                f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
            )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        if self.log_responses:
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.4f}s"
            )
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response