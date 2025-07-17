#!/usr/bin/env python3
"""
Script para obtener tu Telegram User ID
Ejecuta este script y luego envía un mensaje a tu bot
"""

import os
import sys
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    print("❌ Error: No se encontró TELEGRAM_BOT_TOKEN en el archivo .env")
    sys.exit(1)

print(f"🤖 Bot Token encontrado: {TELEGRAM_BOT_TOKEN[:10]}...")

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para obtener el User ID del usuario"""
    user = update.effective_user
    chat = update.effective_chat
    
    print(f"\n✅ ¡Información del usuario obtenida!")
    print(f"👤 Nombre: {user.first_name} {user.last_name or ''}")
    print(f"🆔 User ID: {user.id}")
    print(f"📞 Username: @{user.username if user.username else 'N/A'}")
    print(f"💬 Chat ID: {chat.id}")
    print(f"🌐 Idioma: {user.language_code}")
    
    # Enviar respuesta al usuario
    await update.message.reply_text(
        f"✅ ¡Hola {user.first_name}!\n\n"
        f"🆔 Tu User ID es: `{user.id}`\n"
        f"💬 Chat ID: `{chat.id}`\n\n"
        f"Copia este User ID y actualiza la variable TELEGRAM_ADMIN_USER_ID en tu archivo .env",
        parse_mode="Markdown"
    )
    
    print("\n🔄 Para actualizar tu .env, ejecuta:")
    print(f"TELEGRAM_ADMIN_USER_ID={user.id}")
    
    # Parar la aplicación después de obtener el ID
    context.application.stop_running()

def main():
    """Función principal"""
    print("🚀 Iniciando bot para obtener User ID...")
    print("📱 Envía cualquier mensaje a tu bot para obtener tu User ID")
    print("⏹️  Presiona Ctrl+C para detener\n")
    
    try:
        # Crear aplicación
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Agregar handler para cualquier mensaje
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_id))
        
        # Iniciar bot
        app.run_polling(stop_signals=None)
        
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al ejecutar el bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()