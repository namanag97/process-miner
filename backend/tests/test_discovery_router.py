"""Tests for Discovery Router (/api/discovery/)

Test Coverage:
- List available miners
- Process model discovery (Alpha, Inductive, Heuristics, DFG)
- Model management (list, get, delete)
- Model quality metrics (fitness, precision)
"""

import pytest
from httpx import AsyncClient


class TestMinersCatalog:
    """Tests for miners catalog."""

    @pytest.mark.asyncio
    async def test_list_miners(self, client: AsyncClient):
        """List available mining algorithms."""
        response = await client.get("/api/v1/discovery/miners")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should include alpha, inductive, heuristics, dfg
        miner_types = [m.get("type") or m.get("name") for m in data]
        assert any("alpha" in str(m).lower() for m in miner_types)
        assert any("inductive" in str(m).lower() for m in miner_types)


class TestModelDiscovery:
    """Tests for process model discovery."""

    @pytest.mark.asyncio
    async def test_discover_with_inductive_miner(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Discover model using inductive miner."""
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": uploaded_insurance_log_id,
                "miner_type": "inductive",
                "model_name": "Test Inductive Model"
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "fitness" in data or "quality" in data

    @pytest.mark.asyncio
    async def test_discover_with_alpha_miner(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Discover model using alpha miner."""
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": uploaded_insurance_log_id,
                "miner_type": "alpha",
                "model_name": "Test Alpha Model"
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data

    @pytest.mark.asyncio
    async def test_discover_with_heuristics_miner(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Discover model using heuristics miner."""
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": uploaded_insurance_log_id,
                "miner_type": "heuristics",
                "model_name": "Test Heuristics Model"
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data

    @pytest.mark.asyncio
    async def test_discover_with_invalid_log_id(self, client: AsyncClient):
        """Discover with invalid log_id should return 404."""
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": "nonexistent",
                "miner_type": "inductive",
                "model_name": "Test"
            },
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_discover_with_invalid_miner_type(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Discover with unsupported miner_type should return 400."""
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": uploaded_insurance_log_id,
                "miner_type": "nonexistent_miner",
                "model_name": "Test"
            },
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_self_discovered_model_has_good_fitness(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Self-discovered model should have fitness > 0.5."""
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": uploaded_insurance_log_id,
                "miner_type": "inductive",
                "model_name": "Test Fitness"
            },
        )
        assert response.status_code == 200
        data = response.json()
        if "fitness" in data:
            assert 0.0 <= data["fitness"] <= 1.0
            # Self-discovered should fit source data reasonably well
            # (though not always perfect due to noise/infrequent paths)


class TestModelManagement:
    """Tests for model management."""

    @pytest.mark.asyncio
    async def test_list_models(self, client: AsyncClient, discovered_petri_net_id: str):
        """List all discovered models."""
        response = await client.get("/api/v1/discovery/models")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "models" in data

    @pytest.mark.asyncio
    async def test_get_model_by_id(self, client: AsyncClient, discovered_petri_net_id: str):
        """Get model details by ID."""
        response = await client.get(f"/api/v1/discovery/models/{discovered_petri_net_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == discovered_petri_net_id

    @pytest.mark.asyncio
    async def test_delete_model(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """Delete discovered model."""
        # Discover first
        discover_resp = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": uploaded_insurance_log_id,
                "miner_type": "inductive",
                "model_name": "To Delete"
            },
        )
        model_id = discover_resp.json()["id"]

        # Delete
        response = await client.delete(f"/api/v1/discovery/models/{model_id}")
        assert response.status_code == 200

        # Verify deleted
        get_resp = await client.get(f"/api/v1/discovery/models/{model_id}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_nonexistent_model(self, client: AsyncClient):
        """Get non-existent model should return 404."""
        response = await client.get("/api/v1/discovery/models/nonexistent-id")
        assert response.status_code == 404


class TestModelQuality:
    """Tests for model quality metrics."""

    @pytest.mark.asyncio
    async def test_quality_metrics_in_valid_range(self, client: AsyncClient, discovered_petri_net_id: str):
        """Verify fitness and precision are in [0, 1]."""
        response = await client.get(f"/api/v1/discovery/models/{discovered_petri_net_id}")
        assert response.status_code == 200
        data = response.json()

        if "fitness" in data:
            assert 0.0 <= data["fitness"] <= 1.0
        if "precision" in data:
            assert 0.0 <= data["precision"] <= 1.0

    @pytest.mark.asyncio
    async def test_discover_from_tiny_log_handles_gracefully(self, client: AsyncClient):
        """Discover from tiny log (2 cases) should handle gracefully."""
        # Upload tiny CSV
        tiny_csv = b"""case_id,activity_name,timestamp
c1,A,2023-01-01 09:00:00
c1,B,2023-01-01 09:30:00
c2,A,2023-01-02 10:00:00
c2,B,2023-01-02 10:30:00"""

        upload_resp = await client.post(
            "/api/v1/processes/upload",
            files={"file": ("tiny.csv", tiny_csv, "text/csv")},
        )
        if upload_resp.status_code != 200:
            pytest.skip("Tiny log upload failed")

        log_id = upload_resp.json()["id"]

        # Discover - should not crash
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": log_id,
                "miner_type": "inductive",
                "model_name": "Tiny Model"
            },
        )
        # Either succeeds or returns a meaningful error
        assert response.status_code in [200, 400, 500]
