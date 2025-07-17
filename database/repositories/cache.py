"""
Cache repository for Sistema Mayra.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cache import CacheEntry, CacheTypeEnum
from .base import BaseRepository, FilterOptions


class CacheRepository(BaseRepository[CacheEntry]):
    """Cache repository with specialized methods."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, CacheEntry)
    
    async def get_by_key(self, cache_key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        return await self.find_one_by(cache_key=cache_key)
    
    async def get_by_type(self, cache_type: CacheTypeEnum) -> List[CacheEntry]:
        """Get cache entries by type."""
        return await self.find_by(cache_type=cache_type)
    
    async def get_valid_entry(self, cache_key: str) -> Optional[CacheEntry]:
        """Get valid (non-expired) cache entry."""
        entry = await self.get_by_key(cache_key)
        if entry and entry.is_valid:
            return entry
        return None
    
    async def set_cache(self, cache_key: str, cache_type: CacheTypeEnum, 
                       data: Dict[str, Any], ttl_seconds: Optional[int] = None,
                       tags: Optional[List[str]] = None, compress: bool = False) -> CacheEntry:
        """Set cache entry."""
        # Delete existing entry if it exists
        existing = await self.get_by_key(cache_key)
        if existing:
            await self.delete(existing.id)
        
        # Create new entry
        entry = await self.create(
            cache_key=cache_key,
            cache_type=cache_type,
            data=data,
            data_size=len(str(data)),
            tags=tags
        )
        
        if ttl_seconds:
            entry.set_ttl(ttl_seconds)
        
        if compress:
            entry.compress_data()
        
        await self.session.commit()
        await self.session.refresh(entry)
        
        return entry
    
    async def get_cache_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cache data and update access stats."""
        entry = await self.get_by_key(cache_key)
        if not entry:
            return None
        
        # Check if expired
        if entry.is_expired:
            await self.delete(entry.id)
            return None
        
        # Update access stats
        entry.access_count += 1
        entry.last_accessed_at = datetime.utcnow()
        
        # Refresh expiration if TTL is set
        if entry.ttl_seconds:
            entry.refresh_expiration()
        
        await self.session.commit()
        
        return entry.get_data()
    
    async def delete_by_key(self, cache_key: str) -> bool:
        """Delete cache entry by key."""
        entry = await self.get_by_key(cache_key)
        if not entry:
            return False
        
        await self.delete(entry.id)
        return True
    
    async def invalidate_by_keys(self, cache_keys: List[str]) -> int:
        """Invalidate multiple cache entries by keys."""
        count = 0
        for cache_key in cache_keys:
            if await self.delete_by_key(cache_key):
                count += 1
        return count
    
    async def invalidate_by_type(self, cache_type: CacheTypeEnum) -> int:
        """Invalidate all cache entries of a specific type."""
        entries = await self.get_by_type(cache_type)
        
        for entry in entries:
            await self.delete(entry.id)
        
        return len(entries)
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags."""
        filter_options = FilterOptions()
        
        # Build filter for entries that contain any of the tags
        tag_conditions = []
        for tag in tags:
            tag_conditions.append(CacheEntry.tags.contains([tag]))
        
        filter_options.add_filter(or_(*tag_conditions))
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        entries = result.scalars().all()
        
        for entry in entries:
            await self.delete(entry.id)
        
        return len(entries)
    
    async def get_expired_entries(self) -> List[CacheEntry]:
        """Get expired cache entries."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                CacheEntry.expires_at.is_not(None),
                CacheEntry.expires_at <= datetime.utcnow()
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def cleanup_expired_entries(self) -> int:
        """Clean up expired cache entries."""
        expired_entries = await self.get_expired_entries()
        
        for entry in expired_entries:
            await self.delete(entry.id)
        
        return len(expired_entries)
    
    async def get_large_entries(self, min_size: int) -> List[CacheEntry]:
        """Get cache entries larger than specified size."""
        filter_options = FilterOptions()
        filter_options.add_filter(CacheEntry.data_size >= min_size)
        filter_options.add_order_by(CacheEntry.data_size, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_least_accessed_entries(self, limit: int = 10) -> List[CacheEntry]:
        """Get least accessed cache entries."""
        filter_options = FilterOptions()
        filter_options.add_order_by(CacheEntry.access_count, "asc")
        filter_options.add_order_by(CacheEntry.last_accessed_at, "asc")
        
        stmt = self.build_query(filter_options).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_most_accessed_entries(self, limit: int = 10) -> List[CacheEntry]:
        """Get most accessed cache entries."""
        filter_options = FilterOptions()
        filter_options.add_order_by(CacheEntry.access_count, "desc")
        filter_options.add_order_by(CacheEntry.last_accessed_at, "desc")
        
        stmt = self.build_query(filter_options).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_unused_entries(self, days: int = 7) -> List[CacheEntry]:
        """Get unused cache entries (not accessed in specified days)."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        filter_options = FilterOptions()
        filter_options.add_filter(
            or_(
                CacheEntry.last_accessed_at < cutoff_date,
                CacheEntry.last_accessed_at.is_(None)
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def cleanup_unused_entries(self, days: int = 30) -> int:
        """Clean up unused cache entries."""
        unused_entries = await self.get_unused_entries(days)
        
        for entry in unused_entries:
            await self.delete(entry.id)
        
        return len(unused_entries)
    
    async def get_entries_by_size_range(self, min_size: int, max_size: int) -> List[CacheEntry]:
        """Get cache entries by size range."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                CacheEntry.data_size >= min_size,
                CacheEntry.data_size <= max_size
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_compressed_entries(self) -> List[CacheEntry]:
        """Get compressed cache entries."""
        return await self.find_by(is_compressed=True)
    
    async def get_uncompressed_entries(self) -> List[CacheEntry]:
        """Get uncompressed cache entries."""
        return await self.find_by(is_compressed=False)
    
    async def compress_large_entries(self, min_size: int = 1000) -> int:
        """Compress large cache entries."""
        large_entries = await self.get_large_entries(min_size)
        compressed_count = 0
        
        for entry in large_entries:
            if not entry.is_compressed:
                entry.compress_data()
                compressed_count += 1
        
        if compressed_count > 0:
            await self.session.commit()
        
        return compressed_count
    
    async def extend_ttl(self, cache_key: str, seconds: int) -> bool:
        """Extend TTL for cache entry."""
        entry = await self.get_by_key(cache_key)
        if not entry:
            return False
        
        entry.extend_ttl(seconds)
        await self.session.commit()
        return True
    
    async def refresh_expiration(self, cache_key: str) -> bool:
        """Refresh expiration for cache entry."""
        entry = await self.get_by_key(cache_key)
        if not entry:
            return False
        
        entry.refresh_expiration()
        await self.session.commit()
        return True
    
    async def add_tag_to_entry(self, cache_key: str, tag: str) -> bool:
        """Add tag to cache entry."""
        entry = await self.get_by_key(cache_key)
        if not entry:
            return False
        
        entry.add_tag(tag)
        await self.session.commit()
        return True
    
    async def remove_tag_from_entry(self, cache_key: str, tag: str) -> bool:
        """Remove tag from cache entry."""
        entry = await self.get_by_key(cache_key)
        if not entry:
            return False
        
        entry.remove_tag(tag)
        await self.session.commit()
        return True
    
    async def search_cache_entries(self, query: str, cache_type: Optional[CacheTypeEnum] = None,
                                 page: int = 1, per_page: int = 20):
        """Search cache entries."""
        filter_options = FilterOptions()
        
        # Add text search
        search_conditions = []
        search_conditions.append(CacheEntry.cache_key.ilike(f"%{query}%"))
        search_conditions.append(CacheEntry.description.ilike(f"%{query}%"))
        
        filter_options.add_filter(or_(*search_conditions))
        
        # Add type filter
        if cache_type:
            filter_options.add_filter(CacheEntry.cache_type == cache_type)
        
        # Order by access count
        filter_options.add_order_by(CacheEntry.access_count, "desc")
        
        return await self.paginate(page, per_page, filter_options)
    
    async def get_statistics_by_type(self) -> Dict[str, int]:
        """Get statistics by cache type."""
        stmt = select(
            CacheEntry.cache_type,
            func.count(CacheEntry.id)
        ).group_by(CacheEntry.cache_type)
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_size_statistics(self) -> Dict[str, Any]:
        """Get size statistics."""
        # Total size
        total_size_stmt = select(func.sum(CacheEntry.data_size))
        total_size_result = await self.session.execute(total_size_stmt)
        total_size = total_size_result.scalar() or 0
        
        # Average size
        avg_size_stmt = select(func.avg(CacheEntry.data_size))
        avg_size_result = await self.session.execute(avg_size_stmt)
        avg_size = avg_size_result.scalar() or 0
        
        # Largest entry
        max_size_stmt = select(func.max(CacheEntry.data_size))
        max_size_result = await self.session.execute(max_size_stmt)
        max_size = max_size_result.scalar() or 0
        
        # Compressed entries
        compressed_count_stmt = select(func.count(CacheEntry.id)).where(
            CacheEntry.is_compressed == True
        )
        compressed_count_result = await self.session.execute(compressed_count_stmt)
        compressed_count = compressed_count_result.scalar() or 0
        
        # Compression ratio
        avg_compression_stmt = select(func.avg(CacheEntry.compression_ratio)).where(
            CacheEntry.compression_ratio.is_not(None)
        )
        avg_compression_result = await self.session.execute(avg_compression_stmt)
        avg_compression = avg_compression_result.scalar() or 0
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "average_size_bytes": round(avg_size, 2),
            "max_size_bytes": max_size,
            "compressed_entries": compressed_count,
            "average_compression_ratio": round(avg_compression, 3)
        }
    
    async def get_access_statistics(self) -> Dict[str, Any]:
        """Get access statistics."""
        # Total accesses
        total_accesses_stmt = select(func.sum(CacheEntry.access_count))
        total_accesses_result = await self.session.execute(total_accesses_stmt)
        total_accesses = total_accesses_result.scalar() or 0
        
        # Average accesses
        avg_accesses_stmt = select(func.avg(CacheEntry.access_count))
        avg_accesses_result = await self.session.execute(avg_accesses_stmt)
        avg_accesses = avg_accesses_result.scalar() or 0
        
        # Most accessed
        max_accesses_stmt = select(func.max(CacheEntry.access_count))
        max_accesses_result = await self.session.execute(max_accesses_stmt)
        max_accesses = max_accesses_result.scalar() or 0
        
        # Hit rate (entries accessed at least once)
        hit_count_stmt = select(func.count(CacheEntry.id)).where(
            CacheEntry.access_count > 0
        )
        hit_count_result = await self.session.execute(hit_count_stmt)
        hit_count = hit_count_result.scalar() or 0
        
        total_entries = await self.count()
        hit_rate = (hit_count / total_entries * 100) if total_entries > 0 else 0
        
        return {
            "total_accesses": total_accesses,
            "average_accesses": round(avg_accesses, 2),
            "max_accesses": max_accesses,
            "hit_rate": round(hit_rate, 2),
            "hit_count": hit_count,
            "total_entries": total_entries
        }
    
    async def get_expiration_statistics(self) -> Dict[str, Any]:
        """Get expiration statistics."""
        # Expired entries
        expired_count_stmt = select(func.count(CacheEntry.id)).where(
            and_(
                CacheEntry.expires_at.is_not(None),
                CacheEntry.expires_at <= datetime.utcnow()
            )
        )
        expired_count_result = await self.session.execute(expired_count_stmt)
        expired_count = expired_count_result.scalar() or 0
        
        # Entries with expiration
        with_expiration_stmt = select(func.count(CacheEntry.id)).where(
            CacheEntry.expires_at.is_not(None)
        )
        with_expiration_result = await self.session.execute(with_expiration_stmt)
        with_expiration = with_expiration_result.scalar() or 0
        
        # Entries expiring soon (next 24 hours)
        soon_expire_stmt = select(func.count(CacheEntry.id)).where(
            and_(
                CacheEntry.expires_at.is_not(None),
                CacheEntry.expires_at <= datetime.utcnow() + timedelta(hours=24),
                CacheEntry.expires_at > datetime.utcnow()
            )
        )
        soon_expire_result = await self.session.execute(soon_expire_stmt)
        soon_expire = soon_expire_result.scalar() or 0
        
        return {
            "expired_count": expired_count,
            "with_expiration": with_expiration,
            "expiring_soon": soon_expire
        }
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        base_stats = await self.get_statistics()
        
        return {
            **base_stats,
            "by_type": await self.get_statistics_by_type(),
            "size": await self.get_size_statistics(),
            "access": await self.get_access_statistics(),
            "expiration": await self.get_expiration_statistics()
        }