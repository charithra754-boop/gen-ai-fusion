"""
Database connection management with connection pooling for FPO Economics Management System.
Provides both synchronous and asynchronous database connections.
"""

import logging
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator, Optional
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
import asyncpg
from .config import DatabaseConfig, load_database_config

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Manages database connections with connection pooling."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database connection manager.
        
        Args:
            config: Database configuration. If None, loads from environment.
        """
        self.config = config or load_database_config()
        self._connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._async_pool: Optional[asyncpg.Pool] = None
        
    def initialize_pool(self) -> None:
        """Initialize the connection pool."""
        try:
            self._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=self.config.pool_size,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                cursor_factory=RealDictCursor
            )
            logger.info(f"Database connection pool initialized with {self.config.pool_size} connections")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    async def initialize_async_pool(self) -> None:
        """Initialize the async connection pool."""
        try:
            self._async_pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=1,
                max_size=self.config.pool_size,
                command_timeout=self.config.pool_timeout
            )
            logger.info(f"Async database connection pool initialized with {self.config.pool_size} connections")
        except Exception as e:
            logger.error(f"Failed to initialize async database connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """
        Get a database connection from the pool.
        
        Yields:
            psycopg2.extensions.connection: Database connection
            
        Raises:
            RuntimeError: If connection pool is not initialized
        """
        if not self._connection_pool:
            raise RuntimeError("Connection pool not initialized. Call initialize_pool() first.")
        
        connection = None
        try:
            connection = self._connection_pool.getconn()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                self._connection_pool.putconn(connection)
    
    @asynccontextmanager
    async def get_async_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Get an async database connection from the pool.
        
        Yields:
            asyncpg.Connection: Async database connection
            
        Raises:
            RuntimeError: If async connection pool is not initialized
        """
        if not self._async_pool:
            raise RuntimeError("Async connection pool not initialized. Call initialize_async_pool() first.")
        
        async with self._async_pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"Async database connection error: {e}")
                raise
    
    def close_pool(self) -> None:
        """Close the connection pool."""
        if self._connection_pool:
            self._connection_pool.closeall()
            self._connection_pool = None
            logger.info("Database connection pool closed")
    
    async def close_async_pool(self) -> None:
        """Close the async connection pool."""
        if self._async_pool:
            await self._async_pool.close()
            self._async_pool = None
            logger.info("Async database connection pool closed")
    
    def test_connection(self) -> bool:
        """
        Test database connectivity.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    async def test_async_connection(self) -> bool:
        """
        Test async database connectivity.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            async with self.get_async_connection() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"Async database connection test failed: {e}")
            return False


# Global database manager instance
_db_manager: Optional[DatabaseConnectionManager] = None


def get_database_manager() -> DatabaseConnectionManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseConnectionManager: Global database manager
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseConnectionManager()
    return _db_manager


def initialize_database() -> None:
    """Initialize the global database connection pool."""
    manager = get_database_manager()
    manager.initialize_pool()


async def initialize_async_database() -> None:
    """Initialize the global async database connection pool."""
    manager = get_database_manager()
    await manager.initialize_async_pool()


def close_database() -> None:
    """Close the global database connection pool."""
    global _db_manager
    if _db_manager:
        _db_manager.close_pool()
        _db_manager = None


async def close_async_database() -> None:
    """Close the global async database connection pool."""
    global _db_manager
    if _db_manager:
        await _db_manager.close_async_pool()
        _db_manager = None


@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Convenience function to get a database connection.
    
    Yields:
        psycopg2.extensions.connection: Database connection
    """
    manager = get_database_manager()
    with manager.get_connection() as conn:
        yield conn


@asynccontextmanager
async def get_async_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Convenience function to get an async database connection.
    
    Yields:
        asyncpg.Connection: Async database connection
    """
    manager = get_database_manager()
    async with manager.get_async_connection() as conn:
        yield conn