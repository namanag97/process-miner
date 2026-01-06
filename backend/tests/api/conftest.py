"""
Pytest configuration and shared fixtures for API tests.

Provides:
- AsyncClient for testing FastAPI endpoints
- Database session with test isolation
- Pre-seeded test data (user, workspace, project, datasets)
"""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.shared.database import Base
from src.platform.infrastructure.database import async_session_maker
from src.platform.models import Organization, User, Workspace, WorkspaceMember


# =============================================================================
# Event Loop
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

# Test database URL - in-memory SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
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
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


# =============================================================================
# HTTP Client Fixture
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    
    # Override the database dependency to use test session
    from src.platform.infrastructure.database import get_session
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as ac:
        yield ac
    
    # Clean up overrides
    app.dependency_overrides.clear()


# =============================================================================
# Authenticated Client
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def auth_client(client: AsyncClient, seeded_user: User) -> AsyncClient:
    """HTTP client with auth headers for the seeded user."""
    # In dev mode with AUTH_ENABLED=false, just add a placeholder header
    # The auth system will use the mock user
    client.headers["Authorization"] = "Bearer test-token"
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
    
    # Add user as workspace owner
    membership = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=seeded_user.id,
        role="owner",
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(workspace)
    return workspace


# =============================================================================
# Project and Dataset Fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def seeded_project(
    db_session: AsyncSession,
    seeded_workspace: Workspace,
) -> Any:
    """Create a test project."""
    from src.platform.models import Project
    
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
async def seeded_dataset_pending(
    db_session: AsyncSession,
    seeded_project: Any,
) -> Any:
    """Create a test dataset in PENDING status."""
    from src.features.process_mining.models import Dataset, DatasetStatus
    
    dataset = Dataset(
        id=str(uuid4()),
        project_id=seeded_project.id,
        name="Test Dataset (Pending)",
        source_format="csv",
        original_filename="test.csv",
        status=DatasetStatus.PENDING.value,
    )
    db_session.add(dataset)
    await db_session.commit()
    await db_session.refresh(dataset)
    return dataset


@pytest_asyncio.fixture(scope="function")
async def seeded_dataset_ready(
    db_session: AsyncSession,
    seeded_project: Any,
) -> Any:
    """Create a test dataset in READY status with sample data."""
    import json
    from src.features.process_mining.models import Dataset, DatasetStatus, ProcessCase, ProcessEvent
    
    dataset = Dataset(
        id=str(uuid4()),
        project_id=seeded_project.id,
        name="Test Dataset (Ready)",
        source_format="csv",
        original_filename="test.csv",
        status=DatasetStatus.READY.value,
        total_cases=3,
        total_events=9,
        total_activities=3,
        activities_json=json.dumps(["Start", "Process", "End"]),
        case_id_column="case_id",
        activity_column="activity",
        timestamp_column="timestamp",
    )
    db_session.add(dataset)
    await db_session.flush()
    
    # Add sample cases and events
    activities = ["Start", "Process", "End"]
    for i in range(3):
        case = ProcessCase(
            id=str(uuid4()),
            dataset_id=dataset.id,
            case_id=f"case_{i+1}",
        )
        db_session.add(case)
        await db_session.flush()
        
        for j, activity in enumerate(activities):
            event = ProcessEvent(
                id=str(uuid4()),
                case_ref_id=case.id,
                activity=activity,
                timestamp=datetime(2024, 1, 1, 10, j, 0, tzinfo=timezone.utc),
            )
            db_session.add(event)
    
    await db_session.commit()
    await db_session.refresh(dataset)
    return dataset


# =============================================================================
# Process Model Fixture
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def seeded_process_model(
    db_session: AsyncSession,
    seeded_dataset_ready: Any,
) -> Any:
    """Create a test process model."""
    from src.features.process_mining.models import ProcessModel
    
    model = ProcessModel(
        id=str(uuid4()),
        dataset_id=seeded_dataset_ready.id,
        name="Test Model",
        algorithm="inductive",
        model_format="petri_net",
    )
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)
    return model


# =============================================================================
# Sample CSV Data
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
