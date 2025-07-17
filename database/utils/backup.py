"""
Database backup utilities for Sistema Mayra.
"""
import os
import subprocess
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import gzip
import shutil

logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Database backup manager with compression and rotation."""
    
    def __init__(self, backup_dir: str = "backups", 
                 database_url: Optional[str] = None):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.database_url = database_url
        
        # Parse database URL for pg_dump
        if database_url:
            self._parse_database_url(database_url)
    
    def _parse_database_url(self, database_url: str):
        """Parse database URL for connection parameters."""
        from urllib.parse import urlparse
        
        parsed = urlparse(database_url)
        
        self.db_host = parsed.hostname
        self.db_port = parsed.port or 5432
        self.db_name = parsed.path[1:]  # Remove leading slash
        self.db_user = parsed.username
        self.db_password = parsed.password
    
    def create_backup(self, filename: Optional[str] = None, 
                     compress: bool = True, 
                     schema_only: bool = False,
                     data_only: bool = False) -> str:
        """Create database backup."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backup_{timestamp}.sql"
        
        if compress and not filename.endswith('.gz'):
            filename += '.gz'
        
        backup_path = self.backup_dir / filename
        
        try:
            # Build pg_dump command
            cmd = [
                'pg_dump',
                '-h', self.db_host,
                '-p', str(self.db_port),
                '-U', self.db_user,
                '-d', self.db_name,
                '--verbose',
                '--no-password'
            ]
            
            if schema_only:
                cmd.append('--schema-only')
            elif data_only:
                cmd.append('--data-only')
            
            # Set environment variables
            env = os.environ.copy()
            if self.db_password:
                env['PGPASSWORD'] = self.db_password
            
            # Execute backup
            logger.info(f"Creating backup: {backup_path}")
            
            if compress:
                # Stream directly to gzip
                with gzip.open(backup_path, 'wt') as f:
                    process = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        env=env,
                        text=True,
                        check=True
                    )
            else:
                # Write to file directly
                with open(backup_path, 'w') as f:
                    process = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        env=env,
                        text=True,
                        check=True
                    )
            
            # Check for errors
            if process.returncode != 0:
                logger.error(f"Backup failed: {process.stderr}")
                return None
            
            # Log success
            file_size = backup_path.stat().st_size
            logger.info(f"Backup created successfully: {backup_path} ({file_size} bytes)")
            
            return str(backup_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup command failed: {e}")
            # Clean up failed backup file
            if backup_path.exists():
                backup_path.unlink()
            return None
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            if backup_path.exists():
                backup_path.unlink()
            return None
    
    def restore_backup(self, backup_file: str, 
                      drop_database: bool = False,
                      create_database: bool = False) -> bool:
        """Restore database from backup."""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Drop database if requested
            if drop_database:
                if not self._drop_database():
                    return False
            
            # Create database if requested
            if create_database:
                if not self._create_database():
                    return False
            
            # Build psql command
            cmd = [
                'psql',
                '-h', self.db_host,
                '-p', str(self.db_port),
                '-U', self.db_user,
                '-d', self.db_name,
                '--quiet',
                '--no-password'
            ]
            
            # Set environment variables
            env = os.environ.copy()
            if self.db_password:
                env['PGPASSWORD'] = self.db_password
            
            # Execute restore
            logger.info(f"Restoring backup: {backup_path}")
            
            if backup_path.suffix == '.gz':
                # Decompress and restore
                with gzip.open(backup_path, 'rt') as f:
                    process = subprocess.run(
                        cmd,
                        stdin=f,
                        stderr=subprocess.PIPE,
                        env=env,
                        text=True,
                        check=True
                    )
            else:
                # Restore directly
                with open(backup_path, 'r') as f:
                    process = subprocess.run(
                        cmd,
                        stdin=f,
                        stderr=subprocess.PIPE,
                        env=env,
                        text=True,
                        check=True
                    )
            
            # Check for errors
            if process.returncode != 0:
                logger.error(f"Restore failed: {process.stderr}")
                return False
            
            logger.info("Restore completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Restore command failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def _drop_database(self) -> bool:
        """Drop database."""
        try:
            cmd = [
                'dropdb',
                '-h', self.db_host,
                '-p', str(self.db_port),
                '-U', self.db_user,
                '--if-exists',
                self.db_name
            ]
            
            env = os.environ.copy()
            if self.db_password:
                env['PGPASSWORD'] = self.db_password
            
            process = subprocess.run(
                cmd,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                check=True
            )
            
            logger.info(f"Database {self.db_name} dropped")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to drop database: {e}")
            return False
    
    def _create_database(self) -> bool:
        """Create database."""
        try:
            cmd = [
                'createdb',
                '-h', self.db_host,
                '-p', str(self.db_port),
                '-U', self.db_user,
                self.db_name
            ]
            
            env = os.environ.copy()
            if self.db_password:
                env['PGPASSWORD'] = self.db_password
            
            process = subprocess.run(
                cmd,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                check=True
            )
            
            logger.info(f"Database {self.db_name} created")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create database: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups."""
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*.sql*"):
            try:
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size": stat.st_size,
                    "size_pretty": self._format_size(stat.st_size),
                    "created": datetime.fromtimestamp(stat.st_ctime),
                    "compressed": backup_file.suffix == '.gz'
                })
            except Exception as e:
                logger.warning(f"Error reading backup file {backup_file}: {e}")
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return backups
    
    def cleanup_old_backups(self, keep_days: int = 30, keep_count: int = 10) -> int:
        """Clean up old backups."""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed_count = 0
        
        # Keep at least keep_count backups, regardless of age
        for backup in backups[keep_count:]:
            try:
                # Remove if older than keep_days
                if backup['created'] < cutoff_date:
                    Path(backup['path']).unlink()
                    removed_count += 1
                    logger.info(f"Removed old backup: {backup['filename']}")
            except Exception as e:
                logger.error(f"Failed to remove backup {backup['filename']}: {e}")
        
        return removed_count
    
    def verify_backup(self, backup_file: str) -> Dict[str, Any]:
        """Verify backup integrity."""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            return {"valid": False, "error": "Backup file not found"}
        
        try:
            # Check if file is compressed
            if backup_path.suffix == '.gz':
                # Test gzip integrity
                with gzip.open(backup_path, 'rt') as f:
                    # Read first few lines to check if it's valid SQL
                    lines = [f.readline() for _ in range(5)]
            else:
                with open(backup_path, 'r') as f:
                    lines = [f.readline() for _ in range(5)]
            
            # Basic validation - check for SQL dump header
            content = ''.join(lines).lower()
            
            is_valid = (
                'postgresql database dump' in content or
                'create' in content or
                'insert' in content or
                'copy' in content
            )
            
            if is_valid:
                file_size = backup_path.stat().st_size
                return {
                    "valid": True,
                    "size": file_size,
                    "size_pretty": self._format_size(file_size),
                    "compressed": backup_path.suffix == '.gz',
                    "preview": lines[:3]
                }
            else:
                return {"valid": False, "error": "Invalid SQL dump format"}
                
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def create_scheduled_backup(self, schedule: str = "daily") -> str:
        """Create backup with scheduled naming."""
        timestamp = datetime.now()
        
        if schedule == "daily":
            filename = f"daily_backup_{timestamp.strftime('%Y%m%d')}.sql.gz"
        elif schedule == "weekly":
            week_num = timestamp.isocalendar()[1]
            filename = f"weekly_backup_{timestamp.year}_W{week_num:02d}.sql.gz"
        elif schedule == "monthly":
            filename = f"monthly_backup_{timestamp.strftime('%Y%m')}.sql.gz"
        else:
            filename = f"backup_{timestamp.strftime('%Y%m%d_%H%M%S')}.sql.gz"
        
        return self.create_backup(filename, compress=True)
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics."""
        backups = self.list_backups()
        
        if not backups:
            return {"total_backups": 0, "total_size": 0}
        
        total_size = sum(b['size'] for b in backups)
        oldest_backup = min(b['created'] for b in backups)
        newest_backup = max(b['created'] for b in backups)
        
        # Calculate average size
        avg_size = total_size / len(backups)
        
        # Count by type
        compressed_count = sum(1 for b in backups if b['compressed'])
        
        return {
            "total_backups": len(backups),
            "total_size": total_size,
            "total_size_pretty": self._format_size(total_size),
            "average_size": avg_size,
            "average_size_pretty": self._format_size(avg_size),
            "oldest_backup": oldest_backup,
            "newest_backup": newest_backup,
            "compressed_count": compressed_count,
            "uncompressed_count": len(backups) - compressed_count
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def compress_backup(self, backup_file: str) -> bool:
        """Compress existing backup."""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        if backup_path.suffix == '.gz':
            logger.info("Backup is already compressed")
            return True
        
        try:
            compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
            
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file
            backup_path.unlink()
            
            logger.info(f"Backup compressed: {compressed_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to compress backup: {e}")
            return False
    
    def decompress_backup(self, backup_file: str) -> bool:
        """Decompress backup."""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        if backup_path.suffix != '.gz':
            logger.info("Backup is not compressed")
            return True
        
        try:
            decompressed_path = backup_path.with_suffix('')
            
            with gzip.open(backup_path, 'rb') as f_in:
                with open(decompressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove compressed file
            backup_path.unlink()
            
            logger.info(f"Backup decompressed: {decompressed_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to decompress backup: {e}")
            return False