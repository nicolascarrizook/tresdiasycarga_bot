"""
User data models for Sistema Mayra Telegram Bot.
"""
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class ConversationStatus(Enum):
    """Conversation status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class UserData:
    """User data storage model."""
    
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = "es"
    
    # User preferences
    timezone: str = "America/Argentina/Buenos_Aires"
    notification_enabled: bool = True
    preferred_format: str = "pdf"
    
    # Statistics
    total_conversations: int = 0
    total_plans_generated: int = 0
    last_activity: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    # Flags
    is_active: bool = True
    is_blocked: bool = False
    is_admin: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "language_code": self.language_code,
            "timezone": self.timezone,
            "notification_enabled": self.notification_enabled,
            "preferred_format": self.preferred_format,
            "total_conversations": self.total_conversations,
            "total_plans_generated": self.total_plans_generated,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "is_blocked": self.is_blocked,
            "is_admin": self.is_admin
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserData":
        """Create from dictionary."""
        if "last_activity" in data and data["last_activity"]:
            data["last_activity"] = datetime.fromisoformat(data["last_activity"])
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class PatientData:
    """Patient data for plan generation."""
    
    # Basic information
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    
    # Objective and activity
    objective: Optional[str] = None
    activity_type: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[int] = None
    
    # Dietary preferences
    peso_tipo: Optional[str] = None
    economic_level: Optional[str] = None
    supplements: List[str] = field(default_factory=list)
    pathologies: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    preferences: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    
    # Meal configuration
    main_meals: Optional[int] = None
    collations: Optional[int] = None
    schedule: Optional[Dict[str, str]] = None
    
    # Additional information
    notes: Optional[str] = None
    telegram_user_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "age": self.age,
            "sex": self.sex,
            "height": self.height,
            "weight": self.weight,
            "objective": self.objective,
            "activity_type": self.activity_type,
            "frequency": self.frequency,
            "duration": self.duration,
            "peso_tipo": self.peso_tipo,
            "economic_level": self.economic_level,
            "supplements": self.supplements,
            "pathologies": self.pathologies,
            "restrictions": self.restrictions,
            "preferences": self.preferences,
            "dislikes": self.dislikes,
            "allergies": self.allergies,
            "main_meals": self.main_meals,
            "collations": self.collations,
            "schedule": self.schedule,
            "notes": self.notes,
            "telegram_user_id": self.telegram_user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatientData":
        """Create from dictionary."""
        return cls(**data)
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled."""
        required_fields = [
            "name", "age", "sex", "height", "weight",
            "objective", "activity_type", "frequency", "duration",
            "peso_tipo", "economic_level"
        ]
        
        for field in required_fields:
            if getattr(self, field) is None:
                return False
        return True
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields."""
        required_fields = [
            "name", "age", "sex", "height", "weight",
            "objective", "activity_type", "frequency", "duration",
            "peso_tipo", "economic_level"
        ]
        
        missing = []
        for field in required_fields:
            if getattr(self, field) is None:
                missing.append(field)
        return missing
    
    def calculate_bmi(self) -> Optional[float]:
        """Calculate BMI if height and weight are available."""
        if self.height and self.weight:
            height_m = self.height / 100  # Convert cm to m
            return round(self.weight / (height_m ** 2), 2)
        return None
    
    def get_display_summary(self) -> str:
        """Get formatted summary for display."""
        if not self.is_complete():
            return "Datos incompletos"
        
        bmi = self.calculate_bmi()
        bmi_str = f" (IMC: {bmi})" if bmi else ""
        
        return f"""
<b>Datos del Paciente:</b>
👤 Nombre: {self.name}
📅 Edad: {self.age} años
⚤ Sexo: {'Masculino' if self.sex == 'M' else 'Femenino'}
📏 Altura: {self.height} cm
⚖️ Peso: {self.weight} kg{bmi_str}

