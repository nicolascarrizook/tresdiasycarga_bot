"""
Configuration settings for Sistema Mayra Telegram Bot.
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field


class BotSettings(BaseSettings):
    """Telegram bot configuration settings."""
    
    # Bot credentials
    bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    webhook_url: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_URL")
    webhook_path: str = Field("/telegram/webhook", env="TELEGRAM_WEBHOOK_PATH")
    webhook_secret: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_SECRET")
    
    # Bot behavior
    parse_mode: str = Field("HTML", env="TELEGRAM_PARSE_MODE")
    max_message_length: int = Field(4096, env="TELEGRAM_MAX_MESSAGE_LENGTH")
    timeout: int = Field(30, env="TELEGRAM_TIMEOUT")
    retry_attempts: int = Field(3, env="TELEGRAM_RETRY_ATTEMPTS")
    
    # Conversation settings
    conversation_timeout: int = Field(1800, env="CONVERSATION_TIMEOUT")  # 30 minutes
    per_user_timeout: int = Field(3600, env="PER_USER_TIMEOUT")  # 1 hour
    
    # File handling
    max_file_size: int = Field(20 * 1024 * 1024, env="MAX_FILE_SIZE")  # 20MB
    temp_dir: str = Field("/tmp/telegram_bot", env="TEMP_DIR")
    
    # API integration
    api_base_url: str = Field("http://localhost:8000", env="API_BASE_URL")
    api_timeout: int = Field(30, env="API_TIMEOUT")
    
    # Database
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    redis_db: int = Field(0, env="REDIS_DB")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(None, env="LOG_FILE")
    
    # Development
    debug: bool = Field(False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global bot settings instance
bot_settings = BotSettings()


# Bot configuration constants
BOT_CONFIG = {
    "allowed_updates": ["message", "callback_query", "inline_query"],
    "drop_pending_updates": True,
    "local_mode": False,
    "use_context": True,
    "arbitrary_callback_data": True,
    
    # Rate limiting
    "rate_limit": {
        "enabled": True,
        "max_requests": 30,
        "window_seconds": 60,
        "per_user": True
    },
    
    # Error handling
    "error_retry_delay": 5,
    "max_error_retries": 3,
    
    # Conversation persistence
    "persistence": {
        "enabled": True,
        "store_user_data": True,
        "store_chat_data": True,
        "store_bot_data": True
    }
}


# Message templates
MESSAGE_TEMPLATES = {
    "welcome": """
¡Hola {name}! 👋

Soy el asistente de Mayra y te ayudo a crear tu plan nutricional personalizado usando el método <b>"Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva"</b>.

¿Qué necesitas hacer hoy?
""",
    
    "motor_selection": """
Selecciona el tipo de consulta que necesitas:

🆕 <b>Nuevo Paciente</b>
Crear un plan nutricional completo desde cero

🔄 <b>Control/Ajuste</b>
Modificar tu plan existente según tu progreso

🍽️ <b>Reemplazo de Comida</b>
Cambiar una comida específica manteniendo los macros

¿Cuál prefieres?
""",
    
    "data_collection_start": """
Perfecto! Voy a recopilar algunos datos para crear tu plan personalizado.

Este proceso tomará aproximadamente 5-10 minutos. Puedes cancelar en cualquier momento escribiendo /cancel.

¿Empezamos? 🚀
""",
    
    "plan_generated": """
¡Excelente! 🎉

Tu plan nutricional personalizado ha sido generado exitosamente usando el método <b>"Tres Días y Carga"</b>.

📋 El plan incluye:
• 3 días de menú completo
• Porciones exactas en gramos
• Instrucciones de preparación
• Equivalencias nutricionales

Te envío el PDF con todos los detalles 📄
""",
    
    "error_general": """
😔 Ocurrió un error inesperado.

Por favor, intenta nuevamente o contacta al administrador si el problema persiste.

Puedes escribir /start para comenzar de nuevo.
""",
    
    "error_timeout": """
⏰ La conversación ha expirado por inactividad.

