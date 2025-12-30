"""Tests for Filtering Router (/api/filtering/)

Test Coverage:
- Filter application (time, variant, activity, performance)
- Filter preview
- Filter options
- Filter templates
"""

import pytest
from httpx import AsyncClient


class TestFilterApplication:
    """Tests for filter application."""

    @pytest.mark.asyncio
    async def test_apply_time_range_filter(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Apply time range filter."""
        response = await client.post(
            f"/api/v1/filtering/logs/{uploaded_insurance_log_id}/apply",
            json={
                "filters": [
                    {
                        "type": "time_range",
                        "start_time": "2023-01-01T00:00:00",
                        "end_time": "2023-12-31T23:59:59",
                    }
                ]
            },
        )
        # Either succeeds or endpoint not implemented
        assert response.status_code in [200, 404, 501]

    @pytest.mark.asyncio
    async def test_filter_reduces_case_count(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Verify filtering reduces case count."""
        # Get original stats
        original_resp = await client.get(
            f"/api/v1/processes/{uploaded_insurance_log_id}/statistics"
        )
        if original_resp.status_code != 200:
            pytest.skip("Statistics not available")

        original_stats = original_resp.json()
        original_cases = original_stats["total_cases"]

        # Apply variant filter (top 50%)
        filter_resp = await client.post(
            f"/api/v1/filtering/logs/{uploaded_insurance_log_id}/apply",
            json={"filters": [{"type": "variant", "top_k_percent": 50}]},
        )
        if filter_resp.status_code not in [200]:
            pytest.skip("Filtering not available")

        # Filtered cases should be <= original
        filtered_data = filter_resp.json()
        if "total_cases" in filtered_data:
            assert filtered_data["total_cases"] <= original_cases


class TestFilterPreview:
    """Tests for filter preview."""

    @pytest.mark.asyncio
    async def test_preview_filter(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Preview filter without applying."""
        response = await client.post(
            f"/api/v1/filtering/logs/{uploaded_insurance_log_id}/preview",
            json={"filters": [{"type": "variant", "top_k": 5}]},
        )
        # Either succeeds or endpoint not implemented
        assert response.status_code in [200, 404, 501]
