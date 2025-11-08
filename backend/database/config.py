"""
Database configuration management for FPO Economics Management System.
Handles database connection parameters and environment-specific settings.
"""

import os
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class DatabaseConfig:
    """Database configuration parameters."""
    host: str
    port: int
    database: str
    username: str
    password: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    @property
    def connection_url(self) -> str:
        """Generate PostgreSQL connection URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_connection_url(self) -> str:
        """Generate async PostgreSQL connection URL."""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


def load_database_config() -> DatabaseConfig:
    """
    Load database configuration from environment variables.
    
    Returns:
        DatabaseConfig: Configured database parameters
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Check for DATABASE_URL first (common in cloud deployments)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        parsed = urlparse(database_url)
        return DatabaseConfig(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/') if parsed.path else 'fpo_economics',
            username=parsed.username or 'postgres',
            password=parsed.password or '',
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30')),
            pool_recycle=int(os.getenv('DB_POOL_RECYCLE', '3600')),
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
        )
    
    # Fall back to individual environment variables
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return DatabaseConfig(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'fpo_economics'),
        username=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
        max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
        pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30')),
        pool_recycle=int(os.getenv('DB_POOL_RECYCLE', '3600')),
        echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
    )


def get_test_database_config() -> DatabaseConfig:
    """
    Get database configuration for testing environment.
    
    Returns:
        DatabaseConfig: Test database configuration
    """
    config = load_database_config()
    # Use separate test database
    config.database = f"{config.database}_test"
    config.echo = True  # Enable SQL logging for tests
    return config