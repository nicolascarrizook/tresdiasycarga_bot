# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Sistema Mayra - Nutrition AI Platform

Sistema Mayra is a complete AI-powered nutrition planning system that generates personalized nutrition plans using the "Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva" methodology. The system combines OpenAI GPT-4, RAG (Retrieval-Augmented Generation), and a Telegram bot interface to create a comprehensive nutrition consultation platform.

## Quick Start Guide

```bash
# 1. Clone and setup environment
git clone <repository-url>
cd botresdiasycarga
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your keys

# 3. Setup databases
docker-compose up -d postgres redis chromadb
alembic upgrade head
python -m database.seeders.main --mode=all

# 4. Process initial data
python -m data_processor.main

# 5. Start services
uvicorn api.main:app --reload  # Terminal 1
python -m telegram_bot.main     # Terminal 2
```

## Architecture Overview

The system follows a multi-service architecture with four main components:

1. **FastAPI Backend** (`api/`) - REST API with RAG system integration
2. **Telegram Bot** (`telegram_bot/`) - User interface with three conversation motors
3. **Data Processor** (`data_processor/`) - DOCX document processing and embedding generation
4. **Database Layer** (`database/`) - PostgreSQL, Redis, and ChromaDB management

### Three Motors System

The core functionality is built around three conversation motors:

- **Motor 1**: New patient registration and plan generation
- **Motor 2**: Plan control and adjustments for existing patients
- **Motor 3**: Meal replacement while maintaining nutritional balance

### Project Structure

```
botresdiasycarga/
├── api/                    # FastAPI Backend
│   ├── core/              # Core configuration
│   ├── endpoints/         # REST API routes
│   ├── services/          # Business logic
│   └── schemas/           # Pydantic models
├── telegram_bot/          # Telegram Bot
│   ├── handlers/          # Message/command handlers
│   ├── keyboards/         # Interactive UI
│   ├── states/            # Conversation states
│   └── services/          # API integration
├── data_processor/        # Document Processing
│   ├── parsers/           # DOCX parsers
│   ├── extractors/        # Data extraction
│   ├── embeddings/        # Vector generation
│   └── validators/        # Data validation
├── database/              # Database Layer
│   ├── models/            # SQLAlchemy models
│   ├── migrations/        # Alembic migrations
│   ├── repositories/      # Data access layer
│   └── seeders/           # Database initialization
├── n8n_workflows/         # Automation
├── tests/                 # Test suites
├── docker/                # Docker configurations
└── data/                  # Data storage
    ├── raw/              # Source DOCX files
    └── processed/        # Processed data
```

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Database Management
```bash
# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# Populate database with seed data
python -m database.seeders.main --mode=all

# Reset database (CAUTION: Deletes all data)
alembic downgrade base && alembic upgrade head
```

### Data Processing
```bash
# Process DOCX files and generate embeddings
python -m data_processor.main

# Process specific directory
python data_processor/main.py --input-dir data/raw --output-dir data/processed

# Validate processed data
python -m data_processor.validators.validate_all

# Generate embeddings only
python -m data_processor.embeddings.generate
```

### Service Management
```bash
# Start API server
uvicorn api.main:app --reload --port 8000

# Start Telegram bot
python -m telegram_bot.main

# Start all services with Docker
docker-compose up --build

# Start specific services
docker-compose up api telegram-bot

# View logs
docker-compose logs -f api
docker-compose logs -f telegram-bot
```

### Testing
```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_api/
pytest tests/test_bot/
pytest tests/test_processor/

# Run with coverage
pytest --cov=api --cov=telegram_bot --cov=data_processor

# Run with coverage report
pytest --cov=api --cov-report=html

# Run single test
pytest tests/test_api/test_endpoints.py::test_health_check

# Run tests with verbose output
pytest -v

# Run only fast tests (unit tests)
pytest -m "not slow"

# Run integration tests only
pytest -m integration
```

