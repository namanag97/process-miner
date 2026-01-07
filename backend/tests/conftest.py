"""
Pytest configuration and shared fixtures for all tests.

This is the ROOT conftest.py that provides fixtures inherited by all test subdirectories.

Test Categories (use markers):
- @pytest.mark.unit: Fast tests with no I/O
- @pytest.mark.integration: Tests requiring database or external services
- @pytest.mark.e2e: Full end-to-end workflow tests
- @pytest.mark.slow: Tests taking >5s
"""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.infra.models import Organization, User, Workspace, WorkspaceMember
from src.shared.database import Base

# =============================================================================
# Pytest Configuration
# =============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no I/O)")
    config.addinivalue_line("markers", "integration: Integration tests (DB, services)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (full workflow)")
    config.addinivalue_line("markers", "slow: Slow tests (>5s)")


# =============================================================================
# Event Loop (Session-scoped for all async tests)
# =============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Database Fixtures
# =============================================================================

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine with in-memory SQLite."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with automatic rollback."""
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()


# =============================================================================
# HTTP Client Fixtures
# =============================================================================


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing with DB override."""
    from src.infra.health.router import mark_startup_complete
    from src.infra.infrastructure.database import get_session

    # Mark startup complete so health probes pass
    mark_startup_complete()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        # NOTE: Do NOT set Content-Type here - httpx sets it automatically
        # based on the request type (JSON, multipart form, etc.)
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_client(client: AsyncClient, seeded_user: User) -> AsyncClient:
    """HTTP client with auth headers for the seeded user."""
    # For tests, we set a header that the mock auth will recognize
    # In dev mode, auth can be bypassed with email query param
    client.headers["Authorization"] = "Bearer test-token"
    client.headers["X-Test-User-Email"] = seeded_user.email
    return client


# =============================================================================
# Seeded Data Fixtures
# =============================================================================


@pytest_asyncio.fixture(scope="function")
async def seeded_org(db_session: AsyncSession) -> Organization:
    """Create a test organization."""
    org = Organization(
        id=str(uuid4()),
        name="Test Organization",
        slug="test-org",
        plan="free",
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest_asyncio.fixture(scope="function")
async def seeded_user(db_session: AsyncSession, seeded_org: Organization) -> User:
    """Create a test user."""
    user = User(
        id=str(uuid4()),
        org_id=seeded_org.id,
        email="test@example.com",
        name="Test User",
        role="admin",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def seeded_workspace(
    db_session: AsyncSession,
    seeded_org: Organization,
    seeded_user: User,
) -> Workspace:
    """Create a test workspace with user membership."""
    workspace = Workspace(
        id=str(uuid4()),
        org_id=seeded_org.id,
        name="Test Workspace",
        description="Workspace for testing",
    )
    db_session.add(workspace)
    await db_session.flush()

    membership = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=seeded_user.id,
        role="owner",
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(workspace)
    return workspace


@pytest_asyncio.fixture(scope="function")
async def seeded_project(db_session: AsyncSession, seeded_workspace: Workspace) -> Any:
    """Create a test project."""
    from src.infra.models import Project

    project = Project(
        id=str(uuid4()),
        workspace_id=seeded_workspace.id,
        name="Test Project",
        description="Project for testing",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture(scope="function")
async def seeded_dataset_ready(db_session: AsyncSession, seeded_project: Any) -> Any:
    """Create a test dataset in READY status with sample data."""
    import json

    from src.features.process_mining.models import Dataset, DatasetStatus, ProcessCase, ProcessEvent

    dataset = Dataset(
        id=str(uuid4()),
        project_id=seeded_project.id,
        name="Test Dataset (Ready)",
        source_format="csv",
        source_file="test.csv",
        status=DatasetStatus.READY.value,
        total_cases=3,
        total_events=9,
        total_activities=3,
        activities_json=json.dumps(["Start", "Process", "End"]),
    )
    db_session.add(dataset)
    await db_session.flush()

    activities = ["Start", "Process", "End"]
    for i in range(3):
        case = ProcessCase(
            id=str(uuid4()),
            dataset_id=dataset.id,
            case_id=f"case_{i + 1}",
        )
        db_session.add(case)
        await db_session.flush()

        for j, activity in enumerate(activities):
            event = ProcessEvent(
                id=str(uuid4()),
                dataset_id=dataset.id,
                case_ref_id=case.id,
                activity=activity,
                timestamp=datetime(2024, 1, 1, 10, j, 0, tzinfo=timezone.utc),
            )
            db_session.add(event)

    await db_session.commit()
    await db_session.refresh(dataset)
    return dataset


# =============================================================================
# Sample Test Data
# =============================================================================

SAMPLE_CSV_CONTENT = """\
case_id,activity,timestamp,resource
1,Start,2024-01-01 10:00:00,Alice
1,Process,2024-01-01 10:30:00,Bob
1,End,2024-01-01 11:00:00,Alice
2,Start,2024-01-01 10:00:00,Bob
2,Process,2024-01-01 10:45:00,Alice
2,End,2024-01-01 11:30:00,Bob
3,Start,2024-01-01 10:00:00,Alice
3,Review,2024-01-01 10:20:00,Charlie
3,Process,2024-01-01 10:50:00,Bob
3,End,2024-01-01 11:20:00,Alice
"""


@pytest.fixture
def sample_csv_bytes() -> bytes:
    """Return sample CSV content as bytes."""
    return SAMPLE_CSV_CONTENT.encode("utf-8")
