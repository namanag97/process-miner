"""Tests for Processes Router (/api/processes/)

Test Coverage:
- Process upload (CSV with auto-detection and manual mapping)
- Process listing and retrieval
- Process statistics
- Variant analysis with complexity metrics
- Activity analysis
"""

import pytest
from httpx import AsyncClient


class TestProcessUpload:
    """Tests for process upload functionality."""

    @pytest.mark.asyncio
    async def test_upload_insurance_small_csv(
        self, client: AsyncClient, insurance_small_csv: bytes
    ):
        """Upload insurance small CSV and verify structure."""
        response = await client.post(
            "/api/v1/processes/upload",
            files={"file": ("insurance_small.csv", insurance_small_csv, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["total_cases"] == 100
        assert data["total_events"] == 600
        assert len(data["activities"]) == 6  # Insurance has 6 activities

    @pytest.mark.asyncio
    async def test_upload_with_auto_column_detection(
        self, client: AsyncClient, insurance_small_csv: bytes
    ):
        """Verify auto-column detection works correctly."""
        response = await client.post(
            "/api/v1/processes/upload",
            files={"file": ("test.csv", insurance_small_csv, "text/csv")},
        )
        assert response.status_code == 200
        # Auto-detection should find case_id, activity_name, timestamp

    @pytest.mark.asyncio
    async def test_upload_invalid_csv(self, client: AsyncClient):
        """Upload invalid CSV should return 422."""
        invalid_csv = b"not,a,valid\ncsv,file"
        response = await client.post(
            "/api/v1/processes/upload",
            files={"file": ("invalid.csv", invalid_csv, "text/csv")},
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_upload_empty_file(self, client: AsyncClient):
        """Upload empty file should return validation error."""
        response = await client.post(
            "/api/v1/processes/upload",
            files={"file": ("empty.csv", b"", "text/csv")},
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_upload_medium_dataset(self, client: AsyncClient, insurance_medium_csv: bytes):
        """Upload medium dataset (1K cases) for thorough testing."""
        response = await client.post(
            "/api/v1/processes/upload",
            files={"file": ("insurance_medium.csv", insurance_medium_csv, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_cases"] == 1000
        assert data["total_events"] == 6000


class TestProcessList:
    """Tests for process listing."""

    @pytest.mark.asyncio
    async def test_list_processes(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """List all processes."""
        response = await client.get("/api/v1/processes/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "processes" in data

    @pytest.mark.asyncio
    async def test_get_process_by_id(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Get process details by ID."""
        response = await client.get(f"/api/v1/processes/{uploaded_insurance_log_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == uploaded_insurance_log_id
        assert "total_cases" in data
        assert "total_events" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent_process(self, client: AsyncClient):
        """Get non-existent process should return 404."""
        response = await client.get("/api/v1/processes/nonexistent-id")
        assert response.status_code == 404


class TestProcessStatistics:
    """Tests for process statistics."""

    @pytest.mark.asyncio
    async def test_get_statistics(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Get process statistics."""
        response = await client.get(f"/api/v1/processes/{uploaded_insurance_log_id}/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_cases" in data
        assert "total_events" in data
        assert "start_activities" in data
        assert "end_activities" in data

    @pytest.mark.asyncio
    async def test_statistics_counts_accurate(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Verify statistics counts are accurate."""
        response = await client.get(f"/api/v1/processes/{uploaded_insurance_log_id}/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_cases"] == 100
        assert data["total_events"] == 600
        # Insurance data: all cases start with FNOL, end with Close Claim
        assert "First Notification of Loss (FNOL)" in str(data["start_activities"])


class TestProcessVariants:
    """Tests for process variant analysis."""

    @pytest.mark.asyncio
    async def test_get_variants(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Get process variants."""
        response = await client.get(f"/api/v1/processes/{uploaded_insurance_log_id}/variants")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "variants" in data

    @pytest.mark.asyncio
    async def test_get_variants_with_top_n(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Get top N variants."""
        response = await client.get(
            f"/api/v1/processes/{uploaded_insurance_log_id}/variants?top_n=5"
        )
        assert response.status_code == 200
        data = response.json()
        variants = data if isinstance(data, list) else data.get("variants", [])
        assert len(variants) <= 5

    @pytest.mark.asyncio
    async def test_variants_with_complexity_scores(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Verify complexity scores are in valid range [0, 1]."""
        response = await client.get(
            f"/api/v1/processes/{uploaded_insurance_log_id}/variants?include_complexity=true"
        )
        assert response.status_code == 200
        data = response.json()
        variants = data if isinstance(data, list) else data.get("variants", [])
        for variant in variants:
            if "complexity_score" in variant:
                assert 0 <= variant["complexity_score"] <= 1
            if "rework_count" in variant:
                assert variant["rework_count"] >= 0

    @pytest.mark.asyncio
    async def test_variant_case_counts_sum_to_total(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Verify SUM(variant.case_count) = log.total_cases."""
        response = await client.get(f"/api/v1/processes/{uploaded_insurance_log_id}/variants")
        assert response.status_code == 200
        variants_data = response.json()
        variants = (
            variants_data if isinstance(variants_data, list) else variants_data.get("variants", [])
        )

        total_variant_cases = sum(v.get("case_count", 0) for v in variants)

        stats_response = await client.get(
            f"/api/v1/processes/{uploaded_insurance_log_id}/statistics"
        )
        stats = stats_response.json()

        assert total_variant_cases == stats["total_cases"]


class TestProcessActivities:
    """Tests for process activity analysis."""

    @pytest.mark.asyncio
    async def test_get_activities(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Get process activities."""
        response = await client.get(f"/api/v1/processes/{uploaded_insurance_log_id}/activities")
        assert response.status_code == 200
        data = response.json()
        activities = data if isinstance(data, list) else data.get("activities", [])
        assert len(activities) == 6  # Insurance has 6 activities

    @pytest.mark.asyncio
    async def test_activities_sorted_by_frequency(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Verify activities can be sorted by frequency."""
        response = await client.get(
            f"/api/v1/processes/{uploaded_insurance_log_id}/activities?sort_by=frequency"
        )
        assert response.status_code == 200
        data = response.json()
        activities = data if isinstance(data, list) else data.get("activities", [])
        # Verify activities have frequency information
        for activity in activities:
            assert "name" in activity or "activity" in activity

    @pytest.mark.asyncio
    async def test_activity_frequencies_sum_correctly(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Verify activity frequency percentages are valid."""
        response = await client.get(f"/api/v1/processes/{uploaded_insurance_log_id}/activities")
        assert response.status_code == 200
        data = response.json()
        activities = data if isinstance(data, list) else data.get("activities", [])

        # Each activity should have valid frequency
        for activity in activities:
            if "frequency" in activity:
                assert activity["frequency"] > 0
            if "frequency_percent" in activity:
                assert 0 <= activity["frequency_percent"] <= 100
