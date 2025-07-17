"""
Audit log repository for Sistema Mayra.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.audit import AuditLog, AuditActionEnum
from .base import BaseRepository, FilterOptions


class AuditLogRepository(BaseRepository[AuditLog]):
    """Audit log repository with specialized methods."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditLog)
    
    async def create_audit_log(self, action: AuditActionEnum, resource_type: str,
                             description: str, user_id: Optional[int] = None,
                             resource_id: Optional[int] = None, **kwargs) -> AuditLog:
        """Create new audit log entry."""
        return await self.create(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            user_id=user_id,
            success=True,
            **kwargs
        )
    
    async def get_by_user(self, user_id: int) -> List[AuditLog]:
        """Get audit logs by user."""
        filter_options = FilterOptions()
        filter_options.add_filter(AuditLog.user_id == user_id)
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_action(self, action: AuditActionEnum) -> List[AuditLog]:
        """Get audit logs by action."""
        filter_options = FilterOptions()
        filter_options.add_filter(AuditLog.action == action)
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_resource(self, resource_type: str, resource_id: Optional[int] = None) -> List[AuditLog]:
        """Get audit logs by resource."""
        filter_options = FilterOptions()
        filter_options.add_filter(AuditLog.resource_type == resource_type)
        
        if resource_id:
            filter_options.add_filter(AuditLog.resource_id == resource_id)
        
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_session(self, session_id: str) -> List[AuditLog]:
        """Get audit logs by session."""
        filter_options = FilterOptions()
        filter_options.add_filter(AuditLog.session_id == session_id)
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_ip_address(self, ip_address: str) -> List[AuditLog]:
        """Get audit logs by IP address."""
        filter_options = FilterOptions()
        filter_options.add_filter(AuditLog.ip_address == ip_address)
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_successful_logs(self) -> List[AuditLog]:
        """Get successful audit logs."""
        return await self.find_by(success=True)
    
    async def get_failed_logs(self) -> List[AuditLog]:
        """Get failed audit logs."""
        return await self.find_by(success=False)
    
    async def get_with_user(self, log_id: int) -> Optional[AuditLog]:
        """Get audit log with user."""
        stmt = select(AuditLog).where(AuditLog.id == log_id).options(
            selectinload(AuditLog.user)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_recent_logs(self, hours: int = 24) -> List[AuditLog]:
        """Get recent audit logs."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            AuditLog.created_at >= datetime.utcnow() - timedelta(hours=hours)
        )
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_logs_by_date_range(self, start_date: datetime, end_date: datetime) -> List[AuditLog]:
        """Get audit logs by date range."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                AuditLog.created_at >= start_date,
                AuditLog.created_at <= end_date
            )
        )
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_security_logs(self) -> List[AuditLog]:
        """Get security-related audit logs."""
        security_actions = [
            AuditActionEnum.LOGIN,
            AuditActionEnum.LOGOUT,
            AuditActionEnum.SYSTEM_ERROR
        ]
        
        filter_options = FilterOptions()
        filter_options.add_filter(AuditLog.action.in_(security_actions))
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_user_activity(self, user_id: int, days: int = 30) -> List[AuditLog]:
        """Get user activity logs."""
        filter_options = FilterOptions()
        filter_options.add_filter(AuditLog.user_id == user_id)
        filter_options.add_filter(
            AuditLog.created_at >= datetime.utcnow() - timedelta(days=days)
        )
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_resource_history(self, resource_type: str, resource_id: int) -> List[AuditLog]:
        """Get resource history."""
        filter_options = FilterOptions()
        filter_options.add_filter(AuditLog.resource_type == resource_type)
        filter_options.add_filter(AuditLog.resource_id == resource_id)
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_failed_logins(self, hours: int = 24) -> List[AuditLog]:
        """Get failed login attempts."""
        filter_options = FilterOptions()
        filter_options.add_filter(AuditLog.action == AuditActionEnum.LOGIN)
        filter_options.add_filter(AuditLog.success == False)
        filter_options.add_filter(
            AuditLog.created_at >= datetime.utcnow() - timedelta(hours=hours)
        )
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_suspicious_activity(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Get suspicious activity (multiple failed attempts from same IP)."""
        # Get IPs with multiple failed login attempts
        suspicious_ips_stmt = select(
            AuditLog.ip_address,
            func.count(AuditLog.id).label('attempt_count')
        ).where(
            and_(
                AuditLog.action == AuditActionEnum.LOGIN,
                AuditLog.success == False,
                AuditLog.created_at >= datetime.utcnow() - timedelta(hours=24),
                AuditLog.ip_address.is_not(None)
            )
        ).group_by(AuditLog.ip_address).having(
            func.count(AuditLog.id) >= threshold
        ).order_by(func.count(AuditLog.id).desc())
        
        result = await self.session.execute(suspicious_ips_stmt)
        return [
            {
                "ip_address": row.ip_address,
                "attempt_count": row.attempt_count
            }
            for row in result.fetchall()
        ]
    
    async def search_logs(self, query: str, filters: Optional[Dict[str, Any]] = None,
                         page: int = 1, per_page: int = 50):
        """Search audit logs."""
        filter_options = FilterOptions()
        
        # Add text search
        search_conditions = []
        search_conditions.append(AuditLog.description.ilike(f"%{query}%"))
        search_conditions.append(AuditLog.resource_type.ilike(f"%{query}%"))
        if query.strip():
            search_conditions.append(AuditLog.error_message.ilike(f"%{query}%"))
        
        filter_options.add_filter(or_(*search_conditions))
        
        # Add filters
        if filters:
            if "user_id" in filters:
                filter_options.add_filter(AuditLog.user_id == filters["user_id"])
            
            if "action" in filters:
                filter_options.add_filter(AuditLog.action == filters["action"])
            
            if "resource_type" in filters:
                filter_options.add_filter(AuditLog.resource_type == filters["resource_type"])
            
            if "success" in filters:
                filter_options.add_filter(AuditLog.success == filters["success"])
            
            if "ip_address" in filters:
                filter_options.add_filter(AuditLog.ip_address == filters["ip_address"])
            
            if "date_from" in filters:
                filter_options.add_filter(AuditLog.created_at >= filters["date_from"])
            
            if "date_to" in filters:
                filter_options.add_filter(AuditLog.created_at <= filters["date_to"])
        
        # Order by creation date
        filter_options.add_order_by(AuditLog.created_at, "desc")
        
        return await self.paginate(page, per_page, filter_options)
    
    async def cleanup_old_logs(self, days: int = 90) -> int:
        """Clean up old audit logs."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Keep security-related logs longer
        security_actions = [
            AuditActionEnum.LOGIN,
            AuditActionEnum.LOGOUT,
            AuditActionEnum.SYSTEM_ERROR
        ]
        
        filter_options = FilterOptions()
        filter_options.add_filter(AuditLog.created_at < cutoff_date)
        filter_options.add_filter(~AuditLog.action.in_(security_actions))
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        logs_to_delete = result.scalars().all()
        
        for log in logs_to_delete:
            await self.delete(log.id)
        
        return len(logs_to_delete)
    
    async def get_statistics_by_action(self) -> Dict[str, int]:
        """Get statistics by action."""
        stmt = select(
            AuditLog.action,
            func.count(AuditLog.id)
        ).group_by(AuditLog.action)
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_statistics_by_resource_type(self) -> Dict[str, int]:
        """Get statistics by resource type."""
        stmt = select(
            AuditLog.resource_type,
            func.count(AuditLog.id)
        ).group_by(AuditLog.resource_type)
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_statistics_by_user(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get statistics by user."""
        stmt = select(
            AuditLog.user_id,
            func.count(AuditLog.id).label('log_count')
        ).where(
            AuditLog.user_id.is_not(None)
        ).group_by(AuditLog.user_id).order_by(
            func.count(AuditLog.id).desc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return [
            {
                "user_id": row.user_id,
                "log_count": row.log_count
            }
            for row in result.fetchall()
        ]
    
    async def get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        # Average execution time
        avg_time_stmt = select(func.avg(AuditLog.execution_time)).where(
            AuditLog.execution_time.is_not(None)
        )
        avg_time_result = await self.session.execute(avg_time_stmt)
        avg_time = avg_time_result.scalar() or 0
        
        # Slow requests (> 1 second)
        slow_requests_stmt = select(func.count(AuditLog.id)).where(
            AuditLog.execution_time > 1.0
        )
        slow_requests_result = await self.session.execute(slow_requests_stmt)
        slow_requests = slow_requests_result.scalar() or 0
        
        # Success rate
        success_rate_stmt = select(
            func.count(AuditLog.id).filter(AuditLog.success == True),
            func.count(AuditLog.id)
        )
        success_rate_result = await self.session.execute(success_rate_stmt)
        success_count, total_count = success_rate_result.fetchone()
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "average_execution_time": round(avg_time, 3),
            "slow_requests": slow_requests,
            "success_rate": round(success_rate, 2)
        }
    
    async def get_daily_activity(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily activity statistics."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = select(
            func.date(AuditLog.created_at).label('date'),
            func.count(AuditLog.id).label('log_count'),
            func.count(AuditLog.id).filter(AuditLog.success == True).label('success_count'),
            func.count(AuditLog.id).filter(AuditLog.success == False).label('error_count')
        ).where(
            AuditLog.created_at >= start_date
        ).group_by(
            func.date(AuditLog.created_at)
        ).order_by(
            func.date(AuditLog.created_at).desc()
        )
        
        result = await self.session.execute(stmt)
        return [
            {
                "date": row.date.isoformat(),
                "total_logs": row.log_count,
                "success_count": row.success_count,
                "error_count": row.error_count
            }
            for row in result.fetchall()
        ]
    
    async def get_audit_statistics(self) -> Dict[str, Any]:
        """Get comprehensive audit statistics."""
        base_stats = await self.get_statistics()
        
        # Success/failure counts
        success_count = await self.count_by_filter(AuditLog.success == True)
        error_count = await self.count_by_filter(AuditLog.success == False)
        
        return {
            **base_stats,
            "success_count": success_count,
            "error_count": error_count,
            "by_action": await self.get_statistics_by_action(),
            "by_resource_type": await self.get_statistics_by_resource_type(),
            "by_user": await self.get_statistics_by_user(),
            "performance": await self.get_performance_statistics()
        }
    
    async def count_by_filter(self, filter_condition) -> int:
        """Count records by filter condition."""
        stmt = select(func.count(AuditLog.id)).where(filter_condition)
        result = await self.session.execute(stmt)
        return result.scalar() or 0