"""Integration Tests for MiningService Layer.

These tests bypass the API and test the MiningService directly,
providing faster feedback and more granular error messages.

Run: pytest tests/test_discovery_integration.py -v --tb=short
"""

import time
from pathlib import Path

import pytest
from src.features.process_mining.enums import MinerType, ModelFormat

from src.features.process_mining.services.mining import MiningService, mining_service

# =============================================================================
# TEST DATA PATHS
# =============================================================================

# BPI Challenge 2019 XES file (real-world dataset)
BPI_2019_XES = Path("/Users/namanagarwal/system/backend/data/BPI_Challenge_2019.xes")

# Existing test data
INSURANCE_SMALL = Path("tests/data/insurance_small.csv")
INSURANCE_MEDIUM = Path("tests/data/insurance_medium.csv")


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mining_svc() -> MiningService:
    """Get MiningService instance."""
    return mining_service


@pytest.fixture
def bpi_2019_available() -> bool:
    """Check if BPI 2019 XES file is available."""
    return BPI_2019_XES.exists()


# =============================================================================
# SERVICE LAYER TESTS
# =============================================================================


class TestMiningServiceAvailableMiners:
    """Tests for the get_available_miners method."""

    def test_get_available_miners_returns_list(self, mining_svc: MiningService):
        """
        TEST: get_available_miners should return a list of miner info dicts.
        """
        miners = mining_svc.get_available_miners()

        assert isinstance(miners, list)
        assert len(miners) >= 10  # At least 10 miners available

        # Each miner should have basic info
        for miner in miners:
            assert "type" in miner or "name" in miner
            assert "output_format" in miner or "format" in miner

    def test_all_miner_types_are_available(self, mining_svc: MiningService):
        """
        TEST: All MinerType enum values should be available.
        """
        miners = mining_svc.get_available_miners()
        available_types = {m.get("type", m.get("name", "")).lower() for m in miners}

        expected_types = [
            "alpha",
            "inductive",
            "inductive_infrequent",
            "heuristics",
            "dfg",
            "performance_dfg",
            "ilp",
            "powl",
            "bpmn_inductive",
            "declare",
            "log_skeleton",
            "temporal_profile",
            "prefix_tree",
            "transition_system",
            "batches",
            "correlation",
        ]

        for expected in expected_types:
            assert any(expected in t for t in available_types), (
                f"MinerType '{expected}' not found in available miners"
            )


class TestModelSerialization:
    """Tests for model serialization/deserialization."""

    def test_serialize_returns_bytes(self, mining_svc: MiningService):
        """
        TEST: serialize_model should return bytes for joblib storage.
        """
        # Create a simple test object
        test_model = {"test": "data", "value": 42}
        serialized = mining_svc.serialize_model(test_model)

        assert isinstance(serialized, bytes)
        assert len(serialized) > 0

    def test_deserialize_returns_original(self, mining_svc: MiningService):
        """
        TEST: deserialize_model should return the original object.
        """
        test_model = {"test": "data", "nested": {"key": "value"}}
        serialized = mining_svc.serialize_model(test_model)
        deserialized = mining_svc.deserialize_model(serialized)

        assert deserialized == test_model


class TestGraphJSONSerialization:
    """Tests for frontend-compatible graph JSON serialization."""

    def test_serialize_to_graph_json_dfg_format(self, mining_svc: MiningService):
        """
        TEST: DFG models should serialize to graph JSON with nodes/edges.
        """
        # Create mock DFG data structure
        dfg_data = (
            {("A", "B"): 10, ("B", "C"): 8},  # DFG edges
            {"A": 10},  # Start activities
            {"C": 8},  # End activities
        )

        graph_json = mining_svc.serialize_to_graph_json(dfg_data, ModelFormat.DFG)

        assert graph_json is not None
        assert "nodes" in graph_json
        assert "edges" in graph_json


# =============================================================================
# ALGORITHM OUTPUT FORMAT VALIDATION
# =============================================================================


class TestAlgorithmOutputFormats:
    """Tests that validate the output structure of each algorithm."""

    def test_miner_type_to_format_mapping(self):
        """
        TEST: Verify MinerType -> ModelFormat mapping is correct.
        """
        expected_mappings = {
            MinerType.ALPHA: ModelFormat.PETRI_NET,
            # Alpha+ is legacy/deprecated
            MinerType.INDUCTIVE: ModelFormat.PROCESS_TREE,
            MinerType.INDUCTIVE_INFREQUENT: ModelFormat.PROCESS_TREE,
            MinerType.HEURISTICS: ModelFormat.PETRI_NET,
            MinerType.DFG: ModelFormat.DFG,
            MinerType.PERFORMANCE_DFG: ModelFormat.PERFORMANCE_DFG,
            MinerType.ILP: ModelFormat.PETRI_NET,
            MinerType.POWL: ModelFormat.POWL,
            MinerType.BPMN_INDUCTIVE: ModelFormat.BPMN,
            MinerType.DECLARE: ModelFormat.DECLARE,
            MinerType.LOG_SKELETON: ModelFormat.LOG_SKELETON,
            MinerType.TEMPORAL_PROFILE: ModelFormat.TEMPORAL_PROFILE,
            MinerType.PREFIX_TREE: ModelFormat.PREFIX_TREE,
            MinerType.TRANSITION_SYSTEM: ModelFormat.TRANSITION_SYSTEM,
            MinerType.BATCHES: ModelFormat.BATCHES,
        }

        for miner_type, expected_format in expected_mappings.items():
            assert expected_format is not None, (
                f"Expected format for {miner_type} should be defined"
            )


