"""
Database connection and session management for asynchronous SQLAlchemy.

This module provides a centralized database helper class that manages
asynchronous database engine creation, connection pooling, and session handling
for the application.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)

from app.core.config import settings


class DatabaseHelper:
    """
    A database connections helper.

    A class for managing asynchronous database connections and sessions.
    This class encapsulates the creation and management of SQLAlchemy async engine
    and session factory with configurable connection pooling and logging.

    Attributes:
        engine (AsyncEngine): The SQLAlchemy async engine instance.
        session_factory (async_sessionmaker[AsyncSession]):
            Factory for creating async sessions.
    """

    def __init__(
            self,
            url: str,
            echo: bool,
            echo_pool: bool,
            pool_size: int = 5,
            max_overflow: int = 10,
    ):
        """
        Initialize the DatabaseHelper with connection parameters.

        Args:
            url: Database connection URL (e.g., "postgresql+asyncpg://user:pass@host/db").
            echo: If True, log all SQL statements and their parameters.
            echo_pool: If True, log connection pool events.
            pool_size: Number of connections to keep open in the pool (default: 5).
            max_overflow: Maximum number of connections that can be created beyond pool_size
                         during peak usage (default: 10).


        Note:
            - For PostgreSQL with async support, use "postgresql+asyncpg://" driver.
            - Connection pooling helps manage database connections efficiently.
            - Set echo=True only in development for debugging SQL queries.
        """
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        """
        Close all database connections and dispose of the engine.

        This method should be called during application shutdown to properly
        clean up database connections and release resources.

        """

        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for acquiring database sessions.

        Yields an async database session that is automatically closed when the
        context exits. This is the recommended way to get database sessions
        as it ensures proper cleanup.

        Yields:
            AsyncSession: An SQLAlchemy async session for database operations.
        """
        async with self.session_factory() as session:
            yield session


db_helper = DatabaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.echo_pool,
    max_overflow=settings.db.max_overflow,
)