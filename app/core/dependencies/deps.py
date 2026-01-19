"""
FastAPI dependency injection for application services and connections.

This module provides centralized dependency definitions for injecting
database sessions and business services into FastAPI route
handlers.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_getter)]
"""
Type alias for SQLAlchemy async session dependency injection.

Provides database sessions with automatic connection pooling, transaction
management, and proper cleanup. Each request receives a fresh session that
is automatically closed when the request completes.

Attributes:
    Type Parameters:
        AsyncSession: SQLAlchemy asynchronous session instance.

Usage:
    ```python
    @router.get("/users/{user_id}")
    async def get_user(user_id: int, session: SessionDep):
        user = await session.get(User, user_id)
        return user
    ```
"""
