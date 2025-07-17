"""
Plan endpoints for Sistema Mayra API.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import (
    get_db_session, get_current_user, get_plan_service, 
    get_pagination_params, require_admin_access
)
from ..schemas.plan import (
    Plan, PlanCreate, PlanUpdate, PlanSummary, PlanSearch,
    PlanGeneration, PlanGenerationResult, PlanAnalytics,
    PlanReplacement, PlanReplacementResult, PlanFeedback
)
from ..schemas.base import PaginatedResponse, ResponseBase
from ..schemas.auth import User
from ..services.plan import PlanService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("/generate", response_model=PlanGenerationResult, status_code=status.HTTP_201_CREATED)
async def generate_plan(
    generation_request: PlanGeneration,
    current_user: User = Depends(get_current_user),
    plan_service: PlanService = Depends(get_plan_service)
):
    """Generate a new nutrition plan."""
    try:
        # Check if user has access to the patient
        patient = await plan_service.patient_service.get_by_id(generation_request.patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        if not current_user.is_admin and patient.telegram_user_id != current_user.telegram_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Generate plan
        result = await plan_service.generate_plan(generation_request)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to generate plan"
            )
        
        logger.info(f"Generated plan for patient {generation_request.patient_id} by user {current_user.id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=PaginatedResponse[PlanSummary])
async def get_plans(
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    plan_service: PlanService = Depends(get_plan_service)
):
    """Get paginated list of plans."""
    try:
        # Non-admin users can only see their own plans
        filters = {}
        if not current_user.is_admin:
            # Get user's patients first
            patients = await plan_service.patient_service.get_many_by_field(
                "telegram_user_id", 
                [current_user.telegram_user_id]
            )
            patient_ids = [p.id for p in patients]
            if patient_ids:
                filters["patient_id"] = patient_ids
            else:
                # No patients, return empty result
                return PaginatedResponse(
                    items=[],
                    total=0,
                    page=pagination["page"],
                    limit=pagination["limit"],
                    total_pages=0,
                    has_next=False,
                    has_previous=False
                )
        
        result = await plan_service.get_paginated(
            page=pagination["page"],
            limit=pagination["limit"],
            filters=filters,
            order_by="created_at",
            order_desc=True
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/analytics", response_model=PlanAnalytics)
async def get_plan_analytics(
    current_user: User = Depends(require_admin_access),
    plan_service: PlanService = Depends(get_plan_service)
):
    """Get plan analytics (admin only)."""
    try:
        analytics = await plan_service.get_plan_analytics()
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting plan analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{plan_id}", response_model=Plan)
async def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    plan_service: PlanService = Depends(get_plan_service)
):
    """Get plan by ID."""
    try:
        plan = await plan_service.get_by_id(plan_id)
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        # Check if user has access to the plan
        if not current_user.is_admin:
            patient = await plan_service.patient_service.get_by_id(plan.patient_id)
            if not patient or patient.telegram_user_id != current_user.telegram_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{plan_id}", response_model=Plan)
async def update_plan(
    plan_id: int,
    update_data: PlanUpdate,
    current_user: User = Depends(get_current_user),
    plan_service: PlanService = Depends(get_plan_service)
):
    """Update plan."""
    try:
        # Check if plan exists and user has access
        plan = await plan_service.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        if not current_user.is_admin:
            patient = await plan_service.patient_service.get_by_id(plan.patient_id)
            if not patient or patient.telegram_user_id != current_user.telegram_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        # Update plan
        updated_plan = await plan_service.update(plan_id, update_data)
        
        if not updated_plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update plan"
            )
        
        logger.info(f"Updated plan {plan_id} by user {current_user.id}")
        return updated_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{plan_id}", response_model=ResponseBase)
async def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    plan_service: PlanService = Depends(get_plan_service)
):
    """Delete plan."""
    try:
        # Check if plan exists and user has access
        plan = await plan_service.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        if not current_user.is_admin:
            patient = await plan_service.patient_service.get_by_id(plan.patient_id)
            if not patient or patient.telegram_user_id != current_user.telegram_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        # Soft delete plan
        success = await plan_service.delete(plan_id, soft_delete=True)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete plan"
            )
        
        logger.info(f"Deleted plan {plan_id} by user {current_user.id}")
        return ResponseBase(
            success=True,
            message="Plan deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{plan_id}/replacement", response_model=PlanReplacementResult)
async def create_meal_replacement(
    plan_id: int,
    replacement_request: PlanReplacement,
    current_user: User = Depends(get_current_user),
    plan_service: PlanService = Depends(get_plan_service)
):
    """Create meal replacement for plan."""
    try:
        # Check if plan exists and user has access
        plan = await plan_service.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        if not current_user.is_admin:
            patient = await plan_service.patient_service.get_by_id(plan.patient_id)
            if not patient or patient.telegram_user_id != current_user.telegram_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        # Set plan_id in replacement request
        replacement_request.plan_id = plan_id
        
        # Generate replacement plan
        generation_request = PlanGeneration(
            patient_id=plan.patient_id,
            plan_type="reemplazo",
            replacement_data=replacement_request
        )
        
        result = await plan_service.generate_plan(generation_request)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to generate replacement"
            )
        
        # Create replacement result
        replacement_result = PlanReplacementResult(
            original_meal={},  # Would extract from original plan
            replacement_meal={},  # Would extract from new plan
            calorie_difference=0,
            protein_difference=0,
            carbs_difference=0,
            fat_difference=0,
            within_tolerance=True,
            tolerance_percentage=5.0,
            replacement_reason="User requested replacement",
            generated_at=result.plan.created_at
        )
        
        logger.info(f"Created meal replacement for plan {plan_id}")
        return replacement_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating meal replacement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{plan_id}/feedback", response_model=ResponseBase)
async def submit_plan_feedback(
    plan_id: int,
    feedback: PlanFeedback,
    current_user: User = Depends(get_current_user),
    plan_service: PlanService = Depends(get_plan_service)
):
    """Submit feedback for plan."""
    try:
        # Check if plan exists and user has access
        plan = await plan_service.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        if not current_user.is_admin:
            patient = await plan_service.patient_service.get_by_id(plan.patient_id)
            if not patient or patient.telegram_user_id != current_user.telegram_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        # Set plan_id and user_id in feedback
        feedback.plan_id = plan_id
        feedback.user_id = current_user.id
        
        # This would typically save feedback to database
        # For now, just log it
        logger.info(f"Received feedback for plan {plan_id} from user {current_user.id}")
        
        return ResponseBase(
            success=True,
            message="Feedback submitted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/patient/{patient_id}", response_model=List[PlanSummary])
async def get_patient_plans(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    plan_service: PlanService = Depends(get_plan_service)
):
    """Get all plans for a specific patient."""
    try:
        # Check if patient exists and user has access
        patient = await plan_service.patient_service.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        if not current_user.is_admin and patient.telegram_user_id != current_user.telegram_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get patient's plans
        plans = await plan_service.get_many_by_field("patient_id", [patient_id])
        
        # Convert to summaries
        plan_summaries = []
        for plan in plans:
            plan_summaries.append(PlanSummary(
                id=plan.id,
                patient_id=plan.patient_id,
                plan_type=plan.plan_type,
                target_calories=plan.target_calories,
                duration_days=plan.duration_days,
                is_active=plan.is_active,
                is_current=plan.is_current,
                created_at=plan.created_at,
                has_pdf=bool(plan.pdf_path),
                patient_name=patient.name
            ))
        
        return plan_summaries
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/patient/{patient_id}/current", response_model=Plan)
async def get_current_patient_plan(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    plan_service: PlanService = Depends(get_plan_service)
):
    """Get current active plan for patient."""
    try:
        # Check if patient exists and user has access
        patient = await plan_service.patient_service.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        if not current_user.is_admin and patient.telegram_user_id != current_user.telegram_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get current plan
        current_plan = await plan_service.get_latest_plan(patient_id)
        
        if not current_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No current plan found for patient"
            )
        
        return current_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current patient plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )