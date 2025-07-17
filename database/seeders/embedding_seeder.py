"""
Embedding seeder for Sistema Mayra database.
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from database.models.embedding import Embedding, EmbeddingTypeEnum, EmbeddingSourceTypeEnum
from database.seeders.base import BaseSeeder


class EmbeddingSeeder(BaseSeeder):
    """Seeder for creating initial embeddings."""
    
    def get_seeder_name(self) -> str:
        return "EmbeddingSeeder"
    
    async def seed(self) -> Dict[str, Any]:
        """Create initial embeddings."""
        self.log_info("Starting embedding seeding...")
        
        # Create recipe embeddings
        recipe_embeddings = await self.create_recipe_embeddings()
        
        # Create nutrition knowledge embeddings
        nutrition_embeddings = await self.create_nutrition_embeddings()
        
        # Create FAQ embeddings
        faq_embeddings = await self.create_faq_embeddings()
        
        return {
            "seeder": self.get_seeder_name(),
            "success": True,
            "created_count": len(self.created_records),
            "recipe_embeddings_count": len(recipe_embeddings),
            "nutrition_embeddings_count": len(nutrition_embeddings),
            "faq_embeddings_count": len(faq_embeddings),
            "timestamp": datetime.utcnow()
        }
    
    async def create_recipe_embeddings(self) -> List[Embedding]:
        """Create recipe embeddings for semantic search."""
        recipe_embeddings = []
        
        # Embedding 1: Breakfast recipe
        embedding1 = Embedding(
            content="Avena con frutas y canela es un desayuno nutritivo rico en fibra que ayuda a mantener la saciedad. Contiene carbohidratos complejos que proporcionan energía sostenida durante la mañana. La canela ayuda a regular los niveles de azúcar en sangre y las frutas aportan vitaminas y antioxidantes. Es una excelente opción para personas que buscan perder peso de manera saludable.",
            embedding_type=EmbeddingTypeEnum.RECIPE,
            source_type=EmbeddingSourceTypeEnum.RECIPE,
            source_id=1,
            chromadb_id="recipe_avena_frutas_001",
            vector_embedding=[0.1, 0.2, 0.3, 0.4, 0.5] * 300,  # Mock 1536-dimensional vector
            metadata_json={
                "recipe_name": "Avena con frutas y canela",
                "category": "breakfast",
                "economic_level": "bajo",
                "difficulty": "easy",
                "calories": 280,
                "protein": 8.5,
                "keywords": ["avena", "frutas", "canela", "desayuno", "fibra", "saciedad"]
            },
            language="es",
            content_length=len("Avena con frutas y canela es un desayuno nutritivo rico en fibra que ayuda a mantener la saciedad. Contiene carbohidratos complejos que proporcionan energía sostenida durante la mañana. La canela ayuda a regular los niveles de azúcar en sangre y las frutas aportan vitaminas y antioxidantes. Es una excelente opción para personas que buscan perder peso de manera saludable."),
            word_count=50,
            quality_score=0.95,
            created_at=datetime.utcnow() - timedelta(days=30),
            updated_at=datetime.utcnow() - timedelta(days=30),
            retrieval_count=15,
            last_retrieved_at=datetime.utcnow() - timedelta(days=1)
        )
        recipe_embeddings.append(embedding1)
        
        # Embedding 2: Lunch recipe
        embedding2 = Embedding(
            content="Ensalada de pollo con aguacate es una comida completa que combina proteína magra con grasas saludables. El pollo proporciona aminoácidos esenciales para la construcción muscular, mientras que el aguacate aporta ácidos grasos monoinsaturados que favorecen la salud cardiovascular. Las verduras mixtas añaden fibra, vitaminas y minerales. Es ideal para personas que buscan mantener o perder peso.",
            embedding_type=EmbeddingTypeEnum.RECIPE,
            source_type=EmbeddingSourceTypeEnum.RECIPE,
            source_id=4,
            chromadb_id="recipe_ensalada_pollo_002",
            vector_embedding=[0.2, 0.3, 0.4, 0.5, 0.6] * 300,
            metadata_json={
                "recipe_name": "Ensalada de pollo con aguacate",
                "category": "lunch",
                "economic_level": "medio",
                "difficulty": "medium",
                "calories": 350,
                "protein": 25.0,
                "keywords": ["pollo", "aguacate", "ensalada", "proteína", "grasas_saludables"]
            },
            language="es",
            content_length=len("Ensalada de pollo con aguacate es una comida completa que combina proteína magra con grasas saludables. El pollo proporciona aminoácidos esenciales para la construcción muscular, mientras que el aguacate aporta ácidos grasos monoinsaturados que favorecen la salud cardiovascular. Las verduras mixtas añaden fibra, vitaminas y minerales. Es ideal para personas que buscan mantener o perder peso."),
            word_count=48,
            quality_score=0.92,
            created_at=datetime.utcnow() - timedelta(days=28),
            updated_at=datetime.utcnow() - timedelta(days=28),
            retrieval_count=22,
            last_retrieved_at=datetime.utcnow() - timedelta(hours=12)
        )
        recipe_embeddings.append(embedding2)
        
        # Embedding 3: Dinner recipe
        embedding3 = Embedding(
            content="Salmón al horno con verduras es una cena perfecta para obtener omega-3 y proteínas de alta calidad. El salmón es rico en ácidos grasos esenciales que reducen la inflamación y mejoran la función cerebral. Las verduras al horno conservan mejor sus nutrientes y tienen un sabor intenso. Esta combinación es ideal para personas que buscan mejorar su salud cardiovascular.",
            embedding_type=EmbeddingTypeEnum.RECIPE,
            source_type=EmbeddingSourceTypeEnum.RECIPE,
            source_id=5,
            chromadb_id="recipe_salmon_horno_003",
            vector_embedding=[0.3, 0.4, 0.5, 0.6, 0.7] * 300,
            metadata_json={
                "recipe_name": "Salmón al horno con verduras",
                "category": "dinner",
                "economic_level": "alto",
                "difficulty": "medium",
                "calories": 420,
                "protein": 35.0,
                "keywords": ["salmón", "omega3", "verduras", "horno", "antiinflamatorio"]
            },
            language="es",
            content_length=len("Salmón al horno con verduras es una cena perfecta para obtener omega-3 y proteínas de alta calidad. El salmón es rico en ácidos grasos esenciales que reducen la inflamación y mejoran la función cerebral. Las verduras al horno conservan mejor sus nutrientes y tienen un sabor intenso. Esta combinación es ideal para personas que buscan mejorar su salud cardiovascular."),
            word_count=45,
            quality_score=0.94,
            created_at=datetime.utcnow() - timedelta(days=25),
            updated_at=datetime.utcnow() - timedelta(days=25),
            retrieval_count=18,
            last_retrieved_at=datetime.utcnow() - timedelta(hours=6)
        )
        recipe_embeddings.append(embedding3)
        
        await self.commit_batch(recipe_embeddings, "recipe embeddings")
        return recipe_embeddings
    
    async def create_nutrition_embeddings(self) -> List[Embedding]:
        """Create nutrition knowledge embeddings."""
        nutrition_embeddings = []
        
        # Embedding 1: Weight loss knowledge
        embedding1 = Embedding(
            content="La pérdida de peso saludable requiere un déficit calórico moderado de 300-500 calorías diarias. Es importante mantener un equilibrio entre macronutrientes: 25-30% proteínas, 45-50% carbohidratos complejos y 20-25% grasas saludables. La pérdida recomendada es de 0.5-1 kg por semana para evitar pérdida de masa muscular. El ejercicio regular potencia los resultados.",
            embedding_type=EmbeddingTypeEnum.NUTRITION_KNOWLEDGE,
            source_type=EmbeddingSourceTypeEnum.KNOWLEDGE_BASE,
            source_id=None,
            chromadb_id="nutrition_weight_loss_001",
            vector_embedding=[0.4, 0.5, 0.6, 0.7, 0.8] * 300,
            metadata_json={
                "topic": "weight_loss",
                "category": "nutrition_basics",
                "keywords": ["pérdida_peso", "déficit_calórico", "macronutrientes", "ejercicio"]
            },
            language="es",
            content_length=len("La pérdida de peso saludable requiere un déficit calórico moderado de 300-500 calorías diarias. Es importante mantener un equilibrio entre macronutrientes: 25-30% proteínas, 45-50% carbohidratos complejos y 20-25% grasas saludables. La pérdida recomendada es de 0.5-1 kg por semana para evitar pérdida de masa muscular. El ejercicio regular potencia los resultados."),
            word_count=52,
            quality_score=0.97,
            created_at=datetime.utcnow() - timedelta(days=20),
            updated_at=datetime.utcnow() - timedelta(days=20),
            retrieval_count=35,
            last_retrieved_at=datetime.utcnow() - timedelta(hours=3)
        )
        nutrition_embeddings.append(embedding1)
        
        # Embedding 2: Muscle gain knowledge
        embedding2 = Embedding(
            content="Para ganar masa muscular es necesario un superávit calórico de 200-500 calorías diarias combinado con entrenamiento de resistencia. La proteína debe representar 1.6-2.2g por kg de peso corporal. Los carbohidratos son fundamentales para la recuperación muscular y deben consumirse especialmente después del entrenamiento. La hidratación adecuada y el descanso son igualmente importantes.",
            embedding_type=EmbeddingTypeEnum.NUTRITION_KNOWLEDGE,
            source_type=EmbeddingSourceTypeEnum.KNOWLEDGE_BASE,
            source_id=None,
            chromadb_id="nutrition_muscle_gain_002",
            vector_embedding=[0.5, 0.6, 0.7, 0.8, 0.9] * 300,
            metadata_json={
                "topic": "muscle_gain",
                "category": "sports_nutrition",
                "keywords": ["masa_muscular", "superávit_calórico", "proteína", "entrenamiento"]
            },
            language="es",
            content_length=len("Para ganar masa muscular es necesario un superávit calórico de 200-500 calorías diarias combinado con entrenamiento de resistencia. La proteína debe representar 1.6-2.2g por kg de peso corporal. Los carbohidratos son fundamentales para la recuperación muscular y deben consumirse especialmente después del entrenamiento. La hidratación adecuada y el descanso son igualmente importantes."),
            word_count=48,
            quality_score=0.96,
            created_at=datetime.utcnow() - timedelta(days=18),
            updated_at=datetime.utcnow() - timedelta(days=18),
            retrieval_count=28,
            last_retrieved_at=datetime.utcnow() - timedelta(hours=8)
        )
        nutrition_embeddings.append(embedding2)
        
        # Embedding 3: Diabetes nutrition
        embedding3 = Embedding(
            content="La alimentación para personas con diabetes debe enfocarse en controlar los niveles de glucosa en sangre. Se recomienda consumir carbohidratos complejos con bajo índice glucémico, como quinoa, avena y vegetales. Las porciones deben ser moderadas y distribuidas en 5-6 comidas pequeñas al día. Las fibras ayudan a ralentizar la absorción de glucosa. Es importante evitar azúcares simples y harinas refinadas.",
            embedding_type=EmbeddingTypeEnum.NUTRITION_KNOWLEDGE,
            source_type=EmbeddingSourceTypeEnum.KNOWLEDGE_BASE,
            source_id=None,
            chromadb_id="nutrition_diabetes_003",
            vector_embedding=[0.6, 0.7, 0.8, 0.9, 1.0] * 300,
            metadata_json={
                "topic": "diabetes",
                "category": "medical_nutrition",
                "keywords": ["diabetes", "glucosa", "índice_glucémico", "fibra"]
            },
            language="es",
            content_length=len("La alimentación para personas con diabetes debe enfocarse en controlar los niveles de glucosa en sangre. Se recomienda consumir carbohidratos complejos con bajo índice glucémico, como quinoa, avena y vegetales. Las porciones deben ser moderadas y distribuidas en 5-6 comidas pequeñas al día. Las fibras ayudan a ralentizar la absorción de glucosa. Es importante evitar azúcares simples y harinas refinadas."),
            word_count=55,
            quality_score=0.98,
            created_at=datetime.utcnow() - timedelta(days=15),
            updated_at=datetime.utcnow() - timedelta(days=15),
            retrieval_count=42,
            last_retrieved_at=datetime.utcnow() - timedelta(hours=2)
        )
        nutrition_embeddings.append(embedding3)
        
        await self.commit_batch(nutrition_embeddings, "nutrition knowledge embeddings")
        return nutrition_embeddings
    
    async def create_faq_embeddings(self) -> List[Embedding]:
        """Create FAQ embeddings for common questions."""
        faq_embeddings = []
        
        # Embedding 1: Plan flexibility
        embedding1 = Embedding(
            content="¿Puedo cambiar comidas del plan? Sí, puedes cambiar comidas manteniendo el equilibrio nutricional. El sistema te sugerirá alternativas equivalentes en calorías y macronutrientes. Es importante mantener la estructura del plan pero tienes flexibilidad para adaptar las comidas a tus preferencias y disponibilidad de ingredientes.",
            embedding_type=EmbeddingTypeEnum.FAQ,
            source_type=EmbeddingSourceTypeEnum.FAQ,
            source_id=None,
            chromadb_id="faq_meal_changes_001",
            vector_embedding=[0.7, 0.8, 0.9, 1.0, 0.9] * 300,
            metadata_json={
                "question": "¿Puedo cambiar comidas del plan?",
                "category": "plan_flexibility",
                "keywords": ["cambiar_comidas", "flexibilidad", "alternativas", "equilibrio_nutricional"]
            },
            language="es",
            content_length=len("¿Puedo cambiar comidas del plan? Sí, puedes cambiar comidas manteniendo el equilibrio nutricional. El sistema te sugerirá alternativas equivalentes en calorías y macronutrientes. Es importante mantener la estructura del plan pero tienes flexibilidad para adaptar las comidas a tus preferencias y disponibilidad de ingredientes."),
            word_count=40,
            quality_score=0.93,
            created_at=datetime.utcnow() - timedelta(days=10),
            updated_at=datetime.utcnow() - timedelta(days=10),
            retrieval_count=55,
            last_retrieved_at=datetime.utcnow() - timedelta(hours=4)
        )
        faq_embeddings.append(embedding1)
        
        # Embedding 2: Weight plateau
        embedding2 = Embedding(
            content="¿Qué hago si no bajo más de peso? Los plateaus son normales en el proceso de pérdida de peso. Tu cuerpo se adapta al déficit calórico. Puedes ajustar las porciones ligeramente, aumentar la actividad física o cambiar el tipo de ejercicio. A veces es necesario un descanso metabólico comiendo a mantenimiento por una semana.",
            embedding_type=EmbeddingTypeEnum.FAQ,
            source_type=EmbeddingSourceTypeEnum.FAQ,
            source_id=None,
            chromadb_id="faq_weight_plateau_002",
            vector_embedding=[0.8, 0.9, 1.0, 0.9, 0.8] * 300,
            metadata_json={
                "question": "¿Qué hago si no bajo más de peso?",
                "category": "weight_loss_issues",
                "keywords": ["plateau", "estancamiento", "ajustar_porciones", "actividad_física"]
            },
            language="es",
            content_length=len("¿Qué hago si no bajo más de peso? Los plateaus son normales en el proceso de pérdida de peso. Tu cuerpo se adapta al déficit calórico. Puedes ajustar las porciones ligeramente, aumentar la actividad física o cambiar el tipo de ejercicio. A veces es necesario un descanso metabólico comiendo a mantenimiento por una semana."),
            word_count=46,
            quality_score=0.95,
            created_at=datetime.utcnow() - timedelta(days=8),
            updated_at=datetime.utcnow() - timedelta(days=8),
            retrieval_count=38,
            last_retrieved_at=datetime.utcnow() - timedelta(hours=1)
        )
        faq_embeddings.append(embedding2)
        
        # Embedding 3: Meal timing
        embedding3 = Embedding(
            content="¿A qué hora debo comer cada comida? Los horarios pueden ser flexibles según tu rutina. Lo importante es mantener intervalos regulares entre comidas (3-4 horas) y no saltear ninguna. El desayuno dentro de la primera hora de levantarse, el almuerzo entre 12-14h, la cena antes de las 21h y snacks según necesidad.",
            embedding_type=EmbeddingTypeEnum.FAQ,
            source_type=EmbeddingSourceTypeEnum.FAQ,
            source_id=None,
            chromadb_id="faq_meal_timing_003",
            vector_embedding=[0.9, 1.0, 0.9, 0.8, 0.7] * 300,
            metadata_json={
                "question": "¿A qué hora debo comer cada comida?",
                "category": "meal_timing",
                "keywords": ["horarios", "intervalos", "flexibilidad", "rutina"]
            },
            language="es",
            content_length=len("¿A qué hora debo comer cada comida? Los horarios pueden ser flexibles según tu rutina. Lo importante es mantener intervalos regulares entre comidas (3-4 horas) y no saltear ninguna. El desayuno dentro de la primera hora de levantarse, el almuerzo entre 12-14h, la cena antes de las 21h y snacks según necesidad."),
            word_count=45,
            quality_score=0.91,
            created_at=datetime.utcnow() - timedelta(days=5),
            updated_at=datetime.utcnow() - timedelta(days=5),
            retrieval_count=29,
            last_retrieved_at=datetime.utcnow() - timedelta(hours=5)
        )
        faq_embeddings.append(embedding3)
        
        await self.commit_batch(faq_embeddings, "FAQ embeddings")
        return faq_embeddings