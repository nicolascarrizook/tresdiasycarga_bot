"""
Main FastAPI application for Sistema Mayra API.
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from .core.config import settings
from .core.database import startup_database, shutdown_database
from .middleware.cors import setup_cors
from .middleware.logging import LoggingMiddleware
from .utils.logging import setup_logging
from .endpoints import health, patients, plans

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    try:
        logger.info("Starting up Sistema Mayra API...")
        await startup_database()
        logger.info("Sistema Mayra API started successfully")
        yield
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    finally:
        # Shutdown
        try:
            logger.info("Shutting down Sistema Mayra API...")
            await shutdown_database()
            logger.info("Sistema Mayra API shut down successfully")
        except Exception as e:
            logger.error(f"Shutdown failed: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=settings.description,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
    openapi_url="/openapi.json" if settings.is_development else None,
)

# Setup CORS
setup_cors(app)

# Add middleware
app.add_middleware(
    LoggingMiddleware,
    log_requests=True,
    log_responses=True
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(plans.router, prefix="/api/v1")

# Create additional endpoints that might be needed
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Sistema Mayra API",
        "version": settings.version,
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "docs_url": "/docs" if settings.is_development else None
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": settings.project_name,
        "version": settings.version,
        "description": settings.description,
        "environment": settings.environment,
        "features": {
            "patient_management": True,
            "nutrition_plan_generation": True,
            "rag_system": True,
            "meal_replacements": True,
            "telegram_bot_integration": True,
            "pdf_generation": True,
            "analytics": True
        },
        "endpoints": {
            "health": "/api/v1/health",
            "patients": "/api/v1/patients",
            "plans": "/api/v1/plans",
            "recipes": "/api/v1/recipes",
            "auth": "/api/v1/auth"
        }
    }


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "validation_error",
            "message": "Invalid request data",
            "details": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.project_name,
        version=settings.version,
        description=settings.description,
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["contact"] = {
        "name": "Sistema Mayra API",
        "url": "https://github.com/your-repo",
        "email": "admin@sistemamayra.com"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Add tags
    openapi_schema["tags"] = [
        {
            "name": "health",
            "description": "Health check and system status endpoints"
        },
        {
            "name": "patients",
            "description": "Patient management operations"
        },
        {
            "name": "plans",
            "description": "Nutrition plan generation and management"
        },
        {
            "name": "recipes",
            "description": "Recipe management and recommendations"
        },
        {
            "name": "auth",
            "description": "Authentication and authorization"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set custom OpenAPI schema
app.openapi = custom_openapi


# Middleware for additional headers
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    """Add custom headers to responses."""
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Add API version header
    response.headers["X-API-Version"] = settings.version
    
    # Add environment header (for development)
    if settings.is_development:
        response.headers["X-Environment"] = settings.environment
    
    return response


# Health check middleware
@app.middleware("http")
async def health_check_middleware(request: Request, call_next):
    """Basic health check middleware."""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "service_unavailable",
                "message": "Service temporarily unavailable",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Add startup event for additional initialization
@app.on_event("startup")
async def startup_event():
    """Additional startup tasks."""
    logger.info("Performing additional startup tasks...")
    
    # Initialize any additional services here
    # For example: cache warming, background tasks, etc.
    
    logger.info("Additional startup tasks completed")


# Add shutdown event for cleanup
@app.on_event("shutdown")
async def shutdown_event():
    """Additional shutdown tasks."""
    logger.info("Performing additional shutdown tasks...")
    
    # Cleanup any additional resources here
    # For example: close connections, save state, etc.
    
    logger.info("Additional shutdown tasks completed")


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        log_level=settings.log_level.lower(),
        workers=settings.api.workers if not settings.api.reload else 1
    )