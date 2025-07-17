"""
User seeder for Sistema Mayra database.
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta

from database.models.user import User, UserRoleEnum, UserStatusEnum
from database.seeders.base import BaseSeeder


class UserSeeder(BaseSeeder):
    """Seeder for creating initial users."""
    
    def get_seeder_name(self) -> str:
        return "UserSeeder"
    
    async def seed(self) -> Dict[str, Any]:
        """Create initial users."""
        self.log_info("Starting user seeding...")
        
        # Create admin user
        admin_user = await self.create_admin_user()
        
        # Create API user
        api_user = await self.create_api_user()
        
        # Create test users
        test_users = await self.create_test_users()
        
        return {
            "seeder": self.get_seeder_name(),
            "success": True,
            "created_count": len(self.created_records),
            "admin_user_id": admin_user.id if admin_user else None,
            "api_user_id": api_user.id if api_user else None,
            "test_users_count": len(test_users),
            "timestamp": datetime.utcnow()
        }
    
    async def create_admin_user(self) -> User:
        """Create the main admin user."""
        admin_user = User(
            username="admin",
            email="admin@sistemamayra.com",
            full_name="Administrator",
            role=UserRoleEnum.ADMIN,
            status=UserStatusEnum.ACTIVE,
            is_email_verified=True,
            is_2fa_enabled=False,
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewbJhTKYKGdWbHYW",  # "admin123"
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_login=datetime.utcnow(),
            login_count=1,
            failed_login_attempts=0,
            account_locked_until=None,
            rate_limit_reset=datetime.utcnow() + timedelta(hours=1),
            api_calls_today=0,
            api_calls_this_month=0,
            preferences={
                "theme": "light",
                "language": "es",
                "notifications": True,
                "email_alerts": True
            },
            permissions={
                "users": ["create", "read", "update", "delete"],
                "patients": ["create", "read", "update", "delete"],
                "recipes": ["create", "read", "update", "delete"],
                "plans": ["create", "read", "update", "delete"],
                "system": ["backup", "restore", "maintenance"]
            }
        )
        
        await self.create_single(admin_user, "admin user")
        return admin_user
    
    async def create_api_user(self) -> User:
        """Create API service user."""
        api_user = User(
            username="api_service",
            email="api@sistemamayra.com",
            full_name="API Service User",
            role=UserRoleEnum.API,
            status=UserStatusEnum.ACTIVE,
            is_email_verified=True,
            is_2fa_enabled=False,
            password_hash="$2b$12$XYZ123ApiServiceHashForSystemAccess456",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_login=datetime.utcnow(),
            login_count=0,
            failed_login_attempts=0,
            account_locked_until=None,
            rate_limit_reset=datetime.utcnow() + timedelta(hours=1),
            api_calls_today=0,
            api_calls_this_month=0,
            daily_api_limit=10000,
            monthly_api_limit=300000,
            preferences={
                "api_format": "json",
                "rate_limit_notifications": True
            },
            permissions={
                "patients": ["create", "read", "update"],
                "recipes": ["read"],
                "plans": ["create", "read", "update"],
                "conversations": ["create", "read", "update"]
            }
        )
        
        await self.create_single(api_user, "API service user")
        return api_user
    
    async def create_test_users(self) -> List[User]:
        """Create test users for development."""
        test_users = []
        
        # Nutritionist user
        nutritionist = User(
            username="nutritionist",
            email="nutritionist@sistemamayra.com",
            full_name="Nutritionist Test User",
            role=UserRoleEnum.NUTRITIONIST,
            status=UserStatusEnum.ACTIVE,
            is_email_verified=True,
            is_2fa_enabled=False,
            password_hash="$2b$12$NutritionistTestHashForDevelopment789",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_login=datetime.utcnow() - timedelta(days=1),
            login_count=5,
            failed_login_attempts=0,
            account_locked_until=None,
            rate_limit_reset=datetime.utcnow() + timedelta(hours=1),
            api_calls_today=0,
            api_calls_this_month=0,
            preferences={
                "theme": "light",
                "language": "es",
                "notifications": True,
                "default_economic_level": "medio"
            },
            permissions={
                "patients": ["create", "read", "update"],
                "recipes": ["read", "update"],
                "plans": ["create", "read", "update"]
            }
        )
        test_users.append(nutritionist)
        
        # Viewer user
        viewer = User(
            username="viewer",
            email="viewer@sistemamayra.com",
            full_name="Viewer Test User",
            role=UserRoleEnum.VIEWER,
            status=UserStatusEnum.ACTIVE,
            is_email_verified=True,
            is_2fa_enabled=False,
            password_hash="$2b$12$ViewerTestHashForDevelopmentOnly456",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_login=datetime.utcnow() - timedelta(hours=2),
            login_count=3,
            failed_login_attempts=0,
            account_locked_until=None,
            rate_limit_reset=datetime.utcnow() + timedelta(hours=1),
            api_calls_today=0,
            api_calls_this_month=0,
            preferences={
                "theme": "dark",
                "language": "es",
                "notifications": False
            },
            permissions={
                "patients": ["read"],
                "recipes": ["read"],
                "plans": ["read"]
            }
        )
        test_users.append(viewer)
        
        # Inactive user for testing
        inactive_user = User(
            username="inactive_test",
            email="inactive@sistemamayra.com",
            full_name="Inactive Test User",
            role=UserRoleEnum.VIEWER,
            status=UserStatusEnum.INACTIVE,
            is_email_verified=False,
            is_2fa_enabled=False,
            password_hash="$2b$12$InactiveTestHashForDevelopment123",
            created_at=datetime.utcnow() - timedelta(days=30),
            updated_at=datetime.utcnow() - timedelta(days=30),
            last_login=None,
            login_count=0,
            failed_login_attempts=0,
            account_locked_until=None,
            rate_limit_reset=datetime.utcnow() + timedelta(hours=1),
            api_calls_today=0,
            api_calls_this_month=0,
            preferences={},
            permissions={}
        )
        test_users.append(inactive_user)
        
        await self.commit_batch(test_users, "test users")
        return test_users