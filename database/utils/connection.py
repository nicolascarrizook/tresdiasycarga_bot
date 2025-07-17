"""
Database connection utilities for Sistema Mayra.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool, NullPool
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager with health checking and reconnection."""
    
    def __init__(self, database_url: str, async_database_url: Optional[str] = None, **kwargs):
        self.database_url = database_url
        self.async_database_url = async_database_url or database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        self.connection_kwargs = kwargs
        
        # Connection objects
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        
        # Health tracking
        self.is_healthy = False
        self.last_health_check = None
        self.connection_errors = 0
        self.max_connection_errors = 5
    
    def initialize(self):
        """Initialize database connections."""
        try:
            self._create_engines()
            self._create_session_factories()
            self._test_connections()
            self.is_healthy = True
            self.connection_errors = 0
            logger.info("Database connections initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            self.connection_errors += 1
            self.is_healthy = False
            raise
    
    def _create_engines(self):
        """Create database engines."""
        engine_kwargs = {
            "echo": self.connection_kwargs.get("echo", False),
            "pool_size": self.connection_kwargs.get("pool_size", 10),
            "max_overflow": self.connection_kwargs.get("max_overflow", 20),
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            **self.connection_kwargs.get("engine_kwargs", {})
        }
        
        # Create sync engine
        self.engine = create_engine(self.database_url, **engine_kwargs)
        
        # Create async engine
        async_engine_kwargs = engine_kwargs.copy()
        self.async_engine = create_async_engine(self.async_database_url, **async_engine_kwargs)
    
    def _create_session_factories(self):
        """Create session factories."""
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
    
    def _test_connections(self):
        """Test database connections."""
        # Test sync connection
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Test async connection would need to be done in async context
        logger.info("Sync database connection test passed")
    
    async def test_async_connection(self):
        """Test async database connection."""
        try:
            async with self.async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Async database connection test passed")
            return True
        except Exception as e:
            logger.error(f"Async database connection test failed: {e}")
            return False
    
    def get_session(self):
        """Get sync database session."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        return self.session_factory()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        if not self.async_session_factory:
            raise RuntimeError("Database not initialized")
        
        session = self.async_session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check."""
        health_info = {
            "healthy": False,
            "timestamp": None,
            "sync_connection": False,
            "async_connection": False,
            "connection_errors": self.connection_errors,
            "error_message": None
        }
        
        try:
            # Test sync connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            health_info["sync_connection"] = True
            
            # Test async connection
            health_info["async_connection"] = await self.test_async_connection()
            
            # Overall health
            health_info["healthy"] = health_info["sync_connection"] and health_info["async_connection"]
            
            if health_info["healthy"]:
                self.is_healthy = True
                self.connection_errors = 0
            
        except Exception as e:
            health_info["error_message"] = str(e)
            self.connection_errors += 1
            self.is_healthy = False
            logger.error(f"Database health check failed: {e}")
        
        from datetime import datetime
        health_info["timestamp"] = datetime.utcnow()
        self.last_health_check = health_info["timestamp"]
        
        return health_info
    
    async def reconnect(self):
        """Attempt to reconnect to database."""
        try:
            await self.close()
            self.initialize()
            logger.info("Database reconnection successful")
        except Exception as e:
            logger.error(f"Database reconnection failed: {e}")
            raise
    
    def should_reconnect(self) -> bool:
        """Check if reconnection is needed."""
        return (
            not self.is_healthy and 
            self.connection_errors < self.max_connection_errors
        )
    
    async def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute raw SQL query."""
        try:
            async with self.get_async_session() as session:
                result = await session.execute(text(query), params or {})
                return result
        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {e}")
            self.connection_errors += 1
            raise
    
    async def execute_query_with_retry(self, query: str, params: Optional[Dict] = None, 
                                     max_retries: int = 3) -> Any:
        """Execute query with retry logic."""
        for attempt in range(max_retries):
            try:
                return await self.execute_query(query, params)
            except SQLAlchemyError as e:
                if attempt == max_retries - 1:
                    raise
                
                logger.warning(f"Query failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if self.should_reconnect():
                    await self.reconnect()
                
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            "database_url": self.database_url.replace(\n                self.database_url.split(\"@\")[0].split(\"//\")[1], \"***\"\n            ) if \"@\" in self.database_url else self.database_url,\n            \"is_healthy\": self.is_healthy,\n            \"connection_errors\": self.connection_errors,\n            \"last_health_check\": self.last_health_check,\n            \"pool_size\": self.connection_kwargs.get(\"pool_size\", 10),\n            \"max_overflow\": self.connection_kwargs.get(\"max_overflow\", 20)\n        }\n    \n    def get_engine_info(self) -> Dict[str, Any]:\n        \"\"\"Get engine information.\"\"\"\n        if not self.engine:\n            return {\"status\": \"not_initialized\"}\n        \n        pool = self.engine.pool\n        return {\n            \"status\": \"initialized\",\n            \"pool_size\": pool.size() if hasattr(pool, 'size') else \"unknown\",\n            \"checked_in\": pool.checkedin() if hasattr(pool, 'checkedin') else \"unknown\",\n            \"checked_out\": pool.checkedout() if hasattr(pool, 'checkedout') else \"unknown\",\n            \"overflow\": pool.overflow() if hasattr(pool, 'overflow') else \"unknown\",\n            \"invalid\": pool.invalid() if hasattr(pool, 'invalid') else \"unknown\"\n        }\n    \n    async def get_database_info(self) -> Dict[str, Any]:\n        \"\"\"Get database information.\"\"\"\n        try:\n            async with self.get_async_session() as session:\n                # Get database version\n                version_result = await session.execute(text(\"SELECT version()\"))\n                version = version_result.scalar()\n                \n                # Get database size\n                size_result = await session.execute(text(\n                    \"SELECT pg_size_pretty(pg_database_size(current_database()))\"\n                ))\n                size = size_result.scalar()\n                \n                # Get connection count\n                connections_result = await session.execute(text(\n                    \"SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()\"\n                ))\n                connections = connections_result.scalar()\n                \n                return {\n                    \"version\": version,\n                    \"size\": size,\n                    \"connections\": connections,\n                    \"database_name\": session.bind.url.database\n                }\n        except Exception as e:\n            logger.error(f\"Failed to get database info: {e}\")\n            return {\"error\": str(e)}\n    \n    async def get_table_info(self) -> Dict[str, Any]:\n        \"\"\"Get table information.\"\"\"\n        try:\n            async with self.get_async_session() as session:\n                # Get table sizes\n                table_sizes_result = await session.execute(text(\"\"\"\n                    SELECT \n                        schemaname,\n                        tablename,\n                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,\n                        pg_total_relation_size(schemaname||'.'||tablename) as size_bytes\n                    FROM pg_tables \n                    WHERE schemaname = 'public'\n                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC\n                \"\"\"))\n                \n                tables = []\n                for row in table_sizes_result.fetchall():\n                    tables.append({\n                        \"schema\": row.schemaname,\n                        \"name\": row.tablename,\n                        \"size\": row.size,\n                        \"size_bytes\": row.size_bytes\n                    })\n                \n                # Get total count\n                count_result = await session.execute(text(\n                    \"SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'\"\n                ))\n                total_tables = count_result.scalar()\n                \n                return {\n                    \"tables\": tables,\n                    \"total_count\": total_tables\n                }\n        except Exception as e:\n            logger.error(f\"Failed to get table info: {e}\")\n            return {\"error\": str(e)}\n    \n    async def close(self):\n        \"\"\"Close database connections.\"\"\"\n        try:\n            if self.async_engine:\n                await self.async_engine.dispose()\n            \n            if self.engine:\n                self.engine.dispose()\n            \n            logger.info(\"Database connections closed\")\n        except Exception as e:\n            logger.error(f\"Error closing database connections: {e}\")\n    \n    def __del__(self):\n        \"\"\"Cleanup on destruction.\"\"\"\n        try:\n            if self.engine:\n                self.engine.dispose()\n        except Exception:\n            pass\n\n\n# Global database connection instance\n_db_connection: Optional[DatabaseConnection] = None\n\n\ndef get_database_connection(database_url: str = None, **kwargs) -> DatabaseConnection:\n    \"\"\"Get or create database connection.\"\"\"\n    global _db_connection\n    \n    if _db_connection is None or database_url:\n        if database_url:\n            _db_connection = DatabaseConnection(database_url, **kwargs)\n        else:\n            raise ValueError(\"Database URL is required for first initialization\")\n    \n    return _db_connection\n\n\nasync def test_database_connection(database_url: str) -> Dict[str, Any]:\n    \"\"\"Test database connection.\"\"\"\n    try:\n        db_conn = DatabaseConnection(database_url)\n        db_conn.initialize()\n        \n        health_info = await db_conn.health_check()\n        db_info = await db_conn.get_database_info()\n        \n        await db_conn.close()\n        \n        return {\n            \"success\": True,\n            \"health\": health_info,\n            \"database_info\": db_info\n        }\n    except Exception as e:\n        return {\n            \"success\": False,\n            \"error\": str(e)\n        }\n\n\nasync def check_database_exists(database_url: str) -> bool:\n    \"\"\"Check if database exists.\"\"\"\n    try:\n        # Parse database URL to get connection to postgres database\n        from urllib.parse import urlparse\n        parsed = urlparse(database_url)\n        \n        # Connect to postgres database to check if target database exists\n        postgres_url = database_url.replace(f\"/{parsed.path[1:]}\", \"/postgres\")\n        \n        db_conn = DatabaseConnection(postgres_url)\n        db_conn.initialize()\n        \n        result = await db_conn.execute_query(\n            \"SELECT 1 FROM pg_database WHERE datname = :db_name\",\n            {\"db_name\": parsed.path[1:]}\n        )\n        \n        exists = result.fetchone() is not None\n        await db_conn.close()\n        \n        return exists\n    except Exception as e:\n        logger.error(f\"Failed to check database existence: {e}\")\n        return False\n\n\nasync def create_database(database_url: str) -> bool:\n    \"\"\"Create database if it doesn't exist.\"\"\"\n    try:\n        from urllib.parse import urlparse\n        parsed = urlparse(database_url)\n        db_name = parsed.path[1:]\n        \n        # Connect to postgres database\n        postgres_url = database_url.replace(f\"/{db_name}\", \"/postgres\")\n        \n        db_conn = DatabaseConnection(postgres_url)\n        db_conn.initialize()\n        \n        # Check if database exists\n        if await check_database_exists(database_url):\n            logger.info(f\"Database {db_name} already exists\")\n            await db_conn.close()\n            return True\n        \n        # Create database\n        await db_conn.execute_query(f\"CREATE DATABASE {db_name}\")\n        await db_conn.close()\n        \n        logger.info(f\"Database {db_name} created successfully\")\n        return True\n    except Exception as e:\n        logger.error(f\"Failed to create database: {e}\")\n        return False\n\n\nasync def drop_database(database_url: str) -> bool:\n    \"\"\"Drop database.\"\"\"\n    try:\n        from urllib.parse import urlparse\n        parsed = urlparse(database_url)\n        db_name = parsed.path[1:]\n        \n        # Connect to postgres database\n        postgres_url = database_url.replace(f\"/{db_name}\", \"/postgres\")\n        \n        db_conn = DatabaseConnection(postgres_url)\n        db_conn.initialize()\n        \n        # Drop database\n        await db_conn.execute_query(f\"DROP DATABASE IF EXISTS {db_name}\")\n        await db_conn.close()\n        \n        logger.info(f\"Database {db_name} dropped successfully\")\n        return True\n    except Exception as e:\n        logger.error(f\"Failed to drop database: {e}\")\n        return False"