"""
Conversation repository for Sistema Mayra.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.conversation import Conversation, ConversationTypeEnum, ConversationStatusEnum, MessageRoleEnum
from .base import BaseRepository, FilterOptions


class ConversationRepository(BaseRepository[Conversation]):
    """Conversation repository with specialized methods."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)
    
    async def get_by_telegram_chat(self, telegram_chat_id: int) -> List[Conversation]:
        """Get conversations by Telegram chat ID."""
        filter_options = FilterOptions()
        filter_options.add_filter(Conversation.telegram_chat_id == telegram_chat_id)
        filter_options.add_order_by(Conversation.started_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_active_by_telegram_chat(self, telegram_chat_id: int) -> Optional[Conversation]:
        """Get active conversation by Telegram chat ID."""
        return await self.find_one_by(
            telegram_chat_id=telegram_chat_id,
            status=ConversationStatusEnum.ACTIVE
        )
    
    async def get_by_user(self, user_id: int) -> List[Conversation]:
        """Get conversations by user ID."""
        filter_options = FilterOptions()
        filter_options.add_filter(Conversation.user_id == user_id)
        filter_options.add_order_by(Conversation.started_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_patient(self, patient_id: int) -> List[Conversation]:
        """Get conversations by patient ID."""
        filter_options = FilterOptions()
        filter_options.add_filter(Conversation.patient_id == patient_id)
        filter_options.add_order_by(Conversation.started_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_plan(self, plan_id: int) -> List[Conversation]:
        """Get conversations by plan ID."""
        filter_options = FilterOptions()
        filter_options.add_filter(Conversation.plan_id == plan_id)
        filter_options.add_order_by(Conversation.started_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_type(self, conversation_type: ConversationTypeEnum) -> List[Conversation]:
        """Get conversations by type."""
        return await self.find_by(conversation_type=conversation_type)
    
    async def get_by_status(self, status: ConversationStatusEnum) -> List[Conversation]:
        """Get conversations by status."""
        return await self.find_by(status=status)
    
    async def get_by_state(self, state: str) -> List[Conversation]:
        """Get conversations by current state."""
        return await self.find_by(current_state=state)
    
    async def get_with_relationships(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation with all relationships."""
        stmt = select(Conversation).where(Conversation.id == conversation_id).options(
            selectinload(Conversation.user),
            selectinload(Conversation.patient),
            selectinload(Conversation.plan)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_conversation(self, conversation_type: ConversationTypeEnum,
                                telegram_chat_id: Optional[int] = None,
                                user_id: Optional[int] = None,
                                patient_id: Optional[int] = None,
                                plan_id: Optional[int] = None,
                                **kwargs) -> Conversation:
        """Create new conversation."""
        conversation = await self.create(
            conversation_type=conversation_type,
            telegram_chat_id=telegram_chat_id,
            user_id=user_id,
            patient_id=patient_id,
            plan_id=plan_id,
            status=ConversationStatusEnum.ACTIVE,
            started_at=datetime.utcnow(),
            current_step=0,
            completion_percentage=0.0,
            **kwargs
        )
        
        return conversation
    
    async def add_message(self, conversation_id: int, role: MessageRoleEnum,
                         content: str, message_type: str = "text",
                         telegram_message_id: Optional[int] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add message to conversation."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        
        conversation.add_message(role, content, message_type, telegram_message_id, metadata)
        await self.session.commit()
        return True
    
    async def update_state(self, conversation_id: int, new_state: str) -> bool:
        """Update conversation state."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        
        conversation.update_state(new_state)
        await self.session.commit()
        return True
    
    async def update_progress(self, conversation_id: int, step: int,
                            total_steps: Optional[int] = None) -> bool:
        """Update conversation progress."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        
        conversation.update_progress(step, total_steps)
        await self.session.commit()
        return True
    
    async def set_context_data(self, conversation_id: int, key: str, value: Any) -> bool:
        """Set context data."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        
        conversation.set_context_data(key, value)
        await self.session.commit()
        return True
    
    async def complete_conversation(self, conversation_id: int,
                                  result_data: Optional[Dict[str, Any]] = None) -> bool:
        """Complete conversation."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        
        conversation.complete(result_data)
        await self.session.commit()
        return True
    
    async def cancel_conversation(self, conversation_id: int, reason: Optional[str] = None) -> bool:
        """Cancel conversation."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        
        conversation.cancel(reason)
        await self.session.commit()
        return True
    
    async def pause_conversation(self, conversation_id: int, reason: Optional[str] = None) -> bool:
        """Pause conversation."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        
        conversation.pause(reason)
        await self.session.commit()
        return True
    
    async def resume_conversation(self, conversation_id: int) -> bool:
        """Resume conversation."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        
        conversation.resume()
        await self.session.commit()
        return True
    
    async def set_error(self, conversation_id: int, error_message: str) -> bool:
        """Set error state."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        
        conversation.set_error(error_message)
        await self.session.commit()
        return True
    
    async def get_active_conversations(self) -> List[Conversation]:
        """Get active conversations."""
        return await self.find_by(status=ConversationStatusEnum.ACTIVE)
    
    async def get_completed_conversations(self) -> List[Conversation]:
        """Get completed conversations."""
        return await self.find_by(status=ConversationStatusEnum.COMPLETED)
    
    async def get_long_running_conversations(self, hours: int = 24) -> List[Conversation]:
        """Get long-running conversations."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        filter_options = FilterOptions()
        filter_options.add_filter(Conversation.status == ConversationStatusEnum.ACTIVE)
        filter_options.add_filter(Conversation.started_at <= cutoff_time)
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_stale_conversations(self, hours: int = 2) -> List[Conversation]:
        """Get stale conversations (no recent activity)."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        filter_options = FilterOptions()
        filter_options.add_filter(Conversation.status == ConversationStatusEnum.ACTIVE)
        filter_options.add_filter(
            or_(
                Conversation.last_message_at <= cutoff_time,
                Conversation.last_message_at.is_(None)
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def cleanup_stale_conversations(self, hours: int = 24) -> int:
        """Clean up stale conversations."""
        stale_conversations = await self.get_stale_conversations(hours)
        
        for conversation in stale_conversations:
            conversation.cancel("Automatically cancelled due to inactivity")
        
        await self.session.commit()
        return len(stale_conversations)
    
    async def get_recent_conversations(self, days: int = 7) -> List[Conversation]:
        """Get recent conversations."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            Conversation.started_at >= datetime.utcnow() - timedelta(days=days)
        )
        filter_options.add_order_by(Conversation.started_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def search_conversations(self, query: str, filters: Optional[Dict[str, Any]] = None,
                                 page: int = 1, per_page: int = 20):
        """Search conversations."""
        filter_options = FilterOptions()
        
        # Add text search
        search_conditions = []
        search_conditions.append(Conversation.title.ilike(f"%{query}%"))
        # Could also search in messages if needed
        filter_options.add_filter(or_(*search_conditions))
        
        # Add filters
        if filters:
            if "conversation_type" in filters:
                filter_options.add_filter(Conversation.conversation_type == filters["conversation_type"])
            
            if "status" in filters:
                filter_options.add_filter(Conversation.status == filters["status"])
            
            if "user_id" in filters:
                filter_options.add_filter(Conversation.user_id == filters["user_id"])
            
            if "patient_id" in filters:
                filter_options.add_filter(Conversation.patient_id == filters["patient_id"])
        
        # Order by start time
        filter_options.add_order_by(Conversation.started_at, "desc")
        
        return await self.paginate(page, per_page, filter_options)
    
    async def get_statistics_by_type(self) -> Dict[str, int]:
        """Get statistics by conversation type."""
        stmt = select(
            Conversation.conversation_type,
            func.count(Conversation.id)
        ).group_by(Conversation.conversation_type)
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_statistics_by_status(self) -> Dict[str, int]:
        """Get statistics by conversation status."""
        stmt = select(
            Conversation.status,
            func.count(Conversation.id)
        ).group_by(Conversation.status)
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_completion_statistics(self) -> Dict[str, Any]:
        """Get completion statistics."""
        # Average completion percentage
        avg_completion_stmt = select(
            func.avg(Conversation.completion_percentage)
        ).where(Conversation.status == ConversationStatusEnum.COMPLETED)
        
        avg_completion_result = await self.session.execute(avg_completion_stmt)
        avg_completion = avg_completion_result.scalar() or 0
        
        # Average duration for completed conversations
        avg_duration_stmt = select(
            func.avg(
                func.extract('epoch', Conversation.completed_at - Conversation.started_at)
            )
        ).where(
            and_(
                Conversation.status == ConversationStatusEnum.COMPLETED,
                Conversation.completed_at.is_not(None)
            )
        )
        
        avg_duration_result = await self.session.execute(avg_duration_stmt)
        avg_duration = avg_duration_result.scalar() or 0
        
        return {
            "average_completion": round(avg_completion, 2),
            "average_duration_seconds": round(avg_duration, 2),
            "average_duration_minutes": round(avg_duration / 60, 2)
        }
    
    async def get_message_statistics(self) -> Dict[str, Any]:
        """Get message statistics."""
        # Total messages
        total_messages_stmt = select(
            func.sum(func.json_array_length(Conversation.messages))
        )
        total_messages_result = await self.session.execute(total_messages_stmt)
        total_messages = total_messages_result.scalar() or 0
        
        # Average messages per conversation
        avg_messages_stmt = select(
            func.avg(func.json_array_length(Conversation.messages))
        )
        avg_messages_result = await self.session.execute(avg_messages_stmt)
        avg_messages = avg_messages_result.scalar() or 0
        
        return {
            "total_messages": total_messages,
            "average_messages_per_conversation": round(avg_messages, 2)
        }
    
    async def get_conversation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive conversation statistics."""
        base_stats = await self.get_statistics()
        
        return {
            **base_stats,
            "by_type": await self.get_statistics_by_type(),
            "by_status": await self.get_statistics_by_status(),
            "completion": await self.get_completion_statistics(),
            "messages": await self.get_message_statistics()
        }