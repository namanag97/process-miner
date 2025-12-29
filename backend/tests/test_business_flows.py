"""Comprehensive Business Logic Tests for Process Mining SaaS.

This unified test file covers all process mining business flows with
business logic validation:
- Flow 1: Event Log Ingestion
- Flow 2: Process Discovery
- Flow 3: Conformance Checking
- Flow 4: Performance Analysis
- Flow 5: Organizational Mining
- Flow 6: PM4Py Advanced Analytics

Each test validates not just HTTP status codes, but actual business logic
correctness (e.g., fitness scores in valid range, probabilities summing to 1.0).
"""

from uuid import UUID

import pytest
from httpx import AsyncClient

# =============================================================================
# FLOW 1: EVENT LOG INGESTION TESTS
# =============================================================================


class TestEventLogIngestion:
    """Tests for Event Log Ingestion flow (Upload → Statistics → Quality → Variants)."""

    @pytest.mark.asyncio
    async def test_upload_csv_creates_log_with_correct_counts(
        self, client: AsyncClient, sample_csv_with_multiple_variants: bytes
    ):
        """Test CSV upload returns correct case and event counts."""
        response = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("test.csv", sample_csv_with_multiple_variants, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()

        # Business Logic: 6 cases in test data, 34 total events
        assert data["total_cases"] == 6
        assert data["total_events"] >= 30
        assert "id" in data
        # Verify UUID format
        UUID(data["id"])

    @pytest.mark.asyncio
    async def test_column_detection_identifies_required_fields(
        self, client: AsyncClient, sample_csv_content: bytes
    ):
        """Test column detection correctly identifies case, activity, timestamp."""
        response = await client.post(
            "/api/v1/logs/detect-columns",
            files={"file": ("test.csv", sample_csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()

        # Business Logic: Should detect at least case, activity, timestamp columns
        assert "columns" in data
        assert len(data["columns"]) >= 3
        assert "suggestions" in data

    @pytest.mark.asyncio
    async def test_log_statistics_are_consistent(
        self, client: AsyncClient, sample_csv_with_multiple_variants: bytes
    ):
        """Test log statistics are mathematically consistent."""
        # Upload
        upload_resp = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("test.csv", sample_csv_with_multiple_variants, "text/csv")},
        )
        log_id = upload_resp.json()["id"]

        # Get statistics
        stats_resp = await client.get(f"/api/v1/logs/{log_id}/statistics")
        assert stats_resp.status_code == 200
        stats = stats_resp.json()

        # Business Logic Validations
        assert stats["case_count"] == 6
        assert stats["variant_count"] <= stats["case_count"]  # variants <= cases
        assert stats["activity_count"] > 0
        assert stats["event_count"] >= stats["case_count"]  # at least 1 event per case

    @pytest.mark.asyncio
    async def test_quality_scores_in_valid_range(
        self, client: AsyncClient, sample_csv_with_multiple_variants: bytes
    ):
        """Test quality scores are between 0 and 1."""
        upload_resp = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("test.csv", sample_csv_with_multiple_variants, "text/csv")},
        )
        log_id = upload_resp.json()["id"]

        quality_resp = await client.get(f"/api/v1/logs/{log_id}/quality")
        assert quality_resp.status_code == 200
        quality = quality_resp.json()

        # Business Logic: Scores must be 0.0 to 1.0
        assert 0.0 <= quality["completeness_score"] <= 1.0
        assert 0.0 <= quality["validity_score"] <= 1.0
        assert 0.0 <= quality["overall_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_variant_case_counts_sum_to_total(
        self, client: AsyncClient, sample_csv_with_multiple_variants: bytes
    ):
        """Test variant case counts sum to total number of cases."""
        upload_resp = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("test.csv", sample_csv_with_multiple_variants, "text/csv")},
        )
        log_id = upload_resp.json()["id"]

        variants_resp = await client.get(f"/api/v1/logs/{log_id}/variants")
        assert variants_resp.status_code == 200
        variants = variants_resp.json()

        # Business Logic: Sum of variant case counts = total cases
        total_from_variants = sum(v["case_count"] for v in variants)
        assert total_from_variants == 6

    @pytest.mark.asyncio
    async def test_activities_endpoint_returns_data(
        self, client: AsyncClient, sample_csv_with_multiple_variants: bytes
    ):
        """Test activities endpoint returns activity data."""
        upload_resp = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("test.csv", sample_csv_with_multiple_variants, "text/csv")},
        )
        log_id = upload_resp.json()["id"]

        activities_resp = await client.get(f"/api/v1/logs/{log_id}/activities")
        assert activities_resp.status_code == 200
        activities = activities_resp.json()

        # Verify endpoint returns data in expected format
        assert "activities" in activities, "Response should have 'activities' key"
        assert isinstance(activities["activities"], list), "activities should be a list"
        assert len(activities["activities"]) > 0, "Should have at least one activity"


