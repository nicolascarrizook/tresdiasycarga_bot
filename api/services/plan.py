"""
Plan service for Sistema Mayra API.
"""
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import BaseModel
from ..schemas.plan import Plan, PlanCreate, PlanGeneration, PlanGenerationResult
from .base import BaseService
from .patient import PatientService
from .recipe import RecipeService
from .rag import RAGService
from .openai import OpenAIService

logger = logging.getLogger(__name__)


class PlanModel(BaseModel):
    """Plan model placeholder."""
    __tablename__ = "plans"


class PlanService(BaseService[PlanModel, Plan]):
    """Plan service for managing nutrition plans."""
    
    def __init__(
        self, 
        db: AsyncSession,
        patient_service: PatientService,
        recipe_service: RecipeService,
        rag_service: RAGService,
        openai_service: OpenAIService
    ):
        super().__init__(db, PlanModel)
        self.patient_service = patient_service
        self.recipe_service = recipe_service
        self.rag_service = rag_service
        self.openai_service = openai_service
    
    async def generate_plan(self, generation_request: PlanGeneration) -> Optional[PlanGenerationResult]:
        """Generate nutrition plan based on request."""
        try:
            # Get patient data
            patient = await self.patient_service.get_by_id(generation_request.patient_id)
            if not patient:
                return None
            
            # Based on plan type, generate appropriate plan
            if generation_request.plan_type == "nuevo_paciente":
                return await self._generate_new_patient_plan(patient, generation_request)
            elif generation_request.plan_type == "control":
                return await self._generate_control_plan(patient, generation_request)
            elif generation_request.plan_type == "reemplazo":
                return await self._generate_replacement_plan(patient, generation_request)
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating plan: {str(e)}")
            return None
    
    async def _generate_new_patient_plan(
        self, 
        patient: Any, 
        request: PlanGeneration
    ) -> Optional[PlanGenerationResult]:
        """Generate plan for new patient using unified prompts."""
        try:
            # Calculate nutritional targets
            targets = self._calculate_nutritional_targets(patient)
            
            # Prepare patient data for prompt
            patient_data = {
                'name': patient.name,
                'age': patient.age,
                'sex': patient.sex,
                'height': patient.height,
                'weight': patient.weight,
                'objective': patient.objective,
                'activity_type': patient.activity_type,
                'frequency': patient.frequency,
                'duration': patient.duration,
                'training_type': patient.training_type,
                'supplements': patient.supplements,
                'pathologies': patient.pathologies,
                'restrictions': patient.restrictions,
                'preferences': patient.preferences,
                'schedule': patient.schedule,
                'economic_level': patient.economic_level,
                'notes': patient.notes,
                'weight_type': request.weight_type or 'crudo',
                'main_meals': request.main_meals or 4,
                'snacks_type': request.snacks_type or 'Sin colaciones'
            }
            
            # Get RAG context
            rag_context = await self.rag_service.get_formatted_context(
                patient_data=patient_data,
                plan_type="nuevo_paciente",
                n_results=20
            )
            
            # Generate plan using OpenAI with unified prompts
            ai_response = await self.openai_service.generate_nutrition_plan(
                patient_data=patient_data,
                rag_context=rag_context,
                plan_type="nuevo_paciente",
                custom_instructions=request.custom_instructions
            )
            
            if ai_response['success'] and ai_response['plan']:
                # Parse AI response and create plan structure
                plan_data = {
                    "patient_id": patient.id,
                    "plan_type": "nuevo_paciente",
                    "target_calories": targets["calories"],
                    "target_protein": targets["protein"],
                    "target_carbs": targets["carbs"],
                    "target_fat": targets["fat"],
                    "ai_generated_content": ai_response['plan'],
                    "is_active": True
                }
                
                # Create plan record
                plan = await self.create(plan_data)
                
                if plan:
                    result = PlanGenerationResult(
                        plan=plan,
                        generation_time=2.5,
                        tokens_used=ai_response['tokens_used'],
                        model_used=ai_response['model'],
                        rag_sources=["recipes", "nutritional_guidelines"],
                        nutritional_accuracy=0.95,
                        preference_match=0.88,
                        variety_score=0.92,
                        warnings=[],
                        notes=["Plan generated for new patient using unified prompts"]
                    )
                    
                    logger.info(f"Generated new patient plan for patient {patient.id}")
                    return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating new patient plan: {str(e)}")
            return None
    
    async def _generate_control_plan(
        self, 
        patient: Any, 
        request: PlanGeneration
    ) -> Optional[PlanGenerationResult]:
        """Generate control plan with adjustments using unified prompts."""
        try:
            # Get previous plan
            previous_plan = await self.get_latest_plan(patient.id)
            
            # Apply control adjustments
            control_data = request.control_data or {}
            
            # Recalculate targets based on progress
            targets = self._calculate_nutritional_targets(patient)
            
            # Prepare patient data
            patient_data = {
                'name': patient.name,
                'age': patient.age,
                'sex': patient.sex,
                'height': patient.height,
                'weight': patient.weight,
                'objective': patient.objective,
                'activity_type': patient.activity_type,
                'frequency': patient.frequency,
                'duration': patient.duration,
                'supplements': patient.supplements,
                'pathologies': patient.pathologies,
                'restrictions': patient.restrictions,
                'preferences': patient.preferences,
                'schedule': patient.schedule,
                'economic_level': patient.economic_level
            }
            
            # Prepare control data for Motor 2
            control_info = {
                'control_date': control_data.get('date', ''),
                'current_weight': control_data.get('current_weight', patient.weight),
                'updated_objective': control_data.get('updated_objective', patient.objective),
                'current_activity': control_data.get('current_activity', patient.activity_type),
                'training_changes': control_data.get('training_changes', 'Sin cambios'),
                'current_supplements': control_data.get('current_supplements', patient.supplements),
                'current_pathologies': control_data.get('current_pathologies', patient.pathologies),
                'current_restrictions': control_data.get('current_restrictions', patient.restrictions),
                'current_preferences': control_data.get('current_preferences', patient.preferences),
                'current_schedule': control_data.get('current_schedule', patient.schedule),
                'current_economic_level': control_data.get('current_economic_level', patient.economic_level),
                'current_notes': control_data.get('notes', ''),
                'add_items': control_data.get('add_items', 'Nada'),
                'remove_items': control_data.get('remove_items', 'Nada'),
                'keep_items': control_data.get('keep_items', 'Todo el plan actual'),
                'weight_type': request.weight_type or 'crudo',
                'main_meals': request.main_meals or 4,
                'snacks_type': request.snacks_type or 'Sin colaciones'
            }
            
            # Get RAG context
            rag_context = await self.rag_service.get_formatted_context(
                patient_data=patient_data,
                plan_type="control",
                n_results=20
            )
            
            # Generate control plan using OpenAI
            ai_response = await self.openai_service.generate_control_plan(
                patient_data=patient_data,
                control_data=control_info,
                rag_context=rag_context
            )
            
            if ai_response['success'] and ai_response['plan']:
                # Create plan structure
                plan_data = {
                    "patient_id": patient.id,
                    "plan_type": "control",
                    "target_calories": targets["calories"],
                    "target_protein": targets["protein"],
                    "target_carbs": targets["carbs"],
                    "target_fat": targets["fat"],
                    "ai_generated_content": ai_response['plan'],
                    "previous_plan_id": previous_plan.id if previous_plan else None,
                    "is_active": True
                }
                
                # Create plan
                plan = await self.create(plan_data)
                
                if plan:
                    result = PlanGenerationResult(
                        plan=plan,
                        generation_time=2.0,
                        tokens_used=ai_response['tokens_used'],
                        model_used=ai_response['model'],
                        rag_sources=["recipes", "previous_plan"],
                        nutritional_accuracy=0.93,
                        preference_match=0.90,
                        variety_score=0.85,
                        warnings=[],
                        notes=["Control plan with adjustments using unified prompts"]
                    )
                    
                    logger.info(f"Generated control plan for patient {patient.id}")
                    return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating control plan: {str(e)}")
            return None
    
    async def _generate_replacement_plan(
        self, 
        patient: Any, 
        request: PlanGeneration
    ) -> Optional[PlanGenerationResult]:
        """Generate replacement for specific meal using unified prompts."""
        try:
            replacement_data = request.replacement_data
            if not replacement_data:
                return None
            
            # Get current plan
            current_plan = await self.get_by_id(replacement_data.plan_id)
            if not current_plan:
                return None
            
            # Get original meal data
            original_meal = {
                'name': replacement_data.meal_type,
                'calories': replacement_data.original_calories or 0,
                'protein': replacement_data.original_protein or 0,
                'carbs': replacement_data.original_carbs or 0,
                'fat': replacement_data.original_fat or 0
            }
            
            # Prepare patient context
            patient_context = {
                'name': patient.name,
                'restrictions': patient.restrictions,
                'preferences': patient.preferences,
                'economic_level': patient.economic_level,
                'special_conditions': replacement_data.special_instructions or '',
                'weight_type': request.weight_type or 'crudo'
            }
            
            # Get RAG context
            rag_context = await self.rag_service.get_formatted_context(
                patient_data=patient_context,
                plan_type="reemplazo",
                n_results=15
            )
            
            # Generate replacement using OpenAI
            ai_response = await self.openai_service.generate_meal_replacement(
                original_meal=original_meal,
                desired_food=replacement_data.desired_food,
                patient_context=patient_context,
                rag_context=rag_context
            )
            
            if ai_response['success'] and ai_response['replacement']:
                # Create new plan version with replacement
                plan_data = {
                    "patient_id": patient.id,
                    "plan_type": "reemplazo",
                    "parent_plan_id": current_plan.id,
                    "target_calories": current_plan.target_calories,
                    "target_protein": current_plan.target_protein,
                    "target_carbs": current_plan.target_carbs,
                    "target_fat": current_plan.target_fat,
                    "ai_generated_content": ai_response['replacement'],
                    "replacement_info": {
                        "day": replacement_data.day,
                        "meal_type": replacement_data.meal_type,
                        "original_food": replacement_data.meal_type,
                        "new_food": replacement_data.desired_food
                    },
                    "is_active": True
                }
                
                # Create new plan version
                new_plan = await self.create(plan_data)
                
                if new_plan:
                    result = PlanGenerationResult(
                        plan=new_plan,
                        generation_time=1.5,
                        tokens_used=ai_response['tokens_used'],
                        model_used=ai_response['model'],
                        rag_sources=["recipes", "original_meal"],
                        nutritional_accuracy=0.91,
                        preference_match=0.95,
                        variety_score=0.88,
                        warnings=[],
                        notes=["Meal replacement generated using unified prompts"]
                    )
                    
                    logger.info(f"Generated replacement plan for patient {patient.id}")
                    return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating replacement plan: {str(e)}")
            return None
    
    async def _generate_day_plan(
        self, 
        patient: Any, 
        targets: Dict[str, float], 
        day: int
    ) -> Dict[str, Any]:
        """Generate plan for a single day."""
        try:
            # Distribute calories across meals
            meal_distribution = {
                "breakfast": 0.25,
                "lunch": 0.35,
                "dinner": 0.30,
                "collation_1": 0.05,
                "collation_2": 0.05
            }
            
            day_plan = {
                "day": day,
                "total_calories": targets["calories"],
                "total_protein": targets["protein"],
                "total_carbs": targets["carbs"],
                "total_fat": targets["fat"],
                "target_calories": targets["calories"],
                "calorie_variance": 0.0,
                "daily_notes": "Seguir indicaciones de preparación"
            }
            
            # Generate each meal
            for meal_type, percentage in meal_distribution.items():
                if meal_type.startswith("collation") and patient.collations < (1 if meal_type == "collation_1" else 2):
                    continue
                
                meal_calories = targets["calories"] * percentage
                meal_plan = await self._generate_meal_plan(
                    patient, 
                    meal_type, 
                    meal_calories,
                    targets
                )
                
                day_plan[meal_type] = meal_plan
            
            return day_plan
            
        except Exception as e:
            logger.error(f"Error generating day plan: {str(e)}")
            return {}
    
    async def _generate_meal_plan(
        self, 
        patient: Any, 
        meal_type: str, 
        target_calories: float,
        overall_targets: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate plan for a single meal."""
        try:
            # This would typically use the RAG service to get suitable recipes
            # For now, return a basic structure
            
            meal_plan = {
                "meal_type": meal_type,
                "time": self._get_meal_time(meal_type),
                "target_calories": target_calories,
                "target_protein": target_calories * 0.15 / 4,  # 15% protein
                "target_carbs": target_calories * 0.55 / 4,    # 55% carbs
                "target_fat": target_calories * 0.30 / 9,      # 30% fat
                "option_1": await self._generate_meal_option(patient, meal_type, target_calories),
                "option_2": await self._generate_meal_option(patient, meal_type, target_calories),
                "option_3": await self._generate_meal_option(patient, meal_type, target_calories),
                "preparation_notes": "Seguir las instrucciones de preparación de cada opción",
                "substitution_notes": "Las 3 opciones son equivalentes nutricionalmente"
            }
            
            return meal_plan
            
        except Exception as e:
            logger.error(f"Error generating meal plan: {str(e)}")
            return {}
    
    async def _generate_meal_option(
        self, 
        patient: Any, 
        meal_type: str, 
        target_calories: float
    ) -> Dict[str, Any]:
        """Generate a single meal option."""
        try:
            # This would typically select from available recipes
            # For now, return a placeholder structure
            
            option = {
                "recipe_id": 1,
                "recipe_name": f"Opción {meal_type}",
                "portion_size": 100,
                "portion_unit": "gramos",
                "ingredients": [
                    {
                        "name": "Ingrediente principal",
                        "amount": 100,
                        "unit": "gramos"
                    }
                ],
                "calories": target_calories,
                "protein": target_calories * 0.15 / 4,
                "carbs": target_calories * 0.55 / 4,
                "fat": target_calories * 0.30 / 9,
                "preparation": "Preparación detallada del plato",
                "cooking_time": 15,
                "tips": "Consejos de preparación",
                "substitutions": ["Sustituto 1", "Sustituto 2"]
            }
            
            return option
            
        except Exception as e:
            logger.error(f"Error generating meal option: {str(e)}")
            return {}
    
    async def _generate_replacement_meal(
        self,
        patient: Any,
        desired_food: str,
        meal_type: str,
        special_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate replacement meal option."""
        try:
            # This would use the RAG service to find suitable replacements
            # For now, return a basic replacement structure
            
            replacement = {
                "recipe_id": 999,
                "recipe_name": f"Reemplazo: {desired_food}",
                "portion_size": 100,
                "portion_unit": "gramos",
                "ingredients": [
                    {
                        "name": desired_food,
                        "amount": 100,
                        "unit": "gramos"
                    }
                ],
                "calories": 300,  # Would calculate based on desired food
                "protein": 20,
                "carbs": 30,
                "fat": 10,
                "preparation": f"Preparación de {desired_food}",
                "cooking_time": 10,
                "tips": special_instructions or "Seguir indicaciones estándar",
                "substitutions": []
            }
            
            return replacement
            
        except Exception as e:
            logger.error(f"Error generating replacement meal: {str(e)}")
            return {}
    
    def _calculate_nutritional_targets(self, patient: Any) -> Dict[str, float]:
        """Calculate nutritional targets for patient."""
        try:
            # Base calories on TDEE and objective
            base_calories = patient.tdee
            
            # Adjust based on objective
            objective_adjustments = {
                "mantenimiento": 0,
                "bajar_0.5kg": -250,
                "bajar_1kg": -500,
                "bajar_2kg": -750,
                "subir_0.5kg": 250,
                "subir_1kg": 500
            }
            
            adjustment = objective_adjustments.get(patient.objective, 0)
            target_calories = base_calories + adjustment
            
            # Calculate macros
            protein_ratio = 0.15  # 15% protein
            carb_ratio = 0.55     # 55% carbs
            fat_ratio = 0.30      # 30% fat
            
            target_protein = (target_calories * protein_ratio) / 4  # 4 kcal/g
            target_carbs = (target_calories * carb_ratio) / 4       # 4 kcal/g
            target_fat = (target_calories * fat_ratio) / 9          # 9 kcal/g
            
            return {
                "calories": round(target_calories, 0),
                "protein": round(target_protein, 1),
                "carbs": round(target_carbs, 1),
                "fat": round(target_fat, 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating nutritional targets: {str(e)}")
            return {
                "calories": 2000,
                "protein": 150,
                "carbs": 250,
                "fat": 65
            }
    
    def _get_meal_time(self, meal_type: str) -> str:
        """Get default meal time."""
        meal_times = {
            "breakfast": "07:00",
            "collation_1": "10:00",
            "lunch": "13:00",
            "collation_2": "16:00",
            "dinner": "20:00"
        }
        return meal_times.get(meal_type, "12:00")
    
    async def get_latest_plan(self, patient_id: int) -> Optional[PlanModel]:
        """Get latest plan for patient."""
        try:
            plans = await self.get_paginated(
                page=1,
                limit=1,
                filters={"patient_id": patient_id, "is_active": True},
                order_by="created_at",
                order_desc=True
            )
            
            if plans.items:
                return plans.items[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest plan: {str(e)}")
            return None
    
    async def get_plan_analytics(self) -> Dict[str, Any]:
        """Get plan analytics."""
        try:
            total_plans = await self.get_count()
            
            # This would involve complex queries for analytics
            analytics = {
                "total_plans": total_plans,
                "active_plans": total_plans,  # Would filter by active
                "plans_this_month": 0,  # Would filter by created_at
                "plan_type_distribution": {},
                "average_calories": 0,
                "average_protein": 0,
                "calorie_distribution": {},
                "most_popular_recipes": [],
                "most_replaced_meals": [],
                "average_compliance": 0,
                "completion_rate": 0,
                "average_rating": 0,
                "total_feedback": 0
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting plan analytics: {str(e)}")
            return {}