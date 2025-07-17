"""
Conversation state definitions for Sistema Mayra Telegram Bot.
"""
from enum import Enum, auto


class ConversationState(Enum):
    """Base conversation states."""
    
    IDLE = auto()
    MOTOR_SELECTION = auto()
    CANCELLED = auto()
    ENDED = auto()
    ERROR = auto()
    

class CommonStates(Enum):
    """Common states used across all motors."""
    
    CONFIRMATION = auto()
    EDITING = auto()
    WAITING_INPUT = auto()
    PROCESSING = auto()
    SENDING_RESULT = auto()


class Motor1States(Enum):
    """States for Motor 1 (New Patient) conversation flow."""
    
    # Basic personal data
    ASKING_NAME = auto()
    ASKING_AGE = auto()
    ASKING_SEX = auto()
    ASKING_HEIGHT = auto()
    ASKING_WEIGHT = auto()
    
    # Objective and activity
    ASKING_OBJECTIVE = auto()
    ASKING_ACTIVITY_TYPE = auto()
    ASKING_ACTIVITY_FREQUENCY = auto()
    ASKING_ACTIVITY_DURATION = auto()
    
    # Dietary preferences and restrictions
    ASKING_WEIGHT_TYPE = auto()
    ASKING_ECONOMIC_LEVEL = auto()
    ASKING_SUPPLEMENTS = auto()
    ASKING_PATHOLOGIES = auto()
    ASKING_RESTRICTIONS = auto()
    ASKING_PREFERENCES = auto()
    ASKING_DISLIKES = auto()
    ASKING_ALLERGIES = auto()
    
    # Meal configuration
    ASKING_MAIN_MEALS = auto()
    ASKING_COLLATIONS = auto()
    ASKING_SCHEDULE = auto()
    
    # Final steps
    ASKING_NOTES = auto()
    REVIEWING_DATA = auto()
    GENERATING_PLAN = auto()
    PLAN_READY = auto()


class Motor2States(Enum):
    """States for Motor 2 (Control/Adjustment) conversation flow."""
    
    # Patient verification
    VERIFYING_PATIENT = auto()
    PATIENT_NOT_FOUND = auto()
    
    # Current status
    ASKING_CURRENT_WEIGHT = auto()
    ASKING_PROGRESS = auto()
    ASKING_COMPLIANCE = auto()
    ASKING_DIFFICULTIES = auto()
    
    # Adjustments
    ASKING_OBJECTIVE_CHANGE = auto()
    ASKING_ACTIVITY_CHANGE = auto()
    ASKING_PREFERENCE_CHANGE = auto()
    ASKING_SPECIFIC_INSTRUCTIONS = auto()
    
    # Processing
    REVIEWING_CHANGES = auto()
    REGENERATING_PLAN = auto()
    ADJUSTMENT_READY = auto()


class Motor3States(Enum):
    """States for Motor 3 (Meal Replacement) conversation flow."""
    
    # Patient verification
    VERIFYING_PATIENT = auto()
    PATIENT_NOT_FOUND = auto()
    
    # Current plan selection
    SELECTING_PLAN = auto()
    PLAN_NOT_FOUND = auto()
    
    # Meal selection
    SELECTING_DAY = auto()
    SELECTING_MEAL = auto()
    SELECTING_MEAL_OPTION = auto()
    
    # Replacement request
    ASKING_REPLACEMENT_TYPE = auto()
    ASKING_REPLACEMENT_REASON = auto()
    ASKING_SPECIFIC_REQUEST = auto()
    ASKING_SPECIAL_CONDITIONS = auto()
    
    # Processing
    REVIEWING_REPLACEMENT = auto()
    GENERATING_REPLACEMENT = auto()
    REPLACEMENT_READY = auto()


class AdminStates(Enum):
    """States for admin operations."""
    
    ADMIN_MENU = auto()
    VIEWING_STATS = auto()
    MANAGING_USERS = auto()
    MAINTENANCE_MODE = auto()
    SENDING_BROADCAST = auto()
    VIEWING_LOGS = auto()
    

class ErrorStates(Enum):
    """Error handling states."""
    
    INPUT_ERROR = auto()
    VALIDATION_ERROR = auto()
    API_ERROR = auto()
    TIMEOUT_ERROR = auto()
    SYSTEM_ERROR = auto()
    RATE_LIMIT_ERROR = auto()


