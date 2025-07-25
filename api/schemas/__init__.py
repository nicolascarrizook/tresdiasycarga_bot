"""
Schemas package for Sistema Mayra API.
"""
from .base import (
    BaseSchema,
    ResponseBase,
    PaginatedResponse,
    HealthCheckResponse,
    ErrorResponse,
    BulkOperationResponse,
    MacroNutrients,
    PortionSize,
    Ingredient,
    AddressInfo,
    ContactInfo,
    FileInfo,
    SearchParams,
    ValidationError,
    BatchProcessingStatus,
    CacheInfo,
    APIMetrics,
    SystemInfo,
    TimestampMixin,
    IDMixin
)

from .auth import (
    User,
    UserCreate,
    UserUpdate,
    UserProfile,
    Token,
    TokenData,
    TokenRefresh,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    SessionInfo,
    UserActivity,
    UserStats,
    AdminUserUpdate,
    UserSearch,
    BulkUserAction,
    UserExport,
    APIKey,
    APIKeyCreate,
    APIKeyUpdate
)

from .patient import (
    Patient,
    PatientCreate,
    PatientUpdate,
    PatientSummary,
    PatientSearch,
    PatientStats,
    PatientAnalytics,
    WeightEntry,
    WeightHistory,
    PatientExport,
    PatientBulkAction
)

from .recipe import (
    Recipe,
    RecipeCreate,
    RecipeUpdate,
    RecipeSummary,
    RecipeSearch,
    RecipeEquivalent,
    RecipeRating,
    RecipeNutrition,
    RecipeVariation,
    RecipeAnalytics,
    RecipeImport,
    RecipeExport,
    RecipeBulkAction,
    RecipeRecommendation
)

from .plan import (
    Plan,
    PlanCreate,
    PlanUpdate,
    PlanSummary,
    PlanSearch,
    MealPlan,
    MealOption,
    DayPlan,
    PlanReplacement,
    PlanReplacementResult,
    PlanAnalytics,
    PlanGeneration,
    PlanGenerationResult,
    PlanExport,
    PlanFeedback,
    PlanHistory
)

__all__ = [
    # Base schemas
    "BaseSchema",
    "ResponseBase",
    "PaginatedResponse",
    "HealthCheckResponse",
    "ErrorResponse",
    "BulkOperationResponse",
    "MacroNutrients",
    "PortionSize",
    "Ingredient",
    "AddressInfo",
    "ContactInfo",
    "FileInfo",
    "SearchParams",
    "ValidationError",
    "BatchProcessingStatus",
    "CacheInfo",
    "APIMetrics",
    "SystemInfo",
    "TimestampMixin",
    "IDMixin",
    
    # Auth schemas
    "User",
    "UserCreate",
    "UserUpdate",
    "UserProfile",
    "Token",
    "TokenData",
    "TokenRefresh",
    "LoginRequest",
    "LoginResponse",
    "LogoutRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "SessionInfo",
    "UserActivity",
    "UserStats",
    "AdminUserUpdate",
    "UserSearch",
    "BulkUserAction",
    "UserExport",
    "APIKey",
    "APIKeyCreate",
    "APIKeyUpdate",
    
    # Patient schemas
    "Patient",
    "PatientCreate",
    "PatientUpdate",
    "PatientSummary",
    "PatientSearch",
    "PatientStats",
    "PatientAnalytics",
    "WeightEntry",
    "WeightHistory",
    "PatientExport",
    "PatientBulkAction",
    
    # Recipe schemas
    "Recipe",
    "RecipeCreate",
    "RecipeUpdate",
    "RecipeSummary",
    "RecipeSearch",
    "RecipeEquivalent",
    "RecipeRating",
    "RecipeNutrition",
    "RecipeVariation",
    "RecipeAnalytics",
    "RecipeImport",
    "RecipeExport",
    "RecipeBulkAction",
    "RecipeRecommendation",
    
    # Plan schemas
    "Plan",
    "PlanCreate",
    "PlanUpdate",
    "PlanSummary",
    "PlanSearch",
    "MealPlan",
    "MealOption",
    "DayPlan",
    "PlanReplacement",
    "PlanReplacementResult",
    "PlanAnalytics",
    "PlanGeneration",
    "PlanGenerationResult",
    "PlanExport",
    "PlanFeedback",
    "PlanHistory",
]