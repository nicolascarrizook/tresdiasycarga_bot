#!/usr/bin/env python3
"""
Test completo de los 3 motores - Sin dependencias del proyecto
Sistema Mayra - Nutrition AI Platform
"""
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sistema de prompts unificado
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

MOTOR_2_PROMPT = """MOTOR 2: CONTROL Y AJUSTES

Generá plan de control ajustado siguiendo el método Tres Días y Carga. El paciente ya tiene plan activo.

DATOS ACTUALES DEL PACIENTE:
Nombre: {nombre}
Peso anterior: {peso} kg → Peso actual: {peso_actual} kg
Restricciones: {restricciones}
Preferencias: {preferencias}
Nivel económico: {nivel_economico}

CONTROL ACTUAL:
Fecha control: {fecha_control}
Peso actual: {peso_actual} kg
Objetivo actualizado: {objetivo_actualizado}
Actividad actual: {actividad_actual}
Cambios entrenamiento: {cambios_entrenamiento}
Suplementación actual: {suplementacion_actual}
Patologías actuales: {patologias_actuales}
Restricciones actuales: {restricciones_actuales}
Preferencias actuales: {preferencias_actuales}
Horarios actuales: {horarios_actuales}
Nivel económico actual: {nivel_economico_actual}
Notas del control: {notas_control}

INSTRUCCIONES DE AJUSTE:
AGREGAR: {agregar}
SACAR: {sacar}
DEJAR: {dejar}

GENERAR:
1. Análisis breve del progreso
2. Plan actualizado de 3 días iguales
3. Ajustes según instrucciones AGREGAR/SACAR/DEJAR
4. Mantener método Tres Días y Carga

ESTRUCTURA IDÉNTICA AL MOTOR 1 pero con ajustes solicitados."""

MOTOR_3_PROMPT = """MOTOR 3: REEMPLAZO PUNTUAL

SOLICITUD DE REEMPLAZO:
Comida a reemplazar: {comida_reemplazar}
Nueva comida: {comida_nueva}
Condiciones: {condiciones_especiales}
Macros originales: {macros_originales}

DATOS DEL PACIENTE:
Nombre: {nombre}
Restricciones: {restricciones}
Preferencias: {preferencias}
Nivel económico: {nivel_economico}
Tipo de peso: {tipo_peso}

GENERAR:
1. Analizar macros de comida original
2. Ajustar nueva comida para mantener equivalencia (±5%)
3. Detallar preparación completa
4. Comparar macros original vs nueva

FORMATO:
## REEMPLAZO SOLICITADO

**COMIDA ORIGINAL:**
{comida_reemplazar}
{macros_originales}

**NUEVA COMIDA:**
[Nombre de la nueva comida]
- Ingredientes con gramos exactos
- Preparación paso a paso
- Macros: Calorías, Proteínas, Carbohidratos, Grasas

**COMPARACIÓN:**
- Diferencia calórica: X%
- Diferencia proteínas: X%
- Diferencia carbohidratos: X%
- Diferencia grasas: X%

✓ Reemplazo equivalente y apto para el paciente"""


