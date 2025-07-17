#!/usr/bin/env python3
"""
Test simple del bot de Telegram
"""

import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("TELEGRAM_ADMIN_USER_ID", "123456789"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el comando /start"""
    user = update.effective_user
    
    await update.message.reply_text(
        f"¡Hola {user.first_name}! 👋\n\n"
        f"Soy el Sistema Mayra, tu asistente de nutrición.\n"
        f"Tu User ID es: {user.id}\n\n"
        f"{'✅ Eres el administrador' if user.id == ADMIN_USER_ID else '❌ No eres el administrador'}\n\n"
        f"Comandos disponibles:\n"
        f"/start - Iniciar conversación\n"
        f"/help - Mostrar ayuda"
    )
    
    print(f"Usuario conectado: {user.first_name} (ID: {user.id})")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el comando /help"""
    await update.message.reply_text(
        "🤖 Sistema Mayra - Ayuda\n\n"
        "Este es un sistema de nutrición inteligente que genera planes personalizados.\n\n"
        "Próximamente disponible:\n"
        "• Motor 1: Paciente nuevo\n"
        "• Motor 2: Control y ajustes\n"
        "• Motor 3: Reemplazo de comidas"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo de mensajes para pruebas"""
    await update.message.reply_text(f"Recibí tu mensaje: {update.message.text}")

def main():
    """Función principal"""
    print(f"🚀 Iniciando bot de prueba...")
    print(f"Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"Admin User ID: {ADMIN_USER_ID}")
    
    # Crear la aplicación
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Agregar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Iniciar el bot
    print("✅ Bot iniciado. Presiona Ctrl+C para detener.")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()