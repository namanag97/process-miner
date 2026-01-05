"""Comprehensive E2E & Integration Tests for All Process Discovery Algorithms.

This test file covers ALL 16 mining algorithms implemented in the codebase:

Classic Algorithms (7):
    1. Alpha Miner (alpha) -> Petri Net
    2. Alpha+ Miner (alpha_plus) -> Petri Net
    3. Inductive Miner (inductive) -> Process Tree
    4. Inductive Infrequent (inductive_infrequent) -> Process Tree
    5. Heuristics Miner (heuristics) -> Petri Net
    6. DFG (dfg) -> DFG dict
    7. Performance DFG (performance_dfg) -> DFG dict with timing

Advanced Algorithms (9):
    8. ILP Miner (ilp) -> Petri Net
    9. POWL (powl) -> POWL model
    10. BPMN Inductive (bpmn_inductive) -> BPMN model
    11. DECLARE (declare) -> Declare constraints dict
    12. Log Skeleton (log_skeleton) -> LogSkeleton dict
    13. Temporal Profile (temporal_profile) -> Temporal stats dict
    14. Prefix Tree (prefix_tree) -> Trie structure
    15. Transition System (transition_system) -> TS object
    16. Batches (batches) -> Batch activities list
    17. Correlation (correlation) -> DFG-like structure

Run: pytest tests/test_all_discovery_algorithms.py -v --tb=short

Performance Target: Discovery on 100 cases should complete in <5s
"""

import time

import pytest
from httpx import AsyncClient

# =============================================================================
# TEST DATA FIXTURES
# =============================================================================


@pytest.fixture
def minimal_csv() -> bytes:
    """Minimal process: 2 cases, 4 events total. Edge case testing."""
    return b"""case:concept:name,concept:name,time:timestamp
1,Start,2023-01-01 09:00:00
1,End,2023-01-01 10:00:00
2,Start,2023-01-01 11:00:00
2,End,2023-01-01 12:00:00
"""


@pytest.fixture
def single_activity_csv() -> bytes:
    """Degenerate case: Single activity per case."""
    return b"""case:concept:name,concept:name,time:timestamp
1,OnlyActivity,2023-01-01 09:00:00
2,OnlyActivity,2023-01-01 10:00:00
3,OnlyActivity,2023-01-01 11:00:00
"""


@pytest.fixture
def concurrent_activity_csv() -> bytes:
    """Process with parallelism: A -> (B || C) -> D pattern."""
    return b"""case:concept:name,concept:name,time:timestamp,org:resource
1,Start,2023-01-01 09:00:00,System
1,TaskB,2023-01-01 09:30:00,Worker1
1,TaskC,2023-01-01 09:35:00,Worker2
1,End,2023-01-01 10:00:00,System
2,Start,2023-01-01 10:00:00,System
2,TaskC,2023-01-01 10:25:00,Worker2
2,TaskB,2023-01-01 10:30:00,Worker1
2,End,2023-01-01 11:00:00,System
3,Start,2023-01-01 11:00:00,System
3,TaskB,2023-01-01 11:20:00,Worker1
3,TaskC,2023-01-01 11:25:00,Worker2
3,End,2023-01-01 12:00:00,System
"""


@pytest.fixture
def loop_activity_csv() -> bytes:
    """Process with loops: A -> B -> C with B repeating."""
    return b"""case:concept:name,concept:name,time:timestamp
1,Start,2023-01-01 09:00:00
1,Process,2023-01-01 09:30:00
1,Review,2023-01-01 10:00:00
1,Process,2023-01-01 10:30:00
1,Review,2023-01-01 11:00:00
1,End,2023-01-01 11:30:00
2,Start,2023-01-01 12:00:00
2,Process,2023-01-01 12:30:00
2,Review,2023-01-01 13:00:00
2,End,2023-01-01 13:30:00
3,Start,2023-01-01 14:00:00
3,Process,2023-01-01 14:30:00
3,Review,2023-01-01 15:00:00
3,Process,2023-01-01 15:30:00
3,Review,2023-01-01 16:00:00
3,Process,2023-01-01 16:30:00
3,End,2023-01-01 17:00:00
"""


