#!/usr/bin/env python3
"""
Script simple para obtener tu Telegram User ID
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_NAME = "sistema_mayra_bot"  # Cambia esto al username de tu bot

print(f"""
🤖 Sistema Mayra - Obtener User ID
==================================

Tu bot token está configurado: {BOT_TOKEN[:10]}...

Para obtener tu User ID de Telegram:

1. Abre Telegram en tu teléfono o computadora
2. Busca tu bot: @{BOT_NAME}
3. Envíale el comando: /start
4. Luego visita este enlace en tu navegador:

https://api.telegram.org/bot{BOT_TOKEN}/getUpdates

5. Busca tu mensaje en el JSON y encuentra tu User ID en:
   "from": {{
     "id": TU_USER_ID_AQUÍ,
     "first_name": "Tu Nombre",
     ...
   }}

6. Copia ese número y actualiza TELEGRAM_ADMIN_USER_ID en el archivo .env

Nota: Si no ves tu mensaje, envía otro mensaje al bot y recarga la página.
""")