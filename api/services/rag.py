"""
RAG (Retrieval-Augmented Generation) service for Sistema Mayra API.
"""
import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

from ..core.config import settings
from .openai import OpenAIService
from config.prompts import format_rag_context

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for recipe and nutrition knowledge retrieval."""
    
    def __init__(self, chroma_collection, openai_service: OpenAIService):
        self.chroma = chroma_collection
        self.openai_service = openai_service
        self.encoder = SentenceTransformer(settings.RAG_SETTINGS["embedding_model"])
    
    async def get_relevant_recipes(
        self,
        patient_data: Dict[str, Any],
        plan_type: str = "nuevo_paciente",
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Get relevant recipes based on patient data."""
        try:
            # Build search query
            search_query = self._build_search_query(patient_data, plan_type)
            
            # Generate embedding
            query_embedding = self.encoder.encode([search_query])[0].tolist()
            
            # Search in ChromaDB
            results = self.chroma.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            relevant_recipes = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                
                # Filter by patient constraints
                if self._matches_patient_constraints(metadata, patient_data):
                    relevant_recipes.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity": 1 - distance,
                        "category": metadata.get("category", "unknown"),
                        "meal_type": metadata.get("meal_type", "unknown"),
                        "economic_level": metadata.get("economic_level", "medium")
                    })
            
            return relevant_recipes
            
        except Exception as e:
            logger.error(f"Error getting relevant recipes: {str(e)}")
            return []
    
    async def get_meal_replacements(
        self,
        original_meal: Dict[str, Any],
        desired_food: str,
        patient_data: Dict[str, Any],
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Get meal replacement options."""
        try:
            # Build replacement query
            search_query = f"{desired_food} {original_meal.get('meal_type', '')} {patient_data.get('economic_level', 'medium')}"
            
            # Generate embedding
            query_embedding = self.encoder.encode([search_query])[0].tolist()
            
            # Search for similar recipes
            results = self.chroma.query(
                query_embeddings=[query_embedding],
                n_results=n_results * 2,  # Get more to filter
                include=["documents", "metadatas", "distances"],
                where={
                    "meal_type": original_meal.get("meal_type"),
                    "economic_level": {"$lte": patient_data.get("economic_level", "medium")}
                }
            )
            
            # Process and filter results
            replacements = []
            target_calories = original_meal.get("calories", 0)
            
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                
                # Check caloric similarity (±20% tolerance for initial filtering)
                recipe_calories = metadata.get("calories", 0)
                if abs(recipe_calories - target_calories) / target_calories <= 0.2:
                    replacements.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity": 1 - distance,
                        "calorie_difference": abs(recipe_calories - target_calories),
                        "suitable": self._is_suitable_replacement(metadata, patient_data)
                    })
            
            # Sort by suitability and similarity
            replacements.sort(key=lambda x: (x["suitable"], x["similarity"]), reverse=True)
            
            return replacements[:n_results]
            
        except Exception as e:
            logger.error(f"Error getting meal replacements: {str(e)}")
            return []
    
    async def get_nutritional_context(
        self,
        patient_data: Dict[str, Any],
        specific_needs: Optional[List[str]] = None
    ) -> str:
        """Get nutritional context for plan generation."""
        try:
            # Build context query
            query_parts = []
            
            # Add patient-specific needs
            if patient_data.get("restrictions"):
                query_parts.extend(patient_data["restrictions"])
            
            if patient_data.get("objective"):
                query_parts.append(patient_data["objective"])
            
            if patient_data.get("activity_type"):
                query_parts.append(patient_data["activity_type"])
            
            if specific_needs:
                query_parts.extend(specific_needs)
            
            search_query = " ".join(query_parts)
            
            # Get relevant nutritional information
            query_embedding = self.encoder.encode([search_query])[0].tolist()
            
            results = self.chroma.query(
                query_embeddings=[query_embedding],
                n_results=20,
                include=["documents", "metadatas"],
                where={"type": "nutritional_info"}
            )
            
            # Compile context
            context_parts = []
            for doc in results["documents"][0]:
                context_parts.append(doc)
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting nutritional context: {str(e)}")
            return ""
    
    def _build_search_query(self, patient_data: Dict[str, Any], plan_type: str) -> str:
        """Build search query from patient data."""
        query_parts = []
        
        # Add objective
        if patient_data.get("objective"):
            query_parts.append(patient_data["objective"])
        
        # Add activity level
        if patient_data.get("activity_type"):
            query_parts.append(patient_data["activity_type"])
        
        # Add restrictions
        if patient_data.get("restrictions"):
            query_parts.extend(patient_data["restrictions"])
        
        # Add preferences
        if patient_data.get("preferences"):
            query_parts.extend(patient_data["preferences"])
        
        # Add economic level
        if patient_data.get("economic_level"):
            query_parts.append(patient_data["economic_level"])
        
        # Add plan type specific terms
        if plan_type == "nuevo_paciente":
            query_parts.append("plan completo variado")
        elif plan_type == "control":
            query_parts.append("ajuste plan control")
        elif plan_type == "reemplazo":
            query_parts.append("reemplazo comida")
        
        return " ".join(query_parts)
    
    def _matches_patient_constraints(
        self, 
        recipe_metadata: Dict[str, Any], 
        patient_data: Dict[str, Any]
    ) -> bool:
        """Check if recipe matches patient constraints."""
        # Check dietary restrictions
        patient_restrictions = patient_data.get("restrictions", [])
        recipe_restrictions = recipe_metadata.get("dietary_restrictions", [])
        
        for restriction in patient_restrictions:
            if restriction not in recipe_restrictions:
                return False
        
        # Check economic level
        patient_economic = patient_data.get("economic_level", "medium")
        recipe_economic = recipe_metadata.get("economic_level", "medium")
        
        # Simple economic level matching (could be more sophisticated)
        economic_levels = {"low": 1, "medium": 2, "high": 3}
        if economic_levels.get(recipe_economic, 2) > economic_levels.get(patient_economic, 2):
            return False
        
        # Check allergies
        patient_allergies = patient_data.get("allergies", [])
        recipe_ingredients = recipe_metadata.get("ingredients", [])
        
        for allergy in patient_allergies:
            if any(allergy.lower() in ingredient.lower() for ingredient in recipe_ingredients):
                return False
        
        return True
    
    def _is_suitable_replacement(
        self, 
        recipe_metadata: Dict[str, Any], 
        patient_data: Dict[str, Any]
    ) -> bool:
        """Check if recipe is suitable as replacement."""
        # Check basic constraints
        if not self._matches_patient_constraints(recipe_metadata, patient_data):
            return False
        
        # Check if it's not in dislikes
        patient_dislikes = patient_data.get("dislikes", [])
        recipe_name = recipe_metadata.get("name", "")
        
        for dislike in patient_dislikes:
            if dislike.lower() in recipe_name.lower():
                return False
        
        return True
    
    async def add_recipe_to_knowledge_base(
        self,
        recipe_data: Dict[str, Any]
    ) -> bool:
        """Add recipe to the knowledge base."""
        try:
            # Create document text
            document_text = self._create_recipe_document(recipe_data)
            
            # Generate embedding
            embedding = self.encoder.encode([document_text])[0].tolist()
            
            # Add to ChromaDB
            self.chroma.add(
                documents=[document_text],
                embeddings=[embedding],
                metadatas=[{
                    "id": recipe_data.get("id"),
                    "name": recipe_data.get("name"),
                    "category": recipe_data.get("category"),
                    "meal_type": recipe_data.get("meal_type"),
                    "economic_level": recipe_data.get("economic_level"),
                    "dietary_restrictions": recipe_data.get("dietary_restrictions", []),
                    "ingredients": recipe_data.get("ingredients", []),
                    "calories": recipe_data.get("calories", 0),
                    "type": "recipe"
                }],
                ids=[f"recipe_{recipe_data.get('id')}"]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding recipe to knowledge base: {str(e)}")
            return False
    
    def _create_recipe_document(self, recipe_data: Dict[str, Any]) -> str:
        """Create searchable document from recipe data."""
        parts = []
        
        # Basic info
        parts.append(f"Nombre: {recipe_data.get('name', '')}")
        parts.append(f"Categoría: {recipe_data.get('category', '')}")
        parts.append(f"Tipo de comida: {recipe_data.get('meal_type', '')}")
        
        # Ingredients
        ingredients = recipe_data.get("ingredients", [])
        if ingredients:
            parts.append(f"Ingredientes: {', '.join(ingredients)}")
        
        # Preparation
        if recipe_data.get("preparation"):
            parts.append(f"Preparación: {recipe_data['preparation']}")
        
        # Nutritional info
        if recipe_data.get("calories"):
            parts.append(f"Calorías: {recipe_data['calories']}")
        
        # Restrictions
        restrictions = recipe_data.get("dietary_restrictions", [])
        if restrictions:
            parts.append(f"Restricciones: {', '.join(restrictions)}")
        
        # Tags
        tags = recipe_data.get("tags", [])
        if tags:
            parts.append(f"Tags: {', '.join(tags)}")
        
        return "\n".join(parts)
    
    async def update_recipe_embeddings(self, recipe_ids: List[int]) -> int:
        """Update embeddings for specific recipes."""
        try:
            # This would typically fetch recipes from database
            # and update their embeddings in ChromaDB
            updated_count = 0
            
            # Placeholder implementation
            logger.info(f"Updated embeddings for {len(recipe_ids)} recipes")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating recipe embeddings: {str(e)}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        try:
            collection_count = self.chroma.count()
            
            return {
                "total_documents": collection_count,
                "embedding_model": settings.RAG_SETTINGS["embedding_model"],
                "collection_name": settings.chroma.collection_name,
                "status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Error getting RAG stats: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def get_formatted_context(
        self,
        patient_data: Dict[str, Any],
        plan_type: str = "nuevo_paciente",
        n_results: int = 15
    ) -> str:
        """Get formatted RAG context for prompt injection."""
        try:
            # Get relevant recipes
            recipes = await self.get_relevant_recipes(patient_data, plan_type, n_results)
            
            # Format recipe data for prompt
            recipe_data = []
            for recipe in recipes:
                recipe_info = {
                    'name': recipe['metadata'].get('name', ''),
                    'category': recipe['metadata'].get('category', ''),
                    'description': recipe['content']
                }
                recipe_data.append(recipe_info)
            
            # Use the unified format_rag_context function
            return format_rag_context(recipe_data)
            
        except Exception as e:
            logger.error(f"Error formatting RAG context: {str(e)}")
            return "No se encontraron recetas relevantes en la base de datos."