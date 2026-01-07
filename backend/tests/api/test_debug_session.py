import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_debug_dataset_exists(auth_client: AsyncClient, seeded_dataset_ready, db_session):
    """Debug: Check if dataset exists in DB."""
    from src.features.process_mining.models import Dataset
    from sqlalchemy import select

    # Query the DB directly
    result = await db_session.execute(select(Dataset))
    datasets = result.scalars().all()

    print(f"\n=== DEBUG: Datasets in DB: {len(datasets)}")
    for ds in datasets:
        print(f"  - {ds.id}: {ds.name} (project: {ds.project_id})")

    print(f"\n=== Seeded dataset: {seeded_dataset_ready.id}")

    # Now call the API
    response = await auth_client.get("/api/v1/datasets")
    print(f"\n=== API response status: {response.status_code}")
    data = response.json()
    print(f"=== API response total: {data.get('total', 'N/A')}")
    print(f"=== API response items: {len(data.get('items', []))}")

    assert len(datasets) > 0, "No datasets in DB!"
