import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.db_helper import db_helper
from app.core.models.base import Base
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Creates an instance of the default event loop for the test session.

    Required for running asynchronous tests and managing the lifecycle
    of async resources.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Creates a session-scoped SQLAlchemy AsyncEngine using an in-memory SQLite database.

    Initializes the database schema by creating all tables defined in the
    Base metadata before yielding the engine.
    """
    engine: AsyncEngine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", echo=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a function-scoped AsyncSession for database operations.

    Each test runs within a manual transaction that is rolled back
    after the test completes, ensuring a clean state for every test.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()

    async_session_factory = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    session: AsyncSession = async_session_factory()
    yield session

    await transaction.rollback()
    await connection.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Configures and provides a FastAPI TestClient instance.

    The client is initialized with the API base URL prefix from settings
    and handles lifespan events automatically.
    """
    base_url_prefix: str = (
        settings.api.prefix + settings.api.v1.prefix + settings.api.v1.deribit
    )
    with TestClient(app, base_url=f"http://testserver{base_url_prefix}") as c:
        yield c


@pytest.fixture(autouse=True)
def override_db(test_session: AsyncSession) -> Generator[None, None, None]:
    """
    Automatically overrides the production database session dependency.

    Uses FastAPI's dependency_overrides to inject the test session
    into the application's routes during testing.
    """
    app.dependency_overrides[db_helper.session_getter] = lambda: test_session
    yield
    app.dependency_overrides.clear()
