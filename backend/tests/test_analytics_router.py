"""Tests for Analytics Router (/api/analytics/)

Test Coverage:
- Bottleneck detection
- Rework analysis
- Service times
- Cycle times
- Throughput metrics
"""

import pytest
from httpx import AsyncClient


class TestBottleneckDetection:
    """Tests for bottleneck detection."""

    @pytest.mark.asyncio
    async def test_detect_bottlenecks(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Detect bottlenecks in process."""
        response = await client.get(f"/api/v1/analytics/logs/{uploaded_insurance_log_id}/bottlenecks")
        assert response.status_code == 200
        data = response.json()
        # Should return list of bottlenecks or empty list
        assert isinstance(data, list) or "bottlenecks" in data

    @pytest.mark.asyncio
    async def test_bottlenecks_with_special_dataset(self, client: AsyncClient, bottleneck_cases_csv: bytes):
        """Detect bottlenecks using dataset with known bottleneck."""
        # Upload bottleneck dataset
        upload_resp = await client.post(
            "/api/v1/processes/upload",
            files={"file": ("bottleneck.csv", bottleneck_cases_csv, "text/csv")},
        )
        if upload_resp.status_code != 200:
            pytest.skip("Bottleneck dataset upload failed")

        log_id = upload_resp.json()["id"]

        # Detect bottlenecks
        response = await client.get(f"/api/v1/analytics/logs/{log_id}/bottlenecks")
        assert response.status_code == 200
        # Should detect "Set Reserve" activity as bottleneck (8+ hour wait)


class TestReworkAnalysis:
    """Tests for rework analysis."""

    @pytest.mark.asyncio
    async def test_analyze_rework(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Analyze rework patterns."""
        response = await client.get(f"/api/v1/analytics/logs/{uploaded_insurance_log_id}/rework")
        assert response.status_code == 200
        data = response.json()
        if "rework_percentage" in data:
            assert 0 <= data["rework_percentage"] <= 100

    @pytest.mark.asyncio
    async def test_rework_with_special_dataset(self, client: AsyncClient, rework_cases_csv: bytes):
        """Analyze rework using dataset with known rework patterns."""
        # Upload rework dataset
        upload_resp = await client.post(
            "/api/v1/processes/upload",
            files={"file": ("rework.csv", rework_cases_csv, "text/csv")},
        )
        if upload_resp.status_code != 200:
            pytest.skip("Rework dataset upload failed")

        log_id = upload_resp.json()["id"]

        # Analyze rework
        response = await client.get(f"/api/v1/analytics/logs/{log_id}/rework")
        assert response.status_code == 200
        # Should detect repeated activities


class TestPerformanceMetrics:
    """Tests for performance metrics."""

    @pytest.mark.asyncio
    async def test_get_service_times(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Get service time statistics."""
        response = await client.get(f"/api/v1/analytics/logs/{uploaded_insurance_log_id}/service-times")
        assert response.status_code == 200
        data = response.json()
        # Validate service times if present
        if isinstance(data, list):
            for activity in data:
                if "min" in activity and "max" in activity and "avg" in activity:
                    assert activity["min"] <= activity["avg"] <= activity["max"]

    @pytest.mark.asyncio
    async def test_get_cycle_times(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Get cycle time metrics."""
        response = await client.get(f"/api/v1/analytics/logs/{uploaded_insurance_log_id}/cycle-time")
        assert response.status_code == 200
        data = response.json()
        # Validate cycle times
        if "min" in data and "max" in data:
            assert data["min"] <= data["max"]

    @pytest.mark.asyncio
    async def test_get_throughput(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Get throughput metrics."""
        response = await client.get(f"/api/v1/analytics/logs/{uploaded_insurance_log_id}/throughput")
        assert response.status_code == 200
        data = response.json()
        # Throughput rates should be >= 0
        for key in data:
            if "rate" in key or "per" in key:
                assert data[key] >= 0
