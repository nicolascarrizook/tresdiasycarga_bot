"""
Plan repository for Sistema Mayra.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.plan import Plan, PlanTypeEnum, PlanStatusEnum
from database.models.patient import Patient
from .base import BaseRepository, FilterOptions


class PlanRepository(BaseRepository[Plan]):
    """Plan repository with specialized methods."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Plan)
    
    async def get_by_patient(self, patient_id: int) -> List[Plan]:
        """Get plans by patient."""
        filter_options = FilterOptions()
        filter_options.add_filter(Plan.patient_id == patient_id)
        filter_options.add_order_by(Plan.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_active_plan_by_patient(self, patient_id: int) -> Optional[Plan]:
        """Get active plan by patient."""
        return await self.find_one_by(patient_id=patient_id, is_active=True)
    
    async def get_by_type(self, plan_type: PlanTypeEnum) -> List[Plan]:
        """Get plans by type."""
        return await self.find_by(plan_type=plan_type)
    
    async def get_by_status(self, status: PlanStatusEnum) -> List[Plan]:
        """Get plans by status."""
        return await self.find_by(status=status)
    
    async def get_with_patient(self, plan_id: int) -> Optional[Plan]:
        """Get plan with patient."""
        stmt = select(Plan).where(Plan.id == plan_id).options(
            selectinload(Plan.patient)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_conversations(self, plan_id: int) -> Optional[Plan]:
        """Get plan with conversations."""
        stmt = select(Plan).where(Plan.id == plan_id).options(
            selectinload(Plan.conversations)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_plan(self, patient_id: int, plan_type: PlanTypeEnum, 
                         name: str, plan_data: Dict[str, Any], **kwargs) -> Plan:
        """Create new plan."""
        plan = await self.create(
            patient_id=patient_id,
            plan_type=plan_type,
            name=name,
            plan_data=plan_data,
            status=PlanStatusEnum.DRAFT,
            **kwargs
        )
        
        # Calculate nutrition totals
        plan.calculate_total_nutrition()
        await self.session.commit()
        await self.session.refresh(plan)
        
        return plan
    
    async def activate_plan(self, plan_id: int, start_date: Optional[date] = None,
                          end_date: Optional[date] = None) -> bool:
        """Activate plan."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return False
        
        plan.activate(start_date, end_date)
        await self.session.commit()
        return True
    
    async def deactivate_plan(self, plan_id: int) -> bool:
        """Deactivate plan."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return False
        
        plan.deactivate()
        await self.session.commit()
        return True
    
    async def pause_plan(self, plan_id: int) -> bool:
        """Pause plan."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return False
        
        plan.pause()
        await self.session.commit()
        return True
    
    async def resume_plan(self, plan_id: int) -> bool:
        """Resume plan."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return False
        
        plan.resume()
        await self.session.commit()
        return True
    
    async def cancel_plan(self, plan_id: int) -> bool:
        """Cancel plan."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return False
        
        plan.cancel()
        await self.session.commit()
        return True
    
    async def update_adherence_score(self, plan_id: int, score: float) -> bool:
        """Update adherence score."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return False
        
        plan.update_adherence_score(score)
        await self.session.commit()
        return True
    
    async def add_patient_feedback(self, plan_id: int, feedback: str) -> bool:
        """Add patient feedback."""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return False
        
        plan.add_patient_feedback(feedback)
        await self.session.commit()
        return True
    
    async def get_current_plans(self) -> List[Plan]:
        """Get current active plans."""
        today = date.today()
        filter_options = FilterOptions()
        filter_options.add_filter(Plan.is_active == True)
        filter_options.add_filter(Plan.status == PlanStatusEnum.ACTIVE)
        filter_options.add_filter(
            or_(
                Plan.start_date.is_(None),
                Plan.start_date <= today
            )
        )
        filter_options.add_filter(
            or_(
                Plan.end_date.is_(None),
                Plan.end_date >= today
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_expiring_plans(self, days: int = 7) -> List[Plan]:
        """Get plans expiring within specified days."""
        future_date = date.today() + timedelta(days=days)
        filter_options = FilterOptions()
        filter_options.add_filter(Plan.is_active == True)
        filter_options.add_filter(Plan.status == PlanStatusEnum.ACTIVE)
        filter_options.add_filter(
            and_(
                Plan.end_date.is_not(None),
                Plan.end_date <= future_date,
                Plan.end_date >= date.today()
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_expired_plans(self) -> List[Plan]:
        """Get expired plans."""
        today = date.today()
        filter_options = FilterOptions()
        filter_options.add_filter(Plan.status == PlanStatusEnum.ACTIVE)
        filter_options.add_filter(
            and_(
                Plan.end_date.is_not(None),
                Plan.end_date < today
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def cleanup_expired_plans(self) -> int:
        """Clean up expired plans by marking them as completed."""
        expired_plans = await self.get_expired_plans()
        
        for plan in expired_plans:
            plan.deactivate()
        
        await self.session.commit()
        return len(expired_plans)
    
    async def get_by_calorie_range(self, min_calories: float, max_calories: float) -> List[Plan]:
        """Get plans by calorie range."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                Plan.calories_total >= min_calories,
                Plan.calories_total <= max_calories
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_ai_model(self, ai_model: str) -> List[Plan]:
        """Get plans by AI model used."""
        return await self.find_by(ai_model_used=ai_model)
    
    async def get_recent_plans(self, days: int = 30) -> List[Plan]:
        """Get recent plans."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            Plan.created_at >= datetime.utcnow() - timedelta(days=days)
        )
        filter_options.add_order_by(Plan.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def search_plans(self, query: str, filters: Optional[Dict[str, Any]] = None,
                         page: int = 1, per_page: int = 20):
        """Search plans."""
        filter_options = FilterOptions()
        
        # Add text search
        search_conditions = []
        search_conditions.append(Plan.name.ilike(f"%{query}%"))
        search_conditions.append(Plan.description.ilike(f"%{query}%"))
        filter_options.add_filter(or_(*search_conditions))
        
        # Add filters
        if filters:
            if "patient_id" in filters:
                filter_options.add_filter(Plan.patient_id == filters["patient_id"])
            
            if "plan_type" in filters:
                filter_options.add_filter(Plan.plan_type == filters["plan_type"])
            
            if "status" in filters:
                filter_options.add_filter(Plan.status == filters["status"])
            
            if "is_active" in filters:
                filter_options.add_filter(Plan.is_active == filters["is_active"])
        
        # Order by creation date
        filter_options.add_order_by(Plan.created_at, "desc")
        
        return await self.paginate(page, per_page, filter_options)
    
    async def get_statistics_by_type(self) -> Dict[str, int]:
        """Get statistics by plan type."""
        stmt = select(Plan.plan_type, func.count(Plan.id)).group_by(Plan.plan_type)
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_statistics_by_status(self) -> Dict[str, int]:
        """Get statistics by plan status."""
        stmt = select(Plan.status, func.count(Plan.id)).group_by(Plan.status)
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_nutrition_statistics(self) -> Dict[str, Any]:
        """Get nutrition statistics."""
        # Average nutrition values
        avg_stmt = select(
            func.avg(Plan.calories_total).label("avg_calories"),
            func.avg(Plan.protein_total).label("avg_protein"),
            func.avg(Plan.carbs_total).label("avg_carbs"),
            func.avg(Plan.fat_total).label("avg_fat")
        ).where(Plan.calories_total.is_not(None))
        
        avg_result = await self.session.execute(avg_stmt)
        avg_data = avg_result.fetchone()
        
        return {
            "avg_calories": round(avg_data.avg_calories or 0, 2),
            "avg_protein": round(avg_data.avg_protein or 0, 2),
            "avg_carbs": round(avg_data.avg_carbs or 0, 2),
            "avg_fat": round(avg_data.avg_fat or 0, 2)
        }
    
    async def get_adherence_statistics(self) -> Dict[str, Any]:
        """Get adherence statistics."""
        # Average adherence score
        avg_stmt = select(func.avg(Plan.adherence_score)).where(
            Plan.adherence_score.is_not(None)
        )
        avg_result = await self.session.execute(avg_stmt)
        avg_adherence = avg_result.scalar() or 0
        
        # Count by adherence ranges
        high_adherence_stmt = select(func.count(Plan.id)).where(
            Plan.adherence_score >= 80
        )
        medium_adherence_stmt = select(func.count(Plan.id)).where(
            and_(Plan.adherence_score >= 60, Plan.adherence_score < 80)
        )
        low_adherence_stmt = select(func.count(Plan.id)).where(
            Plan.adherence_score < 60
        )
        
        high_result = await self.session.execute(high_adherence_stmt)
        medium_result = await self.session.execute(medium_adherence_stmt)
        low_result = await self.session.execute(low_adherence_stmt)
        
        return {
            "average_adherence": round(avg_adherence, 2),
            "high_adherence": high_result.scalar(),
            "medium_adherence": medium_result.scalar(),
            "low_adherence": low_result.scalar()
        }
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """Get plan generation statistics."""
        # Average generation time
        avg_time_stmt = select(func.avg(Plan.generation_time)).where(
            Plan.generation_time.is_not(None)
        )
        avg_time_result = await self.session.execute(avg_time_stmt)
        avg_generation_time = avg_time_result.scalar() or 0
        
        # Plans with PDF
        pdf_stmt = select(func.count(Plan.id)).where(
            Plan.pdf_path.is_not(None)
        )
        pdf_result = await self.session.execute(pdf_stmt)
        with_pdf = pdf_result.scalar()
        
        # AI model usage
        ai_model_stmt = select(
            Plan.ai_model_used,
            func.count(Plan.id)
        ).where(
            Plan.ai_model_used.is_not(None)
        ).group_by(Plan.ai_model_used)
        
        ai_model_result = await self.session.execute(ai_model_stmt)
        ai_models = dict(ai_model_result.fetchall())
        
        return {
            "average_generation_time": round(avg_generation_time, 2),
            "plans_with_pdf": with_pdf,
            "ai_models_used": ai_models
        }
    
    async def get_plan_statistics(self) -> Dict[str, Any]:
        """Get comprehensive plan statistics."""
        base_stats = await self.get_statistics()
        
        return {
            **base_stats,
            "by_type": await self.get_statistics_by_type(),
            "by_status": await self.get_statistics_by_status(),
            "nutrition": await self.get_nutrition_statistics(),
            "adherence": await self.get_adherence_statistics(),
            "generation": await self.get_generation_statistics()
        }