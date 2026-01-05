"""Pytest configuration and fixtures."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.main import app
from src.shared.database import Base
from src.platform.models import Organization, Project, User, Workspace


@pytest.fixture
def test_db_path():
    """Create a temporary SQLite database file."""
    import os
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
async def test_engine(test_db_path):
    """Create test database engine using file-based SQLite."""
    # Use file path instead of :memory: so DuckDB can attach to it
    database_url = f"sqlite+aiosqlite:///{test_db_path}"

    # Patch event_log_loader to use this path
    from src.features.process_mining.services.loader import event_log_loader

    event_log_loader._sqlite_path = test_db_path

    engine = create_async_engine(
        database_url,
        echo=False,
    )

    async with engine.begin() as conn:
        # Use WAL mode for better concurrency and avoiding file handle invalidation
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    # Create a session without outer transaction wrapper so commits are persisted
    # This allows DuckDB (running in separate connection) to see the data
    session_maker = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_maker() as session:
        yield session

    # Cleanup is handled by clear_db fixture


@pytest.fixture(autouse=True)
async def clear_db(test_session: AsyncSession):
    """Clear all data between tests."""
    yield
    # Truncate all tables in dependency order
    from sqlalchemy import text

    # Disable foreign key checks for truncation
    await test_session.execute(text("PRAGMA foreign_keys = OFF"))

    # List of tables to clear
    tables = [
        "recommendations",
        "simulations",
        "predictions",
        "process_cases",
        "process_events",
        "datasets",
        "async_jobs",
        "projects",
        "workspace_members",
        "users",
        "workspaces",
        "organizations",
    ]

    for table in tables:
        try:
            await test_session.execute(text(f"DELETE FROM {table}"))
        except Exception:
            pass

    await test_session.execute(text("PRAGMA foreign_keys = ON"))
    await test_session.commit()


@pytest.fixture
async def client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override."""
    from src.api.dependencies import get_db

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

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
async def default_project(test_session: AsyncSession) -> str:
    """Create a default project for testing with full hierarchy.

    Uses the MVP org/workspace that matches the mock user in dependencies.py.
    """
    import uuid
    from datetime import datetime

    from src.platform.models import WorkspaceMember

    # Use MVP org/workspace to match mock user from dependencies.py
    org_id = "mvp-org-001"
    workspace_id = "mvp-ws-001"
    user_id = "mvp-user-001"

    # 1. Create Organization if it doesn't exist
    org = await test_session.get(Organization, org_id)
    if not org:
        org = Organization(
            id=org_id,
            name="Demo Organization",
            slug="demo-org",
            plan="free",
            created_at=datetime.utcnow(),
        )
        test_session.add(org)

    # 2. Create Workspace if it doesn't exist
    workspace = await test_session.get(Workspace, workspace_id)
    if not workspace:
        workspace = Workspace(
            id=workspace_id,
            org_id=org_id,
            name="Default Workspace",
            description="Your default process mining workspace",
            created_at=datetime.utcnow(),
        )
        test_session.add(workspace)

    # 3. Create User if it doesn't exist (matches mock user in dependencies.py)
    user = await test_session.get(User, user_id)
    if not user:
        user = User(
            id=user_id,
            email="analyst@company.local",
            name="Process Analyst",
            auth_provider="local",
            org_id=org_id,
            role="admin",
            created_at=datetime.utcnow(),
        )
        test_session.add(user)

    # 4. Create Workspace Member if it doesn't exist
    from sqlalchemy import select
    member_result = await test_session.execute(
        select(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id
        )
    )
    member = member_result.scalar_one_or_none()
    if not member:
        member = WorkspaceMember(
            id="mvp-member-001",
            workspace_id=workspace_id,
            user_id=user_id,
            role="owner",
            joined_at=datetime.utcnow(),
        )
        test_session.add(member)

    # 5. Create Project
    project_id = str(uuid.uuid4())
    project = Project(
        id=project_id,
        workspace_id=workspace_id,
        name="Test Project",
        description="Default project for e2e tests",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    test_session.add(project)

    await test_session.commit()
    return project_id


@pytest.fixture
async def uploaded_log_id(
    client: AsyncClient,
    sample_csv_with_multiple_variants: bytes,
    default_project: str,
    test_session: AsyncSession,
) -> str:
    """Pre-upload a log and return its ID for dependent tests."""
    response = await client.post(
        "/api/v1/datasets/upload",
        files={"file": ("test_variants.csv", sample_csv_with_multiple_variants, "text/csv")},
        data={"project_id": default_project},
    )
    assert response.status_code == 200

    # Force sync to disk for DuckDB visibility (same as e2e_log_id)
    await test_session.commit()
    from sqlalchemy import text

    await test_session.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))

    return response.json()["id"]


