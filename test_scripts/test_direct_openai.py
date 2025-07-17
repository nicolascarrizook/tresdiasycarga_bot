#!/usr/bin/env python3
"""
Test directo de los prompts con OpenAI sin necesidad de base de datos
Sistema Mayra - Nutrition AI Platform
"""
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.prompts import SystemPrompts, MotorType, format_rag_context
from api.services.openai import OpenAIService

# Load environment variables
load_dotenv()


class DirectPromptTester:
    """Test prompts directly with OpenAI."""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.test_recipes = self._load_test_recipes()
    
    def _load_test_recipes(self):
        """Load sample recipes for RAG context."""
        # Estas son recetas del archivo recipes.json
        return [
            {
                "name": "Tostadas con queso crema y mermelada light",
                "category": "desayuno_merienda",
                "description": "2 tostadas de pan integral (50gr) + 2 cdas de queso crema + 2 cdas de mermelada light + 1 cdita de semillas + infusión a gusto"
            },
            {
                "name": "Pollo grillado con ensalada",
                "category": "almuerzo_cena", 
                "description": "150gr de pechuga de pollo + 200gr de ensalada mixta + 50gr de arroz integral + 10ml aceite de oliva"
            },
            {
                "name": "Yogur con frutos rojos",
                "category": "desayuno_merienda",
                "description": "200ml de yogur + 50gr de frutos rojos + 1 cdita de miel (5gr) + 1 cdita de semillas + infusión a gusto"
            },
            {
                "name": "Salmón con vegetales al horno",
                "category": "almuerzo_cena",
                "description": "150gr de salmón + 200gr de vegetales mixtos (zapallitos, berenjenas, pimientos) + 50gr de batata + especias"
            },
            {
                "name": "Ensalada completa con atún",
                "category": "almuerzo_cena",
                "description": "150gr de atún al natural + hojas verdes + tomate + zanahoria + 50gr de garbanzos + 1 cda de aceite de oliva"
            }
        ]
    
    async def test_motor_1(self):
        """Test Motor 1 - Paciente Nuevo."""
        print("\n=== TEST MOTOR 1: PACIENTE NUEVO ===\n")
        
        # Datos del paciente
        patient_data = {
            "name": "Juan Carlos Pérez",
            "age": 35,
            "sex": "masculino",
            "height": 175,
            "weight": 80,
            "objective": "bajar_0.5kg",
            "activity_type": "pesas",
            "frequency": "4 veces por semana",
            "duration": 60,
            "training_type": "fuerza e hipertrofia",
            "supplements": "Creatina 5g diarios",
            "pathologies": "Ninguna",
            "restrictions": ["gluten"],
            "preferences": ["pollo", "pescado", "verduras verdes", "frutos secos"],
            "schedule": "Desayuno 7:00, Almuerzo 13:00, Merienda 17:00, Cena 21:00",
            "economic_level": "medio",
            "notes": "Prefiere comidas simples de preparar",
            "weight_type": "crudo",
            "main_meals": 4,
            "snacks_type": "Sin colaciones"
        }
        
        # Generar contexto RAG
        rag_context = format_rag_context(self.test_recipes)
        
        # Generar prompts
        prompts = SystemPrompts.build_motor_1_prompt(patient_data, rag_context)
        
        print("Generando plan nutricional para:")
        print(f"- Paciente: {patient_data['name']}")
        print(f"- Objetivo: {patient_data['objective']}")
        print(f"- Restricción: Sin gluten")
        print("\nEsperando respuesta de OpenAI...")
        
        try:
            # Llamar a OpenAI
            response = await self.openai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompts['system']},
                    {"role": "user", "content": prompts['user']}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            result = response.choices[0].message.content
            
            # Guardar resultado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_scripts/output/direct_motor1_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write("TEST DIRECTO MOTOR 1 - PACIENTE NUEVO\n")
                f.write("="*50 + "\n")
                f.write(f"Paciente: {patient_data['name']}\n")
                f.write(f"Objetivo: {patient_data['objective']}\n")
                f.write(f"Generado: {datetime.now()}\n")
                f.write("="*50 + "\n\n")
                f.write(result)
            
            print(f"\n✓ Plan generado exitosamente!")
            print(f"✓ Guardado en: {filename}")
            print(f"✓ Tokens usados: {response.usage.total_tokens}")
            
            # Mostrar primeras líneas
            print("\nPrimeras líneas del plan:")
            print("-" * 50)
            lines = result.split('\n')[:10]
            for line in lines:
                print(line)
            print("...")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            return False
    
    async def test_motor_2(self):
        """Test Motor 2 - Control."""
        print("\n=== TEST MOTOR 2: CONTROL Y AJUSTES ===\n")
        
        patient_data = {
            "name": "Juan Carlos Pérez",
            "weight": 80,
            "restrictions": ["gluten"],
            "preferences": ["pollo", "pescado", "verduras"],
            "economic_level": "medio"
        }
        
        control_data = {
            "control_date": datetime.now().strftime("%Y-%m-%d"),
            "current_weight": 79.2,
            "updated_objective": "bajar_0.5kg",
            "current_activity": "pesas + cardio",
            "training_changes": "Agregó 30 min de cardio los sábados",
            "current_supplements": "Creatina 5g + Omega 3",
            "current_pathologies": "Ninguna",
            "current_restrictions": ["gluten"],
            "current_preferences": ["pollo", "pescado", "verduras", "huevos"],
            "current_schedule": "Desayuno 7:00, Almuerzo 13:00, Merienda 17:00, Cena 21:00",
            "current_economic_level": "medio",
            "current_notes": "Buena adherencia, solicita más variedad en desayunos",
            "add_items": "Más opciones de desayuno con huevos",
            "remove_items": "Reducir frutos secos",
            "keep_items": "Mantener 4 comidas sin gluten"
        }
        
        # Generar contexto RAG
        rag_context = format_rag_context(self.test_recipes)
        
        # Generar prompts
        prompts = SystemPrompts.build_motor_2_prompt(patient_data, control_data, rag_context)
        
        print("Generando plan de control para:")
        print(f"- Paciente: {patient_data['name']}")
        print(f"- Peso anterior: 80.0 kg → Peso actual: {control_data['current_weight']} kg")
        print(f"- AGREGAR: {control_data['add_items']}")
        print(f"- SACAR: {control_data['remove_items']}")
        print(f"- DEJAR: {control_data['keep_items']}")
        
        try:
            response = await self.openai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompts['system']},
                    {"role": "user", "content": prompts['user']}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            result = response.choices[0].message.content
            
            # Guardar resultado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_scripts/output/direct_motor2_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write("TEST DIRECTO MOTOR 2 - CONTROL\n")
                f.write("="*50 + "\n")
                f.write(f"Paciente: {patient_data['name']}\n")
                f.write(f"Peso anterior: 80.0 kg → Actual: {control_data['current_weight']} kg\n")
                f.write(f"Generado: {datetime.now()}\n")
                f.write("="*50 + "\n\n")
                f.write(result)
            
            print(f"\n✓ Plan de control generado!")
            print(f"✓ Guardado en: {filename}")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            return False
    
    async def test_motor_3(self):
        """Test Motor 3 - Reemplazo."""
        print("\n=== TEST MOTOR 3: REEMPLAZO DE COMIDA ===\n")
        
        patient_data = {
            "name": "Juan Carlos Pérez",
            "restrictions": ["gluten"],
            "preferences": ["pescado", "vegetales"],
            "economic_level": "medio",
            "weight_type": "crudo"
        }
        
        replacement_data = {
            "meal_to_replace": "Pollo grillado con ensalada",
            "new_meal": "Salmón con vegetales al horno",
            "special_conditions": "Mantener sin gluten, el paciente quiere variar proteínas",
            "original_macros": "Calorías: 450, Proteínas: 45g, Carbohidratos: 30g, Grasas: 15g"
        }
        
        # Generar contexto RAG
        rag_context = format_rag_context(self.test_recipes)
        
        # Generar prompts
        prompts = SystemPrompts.build_motor_3_prompt(patient_data, replacement_data, rag_context)
        
        print("Generando reemplazo:")
        print(f"- Original: {replacement_data['meal_to_replace']}")
        print(f"- Nueva: {replacement_data['new_meal']}")
        print(f"- Condición: {replacement_data['special_conditions']}")
        
        try:
            response = await self.openai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompts['system']},
                    {"role": "user", "content": prompts['user']}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            # Guardar resultado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_scripts/output/direct_motor3_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write("TEST DIRECTO MOTOR 3 - REEMPLAZO\n")
                f.write("="*50 + "\n")
                f.write(f"Original: {replacement_data['meal_to_replace']}\n")
                f.write(f"Nueva: {replacement_data['new_meal']}\n")
                f.write(f"Generado: {datetime.now()}\n")
                f.write("="*50 + "\n\n")
                f.write(result)
            
            print(f"\n✓ Reemplazo generado!")
            print(f"✓ Guardado en: {filename}")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Ejecutar todos los tests."""
        print("\nSistema Mayra - Test Directo con OpenAI")
        print("="*60)
        print("Este test NO requiere base de datos")
        print("Solo necesitas tu OPENAI_API_KEY configurada\n")
        
        # Verificar API key
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key.startswith("your-") or api_key.startswith("sk-your"):
            print("❌ ERROR: OPENAI_API_KEY no está configurada")
            print("Por favor, actualiza tu archivo .env con una API key válida")
            return
        
        print("✓ API Key detectada\n")
        
        # Ejecutar tests
        results = []
        
        # Motor 1
        result1 = await self.test_motor_1()
        results.append(("Motor 1 - Paciente Nuevo", result1))
        await asyncio.sleep(2)
        
        # Motor 2
        result2 = await self.test_motor_2()
        results.append(("Motor 2 - Control", result2))
        await asyncio.sleep(2)
        
        # Motor 3
        result3 = await self.test_motor_3()
        results.append(("Motor 3 - Reemplazo", result3))
        
        # Resumen
        print("\n" + "="*60)
        print("RESUMEN DE PRUEBAS")
        print("="*60)
        for test_name, success in results:
            status = "✓" if success else "✗"
            print(f"{status} {test_name}")
        
        print(f"\nTodos los resultados guardados en: test_scripts/output/")


async def main():
    """Main function."""
    # Create output directory
    os.makedirs("test_scripts/output", exist_ok=True)
    
    tester = DirectPromptTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("\n🚀 PRUEBA DIRECTA SIN BASE DE DATOS")
    print("Este script prueba los 3 motores directamente con OpenAI")
    print("No necesitas PostgreSQL, Redis ni ChromaDB\n")
    
    asyncio.run(main())