#!/usr/bin/env python3
"""
Bot simple del Sistema Mayra con funcionalidad básica
"""

import os
import json
import random
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("TELEGRAM_ADMIN_USER_ID"))

# Cargar recetas
recipes_file = Path("data/processed/recipes.json")
if recipes_file.exists():
    with open(recipes_file, 'r', encoding='utf-8') as f:
        RECIPES = json.load(f)
else:
    RECIPES = []

# Estados de conversación
SELECTING_MOTOR, COLLECTING_DATA = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el comando /start"""
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("🆕 Paciente Nuevo", callback_data='motor_1')],
        [InlineKeyboardButton("📊 Control/Ajustes", callback_data='motor_2')],
        [InlineKeyboardButton("🔄 Reemplazar Comida", callback_data='motor_3')],
        [InlineKeyboardButton("ℹ️ Ayuda", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"¡Hola {user.first_name}! 👋\n\n"
        f"Soy el Sistema Mayra, tu asistente de nutrición inteligente.\n\n"
        f"Utilizo el método 'Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva' "
        f"para crear planes nutricionales personalizados.\n\n"
        f"¿Qué te gustaría hacer hoy?"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    # Limpiar datos de sesión
    context.user_data.clear()
    
    print(f"✅ Usuario conectado: {user.first_name} (ID: {user.id})")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para botones inline"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'motor_1':
        await motor_1_start(update, context)
    elif query.data == 'motor_2':
        await motor_2_start(update, context)
    elif query.data == 'motor_3':
        await motor_3_start(update, context)
    elif query.data == 'help':
        await help_info(update, context)
    elif query.data.startswith('recipe_'):
        await show_recipe_details(update, context)

async def motor_1_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar Motor 1 - Paciente Nuevo"""
    query = update.callback_query
    
    text = (
        "🆕 **MOTOR 1: PACIENTE NUEVO**\n\n"
        "Voy a ayudarte a crear un plan nutricional personalizado.\n"
        "Necesitaré algunos datos:\n\n"
        "• Datos personales (edad, sexo, altura, peso)\n"
        "• Objetivo nutricional\n"
        "• Nivel de actividad física\n"
        "• Restricciones alimentarias\n\n"
        "Por favor, comienza diciéndome tu **nombre completo**:"
    )
    
    await query.edit_message_text(text, parse_mode='Markdown')
    context.user_data['motor'] = 'motor_1'
    context.user_data['step'] = 'name'

