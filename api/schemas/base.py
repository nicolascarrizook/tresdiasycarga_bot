"""
Base schemas for Sistema Mayra API.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        use_enum_values=True
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class IDMixin(BaseModel):
    """Mixin for ID field."""
    
    id: int = Field(..., description="Unique identifier", gt=0)


class ResponseBase(BaseSchema):
    """Base response schema."""
    
    success: bool = Field(True, description="Request success status")
    message: Optional[str] = Field(None, description="Response message")


class PaginatedResponse(BaseSchema):
    """Base paginated response schema."""
    
    items: list = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items", ge=0)
    page: int = Field(..., description="Current page number", ge=1)
    limit: int = Field(..., description="Items per page", ge=1)
    total_pages: int = Field(..., description="Total number of pages", ge=1)
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")


class HealthCheckResponse(BaseSchema):
    """Health check response schema."""
    
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    services: dict = Field(..., description="Individual service statuses")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseSchema):
    """Error response schema."""
    
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(..., description="Error timestamp")


class BulkOperationResponse(BaseSchema):
    """Bulk operation response schema."""
    
    success: bool = Field(..., description="Operation success status")
    total_processed: int = Field(..., description="Total items processed", ge=0)
    successful: int = Field(..., description="Successfully processed items", ge=0)
    failed: int = Field(..., description="Failed items", ge=0)
    errors: list[dict] = Field(default_factory=list, description="List of errors")


class MacroNutrients(BaseSchema):
    """Macro nutrients schema."""
    
    calories: float = Field(..., description="Calories in kcal", ge=0)
    protein: float = Field(..., description="Protein in grams", ge=0)
    carbs: float = Field(..., description="Carbohydrates in grams", ge=0)
    fat: float = Field(..., description="Fat in grams", ge=0)
    fiber: Optional[float] = Field(None, description="Fiber in grams", ge=0)
    sugar: Optional[float] = Field(None, description="Sugar in grams", ge=0)
    sodium: Optional[float] = Field(None, description="Sodium in mg", ge=0)


class PortionSize(BaseSchema):
    """Portion size schema."""
    
    amount: float = Field(..., description="Amount", gt=0)
    unit: str = Field(..., description="Unit of measurement")
    weight_grams: Optional[float] = Field(None, description="Weight in grams", gt=0)


class Ingredient(BaseSchema):
    """Ingredient schema."""
    
    name: str = Field(..., description="Ingredient name", min_length=1, max_length=100)
    amount: float = Field(..., description="Amount", gt=0)
    unit: str = Field(..., description="Unit of measurement", min_length=1, max_length=20)
    category: Optional[str] = Field(None, description="Ingredient category")
    notes: Optional[str] = Field(None, description="Additional notes", max_length=200)


class AddressInfo(BaseSchema):
    """Address information schema."""
    
    country: str = Field(..., description="Country", min_length=2, max_length=50)
    state: Optional[str] = Field(None, description="State/Province", max_length=50)
    city: Optional[str] = Field(None, description="City", max_length=50)
    timezone: str = Field("America/Argentina/Buenos_Aires", description="Timezone")


class ContactInfo(BaseSchema):
    """Contact information schema."""
    
    phone: Optional[str] = Field(None, description="Phone number", max_length=20)
    email: Optional[str] = Field(None, description="Email address", max_length=100)
    telegram_username: Optional[str] = Field(None, description="Telegram username", max_length=50)


class FileInfo(BaseSchema):
    """File information schema."""
    
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="File storage path")
    file_size: int = Field(..., description="File size in bytes", ge=0)
    content_type: str = Field(..., description="MIME content type")
    uploaded_at: datetime = Field(..., description="Upload timestamp")


class SearchParams(BaseSchema):
    """Search parameters schema."""
    
    query: Optional[str] = Field(None, description="Search query")
    category: Optional[str] = Field(None, description="Category filter")
    tags: Optional[list[str]] = Field(None, description="Tags filter")
    economic_level: Optional[str] = Field(None, description="Economic level filter")
    dietary_restrictions: Optional[list[str]] = Field(None, description="Dietary restrictions filter")
    limit: int = Field(20, description="Results limit", ge=1, le=100)
    offset: int = Field(0, description="Results offset", ge=0)


class ValidationError(BaseSchema):
    """Validation error schema."""
    
    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Error message")
    value: Optional[str] = Field(None, description="Invalid value")


class BatchProcessingStatus(BaseSchema):
    """Batch processing status schema."""
    
    batch_id: str = Field(..., description="Batch identifier")
    status: str = Field(..., description="Processing status")
    total_items: int = Field(..., description="Total items to process", ge=0)
    processed_items: int = Field(..., description="Items processed", ge=0)
    failed_items: int = Field(..., description="Failed items", ge=0)
    started_at: datetime = Field(..., description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")
    errors: list[ValidationError] = Field(default_factory=list, description="Processing errors")


class CacheInfo(BaseSchema):
    """Cache information schema."""
    
    key: str = Field(..., description="Cache key")
    ttl: int = Field(..., description="Time to live in seconds", ge=0)
    hit: bool = Field(..., description="Cache hit status")
    size: Optional[int] = Field(None, description="Cache entry size", ge=0)


class APIMetrics(BaseSchema):
    """API metrics schema."""
    
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(..., description="HTTP method")
    status_code: int = Field(..., description="HTTP status code")
    response_time: float = Field(..., description="Response time in milliseconds", ge=0)
    timestamp: datetime = Field(..., description="Request timestamp")
    user_id: Optional[int] = Field(None, description="User ID if authenticated")
    ip_address: Optional[str] = Field(None, description="Client IP address")


class SystemInfo(BaseSchema):
    """System information schema."""
    
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment name")
    uptime: float = Field(..., description="System uptime in seconds", ge=0)
    memory_usage: dict = Field(..., description="Memory usage statistics")
    cpu_usage: float = Field(..., description="CPU usage percentage", ge=0, le=100)
    active_connections: int = Field(..., description="Active database connections", ge=0)
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage", ge=0, le=100)