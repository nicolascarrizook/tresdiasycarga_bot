#!/usr/bin/env python3
"""
Test standalone - Prueba los prompts sin dependencias del proyecto
Sistema Mayra - Nutrition AI Platform
"""
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Prompts del sistema
BASE_SYSTEM_PROMPT = """Eres Mayra, nutricionista experta que genera planes alimentarios usando el método "Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva".

IDENTIDAD:
- Usás léxico argentino exclusivamente (palta, no aguacate)
- Sos precisa con cantidades y preparaciones
- Seguís las reglas del método sin excepciones

REGLAS FUNDAMENTALES DEL MÉTODO:
✓ Plan de 3 días iguales en calorías y macronutrientes
✓ Todas las comidas en gramos {tipo_peso}
✓ Papa, batata y choclo: SIEMPRE en gramos exactos
✓ Verduras no tipo C: libres (porción visual coherente)
✓ Frutas: SIEMPRE en gramos exactos
✓ Incluir preparación detallada de cada comida
✓ No usar suplementos si no están indicados
✓ Calcular desde: https://www.calculator.net/calorie-calculator.html

CONTEXTO DE RECETAS DISPONIBLES:
{rag_context}

ADAPTACIONES AUTOMÁTICAS:
- Nivel económico → Seleccionar ingredientes apropiados
- Patologías → Ajustar automáticamente sin mencionar
- Restricciones → Evitar completamente los alimentos indicados
- Preferencias → Priorizar alimentos que le gustan

FORMATO DE RESPUESTA:
- Título del plan con datos del paciente
- Plan organizado por días y comidas
- 3 opciones equivalentes por comida (±5% calorías)
- Preparación paso a paso para cada opción
- Total calórico y macros del día"""

MOTOR_1_PROMPT = """MOTOR 1: PACIENTE NUEVO

Generá un plan alimentario de 3 días iguales siguiendo el método Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva.

DATOS DEL PACIENTE:
Nombre: {nombre}
Edad: {edad}
Sexo: {sexo}
Estatura: {estatura} cm
Peso: {peso} kg
Objetivo: {objetivo}
Actividad física: {actividad_fisica}
Frecuencia: {frecuencia_semanal}
Duración: {duracion_sesion} minutos
Tipo de entrenamiento: {tipo_entrenamiento}
Suplementación: {suplementacion}
Patologías/Medicación: {patologias}
NO consume: {restricciones}
Le gusta: {preferencias}
Horarios: {horarios}
Nivel económico: {nivel_economico}
Notas: {notas_personales}

CONFIGURACIÓN DEL PLAN:
Tipo de peso: {tipo_peso}
Comidas principales: {comidas_principales}
Colaciones: {tipo_colaciones}

ESPECIFICACIONES:
- {comidas_principales} comidas principales
- 3 opciones por cada comida (equivalentes ±5%)
- Colaciones: {tipo_colaciones}
- Preparación incluida para cada opción
- Usar ingredientes del contexto RAG proporcionado

ESTRUCTURA DE RESPUESTA:
# PLAN NUTRICIONAL - {nombre}
## Objetivo: {objetivo}

### DÍA 1, 2 y 3 (IGUALES)

**DESAYUNO** (XXX kcal)
Opción 1: [Receta detallada con gramos exactos]
Preparación: [Paso a paso]

Opción 2: [Receta equivalente]
Preparación: [Paso a paso]

Opción 3: [Receta equivalente]
Preparación: [Paso a paso]

[Repetir para cada comida]

**TOTALES DEL DÍA:**
- Calorías: XXX kcal
- Proteínas: XX g
- Carbohidratos: XX g  
- Grasas: XX g"""


