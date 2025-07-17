"""
Localization support for Sistema Mayra Telegram Bot.
"""
import random
from typing import Dict, Any, Optional
from datetime import datetime

from .es import MESSAGES, FIELD_LABELS, OPTION_LABELS, TIME_MESSAGES, SEASONAL_GREETINGS, MOTIVATIONAL_MESSAGES


class Localizer:
    """Localization manager for the bot."""
    
    def __init__(self, language: str = "es"):
        """Initialize localizer with language."""
        self.language = language
        self.messages = MESSAGES
        self.field_labels = FIELD_LABELS
        self.option_labels = OPTION_LABELS
        self.time_messages = TIME_MESSAGES
        self.seasonal_greetings = SEASONAL_GREETINGS
        self.motivational_messages = MOTIVATIONAL_MESSAGES
    
    def get_message(self, key: str, **kwargs) -> str:
        """Get localized message with optional formatting."""
        message = self.messages.get(key, f"Missing message: {key}")
        
        if kwargs:
            try:
                return message.format(**kwargs)
            except KeyError as e:
                return f"Message formatting error: {e}"
        
        return message
    
    def get_field_label(self, field: str) -> str:
        """Get field label."""
        return self.field_labels.get(field, field.title())
    
    def get_option_label(self, category: str, option: str) -> str:
        """Get option label."""
        return self.option_labels.get(category, {}).get(option, option)
    
    def get_time_greeting(self) -> str:
        """Get time-appropriate greeting."""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return self.time_messages["morning"]
        elif 12 <= hour < 18:
            return self.time_messages["afternoon"]
        elif 18 <= hour < 22:
            return self.time_messages["evening"]
        else:
            return self.time_messages["dawn"]
    
    def get_seasonal_greeting(self) -> str:
        """Get seasonal greeting."""
        month = datetime.now().month
        
        if month in [12, 1, 2]:
            return self.seasonal_greetings["summer"]  # Southern hemisphere
        elif month in [3, 4, 5]:
            return self.seasonal_greetings["autumn"]
        elif month in [6, 7, 8]:
            return self.seasonal_greetings["winter"]
        else:
            return self.seasonal_greetings["spring"]
    
    def get_motivational_message(self) -> str:
        """Get random motivational message."""
        return random.choice(self.motivational_messages)
    
    def format_patient_summary(self, patient_data: Dict[str, Any]) -> str:
        """Format patient data summary."""
        summary_lines = []
        
        # Basic info
        if patient_data.get("name"):
            summary_lines.append(f"👤 <b>Nombre:</b> {patient_data['name']}")
        
        if patient_data.get("age"):
            summary_lines.append(f"📅 <b>Edad:</b> {patient_data['age']} años")
        
        if patient_data.get("sex"):
            sex_label = self.get_option_label("sex", patient_data["sex"])
            summary_lines.append(f"⚤ <b>Sexo:</b> {sex_label}")
        
        if patient_data.get("height"):
            summary_lines.append(f"📏 <b>Altura:</b> {patient_data['height']} cm")
        
        if patient_data.get("weight"):
            summary_lines.append(f"⚖️ <b>Peso:</b> {patient_data['weight']} kg")
        
        # Calculate BMI if both height and weight are available
        if patient_data.get("height") and patient_data.get("weight"):
            height_m = patient_data["height"] / 100
            bmi = patient_data["weight"] / (height_m ** 2)
            summary_lines.append(f"📊 <b>IMC:</b> {bmi:.1f}")
        
        # Objective and activity
        if patient_data.get("objective"):
            obj_label = self.get_option_label("objectives", patient_data["objective"])
            summary_lines.append(f"🎯 <b>Objetivo:</b> {obj_label}")
        
        if patient_data.get("activity_type"):
            act_label = self.get_option_label("activities", patient_data["activity_type"])
            freq_label = self.get_option_label("frequencies", patient_data.get("frequency", ""))
            duration = patient_data.get("duration", "")
            
            activity_text = f"{act_label}"
            if freq_label:
                activity_text += f" ({freq_label}"
                if duration:
                    activity_text += f", {duration} min"
                activity_text += ")"
            
            summary_lines.append(f"🏃 <b>Actividad:</b> {activity_text}")
        
        # Dietary preferences
        if patient_data.get("economic_level"):
            econ_label = self.get_option_label("economic_levels", patient_data["economic_level"])
            summary_lines.append(f"💰 <b>Nivel Económico:</b> {econ_label}")
        
        if patient_data.get("peso_tipo"):
            weight_label = self.get_option_label("weight_types", patient_data["peso_tipo"])
            summary_lines.append(f"🥩 <b>Tipo de Peso:</b> {weight_label}")
        
        # Meal configuration
        if patient_data.get("main_meals"):
            summary_lines.append(f"🍽️ <b>Comidas Principales:</b> {patient_data['main_meals']}")
        
        if patient_data.get("collations"):
            summary_lines.append(f"🥨 <b>Colaciones:</b> {patient_data['collations']}")
        
        # Lists
        if patient_data.get("supplements"):
            supplements_text = ", ".join(patient_data["supplements"])
            summary_lines.append(f"💊 <b>Suplementos:</b> {supplements_text}")
        
        if patient_data.get("pathologies"):
            pathologies_text = ", ".join(patient_data["pathologies"])
            summary_lines.append(f"🩺 <b>Patologías:</b> {pathologies_text}")
        
        if patient_data.get("restrictions"):
            restrictions_text = ", ".join(patient_data["restrictions"])
            summary_lines.append(f"🚫 <b>Restricciones:</b> {restrictions_text}")
        
        if patient_data.get("preferences"):
            preferences_text = ", ".join(patient_data["preferences"])
            summary_lines.append(f"❤️ <b>Preferencias:</b> {preferences_text}")
        
        if patient_data.get("dislikes"):
            dislikes_text = ", ".join(patient_data["dislikes"])
            summary_lines.append(f"❌ <b>No me gusta:</b> {dislikes_text}")
        
        if patient_data.get("allergies"):
            allergies_text = ", ".join(patient_data["allergies"])
            summary_lines.append(f"🤧 <b>Alergias:</b> {allergies_text}")
        
        # Notes
        if patient_data.get("notes"):
            summary_lines.append(f"📝 <b>Notas:</b> {patient_data['notes']}")
        
        return "\n".join(summary_lines)
    
    def format_validation_error(self, field: str, error_type: str) -> str:
        """Format validation error message."""
        field_label = self.get_field_label(field)
        
        error_key = f"validation_{field}"
        if error_key in self.messages:
            return self.messages[error_key]
        
        # Generic validation messages
        if error_type == "required":
            return f"❌ <b>{field_label} es requerido</b>\n\nPor favor, ingresa un valor válido."
        elif error_type == "invalid_format":
            return f"❌ <b>{field_label} inválido</b>\n\nEl formato ingresado no es correcto."
        elif error_type == "out_of_range":
            return f"❌ <b>{field_label} fuera de rango</b>\n\nEl valor debe estar dentro del rango permitido."
        else:
            return f"❌ <b>Error en {field_label}</b>\n\nPor favor, corrige el valor ingresado."
    
    def format_missing_fields(self, missing_fields: list) -> str:
        """Format missing fields message."""
        if not missing_fields:
            return ""
        
        field_labels = [self.get_field_label(field) for field in missing_fields]
        
        if len(field_labels) == 1:
            return f"Falta información de: <b>{field_labels[0]}</b>"
        else:
            return f"Faltan datos de: <b>{', '.join(field_labels)}</b>"
    
    def format_progress_message(self, progress: int) -> str:
        """Format progress message."""
        if progress >= 100:
            return self.get_message("progress_100")
        elif progress >= 90:
            return self.get_message("progress_90")
        elif progress >= 75:
            return self.get_message("progress_75")
        elif progress >= 50:
            return self.get_message("progress_50")
        elif progress >= 25:
            return self.get_message("progress_25")
        else:
            return self.get_message("progress_10")
    
    def format_plan_history(self, plans: list) -> str:
        """Format plan history."""
        if not plans:
            return "No tienes planes generados aún."
        
        history_lines = []
        for i, plan in enumerate(plans, 1):
            date = plan.get("date", "Fecha no disponible")
            plan_type = plan.get("type", "Tipo no disponible")
            
            history_lines.append(f"{i}. {date} - {plan_type}")
        
        return "\n".join(history_lines)
    
    def format_changes_summary(self, changes: Dict[str, Any]) -> str:
        """Format changes summary for Motor 2."""
        summary_lines = []
        
        for field, value in changes.items():
            field_label = self.get_field_label(field)
            
            if isinstance(value, dict):
                if "from" in value and "to" in value:
                    summary_lines.append(f"🔄 <b>{field_label}:</b> {value['from']} → {value['to']}")
                else:
                    summary_lines.append(f"📝 <b>{field_label}:</b> {value}")
            elif isinstance(value, list):
                if value:
                    summary_lines.append(f"📝 <b>{field_label}:</b> {', '.join(value)}")
            else:
                summary_lines.append(f"📝 <b>{field_label}:</b> {value}")
        
        return "\n".join(summary_lines) if summary_lines else "No se realizaron cambios."
    
    def format_replacement_details(self, replacement: Dict[str, Any]) -> str:
        """Format replacement details for Motor 3."""
        details_lines = []
        
        if replacement.get("day"):
            details_lines.append(f"📅 <b>Día:</b> {replacement['day']}")
        
        if replacement.get("meal_type"):
            details_lines.append(f"🍽️ <b>Comida:</b> {replacement['meal_type']}")
        
        if replacement.get("reason"):
            details_lines.append(f"💭 <b>Motivo:</b> {replacement['reason']}")
        
        if replacement.get("specific_request"):
            details_lines.append(f"🎯 <b>Solicitud:</b> {replacement['specific_request']}")
        
        if replacement.get("special_conditions"):
            details_lines.append(f"⚠️ <b>Condiciones:</b> {replacement['special_conditions']}")
        
        return "\n".join(details_lines)
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def format_time_ago(self, timestamp: datetime) -> str:
        """Format time ago from timestamp."""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"hace {hours} hora{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "hace un momento"


# Global localizer instance
localizer = Localizer()

# Convenience functions
def get_message(key: str, **kwargs) -> str:
    """Get localized message."""
    return localizer.get_message(key, **kwargs)

def get_field_label(field: str) -> str:
    """Get field label."""
    return localizer.get_field_label(field)

def get_option_label(category: str, option: str) -> str:
    """Get option label."""
    return localizer.get_option_label(category, option)

def format_patient_summary(patient_data: Dict[str, Any]) -> str:
    """Format patient data summary."""
    return localizer.format_patient_summary(patient_data)

def format_validation_error(field: str, error_type: str) -> str:
    """Format validation error."""
    return localizer.format_validation_error(field, error_type)

def get_motivational_message() -> str:
    """Get random motivational message."""
    return localizer.get_motivational_message()

def get_time_greeting() -> str:
    """Get time-appropriate greeting."""
    return localizer.get_time_greeting()

__all__ = [
    "Localizer",
    "localizer",
    "get_message",
    "get_field_label",
    "get_option_label",
    "format_patient_summary",
    "format_validation_error",
    "get_motivational_message",
    "get_time_greeting"
]