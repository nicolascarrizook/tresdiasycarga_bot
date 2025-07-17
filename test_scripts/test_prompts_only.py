#!/usr/bin/env python3
"""
Test only the prompts directly without project imports
Sistema Mayra - Nutrition AI Platform
"""
import os
import sys
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import only the prompts module directly
from config.prompts import SystemPrompts, MotorType, format_rag_context


def test_all_motors():
    """Test all three motors with the unified prompt system."""
    print("\n🚀 TEST DIRECTO DE PROMPTS")
    print("="*60)
    print("Probando los 3 motores con el sistema unificado de prompts\n")
    
    # Verificar API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or "your-" in api_key:
        print("❌ ERROR: OPENAI_API_KEY no está configurada en .env")
        return False
    
    # Cliente OpenAI
    client = OpenAI(api_key=api_key)
    
    # Test recipes for RAG context
    test_recipes = [
        {
            "name": "Tostadas con palta y tomate",
            "category": "desayuno_merienda",
            "description": "2 rebanadas de pan integral (50gr) + 1/2 palta (60gr) + tomate a gusto + infusión"
        },
        {
            "name": "Pollo grillado con ensalada",
            "category": "almuerzo_cena", 
            "description": "150gr de pechuga de pollo + 200gr de ensalada mixta + 50gr de arroz integral + 10ml aceite de oliva"
        },
        {
            "name": "Yogur con frutos rojos",
            "category": "desayuno_merienda",
            "description": "200ml de yogur + 50gr de frutos rojos + 1 cdita de miel + 1 cdita de semillas"
        },
        {
            "name": "Salmón con vegetales al horno",
            "category": "almuerzo_cena",
            "description": "150gr de salmón + 200gr de vegetales mixtos + 50gr de batata + especias"
        }
    ]
    
    rag_context = format_rag_context(test_recipes)
    
    print("=== TEST MOTOR 1: PACIENTE NUEVO ===\n")
    
    # Motor 1 test data
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
        "preferences": ["pollo", "pescado", "verduras verdes"],
        "schedule": "Desayuno 7:00, Almuerzo 13:00, Merienda 17:00, Cena 21:00",
        "economic_level": "medio",
        "notes": "Prefiere comidas simples de preparar",
        "weight_type": "crudo",
        "main_meals": 4,
        "snacks_type": "Sin colaciones"
    }
    
    # Build Motor 1 prompts
    prompts_m1 = SystemPrompts.build_motor_1_prompt(patient_data, rag_context)
    
    print(f"Generando plan para: {patient_data['name']}")
    print(f"Objetivo: {patient_data['objective']}")
    print("Esperando respuesta de OpenAI...")
    
    try:
        # Test Motor 1
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": prompts_m1['system']},
                {"role": "user", "content": prompts_m1['user']}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        result_m1 = response.choices[0].message.content
        
        # Save Motor 1 result
        os.makedirs("test_scripts/output", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_m1 = f"test_scripts/output/prompts_motor1_{timestamp}.txt"
        
        with open(filename_m1, "w", encoding="utf-8") as f:
            f.write("TEST MOTOR 1 - PACIENTE NUEVO\n")
            f.write("="*50 + "\n")
            f.write(f"Paciente: {patient_data['name']}\n")
            f.write(f"Generado: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(result_m1)
        
        print(f"✓ Motor 1 generado! Guardado en: {filename_m1}")
        
        # Test Motor 2
        print("\n=== TEST MOTOR 2: CONTROL Y AJUSTES ===\n")
        
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
        
        prompts_m2 = SystemPrompts.build_motor_2_prompt(patient_data, control_data, rag_context)
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": prompts_m2['system']},
                {"role": "user", "content": prompts_m2['user']}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        result_m2 = response.choices[0].message.content
        filename_m2 = f"test_scripts/output/prompts_motor2_{timestamp}.txt"
        
        with open(filename_m2, "w", encoding="utf-8") as f:
            f.write("TEST MOTOR 2 - CONTROL\n")
            f.write("="*50 + "\n")
            f.write(f"Paciente: {patient_data['name']}\n")
            f.write(f"Peso anterior: 80.0 kg → Actual: {control_data['current_weight']} kg\n")
            f.write(f"Generado: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(result_m2)
        
        print(f"✓ Motor 2 generado! Guardado en: {filename_m2}")
        
        # Test Motor 3
        print("\n=== TEST MOTOR 3: REEMPLAZO DE COMIDA ===\n")
        
        replacement_data = {
            "meal_to_replace": "Pollo grillado con ensalada",
            "new_meal": "Salmón con vegetales al horno",
            "special_conditions": "Mantener sin gluten, el paciente quiere variar proteínas",
            "original_macros": "Calorías: 450, Proteínas: 45g, Carbohidratos: 30g, Grasas: 15g"
        }
        
        prompts_m3 = SystemPrompts.build_motor_3_prompt(patient_data, replacement_data, rag_context)
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": prompts_m3['system']},
                {"role": "user", "content": prompts_m3['user']}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result_m3 = response.choices[0].message.content
        filename_m3 = f"test_scripts/output/prompts_motor3_{timestamp}.txt"
        
        with open(filename_m3, "w", encoding="utf-8") as f:
            f.write("TEST MOTOR 3 - REEMPLAZO\n")
            f.write("="*50 + "\n")
            f.write(f"Original: {replacement_data['meal_to_replace']}\n")
            f.write(f"Nueva: {replacement_data['new_meal']}\n")
            f.write(f"Generado: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(result_m3)
        
        print(f"✓ Motor 3 generado! Guardado en: {filename_m3}")
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE!")
        print(f"\nResultados guardados en test_scripts/output/")
        print(f"- Motor 1: prompts_motor1_{timestamp}.txt")
        print(f"- Motor 2: prompts_motor2_{timestamp}.txt")
        print(f"- Motor 3: prompts_motor3_{timestamp}.txt")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if "api_key" in str(e).lower():
            print("\n⚠️  Verifica tu OPENAI_API_KEY en el archivo .env")
        return False


def main():
    """Main function."""
    success = test_all_motors()
    
    if success:
        print("\n✅ Sistema de prompts unificado funcionando correctamente!")
        print("\nPróximos pasos:")
        print("1. Revisar los planes generados en test_scripts/output/")
        print("2. Verificar que siguen el método 'Tres Días y Carga'")
        print("3. Confirmar que respetan restricciones y preferencias")
        print("4. Si todo está bien, el sistema está listo para producción")
    else:
        print("\n❌ Hubo errores en las pruebas")
        print("Verifica tu configuración y vuelve a intentar")


if __name__ == "__main__":
    main()