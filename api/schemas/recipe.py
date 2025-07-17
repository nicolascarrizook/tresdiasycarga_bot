"""
Recipe schemas for Sistema Mayra API.
"""
from datetime import datetime
from typing import Optional

from pydantic import Field, validator

from ..core.settings import (
    MealType, RecipeCategory, EconomicLevel, DietaryRestriction
)
from .base import BaseSchema, IDMixin, TimestampMixin, MacroNutrients, Ingredient, PortionSize


class RecipeBase(BaseSchema):
    """Base recipe schema."""
    
    name: str = Field(..., description="Recipe name", min_length=2, max_length=200)
    category: RecipeCategory = Field(..., description="Recipe category")
    subcategory: Optional[str] = Field(None, description="Recipe subcategory", max_length=100)
    meal_type: MealType = Field(..., description="Meal type")
    
    # Recipe details
    description: Optional[str] = Field(None, description="Recipe description", max_length=500)
    preparation: str = Field(..., description="Preparation instructions", min_length=10)
    cooking_time: int = Field(..., description="Cooking time in minutes", ge=0, le=300)
    servings: int = Field(1, description="Number of servings", ge=1, le=20)
    difficulty: str = Field("medium", description="Difficulty level")
    
    # Nutritional information
    macros: MacroNutrients = Field(..., description="Macro nutrients per serving")
    ingredients: list[Ingredient] = Field(..., description="Recipe ingredients", min_items=1)
    
    # Filters and tags
    economic_level: EconomicLevel = Field(EconomicLevel.MEDIUM, description="Economic level")
    dietary_restrictions: list[DietaryRestriction] = Field(
        default_factory=list, 
        description="Dietary restrictions compatibility"
    )
    tags: list[str] = Field(default_factory=list, description="Recipe tags")
    
    # Additional info
    tips: Optional[str] = Field(None, description="Cooking tips", max_length=500)
    variations: Optional[str] = Field(None, description="Recipe variations", max_length=500)
    storage_instructions: Optional[str] = Field(None, description="Storage instructions", max_length=200)
    
    @validator("difficulty")
    def validate_difficulty(cls, v):
        """Validate difficulty level."""
        allowed_difficulties = ["easy", "medium", "hard"]
        if v not in allowed_difficulties:
            raise ValueError(f"Difficulty must be one of: {allowed_difficulties}")
        return v
    
    @validator("tags", pre=True)
    def validate_tags(cls, v):
        """Validate tags list."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]
        return v or []


class RecipeCreate(RecipeBase):
    """Recipe creation schema."""
    
    # Optional fields for creation
    source: Optional[str] = Field(None, description="Recipe source", max_length=200)
    notes: Optional[str] = Field(None, description="Additional notes", max_length=500)


class RecipeUpdate(BaseSchema):
    """Recipe update schema."""
    
    name: Optional[str] = Field(None, description="Recipe name", min_length=2, max_length=200)
    category: Optional[RecipeCategory] = Field(None, description="Recipe category")
    subcategory: Optional[str] = Field(None, description="Recipe subcategory", max_length=100)
    meal_type: Optional[MealType] = Field(None, description="Meal type")
    
    description: Optional[str] = Field(None, description="Recipe description", max_length=500)
    preparation: Optional[str] = Field(None, description="Preparation instructions", min_length=10)
    cooking_time: Optional[int] = Field(None, description="Cooking time in minutes", ge=0, le=300)
    servings: Optional[int] = Field(None, description="Number of servings", ge=1, le=20)
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    
    macros: Optional[MacroNutrients] = Field(None, description="Macro nutrients per serving")
    ingredients: Optional[list[Ingredient]] = Field(None, description="Recipe ingredients", min_items=1)
    
    economic_level: Optional[EconomicLevel] = Field(None, description="Economic level")
    dietary_restrictions: Optional[list[DietaryRestriction]] = Field(
        None, 
        description="Dietary restrictions compatibility"
    )
    tags: Optional[list[str]] = Field(None, description="Recipe tags")
    
    tips: Optional[str] = Field(None, description="Cooking tips", max_length=500)
    variations: Optional[str] = Field(None, description="Recipe variations", max_length=500)
    storage_instructions: Optional[str] = Field(None, description="Storage instructions", max_length=200)
    
    is_active: Optional[bool] = Field(None, description="Recipe active status")
    
    @validator("difficulty")
    def validate_difficulty(cls, v):
        """Validate difficulty level."""
        if v is None:
            return v
        allowed_difficulties = ["easy", "medium", "hard"]
        if v not in allowed_difficulties:
            raise ValueError(f"Difficulty must be one of: {allowed_difficulties}")
        return v


class Recipe(RecipeBase, IDMixin, TimestampMixin):
    """Recipe response schema."""
    
    is_active: bool = Field(True, description="Recipe active status")
    source: Optional[str] = Field(None, description="Recipe source", max_length=200)
    notes: Optional[str] = Field(None, description="Additional notes", max_length=500)
    
    # Usage statistics
    times_used: int = Field(0, description="Times used in plans", ge=0)
    average_rating: float = Field(0, description="Average rating", ge=0, le=5)
    total_ratings: int = Field(0, description="Total ratings", ge=0)
    
    # Computed fields
    calories_per_100g: float = Field(0, description="Calories per 100g", ge=0)
    protein_percentage: float = Field(0, description="Protein percentage", ge=0, le=100)
    carbs_percentage: float = Field(0, description="Carbs percentage", ge=0, le=100)
    fat_percentage: float = Field(0, description="Fat percentage", ge=0, le=100)
    
    @property
    def total_ingredients(self) -> int:
        """Get total number of ingredients."""
        return len(self.ingredients)
    
    @property
    def is_vegetarian(self) -> bool:
        """Check if recipe is vegetarian."""
        return DietaryRestriction.VEGETARIAN in self.dietary_restrictions
    
    @property
    def is_vegan(self) -> bool:
        """Check if recipe is vegan."""
        return DietaryRestriction.VEGAN in self.dietary_restrictions


class RecipeSummary(BaseSchema):
    """Recipe summary schema."""
    
    id: int = Field(..., description="Recipe ID", gt=0)
    name: str = Field(..., description="Recipe name")
    category: RecipeCategory = Field(..., description="Recipe category")
    meal_type: MealType = Field(..., description="Meal type")
    cooking_time: int = Field(..., description="Cooking time in minutes")
    difficulty: str = Field(..., description="Difficulty level")
    calories: float = Field(..., description="Calories per serving")
    economic_level: EconomicLevel = Field(..., description="Economic level")
    times_used: int = Field(0, description="Times used in plans", ge=0)
    average_rating: float = Field(0, description="Average rating", ge=0, le=5)
    is_active: bool = Field(True, description="Recipe active status")


class RecipeSearch(BaseSchema):
    """Recipe search schema."""
    
    query: Optional[str] = Field(None, description="Search query")
    category: Optional[RecipeCategory] = Field(None, description="Recipe category")
    meal_type: Optional[MealType] = Field(None, description="Meal type")
    economic_level: Optional[EconomicLevel] = Field(None, description="Economic level")
    dietary_restrictions: Optional[list[DietaryRestriction]] = Field(
        None, 
        description="Dietary restrictions compatibility"
    )
    tags: Optional[list[str]] = Field(None, description="Recipe tags")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    max_cooking_time: Optional[int] = Field(None, description="Maximum cooking time", ge=0)
    min_calories: Optional[float] = Field(None, description="Minimum calories", ge=0)
    max_calories: Optional[float] = Field(None, description="Maximum calories", ge=0)
    min_protein: Optional[float] = Field(None, description="Minimum protein", ge=0)
    max_protein: Optional[float] = Field(None, description="Maximum protein", ge=0)
    is_active: Optional[bool] = Field(None, description="Active status")
    
    @validator("difficulty")
    def validate_difficulty(cls, v):
        """Validate difficulty level."""
        if v is None:
            return v
        allowed_difficulties = ["easy", "medium", "hard"]
        if v not in allowed_difficulties:
            raise ValueError(f"Difficulty must be one of: {allowed_difficulties}")
        return v


class RecipeEquivalent(BaseSchema):
    """Recipe equivalent schema."""
    
    original_recipe_id: int = Field(..., description="Original recipe ID", gt=0)
    equivalent_recipe_id: int = Field(..., description="Equivalent recipe ID", gt=0)
    similarity_score: float = Field(..., description="Similarity score", ge=0, le=1)
    macro_difference: dict = Field(..., description="Macro nutrient differences")
    replacement_factor: float = Field(1.0, description="Replacement factor", gt=0)
    notes: Optional[str] = Field(None, description="Replacement notes", max_length=200)


class RecipeRating(BaseSchema):
    """Recipe rating schema."""
    
    recipe_id: int = Field(..., description="Recipe ID", gt=0)
    user_id: int = Field(..., description="User ID", gt=0)
    rating: float = Field(..., description="Rating", ge=1, le=5)
    comment: Optional[str] = Field(None, description="Rating comment", max_length=500)
    created_at: datetime = Field(..., description="Rating timestamp")


class RecipeNutrition(BaseSchema):
    """Recipe nutrition analysis schema."""
    
    recipe_id: int = Field(..., description="Recipe ID", gt=0)
    per_serving: MacroNutrients = Field(..., description="Nutrition per serving")
    per_100g: MacroNutrients = Field(..., description="Nutrition per 100g")
    
    # Detailed breakdown
    ingredient_breakdown: list[dict] = Field(..., description="Nutrition breakdown by ingredient")
    macro_percentages: dict = Field(..., description="Macro percentages")
    micronutrients: Optional[dict] = Field(None, description="Micronutrient content")
    
    # Dietary analysis
    glycemic_index: Optional[float] = Field(None, description="Estimated glycemic index", ge=0, le=100)
    satiety_score: Optional[float] = Field(None, description="Satiety score", ge=0, le=10)
    inflammatory_score: Optional[float] = Field(None, description="Inflammatory score", ge=-10, le=10)


class RecipeVariation(BaseSchema):
    """Recipe variation schema."""
    
    base_recipe_id: int = Field(..., description="Base recipe ID", gt=0)
    name: str = Field(..., description="Variation name", min_length=2, max_length=200)
    description: str = Field(..., description="Variation description", max_length=500)
    modifications: list[str] = Field(..., description="Modifications made", min_items=1)
    macro_changes: dict = Field(..., description="Macro nutrient changes")
    difficulty_change: Optional[str] = Field(None, description="Difficulty change")
    time_change: Optional[int] = Field(None, description="Time change in minutes")


class RecipeAnalytics(BaseSchema):
    """Recipe analytics schema."""
    
    total_recipes: int = Field(0, description="Total recipes", ge=0)
    active_recipes: int = Field(0, description="Active recipes", ge=0)
    recipes_by_category: dict = Field(default_factory=dict, description="Recipes by category")
    recipes_by_meal_type: dict = Field(default_factory=dict, description="Recipes by meal type")
    recipes_by_difficulty: dict = Field(default_factory=dict, description="Recipes by difficulty")
    
    # Usage statistics
    most_used_recipes: list[dict] = Field(default_factory=list, description="Most used recipes")
    best_rated_recipes: list[dict] = Field(default_factory=list, description="Best rated recipes")
    trending_recipes: list[dict] = Field(default_factory=list, description="Trending recipes")
    
    # Nutritional analysis
    average_calories: float = Field(0, description="Average calories", ge=0)
    average_protein: float = Field(0, description="Average protein", ge=0)
    average_cooking_time: float = Field(0, description="Average cooking time", ge=0)
    
    # Dietary compliance
    vegetarian_percentage: float = Field(0, description="Vegetarian recipes percentage", ge=0, le=100)
    vegan_percentage: float = Field(0, description="Vegan recipes percentage", ge=0, le=100)
    gluten_free_percentage: float = Field(0, description="Gluten-free recipes percentage", ge=0, le=100)


class RecipeImport(BaseSchema):
    """Recipe import schema."""
    
    source: str = Field(..., description="Import source")
    format: str = Field(..., description="Import format")
    data: dict = Field(..., description="Import data")
    validation_results: Optional[dict] = Field(None, description="Validation results")
    
    @validator("format")
    def validate_format(cls, v):
        """Validate import format."""
        allowed_formats = ["json", "csv", "xml", "docx"]
        if v not in allowed_formats:
            raise ValueError(f"Format must be one of: {allowed_formats}")
        return v


class RecipeExport(BaseSchema):
    """Recipe export schema."""
    
    format: str = Field("json", description="Export format")
    filters: Optional[RecipeSearch] = Field(None, description="Export filters")
    fields: Optional[list[str]] = Field(None, description="Fields to include")
    include_ingredients: bool = Field(True, description="Include ingredients")
    include_nutrition: bool = Field(True, description="Include nutrition data")
    include_ratings: bool = Field(False, description="Include ratings")
    
    @validator("format")
    def validate_format(cls, v):
        """Validate export format."""
        allowed_formats = ["json", "csv", "xml", "pdf"]
        if v not in allowed_formats:
            raise ValueError(f"Format must be one of: {allowed_formats}")
        return v


class RecipeBulkAction(BaseSchema):
    """Bulk recipe action schema."""
    
    recipe_ids: list[int] = Field(..., description="List of recipe IDs", min_items=1)
    action: str = Field(..., description="Action to perform")
    parameters: Optional[dict] = Field(None, description="Action parameters")
    
    @validator("action")
    def validate_action(cls, v):
        """Validate action type."""
        allowed_actions = ["activate", "deactivate", "delete", "update", "categorize", "export"]
        if v not in allowed_actions:
            raise ValueError(f"Action must be one of: {allowed_actions}")
        return v


class RecipeRecommendation(BaseSchema):
    """Recipe recommendation schema."""
    
    recipe_id: int = Field(..., description="Recipe ID", gt=0)
    score: float = Field(..., description="Recommendation score", ge=0, le=1)
    reason: str = Field(..., description="Recommendation reason")
    factors: dict = Field(..., description="Recommendation factors")
    
    # Recipe summary for display
    recipe_summary: RecipeSummary = Field(..., description="Recipe summary")
    
    # Personalization info
    matches_preferences: bool = Field(..., description="Matches user preferences")
    matches_restrictions: bool = Field(..., description="Matches dietary restrictions")
    economic_level_match: bool = Field(..., description="Matches economic level")
    
    @validator("score")
    def validate_score(cls, v):
        """Validate recommendation score."""
        if not 0 <= v <= 1:
            raise ValueError("Score must be between 0 and 1")
        return v