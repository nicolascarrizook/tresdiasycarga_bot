"""
Health check endpoints for Sistema Mayra API.
"""
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.database import check_database_health
from ..dependencies import get_db_session, check_services_health
from ..schemas.base import HealthCheckResponse, SystemInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthCheckResponse)
async def health_check(
    db: AsyncSession = Depends(get_db_session),
    services_health: Dict[str, Any] = Depends(check_services_health)
):
    """Basic health check endpoint."""
    try:
        # Check overall health
        all_healthy = all(
            status == "healthy" 
            for status in services_health.values()
        )
        
        overall_status = "healthy" if all_healthy else "unhealthy"
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            services=services_health,
            version=settings.version
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check(
    services_health: Dict[str, Any] = Depends(check_services_health)
):
    """Detailed health check with service-specific information."""
    try:
        # Get database health details
        db_health = await check_database_health()
        
        return {
            "status": "healthy" if all(
                status == "healthy" for status in services_health.values()
            ) else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.version,
            "environment": settings.environment,
            "services": {
                "database": db_health,
                "api": {
                    "status": "healthy",
                    "host": settings.api.host,
                    "port": settings.api.port,
                    "debug": settings.api.debug
                },
                "openai": {
                    "status": services_health.get("openai", "unknown"),
                    "model": settings.openai.model,
                    "temperature": settings.openai.temperature
                },
                "redis": {
                    "status": services_health.get("redis", "unknown"),
                    "url": settings.redis.url,
                    "ttl": settings.redis.ttl
                },
                "chroma": {
                    "status": services_health.get("chroma", "unknown"),
                    "collection": settings.chroma.collection_name,
                    "persist_directory": settings.chroma.persist_directory
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/system", response_model=SystemInfo)
async def system_info():
    """Get system information."""
    try:
        import psutil
        
        # Get system metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent()
        
        return SystemInfo(
            version=settings.version,
            environment=settings.environment,
            uptime=0.0,  # Would calculate actual uptime
            memory_usage={
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percentage": memory.percent
            },
            cpu_usage=cpu_percent,
            active_connections=0,  # Would get from connection pool
            cache_hit_rate=0.0  # Would calculate from Redis stats
        )
        
    except Exception as e:
        logger.error(f"System info failed: {str(e)}")
        raise HTTPException(status_code=500, detail="System info failed")


@router.get("/liveness")
async def liveness_probe():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/readiness")
async def readiness_probe(
    services_health: Dict[str, Any] = Depends(check_services_health)
):
    """Kubernetes readiness probe endpoint."""
    try:
        # Check if all critical services are ready
        critical_services = ["database", "redis", "chroma"]
        ready = all(
            services_health.get(service) == "healthy"
            for service in critical_services
        )
        
        if ready:
            return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        else:
            raise HTTPException(
                status_code=503,
                detail="Service not ready"
            )
            
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    try:
        # This would typically return Prometheus format metrics
        # For now, return basic JSON metrics
        
        metrics = {
            "http_requests_total": 0,  # Would track from middleware
            "http_request_duration_seconds": 0.0,
            "active_connections": 0,
            "memory_usage_bytes": 0,
            "cpu_usage_percent": 0.0,
            "database_connections_active": 0,
            "cache_hit_rate": 0.0,
            "openai_requests_total": 0,
            "plans_generated_total": 0,
            "patients_total": 0,
            "recipes_total": 0,
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Metrics unavailable")


@router.get("/version")
async def version_info():
    """Get version information."""
    return {
        "version": settings.version,
        "project_name": settings.project_name,
        "description": settings.description,
        "environment": settings.environment,
        "python_version": "3.11+",
        "fastapi_version": "0.111.0",
        "build_date": datetime.utcnow().isoformat(),
        "git_commit": "unknown"  # Would be injected during build
    }