@pytest.fixture
async def discovered_model_id(client: AsyncClient, uploaded_log_id: str) -> str:
    """Discover a model from the uploaded log and return its ID."""
    response = await client.post(
        "/api/v1/discovery/discover?async_mode=false",  # BUG-019: Sync mode for tests
        json={"dataset_id": uploaded_log_id, "miner_type": "inductive", "model_name": "Test Model"},
    )
    assert response.status_code == 200
    return response.json()["id"]


# ============================================================================
# NEW FIXTURES FOR COMPREHENSIVE TESTING
# ============================================================================


@pytest.fixture
def insurance_small_csv() -> bytes:
    """100 cases, 600 events - fast unit tests."""
    with open("tests/data/insurance_small.csv", "rb") as f:
        return f.read()


@pytest.fixture
def insurance_medium_csv() -> bytes:
    """1,000 cases, 6,000 events - thorough tests."""
    with open("tests/data/insurance_medium.csv", "rb") as f:
        return f.read()


@pytest.fixture
def rework_cases_csv() -> bytes:
    """Cases with rework patterns (repeated activities)."""
    with open("tests/data/rework_cases.csv", "rb") as f:
        return f.read()


@pytest.fixture
def bottleneck_cases_csv() -> bytes:
    """Cases with bottleneck patterns (long waiting times)."""
    with open("tests/data/bottleneck_cases.csv", "rb") as f:
        return f.read()


@pytest.fixture
def simple_ocel_jsonocel() -> bytes:
    """Simple OCEL - Order/Item/Package (10 orders, 25 items, 10 packages)."""
    with open("tests/data/order_management_simple.jsonocel", "rb") as f:
        return f.read()


@pytest.fixture
def complex_ocel_jsonocel() -> bytes:
    """Complex OCEL - Multiple object types (50 orders, multi-type interactions)."""
    with open("tests/data/order_management_complex.jsonocel", "rb") as f:
        return f.read()


@pytest.fixture
async def uploaded_insurance_log_id(
    client: AsyncClient, insurance_small_csv: bytes, default_project: str
) -> str:
    """Pre-upload insurance log and return ID."""
    response = await client.post(
        "/api/v1/datasets/upload",
        files={"file": ("test.csv", insurance_small_csv, "text/csv")},
        data={"project_id": default_project},
    )
    assert response.status_code == 200
    return response.json()["id"]


@pytest.fixture
async def uploaded_ocel_log_id(
    client: AsyncClient, simple_ocel_jsonocel: bytes, default_project: str
) -> str:
    """Pre-upload OCEL log and return ID."""
    response = await client.post(
        "/api/v1/ocpm/upload",
        files={"file": ("test.jsonocel", simple_ocel_jsonocel, "application/json")},
    )
    # Note: OCPM upload might not fallback to datasets upload logic, so we might need to check if it needs project_id or if it creates its own.
    # Looking at legacy code, OCPM might be separate. But if OCPM upload fails, we will see.
    # For now, let's assume OCPM router handles it.
    assert response.status_code == 200
    return response.json()["id"]


@pytest.fixture
async def discovered_petri_net_id(client: AsyncClient, uploaded_insurance_log_id: str) -> str:
    """Pre-discover Petri net model and return ID."""
    response = await client.post(
        "/api/v1/discovery/discover?async_mode=false",  # BUG-019: Sync mode for tests
        json={
            "dataset_id": uploaded_insurance_log_id,
            "miner_type": "inductive",
            "model_name": "Test Model",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]
