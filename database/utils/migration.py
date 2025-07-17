"""
Database migration utilities for Sistema Mayra.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manager for database migrations using Alembic."""
    
    def __init__(self, alembic_cfg_path: str = "alembic.ini", 
                 migrations_dir: str = "database/migrations"):
        self.alembic_cfg_path = alembic_cfg_path
        self.migrations_dir = migrations_dir
        self.config = None
        self._initialize_config()
    
    def _initialize_config(self):
        """Initialize Alembic configuration."""
        try:
            self.config = Config(self.alembic_cfg_path)
            self.config.set_main_option("script_location", self.migrations_dir)
            logger.info("Alembic configuration initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Alembic config: {e}")
            raise
    
    def create_migration(self, message: str, autogenerate: bool = True) -> str:
        """Create a new migration."""
        try:
            # Generate migration
            if autogenerate:
                command.revision(self.config, message=message, autogenerate=True)
            else:
                command.revision(self.config, message=message)
            
            # Get the latest revision
            script_dir = ScriptDirectory.from_config(self.config)
            latest_revision = script_dir.get_current_head()
            
            logger.info(f"Created migration: {latest_revision} - {message}")
            return latest_revision
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            raise
    
    def run_migrations(self, revision: str = "head") -> bool:
        """Run migrations up to specified revision."""
        try:
            command.upgrade(self.config, revision)
            logger.info(f"Migrations applied successfully up to: {revision}")
            return True
        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            return False
    
    def rollback_migration(self, revision: str) -> bool:
        """Rollback to specified revision."""
        try:
            command.downgrade(self.config, revision)
            logger.info(f"Rolled back to revision: {revision}")
            return True
        except Exception as e:
            logger.error(f"Failed to rollback migration: {e}")
            return False
    
    def get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        try:\n            from database.utils.connection import get_database_connection\n            db_conn = get_database_connection()\n            \n            with db_conn.engine.connect() as connection:\n                context = MigrationContext.configure(connection)\n                return context.get_current_revision()\n        except Exception as e:\n            logger.error(f\"Failed to get current revision: {e}\")\n            return None\n    \n    def get_migration_history(self) -> List[Dict[str, Any]]:\n        \"\"\"Get migration history.\"\"\"\n        try:\n            script_dir = ScriptDirectory.from_config(self.config)\n            revisions = []\n            \n            for revision in script_dir.walk_revisions():\n                revisions.append({\n                    \"revision\": revision.revision,\n                    \"down_revision\": revision.down_revision,\n                    \"branch_labels\": revision.branch_labels,\n                    \"depends_on\": revision.depends_on,\n                    \"doc\": revision.doc,\n                    \"path\": revision.path\n                })\n            \n            return revisions\n        except Exception as e:\n            logger.error(f\"Failed to get migration history: {e}\")\n            return []\n    \n    def check_migration_status(self) -> Dict[str, Any]:\n        \"\"\"Check migration status.\"\"\"\n        try:\n            script_dir = ScriptDirectory.from_config(self.config)\n            current_revision = self.get_current_revision()\n            head_revision = script_dir.get_current_head()\n            \n            # Get pending migrations\n            pending_migrations = []\n            if current_revision != head_revision:\n                from database.utils.connection import get_database_connection\n                db_conn = get_database_connection()\n                \n                with db_conn.engine.connect() as connection:\n                    context = MigrationContext.configure(connection)\n                    \n                    for revision in script_dir.iterate_revisions(head_revision, current_revision):\n                        if revision.revision != current_revision:\n                            pending_migrations.append({\n                                \"revision\": revision.revision,\n                                \"doc\": revision.doc,\n                                \"path\": revision.path\n                            })\n            \n            return {\n                \"current_revision\": current_revision,\n                \"head_revision\": head_revision,\n                \"is_up_to_date\": current_revision == head_revision,\n                \"pending_migrations\": pending_migrations\n            }\n        except Exception as e:\n            logger.error(f\"Failed to check migration status: {e}\")\n            return {\"error\": str(e)}\n    \n    def validate_migration(self, revision: str) -> Dict[str, Any]:\n        \"\"\"Validate a migration revision.\"\"\"\n        try:\n            script_dir = ScriptDirectory.from_config(self.config)\n            \n            # Check if revision exists\n            try:\n                revision_obj = script_dir.get_revision(revision)\n            except Exception:\n                return {\"valid\": False, \"error\": \"Revision not found\"}\n            \n            # Check if migration file exists\n            migration_file = Path(revision_obj.path)\n            if not migration_file.exists():\n                return {\"valid\": False, \"error\": \"Migration file not found\"}\n            \n            # Basic syntax check\n            try:\n                with open(migration_file, 'r') as f:\n                    content = f.read()\n                    compile(content, migration_file, 'exec')\n            except SyntaxError as e:\n                return {\"valid\": False, \"error\": f\"Syntax error: {e}\"}\n            \n            return {\n                \"valid\": True,\n                \"revision\": revision_obj.revision,\n                \"doc\": revision_obj.doc,\n                \"down_revision\": revision_obj.down_revision,\n                \"path\": revision_obj.path\n            }\n        except Exception as e:\n            logger.error(f\"Failed to validate migration: {e}\")\n            return {\"valid\": False, \"error\": str(e)}\n    \n    def generate_sql(self, revision: str = \"head\") -> str:\n        \"\"\"Generate SQL for migrations without applying them.\"\"\"\n        try:\n            from io import StringIO\n            import sys\n            \n            # Capture stdout\n            old_stdout = sys.stdout\n            sys.stdout = captured_output = StringIO()\n            \n            try:\n                command.upgrade(self.config, revision, sql=True)\n                sql_output = captured_output.getvalue()\n            finally:\n                sys.stdout = old_stdout\n            \n            return sql_output\n        except Exception as e:\n            logger.error(f\"Failed to generate SQL: {e}\")\n            return \"\"\n    \n    def stamp_database(self, revision: str = \"head\") -> bool:\n        \"\"\"Stamp database with specific revision without running migrations.\"\"\"\n        try:\n            command.stamp(self.config, revision)\n            logger.info(f\"Database stamped with revision: {revision}\")\n            return True\n        except Exception as e:\n            logger.error(f\"Failed to stamp database: {e}\")\n            return False\n    \n    def show_migration_info(self, revision: str) -> Dict[str, Any]:\n        \"\"\"Show detailed information about a migration.\"\"\"\n        try:\n            script_dir = ScriptDirectory.from_config(self.config)\n            revision_obj = script_dir.get_revision(revision)\n            \n            # Read migration file content\n            migration_content = \"\"\n            if revision_obj.path and Path(revision_obj.path).exists():\n                with open(revision_obj.path, 'r') as f:\n                    migration_content = f.read()\n            \n            return {\n                \"revision\": revision_obj.revision,\n                \"down_revision\": revision_obj.down_revision,\n                \"branch_labels\": revision_obj.branch_labels,\n                \"depends_on\": revision_obj.depends_on,\n                \"doc\": revision_obj.doc,\n                \"path\": revision_obj.path,\n                \"content\": migration_content\n            }\n        except Exception as e:\n            logger.error(f\"Failed to show migration info: {e}\")\n            return {\"error\": str(e)}\n    \n    def create_initial_migration(self) -> str:\n        \"\"\"Create initial migration with all tables.\"\"\"\n        return self.create_migration(\"Initial migration - create all tables\")\n    \n    def backup_before_migration(self, revision: str) -> bool:\n        \"\"\"Create backup before applying migration.\"\"\"\n        try:\n            from .backup import DatabaseBackup\n            \n            backup = DatabaseBackup()\n            backup_file = f\"backup_before_{revision}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql\"\n            \n            return backup.create_backup(backup_file)\n        except Exception as e:\n            logger.error(f\"Failed to create backup: {e}\")\n            return False\n    \n    def safe_migration(self, revision: str = \"head\", create_backup: bool = True) -> Dict[str, Any]:\n        \"\"\"Perform safe migration with backup and rollback capability.\"\"\"\n        result = {\n            \"success\": False,\n            \"backup_created\": False,\n            \"migration_applied\": False,\n            \"error\": None\n        }\n        \n        try:\n            # Create backup if requested\n            if create_backup:\n                if self.backup_before_migration(revision):\n                    result[\"backup_created\"] = True\n                    logger.info(\"Backup created before migration\")\n                else:\n                    logger.warning(\"Failed to create backup, continuing with migration\")\n            \n            # Get current revision for potential rollback\n            current_revision = self.get_current_revision()\n            \n            # Apply migration\n            if self.run_migrations(revision):\n                result[\"migration_applied\"] = True\n                result[\"success\"] = True\n                logger.info(f\"Migration to {revision} completed successfully\")\n            else:\n                result[\"error\"] = \"Migration failed\"\n                logger.error(\"Migration failed\")\n                \n                # Attempt rollback if migration failed\n                if current_revision:\n                    logger.info(f\"Attempting rollback to {current_revision}\")\n                    if self.rollback_migration(current_revision):\n                        logger.info(\"Rollback completed successfully\")\n                    else:\n                        logger.error(\"Rollback failed\")\n        \n        except Exception as e:\n            result[\"error\"] = str(e)\n            logger.error(f\"Safe migration failed: {e}\")\n        \n        return result\n    \n    def cleanup_migration_files(self, keep_last: int = 10) -> int:\n        \"\"\"Clean up old migration files, keeping the last N migrations.\"\"\"\n        try:\n            script_dir = ScriptDirectory.from_config(self.config)\n            all_revisions = list(script_dir.walk_revisions())\n            \n            if len(all_revisions) <= keep_last:\n                logger.info(\"No migration files to clean up\")\n                return 0\n            \n            # Get revisions to remove (oldest ones)\n            revisions_to_remove = all_revisions[keep_last:]\n            removed_count = 0\n            \n            for revision in revisions_to_remove:\n                if revision.path and Path(revision.path).exists():\n                    try:\n                        os.remove(revision.path)\n                        removed_count += 1\n                        logger.info(f\"Removed migration file: {revision.path}\")\n                    except Exception as e:\n                        logger.error(f\"Failed to remove migration file {revision.path}: {e}\")\n            \n            return removed_count\n        except Exception as e:\n            logger.error(f\"Failed to cleanup migration files: {e}\")\n            return 0\n    \n    def get_migration_statistics(self) -> Dict[str, Any]:\n        \"\"\"Get migration statistics.\"\"\"\n        try:\n            script_dir = ScriptDirectory.from_config(self.config)\n            all_revisions = list(script_dir.walk_revisions())\n            \n            current_revision = self.get_current_revision()\n            head_revision = script_dir.get_current_head()\n            \n            # Count applied migrations\n            applied_count = 0\n            if current_revision:\n                for revision in script_dir.iterate_revisions(current_revision, None):\n                    applied_count += 1\n            \n            return {\n                \"total_migrations\": len(all_revisions),\n                \"applied_migrations\": applied_count,\n                \"pending_migrations\": len(all_revisions) - applied_count,\n                \"current_revision\": current_revision,\n                \"head_revision\": head_revision,\n                \"is_up_to_date\": current_revision == head_revision\n            }\n        except Exception as e:\n            logger.error(f\"Failed to get migration statistics: {e}\")\n            return {\"error\": str(e)}"