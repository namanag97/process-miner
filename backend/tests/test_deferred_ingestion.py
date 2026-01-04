"""Tests for deferred ingestion (two-phase upload).

Tests the flow:
1. Upload with async_store=True → Dataset(UNSTRUCTURED)
2. POST /ingest with mapping → Celery task queued → Dataset(ANALYZING)
3. Task completes → Dataset(READY)
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.models.orm import Dataset, DatasetStatus, UploadedFile


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
    async def test_upload_async_store_creates_unstructured_dataset(
        self, client, sample_csv_content
    ):
        """Test that async_store=True creates dataset with UNSTRUCTURED status."""
        response = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("test.csv", sample_csv_content, "text/csv")},
            data={"async_store": "true", "name": "Test Dataset"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unstructured"
        assert data["total_events"] == 0
        assert data["total_cases"] == 0

    @pytest.mark.asyncio
    async def test_upload_without_async_store_creates_ready_dataset(
        self, client, sample_csv_content
    ):
        """Test that default upload (async_store=False) processes immediately."""
        response = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("test.csv", sample_csv_content, "text/csv")},
            data={"name": "Test Dataset"},
        )

        assert response.status_code == 200
        data = response.json()
        # Should be ready (processed immediately)
        assert data["total_events"] > 0

    @pytest.mark.asyncio
    async def test_ingest_endpoint_rejects_analyzing_dataset(self, client, db_session):
        """Test that /ingest rejects dataset already being analyzed (idempotency)."""
        # Create dataset in ANALYZING state
        dataset = Dataset(
            name="Test",
            source_file="test.csv",
            source_format="csv",
            status=DatasetStatus.ANALYZING.value,
        )
        db_session.add(dataset)
        await db_session.flush()

        response = client.post(
            f"/api/v1/datasets/{dataset.id}/ingest",
            json={
                "case_id_column": "case_id",
                "activity_column": "activity",
                "timestamp_column": "timestamp",
            },
        )

        assert response.status_code == 400
        assert "already being analyzed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_ingest_endpoint_rejects_ready_dataset(self, client, db_session):
        """Test that /ingest rejects already ready dataset."""
        dataset = Dataset(
            name="Test",
            source_file="test.csv",
            source_format="csv",
            status=DatasetStatus.READY.value,
        )
        db_session.add(dataset)
        await db_session.flush()

        response = client.post(
            f"/api/v1/datasets/{dataset.id}/ingest",
            json={
                "case_id_column": "case_id",
                "activity_column": "activity",
                "timestamp_column": "timestamp",
            },
        )

        assert response.status_code == 400
        assert "UNSTRUCTURED or ERROR" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_ingest_endpoint_allows_error_retry(self, client, db_session):
        """Test that /ingest allows retry for ERROR datasets."""
        # Create dataset in ERROR state (failed previous attempt)
        dataset = Dataset(
            name="Test",
            source_file="test.csv",
            source_format="csv",
            status=DatasetStatus.ERROR.value,
            error_message="Previous attempt failed",
        )
        db_session.add(dataset)

        # Add uploaded file
        uploaded_file = UploadedFile(
            dataset_id=dataset.id,
            filename="test.csv",
            storage_path="/tmp/test.csv",
            size_bytes=100,
        )
        db_session.add(uploaded_file)
        await db_session.flush()

        with patch("src.infrastructure.tasks.ingest_dataset_task.delay") as mock_delay:
            mock_delay.return_value = MagicMock(id="task-123")

            response = client.post(
                f"/api/v1/datasets/{dataset.id}/ingest",
                json={
                    "case_id_column": "case_id",
                    "activity_column": "activity",
                    "timestamp_column": "timestamp",
                },
            )

            assert response.status_code == 200
            mock_delay.assert_called_once()

    @pytest.mark.asyncio
    async def test_ingest_stores_mapping(self, client, db_session):
        """Test that /ingest stores the column mapping."""
        dataset = Dataset(
            name="Test",
            source_file="test.csv",
            source_format="csv",
            status=DatasetStatus.UNSTRUCTURED.value,
        )
        db_session.add(dataset)

        uploaded_file = UploadedFile(
            dataset_id=dataset.id,
            filename="test.csv",
            storage_path="/tmp/test.csv",
            size_bytes=100,
        )
        db_session.add(uploaded_file)
        await db_session.flush()

        with patch("src.infrastructure.tasks.ingest_dataset_task.delay") as mock_delay:
            mock_delay.return_value = MagicMock(id="task-123")

            response = client.post(
                f"/api/v1/datasets/{dataset.id}/ingest",
                json={
                    "case_id_column": "CaseID",
                    "activity_column": "Action",
                    "timestamp_column": "Time",
                    "resource_column": "User",
                },
            )

            assert response.status_code == 200

        # Verify mapping was stored
        await db_session.refresh(dataset)
        mapping = json.loads(dataset.mapping_json)
        assert mapping["case_id_column"] == "CaseID"
        assert mapping["activity_column"] == "Action"
        assert mapping["timestamp_column"] == "Time"
        assert mapping["resource_column"] == "User"


class TestDatasetStatusTransitions:
    """Test dataset status state machine."""

    def test_status_enum_values(self):
        """Verify status enum has correct values."""
        assert DatasetStatus.UNSTRUCTURED.value == "unstructured"
        assert DatasetStatus.ANALYZING.value == "analyzing"
        assert DatasetStatus.READY.value == "ready"
        assert DatasetStatus.ERROR.value == "error"

    @pytest.mark.asyncio
    async def test_status_transitions(self, db_session):
        """Test valid status transitions."""
        dataset = Dataset(
            name="Test",
            source_file="test.csv",
            source_format="csv",
            status=DatasetStatus.UNSTRUCTURED.value,
        )
        db_session.add(dataset)
        await db_session.flush()

        # UNSTRUCTURED -> ANALYZING
        dataset.status = DatasetStatus.ANALYZING.value
        await db_session.flush()
        assert dataset.status == "analyzing"

        # ANALYZING -> READY
        dataset.status = DatasetStatus.READY.value
        await db_session.flush()
        assert dataset.status == "ready"

        # READY -> ERROR (edge case)
        dataset.status = DatasetStatus.ERROR.value
        dataset.error_message = "Something went wrong"
        await db_session.flush()
        assert dataset.status == "error"

        # ERROR -> ANALYZING (retry)
        dataset.status = DatasetStatus.ANALYZING.value
        dataset.error_message = None
        await db_session.flush()
        assert dataset.status == "analyzing"