### Code Quality
```bash
# Format code
black .

# Lint code
ruff check .

# Fix lint issues automatically
ruff check . --fix

# Type checking
mypy .

# Run all quality checks
black . && ruff check . && mypy .

# Pre-commit hooks (if configured)
pre-commit run --all-files
```

## Key Configuration Files

- `.env` - Environment variables (copy from `.env.example`)
- `config/settings.py` - Main application settings
- `config/prompts.py` - System prompts for the three motors
- `pyproject.toml` - Tool configuration (Black, Ruff, MyPy, Pytest)
- `alembic.ini` - Database migration configuration
- `docker-compose.yml` - Docker service orchestration

## Critical Environment Variables

```bash
# Required for functionality
OPENAI_API_KEY=your-openai-key
TELEGRAM_BOT_TOKEN=your-bot-token
DATABASE_URL=postgresql://user:pass@localhost:5432/nutrition_db
REDIS_URL=redis://localhost:6379
CHROMA_HOST=localhost
CHROMA_PORT=8001
SECRET_KEY=your-secret-key

# Optional but recommended
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Data Processing Pipeline

The system processes DOCX files containing recipes and nutritional data:

1. **Parsers** extract structured data from DOCX files
2. **Extractors** process ingredients, nutrition, and preparation steps
3. **Transformers** normalize and standardize the data
4. **Embeddings** generate vector representations for RAG system
5. **Validators** ensure data quality and completeness

Raw DOCX files should be placed in `data/raw/` directory.

### Processing New Recipes
```bash
# 1. Add DOCX files to data/raw/
# 2. Run processor
python -m data_processor.main --validate

# 3. Check logs for any validation errors
tail -f logs/data_processor.log
```

## RAG System Integration

The RAG system uses ChromaDB for vector storage and retrieval:

- Recipe embeddings are generated using sentence-transformers
- Semantic search enables context-aware nutrition recommendations
- OpenAI GPT-4 generates personalized nutrition plans using retrieved context

### RAG Query Examples
```python
# Search for recipes by similarity
results = rag_service.search_similar_recipes("pollo al horno", k=5)

# Filter by dietary restrictions
results = rag_service.search_with_filters(
    query="ensalada",
    filters={"vegetarian": True, "gluten_free": True}
)
```

## Telegram Bot Architecture

The bot uses conversation handlers with state management:

- **States** are defined in `telegram_bot/states/`
- **Handlers** process user interactions in `telegram_bot/handlers/`
- **Keyboards** provide interactive interfaces in `telegram_bot/keyboards/`
- **Services** handle API communication in `telegram_bot/services/`

### Bot Commands
- `/start` - Initialize bot and show main menu
- `/nuevo_paciente` - Start Motor 1 (new patient)
- `/control` - Start Motor 2 (plan control)
- `/reemplazo` - Start Motor 3 (meal replacement)
- `/ayuda` - Show help information
- `/cancelar` - Cancel current operation

## Database Schema

Key models are defined in `database/models/`:

- `Patient` - User profiles with health data and preferences
- `Recipe` - Nutritional recipes with embeddings for RAG
- `Plan` - Generated nutrition plans with 3-day structure
- `Conversation` - Bot interaction history and state
- `User` - System users with authentication

### Common Database Queries
```python
# Get patient by telegram ID
patient = db.query(Patient).filter_by(telegram_id=user_id).first()

# Get active plans for patient
plans = db.query(Plan).filter_by(patient_id=patient.id, is_active=True).all()

# Search recipes by category
recipes = db.query(Recipe).filter_by(category="desayuno").all()
```

## API Endpoints

Main API routes in `api/endpoints/`:

- `/health` - System health checks
- `/patients` - Patient management
- `/plans` - Nutrition plan generation and management
- `/recipes` - Recipe search and management

API documentation available at `http://localhost:8000/docs`

### Example API Requests
```bash
# Health check
curl http://localhost:8000/health

# Create patient
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -d '{"name": "Juan", "age": 30, "weight": 70}'

# Generate plan
curl -X POST http://localhost:8000/plans/generate \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1, "preferences": ["sin gluten"]}'
```

## n8n Workflow Automation

