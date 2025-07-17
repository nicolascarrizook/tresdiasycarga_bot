"""
Application settings and constants for Sistema Mayra API.
"""
from enum import Enum
from typing import Dict, List


class ObjectiveType(str, Enum):
    """Nutrition plan objectives."""
    MAINTENANCE = "mantenimiento"
    LOSE_HALF_KG = "bajar_0.5kg"
    LOSE_ONE_KG = "bajar_1kg"
    LOSE_TWO_KG = "bajar_2kg"
    GAIN_HALF_KG = "subir_0.5kg"
    GAIN_ONE_KG = "subir_1kg"


class ActivityType(str, Enum):
    """Physical activity types."""
    SEDENTARY = "sedentario"
    WALKING = "caminatas"
    WEIGHTS = "pesas"
    CARDIO = "cardio"
    MIXED = "mixto"
    ATHLETE = "deportista"


class FrequencyType(str, Enum):
    """Activity frequency."""
    NEVER = "nunca"
    ONCE_WEEK = "1_vez_semana"
    TWICE_WEEK = "2_veces_semana"
    THREE_TIMES_WEEK = "3_veces_semana"
    FOUR_TIMES_WEEK = "4_veces_semana"
    FIVE_TIMES_WEEK = "5_veces_semana"
    DAILY = "diario"


class WeightType(str, Enum):
    """Weight measurement type."""
    RAW = "crudo"
    COOKED = "cocido"


class EconomicLevel(str, Enum):
    """Economic level for recipe filtering."""
    LOW = "bajo"
    MEDIUM = "medio"
    HIGH = "alto"


class MealType(str, Enum):
    """Meal types."""
    BREAKFAST = "desayuno"
    LUNCH = "almuerzo"
    SNACK = "merienda"
    DINNER = "cena"
    COLLATION = "colacion"


class RecipeCategory(str, Enum):
    """Recipe categories."""
    CHICKEN = "pollo"
    MEAT = "carne"
    VEGETARIAN = "vegetariano"
    PORK = "cerdo"
    FISH_SEAFOOD = "pescado_mariscos"
    SALAD = "ensalada"
    BREAKFAST_SWEET = "desayuno_dulce"
    BREAKFAST_SAVORY = "desayuno_salado"
    COLLATION = "colacion"


class PlanType(str, Enum):
    """Plan generation types."""
    NEW_PATIENT = "nuevo_paciente"
    CONTROL = "control"
    REPLACEMENT = "reemplazo"


class DietaryRestriction(str, Enum):
    """Dietary restrictions."""
    VEGETARIAN = "vegetariano"
    VEGAN = "vegano"
    GLUTEN_FREE = "sin_gluten"
    LACTOSE_FREE = "sin_lactosa"
    DIABETIC = "diabetico"
    HYPERTENSION = "hipertension"
    RENAL = "renal"
    CARDIAC = "cardiaco"


class SupplementType(str, Enum):
    """Supplement types."""
    WHEY_PROTEIN = "proteina_whey"
    CREATINE = "creatina"
    MULTIVITAMIN = "multivitaminico"
    OMEGA_3 = "omega_3"
    MAGNESIUM = "magnesio"
    VITAMIN_D = "vitamina_d"
    BCAA = "bcaa"


# System constants
SYSTEM_CONSTANTS = {
    "plan_duration_days": 3,
    "meals_per_day": 5,
    "macro_tolerance_percent": 5,
    "default_calories_per_kg": {
        "maintenance": 30,
        "weight_loss": 25,
        "weight_gain": 35
    },
    "protein_per_kg": {
        "sedentary": 0.8,
        "active": 1.2,
        "athlete": 1.6
    },
    "carb_percentage": {
        "low": 0.30,
        "medium": 0.45,
        "high": 0.60
    },
    "fat_percentage": {
        "min": 0.20,
        "max": 0.35
    }
}

# Meal scheduling defaults
MEAL_SCHEDULES = {
    "default": {
        "breakfast": "07:00",
        "collation_1": "10:00",
        "lunch": "13:00",
        "snack": "16:00",
        "dinner": "20:00"
    },
    "early_riser": {
        "breakfast": "06:00",
        "collation_1": "09:00",
        "lunch": "12:00",
        "snack": "15:00",
        "dinner": "19:00"
    },
    "night_owl": {
        "breakfast": "09:00",
        "collation_1": "12:00",
        "lunch": "15:00",
        "snack": "18:00",
        "dinner": "21:00"
    }
}

# Portion sizes for different food groups (in grams)
PORTION_SIZES = {
    "protein": {
        "chicken": 100,
        "meat": 100,
        "fish": 120,
        "eggs": 50,  # 1 egg
        "cheese": 30
    },
    "carbs": {
        "rice": 60,  # raw
        "pasta": 70,  # raw
        "bread": 30,  # 1 slice
        "potato": 150,  # cooked
        "sweet_potato": 120  # cooked
    },
    "fats": {
        "oil": 10,  # 1 tbsp
        "nuts": 20,
        "avocado": 50,
        "seeds": 15
    },
    "vegetables": {
        "leafy": 200,
        "cruciferous": 150,
        "root": 100
    },
    "fruits": {
        "apple": 150,
        "banana": 120,
        "orange": 180,
        "berries": 100
    }
}

# Macronutrient values per gram
MACRO_VALUES = {
    "protein": 4,  # kcal/g
    "carbs": 4,    # kcal/g
    "fat": 9,      # kcal/g
    "alcohol": 7   # kcal/g
}

# Bot messages and responses
BOT_MESSAGES = {
    "welcome": "¡Hola! Soy el asistente de Mayra. Te ayudo a crear tu plan nutricional personalizado usando el método 'Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva'.",
    "motor_selection": "¿Qué necesitas hacer hoy?",
    "data_collection": "Necesito algunos datos para crear tu plan personalizado:",
    "plan_generated": "¡Perfecto! Tu plan nutricional ha sido generado. Te lo envío en PDF:",
    "error": "Ocurrió un error. Por favor, intenta nuevamente o contacta al administrador."
}

# PDF template settings
PDF_SETTINGS = {
    "page_size": "A4",
    "margin": {
        "top": 20,
        "bottom": 20,
        "left": 20,
        "right": 20
    },
    "font_family": "Arial",
    "font_sizes": {
        "title": 16,
        "subtitle": 14,
        "body": 12,
        "small": 10
    },
    "colors": {
        "primary": "#2E7D32",
        "secondary": "#4CAF50",
        "text": "#333333",
        "light_gray": "#F5F5F5"
    }
}

# Validation rules
VALIDATION_RULES = {
    "age": {"min": 16, "max": 80},
    "weight": {"min": 40, "max": 200},
    "height": {"min": 140, "max": 220},
    "activity_duration": {"min": 15, "max": 300},  # minutes
    "name_length": {"min": 2, "max": 50},
    "notes_length": {"max": 500}
}

# RAG system settings
RAG_SETTINGS = {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "similarity_threshold": 0.7,
    "max_results": 10,
    "rerank_results": True
}

# Telegram bot settings
TELEGRAM_SETTINGS = {
    "max_message_length": 4096,
    "timeout": 30,
    "retry_attempts": 3,
    "webhook_timeout": 60,
    "allowed_updates": ["message", "callback_query"],
    "parse_mode": "HTML"
}