# =============================================================================
# ALL MINER TYPES - PARAMETERIZED TEST DATA
# =============================================================================

# All miners with their expected output format
# Note: ILP miner still has known NetworkX serialization bug
ALL_MINERS = [
    # Classic algorithms
    pytest.param("alpha", "petri_net", id="alpha_miner"),
    pytest.param(
        "alpha_plus", "petri_net", id="alpha_plus_miner"
    ),  # FIXED: fallback to alpha on failure
    pytest.param("inductive", "process_tree", id="inductive_miner"),
    pytest.param("inductive_infrequent", "process_tree", id="inductive_infrequent_miner"),
    pytest.param("heuristics", "petri_net", id="heuristics_miner"),
    pytest.param("dfg", "dfg", id="dfg_miner"),
    pytest.param("performance_dfg", "performance_dfg", id="performance_dfg_miner"),
    # Advanced algorithms
    pytest.param(
        "ilp",
        "petri_net",
        id="ilp_miner",
        marks=pytest.mark.xfail(
            reason="BUG: NetworkXError - fitness evaluation fails with Unicode start marker"
        ),
    ),
    pytest.param("powl", "powl", id="powl_miner"),
    pytest.param("bpmn_inductive", "bpmn", id="bpmn_inductive_miner"),
    pytest.param("declare", "declare", id="declare_miner"),  # FIXED: graceful error handling
    pytest.param(
        "log_skeleton", "log_skeleton", id="log_skeleton_miner"
    ),  # FIXED: set serialization
    pytest.param("temporal_profile", "temporal_profile", id="temporal_profile_miner"),
    pytest.param("prefix_tree", "prefix_tree", id="prefix_tree_miner"),
    pytest.param("transition_system", "transition_system", id="transition_system_miner"),
    pytest.param("batches", "batches", id="batches_miner"),
    pytest.param("correlation", "dfg", id="correlation_miner"),  # FIXED: DFG format handling
]


# Subset for faster smoke testing
CORE_MINERS = [
    pytest.param("alpha", "petri_net", id="alpha"),
    pytest.param("inductive", "process_tree", id="inductive"),
    pytest.param("heuristics", "petri_net", id="heuristics"),
    pytest.param("dfg", "dfg", id="dfg"),
]


# =============================================================================
# TEST CLASS: API ENDPOINT TESTS FOR ALL MINERS
# =============================================================================


