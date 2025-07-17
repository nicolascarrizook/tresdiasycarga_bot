"""
Inline keyboard layouts for Sistema Mayra Telegram Bot.
"""
from typing import List, Dict, Any, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ..config import KEYBOARD_TEXTS
from ..states.conversation_states import Motor1States, Motor2States, Motor3States


class InlineKeyboardFactory:
    """Factory for creating inline keyboards."""
    
    @staticmethod
    def create_keyboard(buttons: List[List[Dict[str, str]]], 
                       add_cancel: bool = True) -> InlineKeyboardMarkup:
        """Create inline keyboard from button configuration."""
        keyboard = []
        
        for row in buttons:
            keyboard_row = []
            for button in row:
                keyboard_row.append(
                    InlineKeyboardButton(
                        text=button["text"],
                        callback_data=button["callback_data"]
                    )
                )
            keyboard.append(keyboard_row)
        
        if add_cancel:
            keyboard.append([
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["cancel"],
                    callback_data="cancel"
                )
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_single_column(items: List[Dict[str, str]], 
                           add_cancel: bool = True) -> InlineKeyboardMarkup:
        """Create single column keyboard."""
        buttons = [[item] for item in items]
        return InlineKeyboardFactory.create_keyboard(buttons, add_cancel)
    
    @staticmethod
    def create_two_columns(items: List[Dict[str, str]], 
                          add_cancel: bool = True) -> InlineKeyboardMarkup:
        """Create two-column keyboard."""
        buttons = []
        for i in range(0, len(items), 2):
            row = items[i:i+2]
            buttons.append(row)
        
        return InlineKeyboardFactory.create_keyboard(buttons, add_cancel)


class MotorSelectionKeyboard:
    """Keyboard for selecting motor type."""
    
    @staticmethod
    def create() -> InlineKeyboardMarkup:
        """Create motor selection keyboard."""
        buttons = [
            [
                {
                    "text": KEYBOARD_TEXTS["motors"]["new_patient"],
                    "callback_data": "motor_1"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["motors"]["control"],
                    "callback_data": "motor_2"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["motors"]["replacement"],
                    "callback_data": "motor_3"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons, add_cancel=False)


class ConfirmationKeyboard:
    """Keyboard for confirmations."""
    
    @staticmethod
    def create(confirm_data: str = "confirm", 
               cancel_data: str = "cancel") -> InlineKeyboardMarkup:
        """Create confirmation keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["yes"],
                    callback_data=confirm_data
                ),
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["no"],
                    callback_data=cancel_data
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_with_edit(confirm_data: str = "confirm",
                        edit_data: str = "edit",
                        cancel_data: str = "cancel") -> InlineKeyboardMarkup:
        """Create confirmation keyboard with edit option."""
        keyboard = [
            [
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["confirm"],
                    callback_data=confirm_data
                ),
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["edit"],
                    callback_data=edit_data
                )
            ],
            [
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["cancel"],
                    callback_data=cancel_data
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)


class NavigationKeyboard:
    """Keyboard for navigation."""
    
    @staticmethod
    def create(back_data: str = "back",
               skip_data: str = "skip",
               cancel_data: str = "cancel",
               show_skip: bool = False) -> InlineKeyboardMarkup:
        """Create navigation keyboard."""
        keyboard = []
        
        row = []
        if back_data:
            row.append(
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["back"],
                    callback_data=back_data
                )
            )
        
        if show_skip and skip_data:
            row.append(
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["skip"],
                    callback_data=skip_data
                )
            )
        
        if row:
            keyboard.append(row)
        
        if cancel_data:
            keyboard.append([
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["cancel"],
                    callback_data=cancel_data
                )
            ])
        
        return InlineKeyboardMarkup(keyboard)


class DataSelectionKeyboard:
    """Keyboard for data selection."""
    
    @staticmethod
    def create_objective_keyboard() -> InlineKeyboardMarkup:
        """Create objective selection keyboard."""
        buttons = [
            [
                {
                    "text": KEYBOARD_TEXTS["objectives"]["maintenance"],
                    "callback_data": "obj_maintenance"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["objectives"]["lose_half_kg"],
                    "callback_data": "obj_lose_half_kg"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["objectives"]["lose_one_kg"],
                    "callback_data": "obj_lose_one_kg"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["objectives"]["lose_two_kg"],
                    "callback_data": "obj_lose_two_kg"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["objectives"]["gain_half_kg"],
                    "callback_data": "obj_gain_half_kg"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["objectives"]["gain_one_kg"],
                    "callback_data": "obj_gain_one_kg"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_activity_keyboard() -> InlineKeyboardMarkup:
        """Create activity type selection keyboard."""
        buttons = [
            [
                {
                    "text": KEYBOARD_TEXTS["activities"]["sedentary"],
                    "callback_data": "act_sedentary"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["activities"]["walking"],
                    "callback_data": "act_walking"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["activities"]["weights"],
                    "callback_data": "act_weights"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["activities"]["cardio"],
                    "callback_data": "act_cardio"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["activities"]["mixed"],
                    "callback_data": "act_mixed"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["activities"]["athlete"],
                    "callback_data": "act_athlete"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_frequency_keyboard() -> InlineKeyboardMarkup:
        """Create frequency selection keyboard."""
        buttons = [
            [
                {
                    "text": KEYBOARD_TEXTS["frequencies"]["never"],
                    "callback_data": "freq_never"
                },
                {
                    "text": KEYBOARD_TEXTS["frequencies"]["once_week"],
                    "callback_data": "freq_once_week"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["frequencies"]["twice_week"],
                    "callback_data": "freq_twice_week"
                },
                {
                    "text": KEYBOARD_TEXTS["frequencies"]["three_times_week"],
                    "callback_data": "freq_three_times_week"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["frequencies"]["four_times_week"],
                    "callback_data": "freq_four_times_week"
                },
                {
                    "text": KEYBOARD_TEXTS["frequencies"]["five_times_week"],
                    "callback_data": "freq_five_times_week"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["frequencies"]["daily"],
                    "callback_data": "freq_daily"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_sex_keyboard() -> InlineKeyboardMarkup:
        """Create sex selection keyboard."""
        buttons = [
            [
                {
                    "text": KEYBOARD_TEXTS["sex"]["M"],
                    "callback_data": "sex_M"
                },
                {
                    "text": KEYBOARD_TEXTS["sex"]["F"],
                    "callback_data": "sex_F"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_weight_type_keyboard() -> InlineKeyboardMarkup:
        """Create weight type selection keyboard."""
        buttons = [
            [
                {
                    "text": KEYBOARD_TEXTS["weight_types"]["raw"],
                    "callback_data": "weight_raw"
                },
                {
                    "text": KEYBOARD_TEXTS["weight_types"]["cooked"],
                    "callback_data": "weight_cooked"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_economic_level_keyboard() -> InlineKeyboardMarkup:
        """Create economic level selection keyboard."""
        buttons = [
            [
                {
                    "text": KEYBOARD_TEXTS["economic_levels"]["low"],
                    "callback_data": "econ_low"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["economic_levels"]["medium"],
                    "callback_data": "econ_medium"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["economic_levels"]["high"],
                    "callback_data": "econ_high"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_supplements_keyboard() -> InlineKeyboardMarkup:
        """Create supplements selection keyboard."""
        buttons = [
            [
                {
                    "text": "🥤 Proteína Whey",
                    "callback_data": "supp_whey_protein"
                },
                {
                    "text": "💪 Creatina",
                    "callback_data": "supp_creatine"
                }
            ],
            [
                {
                    "text": "💊 Multivitamínico",
                    "callback_data": "supp_multivitamin"
                },
                {
                    "text": "🐟 Omega 3",
                    "callback_data": "supp_omega_3"
                }
            ],
            [
                {
                    "text": "🦴 Magnesio",
                    "callback_data": "supp_magnesium"
                },
                {
                    "text": "☀️ Vitamina D",
                    "callback_data": "supp_vitamin_d"
                }
            ],
            [
                {
                    "text": "🏃 BCAA",
                    "callback_data": "supp_bcaa"
                }
            ],
            [
                {
                    "text": "❌ Ninguno",
                    "callback_data": "supp_none"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_restrictions_keyboard() -> InlineKeyboardMarkup:
        """Create dietary restrictions keyboard."""
        buttons = [
            [
                {
                    "text": "🥬 Vegetariano",
                    "callback_data": "rest_vegetarian"
                },
                {
                    "text": "🌱 Vegano",
                    "callback_data": "rest_vegan"
                }
            ],
            [
                {
                    "text": "🌾 Sin Gluten",
                    "callback_data": "rest_gluten_free"
                },
                {
                    "text": "🥛 Sin Lactosa",
                    "callback_data": "rest_lactose_free"
                }
            ],
            [
                {
                    "text": "🩺 Diabético",
                    "callback_data": "rest_diabetic"
                },
                {
                    "text": "💓 Hipertensión",
                    "callback_data": "rest_hypertension"
                }
            ],
            [
                {
                    "text": "🫘 Renal",
                    "callback_data": "rest_renal"
                },
                {
                    "text": "❤️ Cardíaco",
                    "callback_data": "rest_cardiac"
                }
            ],
            [
                {
                    "text": "❌ Ninguna",
                    "callback_data": "rest_none"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_number_keyboard(min_val: int, max_val: int, 
                              prefix: str = "num") -> InlineKeyboardMarkup:
        """Create number selection keyboard."""
        buttons = []
        
        for i in range(min_val, max_val + 1):
            buttons.append([
                {
                    "text": str(i),
                    "callback_data": f"{prefix}_{i}"
                }
            ])
        
        return InlineKeyboardFactory.create_keyboard(buttons)


class PlanSelectionKeyboard:
    """Keyboard for plan selection."""
    
    @staticmethod
    def create_plan_list(plans: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Create plan list keyboard."""
        buttons = []
        
        for plan in plans:
            buttons.append([
                {
                    "text": f"📋 Plan {plan['created_at']} - {plan['plan_type']}",
                    "callback_data": f"select_plan_{plan['id']}"
                }
            ])
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_day_selection() -> InlineKeyboardMarkup:
        """Create day selection keyboard."""
        buttons = [
            [
                {
                    "text": KEYBOARD_TEXTS["days"]["day_1"],
                    "callback_data": "day_1"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["days"]["day_2"],
                    "callback_data": "day_2"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["days"]["day_3"],
                    "callback_data": "day_3"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)


class MealSelectionKeyboard:
    """Keyboard for meal selection."""
    
    @staticmethod
    def create_meal_type_selection() -> InlineKeyboardMarkup:
        """Create meal type selection keyboard."""
        buttons = [
            [
                {
                    "text": KEYBOARD_TEXTS["meal_types"]["breakfast"],
                    "callback_data": "meal_breakfast"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["meal_types"]["lunch"],
                    "callback_data": "meal_lunch"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["meal_types"]["snack"],
                    "callback_data": "meal_snack"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["meal_types"]["dinner"],
                    "callback_data": "meal_dinner"
                }
            ],
            [
                {
                    "text": KEYBOARD_TEXTS["meal_types"]["collation"],
                    "callback_data": "meal_collation"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_meal_options(meal_options: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Create meal options keyboard."""
        buttons = []
        
        for i, option in enumerate(meal_options, 1):
            buttons.append([
                {
                    "text": f"🍽️ Opción {i}: {option['name']}",
                    "callback_data": f"meal_option_{i}"
                }
            ])
        
        return InlineKeyboardFactory.create_keyboard(buttons)
    
    @staticmethod
    def create_replacement_type_keyboard() -> InlineKeyboardMarkup:
        """Create replacement type keyboard."""
        buttons = [
            [
                {
                    "text": "🔄 Reemplazo Equivalente",
                    "callback_data": "repl_equivalent"
                }
            ],
            [
                {
                    "text": "🍽️ Comida Específica",
                    "callback_data": "repl_specific"
                }
            ],
            [
                {
                    "text": "❌ No me gusta",
                    "callback_data": "repl_dislike"
                }
            ],
            [
                {
                    "text": "🚫 Alergia/Intolerancia",
                    "callback_data": "repl_allergy"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)


class AdminKeyboard:
    """Keyboard for admin operations."""
    
    @staticmethod
    def create_admin_menu() -> InlineKeyboardMarkup:
        """Create admin menu keyboard."""
        buttons = [
            [
                {
                    "text": "📊 Estadísticas",
                    "callback_data": "admin_stats"
                },
                {
                    "text": "👥 Usuarios",
                    "callback_data": "admin_users"
                }
            ],
            [
                {
                    "text": "🔧 Mantenimiento",
                    "callback_data": "admin_maintenance"
                },
                {
                    "text": "📢 Broadcast",
                    "callback_data": "admin_broadcast"
                }
            ],
            [
                {
                    "text": "📝 Logs",
                    "callback_data": "admin_logs"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons, add_cancel=False)
    
    @staticmethod
    def create_user_management(user_id: int) -> InlineKeyboardMarkup:
        """Create user management keyboard."""
        buttons = [
            [
                {
                    "text": "🔍 Ver Información",
                    "callback_data": f"admin_user_info_{user_id}"
                }
            ],
            [
                {
                    "text": "🚫 Bloquear",
                    "callback_data": f"admin_user_block_{user_id}"
                },
                {
                    "text": "✅ Desbloquear",
                    "callback_data": f"admin_user_unblock_{user_id}"
                }
            ],
            [
                {
                    "text": "🗑️ Eliminar Datos",
                    "callback_data": f"admin_user_delete_{user_id}"
                }
            ]
        ]
        
        return InlineKeyboardFactory.create_keyboard(buttons)


class EditKeyboard:
    """Keyboard for editing data."""
    
    @staticmethod
    def create_edit_menu(fields: List[str]) -> InlineKeyboardMarkup:
        """Create edit menu keyboard."""
        buttons = []
        
        field_names = {
            "name": "👤 Nombre",
            "age": "📅 Edad",
            "sex": "⚤ Sexo",
            "height": "📏 Altura",
            "weight": "⚖️ Peso",
            "objective": "🎯 Objetivo",
            "activity_type": "🏃 Actividad",
            "frequency": "📊 Frecuencia",
            "duration": "⏱️ Duración",
            "peso_tipo": "🥩 Tipo de Peso",
            "economic_level": "💰 Nivel Económico",
            "supplements": "💊 Suplementos",
            "pathologies": "🩺 Patologías",
            "restrictions": "🚫 Restricciones",
            "preferences": "❤️ Preferencias",
            "dislikes": "❌ No me gusta",
            "allergies": "🤧 Alergias",
            "main_meals": "🍽️ Comidas Principales",
            "collations": "🥨 Colaciones",
            "notes": "📝 Notas"
        }
        
        for field in fields:
            if field in field_names:
                buttons.append([
                    {
                        "text": field_names[field],
                        "callback_data": f"edit_{field}"
                    }
                ])
        
        return InlineKeyboardFactory.create_keyboard(buttons)


class SkipKeyboard:
    """Keyboard for skipping optional fields."""
    
    @staticmethod
    def create(skip_callback: str = "skip") -> InlineKeyboardMarkup:
        """Create skip keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["skip"],
                    callback_data=skip_callback
                )
            ],
            [
                InlineKeyboardButton(
                    text=KEYBOARD_TEXTS["common"]["cancel"],
                    callback_data="cancel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)