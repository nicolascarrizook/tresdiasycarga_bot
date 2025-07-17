"""
State management for Sistema Mayra Telegram Bot.
"""
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import redis
import logging

from .conversation_states import ConversationState, get_next_state, is_terminal_state
from .user_data import (
    UserData, PatientData, ConversationData, PlanData, 
    ReplacementData, SessionData, UserPreferences, ConversationStatus
)
from ..config import bot_settings, CACHE_SETTINGS


logger = logging.getLogger(__name__)


class StateManager:
    """Base state management class."""
    
    def __init__(self, redis_client: redis.Redis = None):
        """Initialize state manager."""
        self.redis = redis_client or redis.from_url(
            bot_settings.redis_url,
            db=bot_settings.redis_db,
            decode_responses=True
        )
        self.key_prefix = "mayra_bot:"
    
    def _get_key(self, key_type: str, identifier: str) -> str:
        """Generate Redis key."""
        return f"{self.key_prefix}{key_type}:{identifier}"
    
    def _serialize(self, data: Any) -> str:
        """Serialize data to JSON string."""
        if hasattr(data, 'to_dict'):
            return json.dumps(data.to_dict())
        return json.dumps(data)
    
    def _deserialize(self, data: str, data_class: type = None) -> Any:
        """Deserialize JSON string to object."""
        if not data:
            return None
        
        parsed = json.loads(data)
        if data_class and hasattr(data_class, 'from_dict'):
            return data_class.from_dict(parsed)
        return parsed
    
    def set_with_ttl(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value with TTL."""
        try:
            serialized = self._serialize(value)
            if ttl:
                return self.redis.setex(key, ttl, serialized)
            else:
                return self.redis.set(key, serialized)
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False
    
    def get(self, key: str, data_class: type = None) -> Any:
        """Get value from Redis."""
        try:
            data = self.redis.get(key)
            return self._deserialize(data, data_class)
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Error checking key {key}: {e}")
            return False
    
    def get_keys_by_pattern(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        try:
            return self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"Error getting keys by pattern {pattern}: {e}")
            return []


class UserDataManager(StateManager):
    """Manager for user data and preferences."""
    
    def save_user_data(self, user_data: UserData) -> bool:
        """Save user data."""
        key = self._get_key("user", str(user_data.user_id))
        return self.set_with_ttl(key, user_data, CACHE_SETTINGS["user_data_ttl"])
    
    def get_user_data(self, user_id: int) -> Optional[UserData]:
        """Get user data."""
        key = self._get_key("user", str(user_id))
        return self.get(key, UserData)
    
    def update_user_activity(self, user_id: int) -> bool:
        """Update user last activity."""
        user_data = self.get_user_data(user_id)
        if user_data:
            user_data.last_activity = datetime.now()
            return self.save_user_data(user_data)
        return False
    
    def save_user_preferences(self, preferences: UserPreferences) -> bool:
        """Save user preferences."""
        key = self._get_key("prefs", str(preferences.user_id))
        return self.set_with_ttl(key, preferences, CACHE_SETTINGS["user_data_ttl"])
    
    def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences."""
        key = self._get_key("prefs", str(user_id))
        return self.get(key, UserPreferences)
    
    def is_user_blocked(self, user_id: int) -> bool:
        """Check if user is blocked."""
        user_data = self.get_user_data(user_id)
        return user_data.is_blocked if user_data else False
    
    def is_user_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        user_data = self.get_user_data(user_id)
        return user_data.is_admin if user_data else False
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics."""
        user_data = self.get_user_data(user_id)
        if not user_data:
            return {}
        
        return {
            "total_conversations": user_data.total_conversations,
            "total_plans_generated": user_data.total_plans_generated,
            "last_activity": user_data.last_activity,
            "created_at": user_data.created_at,
            "is_active": user_data.is_active
        }


class ConversationManager(StateManager):
    """Manager for conversation states and data."""
    
    def create_conversation(self, user_id: int, motor_type: str) -> ConversationData:
        """Create new conversation."""
        conversation_id = str(uuid.uuid4())
        conversation_data = ConversationData(
            user_id=user_id,
            conversation_id=conversation_id,
            motor_type=motor_type,
            current_state=ConversationState.MOTOR_SELECTION.name
        )
        
        # Initialize patient data with user ID
        conversation_data.patient_data.telegram_user_id = user_id
        
        self.save_conversation(conversation_data)
        return conversation_data
    
    def save_conversation(self, conversation_data: ConversationData) -> bool:
        """Save conversation data."""
        key = self._get_key("conv", str(conversation_data.user_id))
        return self.set_with_ttl(
            key, 
            conversation_data, 
            CACHE_SETTINGS["conversation_ttl"]
        )
    
    def get_conversation(self, user_id: int) -> Optional[ConversationData]:
        """Get current conversation."""
        key = self._get_key("conv", str(user_id))
        return self.get(key, ConversationData)
    
    def update_conversation_state(self, user_id: int, new_state: str) -> bool:
        """Update conversation state."""
        conversation = self.get_conversation(user_id)
        if conversation:
            conversation.update_state(new_state)
            return self.save_conversation(conversation)
        return False
    
    def update_patient_data(self, user_id: int, field: str, value: Any) -> bool:
        """Update patient data field."""
        conversation = self.get_conversation(user_id)
        if conversation:
            setattr(conversation.patient_data, field, value)
            return self.save_conversation(conversation)
        return False
    
    def get_patient_data(self, user_id: int) -> Optional[PatientData]:
        """Get patient data from conversation."""
        conversation = self.get_conversation(user_id)
        return conversation.patient_data if conversation else None
    
    def add_conversation_error(self, user_id: int, error: str) -> bool:
        """Add error to conversation."""
        conversation = self.get_conversation(user_id)
        if conversation:
            conversation.add_error(error)
            return self.save_conversation(conversation)
        return False
    
    def reset_conversation_errors(self, user_id: int) -> bool:
        """Reset conversation errors."""
        conversation = self.get_conversation(user_id)
        if conversation:
            conversation.reset_errors()
            return self.save_conversation(conversation)
        return False
    
    def end_conversation(self, user_id: int, status: ConversationStatus = ConversationStatus.COMPLETED) -> bool:
        """End conversation."""
        conversation = self.get_conversation(user_id)
        if conversation:
            conversation.status = status
            conversation.current_state = ConversationState.ENDED.name
            self.save_conversation(conversation)
            
            # Archive conversation
            archive_key = self._get_key("conv_archive", f"{user_id}_{conversation.conversation_id}")
            self.set_with_ttl(archive_key, conversation, 86400 * 7)  # 7 days
            
            # Clear active conversation
            conv_key = self._get_key("conv", str(user_id))
            return self.delete(conv_key)
        return False
    
    def is_conversation_active(self, user_id: int) -> bool:
        """Check if user has active conversation."""
        conversation = self.get_conversation(user_id)
        return conversation and conversation.status == ConversationStatus.ACTIVE
    
    def is_conversation_expired(self, user_id: int, timeout_minutes: int = 30) -> bool:
        """Check if conversation is expired."""
        conversation = self.get_conversation(user_id)
        return conversation.is_expired(timeout_minutes) if conversation else False
    
    def get_conversation_progress(self, user_id: int) -> Dict[str, Any]:
        """Get conversation progress."""
        conversation = self.get_conversation(user_id)
        if not conversation:
            return {}
        
        patient_data = conversation.patient_data
        total_fields = len(patient_data.to_dict())
        completed_fields = sum(1 for v in patient_data.to_dict().values() if v is not None)
        
        return {
            "current_state": conversation.current_state,
            "motor_type": conversation.motor_type,
            "progress_percentage": (completed_fields / total_fields) * 100,
            "is_complete": patient_data.is_complete(),
            "missing_fields": patient_data.get_missing_fields(),
            "started_at": conversation.started_at,
            "last_update": conversation.last_update,
            "errors": conversation.errors,
            "retries": conversation.retries
        }


class SessionManager(StateManager):
    """Manager for temporary session data."""
    
    def create_session(self, user_id: int, expires_minutes: int = 30) -> str:
        """Create new session."""
        session_id = str(uuid.uuid4())
        session_data = SessionData(
            user_id=user_id,
            session_id=session_id,
            expires_at=datetime.now() + timedelta(minutes=expires_minutes)
        )
        
        key = self._get_key("session", session_id)
        self.set_with_ttl(key, session_data, expires_minutes * 60)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data."""
        key = self._get_key("session", session_id)
        return self.get(key, SessionData)
    
    def update_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data."""
        session = self.get_session(session_id)
        if session and not session.is_expired():
            session.data.update(data)
            key = self._get_key("session", session_id)
            return self.set_with_ttl(key, session, 30 * 60)  # 30 minutes
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        key = self._get_key("session", session_id)
        return self.delete(key)


class PlanManager(StateManager):
    """Manager for plan data."""
    
    def save_plan(self, plan_data: PlanData) -> bool:
        """Save plan data."""
        key = self._get_key("plan", plan_data.plan_id)
        return self.set_with_ttl(key, plan_data, CACHE_SETTINGS["plan_data_ttl"])
    
    def get_plan(self, plan_id: str) -> Optional[PlanData]:
        """Get plan data."""
        key = self._get_key("plan", plan_id)
        return self.get(key, PlanData)
    
    def get_user_plans(self, user_id: int) -> List[PlanData]:
        """Get all plans for user."""
        pattern = self._get_key("plan", "*")
        keys = self.get_keys_by_pattern(pattern)
        
        plans = []
        for key in keys:
            plan = self.get(key, PlanData)
            if plan and plan.patient_id == user_id:
                plans.append(plan)
        
        return sorted(plans, key=lambda p: p.generated_at, reverse=True)
    
    def get_latest_plan(self, user_id: int) -> Optional[PlanData]:
        """Get latest plan for user."""
        plans = self.get_user_plans(user_id)
        return plans[0] if plans else None
    
    def save_replacement(self, replacement_data: ReplacementData) -> bool:
        """Save replacement data."""
        key = self._get_key("replacement", replacement_data.replacement_id)
        return self.set_with_ttl(key, replacement_data, CACHE_SETTINGS["plan_data_ttl"])
    
    def get_replacement(self, replacement_id: str) -> Optional[ReplacementData]:
        """Get replacement data."""
        key = self._get_key("replacement", replacement_id)
        return self.get(key, ReplacementData)


class RateLimitManager(StateManager):
    """Manager for rate limiting."""
    
    def is_rate_limited(self, user_id: int, limit: int = 30, window: int = 60) -> bool:
        """Check if user is rate limited."""
        key = self._get_key("rate", str(user_id))
        
        try:
            # Get current count
            current = self.redis.get(key)
            if current is None:
                # First request
                self.redis.setex(key, window, 1)
                return False
            
            count = int(current)
            if count >= limit:
                return True
            
            # Increment count
            self.redis.incr(key)
            return False
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return False
    
    def reset_rate_limit(self, user_id: int) -> bool:
        """Reset rate limit for user."""
        key = self._get_key("rate", str(user_id))
        return self.delete(key)


class AnalyticsManager(StateManager):
    """Manager for analytics and metrics."""
    
    def record_conversation_start(self, user_id: int, motor_type: str) -> bool:
        """Record conversation start."""
        key = self._get_key("analytics", f"conv_start:{datetime.now().date()}")
        
        try:
            data = self.get(key) or {}
            data[motor_type] = data.get(motor_type, 0) + 1
            return self.set_with_ttl(key, data, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error(f"Error recording conversation start: {e}")
            return False
    
    def record_plan_generation(self, user_id: int, plan_type: str) -> bool:
        """Record plan generation."""
        key = self._get_key("analytics", f"plan_gen:{datetime.now().date()}")
        
        try:
            data = self.get(key) or {}
            data[plan_type] = data.get(plan_type, 0) + 1
            return self.set_with_ttl(key, data, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error(f"Error recording plan generation: {e}")
            return False
    
    def record_error(self, user_id: int, error_type: str, error_message: str) -> bool:
        """Record error."""
        key = self._get_key("analytics", f"errors:{datetime.now().date()}")
        
        try:
            data = self.get(key) or []
            data.append({
                "user_id": user_id,
                "error_type": error_type,
                "error_message": error_message,
                "timestamp": datetime.now().isoformat()
            })
            return self.set_with_ttl(key, data, 86400 * 7)  # 7 days
        except Exception as e:
            logger.error(f"Error recording error: {e}")
            return False
    
    def get_daily_stats(self, date: datetime = None) -> Dict[str, Any]:
        """Get daily statistics."""
        if not date:
            date = datetime.now()
        
        date_str = date.date()
        
        conv_key = self._get_key("analytics", f"conv_start:{date_str}")
        plan_key = self._get_key("analytics", f"plan_gen:{date_str}")
        error_key = self._get_key("analytics", f"errors:{date_str}")
        
        return {
            "date": date_str.isoformat(),
            "conversations": self.get(conv_key) or {},
            "plans": self.get(plan_key) or {},
            "errors": self.get(error_key) or []
        }