class TestAllMinersAPIEndpoint:
    """Tests the /api/v1/discovery/discover endpoint for all miner types."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("miner_type,expected_format", ALL_MINERS)
    async def test_discover_with_all_miners(
        self,
        client: AsyncClient,
        uploaded_insurance_log_id: str,
        miner_type: str,
        expected_format: str,
    ):
        """
        TEST: Each miner type should successfully discover a model via API.

        Validates:
        - HTTP 200 response
        - Model ID returned
        - Correct model_format in response
        """
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": miner_type,
                "model_name": f"Test {miner_type.upper()} Model",
            },
        )

        assert response.status_code == 200, (
            f"Miner {miner_type} failed with status {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "id" in data, f"Miner {miner_type} response missing 'id'"
        assert "miner_type" in data, f"Miner {miner_type} response missing 'miner_type'"
        assert data["miner_type"] == miner_type

        # Verify model format matches expectation
        if "model_format" in data:
            assert data["model_format"] == expected_format, (
                f"Miner {miner_type}: expected format {expected_format}, got {data['model_format']}"
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("miner_type,expected_format", CORE_MINERS)
    async def test_discover_performance_under_5_seconds(
        self,
        client: AsyncClient,
        uploaded_insurance_log_id: str,
        miner_type: str,
        expected_format: str,
    ):
        """
        PERFORMANCE: Core miners must complete discovery in <5 seconds for 100 cases.
        """
        start_time = time.perf_counter()

        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": miner_type,
                "model_name": f"Perf Test {miner_type}",
            },
        )

        elapsed = time.perf_counter() - start_time

        assert response.status_code == 200
        assert elapsed < 5.0, f"Miner {miner_type} took {elapsed:.2f}s, exceeds 5s threshold"

    @pytest.mark.asyncio
    async def test_list_miners_returns_all_types(self, client: AsyncClient):
        """
        TEST: GET /discovery/miners should list all available miner types.
        """
        response = await client.get("/api/v1/discovery/miners")
        assert response.status_code == 200

        miners = response.json()
        assert isinstance(miners, list)

        # Extract miner type values
        miner_types = {m.get("type", m.get("id", "")).lower() for m in miners}

        # Verify core miners are present
        expected_miners = {
            "alpha",
            "inductive",
            "heuristics",
            "dfg",
            "ilp",
            "powl",
            "bpmn_inductive",
        }
        for expected in expected_miners:
            assert any(expected in mt for mt in miner_types), (
                f"Expected miner '{expected}' not found in {miner_types}"
            )


# =============================================================================
# TEST CLASS: MODEL RETRIEVAL AND PERSISTENCE
# =============================================================================


class TestModelPersistenceAllMiners:
    """Tests that discovered models can be retrieved and have correct data."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("miner_type,expected_format", CORE_MINERS)
    async def test_discovered_model_can_be_retrieved(
        self,
        client: AsyncClient,
        uploaded_insurance_log_id: str,
        miner_type: str,
        expected_format: str,
    ):
        """
        TEST: Discover → Retrieve → Validate model data integrity.
        """
        # Discover
        discover_resp = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": miner_type,
                "model_name": f"Persistence Test {miner_type}",
            },
        )
        assert discover_resp.status_code == 200
        model_id = discover_resp.json()["id"]

        # Retrieve
        get_resp = await client.get(f"/api/v1/discovery/models/{model_id}")
        assert get_resp.status_code == 200

        model = get_resp.json()
        assert model["id"] == model_id
        assert model["miner_type"] == miner_type
        assert model["dataset_id"] == uploaded_insurance_log_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize("miner_type,expected_format", CORE_MINERS)
    async def test_discovered_model_can_be_deleted(
        self,
        client: AsyncClient,
        uploaded_insurance_log_id: str,
        miner_type: str,
        expected_format: str,
    ):
        """
        TEST: Discover → Delete → Verify 404 on retrieval.
        """
        # Discover
        discover_resp = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": miner_type,
                "model_name": f"Delete Test {miner_type}",
            },
        )
        assert discover_resp.status_code == 200
        model_id = discover_resp.json()["id"]

        # Delete
        delete_resp = await client.delete(f"/api/v1/discovery/models/{model_id}")
        assert delete_resp.status_code == 200

        # Verify deleted
        get_resp = await client.get(f"/api/v1/discovery/models/{model_id}")
        assert get_resp.status_code == 404


# =============================================================================
# TEST CLASS: EDGE CASES AND ERROR HANDLING
# =============================================================================


