"""
Patient schemas for Sistema Mayra API.
"""
from datetime import datetime
from typing import Optional

from pydantic import Field, validator

from ..core.settings import (
    ObjectiveType, ActivityType, FrequencyType, WeightType, 
    EconomicLevel, DietaryRestriction, SupplementType
)
from .base import BaseSchema, IDMixin, TimestampMixin, ContactInfo, AddressInfo


class PatientBase(BaseSchema):
    """Base patient schema."""
    
    name: str = Field(..., description="Patient name", min_length=2, max_length=100)
    age: int = Field(..., description="Patient age", ge=16, le=100)
    sex: str = Field(..., description="Patient sex", regex="^(M|F)$")
    height: float = Field(..., description="Height in cm", ge=140, le=220)
    weight: float = Field(..., description="Weight in kg", ge=40, le=200)
    objective: ObjectiveType = Field(..., description="Nutrition objective")
    activity_type: ActivityType = Field(..., description="Physical activity type")
    frequency: FrequencyType = Field(..., description="Activity frequency")
    duration: int = Field(..., description="Activity duration in minutes", ge=15, le=300)
    peso_tipo: WeightType = Field(WeightType.CRUDO, description="Weight measurement type")
    economic_level: EconomicLevel = Field(EconomicLevel.MEDIUM, description="Economic level")
    
    # Optional fields
    supplements: list[SupplementType] = Field(default_factory=list, description="Current supplements")
    pathologies: list[str] = Field(default_factory=list, description="Medical conditions")
    restrictions: list[DietaryRestriction] = Field(default_factory=list, description="Dietary restrictions")
    preferences: list[str] = Field(default_factory=list, description="Food preferences")
    dislikes: list[str] = Field(default_factory=list, description="Food dislikes")
    allergies: list[str] = Field(default_factory=list, description="Food allergies")
    
    # Meal configuration
    main_meals: int = Field(3, description="Number of main meals", ge=2, le=5)
    collations: int = Field(2, description="Number of collations", ge=0, le=3)
    
    # Schedule and notes
    schedule: Optional[dict] = Field(None, description="Meal schedule preferences")
    notes: Optional[str] = Field(None, description="Additional notes", max_length=1000)
    
    @validator("sex")
    def validate_sex(cls, v):
        """Validate sex value."""
        if v not in ["M", "F"]:
            raise ValueError("Sex must be 'M' or 'F'")
        return v
    
    @validator("pathologies", pre=True)
    def validate_pathologies(cls, v):
        """Validate pathologies list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v or []
    
    @validator("preferences", "dislikes", "allergies", pre=True)
    def validate_string_lists(cls, v):
        """Validate string lists."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v or []


class PatientCreate(PatientBase):
    """Patient creation schema."""
    
    telegram_user_id: int = Field(..., description="Telegram user ID", gt=0)
    
    # Optional contact and address info
    contact_info: Optional[ContactInfo] = Field(None, description="Contact information")
    address_info: Optional[AddressInfo] = Field(None, description="Address information")


class PatientUpdate(BaseSchema):
    """Patient update schema."""
    
    name: Optional[str] = Field(None, description="Patient name", min_length=2, max_length=100)
    age: Optional[int] = Field(None, description="Patient age", ge=16, le=100)
    sex: Optional[str] = Field(None, description="Patient sex", regex="^(M|F)$")
    height: Optional[float] = Field(None, description="Height in cm", ge=140, le=220)
    weight: Optional[float] = Field(None, description="Weight in kg", ge=40, le=200)
    objective: Optional[ObjectiveType] = Field(None, description="Nutrition objective")
    activity_type: Optional[ActivityType] = Field(None, description="Physical activity type")
    frequency: Optional[FrequencyType] = Field(None, description="Activity frequency")
    duration: Optional[int] = Field(None, description="Activity duration in minutes", ge=15, le=300)
    peso_tipo: Optional[WeightType] = Field(None, description="Weight measurement type")
    economic_level: Optional[EconomicLevel] = Field(None, description="Economic level")
    
    supplements: Optional[list[SupplementType]] = Field(None, description="Current supplements")
    pathologies: Optional[list[str]] = Field(None, description="Medical conditions")
    restrictions: Optional[list[DietaryRestriction]] = Field(None, description="Dietary restrictions")
    preferences: Optional[list[str]] = Field(None, description="Food preferences")
    dislikes: Optional[list[str]] = Field(None, description="Food dislikes")
    allergies: Optional[list[str]] = Field(None, description="Food allergies")
    
    main_meals: Optional[int] = Field(None, description="Number of main meals", ge=2, le=5)
    collations: Optional[int] = Field(None, description="Number of collations", ge=0, le=3)
    
    schedule: Optional[dict] = Field(None, description="Meal schedule preferences")
    notes: Optional[str] = Field(None, description="Additional notes", max_length=1000)
    
    contact_info: Optional[ContactInfo] = Field(None, description="Contact information")
    address_info: Optional[AddressInfo] = Field(None, description="Address information")


