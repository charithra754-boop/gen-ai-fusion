"""
Database migration management for FPO Economics Management System.
Handles schema creation, updates, and version tracking.
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from ..connection import get_db_connection
from ..config import DatabaseConfig

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database schema migrations."""
    
    def __init__(self, migrations_dir: Optional[str] = None):
        """
        Initialize migration manager.
        
        Args:
            migrations_dir: Directory containing migration files
        """
        self.migrations_dir = Path(migrations_dir) if migrations_dir else Path(__file__).parent
        self.schema_version_table = "schema_versions"
    
    def create_schema_version_table(self) -> None:
        """Create the schema version tracking table if it doesn't exist."""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.schema_version_table} (
            version VARCHAR(50) PRIMARY KEY,
            description TEXT,
            applied_at TIMESTAMPTZ DEFAULT NOW(),
            checksum VARCHAR(64)
        );
        """
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_table_sql)
                    conn.commit()
                    logger.info("Schema version table created/verified")
        except Exception as e:
            logger.error(f"Failed to create schema version table: {e}")
            raise
    
    def get_applied_migrations(self) -> List[str]:
        """
        Get list of applied migration versions.
        
        Returns:
            List[str]: List of applied migration versions
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT version FROM {self.schema_version_table} ORDER BY version")
                    return [row['version'] for row in cursor.fetchall()]
        except psycopg2.ProgrammingError:
            # Table doesn't exist yet
            return []
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            raise
    
    def get_pending_migrations(self) -> List[Dict[str, str]]:
        """
        Get list of pending migrations.
        
        Returns:
            List[Dict[str, str]]: List of pending migration info
        """
        applied_versions = set(self.get_applied_migrations())
        pending_migrations = []
        
        # Look for SQL migration files
        for migration_file in sorted(self.migrations_dir.glob("*.sql")):
            version = migration_file.stem
            if version not in applied_versions:
                pending_migrations.append({
                    'version': version,
                    'file_path': str(migration_file),
                    'description': self._extract_description(migration_file)
                })
        
        return pending_migrations
    
    def _extract_description(self, migration_file: Path) -> str:
        """
        Extract description from migration file comment.
        
        Args:
            migration_file: Path to migration file
            
        Returns:
            str: Migration description
        """
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('--'):
                    return first_line[2:].strip()
                return f"Migration {migration_file.stem}"
        except Exception:
            return f"Migration {migration_file.stem}"
    
    def _calculate_checksum(self, content: str) -> str:
        """
        Calculate checksum for migration content.
        
        Args:
            content: Migration file content
            
        Returns:
            str: SHA-256 checksum
        """
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def apply_migration(self, migration_info: Dict[str, str]) -> None:
        """
        Apply a single migration.
        
        Args:
            migration_info: Migration information dictionary
        """
        version = migration_info['version']
        file_path = migration_info['file_path']
        description = migration_info['description']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            checksum = self._calculate_checksum(migration_sql)
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Execute migration
                    cursor.execute(migration_sql)
                    
                    # Record migration
                    cursor.execute(
                        f"""
                        INSERT INTO {self.schema_version_table} 
                        (version, description, checksum) 
                        VALUES (%s, %s, %s)
                        """,
                        (version, description, checksum)
                    )
                    
                    conn.commit()
                    logger.info(f"Applied migration {version}: {description}")
                    
        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            raise
    
    def migrate(self) -> None:
        """Apply all pending migrations."""
        self.create_schema_version_table()
        pending_migrations = self.get_pending_migrations()
        
        if not pending_migrations:
            logger.info("No pending migrations")
            return
        
        logger.info(f"Applying {len(pending_migrations)} pending migrations")
        
        for migration_info in pending_migrations:
            self.apply_migration(migration_info)
        
        logger.info("All migrations applied successfully")
    
    def rollback_migration(self, version: str) -> None:
        """
        Rollback a specific migration (if rollback script exists).
        
        Args:
            version: Migration version to rollback
        """
        rollback_file = self.migrations_dir / f"{version}_rollback.sql"
        
        if not rollback_file.exists():
            raise ValueError(f"No rollback script found for migration {version}")
        
        try:
            with open(rollback_file, 'r', encoding='utf-8') as f:
                rollback_sql = f.read()
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Execute rollback
                    cursor.execute(rollback_sql)
                    
                    # Remove migration record
                    cursor.execute(
                        f"DELETE FROM {self.schema_version_table} WHERE version = %s",
                        (version,)
                    )
                    
                    conn.commit()
                    logger.info(f"Rolled back migration {version}")
                    
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            raise
    
    def get_migration_status(self) -> Dict[str, List[str]]:
        """
        Get current migration status.
        
        Returns:
            Dict[str, List[str]]: Migration status with applied and pending lists
        """
        applied = self.get_applied_migrations()
        pending = [m['version'] for m in self.get_pending_migrations()]
        
        return {
            'applied': applied,
            'pending': pending,
            'total_applied': len(applied),
            'total_pending': len(pending)
        }