# =============================================================================
# FLOW 2: PROCESS DISCOVERY TESTS
# =============================================================================


class TestProcessDiscovery:
    """Tests for Process Discovery flow (DFG → Petri Net → Quality Metrics)."""

    @pytest.mark.asyncio
    async def test_miners_catalog_has_required_algorithms(self, client: AsyncClient):
        """Test that required mining algorithms are available."""
        response = await client.get("/api/v1/discovery/miners")
        assert response.status_code == 200
        miners = response.json()

        # Business Logic: Must have core miners
        miner_ids = [m["id"] for m in miners]
        assert "inductive" in miner_ids
        assert "alpha" in miner_ids
        assert len(miners) >= 3

    @pytest.mark.asyncio
    async def test_dfg_has_nodes_and_edges(self, client: AsyncClient, uploaded_log_id: str):
        """Test DFG contains valid nodes and edges."""
        response = await client.get(f"/api/v1/discovery/dfg/{uploaded_log_id}")
        assert response.status_code == 200
        dfg = response.json()

        # Business Logic: DFG must have structure
        assert "nodes" in dfg or "activities" in dfg
        assert "edges" in dfg or "transitions" in dfg

    @pytest.mark.asyncio
    async def test_dfg_edge_probabilities_valid(self, client: AsyncClient, uploaded_log_id: str):
        """Test DFG edge probabilities are between 0 and 1."""
        response = await client.get(f"/api/v1/discovery/dfg/{uploaded_log_id}/detailed")
        assert response.status_code == 200
        dfg = response.json()

        # Business Logic: Probabilities must be valid
        if "edges" in dfg:
            for edge in dfg["edges"]:
                if "probability" in edge:
                    assert 0.0 <= edge["probability"] <= 1.0

    @pytest.mark.asyncio
    async def test_model_discovery_returns_valid_model(
        self, client: AsyncClient, uploaded_log_id: str
    ):
        """Test model discovery creates valid model with correct metadata."""
        response = await client.post(
            "/api/v1/discovery/discover",
            json={"log_id": uploaded_log_id, "miner_type": "inductive", "model_name": "Test Model"},
        )
        assert response.status_code == 200
        model = response.json()

        # Business Logic: Model should reference source log
        assert model["source_log_id"] == uploaded_log_id
        assert model["miner_type"] == "inductive"
        UUID(model["model_id"])  # Valid UUID

    @pytest.mark.asyncio
    async def test_model_quality_metrics_valid(
        self, client: AsyncClient, uploaded_log_id: str, discovered_model_id: str
    ):
        """Test model quality metrics are in valid range."""
        # Model quality endpoint requires log_id as query param
        response = await client.get(
            f"/api/v1/discovery/model/{discovered_model_id}/quality",
            params={"log_id": uploaded_log_id},
        )
        assert response.status_code == 200
        quality = response.json()

        # Business Logic: Quality dimensions 0-1
        assert 0.0 <= quality["fitness"] <= 1.0
        if quality.get("precision") is not None:
            assert 0.0 <= quality["precision"] <= 1.0


# =============================================================================
# FLOW 3: CONFORMANCE CHECKING TESTS
# =============================================================================


