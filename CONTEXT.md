Prompt Técnico para Claude Code - Sistema Mayra
🎯 Objetivo
Crear un sistema completo de generación automática de planes nutricionales que replique el trabajo de Mayra usando el método "Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva".
📋 Especificaciones del Sistema
Stack Tecnológico Requerido:

Backend: Python 3.11+ con FastAPI
Base de Datos: PostgreSQL + ChromaDB (vectorial)
AI/RAG: OpenAI GPT-4 + LangChain + Sentence Transformers
Bot: Python Telegram Bot
Automatización: n8n workflows
Containerización: Docker + Docker Compose
Hosting: DigitalOcean Droplet

Datos Existentes a Procesar:

Almuerzos/Cenas (formato DOCX): Tabla con 6 categorías (Pollo, Carne, Vegetarianos, Cerdo, Pescado/Mariscos, Ensaladas)
Desayunos/Meriendas (formato DOCX): Organizados en dulces, salados y colaciones
Equivalencias calóricas (formato DOCX): Tablas de intercambio por porciones
Recetas detalladas (formato DOCX): Con preparaciones paso a paso
Planes PDF de Mayra: Como ejemplos de referencia

🏗️ Arquitectura del Sistema
Componentes Principales:

1. Procesador de Datos (data_processor/)

- Convertir DOCX a datos estructurados
- Extraer recetas, ingredientes y valores nutricionales
- Crear embeddings para el sistema RAG
- Generar base de conocimiento vectorial

2. API RAG (api/)

- FastAPI con endpoints para generación de planes
- Integración con OpenAI GPT-4
- Sistema de retrieval inteligente
- Manejo de los 3 motores del prompt de Mayra

3. Bot de Telegram (telegram_bot/)

- Conversación guiada para recolección de datos
- Implementación de los 3 motores:
  - Motor 1: Paciente nuevo
  - Motor 2: Control/ajustes
  - Motor 3: Reemplazo de comida
- Generación y envío de PDFs

4. Base de Datos (database/)

- PostgreSQL: Pacientes, planes, conversaciones
- ChromaDB: Vectores de recetas e ingredientes
- Redis: Cache y gestión de sesiones

5. Workflows n8n (n8n_workflows/)

- Automatización de procesos
- Integración entre servicios
- Notificaciones y seguimiento
  📊 Estructura de Datos a Implementar
  Modelos Principales:
  Paciente:
  python- telegram_user_id, name, age, sex, height, weight
- objective, activity_type, frequency, duration
- supplements, pathologies, restrictions, preferences
- schedule, economic_level, notes
- peso_tipo: "crudo" | "cocido"
  Receta:
  python- name, category, subcategory, ingredients[]
- preparation, cooking_time, difficulty
- economic_level, dietary_restrictions[]
- macros{calories, protein, carbs, fat}
- embedding_vector
  Plan Nutricional:
  python- patient_id, plan_type, plan_data (JSON)
- calories_total, macros{}, created_at
- pdf_path, is_active
  🤖 Implementación del Bot de Telegram
  Flujo de Conversación:
  Motor 1 - Paciente Nuevo:

/start → Bienvenida y registro
Recolección de datos básicos (nombre, edad, sexo, altura, peso)
Objetivo nutricional (botones: mantenimiento, bajar 0.5kg, bajar 1kg, etc.)
Actividad física (botones: sedentario, caminatas, pesas, etc.)
Datos adicionales (suplementos, patologías, restricciones)
Configuración del plan (tipo de peso, comidas principales, colaciones)
Generación y envío del PDF

Motor 2 - Control:

/control → Verificar paciente existente
Datos actualizados (peso actual, objetivo, actividad)
Instrucciones específicas (AGREGAR/SACAR/DEJAR)
Regeneración del plan completo

Motor 3 - Reemplazo:

/reemplazar → Seleccionar día y comida
Nueva comida deseada
Condiciones especiales
Generar reemplazo manteniendo macros

🔧 Prompts del Sistema
Prompt Base (system_prompt.txt):
Eres Mayra, experta en nutrición que genera planes usando el método "Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva".

REGLAS FUNDAMENTALES:

- Plan de 3 días iguales en calorías y macros
- Todas las comidas en gramos {tipo_peso}
- Verduras tipo C (papa, batata, choclo): en gramos
- Otras verduras: libres (porción coherente)
- Frutas: en gramos
- Incluir preparación de cada comida
- Usar léxico argentino
- No usar suplementos no indicados
  Motor 1 - Paciente Nuevo:
  Generá un plan alimentario de 3 días iguales siguiendo el método Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva.

Datos del paciente:
{datos_paciente}

Contexto de recetas disponibles:
{rag_context}

Especificaciones:

- {numero_comidas} comidas principales
- 3 opciones por comida (equivalentes ±5%)
- Colaciones: {tipo_colaciones}
- Tipo de peso: {tipo_peso}
  💾 Implementación RAG
  Proceso de Embedding:

Extraer recetas de los DOCX
Crear embeddings usando sentence-transformers
Almacenar en ChromaDB con metadatos
Implementar retrieval por similitud semántica

Contexto para Generación:
pythondef get_rag_context(patient_data: dict, plan_type: str) -> str:
"""
Recupera contexto relevante basado en: - Restricciones alimentarias - Nivel económico - Preferencias - Tipo de plan (nuevo, control, reemplazo)
""" # Búsqueda vectorial en ChromaDB # Filtrado por metadatos # Ranking por relevancia # Formateo para el prompt
🔐 Configuración y Despliegue
Variables de Entorno (.env):
bash# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key

# Databases

DATABASE_URL=postgresql://user:pass@localhost:5432/nutrition_db
REDIS_URL=redis://localhost:6379
CHROMA_PERSIST_DIRECTORY=./chroma_db

# AI Services

OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4

# Telegram

TELEGRAM_BOT_TOKEN=7965754655:AAF8xliXqzB0v3-W2p_JCfbzXnBnveHACN0
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/telegram/webhook

# n8n

N8N_WEBHOOK_URL=https://n8n-instance.com/webhook
Docker Compose:
yamlservices:
api:
build: ./api
ports: ["8000:8000"]

telegram_bot:
build: ./telegram_bot
depends_on: [api, postgres, redis]

postgres:
image: postgres:15
environment:
POSTGRES_DB: nutrition_db

redis:
image: redis:7

nginx:
image: nginx
ports: ["80:80", "443:443"]
📈 Funcionalidades Específicas
Generación de PDFs:

Template con el formato de Mayra
Información del paciente
Plan de 3 días con equivalencias
Instrucciones de preparación

Validaciones:

Verificar coherencia nutricional
Validar restricciones alimentarias
Comprobar disponibilidad de ingredientes por nivel económico

Monitoreo:

Logs de generación de planes
Métricas de uso del bot
Errores de la API OpenAI

🎯 Entregables Esperados

Sistema completo funcionando con los 3 motores
Base de datos poblada con todas las recetas
Bot de Telegram conversacional
API RAG integrada con OpenAI
Workflows n8n para automatización
Documentación técnica y de usuario
Scripts de deployment para DigitalOcean

🚀 Prioridades de Desarrollo

Fase 1: Procesamiento de datos DOCX → Base de datos estructurada
Fase 2: API RAG básica con OpenAI
Fase 3: Bot de Telegram con Motor 1 (paciente nuevo)
Fase 4: Motores 2 y 3 + generación de PDFs
Fase 5: Workflows n8n + optimizaciones
Fase 6: Deployment y monitoreo
