"""
API service for communication with FastAPI backend.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import httpx
import json

from ..config import bot_settings
from ..states.user_data import PatientData


logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """API response wrapper."""
    
    success: bool
    data: Any = None
    error: Optional[str] = None
    status_code: int = 200
    
    @classmethod
    def success_response(cls, data: Any, status_code: int = 200) -> "APIResponse":
        """Create success response."""
        return cls(success=True, data=data, status_code=status_code)
    
    @classmethod
    def error_response(cls, error: str, status_code: int = 400) -> "APIResponse":
        """Create error response."""
        return cls(success=False, error=error, status_code=status_code)


class APIError(Exception):
    """API error exception."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class APIClient:
    """HTTP client for API communication."""
    
    def __init__(self, base_url: str = None, timeout: int = 30):
        """Initialize API client."""
        self.base_url = base_url or bot_settings.api_base_url
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Sistema-Mayra-Bot/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> APIResponse:
        """Make GET request."""
        try:
            response = await self.session.get(endpoint, params=params)
            return await self._handle_response(response)
        except httpx.RequestError as e:
            logger.error(f"GET request failed: {e}")
            return APIResponse.error_response(f"Request failed: {str(e)}", 500)
        except Exception as e:
            logger.error(f"Unexpected error in GET request: {e}")
            return APIResponse.error_response(f"Unexpected error: {str(e)}", 500)
    
    async def post(self, endpoint: str, data: Dict[str, Any] = None) -> APIResponse:
        """Make POST request."""
        try:
            response = await self.session.post(endpoint, json=data)
            return await self._handle_response(response)
        except httpx.RequestError as e:
            logger.error(f"POST request failed: {e}")
            return APIResponse.error_response(f"Request failed: {str(e)}", 500)
        except Exception as e:
            logger.error(f"Unexpected error in POST request: {e}")
            return APIResponse.error_response(f"Unexpected error: {str(e)}", 500)
    
    async def put(self, endpoint: str, data: Dict[str, Any] = None) -> APIResponse:
        """Make PUT request."""
        try:
            response = await self.session.put(endpoint, json=data)
            return await self._handle_response(response)
        except httpx.RequestError as e:
            logger.error(f"PUT request failed: {e}")
            return APIResponse.error_response(f"Request failed: {str(e)}", 500)
        except Exception as e:
            logger.error(f"Unexpected error in PUT request: {e}")
            return APIResponse.error_response(f"Unexpected error: {str(e)}", 500)
    
    async def delete(self, endpoint: str) -> APIResponse:
        """Make DELETE request."""
        try:
            response = await self.session.delete(endpoint)
            return await self._handle_response(response)
        except httpx.RequestError as e:
            logger.error(f"DELETE request failed: {e}")
            return APIResponse.error_response(f"Request failed: {str(e)}", 500)
        except Exception as e:
            logger.error(f"Unexpected error in DELETE request: {e}")
            return APIResponse.error_response(f"Unexpected error: {str(e)}", 500)
    
    async def _handle_response(self, response: httpx.Response) -> APIResponse:
        """Handle HTTP response."""
        try:
            if response.status_code == 200:
                data = response.json()
                return APIResponse.success_response(data, response.status_code)
            elif response.status_code == 201:
                data = response.json()
                return APIResponse.success_response(data, response.status_code)
            elif response.status_code == 204:
                return APIResponse.success_response(None, response.status_code)
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("detail", f"HTTP {response.status_code}")
                return APIResponse.error_response(error_message, response.status_code)
        except json.JSONDecodeError:
            return APIResponse.error_response(
                f"Invalid JSON response: {response.text}",
                response.status_code
            )
        except Exception as e:
            logger.error(f"Error handling response: {e}")
            return APIResponse.error_response(
                f"Response handling error: {str(e)}",
                response.status_code
            )