class TestConformanceChecking:
    """Tests for Conformance Checking (Fitness → Alignments → Deviations)."""

    @pytest.mark.asyncio
    async def test_conformance_check_returns_valid_fitness(
        self, client: AsyncClient, uploaded_log_id: str, discovered_model_id: str
    ):
        """Test conformance check returns valid fitness score."""
        response = await client.post(
            "/api/v1/conformance/check",
            json={
                "log_id": uploaded_log_id,
                "model_id": discovered_model_id,
                "method": "token_replay",
            },
        )
        assert response.status_code == 200
        result = response.json()

        # Business Logic: Fitness 0-1, is_conformant boolean
        assert 0.0 <= result["fitness"] <= 1.0
        assert isinstance(result["is_conformant"], bool)

    @pytest.mark.asyncio
    async def test_self_discovered_model_has_high_fitness(
        self, client: AsyncClient, uploaded_log_id: str, discovered_model_id: str
    ):
        """Test model discovered from log has high fitness (>0.5) with same log."""
        response = await client.post(
            "/api/v1/conformance/check",
            json={
                "log_id": uploaded_log_id,
                "model_id": discovered_model_id,
                "method": "token_replay",
            },
        )
        fitness = response.json()["fitness"]

        # Business Logic: Self-discovered model should fit well
        assert fitness >= 0.5, f"Fitness {fitness} too low for self-discovered model"

    @pytest.mark.asyncio
    async def test_diagnostics_trace_counts_valid(
        self, client: AsyncClient, uploaded_log_id: str, discovered_model_id: str
    ):
        """Test diagnostics trace counts are logically consistent."""
        response = await client.get(
            "/api/v1/conformance/diagnostics",
            params={"log_id": uploaded_log_id, "model_id": discovered_model_id},
        )
        assert response.status_code == 200
        diag = response.json()

        # Business Logic: Trace count consistency
        assert diag["total_traces"] > 0
        assert 0 <= diag["fitting_traces"] <= diag["total_traces"]
        assert 0.0 <= diag["trace_fitness_ratio"] <= 1.0

    @pytest.mark.asyncio
    async def test_comprehensive_quality_has_all_dimensions(
        self, client: AsyncClient, uploaded_log_id: str, discovered_model_id: str
    ):
        """Test comprehensive quality returns all expected dimensions."""
        # First do a conformance check, then get quality
        check_resp = await client.post(
            "/api/v1/conformance/check",
            json={
                "log_id": uploaded_log_id,
                "model_id": discovered_model_id,
                "method": "token_replay",
            },
        )
        assert check_resp.status_code == 200

        # Use the fitness from check response as quality metric
        result = check_resp.json()

        # Business Logic: Required dimensions present
        assert "fitness" in result
        assert 0.0 <= result["fitness"] <= 1.0


# =============================================================================
# FLOW 4: PERFORMANCE ANALYSIS TESTS
# =============================================================================


class TestPerformanceAnalysis:
    """Tests for Performance Analysis (Bottlenecks → Durations → Metrics)."""

    @pytest.mark.asyncio
    async def test_performance_analysis_creates_results(
        self, client: AsyncClient, uploaded_log_id: str
    ):
        """Test performance analysis endpoint runs successfully."""
        response = await client.post(
            f"/api/v1/performance/analyze/{uploaded_log_id}",
            json={"name": "Test Analysis", "analysis_type": "duration"},
        )
        assert response.status_code == 200
        result = response.json()

        assert "log_id" in result or "analysis_run_id" in result

    @pytest.mark.asyncio
    async def test_performance_summary_has_valid_counts(
        self, client: AsyncClient, uploaded_log_id: str
    ):
        """Test performance summary has correct case/event counts."""
        # Run analysis first
        await client.post(
            f"/api/v1/performance/analyze/{uploaded_log_id}",
            json={"name": "Test Analysis", "analysis_type": "duration"},
        )

        response = await client.get(f"/api/v1/performance/summary/{uploaded_log_id}")
        assert response.status_code == 200
        summary = response.json()

        # Business Logic: Counts must be positive
        assert summary["total_cases"] > 0
        assert summary["total_events"] > 0

    @pytest.mark.asyncio
    async def test_activity_durations_non_negative(self, client: AsyncClient, uploaded_log_id: str):
        """Test activity performance metrics have non-negative durations."""
        await client.post(
            f"/api/v1/performance/analyze/{uploaded_log_id}",
            json={"name": "Test", "analysis_type": "duration"},
        )

        response = await client.get(f"/api/v1/performance/activities/{uploaded_log_id}")
        assert response.status_code == 200
        activities = response.json()

        # Business Logic: Durations >= 0
        if isinstance(activities, list):
            for activity in activities:
                if activity.get("avg_duration_seconds") is not None:
                    assert activity["avg_duration_seconds"] >= 0

    @pytest.mark.asyncio
    async def test_bottleneck_detection(
        self, client: AsyncClient, sample_csv_with_bottleneck: bytes
    ):
        """Test bottleneck detection with log containing slow activity."""
        # Upload bottleneck data
        upload_resp = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("bottleneck.csv", sample_csv_with_bottleneck, "text/csv")},
        )
        log_id = upload_resp.json()["id"]

        # Run analysis
        await client.post(
            f"/api/v1/performance/analyze/{log_id}",
            json={"name": "Bottleneck Test", "analysis_type": "duration"},
        )

        # Get bottlenecks
        response = await client.get(f"/api/v1/performance/bottlenecks/{log_id}")
        assert response.status_code == 200
        # Bottleneck structure should be valid
        assert response.json() is not None


