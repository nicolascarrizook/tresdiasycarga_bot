"""
Embedding repository for Sistema Mayra.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.embedding import Embedding, EmbeddingTypeEnum, EmbeddingModelEnum
from .base import BaseRepository, FilterOptions


class EmbeddingRepository(BaseRepository[Embedding]):
    """Embedding repository with specialized methods."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Embedding)
    
    async def get_by_content_hash(self, content_hash: str) -> Optional[Embedding]:
        """Get embedding by content hash."""
        return await self.find_one_by(content_hash=content_hash)
    
    async def get_by_chroma_id(self, chroma_id: str) -> Optional[Embedding]:
        """Get embedding by ChromaDB ID."""
        return await self.find_one_by(chroma_id=chroma_id)
    
    async def get_by_type(self, embedding_type: EmbeddingTypeEnum) -> List[Embedding]:
        """Get embeddings by type."""
        return await self.find_by(embedding_type=embedding_type)
    
    async def get_by_model(self, model_name: EmbeddingModelEnum) -> List[Embedding]:
        """Get embeddings by model."""
        return await self.find_by(model_name=model_name)
    
    async def get_by_source(self, source_type: str, source_id: int) -> List[Embedding]:
        """Get embeddings by source."""
        return await self.find_by(source_type=source_type, source_id=source_id)
    
    async def get_by_language(self, language: str) -> List[Embedding]:
        """Get embeddings by language."""
        return await self.find_by(language=language)
    
    async def get_by_collection(self, collection: str) -> List[Embedding]:
        """Get embeddings by ChromaDB collection."""
        return await self.find_by(chroma_collection=collection)
    
    async def create_embedding(self, content: str, embedding_type: EmbeddingTypeEnum,
                             vector: List[float], source_type: str, source_id: int,
                             model_name: EmbeddingModelEnum, **kwargs) -> Embedding:
        """Create new embedding."""
        import hashlib
        
        # Generate content hash
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Check if embedding already exists
        existing = await self.get_by_content_hash(content_hash)
        if existing and existing.model_name == model_name:
            return existing
        
        embedding = await self.create(
            content=content,
            content_hash=content_hash,
            embedding_type=embedding_type,
            vector=vector,
            vector_dimension=len(vector),
            source_type=source_type,
            source_id=source_id,
            model_name=model_name,
            content_length=len(content),
            word_count=len(content.split()),
            retrieval_count=0,
            **kwargs
        )
        
        return embedding
    
    async def get_or_create_embedding(self, content: str, embedding_type: EmbeddingTypeEnum,
                                    vector: List[float], source_type: str, source_id: int,
                                    model_name: EmbeddingModelEnum, **kwargs) -> tuple[Embedding, bool]:
        """Get or create embedding."""
        import hashlib
        
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Try to find existing embedding
        existing = await self.find_one_by(content_hash=content_hash, model_name=model_name)
        if existing:
            return existing, False
        
        # Create new embedding
        embedding = await self.create_embedding(
            content=content,
            embedding_type=embedding_type,
            vector=vector,
            source_type=source_type,
            source_id=source_id,
            model_name=model_name,
            **kwargs
        )
        
        return embedding, True
    
    async def update_vector(self, embedding_id: int, vector: List[float]) -> bool:
        """Update embedding vector."""
        embedding = await self.get_by_id(embedding_id)
        if not embedding:
            return False
        
        embedding.vector = vector
        embedding.vector_dimension = len(vector)
        
        if not embedding.validate_vector():
            return False
        
        await self.session.commit()
        return True
    
    async def increment_retrieval_count(self, embedding_id: int) -> bool:
        """Increment retrieval count."""
        embedding = await self.get_by_id(embedding_id)
        if not embedding:
            return False
        
        embedding.increment_retrieval_count()
        await self.session.commit()
        return True
    
    async def update_quality_score(self, embedding_id: int, score: float) -> bool:
        """Update quality score."""
        embedding = await self.get_by_id(embedding_id)
        if not embedding:
            return False
        
        embedding.update_quality_score(score)
        await self.session.commit()
        return True
    
    async def set_chroma_data(self, embedding_id: int, chroma_id: str, collection: str) -> bool:
        """Set ChromaDB data."""
        embedding = await self.get_by_id(embedding_id)
        if not embedding:
            return False
        
        embedding.set_chroma_data(chroma_id, collection)
        await self.session.commit()
        return True
    
    async def get_by_similarity_threshold(self, threshold: float) -> List[Embedding]:
        """Get embeddings by similarity threshold."""
        filter_options = FilterOptions()
        filter_options.add_filter(Embedding.similarity_threshold >= threshold)
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_quality_score(self, min_score: float) -> List[Embedding]:
        """Get embeddings by minimum quality score."""
        filter_options = FilterOptions()
        filter_options.add_filter(Embedding.quality_score >= min_score)
        filter_options.add_order_by(Embedding.quality_score, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_most_used_embeddings(self, limit: int = 10) -> List[Embedding]:
        """Get most used embeddings."""
        filter_options = FilterOptions()
        filter_options.add_order_by(Embedding.retrieval_count, "desc")
        
        stmt = self.build_query(filter_options).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_recent_embeddings(self, days: int = 7) -> List[Embedding]:
        """Get recently created embeddings."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            Embedding.created_at >= datetime.utcnow() - timedelta(days=days)
        )
        filter_options.add_order_by(Embedding.created_at, "desc")
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_unused_embeddings(self, days: int = 30) -> List[Embedding]:
        """Get unused embeddings (not retrieved in specified days)."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        filter_options = FilterOptions()
        filter_options.add_filter(
            or_(
                Embedding.last_retrieved_at < cutoff_date,
                Embedding.last_retrieved_at.is_(None)
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def cleanup_unused_embeddings(self, days: int = 90) -> int:
        """Clean up unused embeddings."""
        unused_embeddings = await self.get_unused_embeddings(days)
        
        for embedding in unused_embeddings:
            await self.delete(embedding.id)
        
        return len(unused_embeddings)
    
    async def get_embeddings_by_content_length(self, min_length: int, max_length: int) -> List[Embedding]:
        """Get embeddings by content length range."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                Embedding.content_length >= min_length,
                Embedding.content_length <= max_length
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_embeddings_by_word_count(self, min_words: int, max_words: int) -> List[Embedding]:
        """Get embeddings by word count range."""
        filter_options = FilterOptions()
        filter_options.add_filter(
            and_(
                Embedding.word_count >= min_words,
                Embedding.word_count <= max_words
            )
        )
        
        stmt = self.build_query(filter_options)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def search_embeddings(self, query: str, embedding_type: Optional[EmbeddingTypeEnum] = None,
                              model_name: Optional[EmbeddingModelEnum] = None,
                              page: int = 1, per_page: int = 20):
        """Search embeddings by content."""
        filter_options = FilterOptions()
        
        # Add text search
        filter_options.add_filter(Embedding.content.ilike(f"%{query}%"))
        
        # Add filters
        if embedding_type:
            filter_options.add_filter(Embedding.embedding_type == embedding_type)
        
        if model_name:
            filter_options.add_filter(Embedding.model_name == model_name)
        
        # Order by quality score and usage
        filter_options.add_order_by(Embedding.quality_score, "desc")
        filter_options.add_order_by(Embedding.retrieval_count, "desc")
        
        return await self.paginate(page, per_page, filter_options)
    
    async def validate_all_vectors(self) -> Dict[str, int]:
        """Validate all embedding vectors."""
        embeddings = await self.get_all(active_only=False)
        
        valid_count = 0
        invalid_count = 0
        
        for embedding in embeddings:
            if embedding.validate_vector():
                valid_count += 1
            else:
                invalid_count += 1
        
        await self.session.commit()
        
        return {
            "valid": valid_count,
            "invalid": invalid_count,
            "total": len(embeddings)
        }
    
    async def get_statistics_by_type(self) -> Dict[str, int]:
        """Get statistics by embedding type."""
        stmt = select(
            Embedding.embedding_type,
            func.count(Embedding.id)
        ).group_by(Embedding.embedding_type)
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_statistics_by_model(self) -> Dict[str, int]:
        """Get statistics by model."""
        stmt = select(
            Embedding.model_name,
            func.count(Embedding.id)
        ).group_by(Embedding.model_name)
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_statistics_by_language(self) -> Dict[str, int]:
        """Get statistics by language."""
        stmt = select(
            Embedding.language,
            func.count(Embedding.id)
        ).group_by(Embedding.language)
        
        result = await self.session.execute(stmt)
        return dict(result.fetchall())
    
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        # Total retrievals
        total_retrievals_stmt = select(func.sum(Embedding.retrieval_count))
        total_retrievals_result = await self.session.execute(total_retrievals_stmt)
        total_retrievals = total_retrievals_result.scalar() or 0
        
        # Average retrievals per embedding
        avg_retrievals_stmt = select(func.avg(Embedding.retrieval_count))
        avg_retrievals_result = await self.session.execute(avg_retrievals_stmt)
        avg_retrievals = avg_retrievals_result.scalar() or 0
        
        # Most used embedding
        most_used_stmt = select(func.max(Embedding.retrieval_count))
        most_used_result = await self.session.execute(most_used_stmt)
        most_used = most_used_result.scalar() or 0
        
        # Recent usage (last 30 days)
        recent_usage_stmt = select(func.count(Embedding.id)).where(
            Embedding.last_retrieved_at >= datetime.utcnow() - timedelta(days=30)
        )
        recent_usage_result = await self.session.execute(recent_usage_stmt)
        recent_usage = recent_usage_result.scalar() or 0
        
        return {
            "total_retrievals": total_retrievals,
            "average_retrievals_per_embedding": round(avg_retrievals, 2),
            "most_used_retrieval_count": most_used,
            "recent_usage_count": recent_usage
        }
    
    async def get_quality_statistics(self) -> Dict[str, Any]:
        """Get quality statistics."""
        # Average quality score
        avg_quality_stmt = select(func.avg(Embedding.quality_score)).where(
            Embedding.quality_score.is_not(None)
        )
        avg_quality_result = await self.session.execute(avg_quality_stmt)
        avg_quality = avg_quality_result.scalar() or 0
        
        # Quality distribution
        high_quality_stmt = select(func.count(Embedding.id)).where(
            Embedding.quality_score >= 0.8
        )
        medium_quality_stmt = select(func.count(Embedding.id)).where(
            and_(Embedding.quality_score >= 0.6, Embedding.quality_score < 0.8)
        )
        low_quality_stmt = select(func.count(Embedding.id)).where(
            Embedding.quality_score < 0.6
        )
        
        high_quality_result = await self.session.execute(high_quality_stmt)
        medium_quality_result = await self.session.execute(medium_quality_stmt)
        low_quality_result = await self.session.execute(low_quality_stmt)
        
        return {
            "average_quality": round(avg_quality, 3),
            "high_quality": high_quality_result.scalar(),
            "medium_quality": medium_quality_result.scalar(),
            "low_quality": low_quality_result.scalar()
        }
    
    async def get_content_statistics(self) -> Dict[str, Any]:
        """Get content statistics."""
        # Average content length
        avg_length_stmt = select(func.avg(Embedding.content_length))
        avg_length_result = await self.session.execute(avg_length_stmt)
        avg_length = avg_length_result.scalar() or 0
        
        # Average word count
        avg_words_stmt = select(func.avg(Embedding.word_count))
        avg_words_result = await self.session.execute(avg_words_stmt)
        avg_words = avg_words_result.scalar() or 0
        
        # Vector dimension distribution
        dimension_stmt = select(
            Embedding.vector_dimension,
            func.count(Embedding.id)
        ).group_by(Embedding.vector_dimension)
        dimension_result = await self.session.execute(dimension_stmt)
        dimensions = dict(dimension_result.fetchall())
        
        return {
            "average_content_length": round(avg_length, 2),
            "average_word_count": round(avg_words, 2),
            "vector_dimensions": dimensions
        }
    
    async def get_embedding_statistics(self) -> Dict[str, Any]:
        """Get comprehensive embedding statistics."""
        base_stats = await self.get_statistics()
        
        return {
            **base_stats,
            "by_type": await self.get_statistics_by_type(),
            "by_model": await self.get_statistics_by_model(),
            "by_language": await self.get_statistics_by_language(),
            "usage": await self.get_usage_statistics(),
            "quality": await self.get_quality_statistics(),
            "content": await self.get_content_statistics()
        }