"""
Authentication schemas for Sistema Mayra API.
"""
from datetime import datetime
from typing import Optional

from pydantic import Field, validator

from ..core.settings import DietaryRestriction, SupplementType
from .base import BaseSchema, IDMixin, TimestampMixin


class UserBase(BaseSchema):
    """Base user schema."""
    
    telegram_user_id: int = Field(..., description="Telegram user ID", gt=0)
    username: Optional[str] = Field(None, description="Telegram username", max_length=50)
    first_name: str = Field(..., description="First name", min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, description="Last name", max_length=50)
    language_code: str = Field("es", description="Language code", max_length=5)
    is_active: bool = Field(True, description="User active status")
    is_admin: bool = Field(False, description="Admin status")


class UserCreate(UserBase):
    """User creation schema."""
    
    pass


class UserUpdate(BaseSchema):
    """User update schema."""
    
    username: Optional[str] = Field(None, description="Telegram username", max_length=50)
    first_name: Optional[str] = Field(None, description="First name", min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, description="Last name", max_length=50)
    language_code: Optional[str] = Field(None, description="Language code", max_length=5)
    is_active: Optional[bool] = Field(None, description="User active status")


class User(UserBase, IDMixin, TimestampMixin):
    """User response schema."""
    
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    total_plans: int = Field(0, description="Total plans generated", ge=0)
    
    @property
    def full_name(self) -> str:
        """Get full name."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name


class UserProfile(User):
    """Extended user profile schema."""
    
    # Additional profile fields could be added here
    preferences: Optional[dict] = Field(None, description="User preferences")
    settings: Optional[dict] = Field(None, description="User settings")


class TokenData(BaseSchema):
    """Token data schema."""
    
    telegram_user_id: int = Field(..., description="Telegram user ID", gt=0)
    exp: datetime = Field(..., description="Expiration time")
    iat: datetime = Field(..., description="Issued at time")
    
    @validator("exp")
    def validate_expiration(cls, v):
        """Validate token expiration."""
        if v < datetime.utcnow():
            raise ValueError("Token has expired")
        return v


class Token(BaseSchema):
    """Token response schema."""
    
    access_token: str = Field(..., description="Access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds", gt=0)
    user: User = Field(..., description="User information")


class TokenRefresh(BaseSchema):
    """Token refresh schema."""
    
    refresh_token: str = Field(..., description="Refresh token")


class LoginRequest(BaseSchema):
    """Login request schema."""
    
    telegram_user_id: int = Field(..., description="Telegram user ID", gt=0)
    username: Optional[str] = Field(None, description="Telegram username", max_length=50)
    first_name: str = Field(..., description="First name", min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, description="Last name", max_length=50)
    language_code: str = Field("es", description="Language code", max_length=5)
    auth_date: int = Field(..., description="Authentication date timestamp", gt=0)
    hash: str = Field(..., description="Telegram auth hash")


class LoginResponse(BaseSchema):
    """Login response schema."""
    
    token: Token = Field(..., description="Authentication token")
    user: User = Field(..., description="User information")
    is_new_user: bool = Field(..., description="Whether this is a new user")


class LogoutRequest(BaseSchema):
    """Logout request schema."""
    
    token: str = Field(..., description="Token to invalidate")


class PasswordResetRequest(BaseSchema):
    """Password reset request schema."""
    
    telegram_user_id: int = Field(..., description="Telegram user ID", gt=0)


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""
    
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., description="New password", min_length=8)


class SessionInfo(BaseSchema):
    """Session information schema."""
    
    session_id: str = Field(..., description="Session identifier")
    user_id: int = Field(..., description="User ID", gt=0)
    ip_address: str = Field(..., description="Client IP address")
    user_agent: str = Field(..., description="User agent string")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity time")
    expires_at: datetime = Field(..., description="Session expiration time")
    is_active: bool = Field(..., description="Session active status")


class UserActivity(BaseSchema):
    """User activity schema."""
    
    user_id: int = Field(..., description="User ID", gt=0)
    action: str = Field(..., description="Action performed")
    resource: Optional[str] = Field(None, description="Resource accessed")
    details: Optional[dict] = Field(None, description="Additional details")
    ip_address: str = Field(..., description="Client IP address")
    user_agent: str = Field(..., description="User agent string")
    timestamp: datetime = Field(..., description="Activity timestamp")


class UserStats(BaseSchema):
    """User statistics schema."""
    
    user_id: int = Field(..., description="User ID", gt=0)
    total_plans_generated: int = Field(0, description="Total plans generated", ge=0)
    total_replacements: int = Field(0, description="Total meal replacements", ge=0)
    total_controls: int = Field(0, description="Total control visits", ge=0)
    last_plan_generated: Optional[datetime] = Field(None, description="Last plan generation time")
    favorite_recipes: list[str] = Field(default_factory=list, description="Favorite recipe IDs")
    total_login_sessions: int = Field(0, description="Total login sessions", ge=0)
    average_session_duration: float = Field(0, description="Average session duration in minutes", ge=0)


class AdminUserUpdate(UserUpdate):
    """Admin user update schema."""
    
    is_admin: Optional[bool] = Field(None, description="Admin status")
    is_active: Optional[bool] = Field(None, description="User active status")
    notes: Optional[str] = Field(None, description="Admin notes", max_length=500)


class UserSearch(BaseSchema):
    """User search schema."""
    
    query: Optional[str] = Field(None, description="Search query")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_admin: Optional[bool] = Field(None, description="Filter by admin status")
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    last_login_after: Optional[datetime] = Field(None, description="Last login after date")
    last_login_before: Optional[datetime] = Field(None, description="Last login before date")
    
    
class BulkUserAction(BaseSchema):
    """Bulk user action schema."""
    
    user_ids: list[int] = Field(..., description="List of user IDs", min_items=1)
    action: str = Field(..., description="Action to perform")
    parameters: Optional[dict] = Field(None, description="Action parameters")
    
    @validator("action")
    def validate_action(cls, v):
        """Validate action type."""
        allowed_actions = ["activate", "deactivate", "delete", "promote", "demote"]
        if v not in allowed_actions:
            raise ValueError(f"Action must be one of: {allowed_actions}")
        return v


class UserExport(BaseSchema):
    """User export schema."""
    
    format: str = Field("csv", description="Export format")
    filters: Optional[UserSearch] = Field(None, description="Export filters")
    fields: Optional[list[str]] = Field(None, description="Fields to include")
    
    @validator("format")
    def validate_format(cls, v):
        """Validate export format."""
        allowed_formats = ["csv", "json", "xlsx"]
        if v not in allowed_formats:
            raise ValueError(f"Format must be one of: {allowed_formats}")
        return v


class APIKey(BaseSchema):
    """API key schema."""
    
    name: str = Field(..., description="API key name", min_length=1, max_length=100)
    key: str = Field(..., description="API key value")
    user_id: int = Field(..., description="Owner user ID", gt=0)
    permissions: list[str] = Field(default_factory=list, description="API key permissions")
    is_active: bool = Field(True, description="API key active status")
    expires_at: Optional[datetime] = Field(None, description="API key expiration time")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")


class APIKeyCreate(BaseSchema):
    """API key creation schema."""
    
    name: str = Field(..., description="API key name", min_length=1, max_length=100)
    permissions: list[str] = Field(default_factory=list, description="API key permissions")
    expires_at: Optional[datetime] = Field(None, description="API key expiration time")


class APIKeyUpdate(BaseSchema):
    """API key update schema."""
    
    name: Optional[str] = Field(None, description="API key name", min_length=1, max_length=100)
    permissions: Optional[list[str]] = Field(None, description="API key permissions")
    is_active: Optional[bool] = Field(None, description="API key active status")
    expires_at: Optional[datetime] = Field(None, description="API key expiration time")