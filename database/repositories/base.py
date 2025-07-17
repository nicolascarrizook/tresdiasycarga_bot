"""
Base repository class for Sistema Mayra.
"""
from typing import Optional, List, Dict, Any, Type, TypeVar, Generic, Union, Sequence
from datetime import datetime
from abc import ABC, abstractmethod

from sqlalchemy import select, update, delete, func, and_, or_, desc, asc, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import Select
from sqlalchemy.exc import IntegrityError, NoResultFound

from database.models.base import BaseModel

T = TypeVar('T', bound=BaseModel)


class PaginationResult(Generic[T]):
    """Pagination result container."""
    
    def __init__(self, items: List[T], total: int, page: int, per_page: int):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_page = page - 1 if self.has_prev else None
        self.next_page = page + 1 if self.has_next else None


class FilterOptions:
    """Filter options for repository queries."""
    
    def __init__(self):
        self.filters: List[Any] = []
        self.order_by: List[Any] = []
        self.joins: List[Any] = []
        self.options: List[Any] = []
    
    def add_filter(self, condition: Any):
        """Add filter condition."""
        self.filters.append(condition)
        return self
    
    def add_order_by(self, column: Any, direction: str = "asc"):
        """Add order by clause."""
        if direction.lower() == "desc":
            self.order_by.append(desc(column))
        else:
            self.order_by.append(asc(column))
        return self
    
    def add_join(self, target: Any):
        """Add join clause."""
        self.joins.append(target)
        return self
    
    def add_option(self, option: Any):
        """Add query option."""
        self.options.append(option)
        return self


