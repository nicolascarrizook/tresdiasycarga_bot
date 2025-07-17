"""
Reply keyboard layouts for Sistema Mayra Telegram Bot.
"""
from typing import List, Optional
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from ..config import KEYBOARD_TEXTS


class ReplyKeyboardFactory:
    """Factory for creating reply keyboards."""
    
    @staticmethod
    def create_keyboard(buttons: List[List[str]], 
                       resize_keyboard: bool = True,
                       one_time_keyboard: bool = True,
                       selective: bool = False) -> ReplyKeyboardMarkup:
        """Create reply keyboard from button texts."""
        keyboard = []
        
        for row in buttons:
            keyboard_row = []
            for button_text in row:
                keyboard_row.append(KeyboardButton(button_text))
            keyboard.append(keyboard_row)
        
        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            selective=selective
        )
    
    @staticmethod
    def remove_keyboard(selective: bool = False) -> ReplyKeyboardRemove:
        """Remove reply keyboard."""
        return ReplyKeyboardRemove(selective=selective)


class BasicReplyKeyboard:
    """Basic reply keyboards."""
    
    @staticmethod
    def create_yes_no() -> ReplyKeyboardMarkup:
        """Create yes/no keyboard."""
        buttons = [
            [
                KEYBOARD_TEXTS["common"]["yes"],
                KEYBOARD_TEXTS["common"]["no"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_skip_cancel() -> ReplyKeyboardMarkup:
        """Create skip/cancel keyboard."""
        buttons = [
            [
                KEYBOARD_TEXTS["common"]["skip"],
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_back_cancel() -> ReplyKeyboardMarkup:
        """Create back/cancel keyboard."""
        buttons = [
            [
                KEYBOARD_TEXTS["common"]["back"],
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)


class ContactKeyboard:
    """Keyboard for contact sharing."""
    
    @staticmethod
    def create_contact_share() -> ReplyKeyboardMarkup:
        """Create contact sharing keyboard."""
        keyboard = [
            [
                KeyboardButton(
                    text="📱 Compartir Contacto",
                    request_contact=True
                )
            ],
            [
                KeyboardButton(text=KEYBOARD_TEXTS["common"]["skip"])
            ],
            [
                KeyboardButton(text=KEYBOARD_TEXTS["common"]["cancel"])
            ]
        ]
        
        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )


class LocationKeyboard:
    """Keyboard for location sharing."""
    
    @staticmethod
    def create_location_share() -> ReplyKeyboardMarkup:
        """Create location sharing keyboard."""
        keyboard = [
            [
                KeyboardButton(
                    text="📍 Compartir Ubicación",
                    request_location=True
                )
            ],
            [
                KeyboardButton(text=KEYBOARD_TEXTS["common"]["skip"])
            ],
            [
                KeyboardButton(text=KEYBOARD_TEXTS["common"]["cancel"])
            ]
        ]
        
        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )


class BooleanKeyboard:
    """Keyboard for boolean responses."""
    
    @staticmethod
    def create_boolean(
        true_text: str = None,
        false_text: str = None,
        add_skip: bool = False,
        add_cancel: bool = True
    ) -> ReplyKeyboardMarkup:
        """Create boolean keyboard."""
        
        true_text = true_text or KEYBOARD_TEXTS["common"]["yes"]
        false_text = false_text or KEYBOARD_TEXTS["common"]["no"]
        
        buttons = [
            [true_text, false_text]
        ]
        
        if add_skip:
            buttons.append([KEYBOARD_TEXTS["common"]["skip"]])
        
        if add_cancel:
            buttons.append([KEYBOARD_TEXTS["common"]["cancel"]])
        
        return ReplyKeyboardFactory.create_keyboard(buttons)


class NumericKeyboard:
    """Keyboard for numeric input."""
    
    @staticmethod
    def create_numeric_pad() -> ReplyKeyboardMarkup:
        """Create numeric pad keyboard."""
        buttons = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["0", ".", "⌫"],
            [
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_age_keyboard() -> ReplyKeyboardMarkup:
        """Create age input keyboard."""
        buttons = [
            ["18", "20", "25"],
            ["30", "35", "40"],
            ["45", "50", "55"],
            ["60", "65", "70"],
            [
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_weight_keyboard() -> ReplyKeyboardMarkup:
        """Create weight input keyboard."""
        buttons = [
            ["50", "55", "60"],
            ["65", "70", "75"],
            ["80", "85", "90"],
            ["95", "100", "105"],
            [
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_height_keyboard() -> ReplyKeyboardMarkup:
        """Create height input keyboard."""
        buttons = [
            ["150", "155", "160"],
            ["165", "170", "175"],
            ["180", "185", "190"],
            ["195", "200", "205"],
            [
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)


class QuickResponseKeyboard:
    """Keyboard for quick responses."""
    
    @staticmethod
    def create_objectives() -> ReplyKeyboardMarkup:
        """Create objectives keyboard."""
        buttons = [
            [
                "Mantenimiento",
                "Bajar 0.5kg"
            ],
            [
                "Bajar 1kg", 
                "Bajar 2kg"
            ],
            [
                "Subir 0.5kg",
                "Subir 1kg"
            ],
            [
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_activities() -> ReplyKeyboardMarkup:
        """Create activities keyboard."""
        buttons = [
            [
                "Sedentario",
                "Caminatas"
            ],
            [
                "Pesas",
                "Cardio"
            ],
            [
                "Mixto",
                "Deportista"
            ],
            [
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_frequencies() -> ReplyKeyboardMarkup:
        """Create frequencies keyboard."""
        buttons = [
            [
                "Nunca",
                "1 vez/semana"
            ],
            [
                "2 veces/semana",
                "3 veces/semana"
            ],
            [
                "4 veces/semana",
                "5 veces/semana"
            ],
            [
                "Diario"
            ],
            [
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_common_foods() -> ReplyKeyboardMarkup:
        """Create common foods keyboard."""
        buttons = [
            [
                "Pollo",
                "Carne"
            ],
            [
                "Pescado",
                "Huevos"
            ],
            [
                "Verduras",
                "Frutas"
            ],
            [
                "Arroz",
                "Pasta"
            ],
            [
                "Lácteos",
                "Legumbres"
            ],
            [
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_pathologies() -> ReplyKeyboardMarkup:
        """Create pathologies keyboard."""
        buttons = [
            [
                "Diabetes",
                "Hipertensión"
            ],
            [
                "Hipotiroidismo",
                "Hipertiroidismo"
            ],
            [
                "Colesterol alto",
                "Triglicéridos altos"
            ],
            [
                "Gastritis",
                "Colon irritable"
            ],
            [
                "Ninguna"
            ],
            [
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)


class ContextualKeyboard:
    """Contextual keyboards based on conversation state."""
    
    @staticmethod
    def create_for_state(state: str, context: dict = None) -> Optional[ReplyKeyboardMarkup]:
        """Create keyboard based on conversation state."""
        
        state_keyboards = {
            "ASKING_AGE": NumericKeyboard.create_age_keyboard(),
            "ASKING_WEIGHT": NumericKeyboard.create_weight_keyboard(),
            "ASKING_HEIGHT": NumericKeyboard.create_height_keyboard(),
            "ASKING_OBJECTIVE": QuickResponseKeyboard.create_objectives(),
            "ASKING_ACTIVITY_TYPE": QuickResponseKeyboard.create_activities(),
            "ASKING_ACTIVITY_FREQUENCY": QuickResponseKeyboard.create_frequencies(),
            "ASKING_PREFERENCES": QuickResponseKeyboard.create_common_foods(),
            "ASKING_DISLIKES": QuickResponseKeyboard.create_common_foods(),
            "ASKING_PATHOLOGIES": QuickResponseKeyboard.create_pathologies(),
        }
        
        return state_keyboards.get(state)
    
    @staticmethod
    def create_motor_specific(motor_type: str) -> Optional[ReplyKeyboardMarkup]:
        """Create keyboard specific to motor type."""
        
        if motor_type == "motor1":
            return BasicReplyKeyboard.create_skip_cancel()
        elif motor_type == "motor2":
            return BasicReplyKeyboard.create_yes_no()
        elif motor_type == "motor3":
            return BasicReplyKeyboard.create_back_cancel()
        
        return None


class InputHelpKeyboard:
    """Keyboard for input help and suggestions."""
    
    @staticmethod
    def create_text_input_help() -> ReplyKeyboardMarkup:
        """Create text input help keyboard."""
        buttons = [
            [
                "💡 Ayuda",
                "📝 Ejemplo"
            ],
            [
                KEYBOARD_TEXTS["common"]["skip"],
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_list_input_help() -> ReplyKeyboardMarkup:
        """Create list input help keyboard."""
        buttons = [
            [
                "➕ Agregar",
                "✅ Terminar"
            ],
            [
                "💡 Ayuda",
                "🗑️ Borrar todo"
            ],
            [
                KEYBOARD_TEXTS["common"]["cancel"]
            ]
        ]
        
        return ReplyKeyboardFactory.create_keyboard(buttons)