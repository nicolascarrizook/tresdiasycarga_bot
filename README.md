# Sistema Mayra - Inteligencia Artificial para Nutrición

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue.svg" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

## 🎯 Descripción

**Sistema Mayra** es una plataforma completa de inteligencia artificial para la generación automática de planes nutricionales que utiliza el método **"Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva"**. 

El sistema combina tecnologías avanzadas de IA, procesamiento de documentos y automatización para crear planes nutricionales personalizados a través de un bot de Telegram intuitivo.

### ✨ Características Principales

- 🤖 **Bot de Telegram inteligente** con tres motores de conversación
- 📊 **Generación automática de planes nutricionales** usando OpenAI GPT-4
- 📚 **Sistema RAG (Retrieval-Augmented Generation)** para recomendaciones precisas
- 📄 **Procesamiento de documentos DOCX** con recetas y equivalencias
- 🔄 **Automatización con n8n** para workflows complejos
- 📱 **API RESTful** con FastAPI para integraciones
- 🐳 **Containerización completa** con Docker

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │   FastAPI API   │    │ Data Processor  │
│                 │    │                 │    │                 │
│ • Motor 1: Nuevo│    │ • Endpoints     │    │ • DOCX Parser   │
│ • Motor 2: Control│  │ • RAG System    │    │ • Embeddings    │
│ • Motor 3: Reemplazo│ │ • Auth & Security│   │ • Validation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                │
                ┌─────────────────────────────────┐
                │        Bases de Datos          │
                │                                │
                │ • PostgreSQL (Principal)       │
                │ • Redis (Cache & Sesiones)     │
                │ • ChromaDB (Embeddings)        │
                └─────────────────────────────────┘
```

### Stack Tecnológico

- **Backend**: Python 3.11+ con FastAPI
- **Base de Datos**: PostgreSQL + Redis + ChromaDB
- **IA**: OpenAI GPT-4 + LangChain + Sentence Transformers
- **Bot**: Python Telegram Bot
- **Automatización**: n8n workflows
- **Containerización**: Docker + Docker Compose
- **Deployment**: DigitalOcean ready

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.11+
- Docker y Docker Compose
- Git
- OpenAI API Key
- Telegram Bot Token

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/sistema-mayra.git
cd sistema-mayra

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Iniciar con Docker Compose
docker-compose up --build

# 4. Acceder a los servicios
# API: http://localhost:8000
# Bot: Se conecta automáticamente
# n8n: http://localhost:5678
```

### Instalación Manual

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar bases de datos
# PostgreSQL
createdb nutrition_db

# Redis
redis-server

# ChromaDB
# Se inicia automáticamente

# 4. Ejecutar migraciones
alembic upgrade head

# 5. Poblar base de datos
python -m database.seeders.main --mode=all

# 6. Iniciar servicios
# API
uvicorn api.main:app --reload

# Bot (en otra terminal)
python -m telegram_bot.main
```

## 📝 Configuración

### Variables de Entorno Principales

```bash
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/nutrition_db
REDIS_URL=redis://localhost:6379
CHROMA_HOST=localhost

# OpenAI
OPENAI_API_KEY=tu-clave-openai
OPENAI_MODEL=gpt-4

# Telegram
TELEGRAM_BOT_TOKEN=tu-token-bot
TELEGRAM_ADMIN_USER_ID=tu-user-id

# API
SECRET_KEY=tu-clave-secreta-muy-larga
DEBUG=false
```

### Estructura de Directorios

```
sistema-mayra/
├── api/                    # FastAPI application
│   ├── core/              # Core configuration
│   ├── endpoints/         # API endpoints
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic
├── telegram_bot/          # Telegram bot
│   ├── handlers/          # Message handlers
│   ├── keyboards/         # Inline keyboards
│   ├── services/          # Bot services
│   └── states/            # Conversation states
├── data_processor/        # Document processing
│   ├── parsers/           # DOCX parsers
│   ├── extractors/        # Data extractors
│   └── embeddings/        # Vector embeddings
├── database/              # Database layer
│   ├── models/            # SQLAlchemy models
│   ├── repositories/      # Data repositories
│   └── migrations/        # Alembic migrations
├── config/                # Configuration files
├── data/                  # Data storage
├── docker/                # Docker configurations
├── n8n_workflows/         # n8n automation
├── static/                # Static files
└── tests/                 # Test suites
```

## 🤖 Uso del Bot de Telegram

### Los Tres Motores

#### Motor 1: Paciente Nuevo
```
/start → Registro completo del paciente
1. Datos básicos (nombre, edad, sexo, altura, peso)
2. Objetivo nutricional
3. Actividad física
4. Restricciones y preferencias
5. Configuración del plan
6. Generación automática del PDF
```

#### Motor 2: Control y Ajustes
```
/control → Seguimiento del paciente
1. Verificación de datos actuales
2. Progreso y dificultades
3. Ajustes del plan
4. Regeneración con cambios
```

#### Motor 3: Reemplazo de Comidas
```
/reemplazar → Cambio de comidas específicas
1. Selección de día y comida
2. Tipo de reemplazo deseado
3. Mantenimiento de macros
4. Generación del reemplazo
```

### Comandos Disponibles

- `/start` - Iniciar proceso de registro
- `/control` - Control y ajustes del plan
- `/reemplazar` - Reemplazar comidas específicas
- `/perfil` - Ver perfil del paciente
- `/ayuda` - Mostrar ayuda
- `/admin` - Panel de administración (solo admin)

## 🔧 Desarrollo

### Estructura de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
pytest

# Linting y formateo
black .
ruff check .
mypy .

# Pre-commit hooks
pre-commit install
```

