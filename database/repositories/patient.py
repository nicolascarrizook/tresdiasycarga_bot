"""
Patient repository for Sistema Mayra.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.patient import Patient, SexEnum, ObjectiveEnum, ActivityTypeEnum, EconomicLevelEnum
from database.models.user import User
from .base import BaseRepository, FilterOptions


class PatientRepository(BaseRepository[Patient]):
    """Patient repository with specialized methods."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Patient)
    
    async def get_by_telegram_user_id(self, telegram_user_id: int) -> Optional[Patient]:
        """Get patient by Telegram user ID."""
        return await self.find_one_by(telegram_user_id=telegram_user_id)
    
    async def get_by_email(self, email: str) -> Optional[Patient]:
        """Get patient by email."""
        return await self.find_one_by(email=email.lower())
    
    async def create_patient(self, telegram_user_id: int, name: str, age: int, 
                           sex: SexEnum, height: float, weight: float,
                           objective: ObjectiveEnum, activity_type: ActivityTypeEnum,
                           economic_level: EconomicLevelEnum, **kwargs) -> Patient:
        """Create new patient."""
        patient_data = {
            "telegram_user_id": telegram_user_id,
            "name": name,
            "age": age,
            "sex": sex,
            "height": height,
            "weight": weight,
            "initial_weight": weight,
            "objective": objective,
            "activity_type": activity_type,
            "economic_level": economic_level,
            "peso_tipo": "crudo",
            "main_meals_count": 3,
            "snacks_enabled": True,
            "is_active_patient": True,
            **kwargs
        }
        
        patient = await self.create(**patient_data)
        patient.update_search_vector()
        await self.session.commit()
        await self.session.refresh(patient)
        
        return patient
    
    async def update_weight(self, patient_id: int, new_weight: float, 
                          notes: Optional[str] = None) -> bool:
        """Update patient weight with history."""
        patient = await self.get_by_id(patient_id)
        if not patient:
            return False
        
        patient.update_weight(new_weight, notes)
        await self.session.commit()
        return True
    
    async def get_with_plans(self, patient_id: int) -> Optional[Patient]:
        """Get patient with plans."""
        stmt = select(Patient).where(Patient.id == patient_id).options(
            selectinload(Patient.plans)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_conversations(self, patient_id: int) -> Optional[Patient]:
        """Get patient with conversations."""
        stmt = select(Patient).where(Patient.id == patient_id).options(
            selectinload(Patient.conversations)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search_patients(self, query: str, page: int = 1, per_page: int = 20):
        """Search patients."""
        return await self.search(
            query=query,
            fields=["name", "email", "telegram_username", "search_vector"],
            page=page,
            per_page=per_page
        )
    
    async def get_by_objective(self, objective: ObjectiveEnum) -> List[Patient]:
        """Get patients by objective."""
        return await self.find_by(objective=objective)
    
    async def get_by_activity_type(self, activity_type: ActivityTypeEnum) -> List[Patient]:
        """Get patients by activity type."""
        return await self.find_by(activity_type=activity_type)
    
    async def get_by_economic_level(self, economic_level: EconomicLevelEnum) -> List[Patient]:
        """Get patients by economic level."""
        return await self.find_by(economic_level=economic_level)
    
    async def get_by_sex(self, sex: SexEnum) -> List[Patient]:
        """Get patients by sex."""
        return await self.find_by(sex=sex)
    
    async def get_by_age_range(self, min_age: int, max_age: int) -> List[Patient]:
        """Get patients by age range."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                Patient.age >= min_age,
                Patient.age <= max_age
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_bmi_range(self, min_bmi: float, max_bmi: float) -> List[Patient]:
        """Get patients by BMI range."""
        # Calculate BMI in SQL
        bmi_expr = Patient.weight / ((Patient.height / 100) * (Patient.height / 100))
        
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                bmi_expr >= min_bmi,
                bmi_expr <= max_bmi
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_with_pathology(self, pathology: str) -> List[Patient]:
        """Get patients with specific pathology."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            Patient.pathologies.contains([pathology])
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_with_restriction(self, restriction: str) -> List[Patient]:
        """Get patients with specific dietary restriction."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            Patient.restrictions.contains([restriction])
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_with_allergy(self, allergy: str) -> List[Patient]:
        """Get patients with specific allergy."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            Patient.allergies.contains([allergy])
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_needing_consultation(self) -> List[Patient]:
        """Get patients needing consultation."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                Patient.next_consultation.is_not(None),
                Patient.next_consultation <= datetime.utcnow()
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_recent_weight_updates(self, days: int = 7) -> List[Patient]:
        """Get patients with recent weight updates."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            Patient.last_weight_update >= datetime.utcnow() - timedelta(days=days)
        )
        filter_options.add_order_by(Patient.last_weight_update, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_user(self, user_id: int) -> List[Patient]:
        """Get patients by user ID."""
        return await self.find_by(user_id=user_id)
    
    async def update_search_vectors(self) -> int:
        """Update search vectors for all patients."""
        patients = await self.get_all(active_only=False)
        for patient in patients:
            patient.update_search_vector()
        
        await self.session.commit()
        return len(patients)
    
    async def get_statistics_by_objective(self) -> Dict[str, int]:
        """Get statistics by objective."""
        stmt = select(Patient.objective, func.count(Patient.id)).group_by(Patient.objective)
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_statistics_by_activity_type(self) -> Dict[str, int]:
        """Get statistics by activity type."""
        stmt = select(Patient.activity_type, func.count(Patient.id)).group_by(Patient.activity_type)
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_statistics_by_economic_level(self) -> Dict[str, int]:
        """Get statistics by economic level."""
        stmt = select(Patient.economic_level, func.count(Patient.id)).group_by(Patient.economic_level)
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_age_distribution(self) -> Dict[str, int]:
        """Get age distribution."""
        from sqlalchemy import case
        
        age_ranges = [
            ("18-25", 18, 25),
            ("26-35", 26, 35),
            ("36-45", 36, 45),
            ("46-55", 46, 55),
            ("56-65", 56, 65),
            ("66+", 66, 100)
        ]
        
        cases = []
        for range_name, min_age, max_age in age_ranges:
            cases.append(
                case(
                    [(and_(Patient.age >= min_age, Patient.age <= max_age), range_name)],
                    else_=None
                )
            )
        
        stmt = select(
            case(cases, else_="other").label("age_range"),
            func.count(Patient.id)
        ).group_by("age_range")
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_bmi_distribution(self) -> Dict[str, int]:
        """Get BMI distribution."""
        from sqlalchemy import case
        
        bmi_expr = Patient.weight / ((Patient.height / 100) * (Patient.height / 100))
        
        bmi_categories = case(
            [
                (bmi_expr < 18.5, "underweight"),
                (bmi_expr < 25, "normal"),
                (bmi_expr < 30, "overweight"),
                (bmi_expr >= 30, "obese")
            ],
            else_="unknown"
        )
        
        stmt = select(
            bmi_categories.label("bmi_category"),
            func.count(Patient.id)
        ).group_by("bmi_category")
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_weight_progress_summary(self) -> Dict[str, Any]:
        """Get weight progress summary."""
        # Patients with weight loss
        weight_loss_stmt = select(func.count(Patient.id)).where(
            Patient.weight < Patient.initial_weight
        )
        weight_loss_result = await self.session.execute(weight_loss_stmt)
        weight_loss = weight_loss_result.scalar()
        
        # Patients with weight gain
        weight_gain_stmt = select(func.count(Patient.id)).where(
            Patient.weight > Patient.initial_weight
        )
        weight_gain_result = await self.session.execute(weight_gain_stmt)
        weight_gain = weight_gain_result.scalar()
        
        # Patients maintaining weight
        weight_maintain_stmt = select(func.count(Patient.id)).where(
            Patient.weight == Patient.initial_weight
        )
        weight_maintain_result = await self.session.execute(weight_maintain_stmt)
        weight_maintain = weight_maintain_result.scalar()
        
        # Average weight change
        avg_change_stmt = select(
            func.avg(Patient.weight - Patient.initial_weight)
        ).where(Patient.initial_weight.is_not(None))
        avg_change_result = await self.session.execute(avg_change_stmt)
        avg_change = avg_change_result.scalar() or 0
        
        return {
            "weight_loss": weight_loss,
            "weight_gain": weight_gain,
            "weight_maintain": weight_maintain,
            "average_weight_change": round(avg_change, 2)
        }
    
    async def get_patient_statistics(self) -> Dict[str, Any]:
        """Get comprehensive patient statistics."""
        base_stats = await self.get_statistics()
        
        return {
            **base_stats,
            "by_objective": await self.get_statistics_by_objective(),
            "by_activity_type": await self.get_statistics_by_activity_type(),
            "by_economic_level": await self.get_statistics_by_economic_level(),
            "age_distribution": await self.get_age_distribution(),
            "bmi_distribution": await self.get_bmi_distribution(),
            "weight_progress": await self.get_weight_progress_summary()
        }