class TestAlgorithmEdgeCases:
    """Tests edge cases: minimal data, degenerate logs, invalid inputs."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("miner_type,expected_format", CORE_MINERS)
    async def test_discover_with_minimal_log(
        self,
        client: AsyncClient,
        minimal_csv: bytes,
        default_project: str,
        miner_type: str,
        expected_format: str,
    ):
        """
        EDGE CASE: Discovery on minimal log (2 cases, 4 events).
        Should succeed or return meaningful error.
        """
        # Upload minimal log
        upload_resp = await client.post(
            "/api/v1/datasets/upload",
            files={"file": ("minimal.csv", minimal_csv, "text/csv")},
            data={"project_id": default_project},
        )
        assert upload_resp.status_code == 200
        log_id = upload_resp.json()["id"]

        # Attempt discovery
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": log_id,
                "miner_type": miner_type,
                "model_name": f"Minimal {miner_type}",
            },
        )

        # Either succeeds or returns meaningful error (not 500)
        assert response.status_code in [200, 400, 422], (
            f"Miner {miner_type} on minimal data returned unexpected {response.status_code}"
        )

    @pytest.mark.asyncio
    async def test_discover_with_nonexistent_dataset(self, client: AsyncClient):
        """
        ERROR: Discovery with non-existent dataset_id should return 404.
        """
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": "nonexistent-uuid-12345",
                "miner_type": "inductive",
                "model_name": "Should Fail",
            },
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_discover_with_invalid_miner_type(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """
        ERROR: Discovery with invalid miner_type should return 400/422.
        """
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": "this_miner_does_not_exist",
                "model_name": "Should Fail",
            },
        )
        assert response.status_code in [400, 422]
        error_data = response.json()
        assert "error" in error_data or "detail" in error_data


# =============================================================================
# TEST CLASS: QUALITY METRICS VALIDATION
# =============================================================================


class TestQualityMetrics:
    """Tests fitness and precision metrics for applicable miners."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "miner_type",
        ["alpha", "inductive", "heuristics", "ilp"],
        ids=["alpha", "inductive", "heuristics", "ilp"],
    )
    async def test_petri_net_miners_have_fitness(
        self, client: AsyncClient, uploaded_insurance_log_id: str, miner_type: str
    ):
        """
        TEST: Petri-net producing miners should return fitness metric.
        """
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": miner_type,
                "model_name": f"Quality Test {miner_type}",
            },
        )
        assert response.status_code == 200
        data = response.json()

        # Fitness should be present and in valid range
        if "fitness" in data and data["fitness"] is not None:
            assert 0.0 <= data["fitness"] <= 1.0, f"Fitness {data['fitness']} out of range [0, 1]"

    @pytest.mark.asyncio
    async def test_self_discovered_model_high_fitness(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """
        TEST: A model discovered from its source log should have fitness >= 0.5.
        """
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": "inductive",
                "model_name": "Self-Fitness Test",
            },
        )
        assert response.status_code == 200
        data = response.json()

        if "fitness" in data and data["fitness"] is not None:
            assert data["fitness"] >= 0.5, (
                f"Self-discovered model has low fitness: {data['fitness']}"
            )


# =============================================================================
# TEST CLASS: E2E FULL FLOW
# =============================================================================


class TestE2EAlgorithmFlow:
    """Full end-to-end flow: Upload → Discover → Retrieve → Delete."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("miner_type,expected_format", ALL_MINERS)
    async def test_full_e2e_flow_all_miners(
        self,
        client: AsyncClient,
        default_project: str,
        miner_type: str,
        expected_format: str,
    ):
        """
        E2E: Upload CSV → Discover with miner → Retrieve model → Delete model.
        """
        # 1. Upload test data
        csv_data = b"""case:concept:name,concept:name,time:timestamp,org:resource