# State transition mappings
MOTOR1_FLOW = {
    ConversationState.MOTOR_SELECTION: Motor1States.ASKING_NAME,
    Motor1States.ASKING_NAME: Motor1States.ASKING_AGE,
    Motor1States.ASKING_AGE: Motor1States.ASKING_SEX,
    Motor1States.ASKING_SEX: Motor1States.ASKING_HEIGHT,
    Motor1States.ASKING_HEIGHT: Motor1States.ASKING_WEIGHT,
    Motor1States.ASKING_WEIGHT: Motor1States.ASKING_OBJECTIVE,
    Motor1States.ASKING_OBJECTIVE: Motor1States.ASKING_ACTIVITY_TYPE,
    Motor1States.ASKING_ACTIVITY_TYPE: Motor1States.ASKING_ACTIVITY_FREQUENCY,
    Motor1States.ASKING_ACTIVITY_FREQUENCY: Motor1States.ASKING_ACTIVITY_DURATION,
    Motor1States.ASKING_ACTIVITY_DURATION: Motor1States.ASKING_WEIGHT_TYPE,
    Motor1States.ASKING_WEIGHT_TYPE: Motor1States.ASKING_ECONOMIC_LEVEL,
    Motor1States.ASKING_ECONOMIC_LEVEL: Motor1States.ASKING_SUPPLEMENTS,
    Motor1States.ASKING_SUPPLEMENTS: Motor1States.ASKING_PATHOLOGIES,
    Motor1States.ASKING_PATHOLOGIES: Motor1States.ASKING_RESTRICTIONS,
    Motor1States.ASKING_RESTRICTIONS: Motor1States.ASKING_PREFERENCES,
    Motor1States.ASKING_PREFERENCES: Motor1States.ASKING_DISLIKES,
    Motor1States.ASKING_DISLIKES: Motor1States.ASKING_ALLERGIES,
    Motor1States.ASKING_ALLERGIES: Motor1States.ASKING_MAIN_MEALS,
    Motor1States.ASKING_MAIN_MEALS: Motor1States.ASKING_COLLATIONS,
    Motor1States.ASKING_COLLATIONS: Motor1States.ASKING_SCHEDULE,
    Motor1States.ASKING_SCHEDULE: Motor1States.ASKING_NOTES,
    Motor1States.ASKING_NOTES: Motor1States.REVIEWING_DATA,
    Motor1States.REVIEWING_DATA: Motor1States.GENERATING_PLAN,
    Motor1States.GENERATING_PLAN: Motor1States.PLAN_READY,
    Motor1States.PLAN_READY: ConversationState.ENDED
}

MOTOR2_FLOW = {
    ConversationState.MOTOR_SELECTION: Motor2States.VERIFYING_PATIENT,
    Motor2States.VERIFYING_PATIENT: Motor2States.ASKING_CURRENT_WEIGHT,
    Motor2States.ASKING_CURRENT_WEIGHT: Motor2States.ASKING_PROGRESS,
    Motor2States.ASKING_PROGRESS: Motor2States.ASKING_COMPLIANCE,
    Motor2States.ASKING_COMPLIANCE: Motor2States.ASKING_DIFFICULTIES,
    Motor2States.ASKING_DIFFICULTIES: Motor2States.ASKING_OBJECTIVE_CHANGE,
    Motor2States.ASKING_OBJECTIVE_CHANGE: Motor2States.ASKING_ACTIVITY_CHANGE,
    Motor2States.ASKING_ACTIVITY_CHANGE: Motor2States.ASKING_PREFERENCE_CHANGE,
    Motor2States.ASKING_PREFERENCE_CHANGE: Motor2States.ASKING_SPECIFIC_INSTRUCTIONS,
    Motor2States.ASKING_SPECIFIC_INSTRUCTIONS: Motor2States.REVIEWING_CHANGES,
    Motor2States.REVIEWING_CHANGES: Motor2States.REGENERATING_PLAN,
    Motor2States.REGENERATING_PLAN: Motor2States.ADJUSTMENT_READY,
    Motor2States.ADJUSTMENT_READY: ConversationState.ENDED
}