def test_motor_1():
    """Test Motor 1 - Paciente Nuevo."""
    print("\n=== TEST MOTOR 1: PACIENTE NUEVO ===\n")
    
    # Verificar API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or "your-" in api_key:
        print("❌ ERROR: OPENAI_API_KEY no está configurada en .env")
        return False
    
    # Cliente OpenAI
    client = OpenAI(api_key=api_key)
    
    # Datos del paciente
    patient_data = {
        "nombre": "Juan Carlos Pérez",
        "edad": 35,
        "sexo": "masculino",
        "estatura": 175,
        "peso": 80,
        "objetivo": "bajar 0.5kg por semana",
        "actividad_fisica": "pesas",
        "frecuencia_semanal": "4 veces por semana",
        "duracion_sesion": 60,
        "tipo_entrenamiento": "fuerza e hipertrofia",
        "suplementacion": "Creatina 5g diarios",
        "patologias": "Ninguna",
        "restricciones": "gluten",
        "preferencias": "pollo, pescado, verduras verdes, frutos secos",
        "horarios": "Desayuno 7:00, Almuerzo 13:00, Merienda 17:00, Cena 21:00",
        "nivel_economico": "medio",
        "notas_personales": "Prefiere comidas simples de preparar",
        "tipo_peso": "crudo",
        "comidas_principales": 4,
        "tipo_colaciones": "Sin colaciones"
    }
    
    # Contexto de recetas
    rag_context = """
- Tostadas con palta y tomate [desayuno]: 2 rebanadas de pan sin gluten (50gr) + 1/2 palta (60gr) + tomate a gusto + infusión
- Yogur con frutas [desayuno]: 200ml yogur natural + 80gr frutas mixtas + 1 cdita miel + 1 cdita semillas
- Revuelto de huevos con vegetales [desayuno]: 2 huevos + vegetales mixtos + 1 cdita aceite + pan sin gluten (30gr)
- Pollo grillado con ensalada [almuerzo]: 150gr pechuga pollo + ensalada mixta + 50gr arroz integral + 1 cda aceite oliva
- Pescado con quinoa [almuerzo]: 150gr pescado blanco + 60gr quinoa cocida + vegetales + 1 cda aceite
- Ensalada completa con atún [almuerzo]: 150gr atún + hojas verdes + 50gr garbanzos + vegetales + 1 cda aceite
- Salmón con vegetales [cena]: 150gr salmón + vegetales al vapor + 50gr batata + especias
- Pollo al horno con papas [cena]: 150gr pollo + 100gr papas + ensalada verde + 1 cda aceite
- Fruta con frutos secos [colación]: 1 manzana mediana (150gr) + 20gr almendras
- Batido proteico [merienda]: 200ml leche + 1 banana + 30gr avena sin gluten + 1 cdita miel
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
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
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
        os.makedirs("test_scripts/output", exist_ok=True)
        filename = f"test_scripts/output/all_motors_motor1_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("TEST MOTOR 1 - PACIENTE NUEVO\n")
            f.write("="*50 + "\n")
            f.write(f"Paciente: {patient_data['nombre']}\n")
            f.write(f"Objetivo: {patient_data['objetivo']}\n")
            f.write(f"Restricción: Sin {patient_data['restricciones']}\n")
            f.write(f"Generado: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(result)
        
        print(f"\n✓ Plan generado exitosamente!")
        print(f"✓ Guardado en: {filename}")
        print(f"✓ Tokens usados: {response.usage.total_tokens}")
        
        # Mostrar preview
        print("\nPrimeras líneas del plan:")
        print("-" * 50)
        lines = result.split('\n')[:10]
        for line in lines:
            print(line)
        print("...\n")
        
        return True, timestamp
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False, None


def test_motor_2(timestamp):
    """Test Motor 2 - Control y Ajustes."""
    print("\n=== TEST MOTOR 2: CONTROL Y AJUSTES ===\n")
    
    # Cliente OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Datos del control
    control_data = {
        "nombre": "Juan Carlos Pérez",
        "peso": 80,
        "peso_actual": 79.2,
        "restricciones": "gluten",
        "preferencias": "pollo, pescado, verduras verdes, frutos secos",
        "nivel_economico": "medio",
        "fecha_control": datetime.now().strftime("%Y-%m-%d"),
        "objetivo_actualizado": "bajar 0.5kg por semana",
        "actividad_actual": "pesas + cardio",
        "cambios_entrenamiento": "Agregó 30 min de cardio los sábados",
        "suplementacion_actual": "Creatina 5g + Omega 3",
        "patologias_actuales": "Ninguna",
        "restricciones_actuales": "gluten",
        "preferencias_actuales": "pollo, pescado, verduras, huevos",
        "horarios_actuales": "Desayuno 7:00, Almuerzo 13:00, Merienda 17:00, Cena 21:00",
        "nivel_economico_actual": "medio",
        "notas_control": "Buena adherencia, solicita más variedad en desayunos",
        "agregar": "Más opciones de desayuno con huevos",
        "sacar": "Reducir frutos secos (le caen pesados)",
        "dejar": "Mantener estructura de 4 comidas sin gluten",
        "tipo_peso": "crudo"
    }
    
    # Mismo contexto RAG
    rag_context = """
- Tostadas con palta y tomate [desayuno]: 2 rebanadas de pan sin gluten (50gr) + 1/2 palta (60gr) + tomate a gusto + infusión
- Yogur con frutas [desayuno]: 200ml yogur natural + 80gr frutas mixtas + 1 cdita miel + 1 cdita semillas
- Revuelto de huevos con vegetales [desayuno]: 2 huevos + vegetales mixtos + 1 cdita aceite + pan sin gluten (30gr)
- Tortilla de vegetales [desayuno]: 2 huevos + espinaca + tomate + 1 cdita aceite + pan sin gluten (30gr)
- Pollo grillado con ensalada [almuerzo]: 150gr pechuga pollo + ensalada mixta + 50gr arroz integral + 1 cda aceite oliva
- Pescado con quinoa [almuerzo]: 150gr pescado blanco + 60gr quinoa cocida + vegetales + 1 cda aceite
- Ensalada completa con atún [almuerzo]: 150gr atún + hojas verdes + 50gr garbanzos + vegetales + 1 cda aceite
- Salmón con vegetales [cena]: 150gr salmón + vegetales al vapor + 50gr batata + especias
- Pollo al horno con papas [cena]: 150gr pollo + 100gr papas + ensalada verde + 1 cda aceite
- Batido proteico [merienda]: 200ml leche + 1 banana + 30gr avena sin gluten + 1 cdita miel
"""
    
    # Formatear prompts
    system_prompt = BASE_SYSTEM_PROMPT.format(
        tipo_peso=control_data["tipo_peso"],
        rag_context=rag_context
    )
    
    user_prompt = MOTOR_2_PROMPT.format(**control_data)
    
    print(f"Generando plan de control para: {control_data['nombre']}")
    print(f"Peso anterior: {control_data['peso']} kg → Actual: {control_data['peso_actual']} kg")
    print(f"AGREGAR: {control_data['agregar']}")
    print(f"SACAR: {control_data['sacar']}")
    print(f"DEJAR: {control_data['dejar']}")
    print("\nEsperando respuesta de OpenAI...")
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content
        filename = f"test_scripts/output/all_motors_motor2_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("TEST MOTOR 2 - CONTROL Y AJUSTES\n")
            f.write("="*50 + "\n")
            f.write(f"Paciente: {control_data['nombre']}\n")
            f.write(f"Peso anterior: {control_data['peso']} kg → Actual: {control_data['peso_actual']} kg\n")
            f.write(f"AGREGAR: {control_data['agregar']}\n")
            f.write(f"SACAR: {control_data['sacar']}\n")
            f.write(f"DEJAR: {control_data['dejar']}\n")
            f.write(f"Generado: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(result)
        
        print(f"\n✓ Plan de control generado!")
        print(f"✓ Guardado en: {filename}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def test_motor_3(timestamp):
    """Test Motor 3 - Reemplazo."""
    print("\n=== TEST MOTOR 3: REEMPLAZO DE COMIDA ===\n")
    
    # Cliente OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Datos del reemplazo
    replacement_data = {
        "nombre": "Juan Carlos Pérez",
        "restricciones": "gluten",
        "preferencias": "pescado, vegetales",
        "nivel_economico": "medio",
        "tipo_peso": "crudo",
        "comida_reemplazar": "Pollo grillado con ensalada: 150gr pechuga pollo + ensalada mixta + 50gr arroz integral + 1 cda aceite oliva",
        "comida_nueva": "Salmón con vegetales al horno",
        "condiciones_especiales": "Mantener sin gluten, el paciente quiere variar proteínas",
        "macros_originales": "Calorías: 450, Proteínas: 45g, Carbohidratos: 50g, Grasas: 12g"
    }
    
    # Contexto RAG para reemplazos
    rag_context = """
- Salmón con vegetales [cena]: 150gr salmón + vegetales al vapor + 50gr batata + especias
- Pescado con quinoa [almuerzo]: 150gr pescado blanco + 60gr quinoa cocida + vegetales + 1 cda aceite
- Atún con arroz [almuerzo]: 150gr atún + 50gr arroz integral + ensalada + 1 cda aceite
"""
    
    # Formatear prompts
    system_prompt = BASE_SYSTEM_PROMPT.format(
        tipo_peso=replacement_data["tipo_peso"],
        rag_context=rag_context
    )
    
    user_prompt = MOTOR_3_PROMPT.format(**replacement_data)
    
    print(f"Generando reemplazo:")
    print(f"Original: {replacement_data['comida_reemplazar'].split(':')[0]}")
    print(f"Nueva: {replacement_data['comida_nueva']}")
    print(f"Condición: {replacement_data['condiciones_especiales']}")
    print("\nEsperando respuesta de OpenAI...")
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        filename = f"test_scripts/output/all_motors_motor3_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("TEST MOTOR 3 - REEMPLAZO\n")
            f.write("="*50 + "\n")
            f.write(f"Original: {replacement_data['comida_reemplazar']}\n")
            f.write(f"Nueva: {replacement_data['comida_nueva']}\n")
            f.write(f"Condición: {replacement_data['condiciones_especiales']}\n")
            f.write(f"Generado: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(result)
        
        print(f"\n✓ Reemplazo generado!")
        print(f"✓ Guardado en: {filename}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def main():
    """Run all motor tests."""
    print("\n🚀 TEST COMPLETO DE LOS 3 MOTORES")
    print("="*60)
    print("Sistema Mayra - Prueba del sistema unificado de prompts")
    print("Este script prueba los 3 motores sin dependencias del proyecto\n")
    
    # Verificar API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or "your-" in api_key:
        print("❌ ERROR: OPENAI_API_KEY no está configurada en .env")
        return
    
    print("✓ API Key detectada")
    print(f"✓ Modelo: {os.getenv('OPENAI_MODEL', 'gpt-4')}\n")
    
    # Test Motor 1
    success1, timestamp = test_motor_1()
    if not success1:
        print("\n❌ Motor 1 falló. Abortando tests.")
        return
    
    # Test Motor 2
    success2 = test_motor_2(timestamp)
    
    # Test Motor 3
    success3 = test_motor_3(timestamp)
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"✓ Motor 1 - Paciente Nuevo: {'✅' if success1 else '❌'}")
    print(f"✓ Motor 2 - Control: {'✅' if success2 else '❌'}")
    print(f"✓ Motor 3 - Reemplazo: {'✅' if success3 else '❌'}")
    
    if all([success1, success2, success3]):
        print("\n✅ TODOS LOS MOTORES FUNCIONAN CORRECTAMENTE!")
        print(f"\nResultados guardados en: test_scripts/output/")
        print(f"- Motor 1: all_motors_motor1_{timestamp}.txt")
        print(f"- Motor 2: all_motors_motor2_{timestamp}.txt")
        print(f"- Motor 3: all_motors_motor3_{timestamp}.txt")
        print("\nEl sistema de prompts unificado está listo para producción! 🎉")
    else:
        print("\n❌ Algunos motores fallaron. Revisa los errores arriba.")


if __name__ == "__main__":
    main()