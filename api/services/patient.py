"""
Patient service for Sistema Mayra API.
"""
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import BaseModel
from ..schemas.patient import Patient, PatientCreate, PatientUpdate, PatientStats
from .base import BaseService

logger = logging.getLogger(__name__)


class PatientModel(BaseModel):
    """Patient model placeholder."""
    __tablename__ = "patients"


class PatientService(BaseService[PatientModel, Patient]):
    """Patient service for managing patient data."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, PatientModel)
    
    async def create_patient(self, patient_data: PatientCreate) -> Optional[PatientModel]:
        """Create new patient with calculated fields."""
        try:
            # Calculate BMI, BMR, TDEE
            calculated_data = self._calculate_patient_metrics(patient_data)
            
            # Merge with patient data
            patient_dict = patient_data.model_dump()
            patient_dict.update(calculated_data)
            
            # Create patient
            patient = await self.create(patient_dict)
            
            if patient:
                logger.info(f"Created patient: {patient.name} (ID: {patient.id})")
            
            return patient
            
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            return None
    
    async def update_patient(self, patient_id: int, update_data: PatientUpdate) -> Optional[PatientModel]:
        """Update patient with recalculated metrics."""
        try:
            patient = await self.get_by_id(patient_id)
            if not patient:
                return None
            
            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # Recalculate metrics if relevant fields changed
            if any(field in update_dict for field in ['weight', 'height', 'age', 'sex', 'activity_type']):
                # Create temporary patient data for calculations
                temp_data = patient.to_dict()
                temp_data.update(update_dict)
                
                calculated_data = self._calculate_patient_metrics(temp_data)
                update_dict.update(calculated_data)
            
            # Update patient
            updated_patient = await self.update(patient_id, update_dict)
            
            if updated_patient:
                logger.info(f"Updated patient: {updated_patient.name} (ID: {patient_id})")
            
            return updated_patient
            
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {str(e)}")
            return None
    
    async def get_patient_by_telegram_id(self, telegram_user_id: int) -> Optional[PatientModel]:
        """Get patient by Telegram user ID."""
        return await self.get_by_field("telegram_user_id", telegram_user_id)
    
    async def get_patient_stats(self, patient_id: int) -> Optional[PatientStats]:
        """Get patient statistics."""
        try:
            patient = await self.get_by_id(patient_id)
            if not patient:
                return None
            
            # This would typically involve queries to related tables
            # For now, return basic stats
            stats = PatientStats(
                patient_id=patient_id,
                total_plans=0,  # Would query plans table
                total_replacements=0,  # Would query replacements table
                total_controls=0,  # Would query controls table
                weight_history=[],  # Would query weight history
                plan_history=[],  # Would query plan history
                favorite_recipes=[],  # Would query user preferences
                most_requested_replacements=[],  # Would query replacements
                compliance_rate=0.0,  # Would calculate from user feedback
                average_plan_duration=0.0  # Would calculate from plan history
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting patient stats {patient_id}: {str(e)}")
            return None
    
    async def search_patients(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search patients with filters."""
        try:
            # Build search fields
            search_fields = ['name', 'notes']
            
            # Use base search functionality
            result = await self.search(query, search_fields, page, limit)
            
            # Apply additional filters if provided
            if filters:
                # This would involve more complex filtering logic
                # For now, return basic search results
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0,
                "has_next": False,
                "has_previous": False
            }
    
    async def get_patient_analytics(self) -> Dict[str, Any]:
        """Get patient analytics."""
        try:
            total_patients = await self.get_count()
            
            # This would involve complex queries for analytics
            # For now, return basic data
            analytics = {
                "total_patients": total_patients,
                "active_patients": total_patients,  # Would filter by active
                "new_patients_this_month": 0,  # Would filter by created_at
                "age_distribution": {},  # Would group by age ranges
                "sex_distribution": {},  # Would group by sex
                "objective_distribution": {},  # Would group by objective
                "activity_distribution": {},  # Would group by activity_type
                "average_bmi": 0.0,  # Would calculate average
                "bmi_distribution": {},  # Would group by BMI ranges
                "most_common_restrictions": [],  # Would analyze restrictions
                "most_common_supplements": [],  # Would analyze supplements
                "economic_level_distribution": {}  # Would group by economic level
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting patient analytics: {str(e)}")
            return {}
    
    def _calculate_patient_metrics(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate BMI, BMR, and TDEE for patient."""
        try:
            weight = patient_data.get("weight", 0)
            height = patient_data.get("height", 0)
            age = patient_data.get("age", 0)
            sex = patient_data.get("sex", "M")
            activity_type = patient_data.get("activity_type", "sedentary")
            
            # Calculate BMI
            if height > 0:
                height_m = height / 100  # Convert cm to m
                bmi = weight / (height_m * height_m)
            else:
                bmi = 0
            
            # Calculate BMR using Mifflin-St Jeor Equation
            if sex == "M":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
            # Calculate TDEE based on activity level
            activity_multipliers = {
                "sedentary": 1.2,
                "walking": 1.375,
                "cardio": 1.55,
                "weights": 1.725,
                "mixed": 1.9,
                "athlete": 2.2
            }
            
            multiplier = activity_multipliers.get(activity_type, 1.2)
            tdee = bmr * multiplier
            
            return {
                "bmi": round(bmi, 2),
                "bmr": round(bmr, 2),
                "tdee": round(tdee, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating patient metrics: {str(e)}")
            return {
                "bmi": 0,
                "bmr": 0,
                "tdee": 0
            }
    
    async def add_weight_entry(
        self,
        patient_id: int,
        weight: float,
        notes: Optional[str] = None
    ) -> bool:
        """Add weight entry to patient history."""
        try:
            # This would typically insert into a weight_history table
            # For now, just update the patient's current weight
            patient = await self.get_by_id(patient_id)
            if not patient:
                return False
            
            # Update current weight
            updated_patient = await self.update(patient_id, {"weight": weight})
            
            if updated_patient:
                logger.info(f"Added weight entry for patient {patient_id}: {weight}kg")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding weight entry: {str(e)}")
            return False
    
    async def get_weight_history(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get patient weight history."""
        try:
            # This would typically query a weight_history table
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting weight history for patient {patient_id}: {str(e)}")
            return []
    
    async def check_patient_constraints(
        self,
        patient_id: int,
        recipe_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if recipe meets patient constraints."""
        try:
            patient = await self.get_by_id(patient_id)
            if not patient:
                return {"valid": False, "reason": "Patient not found"}
            
            # Check dietary restrictions
            patient_restrictions = patient.restrictions or []
            recipe_restrictions = recipe_data.get("dietary_restrictions", [])
            
            for restriction in patient_restrictions:
                if restriction not in recipe_restrictions:
                    return {
                        "valid": False,
                        "reason": f"Recipe doesn't support {restriction} restriction"
                    }
            
            # Check allergies
            patient_allergies = patient.allergies or []
            recipe_ingredients = recipe_data.get("ingredients", [])
            
            for allergy in patient_allergies:
                if any(allergy.lower() in ingredient.lower() for ingredient in recipe_ingredients):
                    return {
                        "valid": False,
                        "reason": f"Recipe contains allergen: {allergy}"
                    }
            
            # Check economic level
            patient_economic = patient.economic_level
            recipe_economic = recipe_data.get("economic_level", "medium")
            
            economic_levels = {"low": 1, "medium": 2, "high": 3}
            if economic_levels.get(recipe_economic, 2) > economic_levels.get(patient_economic, 2):
                return {
                    "valid": False,
                    "reason": f"Recipe economic level ({recipe_economic}) above patient level ({patient_economic})"
                }
            
            return {"valid": True, "reason": "All constraints met"}
            
        except Exception as e:
            logger.error(f"Error checking patient constraints: {str(e)}")
            return {"valid": False, "reason": "Error checking constraints"}
    
    async def get_patient_recommendations(
        self,
        patient_id: int,
        recommendation_type: str = "general"
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations for patient."""
        try:
            patient = await self.get_by_id(patient_id)
            if not patient:
                return []
            
            recommendations = []
            
            # BMI-based recommendations
            if patient.bmi < 18.5:
                recommendations.append({
                    "type": "nutrition",
                    "priority": "high",
                    "message": "Consider increasing caloric intake with healthy, nutrient-dense foods"
                })
            elif patient.bmi > 25:
                recommendations.append({
                    "type": "nutrition",
                    "priority": "medium",
                    "message": "Focus on portion control and regular physical activity"
                })
            
            # Activity-based recommendations
            if patient.activity_type == "sedentary":
                recommendations.append({
                    "type": "activity",
                    "priority": "high",
                    "message": "Consider adding light physical activity like daily walks"
                })
            
            # Age-based recommendations
            if patient.age > 50:
                recommendations.append({
                    "type": "nutrition",
                    "priority": "medium",
                    "message": "Ensure adequate protein intake for muscle maintenance"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting patient recommendations: {str(e)}")
            return []