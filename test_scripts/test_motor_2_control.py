#!/usr/bin/env python3
"""
Test script for Motor 2 - Control Plan (Adjustments)
Sistema Mayra - Nutrition AI Platform
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

import httpx
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "test-api-key")


async def test_motor_2_control():
    """Test Motor 2: Control plan with adjustments."""
    
    print("=== Test Motor 2: Control y Ajustes ===\n")
    
    # Simulate existing patient data
    patient_id = 1  # Assume patient exists from Motor 1 test
    
    # Control data - patient after 2 weeks
    control_data = {
        "control_date": datetime.now().strftime("%Y-%m-%d"),
        "previous_weight": 80.0,
        "current_weight": 79.2,  # Lost 0.8 kg
        "updated_objective": "bajar_0.5kg",  # Continue with same objective
        "current_activity": "pesas",
        "training_changes": "Agregó una sesión de cardio los sábados (30 min caminata rápida)",
        "current_supplements": "Creatina 5g diarios + Omega 3",
        "current_pathologies": "Ninguna",
        "current_restrictions": ["gluten"],  # Maintains gluten-free
        "current_preferences": ["pollo", "pescado", "verduras verdes", "frutos secos", "huevos"],
        "current_schedule": "Desayuno 7:00, Almuerzo 13:00, Merienda 17:00, Cena 21:00",
        "current_economic_level": "medio",
        "current_notes": "El paciente reporta buena adherencia al plan. Solicita más variedad en desayunos.",
        
        # Control instructions
        "add_items": "Más opciones de desayuno, incorporar huevos en diferentes preparaciones",
        "remove_items": "Reducir cantidad de frutos secos (le generan pesadez)",
        "keep_items": "Mantener estructura de 4 comidas, continuar sin gluten",
        
        # Progress notes
        "adherence_percentage": 85,
        "energy_level": "bueno",
        "digestion": "normal",
        "satisfaction": "alta",
        "difficulties": "A veces le cuesta preparar la cena por falta de tiempo"
    }
    
    # Plan generation request for control
    plan_request = {
        "patient_id": patient_id,
        "plan_type": "control",
        "control_data": control_data,
        "weight_type": "crudo",
        "main_meals": 4,
        "snacks_type": "Sin colaciones",
        "custom_instructions": "Aumentar variedad en desayunos con opciones con huevo. Reducir frutos secos. Mantener simplicidad en las cenas."
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # First, get patient info
            print("1. Obteniendo información del paciente...")
            patient_response = await client.get(
                f"{API_BASE_URL}/patients/{patient_id}",
                headers={
                    "Authorization": f"Bearer {API_KEY}"
                }
            )
            
            if patient_response.status_code == 200:
                patient = patient_response.json()
                print(f"✓ Paciente: {patient.get('name', 'Juan Carlos Pérez')}")
                print(f"   - Peso anterior: {control_data['previous_weight']} kg")
                print(f"   - Peso actual: {control_data['current_weight']} kg")
                print(f"   - Cambio: -{control_data['previous_weight'] - control_data['current_weight']:.1f} kg")
                print(f"   - Adherencia: {control_data['adherence_percentage']}%")
            else:
                print(f"✗ Error obteniendo paciente: {patient_response.status_code}")
                # Continue anyway for testing
                print("  Continuando con datos de prueba...")
            
            # Generate control plan
            print("\n2. Generando plan de control...")
            print("   - Tipo: CONTROL - AJUSTE COMPLETO")
            print(f"   - AGREGAR: {control_data['add_items']}")
            print(f"   - SACAR: {control_data['remove_items']}")
            print(f"   - DEJAR: {control_data['keep_items']}")
            
            plan_response = await client.post(
                f"{API_BASE_URL}/plans/generate",
                json=plan_request,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            
            if plan_response.status_code == 201:
                result = plan_response.json()
                print("\n✓ Plan de control generado exitosamente!")
                print(f"   - Tiempo de generación: {result.get('generation_time', 'N/A')} segundos")
                print(f"   - Tokens utilizados: {result.get('tokens_used', 'N/A')}")
                print(f"   - Modelo: {result.get('model_used', 'N/A')}")
                
                # Display plan content
                if 'plan' in result and 'ai_generated_content' in result['plan']:
                    print("\n=== PLAN DE CONTROL GENERADO ===")
                    print(result['plan']['ai_generated_content'])
                    
                    # Save to file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"plan_motor2_control_{timestamp}.txt"
                    with open(f"test_scripts/output/{filename}", "w", encoding="utf-8") as f:
                        f.write("PLAN DE CONTROL - AJUSTE COMPLETO\n")
                        f.write(f"Paciente: {patient.get('name', 'Juan Carlos Pérez')}\n")
                        f.write(f"Fecha de control: {control_data['control_date']}\n")
                        f.write(f"Peso anterior: {control_data['previous_weight']} kg\n")
                        f.write(f"Peso actual: {control_data['current_weight']} kg\n")
                        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("="*50 + "\n\n")
                        f.write(result['plan']['ai_generated_content'])
                    
                    print(f"\n✓ Plan guardado en: test_scripts/output/{filename}")
                
            else:
                print(f"\n✗ Error generando plan de control: {plan_response.status_code}")
                print(plan_response.text)
                
        except httpx.TimeoutException:
            print("\n✗ Timeout: La generación del plan tardó demasiado")
        except Exception as e:
            print(f"\n✗ Error inesperado: {str(e)}")


async def test_motor_2_variations():
    """Test different control scenarios."""
    
    print("\n=== Test Motor 2: Variaciones de Control ===\n")
    
    scenarios = [
        {
            "name": "Paciente que no bajó de peso",
            "current_weight": 80.0,  # Same as before
            "add_items": "Aumentar actividad cardiovascular",
            "remove_items": "Reducir porciones de carbohidratos en cena",
            "keep_items": "Mantener proteínas y estructura general"
        },
        {
            "name": "Paciente que bajó mucho peso",
            "current_weight": 77.5,  # Lost 2.5 kg (too much)
            "add_items": "Aumentar calorías con colaciones saludables",
            "remove_items": "Nada",
            "keep_items": "Todo el plan actual pero con porciones mayores"
        },
        {
            "name": "Paciente con nuevo objetivo",
            "current_weight": 79.0,
            "updated_objective": "ganancia_muscular",
            "add_items": "Incrementar proteínas post-entrenamiento",
            "remove_items": "Restricción calórica",
            "keep_items": "Estructura de comidas y horarios"
        }
    ]
    
    for scenario in scenarios:
        print(f"\nEscenario: {scenario['name']}")
        print(f"- Peso actual: {scenario.get('current_weight')} kg")
        print(f"- Instrucciones: AGREGAR: {scenario['add_items']}")
        print(f"                 SACAR: {scenario['remove_items']}")
        print(f"                 DEJAR: {scenario['keep_items']}")
        
        # Here you would make the API call with each scenario
        # For now, just showing the structure


if __name__ == "__main__":
    # Create output directory
    os.makedirs("test_scripts/output", exist_ok=True)
    
    print("Sistema Mayra - Test Motor 2: Control y Ajustes")
    print("=" * 50)
    
    # Run main test
    asyncio.run(test_motor_2_control())
    
    # Run variation tests
    asyncio.run(test_motor_2_variations())