"""
Base service classes for Sistema Mayra API.
"""
import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload

from ..models.base import BaseModel
from ..schemas.base import BaseSchema, PaginatedResponse
from ..core.config import settings

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseSchema)


class BaseService(Generic[ModelType, SchemaType]):
    """Base service class with common CRUD operations."""
    
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get record by ID."""
        try:
            result = await self.db.execute(
                select(self.model).where(
                    and_(
                        self.model.id == id,
                        self.model.is_deleted == False
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by ID {id}: {str(e)}")
            return None
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """Get all records with pagination."""
        try:
            query = select(self.model)
            
            if not include_deleted:
                query = query.where(self.model.is_deleted == False)
            
            if hasattr(self.model, 'is_active'):
                query = query.where(self.model.is_active == True)
            
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting all {self.model.__name__}: {str(e)}")
            return []
    
    async def get_count(self, include_deleted: bool = False) -> int:
        """Get total count of records."""
        try:
            query = select(func.count(self.model.id))
            
            if not include_deleted:
                query = query.where(self.model.is_deleted == False)
            
            if hasattr(self.model, 'is_active'):
                query = query.where(self.model.is_active == True)
            
            result = await self.db.execute(query)
            return result.scalar()
        except Exception as e:
            logger.error(f"Error getting count for {self.model.__name__}: {str(e)}")
            return 0
    
    async def create(self, schema: SchemaType) -> Optional[ModelType]:
        """Create new record."""
        try:
            # Convert schema to dict
            if hasattr(schema, 'model_dump'):
                data = schema.model_dump(exclude_unset=True)
            else:
                data = schema
            
            # Create model instance
            instance = self.model(**data)
            
            # Add to session
            self.db.add(instance)
            await self.db.commit()
            await self.db.refresh(instance)
            
            logger.info(f"Created {self.model.__name__} with ID: {instance.id}")
            return instance
            
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            await self.db.rollback()
            return None
    
    async def update(self, id: int, schema: SchemaType) -> Optional[ModelType]:
        """Update existing record."""
        try:
            # Get existing record
            instance = await self.get_by_id(id)
            if not instance:
                return None
            
            # Convert schema to dict
            if hasattr(schema, 'model_dump'):
                data = schema.model_dump(exclude_unset=True)
            else:
                data = schema
            
            # Update fields
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            # Update version if available
            if hasattr(instance, 'update_version'):
                instance.update_version()
            
            # Commit changes
            await self.db.commit()
            await self.db.refresh(instance)
            
            logger.info(f"Updated {self.model.__name__} with ID: {id}")
            return instance
            
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__} {id}: {str(e)}")
            await self.db.rollback()
            return None
    
    async def delete(self, id: int, soft_delete: bool = True) -> bool:
        """Delete record (soft or hard)."""
        try:
            instance = await self.get_by_id(id)
            if not instance:
                return False
            
            if soft_delete and hasattr(instance, 'soft_delete'):
                instance.soft_delete()
                await self.db.commit()
                logger.info(f"Soft deleted {self.model.__name__} with ID: {id}")
            else:
                await self.db.delete(instance)
                await self.db.commit()
                logger.info(f"Hard deleted {self.model.__name__} with ID: {id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} {id}: {str(e)}")
            await self.db.rollback()
            return False
    
    async def get_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> PaginatedResponse:
        """Get paginated results."""
        try:
            # Calculate offset
            offset = (page - 1) * limit
            
            # Build query
            query = select(self.model)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.where(getattr(self.model, key) == value)
            
            # Apply soft delete filter
            query = query.where(self.model.is_deleted == False)
            
            # Apply active filter if available
            if hasattr(self.model, 'is_active'):
                query = query.where(self.model.is_active == True)
            
            # Get total count
            count_query = select(func.count(self.model.id))
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        count_query = count_query.where(getattr(self.model, key) == value)
            
            count_query = count_query.where(self.model.is_deleted == False)
            if hasattr(self.model, 'is_active'):
                count_query = count_query.where(self.model.is_active == True)
            
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                if order_desc:
                    query = query.order_by(getattr(self.model, order_by).desc())
                else:
                    query = query.order_by(getattr(self.model, order_by))
            else:
                query = query.order_by(self.model.created_at.desc())
            
            # Apply pagination
            query = query.offset(offset).limit(limit)
            
            # Execute query
            result = await self.db.execute(query)
            items = result.scalars().all()
            
            # Calculate pagination info
            total_pages = (total + limit - 1) // limit
            has_next = page < total_pages
            has_previous = page > 1
            
            return PaginatedResponse(
                items=items,
                total=total,
                page=page,
                limit=limit,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except Exception as e:
            logger.error(f"Error getting paginated {self.model.__name__}: {str(e)}")
            return PaginatedResponse(
                items=[],
                total=0,
                page=page,
                limit=limit,
                total_pages=0,
                has_next=False,
                has_previous=False
            )
    
    async def search(
        self,
        query: str,
        fields: List[str],
        page: int = 1,
        limit: int = 20
    ) -> PaginatedResponse:
        """Search records by text query."""
        try:
            # Build search conditions
            conditions = []
            for field in fields:
                if hasattr(self.model, field):
                    conditions.append(
                        getattr(self.model, field).ilike(f"%{query}%")
                    )
            
            if not conditions:
                return PaginatedResponse(
                    items=[],
                    total=0,
                    page=page,
                    limit=limit,
                    total_pages=0,
                    has_next=False,
                    has_previous=False
                )
            
            # Build query
            search_query = select(self.model).where(
                and_(
                    or_(*conditions),
                    self.model.is_deleted == False
                )
            )
            
            if hasattr(self.model, 'is_active'):
                search_query = search_query.where(self.model.is_active == True)
            
            # Get total count
            count_query = select(func.count(self.model.id)).where(
                and_(
                    or_(*conditions),
                    self.model.is_deleted == False
                )
            )
            
            if hasattr(self.model, 'is_active'):
                count_query = count_query.where(self.model.is_active == True)
            
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            offset = (page - 1) * limit
            search_query = search_query.offset(offset).limit(limit)
            
            # Execute search
            result = await self.db.execute(search_query)
            items = result.scalars().all()
            
            # Calculate pagination info
            total_pages = (total + limit - 1) // limit
            has_next = page < total_pages
            has_previous = page > 1
            
            return PaginatedResponse(
                items=items,
                total=total,
                page=page,
                limit=limit,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except Exception as e:
            logger.error(f"Error searching {self.model.__name__}: {str(e)}")
            return PaginatedResponse(
                items=[],
                total=0,
                page=page,
                limit=limit,
                total_pages=0,
                has_next=False,
                has_previous=False
            )
    
    async def bulk_create(self, schemas: List[SchemaType]) -> List[ModelType]:
        """Create multiple records in bulk."""
        try:
            instances = []
            for schema in schemas:
                if hasattr(schema, 'model_dump'):
                    data = schema.model_dump(exclude_unset=True)
                else:
                    data = schema
                
                instance = self.model(**data)
                instances.append(instance)
            
            # Add all instances
            self.db.add_all(instances)
            await self.db.commit()
            
            # Refresh all instances
            for instance in instances:
                await self.db.refresh(instance)
            
            logger.info(f"Bulk created {len(instances)} {self.model.__name__} records")
            return instances
            
        except Exception as e:
            logger.error(f"Error bulk creating {self.model.__name__}: {str(e)}")
            await self.db.rollback()
            return []
    
    async def bulk_update(
        self, 
        ids: List[int], 
        update_data: Dict[str, Any]
    ) -> int:
        """Update multiple records in bulk."""
        try:
            query = update(self.model).where(
                and_(
                    self.model.id.in_(ids),
                    self.model.is_deleted == False
                )
            ).values(**update_data)
            
            result = await self.db.execute(query)
            await self.db.commit()
            
            updated_count = result.rowcount
            logger.info(f"Bulk updated {updated_count} {self.model.__name__} records")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error bulk updating {self.model.__name__}: {str(e)}")
            await self.db.rollback()
            return 0
    
    async def bulk_delete(self, ids: List[int], soft_delete: bool = True) -> int:
        """Delete multiple records in bulk."""
        try:
            if soft_delete:
                query = update(self.model).where(
                    and_(
                        self.model.id.in_(ids),
                        self.model.is_deleted == False
                    )
                ).values(is_deleted=True, deleted_at=func.now())
            else:
                query = delete(self.model).where(self.model.id.in_(ids))
            
            result = await self.db.execute(query)
            await self.db.commit()
            
            deleted_count = result.rowcount
            delete_type = "soft" if soft_delete else "hard"
            logger.info(f"Bulk {delete_type} deleted {deleted_count} {self.model.__name__} records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error bulk deleting {self.model.__name__}: {str(e)}")
            await self.db.rollback()
            return 0
    
    async def exists(self, id: int) -> bool:
        """Check if record exists."""
        try:
            result = await self.db.execute(
                select(self.model.id).where(
                    and_(
                        self.model.id == id,
                        self.model.is_deleted == False
                    )
                )
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} {id}: {str(e)}")
            return False
    
    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Get record by specific field value."""
        try:
            if not hasattr(self.model, field):
                return None
            
            result = await self.db.execute(
                select(self.model).where(
                    and_(
                        getattr(self.model, field) == value,
                        self.model.is_deleted == False
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by {field}: {str(e)}")
            return None
    
    async def get_many_by_field(self, field: str, values: List[Any]) -> List[ModelType]:
        """Get multiple records by field values."""
        try:
            if not hasattr(self.model, field):
                return []
            
            result = await self.db.execute(
                select(self.model).where(
                    and_(
                        getattr(self.model, field).in_(values),
                        self.model.is_deleted == False
                    )
                )
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by {field}: {str(e)}")
            return []