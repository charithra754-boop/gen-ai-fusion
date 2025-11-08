"""
Database setup utilities for FPO Economics Management System.
Provides functions to initialize, migrate, and manage the database.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from .config import DatabaseConfig, load_database_config, get_test_database_config
from .connection import DatabaseConnectionManager, initialize_database
from .migrations.migration_manager import MigrationManager

logger = logging.getLogger(__name__)


def create_database(config: DatabaseConfig) -> None:
    """
    Create the database if it doesn't exist.
    
    Args:
        config: Database configuration
    """
    # Connect to postgres database to create the target database
    temp_config = DatabaseConfig(
        host=config.host,
        port=config.port,
        database='postgres',  # Connect to default postgres database
        username=config.username,
        password=config.password
    )
    
    try:
        conn = psycopg2.connect(
            host=temp_config.host,
            port=temp_config.port,
            database=temp_config.database,
            user=temp_config.username,
            password=temp_config.password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (config.database,)
            )
            
            if not cursor.fetchone():
                # Create database
                cursor.execute(f'CREATE DATABASE "{config.database}"')
                logger.info(f"Created database: {config.database}")
            else:
                logger.info(f"Database already exists: {config.database}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to create database {config.database}: {e}")
        raise


def drop_database(config: DatabaseConfig) -> None:
    """
    Drop the database if it exists.
    
    Args:
        config: Database configuration
    """
    # Connect to postgres database to drop the target database
    temp_config = DatabaseConfig(
        host=config.host,
        port=config.port,
        database='postgres',  # Connect to default postgres database
        username=config.username,
        password=config.password
    )
    
    try:
        conn = psycopg2.connect(
            host=temp_config.host,
            port=temp_config.port,
            database=temp_config.database,
            user=temp_config.username,
            password=temp_config.password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # Terminate existing connections to the database
            cursor.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
            """, (config.database,))
            
            # Drop database
            cursor.execute(f'DROP DATABASE IF EXISTS "{config.database}"')
            logger.info(f"Dropped database: {config.database}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to drop database {config.database}: {e}")
        raise


def setup_database(config: Optional[DatabaseConfig] = None, 
                  include_sample_data: bool = True) -> None:
    """
    Complete database setup including creation, migration, and sample data.
    
    Args:
        config: Database configuration. If None, loads from environment.
        include_sample_data: Whether to include sample data
    """
    if config is None:
        config = load_database_config()
    
    logger.info(f"Setting up database: {config.database}")
    
    # Create database
    create_database(config)
    
    # Initialize connection manager
    db_manager = DatabaseConnectionManager(config)
    db_manager.initialize_pool()
    
    try:
        # Test connection
        if not db_manager.test_connection():
            raise RuntimeError("Database connection test failed")
        
        # Run migrations
        migrations_dir = Path(__file__).parent / "migrations"
        migration_manager = MigrationManager(str(migrations_dir))
        migration_manager.migrate()
        
        logger.info("Database setup completed successfully")
        
    finally:
        db_manager.close_pool()


def reset_database(config: Optional[DatabaseConfig] = None,
                  include_sample_data: bool = True) -> None:
    """
    Reset database by dropping and recreating it.
    
    Args:
        config: Database configuration. If None, loads from environment.
        include_sample_data: Whether to include sample data
    """
    if config is None:
        config = load_database_config()
    
    logger.warning(f"Resetting database: {config.database}")
    
    # Drop and recreate database
    drop_database(config)
    setup_database(config, include_sample_data)


def setup_test_database() -> None:
    """Setup test database with sample data."""
    config = get_test_database_config()
    logger.info("Setting up test database")
    setup_database(config, include_sample_data=True)


def reset_test_database() -> None:
    """Reset test database."""
    config = get_test_database_config()
    logger.info("Resetting test database")
    reset_database(config, include_sample_data=True)


def check_database_status(config: Optional[DatabaseConfig] = None) -> dict:
    """
    Check database status and migration information.
    
    Args:
        config: Database configuration. If None, loads from environment.
        
    Returns:
        dict: Database status information
    """
    if config is None:
        config = load_database_config()
    
    db_manager = DatabaseConnectionManager(config)
    
    try:
        db_manager.initialize_pool()
        
        # Test connection
        connection_ok = db_manager.test_connection()
        
        if not connection_ok:
            return {
                'database': config.database,
                'connection': False,
                'error': 'Connection failed'
            }
        
        # Get migration status
        migrations_dir = Path(__file__).parent / "migrations"
        migration_manager = MigrationManager(str(migrations_dir))
        migration_status = migration_manager.get_migration_status()
        
        return {
            'database': config.database,
            'connection': True,
            'migrations': migration_status
        }
        
    except Exception as e:
        return {
            'database': config.database,
            'connection': False,
            'error': str(e)
        }
    finally:
        db_manager.close_pool()


if __name__ == "__main__":
    """Command line interface for database setup."""
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 2:
        print("Usage: python setup.py [setup|reset|test-setup|test-reset|status]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "setup":
            setup_database()
        elif command == "reset":
            reset_database()
        elif command == "test-setup":
            setup_test_database()
        elif command == "test-reset":
            reset_test_database()
        elif command == "status":
            status = check_database_status()
            print(f"Database: {status['database']}")
            print(f"Connection: {status['connection']}")
            if 'migrations' in status:
                print(f"Applied migrations: {status['migrations']['total_applied']}")
                print(f"Pending migrations: {status['migrations']['total_pending']}")
            if 'error' in status:
                print(f"Error: {status['error']}")
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)