class BaseRepository(Generic[T], ABC):
    """Base repository class with common CRUD operations."""
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
    
    async def create(self, **kwargs) -> T:
        """Create a new entity."""
        try:
            entity = self.model(**kwargs)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Integrity error creating {self.model.__name__}: {str(e)}")
    
    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        try:
            result = await self.session.get(self.model, entity_id)
            return result
        except NoResultFound:
            return None
    
    async def get_by_uuid(self, uuid: str) -> Optional[T]:
        """Get entity by UUID."""
        try:
            stmt = select(self.model).where(self.model.uuid == uuid)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except NoResultFound:
            return None
    
    async def get_all(self, active_only: bool = True) -> List[T]:
        """Get all entities."""
        stmt = select(self.model)
        
        if active_only and hasattr(self.model, 'is_active'):
            stmt = stmt.where(self.model.is_active == True)
        
        if hasattr(self.model, 'is_deleted'):
            stmt = stmt.where(self.model.is_deleted == False)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_many(self, ids: List[int]) -> List[T]:
        """Get multiple entities by IDs."""
        stmt = select(self.model).where(self.model.id.in_(ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update(self, entity_id: int, **kwargs) -> Optional[T]:
        """Update entity by ID."""
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return None
            
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            entity.updated_at = datetime.utcnow()
            
            if hasattr(entity, 'version'):
                entity.version += 1
            
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Integrity error updating {self.model.__name__}: {str(e)}")
    
    async def delete(self, entity_id: int) -> bool:
        """Delete entity by ID."""
        entity = await self.get_by_id(entity_id)
        if not entity:
            return False
        
        await self.session.delete(entity)
        await self.session.commit()
        return True
    
    async def soft_delete(self, entity_id: int) -> bool:
        """Soft delete entity by ID."""
        entity = await self.get_by_id(entity_id)
        if not entity or not hasattr(entity, 'soft_delete'):
            return False
        
        entity.soft_delete()
        await self.session.commit()
        return True
    
    async def restore(self, entity_id: int) -> bool:
        """Restore soft deleted entity."""
        entity = await self.get_by_id(entity_id)
        if not entity or not hasattr(entity, 'restore'):
            return False
        
        entity.restore()
        await self.session.commit()
        return True
    
    async def count(self, active_only: bool = True) -> int:
        """Count entities."""
        stmt = select(func.count(self.model.id))
        
        if active_only and hasattr(self.model, 'is_active'):
            stmt = stmt.where(self.model.is_active == True)
        
        if hasattr(self.model, 'is_deleted'):
            stmt = stmt.where(self.model.is_deleted == False)
        
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def exists(self, **kwargs) -> bool:
        """Check if entity exists."""
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.first() is not None
    
    async def paginate(
        self, 
        page: int = 1, 
        per_page: int = 20, 
        filter_options: Optional[FilterOptions] = None,
        active_only: bool = True
    ) -> PaginationResult[T]:
        """Paginate entities."""
        # Base query
        stmt = select(self.model)
        
        # Apply default filters
        if active_only and hasattr(self.model, 'is_active'):
            stmt = stmt.where(self.model.is_active == True)
        
        if hasattr(self.model, 'is_deleted'):
            stmt = stmt.where(self.model.is_deleted == False)
        
        # Apply filter options
        if filter_options:
            # Add joins
            for join in filter_options.joins:
                stmt = stmt.join(join)
            
            # Add filters
            if filter_options.filters:
                stmt = stmt.where(and_(*filter_options.filters))
            
            # Add ordering
            if filter_options.order_by:
                stmt = stmt.order_by(*filter_options.order_by)
            
            # Add options
            if filter_options.options:
                stmt = stmt.options(*filter_options.options)
        
        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)
        
        # Execute query
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        
        return PaginationResult(items, total, page, per_page)
    
    async def find_by(self, **kwargs) -> List[T]:
        """Find entities by attributes."""
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_one_by(self, **kwargs) -> Optional[T]:
        """Find one entity by attributes."""
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search(
        self, 
        query: str, 
        fields: List[str],
        filter_options: Optional[FilterOptions] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginationResult[T]:
        """Search entities by text in specified fields."""
        # Build search conditions
        search_conditions = []
        for field in fields:
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                search_conditions.append(column.ilike(f"%{query}%"))
        
        if not search_conditions:
            return PaginationResult([], 0, page, per_page)
        
        # Create filter options if not provided
        if filter_options is None:
            filter_options = FilterOptions()
        
        # Add search filter
        filter_options.add_filter(or_(*search_conditions))
        
        return await self.paginate(page, per_page, filter_options)
    
    async def bulk_create(self, entities_data: List[Dict[str, Any]]) -> List[T]:
        """Bulk create entities."""
        try:
            entities = [self.model(**data) for data in entities_data]
            self.session.add_all(entities)
            await self.session.commit()
            
            # Refresh all entities
            for entity in entities:
                await self.session.refresh(entity)
            
            return entities
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Integrity error bulk creating {self.model.__name__}: {str(e)}")
    
    async def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """Bulk update entities."""
        try:
            count = 0
            for update_data in updates:
                entity_id = update_data.pop('id')
                if await self.update(entity_id, **update_data):
                    count += 1
            return count
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Error bulk updating {self.model.__name__}: {str(e)}")
    
    async def bulk_delete(self, ids: List[int]) -> int:
        """Bulk delete entities."""
        try:
            stmt = delete(self.model).where(self.model.id.in_(ids))
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Error bulk deleting {self.model.__name__}: {str(e)}")
    
    async def execute_raw_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute raw SQL query."""
        try:
            result = await self.session.execute(text(query), params or {})
            return result
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Error executing raw query: {str(e)}")
    
    async def get_or_create(self, **kwargs) -> tuple[T, bool]:
        """Get or create entity."""
        entity = await self.find_one_by(**kwargs)
        if entity:
            return entity, False
        
        entity = await self.create(**kwargs)
        return entity, True
    
    async def update_or_create(self, defaults: Dict[str, Any], **kwargs) -> tuple[T, bool]:
        """Update or create entity."""
        entity = await self.find_one_by(**kwargs)
        if entity:
            for key, value in defaults.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            entity.updated_at = datetime.utcnow()
            
            if hasattr(entity, 'version'):
                entity.version += 1
            
            await self.session.commit()
            await self.session.refresh(entity)
            return entity, False
        
        create_data = {**kwargs, **defaults}
        entity = await self.create(**create_data)
        return entity, True
    
    def build_query(self, filter_options: Optional[FilterOptions] = None) -> Select:
        """Build query with filter options."""
        stmt = select(self.model)
        
        if filter_options:
            # Add joins
            for join in filter_options.joins:
                stmt = stmt.join(join)
            
            # Add filters
            if filter_options.filters:
                stmt = stmt.where(and_(*filter_options.filters))
            
            # Add ordering
            if filter_options.order_by:
                stmt = stmt.order_by(*filter_options.order_by)
            
            # Add options
            if filter_options.options:
                stmt = stmt.options(*filter_options.options)
        
        return stmt
    
    async def get_recent(self, limit: int = 10) -> List[T]:
        """Get recent entities."""
        filter_options = FilterOptions()
        if hasattr(self.model, 'created_at'):
            filter_options.add_order_by(self.model.created_at, "desc")
        
        stmt = self.build_query(filter_options).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics."""
        total = await self.count(active_only=False)
        active = await self.count(active_only=True)
        deleted = 0
        
        if hasattr(self.model, 'is_deleted'):
            stmt = select(func.count(self.model.id)).where(self.model.is_deleted == True)
            result = await self.session.execute(stmt)
            deleted = result.scalar()
        
        return {
            "total": total,
            "active": active,
            "deleted": deleted,
            "inactive": total - active - deleted
        }
    
    async def cleanup_expired(self, field: str = "expires_at") -> int:
        """Clean up expired entities."""
        if not hasattr(self.model, field):
            return 0
        
        column = getattr(self.model, field)
        stmt = delete(self.model).where(
            and_(
                column.is_not(None),
                column < datetime.utcnow()
            )
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
    
    async def batch_process(
        self, 
        batch_size: int = 100, 
        processor = None,
        filter_options: Optional[FilterOptions] = None
    ) -> int:
        """Process entities in batches."""
        if processor is None:
            return 0
        
        processed = 0
        offset = 0
        
        while True:
            stmt = self.build_query(filter_options).offset(offset).limit(batch_size)
            result = await self.session.execute(stmt)
            entities = result.scalars().all()
            
            if not entities:
                break
            
            for entity in entities:
                try:
                    await processor(entity)
                    processed += 1
                except Exception as e:
                    print(f"Error processing entity {entity.id}: {e}")
            
            offset += batch_size
            await self.session.commit()
        
        return processed
    
    async def refresh(self, entity: T) -> T:
        """Refresh entity from database."""
        await self.session.refresh(entity)
        return entity
    
    async def merge(self, entity: T) -> T:
        """Merge entity into session."""
        merged = await self.session.merge(entity)
        await self.session.commit()
        return merged