1,Register,2023-01-01 09:00:00,John
1,Examine,2023-01-01 09:30:00,Sarah
1,Decide,2023-01-01 10:00:00,Mike
1,Complete,2023-01-01 10:30:00,John
2,Register,2023-01-01 10:00:00,Sarah
2,Examine,2023-01-01 10:30:00,Mike
2,Decide,2023-01-01 11:00:00,John
2,Complete,2023-01-01 11:30:00,Sarah
3,Register,2023-01-01 11:00:00,Mike
3,Examine,2023-01-01 11:30:00,John
3,Decide,2023-01-01 12:00:00,Sarah
3,Complete,2023-01-01 12:30:00,Mike
"""

        upload_resp = await client.post(
            "/api/v1/datasets/upload",
            files={"file": (f"e2e_{miner_type}.csv", csv_data, "text/csv")},
            data={"project_id": default_project},
        )
        assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.text}"
        log_id = upload_resp.json()["id"]

        # 2. Discover model
        discover_resp = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": log_id,
                "miner_type": miner_type,
                "model_name": f"E2E Test {miner_type}",
            },
        )
        assert discover_resp.status_code == 200, (
            f"Discovery failed for {miner_type}: {discover_resp.text}"
        )
        model_id = discover_resp.json()["id"]

        # 3. Retrieve model
        get_resp = await client.get(f"/api/v1/discovery/models/{model_id}")
        assert get_resp.status_code == 200
        model_data = get_resp.json()
        assert model_data["miner_type"] == miner_type
        assert model_data["model_format"] == expected_format

        # 4. Delete model
        delete_resp = await client.delete(f"/api/v1/discovery/models/{model_id}")
        assert delete_resp.status_code == 200

        # 5. Verify deletion
        verify_resp = await client.get(f"/api/v1/discovery/models/{model_id}")
        assert verify_resp.status_code == 404


# =============================================================================
# TEST CLASS: ADVANCED ALGORITHMS SPECIFIC TESTS
# =============================================================================


class TestAdvancedAlgorithms:
    """Specific tests for advanced PM4Py algorithms."""

    @pytest.mark.asyncio
    async def test_declare_returns_constraints(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """
        TEST: DECLARE miner should return declarative constraints.
        """
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": "declare",
                "model_name": "Declare Constraints",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_format"] == "declare"

    @pytest.mark.asyncio
    async def test_temporal_profile_returns_timing(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """
        TEST: Temporal Profile miner should return timing statistics.
        """
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": "temporal_profile",
                "model_name": "Temporal Stats",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_format"] == "temporal_profile"

    @pytest.mark.asyncio
    async def test_bpmn_returns_bpmn_format(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """
        TEST: BPMN Inductive miner should return BPMN model.
        """
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": "bpmn_inductive",
                "model_name": "BPMN Model",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_format"] == "bpmn"

    @pytest.mark.asyncio
    async def test_powl_returns_powl_format(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """
        TEST: POWL miner should return POWL model format.
        """
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": "powl",
                "model_name": "POWL Model",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_format"] == "powl"

    @pytest.mark.asyncio
    async def test_ilp_returns_petri_net(self, client: AsyncClient, uploaded_insurance_log_id: str):
        """
        TEST: ILP miner should return Petri net format.
        """
        response = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": uploaded_insurance_log_id,
                "miner_type": "ilp",
                "model_name": "ILP Petri Net",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_format"] == "petri_net"


# =============================================================================
# TEST CLASS: COMPARISON TESTS
# =============================================================================


class TestAlgorithmComparison:
    """Tests that compare multiple algorithms on the same dataset."""

    @pytest.mark.asyncio
    async def test_all_petri_net_miners_produce_valid_models(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """
        TEST: All Petri net producing miners should create valid models.
        """
        petri_net_miners = ["alpha", "alpha_plus", "heuristics", "ilp"]

        for miner_type in petri_net_miners:
            response = await client.post(
                "/api/v1/discovery/discover?async_mode=false",
                json={
                    "dataset_id": uploaded_insurance_log_id,
                    "miner_type": miner_type,
                    "model_name": f"Comparison {miner_type}",
                },
            )
            assert response.status_code == 200, f"Miner {miner_type} failed"
            data = response.json()
            assert data["model_format"] == "petri_net", (
                f"Miner {miner_type} did not produce petri_net"
            )

    @pytest.mark.asyncio
    async def test_dfg_vs_performance_dfg(
        self, client: AsyncClient, uploaded_insurance_log_id: str
    ):
        """
        TEST: DFG and Performance DFG should both succeed on same data.
        """
        for miner_type in ["dfg", "performance_dfg"]:
            response = await client.post(
                "/api/v1/discovery/discover?async_mode=false",
                json={
                    "dataset_id": uploaded_insurance_log_id,
                    "miner_type": miner_type,
                    "model_name": f"DFG Comparison {miner_type}",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert miner_type in data["model_format"]
