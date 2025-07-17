"""
Database connection and session management for Sistema Mayra API.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


class DatabaseManager:
    """Database connection manager."""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        
    def initialize(self):
        """Initialize database connections."""
        try:
            # Create sync engine
            self.engine = create_engine(
                settings.database.url,
                echo=settings.database.echo,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            
            # Create async engine
            async_url = settings.database.url.replace("postgresql://", "postgresql+asyncpg://")
            self.async_engine = create_async_engine(
                async_url,
                echo=settings.database.echo,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            
            # Create session factories
            self.session_factory = sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
                autoflush=False
            )
            
            self.async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False
            )
            
            # Add event listeners
            self._setup_event_listeners()
            
            logger.info("Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def _setup_event_listeners(self):
        """Setup database event listeners."""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for better performance."""
            if "sqlite" in settings.database.url:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log database connection checkout."""
            logger.debug("Database connection checked out")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log database connection checkin."""
            logger.debug("Database connection checked in")
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        if not self.async_session_factory:
            raise RuntimeError("Database not initialized")
        
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def get_session(self):
        """Get sync database session."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        
        return self.session_factory()
    
    async def create_tables(self):
        """Create all database tables."""
        if not self.async_engine:
            raise RuntimeError("Database not initialized")
        
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
    
    async def drop_tables(self):
        """Drop all database tables."""
        if not self.async_engine:
            raise RuntimeError("Database not initialized")
        
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Database tables dropped successfully")
    
    async def close(self):
        """Close database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        
        if self.engine:
            self.engine.dispose()
        
        logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()


# Dependency functions for FastAPI
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database session."""
    async with db_manager.get_async_session() as session:
        yield session


def get_db():
    """FastAPI dependency for sync database session."""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


# Redis connection management
class RedisManager:
    """Redis connection manager."""
    
    def __init__(self):
        self.redis_client = None
        self._connection_pool = None
    
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            import redis.asyncio as redis
            
            self.redis_client = redis.from_url(
                settings.redis.url,
                decode_responses=True,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {str(e)}")
            raise
    
    async def get_client(self):
        """Get Redis client."""
        if not self.redis_client:
            await self.initialize()
        return self.redis_client
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Redis connection closed")


# Global Redis manager instance
redis_manager = RedisManager()


# ChromaDB connection management
class ChromaManager:
    """ChromaDB connection manager."""
    
    def __init__(self):
        self.client = None
        self.collection = None
    
    def initialize(self):
        """Initialize ChromaDB connection."""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            self.client = chromadb.PersistentClient(
                path=settings.chroma.persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("ChromaDB connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    def get_collection(self):
        """Get ChromaDB collection."""
        if not self.collection:
            self.initialize()
        return self.collection
    
    def close(self):
        """Close ChromaDB connection."""
        # ChromaDB doesn't require explicit closing
        logger.info("ChromaDB connection closed")


# Global ChromaDB manager instance
chroma_manager = ChromaManager()


# Database lifecycle management
async def startup_database():
    """Initialize all database connections on startup."""
    try:
        # Initialize main database
        db_manager.initialize()
        
        # Initialize Redis
        await redis_manager.initialize()
        
        # Initialize ChromaDB
        chroma_manager.initialize()
        
        logger.info("All database connections initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize databases: {str(e)}")
        raise


async def shutdown_database():
    """Close all database connections on shutdown."""
    try:
        await db_manager.close()
        await redis_manager.close()
        chroma_manager.close()
        
        logger.info("All database connections closed successfully")
        
    except Exception as e:
        logger.error(f"Error during database shutdown: {str(e)}")


# Dependency functions for external services
async def get_redis():
    """FastAPI dependency for Redis client."""
    return await redis_manager.get_client()


def get_chroma():
    """FastAPI dependency for ChromaDB collection."""
    return chroma_manager.get_collection()


# Health check functions
async def check_database_health() -> dict:
    """Check database health status."""
    health_status = {
        "postgres": {"status": "unknown", "details": None},
        "redis": {"status": "unknown", "details": None},
        "chroma": {"status": "unknown", "details": None}
    }
    
    # Check PostgreSQL
    try:
        async with db_manager.get_async_session() as session:
            result = await session.execute("SELECT 1")
            health_status["postgres"]["status"] = "healthy"
    except Exception as e:
        health_status["postgres"]["status"] = "unhealthy"
        health_status["postgres"]["details"] = str(e)
    
    # Check Redis
    try:
        redis_client = await redis_manager.get_client()
        await redis_client.ping()
        health_status["redis"]["status"] = "healthy"
    except Exception as e:
        health_status["redis"]["status"] = "unhealthy"
        health_status["redis"]["details"] = str(e)
    
    # Check ChromaDB
    try:
        collection = chroma_manager.get_collection()
        collection.count()
        health_status["chroma"]["status"] = "healthy"
    except Exception as e:
        health_status["chroma"]["status"] = "unhealthy"
        health_status["chroma"]["details"] = str(e)
    
    return health_status