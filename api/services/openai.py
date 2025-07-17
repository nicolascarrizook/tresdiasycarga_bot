"""
OpenAI service for Sistema Mayra API.
"""
import logging
from typing import List, Dict, Any, Optional
import httpx
from openai import AsyncOpenAI

from ..core.config import settings
from config.prompts import (
    SystemPrompts, 
    MotorType, 
    build_complete_prompt,
    format_rag_context,
    validate_prompt_variables
)

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI service for AI operations."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai.api_key,
            timeout=settings.openai.timeout
        )
    
    async def generate_nutrition_plan(
        self,
        patient_data: Dict[str, Any],
        rag_context: str,
        plan_type: str = "nuevo_paciente",
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate nutrition plan using OpenAI with unified prompts."""
        try:
            # Map plan_type to MotorType
            motor_mapping = {
                "nuevo_paciente": MotorType.NEW_PATIENT,
                "control": MotorType.CONTROL,
                "reemplazo": MotorType.REPLACEMENT
            }
            motor_type = motor_mapping.get(plan_type, MotorType.NEW_PATIENT)
            
            # Validate required variables
            validation = validate_prompt_variables(motor_type, patient_data)
            if not validation['valid']:
                logger.warning(f"Missing required variables: {validation['missing_variables']}")
            
            # Build prompts using unified system
            prompts = build_complete_prompt(
                motor_type=motor_type,
                patient_data=patient_data,
                additional_data=patient_data.get('control_data', {}),
                rag_context=rag_context
            )
            
            # Add custom instructions if provided
            user_prompt = prompts['user']
            if custom_instructions:
                user_prompt += f"\n\nINSTRUCCIONES ADICIONALES:\n{custom_instructions}"
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=settings.openai.model,
                messages=[
                    {"role": "system", "content": prompts['system']},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.openai.temperature,
                max_tokens=settings.openai.max_tokens
            )
            
            return {
                "plan": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": settings.openai.model,
                "motor_type": motor_type.value,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating nutrition plan: {str(e)}")
            return {
                "plan": None,
                "error": str(e),
                "success": False
            }
    
    async def generate_meal_replacement(
        self,
        original_meal: Dict[str, Any],
        desired_food: str,
        patient_context: Dict[str, Any],
        rag_context: str
    ) -> Dict[str, Any]:
        """Generate meal replacement using Motor 3."""
        try:
            # Prepare replacement data
            replacement_data = {
                'meal_to_replace': original_meal.get('name', ''),
                'new_meal': desired_food,
                'special_conditions': patient_context.get('special_conditions', ''),
                'original_macros': f"Calorías: {original_meal.get('calories', 0)}, Proteínas: {original_meal.get('protein', 0)}g, Carbohidratos: {original_meal.get('carbs', 0)}g, Grasas: {original_meal.get('fat', 0)}g"
            }
            
            # Build prompts using unified system
            prompts = SystemPrompts.build_motor_3_prompt(
                patient_data=patient_context,
                replacement_data=replacement_data,
                rag_context=rag_context
            )
            
            response = await self.client.chat.completions.create(
                model=settings.openai.model,
                messages=[
                    {"role": "system", "content": prompts['system']},
                    {"role": "user", "content": prompts['user']}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return {
                "replacement": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "motor_type": MotorType.REPLACEMENT.value,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating meal replacement: {str(e)}")
            return {
                "replacement": None,
                "error": str(e),
                "success": False
            }
    
    async def generate_control_plan(
        self,
        patient_data: Dict[str, Any],
        control_data: Dict[str, Any],
        rag_context: str
    ) -> Dict[str, Any]:
        """Generate control/adjustment plan using Motor 2."""
        try:
            # Build prompts using unified system
            prompts = SystemPrompts.build_motor_2_prompt(
                patient_data=patient_data,
                control_data=control_data,
                rag_context=rag_context
            )
            
            response = await self.client.chat.completions.create(
                model=settings.openai.model,
                messages=[
                    {"role": "system", "content": prompts['system']},
                    {"role": "user", "content": prompts['user']}
                ],
                temperature=settings.openai.temperature,
                max_tokens=settings.openai.max_tokens
            )
            
            return {
                "plan": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": settings.openai.model,
                "motor_type": MotorType.CONTROL.value,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating control plan: {str(e)}")
            return {
                "plan": None,
                "error": str(e),
                "success": False
            }
    
    async def check_health(self) -> dict:
        """Check OpenAI service health."""
        try:
            # Simple test request
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "model": settings.openai.model,
                "available": True
            }
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "available": False
            }