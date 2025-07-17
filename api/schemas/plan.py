"""
Plan schemas for Sistema Mayra API.
"""
from datetime import datetime
from typing import Optional

from pydantic import Field, validator

from ..core.settings import PlanType, MealType, WeightType
from .base import BaseSchema, IDMixin, TimestampMixin, MacroNutrients
from .patient import PatientSummary
from .recipe import RecipeSummary


class MealPlan(BaseSchema):
    """Meal plan schema."""
    
    meal_type: MealType = Field(..., description="Meal type")
    time: str = Field(..., description="Meal time", regex=r"^\d{2}:\d{2}$")
    
    # Recipe options (3 equivalent options)
    option_1: dict = Field(..., description="First meal option")
    option_2: dict = Field(..., description="Second meal option")
    option_3: dict = Field(..., description="Third meal option")
    
    # Nutritional targets
    target_calories: float = Field(..., description="Target calories", ge=0)
    target_protein: float = Field(..., description="Target protein in grams", ge=0)
    target_carbs: float = Field(..., description="Target carbs in grams", ge=0)
    target_fat: float = Field(..., description="Target fat in grams", ge=0)
    
    # Instructions
    preparation_notes: Optional[str] = Field(None, description="Preparation notes", max_length=500)
    substitution_notes: Optional[str] = Field(None, description="Substitution notes", max_length=500)
    
    @validator("time")
    def validate_time(cls, v):
        """Validate time format."""
        try:
            hour, minute = map(int, v.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time format")
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
        return v


class MealOption(BaseSchema):
    """Meal option schema."""
    
    recipe_id: int = Field(..., description="Recipe ID", gt=0)
    recipe_name: str = Field(..., description="Recipe name")
    portion_size: float = Field(..., description="Portion size", gt=0)
    portion_unit: str = Field(..., description="Portion unit")
    
    # Ingredients with portions
    ingredients: list[dict] = Field(..., description="Ingredients with portions")
    
    # Nutritional values
    calories: float = Field(..., description="Calories", ge=0)
    protein: float = Field(..., description="Protein in grams", ge=0)
    carbs: float = Field(..., description="Carbs in grams", ge=0)
    fat: float = Field(..., description="Fat in grams", ge=0)
    
    # Preparation
    preparation: str = Field(..., description="Preparation instructions")
    cooking_time: int = Field(..., description="Cooking time in minutes", ge=0)
    
    # Additional info
    tips: Optional[str] = Field(None, description="Cooking tips", max_length=200)
    substitutions: Optional[list[str]] = Field(None, description="Possible substitutions")


class DayPlan(BaseSchema):
    """Day plan schema."""
    
    day: int = Field(..., description="Day number (1-3)", ge=1, le=3)
    date: Optional[datetime] = Field(None, description="Specific date for this day")
    
    # Meals
    breakfast: MealPlan = Field(..., description="Breakfast plan")
    collation_1: Optional[MealPlan] = Field(None, description="Morning collation")
    lunch: MealPlan = Field(..., description="Lunch plan")
    collation_2: Optional[MealPlan] = Field(None, description="Afternoon collation")
    dinner: MealPlan = Field(..., description="Dinner plan")
    
    # Daily totals
    total_calories: float = Field(..., description="Total daily calories", ge=0)
    total_protein: float = Field(..., description="Total daily protein", ge=0)
    total_carbs: float = Field(..., description="Total daily carbs", ge=0)
    total_fat: float = Field(..., description="Total daily fat", ge=0)
    
    # Compliance
    target_calories: float = Field(..., description="Target daily calories", ge=0)
    calorie_variance: float = Field(..., description="Calorie variance percentage", ge=-10, le=10)
    
    # Instructions
    daily_notes: Optional[str] = Field(None, description="Daily instructions", max_length=500)
    hydration_reminder: str = Field(
        "Tomar 2-3 litros de agua durante el día",
        description="Hydration reminder"
    )


class PlanBase(BaseSchema):
    """Base plan schema."""
    
    patient_id: int = Field(..., description="Patient ID", gt=0)
    plan_type: PlanType = Field(..., description="Plan type")
    
    # Plan configuration
    duration_days: int = Field(3, description="Plan duration in days", ge=1, le=7)
    weight_type: WeightType = Field(WeightType.CRUDO, description="Weight measurement type")
    
    # Nutritional targets
    target_calories: float = Field(..., description="Target daily calories", ge=1000, le=5000)
    target_protein: float = Field(..., description="Target daily protein", ge=50, le=300)
    target_carbs: float = Field(..., description="Target daily carbs", ge=50, le=500)
    target_fat: float = Field(..., description="Target daily fat", ge=20, le=150)
    
    # Plan data
    days: list[DayPlan] = Field(..., description="Daily plans", min_items=1, max_items=7)
    
    # Instructions
    general_instructions: str = Field(..., description="General plan instructions")
    preparation_tips: Optional[str] = Field(None, description="Preparation tips", max_length=1000)
    substitution_rules: Optional[str] = Field(None, description="Substitution rules", max_length=1000)
    
    # Metadata
    generated_by: str = Field("Sistema Mayra", description="Generator identifier")
    generation_prompt: Optional[str] = Field(None, description="Generation prompt used")
    rag_context: Optional[str] = Field(None, description="RAG context used")


class PlanCreate(PlanBase):
    """Plan creation schema."""
    
    # Optional fields for creation
    notes: Optional[str] = Field(None, description="Additional notes", max_length=1000)
    telegram_user_id: Optional[int] = Field(None, description="Telegram user ID")
    
    # Context for generation
    patient_context: Optional[dict] = Field(None, description="Patient context for generation")
    replacement_context: Optional[dict] = Field(None, description="Replacement context")


class PlanUpdate(BaseSchema):
    """Plan update schema."""
    
    # Only allow updating certain fields
    is_active: Optional[bool] = Field(None, description="Plan active status")
    notes: Optional[str] = Field(None, description="Additional notes", max_length=1000)
    
    # Allow updating specific days or meals
    day_updates: Optional[dict] = Field(None, description="Day-specific updates")
    meal_replacements: Optional[dict] = Field(None, description="Meal replacements")


class Plan(PlanBase, IDMixin, TimestampMixin):
    """Plan response schema."""
    
    # Status
    is_active: bool = Field(True, description="Plan active status")
    is_current: bool = Field(True, description="Current plan status")
    
    # Metadata
    notes: Optional[str] = Field(None, description="Additional notes", max_length=1000)
    telegram_user_id: Optional[int] = Field(None, description="Telegram user ID")
    
    # File information
    pdf_path: Optional[str] = Field(None, description="PDF file path")
    pdf_generated_at: Optional[datetime] = Field(None, description="PDF generation timestamp")
    
    # Usage tracking
    times_viewed: int = Field(0, description="Times viewed", ge=0)
    last_viewed_at: Optional[datetime] = Field(None, description="Last viewed timestamp")
    
    # Relationships
    patient: Optional[PatientSummary] = Field(None, description="Patient summary")
    
    # Compliance tracking
    compliance_score: Optional[float] = Field(None, description="Compliance score", ge=0, le=100)
    feedback_rating: Optional[float] = Field(None, description="User feedback rating", ge=1, le=5)
    feedback_comments: Optional[str] = Field(None, description="User feedback", max_length=500)


class PlanSummary(BaseSchema):
    """Plan summary schema."""
    
    id: int = Field(..., description="Plan ID", gt=0)
    patient_id: int = Field(..., description="Patient ID", gt=0)
    plan_type: PlanType = Field(..., description="Plan type")
    
    # Basic info
    target_calories: float = Field(..., description="Target daily calories", ge=0)
    duration_days: int = Field(..., description="Plan duration in days", ge=1)
    
    # Status
    is_active: bool = Field(True, description="Plan active status")
    is_current: bool = Field(True, description="Current plan status")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    
    # Files
    has_pdf: bool = Field(False, description="Has PDF file")
    
    # Patient info
    patient_name: Optional[str] = Field(None, description="Patient name")


class PlanSearch(BaseSchema):
    """Plan search schema."""
    
    patient_id: Optional[int] = Field(None, description="Patient ID", gt=0)
    plan_type: Optional[PlanType] = Field(None, description="Plan type")
    is_active: Optional[bool] = Field(None, description="Active status")
    is_current: Optional[bool] = Field(None, description="Current status")
    
    # Date filters
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    
    # Nutritional filters
    min_calories: Optional[float] = Field(None, description="Minimum calories", ge=0)
    max_calories: Optional[float] = Field(None, description="Maximum calories", ge=0)
    
    # Text search
    query: Optional[str] = Field(None, description="Search query")


class PlanReplacement(BaseSchema):
    """Plan replacement schema."""
    
    plan_id: int = Field(..., description="Plan ID", gt=0)
    day: int = Field(..., description="Day number", ge=1, le=7)
    meal_type: MealType = Field(..., description="Meal type to replace")
    
    # Replacement request
    desired_food: str = Field(..., description="Desired food/recipe", min_length=2, max_length=200)
    special_instructions: Optional[str] = Field(None, description="Special instructions", max_length=300)
    
    # Context
    patient_context: Optional[dict] = Field(None, description="Patient context")
    nutritional_constraints: Optional[dict] = Field(None, description="Nutritional constraints")


class PlanReplacementResult(BaseSchema):
    """Plan replacement result schema."""
    
    original_meal: MealOption = Field(..., description="Original meal option")
    replacement_meal: MealOption = Field(..., description="Replacement meal option")
    
    # Nutritional comparison
    calorie_difference: float = Field(..., description="Calorie difference")
    protein_difference: float = Field(..., description="Protein difference")
    carbs_difference: float = Field(..., description="Carbs difference")
    fat_difference: float = Field(..., description="Fat difference")
    
    # Compliance
    within_tolerance: bool = Field(..., description="Within nutritional tolerance")
    tolerance_percentage: float = Field(5.0, description="Tolerance percentage", ge=0, le=20)
    
    # Generation info
    replacement_reason: str = Field(..., description="Replacement reason")
    generated_at: datetime = Field(..., description="Generation timestamp")


class PlanAnalytics(BaseSchema):
    """Plan analytics schema."""
    
    total_plans: int = Field(0, description="Total plans generated", ge=0)
    active_plans: int = Field(0, description="Active plans", ge=0)
    plans_this_month: int = Field(0, description="Plans generated this month", ge=0)
    
    # Plan types
    plan_type_distribution: dict = Field(default_factory=dict, description="Plan type distribution")
    
    # Nutritional analysis
    average_calories: float = Field(0, description="Average daily calories", ge=0)
    average_protein: float = Field(0, description="Average daily protein", ge=0)
    calorie_distribution: dict = Field(default_factory=dict, description="Calorie distribution")
    
    # Usage patterns
    most_popular_recipes: list[dict] = Field(default_factory=list, description="Most popular recipes")
    most_replaced_meals: list[dict] = Field(default_factory=list, description="Most replaced meals")
    
    # Compliance
    average_compliance: float = Field(0, description="Average compliance score", ge=0, le=100)
    completion_rate: float = Field(0, description="Plan completion rate", ge=0, le=100)
    
    # Feedback
    average_rating: float = Field(0, description="Average user rating", ge=0, le=5)
    total_feedback: int = Field(0, description="Total feedback received", ge=0)


class PlanGeneration(BaseSchema):
    """Plan generation request schema."""
    
    patient_id: int = Field(..., description="Patient ID", gt=0)
    plan_type: PlanType = Field(..., description="Plan type")
    
    # Generation parameters
    force_regenerate: bool = Field(False, description="Force regeneration")
    use_preferences: bool = Field(True, description="Use patient preferences")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions", max_length=500)
    
    # Context for specific plan types
    control_data: Optional[dict] = Field(None, description="Control visit data")
    replacement_data: Optional[PlanReplacement] = Field(None, description="Replacement data")
    
    # AI parameters
    temperature: float = Field(0.7, description="AI temperature", ge=0, le=1)
    max_tokens: int = Field(4000, description="Max tokens", ge=1000, le=8000)
    
    @validator("plan_type")
    def validate_plan_type_context(cls, v, values):
        """Validate plan type has required context."""
        if v == PlanType.CONTROL and not values.get("control_data"):
            raise ValueError("Control plans require control_data")
        if v == PlanType.REPLACEMENT and not values.get("replacement_data"):
            raise ValueError("Replacement plans require replacement_data")
        return v


class PlanGenerationResult(BaseSchema):
    """Plan generation result schema."""
    
    plan: Plan = Field(..., description="Generated plan")
    generation_time: float = Field(..., description="Generation time in seconds", ge=0)
    
    # Generation metadata
    tokens_used: int = Field(..., description="Tokens used", ge=0)
    model_used: str = Field(..., description="AI model used")
    rag_sources: list[str] = Field(default_factory=list, description="RAG sources used")
    
    # Quality metrics
    nutritional_accuracy: float = Field(..., description="Nutritional accuracy score", ge=0, le=1)
    preference_match: float = Field(..., description="Preference match score", ge=0, le=1)
    variety_score: float = Field(..., description="Recipe variety score", ge=0, le=1)
    
    # Warnings and notes
    warnings: list[str] = Field(default_factory=list, description="Generation warnings")
    notes: list[str] = Field(default_factory=list, description="Generation notes")


class PlanExport(BaseSchema):
    """Plan export schema."""
    
    plan_ids: list[int] = Field(..., description="Plan IDs to export", min_items=1)
    format: str = Field("pdf", description="Export format")
    include_instructions: bool = Field(True, description="Include instructions")
    include_nutrition: bool = Field(True, description="Include nutrition data")
    include_shopping_list: bool = Field(False, description="Include shopping list")
    
    @validator("format")
    def validate_format(cls, v):
        """Validate export format."""
        allowed_formats = ["pdf", "json", "csv", "docx"]
        if v not in allowed_formats:
            raise ValueError(f"Format must be one of: {allowed_formats}")
        return v


class PlanFeedback(BaseSchema):
    """Plan feedback schema."""
    
    plan_id: int = Field(..., description="Plan ID", gt=0)
    user_id: int = Field(..., description="User ID", gt=0)
    
    # Ratings
    overall_rating: float = Field(..., description="Overall rating", ge=1, le=5)
    taste_rating: float = Field(..., description="Taste rating", ge=1, le=5)
    variety_rating: float = Field(..., description="Variety rating", ge=1, le=5)
    difficulty_rating: float = Field(..., description="Difficulty rating", ge=1, le=5)
    
    # Comments
    comments: Optional[str] = Field(None, description="User comments", max_length=1000)
    favorite_meals: Optional[list[str]] = Field(None, description="Favorite meals")
    disliked_meals: Optional[list[str]] = Field(None, description="Disliked meals")
    
    # Compliance
    completion_percentage: float = Field(..., description="Completion percentage", ge=0, le=100)
    followed_days: int = Field(..., description="Days followed", ge=0)
    
    # Timestamp
    submitted_at: datetime = Field(..., description="Submission timestamp")


class PlanHistory(BaseSchema):
    """Plan history schema."""
    
    patient_id: int = Field(..., description="Patient ID", gt=0)
    plans: list[PlanSummary] = Field(..., description="Historical plans")
    
    # Statistics
    total_plans: int = Field(..., description="Total plans", ge=0)
    active_plans: int = Field(..., description="Active plans", ge=0)
    average_rating: float = Field(0, description="Average rating", ge=0, le=5)
    
    # Trends
    weight_trend: Optional[list[dict]] = Field(None, description="Weight trend data")
    compliance_trend: Optional[list[dict]] = Field(None, description="Compliance trend data")
    preference_evolution: Optional[dict] = Field(None, description="Preference evolution data")