"""Full Lifecycle E2E Test - From Registration to Visualization.

This test answers the user's request for testing "from user joining in front end 
to backend to DB to back response". It simulates the exact API calls a frontend 
would make, without using a browser.

Journey:
1. Register new user (API: /auth/register) -> Simulates "User Joining"
2. Create Organization/Workspace (Automatic on register, but verified)
3. Create new Project (API: /projects)
4. Upload Event Log (API: /datasets/upload)
5. Trigger Discovery (API: /visualization/dfg)
6. Verify DB State & Response

Run: pytest backend/tests/test_e2e_full_lifecycle.py -v -s
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
class TestFullLifecycleE2E:

    @pytest.fixture(autouse=True)
    def enable_auth(self):
        """Force auth to be enabled for this test class."""
        from src.core.config import get_settings
        settings = get_settings()
        original_value = settings.auth_enabled
        settings.auth_enabled = True
        yield
        settings.auth_enabled = original_value
    
    @pytest.fixture
    def new_user_data(self):
        """Randomized user data for registration."""
        uid = str(uuid4())[:8]
        return {
            "email": f"test_user_{uid}@example.com",
            "password": "SecurePassword123!",
            "name": f"Test User {uid}",
            "organization_name": f"Test Org {uid}"
        }

    @pytest.fixture
    def user_csv_data(self) -> bytes:
        """Sample CSV data for upload."""
        return b"""case:concept:name,concept:name,time:timestamp,org:resource
