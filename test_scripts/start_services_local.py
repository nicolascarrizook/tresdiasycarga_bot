#!/usr/bin/env python3
"""
Start services locally without Docker
Sistema Mayra - Nutrition AI Platform
"""
import os
import sys
import subprocess
import time
from pathlib import Path


def check_service(service_name, check_command):
    """Check if a service is running."""
    try:
        result = subprocess.run(check_command, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False


def start_postgresql():
    """Check/start PostgreSQL."""
    print("1. Verificando PostgreSQL...")
    
    if check_service("PostgreSQL", "pg_isready"):
        print("   ✓ PostgreSQL está ejecutándose")
        return True
    
    print("   ❌ PostgreSQL no está ejecutándose")
    print("   Intenta: brew services start postgresql@15")
    return False


def start_redis():
    """Check/start Redis."""
    print("\n2. Verificando Redis...")
    
    if check_service("Redis", "redis-cli ping"):
        print("   ✓ Redis está ejecutándose")
        return True
    
    print("   ❌ Redis no está ejecutándose")
    print("   Intenta: brew services start redis")
    return False


def setup_chromadb():
    """Setup ChromaDB in local mode."""
    print("\n3. Configurando ChromaDB...")
    
    # Create directory for ChromaDB
    chroma_dir = Path("./chroma_db_dev")
    chroma_dir.mkdir(exist_ok=True)
    
    print("   ✓ ChromaDB configurado en modo local")
    print(f"   Directorio: {chroma_dir.absolute()}")
    return True


def create_database():
    """Create database if it doesn't exist."""
    print("\n4. Verificando base de datos...")
    
    # Check if database exists
    check_db = subprocess.run(
        "psql -U postgres -lqt | cut -d \\| -f 1 | grep -qw nutrition_db_dev",
        shell=True,
        capture_output=True
    )
    
    if check_db.returncode == 0:
        print("   ✓ Base de datos 'nutrition_db_dev' existe")
    else:
        print("   Creando base de datos 'nutrition_db_dev'...")
        create_result = subprocess.run(
            "createdb -U postgres nutrition_db_dev",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if create_result.returncode == 0:
            print("   ✓ Base de datos creada exitosamente")
        else:
            print("   ❌ Error creando base de datos")
            print(f"   {create_result.stderr}")
            return False
    
    return True


def update_env_for_local():
    """Update .env for local development without Docker."""
    print("\n5. Actualizando configuración para modo local...")
    
    env_updates = {
        "DATABASE_URL": "postgresql://localhost:5432/nutrition_db_dev",
        "REDIS_URL": "redis://localhost:6379",
        "CHROMA_PERSIST_DIRECTORY": "./chroma_db_dev",
        "CHROMA_HOST": "localhost",
        "CHROMA_PORT": "8000"
    }
    
    # Read current .env
    env_path = Path("../.env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update lines
        updated_lines = []
        for line in lines:
            updated = False
            for key, value in env_updates.items():
                if line.startswith(f"{key}="):
                    updated_lines.append(f"{key}={value}\n")
                    updated = True
                    break
            if not updated:
                updated_lines.append(line)
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        print("   ✓ Archivo .env actualizado para modo local")
    
    return True


def main():
    """Main function to setup local services."""
    print("Sistema Mayra - Configuración de Servicios Locales")
    print("=" * 60)
    print("\nEste script configura los servicios sin Docker\n")
    
    all_good = True
    
    # Check services
    if not start_postgresql():
        all_good = False
    
    if not start_redis():
        all_good = False
    
    setup_chromadb()
    
    if all_good:
        create_database()
        update_env_for_local()
    
    print("\n" + "=" * 60)
    
    if all_good:
        print("✅ Servicios configurados correctamente!")
        print("\nPróximos pasos:")
        print("1. Ejecutar migraciones: alembic upgrade head")
        print("2. Cargar datos: python -m database.seeders.main --mode=all")
        print("3. Procesar recetas: python -m data_processor.main")
        print("4. Iniciar API: uvicorn api.main:app --reload")
    else:
        print("⚠️  Algunos servicios requieren instalación manual")
        print("\nInstalar servicios faltantes:")
        print("- PostgreSQL: brew install postgresql@15")
        print("- Redis: brew install redis")
        print("\nIniciar servicios:")
        print("- brew services start postgresql@15")
        print("- brew services start redis")


if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()