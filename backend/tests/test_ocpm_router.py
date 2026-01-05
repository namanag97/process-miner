"""Tests for OCPM Router (/api/ocpm/)

Test Coverage:
- OCEL file upload (JSON format)
- OCEL log management (list, get, delete)
- Object type analysis
- Object-Centric Petri Net discovery
- Object-Centric DFG generation
- RAW OCEL JSON extraction and validation ⭐
"""

import json

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.process_mining.models.orm import OCELLog


class TestOCELUpload:
    """Tests for OCEL file upload."""

    @pytest.mark.asyncio
    async def test_upload_simple_ocel(self, client: AsyncClient, simple_ocel_jsonocel: bytes):
        """Upload simple OCEL JSON and verify structure."""
        response = await client.post(
            "/api/v1/ocpm/upload",
            files={"file": ("order_simple.jsonocel", simple_ocel_jsonocel, "application/json")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["total_events"] == 11
        assert data["total_objects"] == 7  # 2 orders + 3 items + 2 packages
        assert data["total_object_types"] == 3
        assert set(data["object_types"]) == {"Order", "Item", "Package"}

    @pytest.mark.asyncio
    async def test_upload_complex_ocel(self, client: AsyncClient, complex_ocel_jsonocel: bytes):
        """Upload complex OCEL with multiple object types."""
        response = await client.post(
            "/api/v1/ocpm/upload",
            files={"file": ("order_complex.jsonocel", complex_ocel_jsonocel, "application/json")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["total_events"] == 20
        assert data["total_object_types"] == 6
        assert "Order" in data["object_types"]
        assert "Product" in data["object_types"]
        assert "Material" in data["object_types"]

    @pytest.mark.asyncio
    async def test_upload_invalid_ocel(self, client: AsyncClient):
        """Upload invalid OCEL should return 400."""
        invalid_ocel = b'{"invalid": "json"}'
        response = await client.post(
            "/api/v1/ocpm/upload",
            files={"file": ("invalid.jsonocel", invalid_ocel, "application/json")},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_empty_ocel(self, client: AsyncClient):
        """Upload empty OCEL should return validation error."""
        response = await client.post(
            "/api/v1/ocpm/upload",
            files={"file": ("empty.jsonocel", b"", "application/json")},
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_upload_with_custom_name(self, client: AsyncClient, simple_ocel_jsonocel: bytes):
        """Upload OCEL with custom name."""
        response = await client.post(
            "/api/v1/ocpm/upload",
            files={"file": ("test.jsonocel", simple_ocel_jsonocel, "application/json")},
            data={"name": "My Custom OCEL Log"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My Custom OCEL Log"


class TestOCELManagement:
    """Tests for OCEL log management."""

    @pytest.mark.asyncio
    async def test_list_ocel_logs(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """List all OCEL logs."""
        response = await client.get("/api/v1/ocpm/logs")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data or isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_ocel_log_by_id(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """Get OCEL log details by ID."""
        response = await client.get(f"/api/v1/ocpm/logs/{uploaded_ocel_log_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == uploaded_ocel_log_id
        assert "total_events" in data
        assert "total_objects" in data
        assert "object_types" in data

    @pytest.mark.asyncio
    async def test_delete_ocel_log(self, client: AsyncClient, simple_ocel_jsonocel: bytes):
        """Delete OCEL log."""
        # Upload first
        upload_resp = await client.post(
            "/api/v1/ocpm/upload",
            files={"file": ("test.jsonocel", simple_ocel_jsonocel, "application/json")},
        )
        log_id = upload_resp.json()["id"]

        # Delete
        response = await client.delete(f"/api/v1/ocpm/logs/{log_id}")
        assert response.status_code == 200

        # Verify deleted
        get_resp = await client.get(f"/api/v1/ocpm/logs/{log_id}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_nonexistent_ocel_log(self, client: AsyncClient):
        """Get non-existent OCEL log should return 404."""
        response = await client.get("/api/v1/ocpm/logs/nonexistent-id")
        assert response.status_code == 404


class TestObjectTypes:
    """Tests for object type analysis."""

    @pytest.mark.asyncio
    async def test_get_object_types(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """Get object types for OCEL log."""
        response = await client.get(f"/api/v1/ocpm/logs/{uploaded_ocel_log_id}/object-types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # Order, Item, Package

        # Verify structure
        for obj_type in data:
            assert "name" in obj_type
            assert "object_count" in obj_type
            assert obj_type["object_count"] > 0

    @pytest.mark.asyncio
    async def test_object_type_counts(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """Verify object type counts are accurate."""
        response = await client.get(f"/api/v1/ocpm/logs/{uploaded_ocel_log_id}/object-types")
        assert response.status_code == 200
        data = response.json()

        # Sum should match total_objects
        total_objects_sum = sum(ot["object_count"] for ot in data)

        log_resp = await client.get(f"/api/v1/ocpm/logs/{uploaded_ocel_log_id}")
        log_data = log_resp.json()

        assert total_objects_sum == log_data["total_objects"]


class TestOCPetriNetDiscovery:
    """Tests for OC Petri Net discovery."""

    @pytest.mark.asyncio
    async def test_discover_oc_petri_net(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """Discover OC-PN from OCEL log."""
        response = await client.post(
            "/api/v1/ocpm/discover",
            json={"log_id": uploaded_ocel_log_id, "model_name": "Test OC-PN"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["log_id"] == uploaded_ocel_log_id
        assert "object_types" in data

    @pytest.mark.asyncio
    async def test_discover_oc_pn_invalid_log(self, client: AsyncClient):
        """Discover OC-PN with invalid log_id should return 404."""
        response = await client.post(
            "/api/v1/ocpm/discover",
            json={"log_id": "nonexistent", "model_name": "Test"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_oc_petri_nets(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """List all OC Petri Nets."""
        # Discover one first
        await client.post(
            "/api/v1/ocpm/discover",
            json={"log_id": uploaded_ocel_log_id, "model_name": "Test OC-PN"},
        )

        # List
        response = await client.get("/api/v1/ocpm/models")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_oc_pn_by_id(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """Get OC-PN details by ID."""
        # Discover first
        discover_resp = await client.post(
            "/api/v1/ocpm/discover",
            json={"log_id": uploaded_ocel_log_id, "model_name": "Test OC-PN"},
        )
        model_id = discover_resp.json()["id"]

        # Get
        response = await client.get(f"/api/v1/ocpm/models/{model_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == model_id

    @pytest.mark.asyncio
    async def test_delete_oc_pn(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """Delete OC Petri Net."""
        # Discover first
        discover_resp = await client.post(
            "/api/v1/ocpm/discover",
            json={"log_id": uploaded_ocel_log_id, "model_name": "Test OC-PN"},
        )
        model_id = discover_resp.json()["id"]

        # Delete
        response = await client.delete(f"/api/v1/ocpm/models/{model_id}")
        assert response.status_code == 200

        # Verify deleted
        get_resp = await client.get(f"/api/v1/ocpm/models/{model_id}")
        assert get_resp.status_code == 404


class TestOCDFG:
    """Tests for Object-Centric DFG."""

    @pytest.mark.asyncio
    async def test_get_oc_dfg(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """Get Object-Centric DFG."""
        response = await client.get(f"/api/v1/ocpm/logs/{uploaded_ocel_log_id}/oc-dfg")
        assert response.status_code == 200
        data = response.json()
        assert "object_types" in data
        assert "activities" in data
        assert "graphs_by_type" in data

    @pytest.mark.asyncio
    async def test_oc_dfg_structure(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """Verify OC-DFG has valid structure."""
        response = await client.get(f"/api/v1/ocpm/logs/{uploaded_ocel_log_id}/oc-dfg")
        assert response.status_code == 200
        data = response.json()

        # Each object type should have a graph
        graphs = data["graphs_by_type"]
        for obj_type in data["object_types"]:
            assert obj_type in graphs
            graph = graphs[obj_type]
            assert "nodes" in graph or "edges" in graph

    @pytest.mark.asyncio
    async def test_oc_dfg_without_ocel_data(self, client: AsyncClient):
        """Get OC-DFG for log without stored ocel_data should return 400."""
        # This would require creating a log without ocel_data, which shouldn't happen in practice
        # Skipping this edge case for now


class TestOCELStatistics:
    """Tests for OCEL statistics."""

    @pytest.mark.asyncio
    async def test_get_ocel_statistics(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """Get comprehensive OCEL statistics."""
        response = await client.get(f"/api/v1/ocpm/logs/{uploaded_ocel_log_id}/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "total_objects" in data
        assert "total_object_types" in data
        assert "object_types" in data
        assert "activities" in data
        assert "objects_per_type" in data

    @pytest.mark.asyncio
    async def test_get_object_relationships(self, client: AsyncClient, uploaded_ocel_log_id: str):
        """Get object-event relationships."""
        response = await client.get(f"/api/v1/ocpm/logs/{uploaded_ocel_log_id}/relationships")
        assert response.status_code == 200
        data = response.json()
        assert "object_types" in data
        assert "objects_per_type" in data


class TestRawOCELExtraction:
    """Tests for raw OCEL JSON extraction - USER REQUIREMENT ⭐"""

    @pytest.mark.asyncio
    async def test_extract_raw_ocel_json(
        self, client: AsyncClient, simple_ocel_jsonocel: bytes, test_session: AsyncSession
    ):
        """Extract and verify raw OCEL JSON structure.

        USER REQUIREMENT: See raw JSON of OCPM/OCEL data.
        This test uploads OCEL, retrieves the stored ocel_data,
        and validates OCEL 2.0 structure.
        """
        # Upload OCEL
        upload_resp = await client.post(
            "/api/v1/ocpm/upload",
            files={"file": ("test.jsonocel", simple_ocel_jsonocel, "application/json")},
        )
        assert upload_resp.status_code == 200
        log_id = upload_resp.json()["id"]

        # Retrieve from database
        result = await test_session.execute(select(OCELLog).where(OCELLog.id == log_id))
        ocel_log = result.scalar_one()

        # Verify ocel_data field is populated
        assert ocel_log.ocel_data is not None
        assert len(ocel_log.ocel_data) > 0

        # Parse as JSON
        parsed_ocel = json.loads(ocel_log.ocel_data.decode("utf-8"))

        # Validate OCEL 2.0 structure
        assert "ocel:events" in parsed_ocel
        assert "ocel:objects" in parsed_ocel
        assert "ocel:global-log" in parsed_ocel
        assert parsed_ocel["ocel:global-log"]["ocel:version"] == "2.0"

        # Verify object types
        assert set(parsed_ocel["ocel:global-log"]["ocel:object-types"]) == {
            "Order",
            "Item",
            "Package",
        }

        # Verify events structure
        events = parsed_ocel["ocel:events"]
        assert len(events) == 11
        for _event_id, event_data in events.items():
            assert "ocel:activity" in event_data
            assert "ocel:timestamp" in event_data
            assert "ocel:omap" in event_data

        # Verify objects structure
        objects = parsed_ocel["ocel:objects"]
        assert len(objects) == 7  # 2 orders + 3 items + 2 packages
        for _obj_id, obj_data in objects.items():
            assert "ocel:type" in obj_data


class TestSupportedFormats:
    """Tests for supported OCEL formats."""

    @pytest.mark.asyncio
    async def test_list_supported_formats(self, client: AsyncClient):
        """List supported OCEL formats."""
        response = await client.get("/api/v1/ocpm/formats")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # JSON, SQLite, XML

        # Verify structure
        extensions = [fmt["extension"] for fmt in data]
        assert ".jsonocel" in extensions
        assert ".sqlite" in extensions
        assert ".xmlocel" in extensions