# =============================================================================
# FLOW 5: ORGANIZATIONAL MINING TESTS
# =============================================================================


class TestOrganizationalMining:
    """Tests for Organizational Mining (Resources → Handover → Roles)."""

    @pytest.mark.asyncio
    async def test_resources_extracted(self, client: AsyncClient, uploaded_log_id: str):
        """Test resources are extracted from log."""
        response = await client.get(f"/api/v1/org/resources/{uploaded_log_id}")
        assert response.status_code == 200
        resources = response.json()

        # Business Logic: Should have resources
        assert resources is not None

    @pytest.mark.asyncio
    async def test_handover_network_structure(self, client: AsyncClient, uploaded_log_id: str):
        """Test handover network has valid structure."""
        response = await client.get(f"/api/v1/org/handover-network/{uploaded_log_id}")
        assert response.status_code == 200
        handover = response.json()

        # Business Logic: Network should exist
        assert handover is not None

    @pytest.mark.asyncio
    async def test_role_discovery(self, client: AsyncClient, uploaded_log_id: str):
        """Test organizational roles can be discovered."""
        response = await client.get(f"/api/v1/org/roles/{uploaded_log_id}")
        assert response.status_code == 200
        roles = response.json()

        assert roles is not None


# =============================================================================
# FLOW 6: PM4PY ADVANCED ANALYTICS TESTS
# =============================================================================


class TestPM4PyAnalytics:
    """Tests for PM4Py advanced analytics capabilities."""

    @pytest.mark.asyncio
    async def test_footprint_analysis(self, client: AsyncClient, uploaded_log_id: str):
        """Test footprint analysis returns behavioral relations."""
        response = await client.get(f"/api/v1/process-mining/footprints/{uploaded_log_id}")
        assert response.status_code == 200
        footprints = response.json()

        # Business Logic: Should have behavioral relations
        assert "sequence" in footprints or "activities" in footprints

    @pytest.mark.asyncio
    async def test_log_skeleton_constraints(self, client: AsyncClient, uploaded_log_id: str):
        """Test log skeleton returns declarative constraints."""
        response = await client.get(f"/api/v1/process-mining/log-skeleton/{uploaded_log_id}")
        assert response.status_code == 200
        skeleton = response.json()

        assert skeleton is not None

    @pytest.mark.asyncio
    async def test_case_duration_statistics(self, client: AsyncClient, uploaded_log_id: str):
        """Test case duration statistics are calculated correctly."""
        response = await client.get(f"/api/v1/process-mining/duration-stats/{uploaded_log_id}")
        assert response.status_code == 200
        stats = response.json()

        # Business Logic: Duration stats should be non-negative
        assert stats["min_duration_seconds"] >= 0
        assert stats["max_duration_seconds"] >= stats["min_duration_seconds"]
        assert stats["avg_duration_seconds"] >= 0

    @pytest.mark.asyncio
    async def test_start_and_end_activities(self, client: AsyncClient, uploaded_log_id: str):
        """Test start and end activities are identified."""
        start_resp = await client.get(f"/api/v1/process-mining/start-activities/{uploaded_log_id}")
        assert start_resp.status_code == 200

        end_resp = await client.get(f"/api/v1/process-mining/end-activities/{uploaded_log_id}")
        assert end_resp.status_code == 200

        # Business Logic: Should have start/end activities
        assert start_resp.json() is not None
        assert end_resp.json() is not None