<b>Objetivo:</b> {self.objective}
<b>Actividad:</b> {self.activity_type} ({self.frequency}, {self.duration} min)
<b>Nivel Económico:</b> {self.economic_level}
<b>Tipo de Peso:</b> {self.peso_tipo}
"""


@dataclass
class ConversationData:
    """Conversation state and data."""
    
    user_id: int
    conversation_id: str
    motor_type: str
    current_state: str
    previous_state: Optional[str] = None
    
    # Data collection
    patient_data: PatientData = field(default_factory=PatientData)
    
    # Conversation flow
    status: ConversationStatus = ConversationStatus.ACTIVE
    started_at: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    
    # Context and navigation
    context: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    retries: int = 0
    max_retries: int = 3
    
    # Message tracking
    last_message_id: Optional[int] = None
    last_bot_message_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "motor_type": self.motor_type,
            "current_state": self.current_state,
            "previous_state": self.previous_state,
            "patient_data": self.patient_data.to_dict(),
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "last_update": self.last_update.isoformat(),
            "context": self.context,
            "errors": self.errors,
            "retries": self.retries,
            "max_retries": self.max_retries,
            "last_message_id": self.last_message_id,
            "last_bot_message_id": self.last_bot_message_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationData":
        """Create from dictionary."""
        data["patient_data"] = PatientData.from_dict(data["patient_data"])
        data["status"] = ConversationStatus(data["status"])
        data["started_at"] = datetime.fromisoformat(data["started_at"])
        data["last_update"] = datetime.fromisoformat(data["last_update"])
        return cls(**data)
    
    def update_state(self, new_state: str) -> None:
        """Update conversation state."""
        self.previous_state = self.current_state
        self.current_state = new_state
        self.last_update = datetime.now()
    
    def add_error(self, error: str) -> None:
        """Add error to conversation."""
        self.errors.append(error)
        self.retries += 1
        self.last_update = datetime.now()
    
    def reset_errors(self) -> None:
        """Reset error count."""
        self.errors.clear()
        self.retries = 0
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if conversation has expired."""
        timeout_delta = datetime.now() - self.last_update
        return timeout_delta.total_seconds() > (timeout_minutes * 60)
    
    def can_retry(self) -> bool:
        """Check if conversation can retry after error."""
        return self.retries < self.max_retries


@dataclass
class PlanData:
    """Generated plan data."""
    
    patient_id: int
    plan_id: str
    plan_type: str
    
    # Plan content
    plan_data: Dict[str, Any]
    calories_total: float
    macros: Dict[str, float]
    
    # Generation info
    generated_at: datetime = field(default_factory=datetime.now)
    generator_version: str = "1.0"
    
    # File info
    pdf_path: Optional[str] = None
    pdf_size: Optional[int] = None
    
    # Status
    is_active: bool = True
    is_sent: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "patient_id": self.patient_id,
            "plan_id": self.plan_id,
            "plan_type": self.plan_type,
            "plan_data": self.plan_data,
            "calories_total": self.calories_total,
            "macros": self.macros,
            "generated_at": self.generated_at.isoformat(),
            "generator_version": self.generator_version,
            "pdf_path": self.pdf_path,
            "pdf_size": self.pdf_size,
            "is_active": self.is_active,
            "is_sent": self.is_sent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanData":
        """Create from dictionary."""
        data["generated_at"] = datetime.fromisoformat(data["generated_at"])
        return cls(**data)


@dataclass
class ReplacementData:
    """Meal replacement data."""
    
    patient_id: int
    original_plan_id: str
    replacement_id: str
    
    # Replacement details
    day: str
    meal_type: str
    original_meal: Dict[str, Any]
    replacement_meal: Dict[str, Any]
    
    # Request info
    replacement_type: str
    reason: str
    specific_request: Optional[str] = None
    special_conditions: Optional[str] = None
    
    # Generation info
    generated_at: datetime = field(default_factory=datetime.now)
    
    # Status
    is_active: bool = True
    is_applied: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "patient_id": self.patient_id,
            "original_plan_id": self.original_plan_id,
            "replacement_id": self.replacement_id,
            "day": self.day,
            "meal_type": self.meal_type,
            "original_meal": self.original_meal,
            "replacement_meal": self.replacement_meal,
            "replacement_type": self.replacement_type,
            "reason": self.reason,
            "specific_request": self.specific_request,
            "special_conditions": self.special_conditions,
            "generated_at": self.generated_at.isoformat(),
            "is_active": self.is_active,
            "is_applied": self.is_applied
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplacementData":
        """Create from dictionary."""
        data["generated_at"] = datetime.fromisoformat(data["generated_at"])
        return cls(**data)


@dataclass
class SessionData:
    """Session data for temporary storage."""
    
    user_id: int
    session_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionData":
        """Create from dictionary."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("expires_at"):
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False


@dataclass
class UserPreferences:
    """User preferences and settings."""
    
    user_id: int
    language: str = "es"
    timezone: str = "America/Argentina/Buenos_Aires"
    date_format: str = "%d/%m/%Y"
    time_format: str = "%H:%M"
    
    # Notification preferences
    notifications_enabled: bool = True
    plan_reminders: bool = True
    progress_notifications: bool = True
    
    # Display preferences
    preferred_units: str = "metric"  # metric or imperial
    decimal_places: int = 1
    show_macros: bool = True
    show_calories: bool = True
    
    # Privacy settings
    data_sharing: bool = False
    analytics_tracking: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "language": self.language,
            "timezone": self.timezone,
            "date_format": self.date_format,
            "time_format": self.time_format,
            "notifications_enabled": self.notifications_enabled,
            "plan_reminders": self.plan_reminders,
            "progress_notifications": self.progress_notifications,
            "preferred_units": self.preferred_units,
            "decimal_places": self.decimal_places,
            "show_macros": self.show_macros,
            "show_calories": self.show_calories,
            "data_sharing": self.data_sharing,
            "analytics_tracking": self.analytics_tracking
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferences":
        """Create from dictionary."""
        return cls(**data)