class APIService:
    """Main API service class."""
    
    def __init__(self, base_url: str = None, timeout: int = 30):
        """Initialize API service."""
        self.base_url = base_url or bot_settings.api_base_url
        self.timeout = timeout
    
    async def health_check(self) -> APIResponse:
        """Check API health."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.get("/health")
    
    async def create_patient(self, patient_data: PatientData) -> APIResponse:
        """Create new patient."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.post("/patients", patient_data.to_dict())
    
    async def get_patient(self, telegram_user_id: int) -> APIResponse:
        """Get patient by telegram user ID."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.get(f"/patients/telegram/{telegram_user_id}")
    
    async def update_patient(self, patient_id: int, patient_data: Dict[str, Any]) -> APIResponse:
        """Update patient information."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.put(f"/patients/{patient_id}", patient_data)
    
    async def generate_plan(self, patient_id: int, plan_type: str = "nuevo_paciente") -> APIResponse:
        """Generate nutrition plan."""
        async with APIClient(self.base_url, self.timeout) as client:
            data = {
                "patient_id": patient_id,
                "plan_type": plan_type
            }
            return await client.post("/plans/generate", data)
    
    async def get_plan(self, plan_id: str) -> APIResponse:
        """Get plan by ID."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.get(f"/plans/{plan_id}")
    
    async def get_patient_plans(self, patient_id: int) -> APIResponse:
        """Get all plans for a patient."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.get(f"/patients/{patient_id}/plans")
    
    async def generate_meal_replacement(self, 
                                      plan_id: str, 
                                      day: str, 
                                      meal_type: str,
                                      replacement_data: Dict[str, Any]) -> APIResponse:
        """Generate meal replacement."""
        async with APIClient(self.base_url, self.timeout) as client:
            data = {
                "plan_id": plan_id,
                "day": day,
                "meal_type": meal_type,
                **replacement_data
            }
            return await client.post("/plans/replace-meal", data)
    
    async def generate_pdf(self, plan_id: str) -> APIResponse:
        """Generate PDF for plan."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.post(f"/plans/{plan_id}/pdf")
    
    async def get_recipes(self, 
                         category: str = None, 
                         dietary_restrictions: List[str] = None,
                         economic_level: str = None) -> APIResponse:
        """Get recipes with filters."""
        params = {}
        if category:
            params["category"] = category
        if dietary_restrictions:
            params["dietary_restrictions"] = ",".join(dietary_restrictions)
        if economic_level:
            params["economic_level"] = economic_level
        
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.get("/recipes", params)
    
    async def search_recipes(self, query: str, limit: int = 10) -> APIResponse:
        """Search recipes."""
        params = {"q": query, "limit": limit}
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.get("/recipes/search", params)
    
    async def validate_patient_data(self, patient_data: Dict[str, Any]) -> APIResponse:
        """Validate patient data."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.post("/patients/validate", patient_data)
    
    async def calculate_nutritional_needs(self, patient_data: Dict[str, Any]) -> APIResponse:
        """Calculate nutritional needs."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.post("/patients/calculate-needs", patient_data)
    
    async def get_plan_statistics(self, patient_id: int) -> APIResponse:
        """Get plan statistics for patient."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.get(f"/patients/{patient_id}/stats")
    
    async def log_bot_interaction(self, interaction_data: Dict[str, Any]) -> APIResponse:
        """Log bot interaction."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.post("/bot/interactions", interaction_data)
    
    async def get_system_status(self) -> APIResponse:
        """Get system status."""
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.get("/system/status")
    
    async def get_analytics(self, 
                          start_date: str = None, 
                          end_date: str = None) -> APIResponse:
        """Get analytics data."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        async with APIClient(self.base_url, self.timeout) as client:
            return await client.get("/analytics", params)
    
    async def retry_with_backoff(self, 
                               operation, 
                               max_retries: int = 3,
                               base_delay: float = 1.0) -> APIResponse:
        """Retry operation with exponential backoff."""
        for attempt in range(max_retries):
            try:
                response = await operation()
                if response.success:
                    return response
                
                # If not success but not a server error, don't retry
                if response.status_code < 500:
                    return response
                
                # Server error, retry with backoff
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"API operation failed, retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    return response
                    
            except Exception as e:
                logger.error(f"API operation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    return APIResponse.error_response(f"Max retries exceeded: {str(e)}", 500)
        
        return APIResponse.error_response("Operation failed after max retries", 500)


class APIServiceManager:
    """API service manager for connection pooling and caching."""
    
    _instance = None
    _service = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_service(self) -> APIService:
        """Get API service instance."""
        if self._service is None:
            self._service = APIService()
        return self._service
    
    async def test_connection(self) -> bool:
        """Test API connection."""
        try:
            service = self.get_service()
            response = await service.health_check()
            return response.success
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False
    
    async def warmup_connections(self) -> None:
        """Warm up API connections."""
        try:
            service = self.get_service()
            await service.health_check()
            logger.info("API connections warmed up successfully")
        except Exception as e:
            logger.error(f"API warmup failed: {e}")


# Global API service manager
api_manager = APIServiceManager()

# Convenience functions
async def get_api_service() -> APIService:
    """Get API service instance."""
    return api_manager.get_service()

async def test_api_connection() -> bool:
    """Test API connection."""
    return await api_manager.test_connection()

async def warmup_api_connections() -> None:
    """Warm up API connections."""
    await api_manager.warmup_connections()