Escribe /start para comenzar un nuevo proceso.
""",
    
    "error_invalid_data": """
❌ Los datos ingresados no son válidos.

Por favor, revisa la información e intenta nuevamente.
""",
    
    "cancel_conversation": """
❌ Proceso cancelado.

Escribe /start cuando quieras comenzar de nuevo.
""",
    
    "help_message": """
<b>Sistema Mayra - Asistente Nutricional</b>

<b>Comandos disponibles:</b>
/start - Iniciar nueva consulta
/help - Mostrar esta ayuda
/cancel - Cancelar proceso actual
/mi_info - Ver mi información guardada
/historial - Ver historial de planes

<b>Tipos de consulta:</b>
🆕 <b>Nuevo Paciente:</b> Plan completo desde cero
🔄 <b>Control:</b> Ajustar plan existente
🍽️ <b>Reemplazo:</b> Cambiar comida específica

<b>Método "Tres Días y Carga":</b>
• Plan de 3 días iguales en calorías y macros
• Porciones exactas en gramos
• Adaptado a tu objetivo y actividad
• Incluye preparación detallada

¿Necesitas ayuda específica? Escribe /start para comenzar.
""",
    
    "maintenance_mode": """
🔧 <b>Mantenimiento del Sistema</b>

El bot está temporalmente en mantenimiento para mejoras.

Vuelve a intentar en unos minutos.
""",
    
    "user_blocked": """
🚫 <b>Acceso Restringido</b>

Tu acceso al bot ha sido temporalmente restringido.

