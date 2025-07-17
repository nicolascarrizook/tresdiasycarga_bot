#!/usr/bin/env python3
"""
Main application for Sistema Mayra Telegram Bot.
"""
import asyncio
import logging
import sys
import signal
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
    PersistenceInput,
    PicklePersistence
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set httpx logging to WARNING to reduce noise
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Import bot components
from .config import bot_settings, BOT_CONFIG, FEATURE_FLAGS
from .states import (
    ConversationManager, 
    UserDataManager, 
    StateManager,
    ConversationState,
    Motor1States,
    Motor2States,
    Motor3States
)
from .locales import get_message, get_time_greeting
from .keyboards import (
    MotorSelectionKeyboard,
    DataSelectionKeyboard,
    ConfirmationKeyboard,
    NavigationKeyboard
)
from .services import get_api_service, test_api_connection, warmup_api_connections


class SistemaMayraBot:
    """Main bot application class."""
    
    def __init__(self):
        """Initialize bot application."""
        self.application = None
        self.conversation_manager = ConversationManager()
        self.user_manager = UserDataManager()
        self.state_manager = StateManager()
        self.is_running = False
        self.start_time = datetime.now()
        
        # Statistics
        self.total_messages = 0
        self.total_commands = 0
        self.total_errors = 0
        
        logger.info("Sistema Mayra Bot initialized")
    
    async def initialize(self):
        """Initialize bot application."""
        try:
            # Test API connection
            if not await test_api_connection():
                logger.error("API connection test failed")
                return False
            
            # Warm up API connections
            await warmup_api_connections()
            
            # Create persistence
            persistence = self._create_persistence()
            
            # Create application
            self.application = (
                Application.builder()
                .token(bot_settings.bot_token)
                .persistence(persistence)
                .build()
            )
            
            # Setup handlers
            self._setup_handlers()
            
            # Setup error handling
            self.application.add_error_handler(self._error_handler)
            
            logger.info("Bot application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False
    
    def _create_persistence(self):
        """Create persistence for conversation data."""
        if BOT_CONFIG["persistence"]["enabled"]:
            persistence_file = Path("bot_persistence.pkl")
            return PicklePersistence(
                filepath=persistence_file,
                store_user_data=BOT_CONFIG["persistence"]["store_user_data"],
                store_chat_data=BOT_CONFIG["persistence"]["store_chat_data"],
                store_bot_data=BOT_CONFIG["persistence"]["store_bot_data"]
            )
        return None
    
    def _setup_handlers(self):
        """Setup bot handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self._start_handler))
        self.application.add_handler(CommandHandler("help", self._help_handler))
        self.application.add_handler(CommandHandler("cancel", self._cancel_handler))
        self.application.add_handler(CommandHandler("mi_info", self._user_info_handler))
        self.application.add_handler(CommandHandler("historial", self._history_handler))
        
        # Admin handlers
        if FEATURE_FLAGS["admin_commands"]:
            self.application.add_handler(CommandHandler("admin", self._admin_handler))
        
        # Main conversation handler
        conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", self._start_handler),
                CallbackQueryHandler(self._motor_selection_handler, pattern="^motor_")
            ],
            states={
                # Motor selection
                ConversationState.MOTOR_SELECTION: [
                    CallbackQueryHandler(self._motor_selection_handler, pattern="^motor_")
                ],
                
                # Motor 1 states (New Patient)
                Motor1States.ASKING_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_name_handler)
                ],
                Motor1States.ASKING_AGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_age_handler)
                ],
                Motor1States.ASKING_SEX: [
                    CallbackQueryHandler(self._motor1_sex_handler, pattern="^sex_")
                ],
                Motor1States.ASKING_HEIGHT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_height_handler)
                ],
                Motor1States.ASKING_WEIGHT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_weight_handler)
                ],
                Motor1States.ASKING_OBJECTIVE: [
                    CallbackQueryHandler(self._motor1_objective_handler, pattern="^obj_")
                ],
                Motor1States.ASKING_ACTIVITY_TYPE: [
                    CallbackQueryHandler(self._motor1_activity_handler, pattern="^act_")
                ],
                Motor1States.ASKING_ACTIVITY_FREQUENCY: [
                    CallbackQueryHandler(self._motor1_frequency_handler, pattern="^freq_")
                ],
                Motor1States.ASKING_ACTIVITY_DURATION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_duration_handler)
                ],
                Motor1States.ASKING_WEIGHT_TYPE: [
                    CallbackQueryHandler(self._motor1_weight_type_handler, pattern="^weight_")
                ],
                Motor1States.ASKING_ECONOMIC_LEVEL: [
                    CallbackQueryHandler(self._motor1_economic_handler, pattern="^econ_")
                ],
                Motor1States.ASKING_SUPPLEMENTS: [
                    CallbackQueryHandler(self._motor1_supplements_handler, pattern="^supp_")
                ],
                Motor1States.ASKING_PATHOLOGIES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_pathologies_handler)
                ],
                Motor1States.ASKING_RESTRICTIONS: [
                    CallbackQueryHandler(self._motor1_restrictions_handler, pattern="^rest_")
                ],
                Motor1States.ASKING_PREFERENCES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_preferences_handler)
                ],
                Motor1States.ASKING_DISLIKES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_dislikes_handler)
                ],
                Motor1States.ASKING_ALLERGIES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_allergies_handler)
                ],
                Motor1States.ASKING_MAIN_MEALS: [
                    CallbackQueryHandler(self._motor1_main_meals_handler, pattern="^num_")
                ],
                Motor1States.ASKING_COLLATIONS: [
                    CallbackQueryHandler(self._motor1_collations_handler, pattern="^num_")
                ],
                Motor1States.ASKING_SCHEDULE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_schedule_handler)
                ],
                Motor1States.ASKING_NOTES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor1_notes_handler)
                ],
                Motor1States.REVIEWING_DATA: [
                    CallbackQueryHandler(self._motor1_review_handler, pattern="^(confirm|edit)$")
                ],
                Motor1States.GENERATING_PLAN: [
                    CallbackQueryHandler(self._motor1_generate_handler, pattern="^confirm$")
                ],
                
                # Motor 2 states (Control/Adjustment)
                Motor2States.VERIFYING_PATIENT: [
                    CallbackQueryHandler(self._motor2_verify_handler, pattern="^continue$")
                ],
                Motor2States.ASKING_CURRENT_WEIGHT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor2_weight_handler)
                ],
                Motor2States.ASKING_PROGRESS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor2_progress_handler)
                ],
                Motor2States.ASKING_COMPLIANCE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor2_compliance_handler)
                ],
                Motor2States.ASKING_DIFFICULTIES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor2_difficulties_handler)
                ],
                Motor2States.ASKING_OBJECTIVE_CHANGE: [
                    CallbackQueryHandler(self._motor2_objective_handler, pattern="^obj_")
                ],
                Motor2States.ASKING_ACTIVITY_CHANGE: [
                    CallbackQueryHandler(self._motor2_activity_handler, pattern="^act_")
                ],
                Motor2States.ASKING_PREFERENCE_CHANGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor2_preferences_handler)
                ],
                Motor2States.ASKING_SPECIFIC_INSTRUCTIONS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor2_instructions_handler)
                ],
                Motor2States.REVIEWING_CHANGES: [
                    CallbackQueryHandler(self._motor2_review_handler, pattern="^(confirm|edit)$")
                ],
                Motor2States.REGENERATING_PLAN: [
                    CallbackQueryHandler(self._motor2_regenerate_handler, pattern="^confirm$")
                ],
                
                # Motor 3 states (Meal Replacement)
                Motor3States.VERIFYING_PATIENT: [
                    CallbackQueryHandler(self._motor3_verify_handler, pattern="^continue$")
                ],
                Motor3States.SELECTING_PLAN: [
                    CallbackQueryHandler(self._motor3_plan_handler, pattern="^select_plan_")
                ],
                Motor3States.SELECTING_DAY: [
                    CallbackQueryHandler(self._motor3_day_handler, pattern="^day_")
                ],
                Motor3States.SELECTING_MEAL: [
                    CallbackQueryHandler(self._motor3_meal_handler, pattern="^meal_")
                ],
                Motor3States.SELECTING_MEAL_OPTION: [
                    CallbackQueryHandler(self._motor3_option_handler, pattern="^meal_option_")
                ],
                Motor3States.ASKING_REPLACEMENT_TYPE: [
                    CallbackQueryHandler(self._motor3_type_handler, pattern="^repl_")
                ],
                Motor3States.ASKING_REPLACEMENT_REASON: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor3_reason_handler)
                ],
                Motor3States.ASKING_SPECIFIC_REQUEST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor3_request_handler)
                ],
                Motor3States.ASKING_SPECIAL_CONDITIONS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._motor3_conditions_handler)
                ],
                Motor3States.REVIEWING_REPLACEMENT: [
                    CallbackQueryHandler(self._motor3_review_handler, pattern="^(confirm|edit)$")
                ],
                Motor3States.GENERATING_REPLACEMENT: [
                    CallbackQueryHandler(self._motor3_generate_handler, pattern="^confirm$")
                ],
            },
            fallbacks=[
                CommandHandler("cancel", self._cancel_handler),
                CallbackQueryHandler(self._cancel_handler, pattern="^cancel$"),
                MessageHandler(filters.COMMAND, self._unknown_command_handler)
            ],
            per_user=True,
            per_chat=True,
            conversation_timeout=bot_settings.conversation_timeout,
            name="main_conversation"
        )
        
        self.application.add_handler(conversation_handler)
        
        # Fallback handlers
        self.application.add_handler(MessageHandler(filters.TEXT, self._fallback_handler))
        self.application.add_handler(MessageHandler(filters.COMMAND, self._unknown_command_handler))
        self.application.add_handler(CallbackQueryHandler(self._unknown_callback_handler))
    
    # Command handlers
    async def _start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        
        # Update user data
        await self._update_user_data(user)
        
        # Send welcome message
        greeting = get_time_greeting()
        message = get_message("welcome", name=user.first_name)
        
        await update.message.reply_text(
            f"{greeting}\n\n{message}",
            reply_markup=MotorSelectionKeyboard.create(),
            parse_mode="HTML"
        )
        
        # Log command
        self.total_commands += 1
        logger.info(f"User {user.id} started bot")
        
        return ConversationState.MOTOR_SELECTION
    
    async def _help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        message = get_message("help_message")
        
        await update.message.reply_text(
            message,
            parse_mode="HTML"
        )
        
        self.total_commands += 1
        logger.info(f"User {update.effective_user.id} requested help")
    
    async def _cancel_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command."""
        user_id = update.effective_user.id
        
        # End conversation
        self.conversation_manager.end_conversation(user_id)
        
        message = get_message("cancel_conversation")
        
        if update.message:
            await update.message.reply_text(message, parse_mode="HTML")
        elif update.callback_query:
            await update.callback_query.message.reply_text(message, parse_mode="HTML")
        
        self.total_commands += 1
        logger.info(f"User {user_id} cancelled conversation")
        
        return ConversationHandler.END
    
    async def _user_info_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mi_info command."""
        user_id = update.effective_user.id
        
        # Get user data
        user_data = self.user_manager.get_user_data(user_id)
        
        if user_data:
            message = get_message("user_info",
                name=user_data.first_name,
                total_plans=user_data.total_plans_generated,
                last_plan="No disponible",
                member_since=user_data.created_at.strftime("%d/%m/%Y"),
                language=user_data.language_code,
                notifications="Activadas" if user_data.notification_enabled else "Desactivadas"
            )
        else:
            message = "No se encontró información de usuario."
        
        await update.message.reply_text(message, parse_mode="HTML")
        
        self.total_commands += 1
    
    async def _history_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /historial command."""
        user_id = update.effective_user.id
        
        # Get user plans from API
        api_service = await get_api_service()
        response = await api_service.get_patient_plans(user_id)
        
        if response.success and response.data:
            plans = response.data
            message = get_message("user_history",
                plan_history="\n".join([f"" {plan.get('date', 'N/A')} - {plan.get('type', 'N/A')}" for plan in plans]),
                total_plans=len(plans),
                total_replacements=0,  # TODO: Get from API
                total_controls=0  # TODO: Get from API
            )
        else:
            message = "No se encontraron planes en tu historial."
        
        await update.message.reply_text(message, parse_mode="HTML")
        
        self.total_commands += 1
    
    async def _admin_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command."""
        user_id = update.effective_user.id
        
        # Check admin permissions
        if not self.user_manager.is_user_admin(user_id):
            await update.message.reply_text("=« No tienes permisos de administrador.")
            return
        
        # Show admin menu
        from .keyboards import AdminKeyboard
        
        await update.message.reply_text(
            get_message("admin_menu"),
            reply_markup=AdminKeyboard.create_admin_menu(),
            parse_mode="HTML"
        )
        
        self.total_commands += 1
    
    # Motor selection handler
    async def _motor_selection_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle motor selection."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        motor_type = query.data
        
        # Create new conversation
        conversation = self.conversation_manager.create_conversation(user_id, motor_type)
        
        if motor_type == "motor_1":
            # Start Motor 1 flow
            message = get_message("motor1_name")
            await query.message.reply_text(message, parse_mode="HTML")
            return Motor1States.ASKING_NAME
            
        elif motor_type == "motor_2":
            # Start Motor 2 flow
            message = get_message("motor2_verify_patient")
            await query.message.reply_text(message, parse_mode="HTML")
            
            # Check if patient exists
            api_service = await get_api_service()
            response = await api_service.get_patient(user_id)
            
            if response.success and response.data:
                patient = response.data
                message = get_message("motor2_patient_found",
                    last_plan_date="Fecha no disponible",
                    objective=patient.get('objective', 'No disponible'),
                    weight=patient.get('weight', 'No disponible')
                )
                keyboard = ConfirmationKeyboard.create("continue", "cancel")
                await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
                return Motor2States.VERIFYING_PATIENT
            else:
                message = get_message("motor2_patient_not_found")
                keyboard = ConfirmationKeyboard.create("motor_1", "cancel")
                await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
                return Motor2States.PATIENT_NOT_FOUND
                
        elif motor_type == "motor_3":
            # Start Motor 3 flow
            message = get_message("motor3_verify_patient")
            await query.message.reply_text(message, parse_mode="HTML")
            
            # Check if patient exists and has plans
            api_service = await get_api_service()
            response = await api_service.get_patient(user_id)
            
            if response.success and response.data:
                patient = response.data
                plans_response = await api_service.get_patient_plans(patient['id'])
                
                if plans_response.success and plans_response.data:
                    message = get_message("motor3_patient_found",
                        plan_date="Fecha no disponible",
                        plan_type="Tipo no disponible"
                    )
                    keyboard = ConfirmationKeyboard.create("continue", "cancel")
                    await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
                    return Motor3States.VERIFYING_PATIENT
                else:
                    message = "No se encontraron planes activos. Necesitas generar un plan primero."
                    keyboard = ConfirmationKeyboard.create("motor_1", "cancel")
                    await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
                    return Motor3States.PLAN_NOT_FOUND
            else:
                message = get_message("motor3_patient_not_found")
                keyboard = ConfirmationKeyboard.create("motor_1", "cancel")
                await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
                return Motor3States.PATIENT_NOT_FOUND
    
    # Motor 1 handlers (New Patient)
    async def _motor1_name_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle name input for Motor 1."""
        user_id = update.effective_user.id
        name = update.message.text.strip()
        
        # Validate name
        if not self._validate_name(name):
            await update.message.reply_text(get_message("validation_name"), parse_mode="HTML")
            return Motor1States.ASKING_NAME
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "name", name)
        
        # Next step
        message = get_message("motor1_age", name=name)
        await update.message.reply_text(message, parse_mode="HTML")
        
        return Motor1States.ASKING_AGE
    
    async def _motor1_age_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle age input for Motor 1."""
        user_id = update.effective_user.id
        age_text = update.message.text.strip()
        
        # Validate age
        try:
            age = int(age_text)
            if not (16 <= age <= 80):
                raise ValueError("Age out of range")
        except ValueError:
            await update.message.reply_text(get_message("validation_age"), parse_mode="HTML")
            return Motor1States.ASKING_AGE
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "age", age)
        
        # Next step
        message = get_message("motor1_sex")
        keyboard = DataSelectionKeyboard.create_sex_keyboard()
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_SEX
    
    async def _motor1_sex_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle sex selection for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        sex = query.data.replace("sex_", "")
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "sex", sex)
        
        # Next step
        message = get_message("motor1_height")
        await query.message.reply_text(message, parse_mode="HTML")
        
        return Motor1States.ASKING_HEIGHT
    
    async def _motor1_height_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle height input for Motor 1."""
        user_id = update.effective_user.id
        height_text = update.message.text.strip()
        
        # Validate height
        try:
            height = float(height_text)
            if not (140 <= height <= 220):
                raise ValueError("Height out of range")
        except ValueError:
            await update.message.reply_text(get_message("validation_height"), parse_mode="HTML")
            return Motor1States.ASKING_HEIGHT
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "height", height)
        
        # Next step
        message = get_message("motor1_weight")
        await update.message.reply_text(message, parse_mode="HTML")
        
        return Motor1States.ASKING_WEIGHT
    
    async def _motor1_weight_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle weight input for Motor 1."""
        user_id = update.effective_user.id
        weight_text = update.message.text.strip()
        
        # Validate weight
        try:
            weight = float(weight_text)
            if not (40 <= weight <= 200):
                raise ValueError("Weight out of range")
        except ValueError:
            await update.message.reply_text(get_message("validation_weight"), parse_mode="HTML")
            return Motor1States.ASKING_WEIGHT
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "weight", weight)
        
        # Next step
        message = get_message("motor1_objective")
        keyboard = DataSelectionKeyboard.create_objective_keyboard()
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_OBJECTIVE
    
    async def _motor1_objective_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle objective selection for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        objective = query.data.replace("obj_", "")
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "objective", objective)
        
        # Next step
        message = get_message("motor1_activity_type")
        keyboard = DataSelectionKeyboard.create_activity_keyboard()
        await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_ACTIVITY_TYPE
    
    async def _motor1_activity_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle activity selection for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        activity = query.data.replace("act_", "")
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "activity_type", activity)
        
        # Next step
        message = get_message("motor1_activity_frequency")
        keyboard = DataSelectionKeyboard.create_frequency_keyboard()
        await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_ACTIVITY_FREQUENCY
    
    async def _motor1_frequency_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle frequency selection for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        frequency = query.data.replace("freq_", "")
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "frequency", frequency)
        
        # Next step
        message = get_message("motor1_activity_duration")
        await query.message.reply_text(message, parse_mode="HTML")
        
        return Motor1States.ASKING_ACTIVITY_DURATION
    
    async def _motor1_duration_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle duration input for Motor 1."""
        user_id = update.effective_user.id
        duration_text = update.message.text.strip()
        
        # Validate duration
        try:
            duration = int(duration_text)
            if not (15 <= duration <= 300):
                raise ValueError("Duration out of range")
        except ValueError:
            await update.message.reply_text(get_message("validation_duration"), parse_mode="HTML")
            return Motor1States.ASKING_ACTIVITY_DURATION
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "duration", duration)
        
        # Next step
        message = get_message("motor1_weight_type")
        keyboard = DataSelectionKeyboard.create_weight_type_keyboard()
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_WEIGHT_TYPE
    
    async def _motor1_weight_type_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle weight type selection for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        weight_type = query.data.replace("weight_", "")
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "peso_tipo", weight_type)
        
        # Next step
        message = get_message("motor1_economic_level")
        keyboard = DataSelectionKeyboard.create_economic_level_keyboard()
        await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_ECONOMIC_LEVEL
    
    async def _motor1_economic_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle economic level selection for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        economic_level = query.data.replace("econ_", "")
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "economic_level", economic_level)
        
        # Next step
        message = get_message("motor1_supplements")
        keyboard = DataSelectionKeyboard.create_supplements_keyboard()
        await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_SUPPLEMENTS
    
    async def _motor1_supplements_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle supplements selection for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        supplement = query.data.replace("supp_", "")
        
        # Handle supplements (can be multiple)
        if supplement == "none":
            supplements = []
        else:
            # Get current supplements
            patient_data = self.conversation_manager.get_patient_data(user_id)
            supplements = patient_data.supplements if patient_data else []
            
            if supplement not in supplements:
                supplements.append(supplement)
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "supplements", supplements)
        
        # Next step
        message = get_message("motor1_pathologies")
        keyboard = NavigationKeyboard.create(show_skip=True)
        await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_PATHOLOGIES
    
    async def _motor1_pathologies_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pathologies input for Motor 1."""
        user_id = update.effective_user.id
        pathologies_text = update.message.text.strip()
        
        # Parse pathologies
        if pathologies_text.lower() in ["ninguna", "ninguno", "no", "none"]:
            pathologies = []
        else:
            pathologies = [p.strip() for p in pathologies_text.split(",") if p.strip()]
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "pathologies", pathologies)
        
        # Next step
        message = get_message("motor1_restrictions")
        keyboard = DataSelectionKeyboard.create_restrictions_keyboard()
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_RESTRICTIONS
    
    async def _motor1_restrictions_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle restrictions selection for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        restriction = query.data.replace("rest_", "")
        
        # Handle restrictions (can be multiple)
        if restriction == "none":
            restrictions = []
        else:
            # Get current restrictions
            patient_data = self.conversation_manager.get_patient_data(user_id)
            restrictions = patient_data.restrictions if patient_data else []
            
            if restriction not in restrictions:
                restrictions.append(restriction)
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "restrictions", restrictions)
        
        # Next step
        message = get_message("motor1_preferences")
        keyboard = NavigationKeyboard.create(show_skip=True)
        await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_PREFERENCES
    
    async def _motor1_preferences_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle preferences input for Motor 1."""
        user_id = update.effective_user.id
        preferences_text = update.message.text.strip()
        
        # Parse preferences
        preferences = [p.strip() for p in preferences_text.split(",") if p.strip()]
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "preferences", preferences)
        
        # Next step
        message = get_message("motor1_dislikes")
        keyboard = NavigationKeyboard.create(show_skip=True)
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_DISLIKES
    
    async def _motor1_dislikes_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle dislikes input for Motor 1."""
        user_id = update.effective_user.id
        dislikes_text = update.message.text.strip()
        
        # Parse dislikes
        dislikes = [d.strip() for d in dislikes_text.split(",") if d.strip()]
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "dislikes", dislikes)
        
        # Next step
        message = get_message("motor1_allergies")
        keyboard = NavigationKeyboard.create(show_skip=True)
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_ALLERGIES
    
    async def _motor1_allergies_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle allergies input for Motor 1."""
        user_id = update.effective_user.id
        allergies_text = update.message.text.strip()
        
        # Parse allergies
        if allergies_text.lower() in ["ninguna", "ninguno", "no", "none"]:
            allergies = []
        else:
            allergies = [a.strip() for a in allergies_text.split(",") if a.strip()]
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "allergies", allergies)
        
        # Next step
        message = get_message("motor1_main_meals")
        keyboard = DataSelectionKeyboard.create_number_keyboard(2, 5, "num")
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_MAIN_MEALS
    
    async def _motor1_main_meals_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle main meals selection for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        main_meals = int(query.data.replace("num_", ""))
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "main_meals", main_meals)
        
        # Next step
        message = get_message("motor1_collations")
        keyboard = DataSelectionKeyboard.create_number_keyboard(0, 3, "num")
        await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_COLLATIONS
    
    async def _motor1_collations_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle collations selection for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        collations = int(query.data.replace("num_", ""))
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "collations", collations)
        
        # Next step
        message = get_message("motor1_schedule")
        keyboard = NavigationKeyboard.create(show_skip=True)
        await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_SCHEDULE
    
    async def _motor1_schedule_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle schedule input for Motor 1."""
        user_id = update.effective_user.id
        schedule_text = update.message.text.strip()
        
        # Parse schedule (simple text for now)
        schedule = {"notes": schedule_text}
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "schedule", schedule)
        
        # Next step
        message = get_message("motor1_notes")
        keyboard = NavigationKeyboard.create(show_skip=True)
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.ASKING_NOTES
    
    async def _motor1_notes_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle notes input for Motor 1."""
        user_id = update.effective_user.id
        notes = update.message.text.strip()
        
        # Save data
        self.conversation_manager.update_patient_data(user_id, "notes", notes)
        
        # Review data
        return await self._show_motor1_review(user_id, update)
    
    async def _show_motor1_review(self, user_id: int, update: Update):
        """Show data review for Motor 1."""
        # Get patient data
        patient_data = self.conversation_manager.get_patient_data(user_id)
        
        if not patient_data:
            await update.message.reply_text("Error: No se encontraron datos del paciente.")
            return ConversationHandler.END
        
        # Format patient summary
        from ..locales import format_patient_summary
        summary = format_patient_summary(patient_data.to_dict())
        
        message = get_message("motor1_review", patient_summary=summary)
        keyboard = ConfirmationKeyboard.create_with_edit("confirm", "edit", "cancel")
        
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor1States.REVIEWING_DATA
    
    async def _motor1_review_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle review response for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        action = query.data
        
        if action == "confirm":
            # Generate plan
            message = get_message("motor1_generating")
            await query.message.reply_text(message, parse_mode="HTML")
            
            # Call API to generate plan
            api_service = await get_api_service()
            
            # First create patient
            patient_data = self.conversation_manager.get_patient_data(user_id)
            patient_response = await api_service.create_patient(patient_data)
            
            if patient_response.success:
                patient_id = patient_response.data.get("id")
                
                # Generate plan
                plan_response = await api_service.generate_plan(patient_id, "nuevo_paciente")
                
                if plan_response.success:
                    plan_data = plan_response.data
                    
                    # Generate PDF
                    pdf_response = await api_service.generate_pdf(plan_data.get("id"))
                    
                    if pdf_response.success:
                        weight_type = patient_data.peso_tipo or "crudo"
                        message = get_message("motor1_plan_ready", weight_type=weight_type)
                        await query.message.reply_text(message, parse_mode="HTML")
                        
                        # TODO: Send PDF file
                        await query.message.reply_text("=Ä Enviando PDF...")
                        
                        # End conversation
                        self.conversation_manager.end_conversation(user_id)
                        return ConversationHandler.END
                    else:
                        await query.message.reply_text("Error al generar PDF. Intenta nuevamente.")
                        return Motor1States.REVIEWING_DATA
                else:
                    await query.message.reply_text("Error al generar el plan. Intenta nuevamente.")
                    return Motor1States.REVIEWING_DATA
            else:
                await query.message.reply_text("Error al crear el paciente. Intenta nuevamente.")
                return Motor1States.REVIEWING_DATA
        
        elif action == "edit":
            # TODO: Implement edit functionality
            await query.message.reply_text("Funcionalidad de edición en desarrollo.")
            return Motor1States.REVIEWING_DATA
        
        return Motor1States.REVIEWING_DATA
    
    async def _motor1_generate_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle plan generation confirmation for Motor 1."""
        query = update.callback_query
        await query.answer()
        
        # This would be handled by the review handler
        return await self._motor1_review_handler(update, context)
    
    # Motor 2 handlers (Control/Adjustment) - Placeholder implementations
    async def _motor2_verify_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle patient verification for Motor 2."""
        query = update.callback_query
        await query.answer()
        
        # Continue with Motor 2 flow
        message = get_message("motor2_current_weight")
        await query.message.reply_text(message, parse_mode="HTML")
        
        return Motor2States.ASKING_CURRENT_WEIGHT
    
    async def _motor2_weight_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle current weight input for Motor 2."""
        # TODO: Implement Motor 2 weight handler
        await update.message.reply_text("Motor 2 en desarrollo...")
        return ConversationHandler.END
    
    async def _motor2_progress_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle progress input for Motor 2."""
        # TODO: Implement Motor 2 progress handler
        return Motor2States.ASKING_COMPLIANCE
    
    async def _motor2_compliance_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle compliance input for Motor 2."""
        # TODO: Implement Motor 2 compliance handler
        return Motor2States.ASKING_DIFFICULTIES
    
    async def _motor2_difficulties_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle difficulties input for Motor 2."""
        # TODO: Implement Motor 2 difficulties handler
        return Motor2States.ASKING_OBJECTIVE_CHANGE
    
    async def _motor2_objective_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle objective change for Motor 2."""
        # TODO: Implement Motor 2 objective handler
        return Motor2States.ASKING_ACTIVITY_CHANGE
    
    async def _motor2_activity_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle activity change for Motor 2."""
        # TODO: Implement Motor 2 activity handler
        return Motor2States.ASKING_PREFERENCE_CHANGE
    
    async def _motor2_preferences_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle preferences change for Motor 2."""
        # TODO: Implement Motor 2 preferences handler
        return Motor2States.ASKING_SPECIFIC_INSTRUCTIONS
    
    async def _motor2_instructions_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle specific instructions for Motor 2."""
        # TODO: Implement Motor 2 instructions handler
        return Motor2States.REVIEWING_CHANGES
    
    async def _motor2_review_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle changes review for Motor 2."""
        # TODO: Implement Motor 2 review handler
        return Motor2States.REGENERATING_PLAN
    
    async def _motor2_regenerate_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle plan regeneration for Motor 2."""
        # TODO: Implement Motor 2 regeneration handler
        return ConversationHandler.END
    
    # Motor 3 handlers (Meal Replacement) - Placeholder implementations
    async def _motor3_verify_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle patient verification for Motor 3."""
        query = update.callback_query
        await query.answer()
        
        # Continue with Motor 3 flow
        message = get_message("motor3_select_day")
        from ..keyboards import PlanSelectionKeyboard
        keyboard = PlanSelectionKeyboard.create_day_selection()
        await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor3States.SELECTING_DAY
    
    async def _motor3_plan_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle plan selection for Motor 3."""
        # TODO: Implement Motor 3 plan handler
        return Motor3States.SELECTING_DAY
    
    async def _motor3_day_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle day selection for Motor 3."""
        query = update.callback_query
        await query.answer()
        
        day = query.data
        
        # Save selected day
        user_id = query.from_user.id
        conversation = self.conversation_manager.get_conversation(user_id)
        if conversation:
            conversation.context["selected_day"] = day
            self.conversation_manager.save_conversation(conversation)
        
        # Next step
        message = get_message("motor3_select_meal", day=day.replace("day_", ""))
        from ..keyboards import MealSelectionKeyboard
        keyboard = MealSelectionKeyboard.create_meal_type_selection()
        await query.message.reply_text(message, reply_markup=keyboard, parse_mode="HTML")
        
        return Motor3States.SELECTING_MEAL
    
    async def _motor3_meal_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle meal selection for Motor 3."""
        # TODO: Implement Motor 3 meal handler
        return Motor3States.SELECTING_MEAL_OPTION
    
    async def _motor3_option_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle meal option selection for Motor 3."""
        # TODO: Implement Motor 3 option handler
        return Motor3States.ASKING_REPLACEMENT_TYPE
    
    async def _motor3_type_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle replacement type selection for Motor 3."""
        # TODO: Implement Motor 3 type handler
        return Motor3States.ASKING_REPLACEMENT_REASON
    
    async def _motor3_reason_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle replacement reason for Motor 3."""
        # TODO: Implement Motor 3 reason handler
        return Motor3States.ASKING_SPECIFIC_REQUEST
    
    async def _motor3_request_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle specific request for Motor 3."""
        # TODO: Implement Motor 3 request handler
        return Motor3States.ASKING_SPECIAL_CONDITIONS
    
    async def _motor3_conditions_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle special conditions for Motor 3."""
        # TODO: Implement Motor 3 conditions handler
        return Motor3States.REVIEWING_REPLACEMENT
    
    async def _motor3_review_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle replacement review for Motor 3."""
        # TODO: Implement Motor 3 review handler
        return Motor3States.GENERATING_REPLACEMENT
    
    async def _motor3_generate_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle replacement generation for Motor 3."""
        # TODO: Implement Motor 3 generation handler
        return ConversationHandler.END
    
    # Utility handlers
    async def _fallback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle fallback messages."""
        await update.message.reply_text(
            "No entiendo ese mensaje. Usa /help para ver los comandos disponibles."
        )
        
        self.total_messages += 1
    
    async def _unknown_command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown commands."""
        await update.message.reply_text(
            get_message("invalid_command"),
            parse_mode="HTML"
        )
        
        self.total_commands += 1
    
    async def _unknown_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown callback queries."""
        query = update.callback_query
        await query.answer("Comando no reconocido")
        
        await query.message.reply_text(
            "Comando no reconocido. Usa /start para comenzar de nuevo."
        )
    
    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors."""
        logger.error(f"Exception while handling update: {context.error}")
        
        self.total_errors += 1
        
        # Try to send error message to user
        try:
            if update and hasattr(update, 'effective_user'):
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=get_message("error_general"),
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Could not send error message to user: {e}")
    
    # Utility methods
    async def _update_user_data(self, user):
        """Update user data in storage."""
        from ..models import TelegramUser
        
        user_data = TelegramUser(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code or "es"
        )
        
        # Save to storage
        self.user_manager.save_user_data(user_data)
    
    def _validate_name(self, name: str) -> bool:
        """Validate name input."""
        if not name or len(name) < 2 or len(name) > 50:
            return False
        
        # Check for valid characters (letters, spaces, hyphens)
        import re
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$', name):
            return False
        
        return True
    
    def _validate_numeric_input(self, value: str, min_val: float, max_val: float) -> tuple[bool, float]:
        """Validate numeric input."""
        try:
            num_value = float(value)
            if min_val <= num_value <= max_val:
                return True, num_value
            else:
                return False, 0.0
        except ValueError:
            return False, 0.0
    
    async def run(self):
        """Run the bot."""
        if not await self.initialize():
            logger.error("Failed to initialize bot")
            return
        
        self.is_running = True
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, stopping bot...")
            self.is_running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            logger.info("Starting Sistema Mayra Bot...")
            
            # Start polling
            await self.application.initialize()
            await self.application.start()
            
            if bot_settings.webhook_url:
                # Use webhook
                await self.application.bot.set_webhook(
                    url=bot_settings.webhook_url,
                    drop_pending_updates=True
                )
                logger.info(f"Webhook set to: {bot_settings.webhook_url}")
            else:
                # Use polling
                await self.application.updater.start_polling(
                    drop_pending_updates=True,
                    allowed_updates=BOT_CONFIG["allowed_updates"]
                )
                logger.info("Bot started with polling")
            
            # Keep running until stopped
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error running bot: {e}")
        finally:
            logger.info("Stopping bot...")
            await self.application.stop()
            await self.application.shutdown()
    
    async def stop(self):
        """Stop the bot."""
        self.is_running = False
        
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
        
        logger.info("Bot stopped")
    
    def get_stats(self) -> dict:
        """Get bot statistics."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "uptime": uptime,
            "total_messages": self.total_messages,
            "total_commands": self.total_commands,
            "total_errors": self.total_errors,
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat()
        }


async def main():
    """Main function to run the bot."""
    bot = SistemaMayraBot()
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())