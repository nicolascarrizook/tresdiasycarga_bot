#!/usr/bin/env python3
"""
Setup script for test environment
Sistema Mayra - Nutrition AI Platform
"""
import os
import sys
import shutil
from pathlib import Path


def check_environment():
    """Check if environment is properly configured."""
    print("=== Verificando configuración del entorno ===\n")
    
    issues = []
    
    # Check Python version
    print("1. Verificando versión de Python...")
    if sys.version_info < (3, 8):
        issues.append("❌ Python 3.8+ requerido")
    else:
        print(f"✓ Python {sys.version.split()[0]}")
    
    # Check .env file
    print("\n2. Verificando archivo .env...")
    env_path = Path("../.env")
    if not env_path.exists():
        print("❌ Archivo .env no encontrado")
        
        # Try to copy from .env.dev
        env_dev_path = Path("../.env.dev")
        if env_dev_path.exists():
            print("   Copiando .env.dev a .env...")
            shutil.copy(env_dev_path, env_path)
            print("   ✓ .env creado desde .env.dev")
            print("   ⚠️  Recuerda actualizar las variables de entorno!")
        else:
            issues.append("❌ No se encontró .env ni .env.dev")
    else:
        print("✓ Archivo .env encontrado")
        
        # Check required variables
        with open(env_path, 'r') as f:
            env_content = f.read()
            
        required_vars = [
            "OPENAI_API_KEY",
            "TELEGRAM_BOT_TOKEN",
            "DATABASE_URL",
            "REDIS_URL",
            "CHROMA_HOST"
        ]
        
        print("\n3. Verificando variables requeridas...")
        for var in required_vars:
            if var in env_content:
                # Check if it's not a placeholder
                if "your-" in env_content or var + "=" + var.lower() in env_content:
                    print(f"   ⚠️  {var} parece ser un placeholder")
                else:
                    print(f"   ✓ {var} configurado")
            else:
                issues.append(f"❌ {var} no encontrado en .env")
    
    # Check directories
    print("\n4. Verificando estructura de directorios...")
    required_dirs = [
        "api",
        "telegram_bot", 
        "data_processor",
        "database",
        "config",
        "data/raw",
        "data/processed",
        "test_scripts/output"
    ]
    
    for dir_path in required_dirs:
        full_path = Path(f"../{dir_path}")
        if full_path.exists():
            print(f"   ✓ {dir_path}")
        else:
            print(f"   ❌ {dir_path} no encontrado")
            if "output" in dir_path:
                os.makedirs(full_path, exist_ok=True)
                print(f"      ✓ Creado {dir_path}")
    
    # Check data files
    print("\n5. Verificando archivos de datos...")
    data_files = [
        "data/raw/desayunos.docx",
        "data/raw/almuerzoscena.docx",
        "data/processed/recipes.json"
    ]
    
    for file_path in data_files:
        full_path = Path(f"../{file_path}")
        if full_path.exists():
            print(f"   ✓ {file_path}")
        else:
            print(f"   ⚠️  {file_path} no encontrado")
            if "processed" in file_path:
                print("      Ejecuta: python -m data_processor.main")
    
    return issues


def create_sample_env():
    """Create a sample .env file with instructions."""
    sample_env = """# Sistema Mayra - Environment Configuration
# =========================================

# IMPORTANTE: Actualiza estos valores con tus credenciales reales

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# Telegram Bot Configuration  
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nutrition_db
REDIS_URL=redis://localhost:6379
CHROMA_HOST=localhost
CHROMA_PORT=8000

# API Configuration
API_BASE_URL=http://localhost:8000
API_KEY=test-api-key
SECRET_KEY=your-secret-key-at-least-32-chars

# Environment
ENVIRONMENT=development
DEBUG=true
"""
    
    with open("../.env.sample", "w") as f:
        f.write(sample_env)
    
    print("\n✓ Archivo .env.sample creado con configuración de ejemplo")


def print_setup_instructions():
    """Print setup instructions."""
    print("\n" + "="*60)
    print("INSTRUCCIONES DE CONFIGURACIÓN")
    print("="*60)
    
    print("\n1. CONFIGURAR VARIABLES DE ENTORNO:")
    print("   - Edita el archivo .env con tus credenciales")
    print("   - OPENAI_API_KEY: Obtener de https://platform.openai.com/api-keys")
    print("   - TELEGRAM_BOT_TOKEN: Crear bot con @BotFather en Telegram")
    
    print("\n2. INICIAR SERVICIOS DE BASE DE DATOS:")
    print("   docker-compose up -d postgres redis chromadb")
    
    print("\n3. CONFIGURAR BASE DE DATOS:")
    print("   alembic upgrade head")
    print("   python -m database.seeders.main --mode=all")
    
    print("\n4. PROCESAR RECETAS:")
    print("   python -m data_processor.main")
    
    print("\n5. INICIAR SERVICIOS:")
    print("   # Terminal 1 - API")
    print("   uvicorn api.main:app --reload")
    print("   ")
    print("   # Terminal 2 - Bot (opcional)")
    print("   python -m telegram_bot.main")
    
    print("\n6. EJECUTAR TESTS:")
    print("   cd test_scripts")
    print("   python run_all_tests.py")
    
    print("\nOPCIONES DE TEST:")
    print("   python run_all_tests.py          # Todos los tests")
    print("   python run_all_tests.py --quick  # Test rápido")
    print("   python run_all_tests.py --motor1 # Solo Motor 1")
    print("   python run_all_tests.py --motor2 # Solo Motor 2")
    print("   python run_all_tests.py --motor3 # Solo Motor 3")


def main():
    """Main setup function."""
    print("Sistema Mayra - Configuración del Entorno de Pruebas")
    print("="*60 + "\n")
    
    # Check environment
    issues = check_environment()
    
    # Create sample env if needed
    if not Path("../.env").exists():
        create_sample_env()
    
    # Print summary
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    if issues:
        print("\n⚠️  Se encontraron los siguientes problemas:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ El entorno está correctamente configurado!")
    
    # Print instructions
    print_setup_instructions()


if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()