"""
Recipe repository for Sistema Mayra.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.recipe import Recipe, RecipeIngredient, RecipeCategoryEnum, DifficultyEnum, EconomicLevelEnum
from .base import BaseRepository, FilterOptions


class RecipeRepository(BaseRepository[Recipe]):
    """Recipe repository with specialized methods."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Recipe)
    
    async def get_by_name(self, name: str) -> Optional[Recipe]:
        """Get recipe by name."""
        return await self.find_one_by(name=name)
    
    async def get_with_ingredients(self, recipe_id: int) -> Optional[Recipe]:
        """Get recipe with ingredients."""
        stmt = select(Recipe).where(Recipe.id == recipe_id).options(
            selectinload(Recipe.ingredients)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_category(self, category: RecipeCategoryEnum) -> List[Recipe]:
        """Get recipes by category."""
        return await self.find_by(category=category)
    
    async def get_by_subcategory(self, subcategory: str) -> List[Recipe]:
        """Get recipes by subcategory."""
        return await self.find_by(subcategory=subcategory)
    
    async def get_by_difficulty(self, difficulty: DifficultyEnum) -> List[Recipe]:
        """Get recipes by difficulty."""
        return await self.find_by(difficulty=difficulty)
    
    async def get_by_economic_level(self, economic_level: EconomicLevelEnum) -> List[Recipe]:
        """Get recipes by economic level."""
        return await self.find_by(economic_level=economic_level)
    
    async def get_by_calorie_range(self, min_calories: float, max_calories: float) -> List[Recipe]:
        """Get recipes by calorie range."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                Recipe.calories >= min_calories,
                Recipe.calories <= max_calories
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_protein_range(self, min_protein: float, max_protein: float) -> List[Recipe]:
        """Get recipes by protein range."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                Recipe.protein >= min_protein,
                Recipe.protein <= max_protein
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_cooking_time(self, max_minutes: int) -> List[Recipe]:
        """Get recipes by maximum cooking time."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            or_(
                Recipe.cooking_time <= max_minutes,
                Recipe.cooking_time.is_(None)
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_with_dietary_restriction(self, restriction: str) -> List[Recipe]:
        """Get recipes with specific dietary restriction."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            Recipe.dietary_restrictions.contains([restriction])
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_without_allergen(self, allergen: str) -> List[Recipe]:
        """Get recipes without specific allergen."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            or_(
                Recipe.allergens.is_(None),
                ~Recipe.allergens.contains([allergen])
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_validated_recipes(self) -> List[Recipe]:
        """Get validated recipes only."""
        return await self.find_by(is_validated=True)
    
    async def search_recipes(self, query: str, filters: Optional[Dict[str, Any]] = None,
                           page: int = 1, per_page: int = 20):
        """Search recipes with optional filters."""
        filter_options = FilterOptions()
        
        # Add text search
        search_conditions = []
        search_conditions.append(Recipe.name.ilike(f"%{query}%"))
        search_conditions.append(Recipe.description.ilike(f"%{query}%"))
        search_conditions.append(Recipe.preparation.ilike(f"%{query}%"))
        search_conditions.append(Recipe.search_vector.ilike(f"%{query}%"))
        filter_options.add_filter(or_(*search_conditions))
        
        # Add additional filters
        if filters:
            if "category" in filters:
                filter_options.add_filter(Recipe.category == filters["category"])
            
            if "difficulty" in filters:
                filter_options.add_filter(Recipe.difficulty == filters["difficulty"])
            
            if "economic_level" in filters:
                filter_options.add_filter(Recipe.economic_level == filters["economic_level"])
            
            if "max_calories" in filters:
                filter_options.add_filter(Recipe.calories <= filters["max_calories"])
            
            if "min_protein" in filters:
                filter_options.add_filter(Recipe.protein >= filters["min_protein"])
            
            if "max_cooking_time" in filters:
                filter_options.add_filter(
                    or_(
                        Recipe.cooking_time <= filters["max_cooking_time"],
                        Recipe.cooking_time.is_(None)
                    )
                )
            
            if "dietary_restrictions" in filters:
                for restriction in filters["dietary_restrictions"]:
                    filter_options.add_filter(Recipe.dietary_restrictions.contains([restriction]))
            
            if "exclude_allergens" in filters:
                for allergen in filters["exclude_allergens"]:
                    filter_options.add_filter(
                        or_(
                            Recipe.allergens.is_(None),
                            ~Recipe.allergens.contains([allergen])
                        )
                    )
            
            if "validated_only" in filters and filters["validated_only"]:
                filter_options.add_filter(Recipe.is_validated == True)
        
        # Default ordering by usage count
        filter_options.add_order_by(Recipe.usage_count, "desc")
        filter_options.add_order_by(Recipe.validation_score, "desc")
        
        return await self.paginate(page, per_page, filter_options)
    
    async def get_popular_recipes(self, limit: int = 10) -> List[Recipe]:
        """Get popular recipes by usage count."""
        filter_options = FilterOptions()
        filter_options.add_order_by(Recipe.usage_count, "desc")
        filter_options.add_order_by(Recipe.view_count, "desc")
        
        stmt = self.build_query(filter_options).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_recent_recipes(self, limit: int = 10) -> List[Recipe]:
        """Get recently added recipes."""
        filter_options = FilterOptions()
        filter_options.add_order_by(Recipe.created_at, "desc")
        
        stmt = self.build_query(filter_options).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_recommended_recipes(self, category: Optional[RecipeCategoryEnum] = None,
                                    economic_level: Optional[EconomicLevelEnum] = None,
                                    exclude_allergens: Optional[List[str]] = None,
                                    limit: int = 10) -> List[Recipe]:
        """Get recommended recipes based on criteria."""
        filter_options = FilterOptions()
        
        # Only validated recipes
        filter_options.add_filter(Recipe.is_validated == True)
        
        if category:
            filter_options.add_filter(Recipe.category == category)
        
        if economic_level:
            filter_options.add_filter(Recipe.economic_level == economic_level)
        
        if exclude_allergens:
            for allergen in exclude_allergens:
                filter_options.add_filter(
                    or_(
                        Recipe.allergens.is_(None),
                        ~Recipe.allergens.contains([allergen])
                    )
                )
        
        # Order by validation score and usage
        filter_options.add_order_by(Recipe.validation_score, "desc")
        filter_options.add_order_by(Recipe.usage_count, "desc")
        
        stmt = self.build_query(filter_options).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def increment_usage_count(self, recipe_id: int) -> bool:
        """Increment recipe usage count."""
        recipe = await self.get_by_id(recipe_id)
        if not recipe:
            return False
        
        recipe.increment_usage_count()
        await self.session.commit()
        return True
    
    async def validate_recipe(self, recipe_id: int, user_id: int, score: int) -> bool:
        """Validate recipe."""
        recipe = await self.get_by_id(recipe_id)
        if not recipe:
            return False
        
        recipe.validate(user_id, score)
        await self.session.commit()
        return True
    
    async def update_search_vectors(self) -> int:
        """Update search vectors for all recipes."""
        recipes = await self.get_all(active_only=False)
        for recipe in recipes:
            recipe.update_search_vector()
        
        await self.session.commit()
        return len(recipes)
    
    async def get_statistics_by_category(self) -> Dict[str, int]:
        """Get statistics by category."""
        stmt = select(Recipe.category, func.count(Recipe.id)).group_by(Recipe.category)
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_statistics_by_difficulty(self) -> Dict[str, int]:
        """Get statistics by difficulty."""
        stmt = select(Recipe.difficulty, func.count(Recipe.id)).group_by(Recipe.difficulty)
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_statistics_by_economic_level(self) -> Dict[str, int]:
        """Get statistics by economic level."""
        stmt = select(Recipe.economic_level, func.count(Recipe.id)).group_by(Recipe.economic_level)
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_nutrition_statistics(self) -> Dict[str, Any]:
        """Get nutrition statistics."""
        # Average nutrition values
        avg_stmt = select(
            func.avg(Recipe.calories).label("avg_calories"),
            func.avg(Recipe.protein).label("avg_protein"),
            func.avg(Recipe.carbs).label("avg_carbs"),
            func.avg(Recipe.fat).label("avg_fat"),
            func.avg(Recipe.fiber).label("avg_fiber")
        ).where(Recipe.calories.is_not(None))
        
        avg_result = await self.session.execute(avg_stmt)
        avg_data = avg_result.fetchone()
        
        # Min/Max nutrition values
        minmax_stmt = select(
            func.min(Recipe.calories).label("min_calories"),
            func.max(Recipe.calories).label("max_calories"),
            func.min(Recipe.protein).label("min_protein"),
            func.max(Recipe.protein).label("max_protein")
        ).where(Recipe.calories.is_not(None))
        
        minmax_result = await self.session.execute(minmax_stmt)
        minmax_data = minmax_result.fetchone()
        
        return {
            "averages": {
                "calories": round(avg_data.avg_calories or 0, 2),
                "protein": round(avg_data.avg_protein or 0, 2),
                "carbs": round(avg_data.avg_carbs or 0, 2),
                "fat": round(avg_data.avg_fat or 0, 2),
                "fiber": round(avg_data.avg_fiber or 0, 2)
            },
            "ranges": {
                "calories": {"min": minmax_data.min_calories, "max": minmax_data.max_calories},
                "protein": {"min": minmax_data.min_protein, "max": minmax_data.max_protein}
            }
        }
    
    async def get_recipe_statistics(self) -> Dict[str, Any]:
        """Get comprehensive recipe statistics."""
        base_stats = await self.get_statistics()
        
        # Validation stats
        validated_stmt = select(func.count(Recipe.id)).where(Recipe.is_validated == True)
        validated_result = await self.session.execute(validated_stmt)
        validated = validated_result.scalar()
        
        return {
            **base_stats,
            "validated": validated,
            "unvalidated": base_stats["total"] - validated,
            "by_category": await self.get_statistics_by_category(),
            "by_difficulty": await self.get_statistics_by_difficulty(),
            "by_economic_level": await self.get_statistics_by_economic_level(),
            "nutrition": await self.get_nutrition_statistics()
        }


class RecipeIngredientRepository(BaseRepository[RecipeIngredient]):
    """Recipe ingredient repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, RecipeIngredient)
    
    async def get_by_recipe(self, recipe_id: int) -> List[RecipeIngredient]:
        """Get ingredients by recipe."""
        filter_options = FilterOptions()
        filter_options.add_filter(RecipeIngredient.recipe_id == recipe_id)
        filter_options.add_order_by(RecipeIngredient.order, "asc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_name(self, name: str) -> List[RecipeIngredient]:
        """Get ingredients by name."""
        return await self.find_by(name=name)
    
    async def get_ingredient_usage_stats(self) -> Dict[str, int]:
        """Get ingredient usage statistics."""
        stmt = select(
            RecipeIngredient.name,
            func.count(RecipeIngredient.id).label("usage_count")
        ).group_by(RecipeIngredient.name).order_by(func.count(RecipeIngredient.id).desc())
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_most_used_ingredients(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most used ingredients."""
        stmt = select(
            RecipeIngredient.name,
            func.count(RecipeIngredient.id).label("usage_count"),
            func.avg(RecipeIngredient.quantity).label("avg_quantity")
        ).group_by(RecipeIngredient.name).order_by(
            func.count(RecipeIngredient.id).desc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return [
            {
                "name": row.name,
                "usage_count": row.usage_count,
                "avg_quantity": round(row.avg_quantity or 0, 2)
            }
            for row in result.fetchall()
        ]