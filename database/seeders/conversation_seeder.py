"""
Conversation seeder for Sistema Mayra database.
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from database.models.conversation import Conversation, ConversationStatusEnum, ConversationMotorEnum
from database.seeders.base import BaseSeeder


class ConversationSeeder(BaseSeeder):
    """Seeder for creating initial conversations."""
    
    def get_seeder_name(self) -> str:
        return "ConversationSeeder"
    
    async def seed(self) -> Dict[str, Any]:
        """Create initial conversations."""
        self.log_info("Starting conversation seeding...")
        
        # Create test conversations
        test_conversations = await self.create_test_conversations()
        
        return {
            "seeder": self.get_seeder_name(),
            "success": True,
            "created_count": len(self.created_records),
            "test_conversations_count": len(test_conversations),
            "timestamp": datetime.utcnow()
        }
    
    async def create_test_conversations(self) -> List[Conversation]:
        """Create test conversations for development."""
        test_conversations = []
        
        # Conversation 1: Completed new patient onboarding
        conversation1 = Conversation(
            patient_id=1,  # María González
            telegram_chat_id=123456789,
            motor=ConversationMotorEnum.NEW_PATIENT,
            status=ConversationStatusEnum.COMPLETED,
            started_at=datetime.utcnow() - timedelta(days=60),
            completed_at=datetime.utcnow() - timedelta(days=60, minutes=30),
            last_message_at=datetime.utcnow() - timedelta(days=60, minutes=30),
            message_count=15,
            progress_data={
                "current_step": "completed",
                "steps_completed": [
                    "greeting",
                    "personal_info",
                    "physical_measurements",
                    "goals",
                    "preferences",
                    "restrictions",
                    "plan_generation",
                    "plan_presentation"
                ],
                "collected_data": {
                    "name": "María González",
                    "age": 28,
                    "sex": "female",
                    "height": 165,
                    "weight": 75,
                    "objective": "weight_loss",
                    "target_weight": 60,
                    "activity_level": "moderate",
                    "economic_level": "medio",
                    "pathologies": ["hipertension"],
                    "restrictions": ["lactosa"],
                    "preferences": ["vegetales", "pescado"]
                }
            },
            messages_history=[
                {
                    "timestamp": "2024-01-01T10:00:00Z",
                    "role": "assistant",
                    "content": "¡Hola María! Soy el asistente nutricional de Mayra. Te ayudaré a crear un plan personalizado. ¿Empezamos?",
                    "message_type": "greeting"
                },
                {
                    "timestamp": "2024-01-01T10:01:00Z",
                    "role": "user",
                    "content": "Sí, estoy lista",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-01-01T10:02:00Z",
                    "role": "assistant",
                    "content": "Perfecto. Para comenzar, necesito conocer tu información básica. ¿Cuál es tu edad?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-01-01T10:03:00Z",
                    "role": "user",
                    "content": "Tengo 28 años",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-01-01T10:04:00Z",
                    "role": "assistant",
                    "content": "¿Cuál es tu peso actual y tu estatura?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-01-01T10:05:00Z",
                    "role": "user",
                    "content": "Peso 75 kg y mido 1.65 m",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-01-01T10:06:00Z",
                    "role": "assistant",
                    "content": "¿Cuál es tu objetivo principal? ¿Quieres perder peso, mantenerlo o ganar masa muscular?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-01-01T10:07:00Z",
                    "role": "user",
                    "content": "Quiero perder peso, llegar a 60 kg",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-01-01T10:08:00Z",
                    "role": "assistant",
                    "content": "Excelente meta. ¿Tienes alguna condición médica o restricción alimentaria?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-01-01T10:09:00Z",
                    "role": "user",
                    "content": "Tengo hipertensión y soy intolerante a la lactosa",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-01-01T10:10:00Z",
                    "role": "assistant",
                    "content": "¿Qué alimentos te gustan más? ¿Tienes alguna preferencia especial?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-01-01T10:11:00Z",
                    "role": "user",
                    "content": "Me gustan mucho las verduras y el pescado",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-01-01T10:15:00Z",
                    "role": "assistant",
                    "content": "Perfecto. Con toda esta información, he creado un plan personalizado para ti. Es un plan de 30 días enfocado en pérdida de peso gradual, bajo en sodio y sin lactosa, con muchas verduras y pescado. ¿Te parece bien?",
                    "message_type": "plan_presentation"
                },
                {
                    "timestamp": "2024-01-01T10:16:00Z",
                    "role": "user",
                    "content": "¡Sí! Me parece perfecto",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-01-01T10:17:00Z",
                    "role": "assistant",
                    "content": "¡Excelente! Tu plan ya está activado. Te enviaré recordatorios y podemos hacer ajustes cuando lo necesites. ¡Mucho éxito en tu proceso!",
                    "message_type": "completion"
                }
            ],
            created_at=datetime.utcnow() - timedelta(days=60),
            updated_at=datetime.utcnow() - timedelta(days=60, minutes=30)
        )
        test_conversations.append(conversation1)
        
        # Conversation 2: Active control conversation
        conversation2 = Conversation(
            patient_id=2,  # Carlos Rodríguez
            telegram_chat_id=987654321,
            motor=ConversationMotorEnum.CONTROL_ADJUSTMENT,
            status=ConversationStatusEnum.ACTIVE,
            started_at=datetime.utcnow() - timedelta(hours=2),
            completed_at=None,
            last_message_at=datetime.utcnow() - timedelta(minutes=15),
            message_count=8,
            progress_data={
                "current_step": "feedback_collection",
                "steps_completed": [
                    "greeting",
                    "weight_check",
                    "adherence_review"
                ],
                "collected_data": {
                    "current_weight": 78,
                    "weight_change": 3,
                    "adherence_level": "high",
                    "difficulties": ["meal_timing"],
                    "satisfaction": "very_satisfied"
                }
            },
            messages_history=[
                {
                    "timestamp": "2024-03-15T14:00:00Z",
                    "role": "assistant",
                    "content": "¡Hola Carlos! Es hora de tu control semanal. ¿Cómo te has sentido con el plan?",
                    "message_type": "greeting"
                },
                {
                    "timestamp": "2024-03-15T14:01:00Z",
                    "role": "user",
                    "content": "¡Muy bien! He notado buenos cambios",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-03-15T14:02:00Z",
                    "role": "assistant",
                    "content": "¡Excelente! ¿Cuál es tu peso actual?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-03-15T14:03:00Z",
                    "role": "user",
                    "content": "78 kg, he subido 3 kg desde que empecé",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-03-15T14:04:00Z",
                    "role": "assistant",
                    "content": "¡Perfecto! Esa es una ganancia saludable. ¿Has podido seguir el plan sin problemas?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-03-15T14:05:00Z",
                    "role": "user",
                    "content": "Sí, aunque a veces se me complica el timing de las comidas por los entrenamientos",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-03-15T14:06:00Z",
                    "role": "assistant",
                    "content": "Entiendo. ¿Qué horarios de entrenamiento tienes?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-03-15T14:10:00Z",
                    "role": "user",
                    "content": "Entreno de 7 a 9 pm de lunes a viernes",
                    "message_type": "response"
                }
            ],
            created_at=datetime.utcnow() - timedelta(hours=2),
            updated_at=datetime.utcnow() - timedelta(minutes=15)
        )
        test_conversations.append(conversation2)
        
        # Conversation 3: Completed meal replacement
        conversation3 = Conversation(
            patient_id=3,  # Ana Martínez
            telegram_chat_id=456789123,
            motor=ConversationMotorEnum.MEAL_REPLACEMENT,
            status=ConversationStatusEnum.COMPLETED,
            started_at=datetime.utcnow() - timedelta(days=2),
            completed_at=datetime.utcnow() - timedelta(days=2, minutes=10),
            last_message_at=datetime.utcnow() - timedelta(days=2, minutes=10),
            message_count=6,
            progress_data={
                "current_step": "completed",
                "steps_completed": [
                    "greeting",
                    "meal_identification",
                    "preferences_check",
                    "replacement_suggestion",
                    "confirmation"
                ],
                "collected_data": {
                    "original_meal": "arroz con pollo",
                    "meal_type": "lunch",
                    "reason": "high_carb",
                    "replacement_meal": "ensalada de pollo con verduras",
                    "accepted": True
                }
            },
            messages_history=[
                {
                    "timestamp": "2024-03-13T12:00:00Z",
                    "role": "user",
                    "content": "Hola, necesito cambiar el almuerzo de hoy",
                    "message_type": "request"
                },
                {
                    "timestamp": "2024-03-13T12:01:00Z",
                    "role": "assistant",
                    "content": "¡Hola Ana! Claro, te ayudo. ¿Qué comida querías cambiar y por qué?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-03-13T12:02:00Z",
                    "role": "user",
                    "content": "El arroz con pollo del almuerzo. Siento que tiene muchos carbohidratos",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-03-13T12:03:00Z",
                    "role": "assistant",
                    "content": "Entiendo tu preocupación. Te sugiero una ensalada de pollo con aguacate y verduras mixtas. Tiene menos carbohidratos pero mantiene la proteína. ¿Te parece bien?",
                    "message_type": "suggestion"
                },
                {
                    "timestamp": "2024-03-13T12:04:00Z",
                    "role": "user",
                    "content": "Perfecto, me encanta esa opción",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-03-13T12:05:00Z",
                    "role": "assistant",
                    "content": "¡Excelente! He actualizado tu plan. La ensalada de pollo es perfecta para tu control glucémico. ¡Que disfrutes tu almuerzo!",
                    "message_type": "confirmation"
                }
            ],
            created_at=datetime.utcnow() - timedelta(days=2),
            updated_at=datetime.utcnow() - timedelta(days=2, minutes=10)
        )
        test_conversations.append(conversation3)
        
        # Conversation 4: Failed conversation
        conversation4 = Conversation(
            patient_id=4,  # Luis Fernández
            telegram_chat_id=789123456,
            motor=ConversationMotorEnum.NEW_PATIENT,
            status=ConversationStatusEnum.FAILED,
            started_at=datetime.utcnow() - timedelta(days=150),
            completed_at=None,
            last_message_at=datetime.utcnow() - timedelta(days=149),
            message_count=3,
            progress_data={
                "current_step": "personal_info",
                "steps_completed": [
                    "greeting"
                ],
                "collected_data": {
                    "name": "Luis Fernández"
                }
            },
            messages_history=[
                {
                    "timestamp": "2023-10-01T15:00:00Z",
                    "role": "assistant",
                    "content": "¡Hola Luis! Soy el asistente nutricional de Mayra. Te ayudaré a crear un plan personalizado. ¿Empezamos?",
                    "message_type": "greeting"
                },
                {
                    "timestamp": "2023-10-01T15:01:00Z",
                    "role": "user",
                    "content": "Ok",
                    "message_type": "response"
                },
                {
                    "timestamp": "2023-10-01T15:02:00Z",
                    "role": "assistant",
                    "content": "Perfecto. Para comenzar, necesito conocer tu información básica. ¿Cuál es tu edad?",
                    "message_type": "question"
                }
            ],
            error_message="Conversation abandoned by user after initial contact",
            created_at=datetime.utcnow() - timedelta(days=150),
            updated_at=datetime.utcnow() - timedelta(days=149)
        )
        test_conversations.append(conversation4)
        
        # Conversation 5: Recent active conversation
        conversation5 = Conversation(
            patient_id=6,  # Diego Morales
            telegram_chat_id=654321789,
            motor=ConversationMotorEnum.CONTROL_ADJUSTMENT,
            status=ConversationStatusEnum.ACTIVE,
            started_at=datetime.utcnow() - timedelta(hours=1),
            completed_at=None,
            last_message_at=datetime.utcnow() - timedelta(minutes=5),
            message_count=12,
            progress_data={
                "current_step": "adjustment_recommendations",
                "steps_completed": [
                    "greeting",
                    "weight_check",
                    "adherence_review",
                    "performance_check",
                    "feedback_collection"
                ],
                "collected_data": {
                    "current_weight": 78,
                    "weight_change": 2,
                    "adherence_level": "excellent",
                    "performance_level": "improved",
                    "energy_levels": "high",
                    "training_intensity": "increased"
                }
            },
            messages_history=[
                {
                    "timestamp": "2024-03-17T15:00:00Z",
                    "role": "assistant",
                    "content": "¡Hola Diego! Es hora de tu control semanal. ¿Cómo te has sentido con el plan?",
                    "message_type": "greeting"
                },
                {
                    "timestamp": "2024-03-17T15:01:00Z",
                    "role": "user",
                    "content": "¡Increíble! Me siento con mucha más energía",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-03-17T15:02:00Z",
                    "role": "assistant",
                    "content": "¡Excelente! ¿Cuál es tu peso actual?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-03-17T15:03:00Z",
                    "role": "user",
                    "content": "78 kg, he subido 2 kg desde la semana pasada",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-03-17T15:04:00Z",
                    "role": "assistant",
                    "content": "¡Perfecto! ¿Has podido seguir todas las comidas del plan?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-03-17T15:05:00Z",
                    "role": "user",
                    "content": "Sí, al 100%. Me está gustando mucho",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-03-17T15:06:00Z",
                    "role": "assistant",
                    "content": "¿Cómo te sientes durante los entrenamientos?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-03-17T15:07:00Z",
                    "role": "user",
                    "content": "Mucho mejor, tengo más fuerza y resistencia",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-03-17T15:08:00Z",
                    "role": "assistant",
                    "content": "¡Fantástico! ¿Has aumentado la intensidad de tus entrenamientos?",
                    "message_type": "question"
                },
                {
                    "timestamp": "2024-03-17T15:09:00Z",
                    "role": "user",
                    "content": "Sí, he agregado más peso y más repeticiones",
                    "message_type": "response"
                },
                {
                    "timestamp": "2024-03-17T15:10:00Z",
                    "role": "assistant",
                    "content": "Perfecto. Con base en tu progreso, te sugiero aumentar ligeramente las porciones de proteína post-entrenamiento. ¿Te parece bien?",
                    "message_type": "suggestion"
                },
                {
                    "timestamp": "2024-03-17T15:11:00Z",
                    "role": "user",
                    "content": "Sí, me parece excelente",
                    "message_type": "response"
                }
            ],
            created_at=datetime.utcnow() - timedelta(hours=1),
            updated_at=datetime.utcnow() - timedelta(minutes=5)
        )
        test_conversations.append(conversation5)
        
        await self.commit_batch(test_conversations, "test conversations")
        return test_conversations