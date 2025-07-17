#!/usr/bin/env python3
"""
Test script for Motor 3 - Meal Replacement
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


async def test_motor_3_replacement():
    """Test Motor 3: Meal replacement."""
    
    print("=== Test Motor 3: Reemplazo de Comidas ===\n")
    
    # Assume we have an existing plan
    patient_id = 1
    plan_id = 1
    
    # Original meal to replace (example)
    original_meal = {
        "day": 1,
        "meal_type": "almuerzo",
        "name": "Pollo grillado con ensalada",
        "calories": 450,
        "protein": 45,
        "carbs": 30,
        "fat": 15,
        "ingredients": [
            "150g pechuga de pollo",
            "200g de ensalada mixta",
            "50g de arroz integral",
            "10ml aceite de oliva"
        ]
    }
    
    # Replacement request
    replacement_data = {
        "plan_id": plan_id,
        "day": 1,
        "meal_type": "almuerzo",
        "desired_food": "Salmón con vegetales al horno",
        "special_instructions": "El paciente quiere cambiar el pollo por pescado. Mantener sin gluten.",
        "original_calories": original_meal["calories"],
        "original_protein": original_meal["protein"],
        "original_carbs": original_meal["carbs"],
        "original_fat": original_meal["fat"]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Get patient info
            print("1. Obteniendo información del paciente y plan actual...")
            patient_response = await client.get(
                f"{API_BASE_URL}/patients/{patient_id}",
                headers={
                    "Authorization": f"Bearer {API_KEY}"
                }
            )
            
            if patient_response.status_code == 200:
                patient = patient_response.json()
                print(f"✓ Paciente: {patient.get('name', 'Juan Carlos Pérez')}")
                print(f"   - Restricciones: Sin gluten")
                print(f"   - Nivel económico: Medio")
            else:
                print("  Continuando con datos de prueba...")
            
            # Show original meal
            print(f"\n2. Comida original a reemplazar:")
            print(f"   - Día: {original_meal['day']}")
            print(f"   - Tipo: {original_meal['meal_type'].upper()}")
            print(f"   - Comida: {original_meal['name']}")
            print(f"   - Calorías: {original_meal['calories']} kcal")
            print(f"   - Proteínas: {original_meal['protein']}g")
            print(f"   - Carbohidratos: {original_meal['carbs']}g")
            print(f"   - Grasas: {original_meal['fat']}g")
            
            # Request replacement
            print(f"\n3. Solicitando reemplazo:")
            print(f"   - Nueva comida deseada: {replacement_data['desired_food']}")
            print(f"   - Instrucciones: {replacement_data['special_instructions']}")
            
            replacement_response = await client.post(
                f"{API_BASE_URL}/plans/{plan_id}/replacement",
                json=replacement_data,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=45.0
            )
            
            if replacement_response.status_code == 200:
                result = replacement_response.json()
                print("\n✓ Reemplazo generado exitosamente!")
                
                # Show replacement details
                if 'replacement_meal' in result:
                    print("\n=== NUEVA COMIDA ===")
                    meal = result['replacement_meal']
                    print(f"Nombre: {meal.get('recipe_name', replacement_data['desired_food'])}")
                    print(f"Calorías: {meal.get('calories', 'N/A')} kcal")
                    print(f"Proteínas: {meal.get('protein', 'N/A')}g")
                    print(f"Carbohidratos: {meal.get('carbs', 'N/A')}g")
                    print(f"Grasas: {meal.get('fat', 'N/A')}g")
                    
                    # Show tolerance
                    print(f"\n✓ Dentro de tolerancia (±5%): {result.get('within_tolerance', False)}")
                    print(f"   - Diferencia calórica: {result.get('calorie_difference', 0)} kcal")
                    print(f"   - Diferencia proteínas: {result.get('protein_difference', 0)}g")
                    
                # Get full replacement plan content
                plan_response = await client.get(
                    f"{API_BASE_URL}/plans/{result.get('plan', {}).get('id', plan_id)}",
                    headers={
                        "Authorization": f"Bearer {API_KEY}"
                    }
                )
                
                if plan_response.status_code == 200:
                    plan = plan_response.json()
                    if 'ai_generated_content' in plan:
                        print("\n=== REEMPLAZO DETALLADO ===")
                        print(plan['ai_generated_content'])
                        
                        # Save to file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"plan_motor3_reemplazo_{timestamp}.txt"
                        with open(f"test_scripts/output/{filename}", "w", encoding="utf-8") as f:
                            f.write("REEMPLAZO DE COMIDA - MOTOR 3\n")
                            f.write(f"Paciente: {patient.get('name', 'Juan Carlos Pérez')}\n")
                            f.write(f"Comida original: {original_meal['name']}\n")
                            f.write(f"Nueva comida: {replacement_data['desired_food']}\n")
                            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("="*50 + "\n\n")
                            f.write(plan['ai_generated_content'])
                        
                        print(f"\n✓ Reemplazo guardado en: test_scripts/output/{filename}")
                
            else:
                print(f"\n✗ Error generando reemplazo: {replacement_response.status_code}")
                print(replacement_response.text)
                
        except httpx.TimeoutException:
            print("\n✗ Timeout: La generación del reemplazo tardó demasiado")
        except Exception as e:
            print(f"\n✗ Error inesperado: {str(e)}")


async def test_multiple_replacements():
    """Test multiple meal replacements."""
    
    print("\n=== Test Motor 3: Múltiples Reemplazos ===\n")
    
    replacements = [
        {
            "meal": "desayuno",
            "original": "Tostadas con queso crema y mermelada",
            "calories": 350,
            "desired": "Yogur con frutas y granola",
            "reason": "Quiere algo más fresco y rápido"
        },
        {
            "meal": "cena",
            "original": "Omelette con verduras",
            "calories": 380,
            "desired": "Ensalada completa con atún",
            "reason": "Prefiere cenas más livianas"
        },
        {
            "meal": "merienda",
            "original": "Sándwich de jamón y queso",
            "calories": 280,
            "desired": "Licuado de frutas con frutos secos",
            "reason": "Busca opciones más nutritivas"
        }
    ]
    
    for i, repl in enumerate(replacements, 1):
        print(f"\nReemplazo {i}:")
        print(f"- Comida: {repl['meal'].upper()}")
        print(f"- Original: {repl['original']} ({repl['calories']} kcal)")
        print(f"- Deseada: {repl['desired']}")
        print(f"- Motivo: {repl['reason']}")
        
        # Here you would make the API call for each replacement
        # For testing purposes, we're just showing the structure


async def test_special_cases():
    """Test special replacement cases."""
    
    print("\n=== Test Motor 3: Casos Especiales ===\n")
    
    special_cases = [
        {
            "name": "Reemplazo por alergia repentina",
            "original": "Tortilla de papa con huevo",
            "desired": "Opción sin huevo",
            "condition": "Desarrolló alergia al huevo"
        },
        {
            "name": "Reemplazo por disponibilidad",
            "original": "Salmón con quinoa",
            "desired": "Pollo con arroz integral",
            "condition": "No consigue salmón en su zona"
        },
        {
            "name": "Reemplazo por preferencia cultural",
            "original": "Cerdo con batatas",
            "desired": "Opción sin cerdo",
            "condition": "Preferencias religiosas"
        }
    ]
    
    for case in special_cases:
        print(f"\nCaso: {case['name']}")
        print(f"- Original: {case['original']}")
        print(f"- Solicita: {case['desired']}")
        print(f"- Condición: {case['condition']}")


if __name__ == "__main__":
    # Create output directory
    os.makedirs("test_scripts/output", exist_ok=True)
    
    print("Sistema Mayra - Test Motor 3: Reemplazo de Comidas")
    print("=" * 50)
    
    # Run main test
    asyncio.run(test_motor_3_replacement())
    
    # Run multiple replacements test
    asyncio.run(test_multiple_replacements())
    
    # Run special cases test
    asyncio.run(test_special_cases())