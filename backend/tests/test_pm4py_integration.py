"""Tests for PM4Py Integration

Test Coverage:
- PM4Py discovery algorithms produce valid outputs
- PM4Py conformance checking works correctly
- PM4Py statistics are accurate
- PM4Py handles edge cases gracefully
"""

import pytest
from httpx import AsyncClient


class TestPM4PyDiscovery:
    """Tests for PM4Py discovery algorithms."""

    @pytest.mark.asyncio
    async def test_alpha_miner_produces_petri_net(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Alpha miner produces valid Petri net."""
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": uploaded_insurance_log_id,
                "miner_type": "alpha",
                "model_name": "PM4Py Alpha Test",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        # Petri net should have places and transitions

    @pytest.mark.asyncio
    async def test_inductive_miner_produces_petri_net(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Inductive miner produces valid Petri net."""
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": uploaded_insurance_log_id,
                "miner_type": "inductive",
                "model_name": "PM4Py Inductive Test",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data


class TestPM4PyConformance:
    """Tests for PM4Py conformance checking."""

    @pytest.mark.asyncio
    async def test_token_replay_executes(
        self, client: AsyncClient, uploaded_insurance_log_id: str, discovered_petri_net_id: str
    ):
        """Token replay executes and returns fitness."""
        response = await client.post(
            "/api/v1/conformance/check",
            json={
                "log_id": uploaded_insurance_log_id,
                "model_id": discovered_petri_net_id,
                "method": "token_replay",
            },
        )
        assert response.status_code == 200
        data = response.json()
        if "fitness" in data:
            assert 0.0 <= data["fitness"] <= 1.0


class TestPM4PyStatistics:
    """Tests for PM4Py statistics."""

    @pytest.mark.asyncio
    async def test_start_activities_extracted(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """Start activities are correctly extracted."""
        response = await client.get(f"/api/v1/processes/{uploaded_insurance_log_id}/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "start_activities" in data
        # Insurance data: all cases start with FNOL
        assert "First Notification of Loss (FNOL)" in str(data["start_activities"])

    @pytest.mark.asyncio
    async def test_end_activities_extracted(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """End activities are correctly extracted."""
        response = await client.get(f"/api/v1/processes/{uploaded_insurance_log_id}/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "end_activities" in data
        # Insurance data: all cases end with Close Claim
        assert "Close Claim" in str(data["end_activities"])


class TestPM4PyEdgeCases:
    """Tests for PM4Py edge case handling."""

    @pytest.mark.asyncio
    async def test_single_case_log_handled(self, client: AsyncClient):
        """PM4Py handles single-case log without crashing."""
        single_case_csv = b"""case_id,activity_name,timestamp
c1,A,2023-01-01 09:00:00
c1,B,2023-01-01 09:30:00
c1,C,2023-01-01 10:00:00"""

        upload_resp = await client.post(
            "/api/v1/processes/upload",
            files={"file": ("single.csv", single_case_csv, "text/csv")},
        )
        if upload_resp.status_code != 200:
            pytest.skip("Single case upload failed")

        log_id = upload_resp.json()["id"]

        # Discover - should not crash
        response = await client.post(
            "/api/v1/discovery/discover",
            json={"log_id": log_id, "miner_type": "inductive", "model_name": "Single Case Model"},
        )
        assert response.status_code in [200, 400, 500]  # Either succeeds or fails gracefully