def test_motor_1():
    """Test Motor 1 sin dependencias."""
    print("\n=== TEST MOTOR 1: PACIENTE NUEVO (Standalone) ===\n")
    
    # Verificar API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or "your-" in api_key:
        print("❌ ERROR: OPENAI_API_KEY no está configurada en .env")
        return False
    
    # Cliente OpenAI
    client = OpenAI(api_key=api_key)
    
    # Datos del paciente
    patient_data = {
        "nombre": "María González",
        "edad": 28,
        "sexo": "femenino",
        "estatura": 165,
        "peso": 65,
        "objetivo": "mantenimiento",
        "actividad_fisica": "cardio y yoga",
        "frecuencia_semanal": "3 veces por semana",
        "duracion_sesion": 45,
        "tipo_entrenamiento": "cardio moderado y flexibilidad",
        "suplementacion": "Ninguna",
        "patologias": "Hipotiroidismo controlado",
        "restricciones": "lácteos",
        "preferencias": "ensaladas, frutas, pescado, quinoa",
        "horarios": "Desayuno 8:00, Almuerzo 13:00, Cena 20:00",
        "nivel_economico": "medio",
        "notas_personales": "Vegetariana flexible, come pescado ocasionalmente",
        "tipo_peso": "crudo",
        "comidas_principales": 3,
        "tipo_colaciones": "1 colación a media mañana"
    }
    
    # Contexto de recetas (simplificado)
    rag_context = """
- Tostadas con palta y tomate [desayuno]: 2 rebanadas de pan integral (50gr) + 1/2 palta (60gr) + tomate a gusto + infusión
- Yogur con frutas [desayuno]: 200ml yogur natural + 80gr frutas mixtas + 1 cdita miel + 1 cdita semillas
- Ensalada completa con quinoa [almuerzo]: 60gr quinoa cocida + verduras mixtas + 100gr pescado blanco + 1 cda aceite oliva
- Salmón con vegetales [cena]: 120gr salmón + vegetales al vapor + 50gr batata + especias
- Fruta con frutos secos [colación]: 1 manzana mediana (150gr) + 20gr almendras
"""
    
    # Formatear prompts
    system_prompt = BASE_SYSTEM_PROMPT.format(
        tipo_peso=patient_data["tipo_peso"],
        rag_context=rag_context
    )
    
    user_prompt = MOTOR_1_PROMPT.format(**patient_data)
    
    print(f"Generando plan para: {patient_data['nombre']}")
    print(f"Objetivo: {patient_data['objetivo']}")
    print(f"Restricción: Sin {patient_data['restricciones']}")
    print("\nEsperando respuesta de OpenAI...")
    
    try:
        # Llamar a OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content
        
        # Guardar resultado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_scripts/output/standalone_motor1_{timestamp}.txt"
        
        os.makedirs("test_scripts/output", exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("TEST STANDALONE MOTOR 1\n")
            f.write("="*50 + "\n")
            f.write(f"Paciente: {patient_data['nombre']}\n")
            f.write(f"Generado: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(result)
        
        print(f"\n✓ Plan generado exitosamente!")
        print(f"✓ Guardado en: {filename}")
        print(f"✓ Tokens usados: {response.usage.total_tokens}")
        
        # Mostrar preview
        print("\nPrimeras líneas del plan:")
        print("-" * 50)
        lines = result.split('\n')[:15]
        for line in lines:
            print(line)
        print("...\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        if "api_key" in str(e).lower():
            print("\n⚠️  Verifica tu OPENAI_API_KEY en el archivo .env")
        return False


def main():
    """Run standalone test."""
    print("\n🚀 TEST STANDALONE - SIN DEPENDENCIAS")
    print("="*60)
    print("Este script prueba Motor 1 sin necesitar:")
    print("- Base de datos")
    print("- Importaciones del proyecto")
    print("- Servicios externos (excepto OpenAI)")
    print("\nSolo necesitas OPENAI_API_KEY en tu .env")
    
    success = test_motor_1()
    
    if success:
        print("\n✅ Test completado exitosamente!")
        print("\nPróximos pasos:")
        print("1. Revisa el plan generado en test_scripts/output/")
        print("2. Si funciona bien, puedes probar los otros motores")
        print("3. O configurar PostgreSQL para pruebas completas")
    else:
        print("\n❌ Test falló")
        print("\nVerifica:")
        print("1. Que tengas OPENAI_API_KEY configurada en .env")
        print("2. Que la API key sea válida y tenga créditos")
        print("3. Que tengas acceso a GPT-4")


if __name__ == "__main__":
    main()