Automation workflows in `n8n_workflows/`:

- Patient follow-up automation
- Meal reminder notifications
- Data backup and reporting
- System monitoring and alerts

### Workflow Management
```bash
# Import workflows
n8n import:workflow --input=n8n_workflows/

# Export workflows
n8n export:workflow --all --output=n8n_workflows/
```

## Common Issues and Troubleshooting

### ChromaDB Connection Issues
```bash
# Check if ChromaDB is running
docker-compose ps chromadb

# Restart ChromaDB
docker-compose restart chromadb

# View ChromaDB logs
docker-compose logs chromadb
```

### OpenAI API Errors
- Check API key is valid and has credits
- Monitor rate limits (GPT-4 has lower limits)
- Use exponential backoff for retries

### Telegram Bot Not Responding
```bash
# Check bot token
python -c "from config.settings import TELEGRAM_BOT_TOKEN; print(TELEGRAM_BOT_TOKEN[:10])"

# Test webhook
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### Database Migration Errors
```bash
# Check current revision
alembic current

# Generate SQL for inspection
alembic upgrade head --sql

# Force revision if stuck
alembic stamp head
```

## Performance Optimization

### ChromaDB Query Optimization
- Use appropriate embedding model size
- Implement query result caching in Redis
- Batch embedding generation for multiple recipes

### GPT-4 Usage Optimization
- Cache frequent responses in Redis
- Use GPT-3.5 for non-critical tasks
- Implement prompt templates to reduce token usage

### Database Query Optimization
- Add indexes for frequently queried fields
- Use eager loading for related entities
- Implement query result pagination

## Security Best Practices

- **Never commit** `.env` files or secrets
- **Sanitize** all user inputs before database queries
- **Encrypt** sensitive patient data at rest
- **Use HTTPS** for all API endpoints in production
- **Implement** rate limiting for API and bot endpoints
- **Audit** all patient data access and modifications
- **Rotate** API keys and tokens regularly

## Development Workflow

1. **For new features**: Create feature branches and follow the three-motor architecture
2. **For API changes**: Update both endpoints and corresponding bot handlers
3. **For data model changes**: Create Alembic migrations and update seeders
4. **For prompt changes**: Update `config/prompts.py` and test with all three motors
5. **For bot changes**: Test all conversation flows end-to-end
6. **For RAG changes**: Regenerate embeddings and test search quality

## Production Deployment

Use Docker Compose for deployment:

```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.prod.yml up -d

# Scale specific services
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Rolling update
docker-compose -f docker-compose.prod.yml up -d --no-deps api
```

### Production Checklist
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Monitoring and alerts setup
- [ ] Rate limiting enabled
- [ ] Error tracking (Sentry) configured
- [ ] Log rotation configured

## Monitoring and Logging

### Application Logs
```bash
# API logs
tail -f logs/api.log

# Bot logs
tail -f logs/telegram_bot.log

# Data processor logs
tail -f logs/data_processor.log
```

### System Monitoring
- Use Prometheus metrics endpoint: `/metrics`
- Monitor ChromaDB performance
- Track OpenAI API usage and costs
- Monitor database connection pool

## Backup and Recovery

### Database Backup
```bash
# Backup PostgreSQL
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Backup ChromaDB
docker exec chromadb python -m chromadb.utils.backup /data /backup

# Backup Redis
docker exec redis redis-cli BGSAVE
```

### Recovery Procedures
1. Restore PostgreSQL from backup
2. Reindex ChromaDB if needed
3. Clear Redis cache after restore
4. Verify all services are operational

## Important Notes

- All prompts must maintain the "Tres Días y Carga" methodology
- User data is in Spanish with Argentine localization
- The system requires OpenAI GPT-4 (not GPT-3.5) for quality nutrition plans
- ChromaDB embeddings are essential for the RAG system functionality
- Always test all three motors when making changes to conversation flow
- Patient data privacy is critical - follow HIPAA-like standards
- Monitor OpenAI costs closely - GPT-4 is expensive
- Keep conversation context under token limits