async def motor_2_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar Motor 2 - Control"""
    query = update.callback_query
    
    text = (
        "📊 **MOTOR 2: CONTROL Y AJUSTES**\n\n"
        "Esta función te permite ajustar tu plan actual.\n"
        "Próximamente disponible.\n\n"
        "Por ahora, te mostraré algunas recetas disponibles:"
    )
    
    # Mostrar algunas recetas aleatorias
    sample_recipes = random.sample(RECIPES, min(5, len(RECIPES)))
    recipes_text = "\n".join([f"• {r['name']}" for r in sample_recipes])
    
    await query.edit_message_text(f"{text}\n\n{recipes_text}")

async def motor_3_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar Motor 3 - Reemplazo"""
    query = update.callback_query
    
    # Mostrar recetas por categoría
    keyboard = []
    
    # Agrupar por categoría
    categories = {}
    for recipe in RECIPES:
        cat = recipe['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(recipe)
    
    text = "🔄 **REEMPLAZO DE COMIDAS**\n\nSelecciona una categoría:"
    
    for cat_name, recipes in categories.items():
        display_name = {
            'almuerzo_cena': '🍽️ Almuerzos/Cenas',
            'desayuno_merienda': '☕ Desayunos/Meriendas',
            'colacion': '🥜 Colaciones'
        }.get(cat_name, cat_name)
        
        keyboard.append([InlineKeyboardButton(
            f"{display_name} ({len(recipes)})",
            callback_data=f'cat_{cat_name}'
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data='back_to_start')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def help_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar información de ayuda"""
    query = update.callback_query
    
    help_text = (
        "ℹ️ **SISTEMA MAYRA - AYUDA**\n\n"
        "Este sistema utiliza inteligencia artificial para generar planes nutricionales "
        "personalizados usando el método 'Tres Días y Carga'.\n\n"
        "**Características:**\n"
        "• Plans de 3 días iguales en calorías\n"
        "• Todas las porciones en gramos\n"
        "• 3 opciones equivalentes por comida\n"
        "• Adaptado a tus objetivos y restricciones\n\n"
        f"**Base de datos:** {len(RECIPES)} recetas disponibles\n\n"
        "**Comandos:**\n"
        "/start - Menú principal\n"
        "/help - Esta ayuda\n"
        "/recetas - Ver recetas disponibles"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data='back_to_start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensajes de texto"""
    text = update.message.text
    user = update.effective_user
    
    # Si estamos en el motor 1
    if context.user_data.get('motor') == 'motor_1':
        step = context.user_data.get('step')
        
        if step == 'name':
            context.user_data['name'] = text
            context.user_data['step'] = 'age'
            await update.message.reply_text(
                f"Perfecto {text}! Ahora dime tu **edad**:",
                parse_mode='Markdown'
            )
        
        elif step == 'age':
            try:
                age = int(text)
                context.user_data['age'] = age
                context.user_data['step'] = 'complete'
                
                # Mostrar resumen y plan simple
                name = context.user_data['name']
                
                summary = (
                    f"✅ **DATOS REGISTRADOS**\n\n"
                    f"**Nombre:** {name}\n"
                    f"**Edad:** {age} años\n\n"
                    f"Basándome en tus datos, aquí hay algunas recomendaciones:\n\n"
                )
                
                # Seleccionar recetas aleatorias
                breakfast = random.choice([r for r in RECIPES if r['type'] in ['dulce', 'salado']])
                lunch = random.choice([r for r in RECIPES if r['category'] == 'almuerzo_cena'])
                snack = random.choice([r for r in RECIPES if r['category'] == 'colacion'])
                
                plan = (
                    f"**🌅 DESAYUNO:**\n{breakfast['name']}\n\n"
                    f"**🍽️ ALMUERZO:**\n{lunch['name']}\n\n"
                    f"**🥜 COLACIÓN:**\n{snack['name']}\n\n"
                    f"Este es un ejemplo básico. El sistema completo generará "
                    f"un plan personalizado de 3 días con todas las especificaciones."
                )
                
                await update.message.reply_text(
                    summary + plan,
                    parse_mode='Markdown'
                )
                
                # Limpiar datos
                context.user_data.clear()
                
            except ValueError:
                await update.message.reply_text("Por favor, ingresa un número válido para la edad.")
    
    else:
        # Mensaje genérico
        await update.message.reply_text(
            "No entendí tu mensaje. Usa /start para comenzar o /help para ayuda."
        )

async def recipes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar recetas disponibles"""
    # Agrupar por categoría
    categories = {}
    for recipe in RECIPES:
        cat = recipe['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    text = "📚 **RECETAS DISPONIBLES**\n\n"
    for cat, count in categories.items():
        display_name = {
            'almuerzo_cena': '🍽️ Almuerzos/Cenas',
            'desayuno_merienda': '☕ Desayunos/Meriendas',
            'colacion': '🥜 Colaciones'
        }.get(cat, cat)
        text += f"{display_name}: {count} recetas\n"
    
    text += f"\n**Total:** {len(RECIPES)} recetas"
    
    # Mostrar 5 recetas aleatorias
    text += "\n\n**Ejemplos:**\n"
    for recipe in random.sample(RECIPES, min(5, len(RECIPES))):
        text += f"• {recipe['name']}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

def main():
    """Función principal"""
    print("🚀 Iniciando Sistema Mayra Bot...")
    print(f"📚 Recetas cargadas: {len(RECIPES)}")
    print(f"👤 Admin User ID: {ADMIN_USER_ID}")
    
    # Crear la aplicación
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Agregar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", lambda u, c: help_info(u, c)))
    app.add_handler(CommandHandler("recetas", recipes_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar el bot
    print("✅ Bot iniciado. Presiona Ctrl+C para detener.")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()