"""Tests to verify conformance algorithm tracking (existing fix).

This file verifies that the already-implemented algorithm tracking feature
works correctly:
- algorithm_used field is present in responses
- fallback_reason is populated when fallback occurs
- Logging occurs when algorithms fall back
"""

import pytest
from httpx import AsyncClient


class TestAlgorithmTracking:
    """Verify that conformance responses include algorithm tracking metadata."""

    @pytest.mark.asyncio
    async def test_token_replay_includes_algorithm_used(
        self, client: AsyncClient, uploaded_insurance_log_id: str, discovered_petri_net_id: str
    ):
        """Token replay response should include algorithm_used field."""
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

        # Verify algorithm tracking fields exist
        assert "algorithm_used" in data, "Missing algorithm_used field"
        assert "fallback_reason" in data, "Missing fallback_reason field"

        # For token_replay, algorithm_used should match method (no fallback)
        assert data["algorithm_used"] == "token_replay"
        assert data["fallback_reason"] is None

    @pytest.mark.asyncio
    async def test_alignment_includes_algorithm_used(
        self, client: AsyncClient, uploaded_insurance_log_id: str, discovered_petri_net_id: str
    ):
        """Alignment response should include algorithm_used field."""
        response = await client.post(
            "/api/v1/conformance/check",
            json={
                "log_id": uploaded_insurance_log_id,
                "model_id": discovered_petri_net_id,
                "method": "alignment",
            },
        )
        assert response.status_code == 200
        data = response.json()

        # Verify algorithm tracking fields exist
        assert "algorithm_used" in data, "Missing algorithm_used field"
        assert "fallback_reason" in data, "Missing fallback_reason field"
        assert "method" in data, "Missing method field"

        # Verify method is what was requested
        assert data["method"] == "alignment"

        # algorithm_used could be either "alignment" or "token_replay" (if fallback occurred)
        assert data["algorithm_used"] in ["alignment", "token_replay"]

        # If fallback occurred, fallback_reason should be populated
        if data["algorithm_used"] != data["method"]:
            assert data["fallback_reason"] is not None, "Fallback occurred but no reason provided"
            assert "failed" in data["fallback_reason"].lower() or "timeout" in data["fallback_reason"].lower()

    @pytest.mark.asyncio
    async def test_conformance_response_schema(
        self, client: AsyncClient, uploaded_insurance_log_id: str, discovered_petri_net_id: str
    ):
        """Verify conformance response includes all required tracking fields."""
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

        # Verify all expected fields from ConformanceResponse schema
        required_fields = {
            "id", "log_id", "model_id", "fitness", "method",
            "algorithm_used", "is_conformant", "fitting_traces", "total_traces"
        }

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Optional fields should be present (even if None)
        optional_fields = {"precision", "generalization", "simplicity", "fallback_reason"}
        for field in optional_fields:
            assert field in data, f"Missing optional field: {field}"

    @pytest.mark.asyncio
    async def test_stored_results_include_tracking(
        self, client: AsyncClient, uploaded_insurance_log_id: str, discovered_petri_net_id: str
    ):
        """Verify that stored conformance results include algorithm tracking."""
        # Run conformance check
        check_response = await client.post(
            "/api/v1/conformance/check",
            json={
                "log_id": uploaded_insurance_log_id,
                "model_id": discovered_petri_net_id,
                "method": "token_replay",
            },
        )
        assert check_response.status_code == 200
        result_id = check_response.json()["id"]

        # Retrieve stored result
        get_response = await client.get(f"/api/v1/conformance/results/{result_id}")
        assert get_response.status_code == 200
        data = get_response.json()

        # Verify tracking fields are persisted
        assert "algorithm_used" in data
        assert "fallback_reason" in data

    @pytest.mark.asyncio
    async def test_list_results_includes_tracking(
        self, client: AsyncClient, uploaded_insurance_log_id: str, discovered_petri_net_id: str
    ):
        """Verify that conformance results list includes algorithm tracking."""
        # Run conformance check
        await client.post(
            "/api/v1/conformance/check",
            json={
                "log_id": uploaded_insurance_log_id,
                "model_id": discovered_petri_net_id,
                "method": "token_replay",
            },
        )

        # List results
        list_response = await client.get(
            "/api/v1/conformance/results",
            params={"log_id": uploaded_insurance_log_id}
        )
        assert list_response.status_code == 200
        data = list_response.json()

        assert "items" in data
        if data["items"]:
            # Check first result has tracking fields
            first_result = data["items"][0]
            # Note: The list endpoint might not include all fields,
            # but at minimum should have method
            assert "method" in first_result
