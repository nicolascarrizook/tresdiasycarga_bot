"""
Base seeder class for Sistema Mayra database seeders.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseSeeder(ABC):
    """Base class for all database seeders."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.created_records = []
        self.errors = []
    
    @abstractmethod
    async def seed(self) -> Dict[str, Any]:
        """Execute the seeding process."""
        pass
    
    @abstractmethod
    def get_seeder_name(self) -> str:
        """Get the name of this seeder."""
        pass
    
    def log_success(self, message: str, count: int = 1):
        """Log successful seeding operation."""
        logger.info(f"[{self.get_seeder_name()}] {message} ({count} records)")
    
    def log_error(self, message: str, error: Exception = None):
        """Log seeding error."""
        error_msg = f"[{self.get_seeder_name()}] ERROR: {message}"
        if error:
            error_msg += f" - {str(error)}"
        logger.error(error_msg)
        self.errors.append(error_msg)
    
    def log_info(self, message: str):
        """Log informational message."""
        logger.info(f"[{self.get_seeder_name()}] {message}")
    
    async def commit_batch(self, batch: List[Any], batch_name: str = "batch"):
        """Commit a batch of records."""
        try:
            self.session.add_all(batch)
            await self.session.commit()
            self.created_records.extend(batch)
            self.log_success(f"Created {batch_name}", len(batch))
        except Exception as e:
            await self.session.rollback()
            self.log_error(f"Failed to create {batch_name}", e)
            raise
    
    async def create_single(self, record: Any, record_name: str = "record"):
        """Create a single record."""
        try:
            self.session.add(record)
            await self.session.commit()
            self.created_records.append(record)
            self.log_success(f"Created {record_name}")
            return record
        except Exception as e:
            await self.session.rollback()
            self.log_error(f"Failed to create {record_name}", e)
            raise
    
    def get_summary(self) -> Dict[str, Any]:
        """Get seeding summary."""
        return {
            "seeder": self.get_seeder_name(),
            "created_count": len(self.created_records),
            "error_count": len(self.errors),
            "errors": self.errors,
            "timestamp": datetime.utcnow()
        }


class SeederRunner:
    """Runner for executing multiple seeders."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.seeders: List[BaseSeeder] = []
        self.results: List[Dict[str, Any]] = []
    
    def add_seeder(self, seeder: BaseSeeder):
        """Add a seeder to the runner."""
        self.seeders.append(seeder)
    
    async def run_all(self) -> Dict[str, Any]:
        """Run all registered seeders."""
        start_time = datetime.utcnow()
        
        for seeder in self.seeders:
            try:
                result = await seeder.seed()
                self.results.append(result)
                logger.info(f"Seeder {seeder.get_seeder_name()} completed successfully")
            except Exception as e:
                logger.error(f"Seeder {seeder.get_seeder_name()} failed: {e}")
                self.results.append({
                    "seeder": seeder.get_seeder_name(),
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow()
                })
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Calculate summary
        successful_seeders = sum(1 for r in self.results if r.get("success", False))
        total_records = sum(r.get("created_count", 0) for r in self.results)
        
        summary = {
            "total_seeders": len(self.seeders),
            "successful_seeders": successful_seeders,
            "failed_seeders": len(self.seeders) - successful_seeders,
            "total_records_created": total_records,
            "execution_time": execution_time,
            "results": self.results,
            "timestamp": datetime.utcnow()
        }
        
        logger.info(f"Seeding completed: {successful_seeders}/{len(self.seeders)} seeders successful, {total_records} records created")
        
        return summary