case_1,Register,2023-01-01 09:00:00,User
case_1,Verify Email,2023-01-01 09:05:00,System
case_1,Create Workspace,2023-01-01 09:10:00,User
case_1,Upload Data,2023-01-01 09:15:00,User
case_2,Register,2023-01-01 10:00:00,User
case_2,Verify Email,2023-01-01 10:05:00,System
"""

    async def test_full_user_lifecycle(
        self, 
        client: AsyncClient, 
        new_user_data: dict,
        user_csv_data: bytes,
        test_session: "AsyncSession"
    ):
        print("\n" + "=" * 60)
        print("🚀 STARTING FULL LIFECYCLE TEST (User Joining -> Data -> Vis)")
        print("=" * 60)

        # ---------------------------------------------------------------------
        # STEP 1: User Joining (Registration)
        # ---------------------------------------------------------------------
        print(f"\n👤 STEP 1: Registering new user '{new_user_data['email']}'...")
        
        # NOTE: Using proper RegisterRequest model structure
        register_payload = {
            "email": new_user_data["email"],
            "password": new_user_data["password"],
            "name": new_user_data["name"],
            "organization_name": new_user_data["organization_name"]
        }
        
        auth_resp = await client.post("/api/v1/auth/register", json=register_payload)
        
        if auth_resp.status_code != 201:
            print(f"❌ Registration Failed: {auth_resp.text}")
        
        assert auth_resp.status_code == 201
        auth_data = auth_resp.json()
        
        token = auth_data["access_token"]
        user_id = auth_data["user"]["id"]
        
        # Set auth header for subsequent requests
        headers = {"Authorization": f"Bearer {token}"}
        client.headers.update(headers)
        
        print(f"   ✅ Registered. User ID: {user_id}")
        print(f"   🔑 Auth Token obtained")

        # ---------------------------------------------------------------------
        # STEP 2: Verify Initial State (Workspace & Org)
        # ---------------------------------------------------------------------
        print("\n🏢 STEP 2: Verifying Organization & Workspace creation...")
        
        me_resp = await client.get("/api/v1/auth/me")
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        
        org = me_data["organization"]
        workspaces = me_data["workspaces"]
        
        assert org["name"] == new_user_data["organization_name"]
        assert len(workspaces) > 0
        
        workspace_id = workspaces[0]["id"]
        org_id = org["id"]
        
        print(f"   ✅ Organization created: {org['name']} ({org_id})")
        print(f"   ✅ Default Workspace created: {workspaces[0]['name']} ({workspace_id})")

        # ---------------------------------------------------------------------
        # STEP 3: Create Project
        # ---------------------------------------------------------------------
        print("\n📁 STEP 3: Creating new Project...")
        
        project_payload = {
            "name": "E2E Test Project",
            "description": "Created during full lifecycle test"
        }
        
        # Need to include workspace_id in query
        proj_resp = await client.post(
            f"/api/v1/projects?workspace_id={workspace_id}", 
            json=project_payload
        )
        assert proj_resp.status_code == 201
        project = proj_resp.json()
        project_id = project["id"]
        
        print(f"   ✅ Project created: {project['name']} ({project_id})")

        # ---------------------------------------------------------------------
        # STEP 4: Data Ingestion (Upload)
        # ---------------------------------------------------------------------
        print("\n☁️  STEP 4: Uploading Event Log...")
        
        upload_resp = await client.post(
            "/api/v1/datasets/upload",
            files={"file": ("journey.csv", user_csv_data, "text/csv")},
            data={"project_id": project_id}
        )
        assert upload_resp.status_code == 200
        dataset = upload_resp.json()
        dataset_id = dataset["id"]
        
        print(f"   ✅ Dataset uploaded: {dataset_id}")
        print(f"   📊 Stats: {dataset.get('total_cases')} cases, {dataset.get('total_events')} events")

        # Force checkpoint for DuckDB visibility using PASSIVE mode to avoid locks
        from sqlalchemy import text
        await test_session.commit()
        try:
            # Try PASSIVE checkpoint first
            await test_session.execute(text("PRAGMA wal_checkpoint(PASSIVE)"))
        except Exception as e:
            print(f"   ⚠️ Checkpoint warning: {e}")

        # ---------------------------------------------------------------------
        # STEP 5: Request Visualization (Trigger Algorithms)
        # ---------------------------------------------------------------------
        print("\n🕸️  STEP 5: Requesting DFG Visualization...")
        
        # Retry logic for DuckDB consistency (simulating eventual consistency)
        import asyncio
        max_retries = 3
        graph_data = None
        
        for i in range(max_retries):
            vis_resp = await client.get(f"/api/v1/visualization/{dataset_id}/dfg")
            assert vis_resp.status_code == 200
            
            graph_data = vis_resp.json()
            nodes = graph_data.get("nodes", [])
            
            if len(nodes) > 0:
                break
            
            print(f"   ⚠️ Attempt {i+1}: Graph empty, waiting for DB consistency...")
            await asyncio.sleep(1)
            # Try forcing checkpoint again if empty
            await test_session.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        print(f"   ✅ Visualization received")
        print(f"   🔢 Nodes: {len(nodes)}")
        print(f"   🔗 Edges: {len(edges)}")
        
        # ---------------------------------------------------------------------
        # STRICT SCHEMA VALIDATION (Frontend Contract)
        # ---------------------------------------------------------------------
        # Answering User Request: "How do I know if FE is equipped to handle it?"
        # We validate the exact keys the frontend expects.
        
        print("\n   🛡️ Validating JSON Schema for Frontend Compatibility...")
        
        assert isinstance(nodes, list), "Nodes must be a list"
        assert isinstance(edges, list), "Edges must be a list"
        
        # Contract: Nodes must have 'id' and 'name' (used as label)
        for node in nodes:
            assert "id" in node, "CONTRACT VIOLATION: Node missing 'id'"
            assert "name" in node, "CONTRACT VIOLATION: Node missing 'name' (used for label)"
            assert "frequency" in node, "CONTRACT VIOLATION: Node missing 'frequency' (used for sizing)"
            assert isinstance(node["id"], str), "CONTRACT VIOLATION: Node 'id' must be string"
            assert isinstance(node["frequency"], int), "CONTRACT VIOLATION: Node 'frequency' must be int"
            
        # Contract: Edges must have 'source', 'target', 'weight'
        for edge in edges:
            assert "source" in edge, "CONTRACT VIOLATION: Edge missing 'source'"
            assert "target" in edge, "CONTRACT VIOLATION: Edge missing 'target'"
            assert "frequency" in edge, "CONTRACT VIOLATION: Edge missing 'frequency' (used for weight)"
            assert isinstance(edge["source"], str), "CONTRACT VIOLATION: Edge 'source' must be string"
            assert isinstance(edge["target"], str), "CONTRACT VIOLATION: Edge 'target' must be string"
            
        # Verify specific content from our CSV
        node_ids = [n["id"] for n in nodes]
        assert "Register" in node_ids, "Data validation failed: 'Register' node missing"
        assert "Upload Data" in node_ids, "Data validation failed: 'Upload Data' node missing"
        
        print("   ✅ Schema validation passed: Response matches Frontend contract")

        # ---------------------------------------------------------------------
        # STEP 6: Run Conformance Checking (Advanced Alg)
        # ---------------------------------------------------------------------
        print("\n🔬 STEP 6: Running Conformance Checking...")
        
        # First discover a model (Inductive Miner)
        discover_resp = await client.post(
            "/api/v1/discovery/discover?async_mode=false",
            json={
                "dataset_id": dataset_id,
                "miner_type": "inductive",
                "model_name": "Lifecycle Model"
            }
        )
        assert discover_resp.status_code == 200
        model_id = discover_resp.json()["id"]
        
        # Check conformance
        conf_resp = await client.post(
            "/api/v1/conformance/check",
            json={
                "dataset_id": dataset_id,
                "model_id": model_id,
                "method": "token_replay"
            }
        )
        assert conf_resp.status_code == 200
        fitness = conf_resp.json()["fitness"]
        
        print(f"   ✅ Conformance Check Complete. Fitness: {fitness}")

        print("\n" + "=" * 60)
        print("✅ FULL LIFECYCLE TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