class Patient(PatientBase, IDMixin, TimestampMixin):
    """Patient response schema."""
    
    telegram_user_id: int = Field(..., description="Telegram user ID", gt=0)
    is_active: bool = Field(True, description="Patient active status")
    
    # Calculated fields
    bmi: float = Field(..., description="Body Mass Index", ge=10, le=50)
    bmr: float = Field(..., description="Basal Metabolic Rate", ge=800, le=4000)
    tdee: float = Field(..., description="Total Daily Energy Expenditure", ge=1000, le=5000)
    
    # Relationship fields
    total_plans: int = Field(0, description="Total plans generated", ge=0)
    last_plan_date: Optional[datetime] = Field(None, description="Last plan generation date")
    
    # Additional info
    contact_info: Optional[ContactInfo] = Field(None, description="Contact information")
    address_info: Optional[AddressInfo] = Field(None, description="Address information")
    
    @property
    def age_category(self) -> str:
        """Get age category."""
        if self.age < 20:
            return "adolescent"
        elif self.age < 40:
            return "young_adult"
        elif self.age < 60:
            return "adult"
        else:
            return "senior"
    
    @property
    def activity_level(self) -> str:
        """Get activity level description."""
        if self.activity_type == ActivityType.SEDENTARY:
            return "sedentary"
        elif self.activity_type in [ActivityType.WALKING, ActivityType.CARDIO]:
            return "light"
        elif self.activity_type == ActivityType.WEIGHTS:
            return "moderate"
        elif self.activity_type == ActivityType.MIXED:
            return "high"
        else:
            return "very_high"
    
    @property
    def bmi_category(self) -> str:
        """Get BMI category."""
        if self.bmi < 18.5:
            return "underweight"
        elif self.bmi < 25:
            return "normal"
        elif self.bmi < 30:
            return "overweight"
        else:
            return "obese"


class PatientSummary(BaseSchema):
    """Patient summary schema."""
    
    id: int = Field(..., description="Patient ID", gt=0)
    name: str = Field(..., description="Patient name")
    age: int = Field(..., description="Patient age")
    sex: str = Field(..., description="Patient sex")
    weight: float = Field(..., description="Current weight")
    objective: ObjectiveType = Field(..., description="Nutrition objective")
    last_plan_date: Optional[datetime] = Field(None, description="Last plan generation date")
    total_plans: int = Field(0, description="Total plans generated", ge=0)
    is_active: bool = Field(True, description="Patient active status")


class PatientSearch(BaseSchema):
    """Patient search schema."""
    
    query: Optional[str] = Field(None, description="Search query")
    age_min: Optional[int] = Field(None, description="Minimum age", ge=16)
    age_max: Optional[int] = Field(None, description="Maximum age", le=100)
    sex: Optional[str] = Field(None, description="Patient sex", regex="^(M|F)$")
    objective: Optional[ObjectiveType] = Field(None, description="Nutrition objective")
    activity_type: Optional[ActivityType] = Field(None, description="Physical activity type")
    economic_level: Optional[EconomicLevel] = Field(None, description="Economic level")
    has_restrictions: Optional[bool] = Field(None, description="Has dietary restrictions")
    is_active: Optional[bool] = Field(None, description="Active status")
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")


