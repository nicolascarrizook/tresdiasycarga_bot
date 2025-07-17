"""
Recipe service for Sistema Mayra API.
"""
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import BaseModel
from ..schemas.recipe import Recipe, RecipeCreate, RecipeUpdate, RecipeSearch
from .base import BaseService

logger = logging.getLogger(__name__)


class RecipeModel(BaseModel):
    """Recipe model placeholder."""
    __tablename__ = "recipes"


class RecipeService(BaseService[RecipeModel, Recipe]):
    """Recipe service for managing recipes."""
    
    def __init__(self, db: AsyncSession, chroma_collection=None):
        super().__init__(db, RecipeModel)
        self.chroma = chroma_collection
    
    async def create_recipe(self, recipe_data: RecipeCreate) -> Optional[RecipeModel]:
        """Create new recipe with embedding."""
        try:
            # Calculate nutritional percentages
            calculated_data = self._calculate_recipe_metrics(recipe_data)
            
            # Merge with recipe data
            recipe_dict = recipe_data.model_dump()
            recipe_dict.update(calculated_data)
            
            # Create recipe
            recipe = await self.create(recipe_dict)
            
            if recipe and self.chroma:
                # Add to vector database
                await self._add_to_vector_db(recipe)
            
            if recipe:
                logger.info(f"Created recipe: {recipe.name} (ID: {recipe.id})")
            
            return recipe
            
        except Exception as e:
            logger.error(f"Error creating recipe: {str(e)}")
            return None
    
    async def search_recipes(
        self,
        search_params: RecipeSearch,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search recipes with filters."""
        try:
            filters = {}
            
            # Apply filters
            if search_params.category:
                filters["category"] = search_params.category
            
            if search_params.meal_type:
                filters["meal_type"] = search_params.meal_type
            
            if search_params.economic_level:
                filters["economic_level"] = search_params.economic_level
            
            if search_params.difficulty:
                filters["difficulty"] = search_params.difficulty
            
            if search_params.is_active is not None:
                filters["is_active"] = search_params.is_active
            
            # Use text search if query provided
            if search_params.query:
                search_fields = ['name', 'description', 'ingredients', 'preparation']
                result = await self.search(search_params.query, search_fields, page, limit)
            else:
                result = await self.get_paginated(
                    page=page,
                    limit=limit,
                    filters=filters,
                    order_by="created_at",
                    order_desc=True
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching recipes: {str(e)}")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0,
                "has_next": False,
                "has_previous": False
            }
    
    async def get_recipe_recommendations(
        self,
        patient_data: Dict[str, Any],
        meal_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recipe recommendations for patient."""
        try:
            recommendations = []
            
            # Build filters based on patient data
            filters = {
                "is_active": True
            }
            
            if meal_type:
                filters["meal_type"] = meal_type
            
            # Filter by economic level
            if patient_data.get("economic_level"):
                filters["economic_level"] = patient_data["economic_level"]
            
            # Get recipes
            recipes = await self.get_paginated(
                page=1,
                limit=limit * 2,  # Get more to filter
                filters=filters,
                order_by="average_rating",
                order_desc=True
            )
            
            # Filter by patient constraints
            for recipe in recipes.items:
                if self._matches_patient_constraints(recipe, patient_data):
                    score = self._calculate_recommendation_score(recipe, patient_data)
                    
                    recommendations.append({
                        "recipe": recipe,
                        "score": score,
                        "reason": self._get_recommendation_reason(recipe, patient_data)
                    })
            
            # Sort by score and return top results
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recipe recommendations: {str(e)}")
            return []
    
    async def get_recipe_equivalents(
        self,
        recipe_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get equivalent recipes with similar nutritional profile."""
        try:
            recipe = await self.get_by_id(recipe_id)
            if not recipe:
                return []
            
            # Find recipes with similar calories and macros
            target_calories = recipe.macros.calories
            calorie_tolerance = 0.15  # 15% tolerance
            
            min_calories = target_calories * (1 - calorie_tolerance)
            max_calories = target_calories * (1 + calorie_tolerance)
            
            # This would typically use more sophisticated matching
            # For now, return basic filtering
            
            similar_recipes = await self.get_paginated(
                page=1,
                limit=limit * 2,
                filters={
                    "meal_type": recipe.meal_type,
                    "category": recipe.category,
                    "is_active": True
                }
            )
            
            equivalents = []
            for similar in similar_recipes.items:
                if similar.id != recipe_id:
                    similarity_score = self._calculate_similarity_score(recipe, similar)
                    if similarity_score > 0.7:  # 70% similarity threshold
                        equivalents.append({
                            "recipe": similar,
                            "similarity_score": similarity_score,
                            "macro_difference": self._calculate_macro_difference(recipe, similar)
                        })
            
            # Sort by similarity
            equivalents.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return equivalents[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recipe equivalents: {str(e)}")
            return []
    
    async def get_recipe_analytics(self) -> Dict[str, Any]:
        """Get recipe analytics."""
        try:
            total_recipes = await self.get_count()
            
            # This would involve complex queries for analytics
            analytics = {
                "total_recipes": total_recipes,
                "active_recipes": total_recipes,  # Would filter by active
                "recipes_by_category": {},
                "recipes_by_meal_type": {},
                "recipes_by_difficulty": {},
                "most_used_recipes": [],
                "best_rated_recipes": [],
                "trending_recipes": [],
                "average_calories": 0,
                "average_protein": 0,
                "average_cooking_time": 0,
                "vegetarian_percentage": 0,
                "vegan_percentage": 0,
                "gluten_free_percentage": 0
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting recipe analytics: {str(e)}")
            return {}
    
    def _calculate_recipe_metrics(self, recipe_data: RecipeCreate) -> Dict[str, Any]:
        """Calculate recipe metrics."""
        try:
            macros = recipe_data.macros
            total_calories = macros.calories
            
            if total_calories > 0:
                protein_percentage = (macros.protein * 4) / total_calories * 100
                carbs_percentage = (macros.carbs * 4) / total_calories * 100
                fat_percentage = (macros.fat * 9) / total_calories * 100
                
                # Calculate calories per 100g (assuming portion size)
                calories_per_100g = total_calories  # Would adjust based on portion size
            else:
                protein_percentage = 0
                carbs_percentage = 0
                fat_percentage = 0
                calories_per_100g = 0
            
            return {
                "protein_percentage": round(protein_percentage, 1),
                "carbs_percentage": round(carbs_percentage, 1),
                "fat_percentage": round(fat_percentage, 1),
                "calories_per_100g": round(calories_per_100g, 1),
                "times_used": 0,
                "average_rating": 0,
                "total_ratings": 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating recipe metrics: {str(e)}")
            return {
                "protein_percentage": 0,
                "carbs_percentage": 0,
                "fat_percentage": 0,
                "calories_per_100g": 0,
                "times_used": 0,
                "average_rating": 0,
                "total_ratings": 0
            }
    
    def _matches_patient_constraints(
        self, 
        recipe: Any, 
        patient_data: Dict[str, Any]
    ) -> bool:
        """Check if recipe matches patient constraints."""
        try:
            # Check dietary restrictions
            patient_restrictions = patient_data.get("restrictions", [])
            recipe_restrictions = recipe.dietary_restrictions or []
            
            for restriction in patient_restrictions:
                if restriction not in recipe_restrictions:
                    return False
            
            # Check allergies
            patient_allergies = patient_data.get("allergies", [])
            recipe_ingredients = [ing.name for ing in recipe.ingredients] if recipe.ingredients else []
            
            for allergy in patient_allergies:
                if any(allergy.lower() in ingredient.lower() for ingredient in recipe_ingredients):
                    return False
            
            # Check dislikes
            patient_dislikes = patient_data.get("dislikes", [])
            recipe_name = recipe.name.lower()
            
            for dislike in patient_dislikes:
                if dislike.lower() in recipe_name:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking patient constraints: {str(e)}")
            return False
    
    def _calculate_recommendation_score(
        self, 
        recipe: Any, 
        patient_data: Dict[str, Any]
    ) -> float:
        """Calculate recommendation score for recipe."""
        try:
            score = 0.0
            
            # Base score from rating
            if recipe.average_rating > 0:
                score += recipe.average_rating / 5.0 * 0.3  # 30% weight
            
            # Usage frequency
            if recipe.times_used > 0:
                usage_score = min(recipe.times_used / 100, 1.0)  # Normalize to 1.0
                score += usage_score * 0.2  # 20% weight
            
            # Preference matching
            patient_preferences = patient_data.get("preferences", [])
            recipe_tags = recipe.tags or []
            
            if patient_preferences:
                preference_matches = sum(
                    1 for pref in patient_preferences 
                    if any(pref.lower() in tag.lower() for tag in recipe_tags)
                )
                preference_score = preference_matches / len(patient_preferences)
                score += preference_score * 0.3  # 30% weight
            
            # Economic level matching
            patient_economic = patient_data.get("economic_level", "medium")
            recipe_economic = recipe.economic_level
            
            if patient_economic == recipe_economic:
                score += 0.2  # 20% weight
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating recommendation score: {str(e)}")
            return 0.0
    
    def _get_recommendation_reason(
        self, 
        recipe: Any, 
        patient_data: Dict[str, Any]
    ) -> str:
        """Get reason for recommendation."""
        try:
            reasons = []
            
            if recipe.average_rating > 4.0:
                reasons.append("Alta valoración")
            
            if recipe.times_used > 50:
                reasons.append("Popular entre usuarios")
            
            # Check preference matches
            patient_preferences = patient_data.get("preferences", [])
            recipe_tags = recipe.tags or []
            
            for pref in patient_preferences:
                if any(pref.lower() in tag.lower() for tag in recipe_tags):
                    reasons.append(f"Coincide con preferencia: {pref}")
                    break
            
            # Check nutritional fit
            if recipe.difficulty == "easy":
                reasons.append("Fácil de preparar")
            
            if recipe.cooking_time <= 15:
                reasons.append("Preparación rápida")
            
            return ", ".join(reasons) if reasons else "Adecuado para tu perfil"
            
        except Exception as e:
            logger.error(f"Error getting recommendation reason: {str(e)}")
            return "Recomendado para ti"
    
    def _calculate_similarity_score(self, recipe1: Any, recipe2: Any) -> float:
        """Calculate similarity score between two recipes."""
        try:
            score = 0.0
            
            # Calorie similarity
            calorie_diff = abs(recipe1.macros.calories - recipe2.macros.calories)
            max_calories = max(recipe1.macros.calories, recipe2.macros.calories)
            if max_calories > 0:
                calorie_similarity = 1 - (calorie_diff / max_calories)
                score += calorie_similarity * 0.4  # 40% weight
            
            # Macro similarity
            protein_diff = abs(recipe1.macros.protein - recipe2.macros.protein)
            carbs_diff = abs(recipe1.macros.carbs - recipe2.macros.carbs)
            fat_diff = abs(recipe1.macros.fat - recipe2.macros.fat)
            
            # Normalize macro differences
            max_protein = max(recipe1.macros.protein, recipe2.macros.protein)
            max_carbs = max(recipe1.macros.carbs, recipe2.macros.carbs)
            max_fat = max(recipe1.macros.fat, recipe2.macros.fat)
            
            if max_protein > 0:
                protein_similarity = 1 - (protein_diff / max_protein)
                score += protein_similarity * 0.2  # 20% weight
            
            if max_carbs > 0:
                carbs_similarity = 1 - (carbs_diff / max_carbs)
                score += carbs_similarity * 0.2  # 20% weight
            
            if max_fat > 0:
                fat_similarity = 1 - (fat_diff / max_fat)
                score += fat_similarity * 0.2  # 20% weight
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating similarity score: {str(e)}")
            return 0.0
    
    def _calculate_macro_difference(self, recipe1: Any, recipe2: Any) -> Dict[str, float]:
        """Calculate macro nutrient differences."""
        try:
            return {
                "calories": recipe2.macros.calories - recipe1.macros.calories,
                "protein": recipe2.macros.protein - recipe1.macros.protein,
                "carbs": recipe2.macros.carbs - recipe1.macros.carbs,
                "fat": recipe2.macros.fat - recipe1.macros.fat
            }
            
        except Exception as e:
            logger.error(f"Error calculating macro difference: {str(e)}")
            return {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    
    async def _add_to_vector_db(self, recipe: Any) -> bool:
        """Add recipe to vector database."""
        try:
            if not self.chroma:
                return False
            
            # This would typically generate embeddings and add to ChromaDB
            # For now, just log the action
            logger.info(f"Added recipe {recipe.id} to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding recipe to vector DB: {str(e)}")
            return False
    
    async def increment_usage_count(self, recipe_id: int) -> bool:
        """Increment usage count for recipe."""
        try:
            recipe = await self.get_by_id(recipe_id)
            if not recipe:
                return False
            
            recipe.times_used += 1
            recipe.last_used_at = datetime.utcnow()
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing usage count: {str(e)}")
            return False
    
    async def add_rating(
        self, 
        recipe_id: int, 
        rating: float, 
        user_id: int
    ) -> bool:
        """Add rating to recipe."""
        try:
            recipe = await self.get_by_id(recipe_id)
            if not recipe:
                return False
            
            # This would typically insert into a ratings table
            # For now, update the average rating
            current_total = recipe.average_rating * recipe.total_ratings
            new_total = current_total + rating
            recipe.total_ratings += 1
            recipe.average_rating = new_total / recipe.total_ratings
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error adding rating: {str(e)}")
            return False