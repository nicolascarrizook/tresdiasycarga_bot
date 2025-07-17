"""
Validation utilities for Sistema Mayra API.
"""
import re
from typing import Any, Dict, List, Optional

from ..core.settings import VALIDATION_RULES


def validate_patient_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate patient data."""
    errors = {}
    
    # Validate age
    age = data.get("age")
    if age is not None:
        if not isinstance(age, int) or age < VALIDATION_RULES["age"]["min"] or age > VALIDATION_RULES["age"]["max"]:
            errors["age"] = [f"Age must be between {VALIDATION_RULES['age']['min']} and {VALIDATION_RULES['age']['max']}"]
    
    # Validate weight
    weight = data.get("weight")
    if weight is not None:
        if not isinstance(weight, (int, float)) or weight < VALIDATION_RULES["weight"]["min"] or weight > VALIDATION_RULES["weight"]["max"]:
            errors["weight"] = [f"Weight must be between {VALIDATION_RULES['weight']['min']} and {VALIDATION_RULES['weight']['max']} kg"]
    
    # Validate height
    height = data.get("height")
    if height is not None:
        if not isinstance(height, (int, float)) or height < VALIDATION_RULES["height"]["min"] or height > VALIDATION_RULES["height"]["max"]:
            errors["height"] = [f"Height must be between {VALIDATION_RULES['height']['min']} and {VALIDATION_RULES['height']['max']} cm"]
    
    # Validate name
    name = data.get("name")
    if name is not None:
        if not isinstance(name, str) or len(name) < VALIDATION_RULES["name_length"]["min"] or len(name) > VALIDATION_RULES["name_length"]["max"]:
            errors["name"] = [f"Name must be between {VALIDATION_RULES['name_length']['min']} and {VALIDATION_RULES['name_length']['max']} characters"]
    
    return errors


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Basic phone validation (can be enhanced)
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None


def validate_password(password: str) -> List[str]:
    """Validate password strength."""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return errors


def sanitize_string(value: str) -> str:
    """Sanitize string input."""
    if not isinstance(value, str):
        return str(value)
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Basic HTML escaping
    value = value.replace('<', '&lt;').replace('>', '&gt;')
    
    return value


def validate_nutrition_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate nutrition data."""
    errors = {}
    
    # Validate calories
    calories = data.get("calories")
    if calories is not None:
        if not isinstance(calories, (int, float)) or calories < 0 or calories > 5000:
            errors["calories"] = ["Calories must be between 0 and 5000"]
    
    # Validate macros
    for macro in ["protein", "carbs", "fat"]:
        value = data.get(macro)
        if value is not None:
            if not isinstance(value, (int, float)) or value < 0 or value > 1000:
                errors[macro] = [f"{macro.capitalize()} must be between 0 and 1000 grams"]
    
    return errors


def validate_file_upload(file_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate file upload data."""
    errors = {}
    
    # Validate file size
    file_size = file_data.get("file_size")
    if file_size is not None:
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            errors["file_size"] = [f"File size must be less than {max_size / (1024*1024):.1f}MB"]
    
    # Validate content type
    content_type = file_data.get("content_type")
    if content_type is not None:
        allowed_types = ["image/jpeg", "image/png", "application/pdf"]
        if content_type not in allowed_types:
            errors["content_type"] = [f"Content type must be one of: {', '.join(allowed_types)}"]
    
    return errors