class PatientStats(BaseSchema):
    """Patient statistics schema."""
    
    patient_id: int = Field(..., description="Patient ID", gt=0)
    total_plans: int = Field(0, description="Total plans generated", ge=0)
    total_replacements: int = Field(0, description="Total meal replacements", ge=0)
    total_controls: int = Field(0, description="Total control visits", ge=0)
    weight_history: list[dict] = Field(default_factory=list, description="Weight history")
    plan_history: list[dict] = Field(default_factory=list, description="Plan generation history")
    favorite_recipes: list[str] = Field(default_factory=list, description="Favorite recipe IDs")
    most_requested_replacements: list[dict] = Field(default_factory=list, description="Most requested replacements")
    compliance_rate: float = Field(0, description="Plan compliance rate", ge=0, le=100)
    average_plan_duration: float = Field(0, description="Average plan duration in days", ge=0)


class PatientAnalytics(BaseSchema):
    """Patient analytics schema."""
    
    total_patients: int = Field(0, description="Total patients", ge=0)
    active_patients: int = Field(0, description="Active patients", ge=0)
    new_patients_this_month: int = Field(0, description="New patients this month", ge=0)
    
    # Demographics
    age_distribution: dict = Field(default_factory=dict, description="Age distribution")
    sex_distribution: dict = Field(default_factory=dict, description="Sex distribution")
    objective_distribution: dict = Field(default_factory=dict, description="Objective distribution")
    activity_distribution: dict = Field(default_factory=dict, description="Activity distribution")
    
    # Health metrics
    average_bmi: float = Field(0, description="Average BMI", ge=0)
    bmi_distribution: dict = Field(default_factory=dict, description="BMI distribution")
    
    # Preferences
    most_common_restrictions: list[dict] = Field(default_factory=list, description="Most common restrictions")
    most_common_supplements: list[dict] = Field(default_factory=list, description="Most common supplements")
    economic_level_distribution: dict = Field(default_factory=dict, description="Economic level distribution")


class WeightEntry(BaseSchema):
    """Weight entry schema."""
    
    patient_id: int = Field(..., description="Patient ID", gt=0)
    weight: float = Field(..., description="Weight in kg", ge=40, le=200)
    date: datetime = Field(..., description="Measurement date")
    notes: Optional[str] = Field(None, description="Additional notes", max_length=200)


class WeightHistory(BaseSchema):
    """Weight history schema."""
    
    patient_id: int = Field(..., description="Patient ID", gt=0)
    entries: list[WeightEntry] = Field(..., description="Weight entries")
    weight_change: float = Field(..., description="Total weight change in kg")
    weight_change_percentage: float = Field(..., description="Weight change percentage")
    trend: str = Field(..., description="Weight trend (up/down/stable)")
    
    @validator("trend")
    def validate_trend(cls, v):
        """Validate trend value."""
        if v not in ["up", "down", "stable"]:
            raise ValueError("Trend must be 'up', 'down', or 'stable'")
        return v


class PatientExport(BaseSchema):
    """Patient export schema."""
    
    format: str = Field("csv", description="Export format")
    filters: Optional[PatientSearch] = Field(None, description="Export filters")
    fields: Optional[list[str]] = Field(None, description="Fields to include")
    include_history: bool = Field(False, description="Include weight/plan history")
    
    @validator("format")
    def validate_format(cls, v):
        """Validate export format."""
        allowed_formats = ["csv", "json", "xlsx"]
        if v not in allowed_formats:
            raise ValueError(f"Format must be one of: {allowed_formats}")
        return v


class PatientBulkAction(BaseSchema):
    """Bulk patient action schema."""
    
    patient_ids: list[int] = Field(..., description="List of patient IDs", min_items=1)
    action: str = Field(..., description="Action to perform")
    parameters: Optional[dict] = Field(None, description="Action parameters")
    
    @validator("action")
    def validate_action(cls, v):
        """Validate action type."""
        allowed_actions = ["activate", "deactivate", "delete", "update", "export"]
        if v not in allowed_actions:
            raise ValueError(f"Action must be one of: {allowed_actions}")
        return v