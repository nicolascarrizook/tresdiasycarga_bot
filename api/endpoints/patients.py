"""
Patient endpoints for Sistema Mayra API.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import (
    get_db_session, get_current_user, get_patient_service, 
    get_pagination_params, require_admin_access
)
from ..schemas.patient import (
    Patient, PatientCreate, PatientUpdate, PatientSummary,
    PatientSearch, PatientStats, PatientAnalytics, WeightEntry
)
from ..schemas.base import PaginatedResponse, ResponseBase
from ..schemas.auth import User
from ..services.patient import PatientService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("/", response_model=Patient, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Create a new patient."""
    try:
        # Ensure patient belongs to current user
        if patient_data.telegram_user_id != current_user.telegram_user_id:
            # Only allow if user is admin
            if not current_user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Can only create patients for your own account"
                )
        
        patient = await patient_service.create_patient(patient_data)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create patient"
            )
        
        logger.info(f"Created patient {patient.id} for user {current_user.id}")
        return patient
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=PaginatedResponse[PatientSummary])
async def get_patients(
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Get paginated list of patients."""
    try:
        # Non-admin users can only see their own patients
        filters = {}
        if not current_user.is_admin:
            filters["telegram_user_id"] = current_user.telegram_user_id
        
        result = await patient_service.get_paginated(
            page=pagination["page"],
            limit=pagination["limit"],
            filters=filters,
            order_by="created_at",
            order_desc=True
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting patients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/search", response_model=PaginatedResponse[PatientSummary])
async def search_patients(
    q: str = Query(..., description="Search query"),
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Search patients."""
    try:
        # Build filters
        filters = {}
        if not current_user.is_admin:
            filters["telegram_user_id"] = current_user.telegram_user_id
        
        result = await patient_service.search_patients(
            query=q,
            filters=filters,
            page=pagination["page"],
            limit=pagination["limit"]
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching patients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=List[PatientSummary])
async def get_my_patients(
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Get current user's patients."""
    try:
        patients = await patient_service.get_many_by_field(
            "telegram_user_id", 
            [current_user.telegram_user_id]
        )
        
        return patients
        
    except Exception as e:
        logger.error(f"Error getting user patients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/analytics", response_model=PatientAnalytics)
async def get_patient_analytics(
    current_user: User = Depends(require_admin_access),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Get patient analytics (admin only)."""
    try:
        analytics = await patient_service.get_patient_analytics()
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting patient analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{patient_id}", response_model=Patient)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Get patient by ID."""
    try:
        patient = await patient_service.get_by_id(patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check ownership
        if not current_user.is_admin and patient.telegram_user_id != current_user.telegram_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return patient
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{patient_id}", response_model=Patient)
async def update_patient(
    patient_id: int,
    update_data: PatientUpdate,
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Update patient."""
    try:
        # Check if patient exists and user has access
        patient = await patient_service.get_by_id(patient_id)
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
        
        # Update patient
        updated_patient = await patient_service.update_patient(patient_id, update_data)
        
        if not updated_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update patient"
            )
        
        logger.info(f"Updated patient {patient_id} by user {current_user.id}")
        return updated_patient
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{patient_id}", response_model=ResponseBase)
async def delete_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Delete patient."""
    try:
        # Check if patient exists and user has access
        patient = await patient_service.get_by_id(patient_id)
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
        
        # Soft delete patient
        success = await patient_service.delete(patient_id, soft_delete=True)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete patient"
            )
        
        logger.info(f"Deleted patient {patient_id} by user {current_user.id}")
        return ResponseBase(
            success=True,
            message="Patient deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{patient_id}/stats", response_model=PatientStats)
async def get_patient_stats(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Get patient statistics."""
    try:
        # Check if patient exists and user has access
        patient = await patient_service.get_by_id(patient_id)
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
        
        stats = await patient_service.get_patient_stats(patient_id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient stats not found"
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient stats {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{patient_id}/weight", response_model=ResponseBase)
async def add_weight_entry(
    patient_id: int,
    weight_entry: WeightEntry,
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Add weight entry for patient."""
    try:
        # Check if patient exists and user has access
        patient = await patient_service.get_by_id(patient_id)
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
        
        success = await patient_service.add_weight_entry(
            patient_id=patient_id,
            weight=weight_entry.weight,
            notes=weight_entry.notes
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add weight entry"
            )
        
        logger.info(f"Added weight entry for patient {patient_id}")
        return ResponseBase(
            success=True,
            message="Weight entry added successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding weight entry for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{patient_id}/weight-history", response_model=List[dict])
async def get_weight_history(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Get patient weight history."""
    try:
        # Check if patient exists and user has access
        patient = await patient_service.get_by_id(patient_id)
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
        
        history = await patient_service.get_weight_history(patient_id)
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weight history for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{patient_id}/recommendations", response_model=List[dict])
async def get_patient_recommendations(
    patient_id: int,
    recommendation_type: str = Query("general", description="Type of recommendations"),
    current_user: User = Depends(get_current_user),
    patient_service: PatientService = Depends(get_patient_service)
):
    """Get personalized recommendations for patient."""
    try:
        # Check if patient exists and user has access
        patient = await patient_service.get_by_id(patient_id)
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
        
        recommendations = await patient_service.get_patient_recommendations(
            patient_id=patient_id,
            recommendation_type=recommendation_type
        )
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )