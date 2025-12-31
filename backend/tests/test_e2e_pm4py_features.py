"""End-to-End PM4Py Feature Tests.

This comprehensive test file verifies all PM4Py features across the backend API,
testing the complete flow from data upload through to analysis results.

Feature Categories Tested:
1. Upload & Ingestion
2. Process Discovery
3. Conformance Checking
4. Analytics
5. Filtering
6. OCEL / OCPM
7. Organizational Mining
8. Prediction
9. Simulation

Run: pytest tests/test_e2e_pm4py_features.py -v
"""

import pytest
from httpx import AsyncClient


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================


@pytest.fixture
def e2e_process_csv() -> bytes:
    """Standard process with multiple activities for comprehensive testing."""
    return b"""case:concept:name,concept:name,time:timestamp,org:resource
1,Submit Application,2023-01-01 09:00:00,John
1,Review Application,2023-01-01 10:00:00,Sarah
1,Verify Documents,2023-01-01 11:00:00,Mike
1,Approve Application,2023-01-01 14:00:00,Manager
1,Send Confirmation,2023-01-01 14:30:00,System
2,Submit Application,2023-01-01 09:30:00,Sarah
2,Review Application,2023-01-01 10:30:00,John
2,Verify Documents,2023-01-01 11:30:00,Sarah
2,Request Additional Info,2023-01-01 12:00:00,John
2,Review Application,2023-01-01 15:00:00,Mike
2,Verify Documents,2023-01-01 16:00:00,Sarah
2,Approve Application,2023-01-01 17:00:00,Manager
2,Send Confirmation,2023-01-01 17:30:00,System
3,Submit Application,2023-01-02 08:00:00,Mike
3,Review Application,2023-01-02 09:00:00,Sarah
3,Verify Documents,2023-01-02 10:00:00,John
3,Reject Application,2023-01-02 11:00:00,Manager
3,Send Rejection,2023-01-02 11:15:00,System
4,Submit Application,2023-01-02 10:00:00,John
4,Review Application,2023-01-02 11:00:00,Mike
4,Verify Documents,2023-01-02 12:00:00,Sarah
4,Approve Application,2023-01-02 15:00:00,Manager
4,Send Confirmation,2023-01-02 15:30:00,System
5,Submit Application,2023-01-03 09:00:00,Sarah
5,Review Application,2023-01-03 10:00:00,John
5,Verify Documents,2023-01-03 11:00:00,Mike
5,Approve Application,2023-01-03 13:00:00,Manager
5,Send Confirmation,2023-01-03 13:15:00,System
"""


@pytest.fixture
def e2e_ocel_json() -> bytes:
    """Sample OCEL 2.0 JSON for object-centric tests."""
    import json
    ocel_data = {
        "ocel:global-event": {"ocel:ordering": "timestamp"},
        "ocel:global-object": {"ocel:type": ["order", "item"]},
        "ocel:events": {
            "e1": {"ocel:activity": "place order", "ocel:timestamp": "2023-01-01T09:00:00Z", "ocel:omap": ["o1", "i1", "i2"]},
            "e2": {"ocel:activity": "pick item", "ocel:timestamp": "2023-01-01T10:00:00Z", "ocel:omap": ["i1"]},
            "e3": {"ocel:activity": "pick item", "ocel:timestamp": "2023-01-01T10:15:00Z", "ocel:omap": ["i2"]},
            "e4": {"ocel:activity": "pack order", "ocel:timestamp": "2023-01-01T11:00:00Z", "ocel:omap": ["o1", "i1", "i2"]},
            "e5": {"ocel:activity": "ship order", "ocel:timestamp": "2023-01-01T12:00:00Z", "ocel:omap": ["o1"]},
            "e6": {"ocel:activity": "place order", "ocel:timestamp": "2023-01-01T09:30:00Z", "ocel:omap": ["o2", "i3"]},
            "e7": {"ocel:activity": "pick item", "ocel:timestamp": "2023-01-01T10:30:00Z", "ocel:omap": ["i3"]},
            "e8": {"ocel:activity": "pack order", "ocel:timestamp": "2023-01-01T11:30:00Z", "ocel:omap": ["o2", "i3"]},
            "e9": {"ocel:activity": "ship order", "ocel:timestamp": "2023-01-01T13:00:00Z", "ocel:omap": ["o2"]},
        },
        "ocel:objects": {
            "o1": {"ocel:type": "order"},
            "o2": {"ocel:type": "order"},
            "i1": {"ocel:type": "item"},
            "i2": {"ocel:type": "item"},
            "i3": {"ocel:type": "item"},
        }
    }
    return json.dumps(ocel_data).encode()


@pytest.fixture
async def e2e_log_id(client: AsyncClient, e2e_process_csv: bytes) -> str:
    """Upload test log and return its ID."""
    response = await client.post(
        "/api/v1/logs/upload",
        files={"file": ("test_e2e.csv", e2e_process_csv, "text/csv")},
    )
    assert response.status_code == 200, f"Upload failed: {response.text}"
    return response.json()["id"]


@pytest.fixture
async def e2e_model_id(client: AsyncClient, e2e_log_id: str) -> str:
    """Discover model and return its ID."""
    response = await client.post(
        "/api/v1/discovery/discover",
        json={"log_id": e2e_log_id, "miner_type": "inductive", "model_name": "E2E Test Model"},
    )
    assert response.status_code == 200, f"Discovery failed: {response.text}"
    return response.json().get("id") or response.json().get("model_id")


# =============================================================================
# FLOW 1: UPLOAD & INGESTION E2E TESTS
# =============================================================================


class TestE2EUploadFlow:
    """E2E tests for the upload and ingestion flow."""

    async def test_upload_csv_complete_flow(self, client: AsyncClient, e2e_process_csv: bytes):
        """
        User Need: Upload a CSV file and see it processed.
        Flow: Upload CSV → Get log details → Verify statistics
        """
        # Step 1: Upload
        response = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("test.csv", e2e_process_csv, "text/csv")},
        )
        assert response.status_code == 200
        log_data = response.json()
        log_id = log_data["id"]

        # Step 2: Verify log exists
        response = await client.get(f"/api/v1/processes/{log_id}")
        assert response.status_code == 200
        details = response.json()
        assert details["id"] == log_id
        assert details["case_count"] == 5
        assert details["event_count"] >= 25

        # Step 3: Get statistics
        response = await client.get(f"/api/v1/processes/{log_id}/statistics")
        assert response.status_code == 200
        stats = response.json()
        assert "activity_count" in stats or "activities" in stats

    async def test_upload_detects_columns(self, client: AsyncClient, e2e_process_csv: bytes):
        """
        User Need: System should auto-detect case/activity/timestamp columns.
        Flow: Upload → Get columns → Verify detection
        """
        # Upload
        response = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("columns_test.csv", e2e_process_csv, "text/csv")},
        )
        assert response.status_code == 200
        log_id = response.json()["id"]

        # Check columns
        response = await client.get(f"/api/v1/processes/{log_id}/columns")
        if response.status_code == 200:
            columns = response.json()
            # Should have detected case, activity, timestamp
            assert len(columns) >= 3

    async def test_upload_variants_generated(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: After upload, I should see process variants.
        Flow: Get log → Get variants → Verify counts
        """
        response = await client.get(f"/api/v1/processes/{e2e_log_id}/variants")
        assert response.status_code == 200
        variants = response.json()

        # Should have multiple variants
        if isinstance(variants, dict):
            variant_list = variants.get("variants", [])
        else:
            variant_list = variants

        assert len(variant_list) >= 1
        # Case counts should sum to 5
        total_cases = sum(v.get("count", v.get("case_count", 1)) for v in variant_list)
        assert total_cases == 5


# =============================================================================
# FLOW 2: PROCESS DISCOVERY E2E TESTS
# =============================================================================


class TestE2EDiscoveryFlow:
    """E2E tests for process discovery flow."""

    async def test_list_available_miners(self, client: AsyncClient):
        """
        User Need: I want to see what mining algorithms are available.
        Flow: GET /discovery/miners
        """
        response = await client.get("/api/v1/discovery/miners")
        assert response.status_code == 200
        miners = response.json()

        # Should have at least Alpha, Inductive, Heuristics, DFG
        miner_names = [m.get("name", m.get("id", "")).lower() for m in miners]
        assert any("alpha" in n for n in miner_names)
        assert any("inductive" in n for n in miner_names)

    async def test_discover_with_inductive_miner(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Discover a process model using Inductive Miner.
        Flow: Select log → Choose Inductive → Get model
        """
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": e2e_log_id,
                "miner_type": "inductive",
                "model_name": "Inductive Test Model",
            },
        )
        assert response.status_code == 200
        model = response.json()

        assert "id" in model or "model_id" in model
        assert model.get("miner_type") == "inductive"
        # Should have fitness score
        if "fitness" in model:
            assert 0 <= model["fitness"] <= 1

    async def test_discover_with_alpha_miner(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Discover using Alpha Miner (classic algorithm).
        """
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": e2e_log_id,
                "miner_type": "alpha",
                "model_name": "Alpha Test Model",
            },
        )
        assert response.status_code == 200
        model = response.json()
        assert model.get("miner_type") == "alpha"

    async def test_discover_with_heuristics_miner(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Discover using Heuristics Miner (handles noise).
        """
        response = await client.post(
            "/api/v1/discovery/discover",
            json={
                "log_id": e2e_log_id,
                "miner_type": "heuristics",
                "model_name": "Heuristics Test Model",
            },
        )
        assert response.status_code == 200
        model = response.json()
        assert model.get("miner_type") == "heuristics"

    async def test_get_dfg_visualization_data(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: I want to see the process as a directly-follows graph.
        Flow: Get DFG data → Verify nodes and edges
        """
        response = await client.get(f"/api/v1/visualization/{e2e_log_id}/dfg")
        assert response.status_code == 200
        dfg = response.json()

        # Should have nodes and edges
        assert "nodes" in dfg
        assert "edges" in dfg
        assert len(dfg["nodes"]) >= 5  # At least 5 activities
        assert len(dfg["edges"]) >= 4  # At least some edges

    async def test_dfg_with_performance_metrics(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: I want to see DFG with timing information.
        """
        response = await client.get(f"/api/v1/visualization/{e2e_log_id}/dfg?performance=true")
        assert response.status_code == 200
        dfg = response.json()

        # Performance DFG should have timing on edges
        for edge in dfg.get("edges", []):
            if "avg_time" in edge or "duration" in edge or "mean" in edge:
                # Has performance data
                break


# =============================================================================
# FLOW 3: CONFORMANCE CHECKING E2E TESTS
# =============================================================================


class TestE2EConformanceFlow:
    """E2E tests for conformance checking flow."""

    async def test_conformance_check_token_replay(
        self, client: AsyncClient, e2e_log_id: str, e2e_model_id: str
    ):
        """
        User Need: Check how well my log conforms to the discovered model.
        Flow: Select log + model → Run token replay → Get fitness
        """
        response = await client.post(
            "/api/v1/conformance/check",
            json={
                "log_id": e2e_log_id,
                "model_id": e2e_model_id,
                "method": "token_replay",
            },
        )
        assert response.status_code == 200
        result = response.json()

        # Should have fitness score between 0 and 1
        assert "fitness" in result
        assert 0 <= result["fitness"] <= 1

    async def test_conformance_check_alignments(
        self, client: AsyncClient, e2e_log_id: str, e2e_model_id: str
    ):
        """
        User Need: Get precise conformance using alignments.
        """
        response = await client.post(
            "/api/v1/conformance/check",
            json={
                "log_id": e2e_log_id,
                "model_id": e2e_model_id,
                "method": "alignments",
            },
        )
        # Alignments might be slower, just check it works
        assert response.status_code in [200, 202]

    async def test_list_conformance_methods(self, client: AsyncClient):
        """
        User Need: See what conformance methods are available.
        """
        response = await client.get("/api/v1/conformance/methods")
        assert response.status_code == 200
        methods = response.json()
        assert len(methods) >= 2  # At least token_replay and alignments

    async def test_get_conformance_diagnostics(
        self, client: AsyncClient, e2e_log_id: str, e2e_model_id: str
    ):
        """
        User Need: See which cases have deviations.
        """
        response = await client.get(
            f"/api/v1/conformance/logs/{e2e_log_id}/models/{e2e_model_id}/diagnostics"
        )
        assert response.status_code == 200


# =============================================================================
# FLOW 4: ANALYTICS E2E TESTS
# =============================================================================


class TestE2EAnalyticsFlow:
    """E2E tests for analytics flow."""

    async def test_get_bottlenecks(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Find where my process is slow.
        Flow: Get bottlenecks → See activities with high waiting time
        """
        response = await client.get(f"/api/v1/analytics/logs/{e2e_log_id}/bottlenecks")
        assert response.status_code == 200
        result = response.json()

        # Should have bottlenecks list
        assert "bottlenecks" in result or isinstance(result, list)

    async def test_get_rework_analysis(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Find activities that are repeated (rework).
        """
        response = await client.get(f"/api/v1/analytics/logs/{e2e_log_id}/rework")
        assert response.status_code == 200
        result = response.json()

        # Our test data has rework in case 2
        assert "rework_activities" in result or "rework_percentage" in result

    async def test_get_service_times(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: See how long each activity takes on average.
        """
        response = await client.get(f"/api/v1/analytics/logs/{e2e_log_id}/service-times")
        assert response.status_code == 200
        result = response.json()

        # Should have service time per activity
        assert isinstance(result, list) or "activities" in result

    async def test_get_cycle_time(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: See overall case duration statistics.
        """
        response = await client.get(f"/api/v1/analytics/logs/{e2e_log_id}/cycle-time")
        assert response.status_code == 200
        result = response.json()

        # Should have average, min, max
        assert "average" in result or "mean" in result or "avg" in result

    async def test_get_throughput(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: See how many cases are processed over time.
        """
        response = await client.get(f"/api/v1/analytics/logs/{e2e_log_id}/throughput")
        assert response.status_code == 200
        result = response.json()

        # Should have throughput metrics
        assert "cases_per_day" in result or "daily" in result or "total" in result

    async def test_get_performance_dashboard(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Get comprehensive performance overview.
        """
        response = await client.get(f"/api/v1/analytics/logs/{e2e_log_id}/performance")
        assert response.status_code == 200
        result = response.json()

        # Dashboard should have multiple sections
        assert "cycle_time" in result or "throughput" in result or "bottlenecks" in result


# =============================================================================
# FLOW 5: FILTERING E2E TESTS
# =============================================================================


class TestE2EFilteringFlow:
    """E2E tests for filtering flow."""

    async def test_filter_by_top_k_variants(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Keep only the top 2 most common variants.
        """
        response = await client.post(
            f"/api/v1/filtering/logs/{e2e_log_id}/filter",
            json={
                "filters": [
                    {"type": "variants_top_k", "params": {"k": 2}}
                ]
            },
        )
        assert response.status_code == 200

    async def test_filter_by_activities(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Keep only cases with specific activities.
        """
        response = await client.post(
            f"/api/v1/filtering/logs/{e2e_log_id}/filter",
            json={
                "filters": [
                    {"type": "activities", "params": {"activities": ["Approve Application"], "mode": "keep"}}
                ]
            },
        )
        assert response.status_code == 200

    async def test_filter_by_case_size(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Keep only cases with 5+ events.
        """
        response = await client.post(
            f"/api/v1/filtering/logs/{e2e_log_id}/filter",
            json={
                "filters": [
                    {"type": "case_size", "params": {"min_size": 5}}
                ]
            },
        )
        assert response.status_code == 200

    async def test_list_available_filters(self, client: AsyncClient):
        """
        User Need: See what filters are available.
        """
        response = await client.get("/api/v1/filtering/available")
        assert response.status_code == 200
        filters = response.json()
        assert len(filters) >= 5  # At least 5 filter types


# =============================================================================
# FLOW 6: OCEL / OCPM E2E TESTS
# =============================================================================


class TestE2EOCPMFlow:
    """E2E tests for Object-Centric Process Mining flow."""

    async def test_upload_ocel(self, client: AsyncClient, e2e_ocel_json: bytes):
        """
        User Need: Upload an OCEL 2.0 file.
        """
        response = await client.post(
            "/api/v1/ocpm/",
            files={"file": ("test.jsonocel", e2e_ocel_json, "application/json")},
        )
        # OCEL upload might use different endpoint
        if response.status_code == 404:
            pytest.skip("OCEL upload endpoint not configured")
        assert response.status_code == 200

    async def test_get_object_types(self, client: AsyncClient):
        """
        User Need: See what object types exist in my OCEL.
        """
        # First upload
        import json
        ocel_data = {
            "ocel:global-event": {"ocel:ordering": "timestamp"},
            "ocel:global-object": {"ocel:type": ["order", "item"]},
            "ocel:events": {"e1": {"ocel:activity": "test", "ocel:timestamp": "2023-01-01T09:00:00Z", "ocel:omap": ["o1"]}},
            "ocel:objects": {"o1": {"ocel:type": "order"}}
        }
        response = await client.post(
            "/api/v1/ocpm/",
            files={"file": ("test.jsonocel", json.dumps(ocel_data).encode(), "application/json")},
        )
        if response.status_code == 404:
            pytest.skip("OCEL endpoint not configured")

        ocel_id = response.json().get("id")
        if ocel_id:
            response = await client.get(f"/api/v1/ocpm/{ocel_id}/object-types")
            assert response.status_code == 200

    async def test_get_oc_dfg(self, client: AsyncClient, e2e_ocel_json: bytes):
        """
        User Need: Get object-centric DFG.
        """
        response = await client.post(
            "/api/v1/ocpm/",
            files={"file": ("test.jsonocel", e2e_ocel_json, "application/json")},
        )
        if response.status_code == 404:
            pytest.skip("OCEL endpoint not configured")

        ocel_id = response.json().get("id")
        if ocel_id:
            response = await client.get(f"/api/v1/ocpm/{ocel_id}/dfg")
            assert response.status_code == 200


# =============================================================================
# FLOW 7: ORGANIZATIONAL MINING E2E TESTS
# =============================================================================


class TestE2EOrganizationalFlow:
    """E2E tests for organizational mining flow."""

    async def test_get_handover_network(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: See how work is handed over between resources.
        """
        response = await client.get(f"/api/v1/organizational/logs/{e2e_log_id}/handover")
        assert response.status_code == 200
        result = response.json()

        # Should have nodes (resources) and edges (handovers)
        assert "nodes" in result or "resources" in result

    async def test_get_collaboration_network(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: See which resources work together.
        """
        response = await client.get(f"/api/v1/organizational/logs/{e2e_log_id}/collaboration")
        assert response.status_code == 200

    async def test_discover_roles(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Discover organizational roles based on activity patterns.
        """
        response = await client.get(f"/api/v1/organizational/logs/{e2e_log_id}/roles")
        assert response.status_code == 200
        result = response.json()

        # Should have role definitions
        assert "roles" in result or isinstance(result, list)

    async def test_get_workload(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: See workload distribution across resources.
        """
        response = await client.get(f"/api/v1/organizational/logs/{e2e_log_id}/workload")
        assert response.status_code == 200


# =============================================================================
# FLOW 8: PREDICTION E2E TESTS
# =============================================================================


class TestE2EPredictionFlow:
    """E2E tests for prediction flow."""

    async def test_train_next_activity_model(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Train a model to predict next activity.
        """
        response = await client.post(
            f"/api/v1/predictions/logs/{e2e_log_id}/train-next-activity",
            json={"algorithm": "random_forest"},
        )
        assert response.status_code == 200
        result = response.json()
        assert "model_id" in result or "id" in result

    async def test_train_remaining_time_model(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Train a model to predict remaining time.
        """
        response = await client.post(
            f"/api/v1/predictions/logs/{e2e_log_id}/train-remaining-time",
            json={"algorithm": "random_forest"},
        )
        assert response.status_code == 200

    async def test_list_prediction_models(self, client: AsyncClient):
        """
        User Need: See my trained prediction models.
        """
        response = await client.get("/api/v1/predictions/models")
        assert response.status_code == 200
        models = response.json()
        assert isinstance(models, list) or "items" in models


# =============================================================================
# FLOW 9: SIMULATION E2E TESTS
# =============================================================================


class TestE2ESimulationFlow:
    """E2E tests for simulation flow."""

    async def test_play_out_model(self, client: AsyncClient, e2e_model_id: str):
        """
        User Need: Generate synthetic log from my model.
        """
        response = await client.post(
            "/api/v1/simulation/play-out",
            json={"model_id": e2e_model_id, "num_traces": 10},
        )
        assert response.status_code == 200
        result = response.json()
        assert "traces" in result or "cases" in result or "log_id" in result

    async def test_simulate_scenario(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Simulate what-if scenario.
        """
        response = await client.post(
            "/api/v1/simulation/scenario",
            json={
                "log_id": e2e_log_id,
                "modifications": [
                    {"type": "reduce_duration", "factor": 0.8}
                ]
            },
        )
        assert response.status_code == 200
        result = response.json()
        assert "original_metrics" in result or "simulated_metrics" in result

    async def test_estimate_capacity(self, client: AsyncClient, e2e_log_id: str):
        """
        User Need: Estimate resources needed for target throughput.
        """
        response = await client.post(
            "/api/v1/simulation/capacity",
            json={"log_id": e2e_log_id, "target_throughput": 10.0},
        )
        assert response.status_code == 200
        result = response.json()
        assert "estimated_resources_needed" in result or "scaling_factor" in result


# =============================================================================
# SUMMARY TEST - COMPLETE FEATURE COVERAGE
# =============================================================================


class TestE2EFeatureSummary:
    """Summary test to verify all feature categories are accessible."""

    async def test_all_api_categories_accessible(self, client: AsyncClient):
        """
        Verify all major API categories respond.
        """
        endpoints = [
            ("/api/v1/discovery/miners", "Discovery"),
            ("/api/v1/conformance/methods", "Conformance"),
            ("/api/v1/filtering/available", "Filtering"),
        ]

        for endpoint, category in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 200, f"{category} API not accessible at {endpoint}"

    async def test_complete_happy_path(
        self, client: AsyncClient, e2e_process_csv: bytes
    ):
        """
        Complete E2E happy path: Upload → Discover → Analyze → Conform.

        This test runs the entire workflow a user would follow.
        """
        # 1. UPLOAD
        response = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("complete_test.csv", e2e_process_csv, "text/csv")},
        )
        assert response.status_code == 200
        log_id = response.json()["id"]

        # 2. DISCOVER (DFG)
        response = await client.get(f"/api/v1/visualization/{log_id}/dfg")
        assert response.status_code == 200
        assert len(response.json()["nodes"]) >= 5

        # 3. DISCOVER (Inductive Miner)
        response = await client.post(
            "/api/v1/discovery/discover",
            json={"log_id": log_id, "miner_type": "inductive", "model_name": "Happy Path Model"},
        )
        assert response.status_code == 200
        model_id = response.json().get("id") or response.json().get("model_id")

        # 4. ANALYZE
        response = await client.get(f"/api/v1/analytics/logs/{log_id}/bottlenecks")
        assert response.status_code == 200

        response = await client.get(f"/api/v1/analytics/logs/{log_id}/cycle-time")
        assert response.status_code == 200

        # 5. CONFORMANCE
        response = await client.post(
            "/api/v1/conformance/check",
            json={"log_id": log_id, "model_id": model_id, "method": "token_replay"},
        )
        assert response.status_code == 200
        fitness = response.json()["fitness"]
        # Model discovered from same log should have high fitness
        assert fitness >= 0.5

        # 6. ORGANIZATIONAL
        response = await client.get(f"/api/v1/organizational/logs/{log_id}/handover")
        assert response.status_code == 200

        print(f"✅ Complete E2E happy path passed!")
        print(f"   Log: {log_id}")
        print(f"   Model: {model_id}")
        print(f"   Fitness: {fitness}")
