"""
Authentication service for Sistema Mayra API.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.config import settings
from ..models.base import BaseModel
from ..schemas.auth import User, UserCreate, Token, LoginRequest
from .base import BaseService

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserModel(BaseModel):
    """User model placeholder - would be fully implemented in actual models."""
    __tablename__ = "users"


class AuthService(BaseService[UserModel, User]):
    """Authentication service."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, UserModel)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    async def get_user_by_telegram_id(self, telegram_user_id: int) -> Optional[UserModel]:
        """Get user by Telegram user ID."""
        return await self.get_by_field("telegram_user_id", telegram_user_id)
    
    async def create_user(self, user_data: UserCreate) -> Optional[UserModel]:
        """Create new user."""
        return await self.create(user_data)
    
    async def authenticate_user(self, login_data: LoginRequest) -> Optional[UserModel]:
        """Authenticate user from Telegram login data."""
        # In a real implementation, you would verify the Telegram auth hash
        user = await self.get_user_by_telegram_id(login_data.telegram_user_id)
        
        if not user:
            # Create new user if doesn't exist
            user_data = UserCreate(
                telegram_user_id=login_data.telegram_user_id,
                username=login_data.username,
                first_name=login_data.first_name,
                last_name=login_data.last_name,
                language_code=login_data.language_code
            )
            user = await self.create_user(user_data)
        
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.security.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.security.secret_key, 
            algorithm=settings.security.algorithm
        )
        
        return encoded_jwt
    
    async def login(self, login_data: LoginRequest) -> Optional[Token]:
        """User login."""
        user = await self.authenticate_user(login_data)
        
        if not user:
            return None
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.security.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": str(user.telegram_user_id)},
            expires_delta=access_token_expires
        )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.security.access_token_expire_minutes * 60,
            user=user
        )
    
    async def check_health(self) -> dict:
        """Check authentication service health."""
        return {
            "status": "healthy",
            "total_users": await self.get_count(),
            "last_check": datetime.utcnow().isoformat()
        }