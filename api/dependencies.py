"""
Dependency injection for Sistema Mayra API.
"""
import logging
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from .core.config import settings
from .core.database import get_async_db, get_redis, get_chroma
from .services.auth import AuthService
from .services.openai import OpenAIService
from .services.rag import RAGService
from .services.patient import PatientService
from .services.recipe import RecipeService
from .services.plan import PlanService
from .schemas.auth import User

logger = logging.getLogger(__name__)
security = HTTPBearer()


# Database dependencies
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async for session in get_async_db():
        yield session


async def get_redis_client():
    """Get Redis client dependency."""
    return await get_redis()


def get_chroma_collection():
    """Get ChromaDB collection dependency."""
    return get_chroma()


# Authentication dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.security.secret_key,
            algorithms=[settings.security.algorithm]
        )
        telegram_user_id: str = payload.get("sub")
        if telegram_user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_telegram_id(int(telegram_user_id))
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# Optional authentication for some endpoints
async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """Get current user optionally (for endpoints that work with/without auth)."""
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
    
    try:
        scheme, credentials = authorization.split()
        if scheme.lower() != "bearer":
            return None
        
        payload = jwt.decode(
            credentials,
            settings.security.secret_key,
            algorithms=[settings.security.algorithm]
        )
        telegram_user_id: str = payload.get("sub")
        if telegram_user_id is None:
            return None
        
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_telegram_id(int(telegram_user_id))
        return user
        
    except Exception as e:
        logger.debug(f"Optional auth failed: {str(e)}")
        return None


# Service dependencies
async def get_auth_service(
    db: AsyncSession = Depends(get_db_session)
) -> AuthService:
    """Get authentication service."""
    return AuthService(db)


async def get_patient_service(
    db: AsyncSession = Depends(get_db_session)
) -> PatientService:
    """Get patient service."""
    return PatientService(db)


async def get_recipe_service(
    db: AsyncSession = Depends(get_db_session),
    chroma = Depends(get_chroma_collection)
) -> RecipeService:
    """Get recipe service."""
    return RecipeService(db, chroma)


async def get_plan_service(
    db: AsyncSession = Depends(get_db_session),
    patient_service: PatientService = Depends(get_patient_service),
    recipe_service: RecipeService = Depends(get_recipe_service),
    rag_service: RAGService = Depends(get_rag_service),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> PlanService:
    """Get plan service."""
    return PlanService(db, patient_service, recipe_service, rag_service, openai_service)


async def get_openai_service() -> OpenAIService:
    """Get OpenAI service."""
    return OpenAIService()


async def get_rag_service(
    chroma = Depends(get_chroma_collection),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> RAGService:
    """Get RAG service."""
    return RAGService(chroma, openai_service)




# Request validation dependencies
async def validate_telegram_webhook(request: Request) -> dict:
    """Validate Telegram webhook request."""
    try:
        body = await request.body()
        return await request.json()
    except Exception as e:
        logger.error(f"Invalid webhook request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook request"
        )


# Rate limiting dependency
class RateLimiter:
    """Simple rate limiter using Redis."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def __call__(
        self,
        request: Request,
        redis_client = Depends(get_redis_client)
    ):
        """Rate limit check."""
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        try:
            current_requests = await redis_client.get(key)
            
            if current_requests is None:
                await redis_client.setex(key, self.window_seconds, 1)
                return
            
            if int(current_requests) >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            await redis_client.incr(key)
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Don't block requests if Redis is down
            pass


# Create rate limiter instances
rate_limit_strict = RateLimiter(max_requests=50, window_seconds=3600)  # 50 per hour
rate_limit_normal = RateLimiter(max_requests=100, window_seconds=3600)  # 100 per hour
rate_limit_lenient = RateLimiter(max_requests=200, window_seconds=3600)  # 200 per hour


# Logging dependency
async def log_request(request: Request):
    """Log request information."""
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host}"
    )


# Health check dependencies
async def check_services_health(
    db: AsyncSession = Depends(get_db_session),
    redis_client = Depends(get_redis_client),
    chroma = Depends(get_chroma_collection)
) -> dict:
    """Check all services health."""
    health_status = {
        "database": "unknown",
        "redis": "unknown",
        "chroma": "unknown",
        "openai": "unknown"
    }
    
    # Check database
    try:
        await db.execute("SELECT 1")
        health_status["database"] = "healthy"
    except Exception:
        health_status["database"] = "unhealthy"
    
    # Check Redis
    try:
        await redis_client.ping()
        health_status["redis"] = "healthy"
    except Exception:
        health_status["redis"] = "unhealthy"
    
    # Check ChromaDB
    try:
        chroma.count()
        health_status["chroma"] = "healthy"
    except Exception:
        health_status["chroma"] = "unhealthy"
    
    # Check OpenAI
    try:
        openai_service = OpenAIService()
        await openai_service.check_health()
        health_status["openai"] = "healthy"
    except Exception:
        health_status["openai"] = "unhealthy"
    
    return health_status


# Validation dependencies
def validate_plan_parameters(
    plan_type: str,
    patient_id: Optional[int] = None
):
    """Validate plan generation parameters."""
    if plan_type not in ["nuevo_paciente", "control", "reemplazo"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan type"
        )
    
    if plan_type in ["control", "reemplazo"] and patient_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient ID required for control and replacement plans"
        )
    
    return {"plan_type": plan_type, "patient_id": patient_id}


# Telegram user validation
async def validate_telegram_user(
    telegram_user_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Validate Telegram user exists."""
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_telegram_id(telegram_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"user": user}


# File upload validation
def validate_file_upload(file_size: int, content_type: str):
    """Validate file upload parameters."""
    max_size = 10 * 1024 * 1024  # 10MB
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large"
        )
    
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type"
        )
    
    return True


# Admin access dependency
async def require_admin_access(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require admin access for certain endpoints."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Pagination dependency
def get_pagination_params(
    page: int = 1,
    limit: int = 20,
    max_limit: int = 100
) -> dict:
    """Get pagination parameters."""
    if page < 1:
        page = 1
    
    if limit < 1:
        limit = 20
    elif limit > max_limit:
        limit = max_limit
    
    offset = (page - 1) * limit
    
    return {
        "page": page,
        "limit": limit,
        "offset": offset
    }


# Search parameters dependency
def get_search_params(
    q: Optional[str] = None,
    category: Optional[str] = None,
    economic_level: Optional[str] = None,
    dietary_restrictions: Optional[str] = None
) -> dict:
    """Get search parameters."""
    params = {}
    
    if q:
        params["query"] = q.strip()
    
    if category:
        params["category"] = category
    
    if economic_level:
        params["economic_level"] = economic_level
    
    if dietary_restrictions:
        params["dietary_restrictions"] = dietary_restrictions.split(",")
    
    return params