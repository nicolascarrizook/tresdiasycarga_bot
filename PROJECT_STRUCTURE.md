# Sistema Mayra - Project Directory Structure

```
botresdiasycarga/
│
├── api/                          # FastAPI backend with RAG system
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── core/                     # Core configuration and settings
│   │   └── __init__.py
│   ├── dependencies/             # Dependency injection
│   │   └── __init__.py
│   ├── endpoints/                # API endpoints/routes
│   │   └── __init__.py
│   ├── middleware/               # Custom middleware
│   │   └── __init__.py
│   ├── models/                   # Pydantic models
│   │   └── __init__.py
│   ├── schemas/                  # Request/Response schemas
│   │   └── __init__.py
│   ├── services/                 # Business logic services
│   │   └── __init__.py
│   └── utils/                    # Utility functions
│       └── __init__.py
│
├── telegram_bot/                 # Telegram bot implementation
│   ├── __init__.py
│   ├── main.py                   # Bot entry point
│   ├── handlers/                 # Message and command handlers
│   │   └── __init__.py
│   ├── keyboards/                # Inline and reply keyboards
│   │   └── __init__.py
│   ├── locales/                  # Internationalization files
│   ├── models/                   # Bot-specific models
│   │   └── __init__.py
│   ├── services/                 # Bot services (API client, etc.)
│   │   └── __init__.py
│   ├── states/                   # FSM states for conversations
│   │   └── __init__.py
│   └── utils/                    # Bot utilities
│       └── __init__.py
│
├── data_processor/               # DOCX data processing utilities
│   ├── __init__.py
│   ├── main.py                   # Data processor entry point
│   ├── embeddings/               # Embedding generation
│   │   └── __init__.py
│   ├── extractors/               # Data extraction from DOCX
│   │   └── __init__.py
│   ├── parsers/                  # DOCX parsing logic
│   │   └── __init__.py
│   ├── transformers/             # Data transformation
│   │   └── __init__.py
│   └── validators/               # Data validation
│       └── __init__.py
│
├── database/                     # Database models and migrations
│   ├── __init__.py
│   ├── migrations/               # Alembic migrations
│   │   └── __init__.py
│   ├── models/                   # SQLAlchemy models
│   │   └── __init__.py
│   ├── repositories/             # Repository pattern implementation
│   │   └── __init__.py
│   ├── seeders/                  # Database seeders
│   │   └── __init__.py
│   └── utils/                    # Database utilities
│       └── __init__.py
│
├── n8n_workflows/                # n8n automation workflows
│   ├── configs/                  # Workflow configurations
│   ├── templates/                # Workflow templates
│   ├── patient_registration.json
│   ├── plan_generation.json
│   └── notification_system.json
│
├── docker/                       # Docker configuration files
│   ├── api/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── telegram_bot/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── nginx/
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   └── postgres/
│       └── init.sql
│
├── docs/                         # Documentation
│   ├── README.md
│   ├── api/                      # API documentation
│   │   └── README.md
│   ├── architecture/             # Architecture documentation
│   │   └── system_design.md
│   ├── bot/                      # Bot documentation
│   │   └── README.md
│   ├── deployment/               # Deployment guides
│   │   └── README.md
│   └── user_guide/               # User guides
│       └── bot_usage.md
│
├── data/                         # Data directories
│   ├── raw/                      # Raw DOCX files
│   ├── processed/                # Processed data
│   └── embeddings/               # Vector embeddings
│
├── tests/                        # Test suites
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── unit/                     # Unit tests
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   └── __init__.py
│   │   ├── bot/
│   │   │   └── __init__.py
│   │   └── processor/
│   │       └── __init__.py
│   ├── integration/              # Integration tests
│   │   └── __init__.py
│   └── e2e/                      # End-to-end tests
│       └── __init__.py
│
├── scripts/                      # Utility scripts
│   ├── deployment/               # Deployment scripts
│   │   ├── deploy.sh
│   │   └── rollback.sh
│   ├── maintenance/              # Maintenance scripts
│   │   ├── backup_db.sh
│   │   └── health_check.sh
│   └── data/                     # Data processing scripts
│       ├── import_docx.py
│       └── generate_embeddings.py
│
├── config/                       # Configuration files
├── logs/                         # Log files
├── static/                       # Static files
│   ├── assets/                   # Images, CSS, etc.
│   └── templates/                # PDF templates
│
├── .github/                      # GitHub Actions
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── CONTEXT.md                    # Project context and specifications
├── PROJECT_STRUCTURE.md          # This file
├── .env.example                  # Environment variables example
├── .gitignore                    # Git ignore file
├── docker-compose.yml            # Docker Compose configuration
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Python project configuration
├── pytest.ini                    # Pytest configuration
└── Makefile                      # Build automation
```

## Directory Descriptions

### `/api`
FastAPI backend service that implements the RAG system for nutrition plan generation. Contains all API endpoints, services for OpenAI integration, and business logic.

### `/telegram_bot`
Telegram bot implementation with conversational flow for the three motors (new patient, control, replacement). Handles user interactions and communicates with the API.

### `/data_processor`
Utilities for processing DOCX files containing recipes, meal plans, and nutritional information. Generates embeddings and structures data for the database.

### `/database`
Database layer with SQLAlchemy models for PostgreSQL and ChromaDB integration. Includes migrations, repositories, and seeders.

### `/n8n_workflows`
Automation workflows for n8n including patient registration, plan generation, and notification systems.

### `/docker`
Docker configuration files for all services including API, Telegram bot, Nginx, and PostgreSQL.

### `/docs`
Comprehensive documentation including API specs, bot usage guides, deployment instructions, and system architecture.

### `/data`
Data storage directories for raw DOCX files, processed data, and vector embeddings.

### `/tests`
Complete test suite with unit tests, integration tests, and end-to-end tests for all components.

### `/scripts`
Utility scripts for deployment, maintenance, database backups, health checks, and data processing.

### `/config`
Configuration files for various environments and services.

### `/logs`
Application logs for monitoring and debugging.

### `/static`
Static assets and templates, including PDF generation templates.