### Agregar Nuevas Funcionalidades

1. **Nuevos endpoints de API**:
   ```python
   # En api/endpoints/
   from fastapi import APIRouter
   router = APIRouter()
   
   @router.get("/nueva-funcionalidad")
   async def nueva_funcionalidad():
       return {"mensaje": "Funcionando"}
   ```

2. **Nuevos handlers del bot**:
   ```python
   # En telegram_bot/handlers/
   from telegram.ext import CommandHandler
   
   async def nuevo_comando(update, context):
       await update.message.reply_text("Nuevo comando")
   
   # Registrar en main.py
   app.add_handler(CommandHandler("nuevo", nuevo_comando))
   ```

3. **Nuevos modelos de datos**:
   ```python
   # En database/models/
   from sqlalchemy import Column, Integer, String
   
   class NuevoModelo(Base):
       __tablename__ = "nuevo_modelo"
       id = Column(Integer, primary_key=True)
       nombre = Column(String)
   ```

### Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con coverage
pytest --cov=api --cov=telegram_bot --cov=data_processor

# Tests específicos
pytest tests/test_api/
pytest tests/test_bot/
pytest tests/test_processor/
```

## 📊 Monitoreo y Logging

### Logs Estructurados

```python
from config.logging import get_logger

logger = get_logger(__name__)

logger.info("Procesando plan nutricional", extra={
    "patient_id": patient.id,
    "plan_type": "new_patient",
    "calories": 2000
})
```

### Métricas y Salud

- **Health checks**: `GET /health`
- **Métricas**: `GET /metrics`
- **Status del sistema**: `GET /status`

### Grafana Dashboard

```bash
# Acceder a Grafana
http://localhost:3000
# Usuario: admin
# Password: configurado en .env
```

## 🔐 Seguridad

### Autenticación

- **JWT tokens** para autenticación API
- **Telegram user verification** para el bot
- **Role-based access control**

### Mejores Prácticas

- Variables de entorno para credenciales
- Validación de entrada en todos los endpoints
- Rate limiting en API y bot
- Logging de auditoría
- Encriptación de datos sensibles

## 🌍 Deployment

### DigitalOcean Droplet

```bash
# 1. Crear droplet con Docker
doctl compute droplet create sistema-mayra \
  --image docker-20-04 \
  --size s-2vcpu-4gb \
  --region nyc3

# 2. Configurar dominio y SSL
certbot --nginx -d tudominio.com

# 3. Deploy con Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Variables de Producción

```bash
# .env.prod
ENV=production
DEBUG=false
DATABASE_URL=postgresql://usuario:password@db:5432/nutrition_db
TELEGRAM_WEBHOOK_URL=https://tudominio.com/webhook
CORS_ORIGINS=["https://tudominio.com"]
```

## 🧪 Procesamiento de Datos

### Cargar Recetas desde DOCX

```python
from data_processor.main import DataProcessor

# Procesar documentos DOCX
processor = DataProcessor()
resultados = processor.process_directory("./data/raw/")

# Generar embeddings
processor.generate_embeddings()

# Poblar base de datos
processor.populate_database()
```

### Formatos Soportados

- **Almuerzos/Cenas**: Tablas con 6 categorías
- **Desayunos/Meriendas**: Dulces, salados, colaciones
- **Equivalencias**: Intercambios por porciones
- **Recetas detalladas**: Paso a paso

## 📈 Workflow n8n

### Automatizaciones Disponibles

1. **Seguimiento de pacientes**
2. **Notificaciones automáticas**
3. **Backup de datos**
4. **Reportes periódicos**
5. **Integración con servicios externos**

### Configurar n8n

```bash
# Acceder a n8n
http://localhost:5678

# Importar workflows
cp n8n_workflows/*.json /home/node/workflows/
```

## 🤝 Contribución

### Guía de Contribución

1. Fork el repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estilo de Código

- **Black** para formateo
- **Ruff** para linting
- **MyPy** para type checking
- **Pytest** para testing
- **Docstrings** en español

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

### Documentación

- **API**: http://localhost:8000/docs
- **Arquitectura**: [docs/architecture.md](docs/architecture.md)
- **Deployment**: [docs/deployment.md](docs/deployment.md)

### Contacto

- **Email**: soporte@sistema-mayra.com
- **Telegram**: @sistema_mayra_bot
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/sistema-mayra/issues)

---

<div align="center">
  <p>Desarrollado con ❤️ para profesionales de la nutrición</p>
  <p><strong>Sistema Mayra</strong> - Inteligencia Artificial para Nutrición</p>
</div>