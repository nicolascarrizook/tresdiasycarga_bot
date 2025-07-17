#!/usr/bin/env python3
"""
Main test runner for Sistema Mayra - Nutrition AI Platform
Executes all motor tests in sequence
"""
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_motor_1_new_patient import test_motor_1_new_patient
from test_motor_2_control import test_motor_2_control
from test_motor_3_replacement import test_motor_3_replacement


class TestRunner:
    """Test runner for Sistema Mayra motors."""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
    
    async def run_test(self, test_name: str, test_func) -> Tuple[str, bool, str]:
        """Run a single test and capture results."""
        print(f"\n{'='*60}")
        print(f"Ejecutando: {test_name}")
        print(f"{'='*60}")
        
        try:
            await test_func()
            return (test_name, True, "Completado exitosamente")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n✗ {test_name} falló: {error_msg}")
            return (test_name, False, error_msg)
    
    async def run_all_tests(self):
        """Run all motor tests."""
        self.start_time = datetime.now()
        
        print("\n" + "="*80)
        print("SISTEMA MAYRA - TEST SUITE COMPLETO")
        print("Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva")
        print("="*80)
        print(f"\nIniciando pruebas: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define tests
        tests = [
            ("Motor 1 - Paciente Nuevo", test_motor_1_new_patient),
            ("Motor 2 - Control y Ajustes", test_motor_2_control),
            ("Motor 3 - Reemplazo de Comidas", test_motor_3_replacement)
        ]
        
        # Run tests
        for test_name, test_func in tests:
            result = await self.run_test(test_name, test_func)
            self.results.append(result)
            
            # Wait between tests
            print("\nEsperando 2 segundos antes del siguiente test...")
            await asyncio.sleep(2)
        
        self.end_time = datetime.now()
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        duration = self.end_time - self.start_time
        total_tests = len(self.results)
        passed_tests = sum(1 for _, passed, _ in self.results if passed)
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*80)
        print("RESUMEN DE PRUEBAS")
        print("="*80)
        print(f"Tiempo total: {duration.total_seconds():.2f} segundos")
        print(f"Total de tests: {total_tests}")
        print(f"✓ Exitosos: {passed_tests}")
        print(f"✗ Fallidos: {failed_tests}")
        
        print("\nDetalle:")
        for test_name, passed, message in self.results:
            status = "✓" if passed else "✗"
            print(f"{status} {test_name}: {message}")
        
        if failed_tests == 0:
            print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        else:
            print(f"\n⚠️  {failed_tests} test(s) fallaron. Revisar los logs para más detalles.")
        
        # Save summary to file
        self.save_summary()
    
    def save_summary(self):
        """Save test summary to file."""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_scripts/output/test_summary_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("SISTEMA MAYRA - RESUMEN DE PRUEBAS\n")
            f.write("="*50 + "\n")
            f.write(f"Fecha: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duración: {(self.end_time - self.start_time).total_seconds():.2f} segundos\n")
            f.write(f"\nResultados:\n")
            
            for test_name, passed, message in self.results:
                status = "PASS" if passed else "FAIL"
                f.write(f"[{status}] {test_name}: {message}\n")
        
        print(f"\nResumen guardado en: {filename}")


async def quick_test():
    """Quick test to verify system is working."""
    print("\n=== PRUEBA RÁPIDA DEL SISTEMA ===")
    
    # Test imports
    print("\n1. Verificando imports...")
    try:
        from config.prompts import SystemPrompts, MotorType
        print("✓ Imports de prompts correctos")
    except ImportError as e:
        print(f"✗ Error en imports: {e}")
        return
    
    # Test prompt generation
    print("\n2. Verificando generación de prompts...")
    try:
        patient_data = {
            "name": "Test User",
            "age": 30,
            "sex": "masculino",
            "height": 170,
            "weight": 70,
            "objective": "mantenimiento"
        }
        
        prompts = SystemPrompts.build_motor_1_prompt(patient_data, "contexto de prueba")
        print("✓ Prompts generados correctamente")
        print(f"  - System prompt length: {len(prompts['system'])} chars")
        print(f"  - User prompt length: {len(prompts['user'])} chars")
    except Exception as e:
        print(f"✗ Error generando prompts: {e}")
    
    print("\n✓ Prueba rápida completada")


def main():
    """Main entry point."""
    # Create output directory
    os.makedirs("test_scripts/output", exist_ok=True)
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            asyncio.run(quick_test())
        elif sys.argv[1] == "--motor1":
            asyncio.run(test_motor_1_new_patient())
        elif sys.argv[1] == "--motor2":
            asyncio.run(test_motor_2_control())
        elif sys.argv[1] == "--motor3":
            asyncio.run(test_motor_3_replacement())
        else:
            print("Uso: python run_all_tests.py [--quick|--motor1|--motor2|--motor3]")
    else:
        # Run all tests
        runner = TestRunner()
        asyncio.run(runner.run_all_tests())


if __name__ == "__main__":
    main()