Contacta al administrador para más información.
"""
}


# Keyboard button texts
KEYBOARD_TEXTS = {
    "motors": {
        "new_patient": "🆕 Nuevo Paciente",
        "control": "🔄 Control/Ajuste", 
        "replacement": "🍽️ Reemplazo de Comida"
    },
    
    "common": {
        "yes": "✅ Sí",
        "no": "❌ No",
        "skip": "⏭️ Saltar",
        "back": "⬅️ Atrás",
        "cancel": "❌ Cancelar",
        "continue": "➡️ Continuar",
        "confirm": "✅ Confirmar",
        "edit": "✏️ Editar"
    },
    
    "objectives": {
        "maintenance": "🔄 Mantenimiento",
        "lose_half_kg": "📉 Bajar 0.5kg",
        "lose_one_kg": "📉 Bajar 1kg",
        "lose_two_kg": "📉 Bajar 2kg",
        "gain_half_kg": "📈 Subir 0.5kg",
        "gain_one_kg": "📈 Subir 1kg"
    },
    
    "activities": {
        "sedentary": "🪑 Sedentario",
        "walking": "🚶 Caminatas",
        "weights": "🏋️ Pesas",
        "cardio": "🏃 Cardio",
        "mixed": "🏃🏋️ Mixto",
        "athlete": "🏆 Deportista"
    },
    
    "frequencies": {
        "never": "❌ Nunca",
        "once_week": "1️⃣ 1 vez/semana",
        "twice_week": "2️⃣ 2 veces/semana",
        "three_times_week": "3️⃣ 3 veces/semana",
        "four_times_week": "4️⃣ 4 veces/semana",
        "five_times_week": "5️⃣ 5 veces/semana",
        "daily": "📅 Diario"
    },
    
    "weight_types": {
        "raw": "🥩 Crudo",
        "cooked": "🍽️ Cocido"
    },
    
    "economic_levels": {
        "low": "💰 Económico",
        "medium": "💰💰 Intermedio",
        "high": "💰💰💰 Premium"
    },
    
    "sex": {
        "M": "👨 Masculino",
        "F": "👩 Femenino"
    },
    
    "meal_types": {
        "breakfast": "🌅 Desayuno",
        "lunch": "🍽️ Almuerzo",
        "snack": "🍪 Merienda",
        "dinner": "🌙 Cena",
        "collation": "🥨 Colación"
    },
    
    "days": {
        "day_1": "📅 Día 1",
        "day_2": "📅 Día 2", 
        "day_3": "📅 Día 3"
    }
}


# Validation messages
VALIDATION_MESSAGES = {
    "name": {
        "required": "Por favor, ingresa tu nombre.",
        "min_length": "El nombre debe tener al menos 2 caracteres.",
        "max_length": "El nombre no puede tener más de 50 caracteres.",
        "invalid_chars": "El nombre solo puede contener letras y espacios."
    },
    
    "age": {
        "required": "Por favor, ingresa tu edad.",
        "invalid_format": "La edad debe ser un número entero.",
        "min_value": "La edad mínima es 16 años.",
        "max_value": "La edad máxima es 80 años."
    },
    
    "weight": {
        "required": "Por favor, ingresa tu peso actual.",
        "invalid_format": "El peso debe ser un número (puedes usar decimales).",
        "min_value": "El peso mínimo es 40 kg.",
        "max_value": "El peso máximo es 200 kg."
    },
    
    "height": {
        "required": "Por favor, ingresa tu altura.",
        "invalid_format": "La altura debe ser un número (puedes usar decimales).",
        "min_value": "La altura mínima es 140 cm.",
        "max_value": "La altura máxima es 220 cm."
    },
    
    "activity_duration": {
        "required": "Por favor, ingresa la duración de tu actividad.",
        "invalid_format": "La duración debe ser un número entero en minutos.",
        "min_value": "La duración mínima es 15 minutos.",
        "max_value": "La duración máxima es 300 minutos (5 horas)."
    },
    
    "notes": {
        "max_length": "Las notas no pueden tener más de 500 caracteres."
    }
}


# File and media settings
FILE_SETTINGS = {
    "allowed_document_types": [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/gif"
    ],
    
    "max_file_size": 20 * 1024 * 1024,  # 20MB
    
    "pdf_generation": {
        "timeout": 30,
        "quality": "high",
        "format": "A4",
        "orientation": "portrait"
    },
    
    "image_processing": {
        "max_width": 1920,
        "max_height": 1080,
        "quality": 85,
        "format": "JPEG"
    }
}


# Cache settings
CACHE_SETTINGS = {
    "user_data_ttl": 3600,  # 1 hour
    "conversation_ttl": 1800,  # 30 minutes
    "plan_data_ttl": 86400,  # 24 hours
    "recipe_data_ttl": 43200,  # 12 hours
    
    "keys": {
        "user_data": "user:{user_id}",
        "conversation": "conv:{user_id}",
        "patient_data": "patient:{user_id}",
        "plan_history": "plans:{user_id}",
        "rate_limit": "rate:{user_id}"
    }
}


# Feature flags
FEATURE_FLAGS = {
    "maintenance_mode": False,
    "new_user_registration": True,
    "pdf_generation": True,
    "meal_replacement": True,
    "control_appointments": True,
    "user_analytics": True,
    "admin_commands": True,
    "rate_limiting": True,
    "conversation_persistence": True
}


# Admin configuration
ADMIN_CONFIG = {
    "admin_user_ids": [
        # Add admin user IDs here
    ],
    
    "commands": {
        "stats": "/admin_stats",
        "users": "/admin_users", 
        "maintenance": "/admin_maintenance",
        "broadcast": "/admin_broadcast",
        "logs": "/admin_logs"
    },
    
    "permissions": {
        "view_stats": True,
        "manage_users": True,
        "system_control": True,
        "send_broadcasts": True,
        "view_logs": True
    }
}


# Monitoring and analytics
MONITORING_CONFIG = {
    "metrics": {
        "enabled": True,
        "endpoint": "/metrics",
        "collect_user_metrics": True,
        "collect_conversation_metrics": True,
        "collect_api_metrics": True
    },
    
    "alerts": {
        "enabled": True,
        "error_threshold": 10,  # errors per minute
        "response_time_threshold": 5000,  # milliseconds
        "memory_threshold": 80,  # percentage
        "disk_threshold": 90  # percentage
    }
}