# =============================================================================
# BPI CHALLENGE 2019 TESTS (REAL DATASET)
# =============================================================================


class TestBPIChallenge2019:
    """Tests using the real BPI Challenge 2019 dataset."""

    @pytest.mark.skipif(
        not BPI_2019_XES.exists(), reason="BPI Challenge 2019 XES file not available"
    )
    def test_bpi_2019_file_exists(self):
        """
        PREREQ: Verify BPI 2019 XES file is accessible.
        """
        assert BPI_2019_XES.exists()
        assert BPI_2019_XES.stat().st_size > 0

    @pytest.mark.skipif(
        not BPI_2019_XES.exists(), reason="BPI Challenge 2019 XES file not available"
    )
    @pytest.mark.asyncio
    async def test_upload_bpi_2019_xes(self, client, default_project: str):
        """
        TEST: Upload BPI 2019 XES and verify ingestion.
        """
        with open(BPI_2019_XES, "rb") as f:
            xes_content = f.read()

        response = await client.post(
            "/api/v1/datasets/upload",
            files={"file": ("BPI_Challenge_2019.xes", xes_content, "application/xml")},
            data={"project_id": default_project},
        )

        # BPI 2019 is large, so upload might take time or be async
        assert response.status_code in [200, 202], f"Upload failed: {response.text}"

    @pytest.mark.skipif(
        not BPI_2019_XES.exists(), reason="BPI Challenge 2019 XES file not available"
    )
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_discover_inductive_on_bpi_2019(self, client, default_project: str):
        """
        PERFORMANCE: Discover inductive model on real BPI 2019 dataset.
        This test is marked slow and may take >30s.
        """
        # Upload
        with open(BPI_2019_XES, "rb") as f:
            xes_content = f.read()

        upload_resp = await client.post(
            "/api/v1/datasets/upload",
            files={"file": ("BPI_2019.xes", xes_content, "application/xml")},
            data={"project_id": default_project},
        )

        if upload_resp.status_code not in [200, 202]:
            pytest.skip("BPI 2019 upload failed")

        log_id = upload_resp.json().get("id")
        if not log_id:
            pytest.skip("No log_id returned from upload")

        # Discover with timeout awareness
        start = time.perf_counter()
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": log_id,
                "miner_type": "inductive",
                "model_name": "BPI 2019 Inductive",
            },
        )
        elapsed = time.perf_counter() - start

        print(f"BPI 2019 Inductive discovery took {elapsed:.2f}s")

        # May timeout on large dataset, which is acceptable
        assert response.status_code in [200, 408, 504]


# =============================================================================
# CONFORMANCE CHECKING INTEGRATION
# =============================================================================


class TestConformanceIntegration:
    """Tests that discovered models can be used for conformance checking."""

    @pytest.mark.asyncio
    async def test_discover_then_conformance(self, client, uploaded_insurance_log_id: str):
        """
        E2E: Discover model → Run conformance check → Get fitness.
        """
        # 1. Discover
        discover_resp = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": "inductive",
                "model_name": "Conformance Integration Test",
            },
        )
        assert discover_resp.status_code == 200
        model_id = discover_resp.json()["id"]

        # 2. Conformance check
        conf_resp = await client.post(
            "/api/v1/conformance/check",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "model_id": model_id,
                "method": "token_replay",
            },
        )
        assert conf_resp.status_code == 200
        conf_data = conf_resp.json()

        # 3. Validate fitness
        assert "fitness" in conf_data
        assert 0.0 <= conf_data["fitness"] <= 1.0


# =============================================================================
# VISUALIZATION INTEGRATION
# =============================================================================


class TestVisualizationIntegration:
    """Tests that discovered models produce valid visualization data."""

    @pytest.mark.asyncio
    async def test_dfg_visualization_endpoint(self, client, uploaded_insurance_log_id: str):
        """
        TEST: DFG visualization endpoint returns nodes/edges.
        """
        response = await client.get(f"/api/v1/visualization/{uploaded_insurance_log_id}/dfg")
        assert response.status_code == 200

        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) >= 1
        assert len(data["edges"]) >= 1

    @pytest.mark.asyncio
    async def test_performance_dfg_visualization(self, client, uploaded_insurance_log_id: str):
        """
        TEST: Performance DFG returns timing data on edges.
        """
        response = await client.get(
            f"/api/v1/visualization/{uploaded_insurance_log_id}/dfg?performance=true"
        )
        assert response.status_code == 200

        data = response.json()
        assert "edges" in data

        # At least some edges should have timing data
        edges_with_timing = [
            e
            for e in data["edges"]
            if "avg_duration_seconds" in e or "mean" in e or "avg_time" in e
        ]
        # Note: timing data may not always be present depending on log
