"""
User repository for Sistema Mayra.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User
from .base import BaseRepository, FilterOptions


class UserRepository(BaseRepository[User]):
    """User repository with specialized methods."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.find_one_by(email=email.lower())
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.find_one_by(username=username.lower())
    
    async def get_by_api_key(self, api_key: str) -> Optional[User]:
        """Get user by API key."""
        return await self.find_one_by(api_key=api_key)
    
    async def create_user(self, email: str, username: str, full_name: str, password: str, 
                         role: str = "user", **kwargs) -> User:
        """Create new user."""
        user_data = {
            "email": email.lower(),
            "username": username.lower(),
            "full_name": full_name,
            "role": role,
            "is_verified": False,
            "failed_login_attempts": 0,
            "is_2fa_enabled": False,
            "rate_limit_remaining": 1000,
            "timezone": "America/Argentina/Buenos_Aires",
            "language": "es",
            **kwargs
        }
        
        user = await self.create(**user_data)
        user.set_password(password)
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def authenticate(self, email_or_username: str, password: str) -> Optional[User]:
        """Authenticate user."""
        # Try to find by email first, then username
        user = await self.get_by_email(email_or_username)
        if not user:
            user = await self.get_by_username(email_or_username)
        
        if not user:
            return None
        
        # Check if account is locked
        if user.is_locked():
            return None
        
        # Check password
        if not user.check_password(password):
            user.increment_failed_login()
            await self.session.commit()
            return None
        
        # Update last login
        user.reset_failed_login()
        await self.session.commit()
        
        return user
    
    async def update_last_login(self, user_id: int, ip_address: str) -> bool:
        """Update last login information."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.update_last_login(ip_address)
        await self.session.commit()
        return True
    
    async def generate_verification_token(self, user_id: int) -> Optional[str]:
        """Generate verification token."""
        import secrets
        
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        token = secrets.token_urlsafe(32)
        user.verification_token = token
        user.verification_expires_at = datetime.utcnow() + timedelta(hours=24)
        
        await self.session.commit()
        return token
    
    async def verify_email(self, token: str) -> bool:
        """Verify email with token."""
        user = await self.find_one_by(verification_token=token)
        if not user:
            return False
        
        # Check if token is expired
        if user.verification_expires_at and user.verification_expires_at < datetime.utcnow():
            return False
        
        user.is_verified = True
        user.verification_token = None
        user.verification_expires_at = None
        
        await self.session.commit()
        return True
    
    async def generate_password_reset_token(self, email: str) -> Optional[str]:
        """Generate password reset token."""
        import secrets
        
        user = await self.get_by_email(email)
        if not user:
            return None
        
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_expires_at = datetime.utcnow() + timedelta(hours=1)
        
        await self.session.commit()
        return token
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token."""
        user = await self.find_one_by(reset_token=token)
        if not user:
            return False
        
        # Check if token is expired
        if user.reset_expires_at and user.reset_expires_at < datetime.utcnow():
            return False
        
        user.set_password(new_password)
        user.reset_token = None
        user.reset_expires_at = None
        user.unlock_account()  # Unlock if locked
        
        await self.session.commit()
        return True
    
    async def lock_user(self, user_id: int, duration_minutes: int = 30) -> bool:
        """Lock user account."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.lock_account(duration_minutes)
        await self.session.commit()
        return True
    
    async def unlock_user(self, user_id: int) -> bool:
        """Unlock user account."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.unlock_account()
        await self.session.commit()
        return True
    
    async def update_permissions(self, user_id: int, permissions: List[str]) -> bool:
        """Update user permissions."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.permissions = permissions
        await self.session.commit()
        return True
    
    async def add_permission(self, user_id: int, permission: str) -> bool:
        """Add permission to user."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.add_permission(permission)
        await self.session.commit()
        return True
    
    async def remove_permission(self, user_id: int, permission: str) -> bool:
        """Remove permission from user."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.remove_permission(permission)
        await self.session.commit()
        return True
    
    async def generate_api_key(self, user_id: int) -> Optional[str]:
        """Generate API key for user."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        api_key = user.generate_api_key()
        await self.session.commit()
        return api_key
    
    async def revoke_api_key(self, user_id: int) -> bool:
        """Revoke API key for user."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.revoke_api_key()
        await self.session.commit()
        return True
    
    async def consume_rate_limit(self, user_id: int, amount: int = 1) -> bool:
        """Consume rate limit for user."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        if not user.can_make_api_request():
            return False
        
        user.consume_rate_limit(amount)
        await self.session.commit()
        return True
    
    async def get_by_role(self, role: str) -> List[User]:
        """Get users by role."""
        return await self.find_by(role=role)
    
    async def get_admins(self) -> List[User]:
        """Get admin users."""
        return await self.get_by_role("admin")
    
    async def get_nutritionists(self) -> List[User]:
        """Get nutritionist users."""
        filter_options = FilterOptions()
        filter_options.add_filter(User.role.in_(["admin", "nutritionist"]))
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def search_users(self, query: str, page: int = 1, per_page: int = 20):
        """Search users."""
        return await self.search(
            query=query,
            fields=["full_name", "email", "username"],
            page=page,
            per_page=per_page
        )
    
    async def get_locked_users(self) -> List[User]:
        """Get locked users."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                User.locked_until.is_not(None),
                User.locked_until > datetime.utcnow()
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_unverified_users(self) -> List[User]:
        """Get unverified users."""
        return await self.find_by(is_verified=False)
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens."""
        from sqlalchemy import update
        
        now = datetime.utcnow()
        
        # Clean up verification tokens
        verification_stmt = update(User).where(
            and_(
                User.verification_expires_at.is_not(None),
                User.verification_expires_at < now
            )
        ).values(
            verification_token=None,
            verification_expires_at=None
        )
        
        # Clean up reset tokens
        reset_stmt = update(User).where(
            and_(
                User.reset_expires_at.is_not(None),
                User.reset_expires_at < now
            )
        ).values(
            reset_token=None,
            reset_expires_at=None
        )
        
        # Clean up expired locks
        lock_stmt = update(User).where(
            and_(
                User.locked_until.is_not(None),
                User.locked_until < now
            )
        ).values(
            locked_until=None,
            failed_login_attempts=0
        )
        
        verification_result = await self.session.execute(verification_stmt)
        reset_result = await self.session.execute(reset_stmt)
        lock_result = await self.session.execute(lock_stmt)
        
        await self.session.commit()
        
        return verification_result.rowcount + reset_result.rowcount + lock_result.rowcount
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        base_stats = await self.get_statistics()
        
        # Role distribution
        role_stmt = select(User.role, func.count(User.id)).group_by(User.role)
        role_result = await self.session.execute(role_stmt)
        roles = dict(role_result.fetchall())
        
        # Verification status
        verified_stmt = select(func.count(User.id)).where(User.is_verified == True)
        verified_result = await self.session.execute(verified_stmt)
        verified = verified_result.scalar()
        
        # Locked users
        locked_stmt = select(func.count(User.id)).where(
            and_(
                User.locked_until.is_not(None),
                User.locked_until > datetime.utcnow()
            )
        )
        locked_result = await self.session.execute(locked_stmt)
        locked = locked_result.scalar()
        
        # Recent logins (last 30 days)
        recent_login_stmt = select(func.count(User.id)).where(
            User.last_login_at >= datetime.utcnow() - timedelta(days=30)
        )
        recent_login_result = await self.session.execute(recent_login_stmt)
        recent_logins = recent_login_result.scalar()
        
        return {
            **base_stats,
            "role_distribution": roles,
            "verified": verified,
            "unverified": base_stats["total"] - verified,
            "locked": locked,
            "recent_logins": recent_logins
        }