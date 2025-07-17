"""
State management for Sistema Mayra Telegram Bot conversations.
"""

from .conversation_states import (
    ConversationState,
    Motor1States,
    Motor2States,
    Motor3States,
    CommonStates
)

from .user_data import (
    UserData,
    PatientData,
    ConversationData,
    PlanData,
    ReplacementData
)

from .state_manager import (
    StateManager,
    ConversationManager,
    UserDataManager
)

__all__ = [
    # States
    "ConversationState",
    "Motor1States", 
    "Motor2States",
    "Motor3States",
    "CommonStates",
    
    # Data models
    "UserData",
    "PatientData", 
    "ConversationData",
    "PlanData",
    "ReplacementData",
    
    # Managers
    "StateManager",
    "ConversationManager",
    "UserDataManager"
]