MOTOR3_FLOW = {
    ConversationState.MOTOR_SELECTION: Motor3States.VERIFYING_PATIENT,
    Motor3States.VERIFYING_PATIENT: Motor3States.SELECTING_PLAN,
    Motor3States.SELECTING_PLAN: Motor3States.SELECTING_DAY,
    Motor3States.SELECTING_DAY: Motor3States.SELECTING_MEAL,
    Motor3States.SELECTING_MEAL: Motor3States.SELECTING_MEAL_OPTION,
    Motor3States.SELECTING_MEAL_OPTION: Motor3States.ASKING_REPLACEMENT_TYPE,
    Motor3States.ASKING_REPLACEMENT_TYPE: Motor3States.ASKING_REPLACEMENT_REASON,
    Motor3States.ASKING_REPLACEMENT_REASON: Motor3States.ASKING_SPECIFIC_REQUEST,
    Motor3States.ASKING_SPECIFIC_REQUEST: Motor3States.ASKING_SPECIAL_CONDITIONS,
    Motor3States.ASKING_SPECIAL_CONDITIONS: Motor3States.REVIEWING_REPLACEMENT,
    Motor3States.REVIEWING_REPLACEMENT: Motor3States.GENERATING_REPLACEMENT,
    Motor3States.GENERATING_REPLACEMENT: Motor3States.REPLACEMENT_READY,
    Motor3States.REPLACEMENT_READY: ConversationState.ENDED
}

# Optional states that can be skipped
OPTIONAL_STATES = {
    Motor1States.ASKING_SUPPLEMENTS,
    Motor1States.ASKING_PATHOLOGIES,
    Motor1States.ASKING_RESTRICTIONS,
    Motor1States.ASKING_PREFERENCES,
    Motor1States.ASKING_DISLIKES,
    Motor1States.ASKING_ALLERGIES,
    Motor1States.ASKING_SCHEDULE,
    Motor1States.ASKING_NOTES,
    Motor2States.ASKING_DIFFICULTIES,
    Motor2States.ASKING_SPECIFIC_INSTRUCTIONS,
    Motor3States.ASKING_SPECIAL_CONDITIONS
}

# States that allow editing previous responses
EDITABLE_STATES = {
    Motor1States.REVIEWING_DATA,
    Motor2States.REVIEWING_CHANGES,
    Motor3States.REVIEWING_REPLACEMENT
}

# States that require user confirmation
CONFIRMATION_STATES = {
    Motor1States.REVIEWING_DATA,
    Motor1States.GENERATING_PLAN,
    Motor2States.REVIEWING_CHANGES,
    Motor2States.REGENERATING_PLAN,
    Motor3States.REVIEWING_REPLACEMENT,
    Motor3States.GENERATING_REPLACEMENT
}

# Terminal states (conversation ends)
TERMINAL_STATES = {
    ConversationState.ENDED,
    ConversationState.CANCELLED,
    ConversationState.ERROR,
    Motor1States.PLAN_READY,
    Motor2States.ADJUSTMENT_READY,
    Motor3States.REPLACEMENT_READY
}

# Error recovery states
ERROR_RECOVERY_STATES = {
    ErrorStates.INPUT_ERROR: "previous_state",
    ErrorStates.VALIDATION_ERROR: "previous_state",
    ErrorStates.API_ERROR: "retry_or_cancel",
    ErrorStates.TIMEOUT_ERROR: "restart_or_cancel",
    ErrorStates.SYSTEM_ERROR: "cancel",
    ErrorStates.RATE_LIMIT_ERROR: "wait_and_retry"
}


def get_next_state(current_state, motor_type: str = None):
    """Get the next state in the conversation flow."""
    if motor_type == "motor1":
        return MOTOR1_FLOW.get(current_state)
    elif motor_type == "motor2":
        return MOTOR2_FLOW.get(current_state)
    elif motor_type == "motor3":
        return MOTOR3_FLOW.get(current_state)
    else:
        return None


def is_terminal_state(state):
    """Check if a state is terminal (ends conversation)."""
    return state in TERMINAL_STATES


def is_optional_state(state):
    """Check if a state can be skipped."""
    return state in OPTIONAL_STATES


def is_editable_state(state):
    """Check if a state allows editing previous responses."""
    return state in EDITABLE_STATES


def requires_confirmation(state):
    """Check if a state requires user confirmation."""
    return state in CONFIRMATION_STATES


def get_error_recovery_action(error_state):
    """Get the recovery action for an error state."""
    return ERROR_RECOVERY_STATES.get(error_state, "cancel")


