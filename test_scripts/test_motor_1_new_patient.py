#!/usr/bin/env python3
"""
Test script for Motor 1 - New Patient Plan Generation
Sistema Mayra - Nutrition AI Platform
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

import httpx
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "test-api-key")


async def test_motor_1_new_patient():
    """Test Motor 1: Generate plan for new patient."""
    
    print("=== Test Motor 1: Paciente Nuevo ===\n")
    
    # Test patient data
    patient_data = {
        "name": "Juan Carlos Pérez",
        "age": 35,
        "sex": "masculino",
        "height": 175,  # cm
        "weight": 80,   # kg
        "email": "juan.perez@email.com",
        "phone": "+54 11 1234-5678",
        "telegram_user_id": 123456789,
        
        # Objectives and activity
        "objective": "bajar_0.5kg",
        "activity_type": "pesas",
        "activity_frequency": "4 veces por semana",
        "activity_duration": 60,  # minutes
        "training_type": "fuerza e hipertrofia",
        
        # Health data
        "supplements": "Creatina 5g diarios",
        "pathologies": "Ninguna",
        "medications": "Ninguna",
        "allergies": [],
        
        # Food preferences and restrictions
        "restrictions": ["gluten"],  # Sin gluten
        "preferences": ["pollo", "pescado", "verduras verdes", "frutos secos"],
        "dislikes": ["hígado", "mondongo"],
        
        # Schedule and lifestyle
        "schedule": "Desayuno 7:00, Almuerzo 13:00, Merienda 17:00, Cena 21:00",
        "occupation": "Oficinista",
        "economic_level": "medio",
        
        # Additional notes
        "notes": "Prefiere comidas simples de preparar. Tiene poco tiempo para cocinar durante la semana.",
        
        # Plan configuration
        "weight_type": "crudo",
        "main_meals": 4,
        "snacks_type": "Sin colaciones",
        "collations": 0
    }
    
    # Plan generation request
    plan_request = {
        "patient_id": 1,  # Assuming patient is already created
        "plan_type": "nuevo_paciente",
        "weight_type": "crudo",
        "main_meals": 4,
        "snacks_type": "Sin colaciones",
        "custom_instructions": "Priorizar recetas simples y rápidas de preparar. Evitar completamente el gluten."
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # First, create the patient
            print("1. Creando paciente...")
            patient_response = await client.post(
                f"{API_BASE_URL}/patients",
                json=patient_data,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            
            if patient_response.status_code == 201:
                patient = patient_response.json()
                print(f"✓ Paciente creado: {patient['name']} (ID: {patient['id']})")
                plan_request["patient_id"] = patient['id']
            else:
                print(f"✗ Error creando paciente: {patient_response.status_code}")
                print(patient_response.text)
                return
            
            # Generate nutrition plan
            print("\n2. Generando plan nutricional...")
            print("   - Objetivo: Bajar 0.5kg por semana")
            print("   - Restricción: Sin gluten")
            print("   - Actividad: Pesas 4x semana")
            print("   - Preferencias: Comidas simples y rápidas")
            
            plan_response = await client.post(
                f"{API_BASE_URL}/plans/generate",
                json=plan_request,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=60.0  # 60 seconds timeout for AI generation
            )
            
            if plan_response.status_code == 201:
                result = plan_response.json()
                print("\n✓ Plan generado exitosamente!")
                print(f"   - Tiempo de generación: {result.get('generation_time', 'N/A')} segundos")
                print(f"   - Tokens utilizados: {result.get('tokens_used', 'N/A')}")
                print(f"   - Modelo: {result.get('model_used', 'N/A')}")
                print(f"   - Precisión nutricional: {result.get('nutritional_accuracy', 0) * 100:.1f}%")
                print(f"   - Coincidencia preferencias: {result.get('preference_match', 0) * 100:.1f}%")
                
                # Display plan content
                if 'plan' in result and 'ai_generated_content' in result['plan']:
                    print("\n=== PLAN NUTRICIONAL GENERADO ===")
                    print(result['plan']['ai_generated_content'])
                    
                    # Save to file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"plan_motor1_{patient['name'].replace(' ', '_')}_{timestamp}.txt"
                    with open(f"test_scripts/output/{filename}", "w", encoding="utf-8") as f:
                        f.write(f"PLAN NUTRICIONAL - {patient['name']}\n")
                        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("="*50 + "\n\n")
                        f.write(result['plan']['ai_generated_content'])
                    
                    print(f"\n✓ Plan guardado en: test_scripts/output/{filename}")
                
            else:
                print(f"\n✗ Error generando plan: {plan_response.status_code}")
                print(plan_response.text)
                
        except httpx.TimeoutException:
            print("\n✗ Timeout: La generación del plan tardó demasiado")
        except Exception as e:
            print(f"\n✗ Error inesperado: {str(e)}")


async def test_direct_api():
    """Test direct API call without creating patient first."""
    
    print("\n=== Test Directo API (sin crear paciente) ===\n")
    
    # Complete patient data for prompt
    patient_data = {
        "name": "María González",
        "age": 28,
        "sex": "femenino",
        "height": 165,
        "weight": 65,
        "objective": "mantenimiento",
        "activity_type": "cardio",
        "frequency": "3 veces por semana",
        "duration": 45,
        "training_type": "running y spinning",
        "supplements": "Ninguno",
        "pathologies": "Hipotiroidismo controlado",
        "restrictions": ["lacteos"],
        "preferences": ["ensaladas", "frutas", "pescado", "quinoa"],
        "schedule": "Desayuno 8:00, Almuerzo 13:00, Cena 20:00",
        "economic_level": "medio",
        "notes": "Vegetariana flexible, come pescado ocasionalmente",
        "weight_type": "crudo",
        "main_meals": 3,
        "snacks_type": "2 colaciones saludables"
    }
    
    # This would be used directly with the services
    print("Datos del paciente preparados para generación directa")
    print(f"Paciente: {patient_data['name']}")
    print(f"Objetivo: {patient_data['objective']}")
    print(f"Restricciones: {', '.join(patient_data['restrictions'])}")
    
    # Note: This would require direct access to services, not through HTTP API
    print("\nNota: Para prueba directa, ejecutar desde el contexto de la aplicación")


if __name__ == "__main__":
    # Create output directory
    os.makedirs("test_scripts/output", exist_ok=True)
    
    print("Sistema Mayra - Test Motor 1: Paciente Nuevo")
    print("=" * 50)
    
    # Run tests
    asyncio.run(test_motor_1_new_patient())
    
    # Uncomment to test direct API
    # asyncio.run(test_direct_api())