# Scripts de Prueba - Sistema Mayra

Este directorio contiene scripts de prueba para los tres motores del Sistema Mayra de generación de planes nutricionales.

## 📋 Contenido

- `test_motor_1_new_patient.py` - Prueba Motor 1: Generación de plan para paciente nuevo
- `test_motor_2_control.py` - Prueba Motor 2: Control y ajustes de plan existente  
- `test_motor_3_replacement.py` - Prueba Motor 3: Reemplazo de comidas específicas
- `run_all_tests.py` - Ejecutor principal de todas las pruebas
- `setup_test_env.py` - Script de configuración del entorno

## 🚀 Inicio Rápido

### 1. Configurar el entorno

```bash
cd test_scripts
python setup_test_env.py
```

Este script verificará:
- ✅ Versión de Python (3.8+)
- ✅ Archivo .env configurado
- ✅ Estructura de directorios
- ✅ Archivos de datos necesarios

### 2. Configurar variables de entorno

Edita el archivo `.env` en la raíz del proyecto:

```env
# Requerido
OPENAI_API_KEY=sk-tu-clave-api-openai
TELEGRAM_BOT_TOKEN=tu-token-bot-telegram

# Base de datos
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nutrition_db
REDIS_URL=redis://localhost:6379
CHROMA_HOST=localhost
```

### 3. Iniciar servicios

```bash
# Bases de datos con Docker
docker-compose up -d postgres redis chromadb

# Migraciones
alembic upgrade head

# Cargar datos semilla
python -m database.seeders.main --mode=all

# Procesar recetas
python -m data_processor.main
```

### 4. Iniciar API

```bash
# En una terminal
uvicorn api.main:app --reload
```

## 🧪 Ejecutar Pruebas

### Todas las pruebas
```bash
python run_all_tests.py
```

### Pruebas individuales
```bash
# Test rápido del sistema
python run_all_tests.py --quick

# Motor 1 - Paciente nuevo
python run_all_tests.py --motor1

# Motor 2 - Control
python run_all_tests.py --motor2  

# Motor 3 - Reemplazo
python run_all_tests.py --motor3
```

### Ejecutar directamente
```bash
# Motor 1
python test_motor_1_new_patient.py

# Motor 2
python test_motor_2_control.py

# Motor 3
python test_motor_3_replacement.py
```

## 📊 Resultados

Los resultados se guardan en `test_scripts/output/`:
- `plan_motor1_*.txt` - Planes generados para pacientes nuevos
- `plan_motor2_*.txt` - Planes de control ajustados
- `plan_motor3_*.txt` - Reemplazos de comidas
- `test_summary_*.txt` - Resumen de ejecución de pruebas

## 🔧 Casos de Prueba

### Motor 1 - Paciente Nuevo
- **Paciente**: Juan Carlos Pérez, 35 años
- **Objetivo**: Bajar 0.5kg por semana
- **Actividad**: Pesas 4x semana
- **Restricción**: Sin gluten
- **Preferencias**: Comidas simples y rápidas

### Motor 2 - Control y Ajustes
- **Escenario**: Paciente después de 2 semanas
- **Peso**: -0.8 kg (progreso adecuado)
- **Ajustes**: 
  - AGREGAR: Más opciones de desayuno con huevos
  - SACAR: Reducir frutos secos
  - DEJAR: Estructura de 4 comidas sin gluten

### Motor 3 - Reemplazo Puntual
- **Comida original**: Pollo grillado con ensalada (450 kcal)
- **Reemplazo**: Salmón con vegetales al horno
- **Condición**: Mantener macros equivalentes (±5%)
- **Restricción**: Sin gluten

## 🐛 Solución de Problemas

### Error: "Connection refused"
- Verifica que la API esté ejecutándose: `curl http://localhost:8000/health`
- Confirma el puerto en `.env`: `API_PORT=8000`

### Error: "Invalid API key"
- Verifica `OPENAI_API_KEY` en `.env`
- Asegúrate de tener créditos en tu cuenta OpenAI

### Error: "Timeout"
- La generación con GPT-4 puede tomar 30-60 segundos
- Aumenta el timeout en los scripts si es necesario

### Error: "ChromaDB not found"
- Ejecuta: `docker-compose up -d chromadb`
- Procesa las recetas: `python -m data_processor.main`

## 📝 Notas

- Los tests usan la API REST, no acceso directo a servicios
- Cada test crea datos de prueba independientes
- Los planes generados siguen el método "Tres Días y Carga"
- Se respetan todas las restricciones y preferencias del paciente

## 🤝 Contribuir

Para agregar nuevos casos de prueba:

1. Crea un nuevo archivo `test_motor_X_caso.py`
2. Importa las funciones necesarias
3. Define los datos del caso de prueba
4. Implementa la lógica de prueba
5. Agrega al `run_all_tests.py` si es necesario

## 📚 Referencias

- [Documentación API](../docs/api/README.md)
- [Guía de Prompts](../config/prompts.py)
- [Arquitectura del Sistema](../docs/architecture/system_design.md)