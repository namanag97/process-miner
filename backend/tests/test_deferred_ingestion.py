"""Tests for deferred ingestion (two-phase upload).

Tests the flow:
1. Upload with async_store=True → Dataset(UNSTRUCTURED)
2. POST /ingest with mapping → Celery task queued → Dataset(ANALYZING)
3. Task completes → Dataset(READY)
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.features.process_mining.models.orm import Dataset, DatasetStatus, UploadedFile


class TestDeferredIngestion:
    """Test suite for deferred ingestion flow."""

    @pytest.fixture
    def sample_csv_content(self):
        """Sample CSV file content."""
        return b"""case_id,activity,timestamp,resource
1,Start,2024-01-01 10:00:00,Alice
1,Process,2024-01-01 11:00:00,Bob
1,End,2024-01-01 12:00:00,Alice
2,Start,2024-01-01 10:30:00,Bob
2,End,2024-01-01 11:30:00,Bob
"""


    @pytest.mark.asyncio
    async def test_direct_upload_creates_uploaded_dataset(
        self, client, sample_csv_content, default_project
    ):
        """Test that direct upload creates dataset with UPLOADED status."""
        response = await client.post(
            "/api/v1/datasets/",
            files={"file": ("test.csv", sample_csv_content, "text/csv")},
            data={"name": "Test Dataset", "project_id": default_project},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "uploaded"
        assert data["source_file"] == "test.csv"

    @pytest.mark.asyncio
    async def test_ingest_endpoint_requires_mapped_status(self, client, db_session, default_project):
        """Test that /ingest rejects dataset not in MAPPED state."""
        # Create dataset in UPLOADED state
        dataset = Dataset(
            name="Test",
            source_file="test.csv",
            source_format="csv",
            status=DatasetStatus.UPLOADED.value,
            project_id=default_project,
        )
        db_session.add(dataset)
        await db_session.flush()

        response = await client.post(
            f"/api/v1/datasets/{dataset.id}/ingest",
        )

        assert response.status_code == 400
        assert "MAPPED or ERROR" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_ingest_endpoint_requires_mapping(self, client, db_session, default_project):
        """Test that /ingest fails if no mapping exists."""
        dataset = Dataset(
            name="Test",
            source_file="test.csv",
            source_format="csv",
            status=DatasetStatus.MAPPED.value,
            project_id=default_project,
        )
        db_session.add(dataset)
        await db_session.flush()

        # No mapping set
        response = await client.post(
            f"/api/v1/datasets/{dataset.id}/ingest",
        )

        assert response.status_code == 422
        assert "mapping" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_ingest_endpoint_success(self, client, db_session, default_project):
        """Test successful ingestion trigger."""
        # Create dataset in MAPPED state with mapping
        dataset = Dataset(
            name="Test",
            source_file="test.csv",
            source_format="csv",
            status=DatasetStatus.MAPPED.value,
            project_id=default_project,
            mapping_json=json.dumps({
                "case_id_column": "case_id",
                "activity_column": "activity",
                "timestamp_column": "timestamp"
            })
        )
        db_session.add(dataset)
        await db_session.flush()

        with patch("src.features.process_mining.api.datasets.ingest.ingest_dataset_task.delay") as mock_delay:
            mock_delay.return_value = MagicMock(id="task-123")

            response = await client.post(
                f"/api/v1/datasets/{dataset.id}/ingest",
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "pending"
            assert data["job_type"] == "ingest_dataset"
            mock_delay.assert_called_once()

class TestDatasetStatusTransitions:
    """Test dataset status state machine."""

    def test_status_enum_values(self):
        """Verify status enum has correct values."""
        assert DatasetStatus.UPLOADED.value == "uploaded"
        assert DatasetStatus.MAPPED.value == "mapped"
        assert DatasetStatus.INGESTING.value == "ingesting" 
        assert DatasetStatus.READY.value == "ready"
        assert DatasetStatus.ERROR.value == "error"

    @pytest.mark.asyncio
    async def test_status_transitions(self, db_session, default_project):
        """Test valid status transitions."""
        dataset = Dataset(
            name="Test",
            source_file="test.csv",
            source_format="csv",
            status=DatasetStatus.UPLOADED.value,
            project_id=default_project,
        )
        db_session.add(dataset)
        await db_session.flush()

        # UPLOADED -> MAPPED
        dataset.status = DatasetStatus.MAPPED.value
        await db_session.flush()
        assert dataset.status == "mapped"

        # MAPPED -> INGESTING
        dataset.status = DatasetStatus.INGESTING.value
        await db_session.flush()
        assert dataset.status == "ingesting"

        # INGESTING -> READY
        dataset.status = DatasetStatus.READY.value
        await db_session.flush()
        assert dataset.status == "ready"

