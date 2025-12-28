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


@pytest.fixture
def sample_csv_with_multiple_variants() -> bytes:
    """Sample CSV with multiple distinct process variants for testing.
    
    Variants:
    1. Happy path: Register -> Examine Casually -> Check -> Decide -> Pay (3 cases)
    2. Rejection path: Register -> Examine Thoroughly -> Check -> Decide -> Reject (2 cases)
    3. Reinitiation path: Register -> Examine -> Check -> Decide -> Reinitiate -> ... -> Pay (1 case)
    """
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
3,Register Request,2023-01-02 08:00:00,Mike
3,Examine Casually,2023-01-02 08:30:00,John
3,Check Ticket,2023-01-02 09:00:00,Sarah
3,Decide,2023-01-02 10:00:00,John
3,Pay Compensation,2023-01-02 11:00:00,Mike
4,Register Request,2023-01-02 09:00:00,John
4,Examine Casually,2023-01-02 09:45:00,Mike
4,Check Ticket,2023-01-02 10:30:00,John
4,Decide,2023-01-02 11:30:00,Sarah
4,Reinitiate Request,2023-01-02 12:00:00,John
4,Examine Thoroughly,2023-01-02 13:00:00,Sarah
4,Check Ticket,2023-01-02 14:00:00,Mike
4,Decide,2023-01-02 15:00:00,John
4,Pay Compensation,2023-01-02 16:00:00,Sarah
5,Register Request,2023-01-03 08:30:00,Sarah
5,Examine Casually,2023-01-03 09:00:00,Mike
5,Check Ticket,2023-01-03 09:30:00,John
5,Decide,2023-01-03 10:00:00,Sarah
5,Pay Compensation,2023-01-03 10:30:00,Mike
6,Register Request,2023-01-03 11:00:00,John
6,Examine Thoroughly,2023-01-03 12:00:00,Sarah
6,Check Ticket,2023-01-03 13:00:00,Mike
6,Decide,2023-01-03 14:00:00,John
6,Reject Request,2023-01-03 15:00:00,Sarah
"""


@pytest.fixture
def sample_csv_with_bottleneck() -> bytes:
    """Sample CSV with clear bottleneck activity (Wait for Approval has long duration).
    
    This data has a clear bottleneck at "Wait for Approval" activity
    with durations of 8+ hours to test bottleneck detection.
    """
    return b"""case:concept:name,concept:name,time:timestamp,org:resource
1,Submit Request,2023-01-01 09:00:00,John
1,Initial Review,2023-01-01 09:15:00,Sarah
1,Wait for Approval,2023-01-01 09:30:00,System
1,Final Approval,2023-01-01 18:00:00,Manager
1,Complete,2023-01-01 18:15:00,John
2,Submit Request,2023-01-01 10:00:00,Sarah
2,Initial Review,2023-01-01 10:20:00,Mike
2,Wait for Approval,2023-01-01 10:30:00,System
2,Final Approval,2023-01-01 19:00:00,Manager
2,Complete,2023-01-01 19:10:00,Sarah
3,Submit Request,2023-01-02 08:00:00,Mike
3,Initial Review,2023-01-02 08:10:00,John
3,Wait for Approval,2023-01-02 08:20:00,System
3,Final Approval,2023-01-02 17:30:00,Manager
3,Complete,2023-01-02 17:45:00,Mike
"""


@pytest.fixture
async def uploaded_log_id(client: AsyncClient, sample_csv_with_multiple_variants: bytes) -> str:
    """Pre-upload a log and return its ID for dependent tests."""
    response = await client.post(
        "/api/v1/logs/upload",
        files={"file": ("test_variants.csv", sample_csv_with_multiple_variants, "text/csv")},
    )
    assert response.status_code == 200
    return response.json()["id"]


@pytest.fixture
async def discovered_model_id(client: AsyncClient, uploaded_log_id: str) -> str:
    """Discover a model from the uploaded log and return its ID."""
    response = await client.post(
        "/api/v1/discovery/discover",
        json={
            "log_id": uploaded_log_id,
            "miner_type": "inductive",
            "model_name": "Test Model"
        }
    )
    assert response.status_code == 200
    return response.json()["model_id"]
