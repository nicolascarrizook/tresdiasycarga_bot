"""
Main seeder runner for Sistema Mayra database.
"""
import asyncio
from typing import Dict, Any
from datetime import datetime

from database.utils.connection import get_database_connection
from database.seeders.base import SeederRunner
from database.seeders.user_seeder import UserSeeder
from database.seeders.recipe_seeder import RecipeSeeder
from database.seeders.patient_seeder import PatientSeeder
from database.seeders.plan_seeder import PlanSeeder
from database.seeders.conversation_seeder import ConversationSeeder
from database.seeders.embedding_seeder import EmbeddingSeeder


async def run_all_seeders() -> Dict[str, Any]:
    """Run all database seeders."""
    # Get database connection
    db_connection = get_database_connection()
    
    # Create seeder runner
    runner = SeederRunner(db_connection.get_async_session())
    
    # Add all seeders in order
    runner.add_seeder(UserSeeder(db_connection.get_async_session()))
    runner.add_seeder(RecipeSeeder(db_connection.get_async_session()))
    runner.add_seeder(PatientSeeder(db_connection.get_async_session()))
    runner.add_seeder(PlanSeeder(db_connection.get_async_session()))
    runner.add_seeder(ConversationSeeder(db_connection.get_async_session()))
    runner.add_seeder(EmbeddingSeeder(db_connection.get_async_session()))
    
    # Run all seeders
    return await runner.run_all()


async def run_basic_seeders() -> Dict[str, Any]:
    """Run only basic seeders (users and recipes)."""
    # Get database connection
    db_connection = get_database_connection()
    
    # Create seeder runner
    runner = SeederRunner(db_connection.get_async_session())
    
    # Add basic seeders
    runner.add_seeder(UserSeeder(db_connection.get_async_session()))
    runner.add_seeder(RecipeSeeder(db_connection.get_async_session()))
    
    # Run basic seeders
    return await runner.run_all()


async def run_test_data_seeders() -> Dict[str, Any]:
    """Run seeders for test data only."""
    # Get database connection
    db_connection = get_database_connection()
    
    # Create seeder runner
    runner = SeederRunner(db_connection.get_async_session())
    
    # Add test data seeders
    runner.add_seeder(PatientSeeder(db_connection.get_async_session()))
    runner.add_seeder(PlanSeeder(db_connection.get_async_session()))
    runner.add_seeder(ConversationSeeder(db_connection.get_async_session()))
    runner.add_seeder(EmbeddingSeeder(db_connection.get_async_session()))
    
    # Run test data seeders
    return await runner.run_all()


if __name__ == "__main__":
    import sys
    
    async def main():
        """Main function to run seeders."""
        if len(sys.argv) > 1:
            mode = sys.argv[1]
            if mode == "basic":
                result = await run_basic_seeders()
            elif mode == "test":
                result = await run_test_data_seeders()
            else:
                result = await run_all_seeders()
        else:
            result = await run_all_seeders()
        
        print(f"Seeding completed:")
        print(f"- Total seeders: {result['total_seeders']}")
        print(f"- Successful: {result['successful_seeders']}")
        print(f"- Failed: {result['failed_seeders']}")
        print(f"- Total records created: {result['total_records_created']}")
        print(f"- Execution time: {result['execution_time']:.2f}s")
        
        if result['failed_seeders'] > 0:
            print("\nFailed seeders:")
            for seeder_result in result['results']:
                if not seeder_result.get('success', False):
                    print(f"- {seeder_result['seeder']}: {seeder_result.get('error', 'Unknown error')}")
    
    # Run the main function
    asyncio.run(main())