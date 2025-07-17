"""
Plan seeder for Sistema Mayra database.
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta, date
from decimal import Decimal

from database.models.plan import Plan, PlanStatusEnum, PlanMotorEnum
from database.seeders.base import BaseSeeder


class PlanSeeder(BaseSeeder):
    """Seeder for creating initial plans."""
    
    def get_seeder_name(self) -> str:
        return "PlanSeeder"
    
    async def seed(self) -> Dict[str, Any]:
        """Create initial plans."""
        self.log_info("Starting plan seeding...")
        
        # Create test plans
        test_plans = await self.create_test_plans()
        
        return {
            "seeder": self.get_seeder_name(),
            "success": True,
            "created_count": len(self.created_records),
            "test_plans_count": len(test_plans),
            "timestamp": datetime.utcnow()
        }
    
    async def create_test_plans(self) -> List[Plan]:
        """Create test plans for development."""
        test_plans = []
        
        # Plan 1: Active weight loss plan
        plan1 = Plan(
            patient_id=1,  # María González
            name="Plan de Pérdida de Peso - María",
            description="Plan nutricional personalizado para pérdida de peso gradual",
            motor=PlanMotorEnum.NEW_PATIENT,
            status=PlanStatusEnum.ACTIVE,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() + timedelta(days=23),
            target_calories=1500,
            target_protein=Decimal("100.0"),
            target_carbs=Decimal("150.0"),
            target_fat=Decimal("67.0"),
            meals_data={
                "day1": {
                    "breakfast": {
                        "recipe_id": 1,
                        "recipe_name": "Avena con frutas y canela",
                        "calories": 280,
                        "protein": 8.5,
                        "carbs": 45.0,
                        "fat": 6.2,
                        "notes": "Desayuno rico en fibra"
                    },
                    "lunch": {
                        "recipe_id": 4,
                        "recipe_name": "Ensalada de pollo con aguacate",
                        "calories": 350,
                        "protein": 25.0,
                        "carbs": 15.0,
                        "fat": 20.0,
                        "notes": "Almuerzo completo y saciante"
                    },
                    "dinner": {
                        "recipe_id": 7,
                        "recipe_name": "Pechuga de pollo a la plancha con puré de coliflor",
                        "calories": 320,
                        "protein": 40.0,
                        "carbs": 10.0,
                        "fat": 12.0,
                        "notes": "Cena ligera pero nutritiva"
                    },
                    "snack": {
                        "recipe_id": 10,
                        "recipe_name": "Hummus casero con bastones de verduras",
                        "calories": 150,
                        "protein": 6.0,
                        "carbs": 18.0,
                        "fat": 6.0,
                        "notes": "Snack saludable"
                    }
                },
                "day2": {
                    "breakfast": {
                        "recipe_id": 2,
                        "recipe_name": "Huevos revueltos con verduras",
                        "calories": 180,
                        "protein": 12.0,
                        "carbs": 6.0,
                        "fat": 12.0,
                        "notes": "Desayuno proteico"
                    },
                    "lunch": {
                        "recipe_id": 5,
                        "recipe_name": "Salmón al horno con verduras",
                        "calories": 420,
                        "protein": 35.0,
                        "carbs": 12.0,
                        "fat": 25.0,
                        "notes": "Rico en omega-3"
                    },
                    "dinner": {
                        "recipe_id": 8,
                        "recipe_name": "Pescado al vapor con vegetales",
                        "calories": 250,
                        "protein": 30.0,
                        "carbs": 8.0,
                        "fat": 8.0,
                        "notes": "Cena muy ligera"
                    },
                    "snack": {
                        "recipe_id": 9,
                        "recipe_name": "Batido de proteínas con banana",
                        "calories": 220,
                        "protein": 25.0,
                        "carbs": 20.0,
                        "fat": 4.0,
                        "notes": "Post-entrenamiento"
                    }
                },
                "day3": {
                    "breakfast": {
                        "recipe_id": 3,
                        "recipe_name": "Yogurt griego con granola y berries",
                        "calories": 320,
                        "protein": 20.0,
                        "carbs": 35.0,
                        "fat": 10.0,
                        "notes": "Desayuno con probióticos"
                    },
                    "lunch": {
                        "recipe_id": 6,
                        "recipe_name": "Bowl de quinoa con verduras asadas",
                        "calories": 380,
                        "protein": 15.0,
                        "carbs": 55.0,
                        "fat": 12.0,
                        "notes": "Opción vegetariana"
                    },
                    "dinner": {
                        "recipe_id": 7,
                        "recipe_name": "Pechuga de pollo a la plancha con puré de coliflor",
                        "calories": 320,
                        "protein": 40.0,
                        "carbs": 10.0,
                        "fat": 12.0,
                        "notes": "Repetir por preferencia"
                    },
                    "snack": {
                        "recipe_id": 10,
                        "recipe_name": "Hummus casero con bastones de verduras",
                        "calories": 150,
                        "protein": 6.0,
                        "carbs": 18.0,
                        "fat": 6.0,
                        "notes": "Snack balanceado"
                    }
                }
            },
            adherence_percentage=Decimal("85.0"),
            current_cycle=1,
            total_cycles=1,
            notes="Paciente muy comprometida con el plan",
            created_at=datetime.utcnow() - timedelta(days=7),
            updated_at=datetime.utcnow() - timedelta(days=1),
            activated_at=datetime.utcnow() - timedelta(days=7),
            is_active=True
        )
        test_plans.append(plan1)
        
        # Plan 2: Muscle gain plan
        plan2 = Plan(
            patient_id=2,  # Carlos Rodríguez
            name="Plan de Ganancia Muscular - Carlos",
            description="Plan hipercalórico para ganancia de masa muscular",
            motor=PlanMotorEnum.NEW_PATIENT,
            status=PlanStatusEnum.ACTIVE,
            start_date=date.today() - timedelta(days=14),
            end_date=date.today() + timedelta(days=16),
            target_calories=2800,
            target_protein=Decimal("180.0"),
            target_carbs=Decimal("300.0"),
            target_fat=Decimal("100.0"),
            meals_data={
                "day1": {
                    "breakfast": {
                        "recipe_id": 3,
                        "recipe_name": "Yogurt griego con granola y berries",
                        "calories": 320,
                        "protein": 20.0,
                        "carbs": 35.0,
                        "fat": 10.0,
                        "notes": "Desayuno rico en proteína"
                    },
                    "lunch": {
                        "recipe_id": 5,
                        "recipe_name": "Salmón al horno con verduras",
                        "calories": 420,
                        "protein": 35.0,
                        "carbs": 12.0,
                        "fat": 25.0,
                        "notes": "Almuerzo con omega-3"
                    },
                    "dinner": {
                        "recipe_id": 7,
                        "recipe_name": "Pechuga de pollo a la plancha con puré de coliflor",
                        "calories": 320,
                        "protein": 40.0,
                        "carbs": 10.0,
                        "fat": 12.0,
                        "notes": "Cena proteica"
                    },
                    "snack": {
                        "recipe_id": 9,
                        "recipe_name": "Batido de proteínas con banana",
                        "calories": 220,
                        "protein": 25.0,
                        "carbs": 20.0,
                        "fat": 4.0,
                        "notes": "Post-entrenamiento"
                    },
                    "pre_workout": {
                        "custom_meal": "Avena con banana y miel",
                        "calories": 300,
                        "protein": 8.0,
                        "carbs": 60.0,
                        "fat": 3.0,
                        "notes": "Energía para el entrenamiento"
                    }
                },
                "day2": {
                    "breakfast": {
                        "recipe_id": 1,
                        "recipe_name": "Avena con frutas y canela",
                        "calories": 280,
                        "protein": 8.5,
                        "carbs": 45.0,
                        "fat": 6.2,
                        "notes": "Desayuno energético"
                    },
                    "lunch": {
                        "recipe_id": 4,
                        "recipe_name": "Ensalada de pollo con aguacate",
                        "calories": 350,
                        "protein": 25.0,
                        "carbs": 15.0,
                        "fat": 20.0,
                        "notes": "Almuerzo completo"
                    },
                    "dinner": {
                        "recipe_id": 8,
                        "recipe_name": "Pescado al vapor con vegetales",
                        "calories": 250,
                        "protein": 30.0,
                        "carbs": 8.0,
                        "fat": 8.0,
                        "notes": "Cena ligera"
                    },
                    "snack": {
                        "recipe_id": 10,
                        "recipe_name": "Hummus casero con bastones de verduras",
                        "calories": 150,
                        "protein": 6.0,
                        "carbs": 18.0,
                        "fat": 6.0,
                        "notes": "Snack saludable"
                    },
                    "pre_workout": {
                        "custom_meal": "Sandwich integral con pavo",
                        "calories": 350,
                        "protein": 25.0,
                        "carbs": 40.0,
                        "fat": 8.0,
                        "notes": "Comida pre-entrenamiento"
                    }
                },
                "day3": {
                    "breakfast": {
                        "recipe_id": 2,
                        "recipe_name": "Huevos revueltos con verduras",
                        "calories": 180,
                        "protein": 12.0,
                        "carbs": 6.0,
                        "fat": 12.0,
                        "notes": "Desayuno proteico"
                    },
                    "lunch": {
                        "recipe_id": 6,
                        "recipe_name": "Bowl de quinoa con verduras asadas",
                        "calories": 380,
                        "protein": 15.0,
                        "carbs": 55.0,
                        "fat": 12.0,
                        "notes": "Almuerzo con carbohidratos"
                    },
                    "dinner": {
                        "recipe_id": 7,
                        "recipe_name": "Pechuga de pollo a la plancha con puré de coliflor",
                        "calories": 320,
                        "protein": 40.0,
                        "carbs": 10.0,
                        "fat": 12.0,
                        "notes": "Cena alta en proteína"
                    },
                    "snack": {
                        "recipe_id": 9,
                        "recipe_name": "Batido de proteínas con banana",
                        "calories": 220,
                        "protein": 25.0,
                        "carbs": 20.0,
                        "fat": 4.0,
                        "notes": "Recuperación muscular"
                    },
                    "pre_workout": {
                        "custom_meal": "Frutas con yogurt",
                        "calories": 200,
                        "protein": 10.0,
                        "carbs": 35.0,
                        "fat": 2.0,
                        "notes": "Energía rápida"
                    }
                }
            },
            adherence_percentage=Decimal("92.0"),
            current_cycle=1,
            total_cycles=1,
            notes="Atleta muy disciplinado, excelente adherencia",
            created_at=datetime.utcnow() - timedelta(days=14),
            updated_at=datetime.utcnow() - timedelta(hours=6),
            activated_at=datetime.utcnow() - timedelta(days=14),
            is_active=True
        )
        test_plans.append(plan2)
        
        # Plan 3: Completed plan
        plan3 = Plan(
            patient_id=3,  # Ana Martínez
            name="Plan de Mantenimiento - Ana",
            description="Plan para mantenimiento de peso con control diabético",
            motor=PlanMotorEnum.CONTROL_ADJUSTMENT,
            status=PlanStatusEnum.COMPLETED,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() - timedelta(days=1),
            target_calories=1800,
            target_protein=Decimal("90.0"),
            target_carbs=Decimal("180.0"),
            target_fat=Decimal("70.0"),
            meals_data={
                "day1": {
                    "breakfast": {
                        "recipe_id": 1,
                        "recipe_name": "Avena con frutas y canela",
                        "calories": 280,
                        "protein": 8.5,
                        "carbs": 45.0,
                        "fat": 6.2,
                        "notes": "Sin azúcar agregado"
                    },
                    "lunch": {
                        "recipe_id": 6,
                        "recipe_name": "Bowl de quinoa con verduras asadas",
                        "calories": 380,
                        "protein": 15.0,
                        "carbs": 55.0,
                        "fat": 12.0,
                        "notes": "Alto en fibra"
                    },
                    "dinner": {
                        "recipe_id": 8,
                        "recipe_name": "Pescado al vapor con vegetales",
                        "calories": 250,
                        "protein": 30.0,
                        "carbs": 8.0,
                        "fat": 8.0,
                        "notes": "Bajo en carbohidratos"
                    },
                    "snack": {
                        "recipe_id": 10,
                        "recipe_name": "Hummus casero con bastones de verduras",
                        "calories": 150,
                        "protein": 6.0,
                        "carbs": 18.0,
                        "fat": 6.0,
                        "notes": "Snack sin azúcar"
                    }
                },
                "day2": {
                    "breakfast": {
                        "recipe_id": 2,
                        "recipe_name": "Huevos revueltos con verduras",
                        "calories": 180,
                        "protein": 12.0,
                        "carbs": 6.0,
                        "fat": 12.0,
                        "notes": "Bajo en carbohidratos"
                    },
                    "lunch": {
                        "recipe_id": 4,
                        "recipe_name": "Ensalada de pollo con aguacate",
                        "calories": 350,
                        "protein": 25.0,
                        "carbs": 15.0,
                        "fat": 20.0,
                        "notes": "Grasas saludables"
                    },
                    "dinner": {
                        "recipe_id": 7,
                        "recipe_name": "Pechuga de pollo a la plancha con puré de coliflor",
                        "calories": 320,
                        "protein": 40.0,
                        "carbs": 10.0,
                        "fat": 12.0,
                        "notes": "Proteína magra"
                    },
                    "snack": {
                        "custom_meal": "Nueces y almendras",
                        "calories": 200,
                        "protein": 6.0,
                        "carbs": 6.0,
                        "fat": 18.0,
                        "notes": "Grasas buenas"
                    }
                },
                "day3": {
                    "breakfast": {
                        "recipe_id": 3,
                        "recipe_name": "Yogurt griego con granola y berries",
                        "calories": 320,
                        "protein": 20.0,
                        "carbs": 35.0,
                        "fat": 10.0,
                        "notes": "Probióticos"
                    },
                    "lunch": {
                        "recipe_id": 5,
                        "recipe_name": "Salmón al horno con verduras",
                        "calories": 420,
                        "protein": 35.0,
                        "carbs": 12.0,
                        "fat": 25.0,
                        "notes": "Omega-3"
                    },
                    "dinner": {
                        "recipe_id": 8,
                        "recipe_name": "Pescado al vapor con vegetales",
                        "calories": 250,
                        "protein": 30.0,
                        "carbs": 8.0,
                        "fat": 8.0,
                        "notes": "Cena ligera"
                    },
                    "snack": {
                        "recipe_id": 10,
                        "recipe_name": "Hummus casero con bastones de verduras",
                        "calories": 150,
                        "protein": 6.0,
                        "carbs": 18.0,
                        "fat": 6.0,
                        "notes": "Fibra y proteína"
                    }
                }
            },
            adherence_percentage=Decimal("78.0"),
            current_cycle=1,
            total_cycles=1,
            notes="Plan completado exitosamente, control glucémico mejorado",
            created_at=datetime.utcnow() - timedelta(days=30),
            updated_at=datetime.utcnow() - timedelta(days=1),
            activated_at=datetime.utcnow() - timedelta(days=30),
            deactivated_at=datetime.utcnow() - timedelta(days=1),
            is_active=False
        )
        test_plans.append(plan3)
        
        await self.commit_batch(test_plans, "test plans")
        return test_plans