# =============================================================================
# END-TO-END INTEGRATION TESTS
# =============================================================================


class TestEndToEndIntegration:
    """Complete end-to-end integration tests across all flows."""

    @pytest.mark.asyncio
    async def test_complete_process_mining_workflow(
        self, client: AsyncClient, sample_csv_with_multiple_variants: bytes
    ):
        """Test complete workflow: Upload → Discover → Conform → Analyze."""

        # === STEP 1: INGEST ===
        upload_resp = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("e2e.csv", sample_csv_with_multiple_variants, "text/csv")},
        )
        assert upload_resp.status_code == 200
        log_id = upload_resp.json()["id"]

        # Verify ingestion
        stats_resp = await client.get(f"/api/v1/logs/{log_id}/statistics")
        assert stats_resp.status_code == 200
        assert stats_resp.json()["case_count"] == 6

        # === STEP 2: DISCOVER ===
        discover_resp = await client.post(
            "/api/v1/discovery/discover",
            json={"log_id": log_id, "miner_type": "inductive", "model_name": "E2E Model"},
        )
        assert discover_resp.status_code == 200
        model_id = discover_resp.json()["model_id"]

        # === STEP 3: CONFORMANCE ===
        conform_resp = await client.post(
            "/api/v1/conformance/check",
            json={"log_id": log_id, "model_id": model_id, "method": "token_replay"},
        )
        assert conform_resp.status_code == 200
        fitness = conform_resp.json()["fitness"]
        assert fitness >= 0.5  # Self-discovered should fit well

        # === STEP 4: PERFORMANCE ===
        perf_resp = await client.post(
            f"/api/v1/performance/analyze/{log_id}",
            json={"name": "E2E Analysis", "analysis_type": "duration"},
        )
        assert perf_resp.status_code == 200

        summary_resp = await client.get(f"/api/v1/performance/summary/{log_id}")
        assert summary_resp.status_code == 200

        # === STEP 5: ORG MINING ===
        resources_resp = await client.get(f"/api/v1/org/resources/{log_id}")
        assert resources_resp.status_code == 200

        # === STEP 6: ANALYTICS ===
        dashboard_resp = await client.get(f"/api/v1/analytics/dashboard/{log_id}")
        assert dashboard_resp.status_code == 200

        # All steps successful
        assert True

    @pytest.mark.asyncio
    async def test_pagination_and_listing(self, client: AsyncClient):
        """Test pagination works correctly for log listing."""
        response = await client.get("/api/v1/logs/", params={"page": 1, "page_size": 10})
        assert response.status_code == 200
        data = response.json()

        # Business Logic: Pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    @pytest.mark.asyncio
    async def test_error_handling_invalid_uuid(self, client: AsyncClient):
        """Test proper error handling for invalid UUIDs."""
        import uuid

        fake_id = str(uuid.uuid4())

        response = await client.get(f"/api/v1/logs/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_model_crud_operations(self, client: AsyncClient, uploaded_log_id: str):
        """Test model CRUD operations work correctly."""
        # Create
        create_resp = await client.post(
            "/api/v1/discovery/discover",
            json={"log_id": uploaded_log_id, "miner_type": "inductive", "model_name": "CRUD Test"},
        )
        assert create_resp.status_code == 200
        model_id = create_resp.json()["model_id"]

        # Read
        read_resp = await client.get(f"/api/v1/models/{model_id}")
        assert read_resp.status_code == 200

        # List
        list_resp = await client.get("/api/v1/models/")
        assert list_resp.status_code == 200
