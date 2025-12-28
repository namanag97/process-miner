"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.main import app
from src.infrastructure.persistence.database import Base, get_session


# Test database URL (in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with session_maker() as session:
        yield session


@pytest.fixture
async def client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override."""
    
    async def override_get_session():
        yield test_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_csv_content() -> bytes:
    """Sample CSV content for testing."""
    return b"""case:concept:name,concept:name,time:timestamp,org:resource
1,Register Request,2023-01-01 09:00:00,John
1,Examine Casually,2023-01-01 09:30:00,Sarah
1,Check Ticket,2023-01-01 10:00:00,Mike
1,Decide,2023-01-01 11:00:00,Sarah
1,Pay Compensation,2023-01-01 12:00:00,John
2,Register Request,2023-01-01 09:15:00,Sarah
2,Examine Thoroughly,2023-01-01 10:00:00,Sarah
2,Check Ticket,2023-01-01 11:00:00,John
2,Decide,2023-01-01 12:00:00,Mike
2,Reject Request,2023-01-01 13:00:00,Sarah
"""