def get_motor_states(motor_type: str):
    """Get all states for a specific motor."""
    if motor_type == "motor1":
        return Motor1States
    elif motor_type == "motor2":
        return Motor2States
    elif motor_type == "motor3":
        return Motor3States
    else:
        return None


def get_state_description(state):
    """Get human-readable description of a state."""
    descriptions = {
        # Motor 1
        Motor1States.ASKING_NAME: "Solicitando nombre",
        Motor1States.ASKING_AGE: "Solicitando edad",
        Motor1States.ASKING_SEX: "Solicitando sexo",
        Motor1States.ASKING_HEIGHT: "Solicitando altura",
        Motor1States.ASKING_WEIGHT: "Solicitando peso",
        Motor1States.ASKING_OBJECTIVE: "Solicitando objetivo",
        Motor1States.ASKING_ACTIVITY_TYPE: "Solicitando tipo de actividad",
        Motor1States.ASKING_ACTIVITY_FREQUENCY: "Solicitando frecuencia",
        Motor1States.ASKING_ACTIVITY_DURATION: "Solicitando duración",
        Motor1States.ASKING_WEIGHT_TYPE: "Solicitando tipo de peso",
        Motor1States.ASKING_ECONOMIC_LEVEL: "Solicitando nivel económico",
        Motor1States.ASKING_SUPPLEMENTS: "Solicitando suplementos",
        Motor1States.ASKING_PATHOLOGIES: "Solicitando patologías",
        Motor1States.ASKING_RESTRICTIONS: "Solicitando restricciones",
        Motor1States.ASKING_PREFERENCES: "Solicitando preferencias",
        Motor1States.ASKING_DISLIKES: "Solicitando no gustos",
        Motor1States.ASKING_ALLERGIES: "Solicitando alergias",
        Motor1States.ASKING_MAIN_MEALS: "Solicitando comidas principales",
        Motor1States.ASKING_COLLATIONS: "Solicitando colaciones",
        Motor1States.ASKING_SCHEDULE: "Solicitando horarios",
        Motor1States.ASKING_NOTES: "Solicitando notas adicionales",
        Motor1States.REVIEWING_DATA: "Revisando datos",
        Motor1States.GENERATING_PLAN: "Generando plan",
        Motor1States.PLAN_READY: "Plan listo",
        
        # Motor 2
        Motor2States.VERIFYING_PATIENT: "Verificando paciente",
        Motor2States.ASKING_CURRENT_WEIGHT: "Solicitando peso actual",
        Motor2States.ASKING_PROGRESS: "Solicitando progreso",
        Motor2States.ASKING_COMPLIANCE: "Solicitando cumplimiento",
        Motor2States.ASKING_DIFFICULTIES: "Solicitando dificultades",
        Motor2States.ASKING_OBJECTIVE_CHANGE: "Solicitando cambio objetivo",
        Motor2States.ASKING_ACTIVITY_CHANGE: "Solicitando cambio actividad",
        Motor2States.ASKING_PREFERENCE_CHANGE: "Solicitando cambio preferencias",
        Motor2States.ASKING_SPECIFIC_INSTRUCTIONS: "Solicitando instrucciones",
        Motor2States.REVIEWING_CHANGES: "Revisando cambios",
        Motor2States.REGENERATING_PLAN: "Regenerando plan",
        Motor2States.ADJUSTMENT_READY: "Ajuste listo",
        
        # Motor 3
        Motor3States.VERIFYING_PATIENT: "Verificando paciente",
        Motor3States.SELECTING_PLAN: "Seleccionando plan",
        Motor3States.SELECTING_DAY: "Seleccionando día",
        Motor3States.SELECTING_MEAL: "Seleccionando comida",
        Motor3States.SELECTING_MEAL_OPTION: "Seleccionando opción",
        Motor3States.ASKING_REPLACEMENT_TYPE: "Solicitando tipo reemplazo",
        Motor3States.ASKING_REPLACEMENT_REASON: "Solicitando razón",
        Motor3States.ASKING_SPECIFIC_REQUEST: "Solicitando petición específica",
        Motor3States.ASKING_SPECIAL_CONDITIONS: "Solicitando condiciones especiales",
        Motor3States.REVIEWING_REPLACEMENT: "Revisando reemplazo",
        Motor3States.GENERATING_REPLACEMENT: "Generando reemplazo",
        Motor3States.REPLACEMENT_READY: "Reemplazo listo"
    }
    
    return descriptions.get(state, str(state))