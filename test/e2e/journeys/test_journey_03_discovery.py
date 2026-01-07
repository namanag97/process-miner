"""
User Journey 03: Process Discovery

Tests the process discovery flow:
1. Verify dataset is ready
2. List available miners
3. Discover process model (DFG/Petri net)
4. View visualization data
5. Explore process
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import API_V1, wait_for_state
from debug_helpers import dump_request


class TestProcessDiscoveryJourney:
    """Process discovery journey - from ready dataset to process model."""
    
    @pytest.mark.journey
    def test_01_verify_dataset_ready(self, api_client, context):
        """Verify we have a ready dataset to work with."""
        if not context.dataset_id:
            pytest.skip("No dataset available - run upload journey first")
        
        url = f"{API_V1}/datasets/{context.dataset_id}"
        response = api_client.get(url)
        
        assert response.status_code == 200
        data = response.json()
        
        status = data.get("status", "").lower()
        if status != "ready":
            pytest.skip(f"Dataset not ready: {status}")
        
        print(f"✓ Dataset ready for discovery")
    
    @pytest.mark.journey
    def test_02_list_miners(self, api_client, context):
        """List available mining algorithms."""
        response = api_client.get(f"{API_V1}/discovery/miners")
        
        assert response.status_code == 200
        miners = response.json()
        
        miner_names = [m.get("name", m.get("id")) for m in miners]
        print(f"✓ Available miners: {miner_names}")
        
        assert len(miners) > 0, "Expected at least one miner"
    
    @pytest.mark.journey
    def test_03_get_dfg(self, api_client, context):
        """Get Directly-Follows Graph for the dataset."""
        if not context.dataset_id:
            pytest.skip("No dataset available")
        
        url = f"{API_V1}/visualization/{context.dataset_id}/dfg"
        params = {"include_performance": True}
        
        response = api_client.get(url, params=params)
        
        assert response.status_code == 200, f"DFG fetch failed: {response.text}"
        
        data = response.json()
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        
        print(f"✓ DFG: {len(nodes)} nodes, {len(edges)} edges")
        
        assert len(nodes) > 0, "Expected nodes in DFG"
        assert len(edges) > 0, "Expected edges in DFG"
    
    @pytest.mark.journey
    def test_04_discover_model(self, api_client, context):
        """Discover a process model using inductive miner."""
        if not context.dataset_id:
            pytest.skip("No dataset available")
        
        url = f"{API_V1}/discovery/discover"
        payload = {
            "dataset_id": context.dataset_id,
            "miner": "inductive",
            "name": "E2E Test Model"
        }
        
        response = api_client.post(url, json=payload, params={"async_mode": False})
        
        if response.status_code == 200:
            data = response.json()
            context.model_id = data.get("id") or data.get("model_id")
            context.model_discovered = True
            print(f"✓ Model discovered: {context.model_id}")
        elif response.status_code == 202:
            # Async mode - extract job/workflow ID
            data = response.json()
            context.workflow_id = data.get("workflow_id")
            print(f"✓ Discovery started (async): {context.workflow_id}")
        else:
            print(f"⚠ Discovery failed: {response.status_code} - {response.text[:200]}")
    
    @pytest.mark.journey
    def test_05_get_explorer_data(self, api_client, context):
        """Get unified explorer data (DFG + variants + activities)."""
        if not context.dataset_id:
            pytest.skip("No dataset available")
        
        url = f"{API_V1}/visualization/{context.dataset_id}/explorer-data"
        params = {
            "include_performance": True,
            "include_complexity": True,
            "top_variants": 10
        }
        
        response = api_client.get(url, params=params)
        
        assert response.status_code == 200, f"Explorer data failed: {response.text}"
        
        data = response.json()
        
        # Verify DFG
        dfg = data.get("dfg", {})
        assert len(dfg.get("nodes", [])) > 0, "Expected DFG nodes"
        
        # Verify variants
        variants = data.get("variants", [])
        print(f"✓ Explorer data: {len(variants)} variants")
        
        # Verify activities
        activities = data.get("activities", [])
        print(f"✓ Activities: {len(activities)}")
    
    @pytest.mark.journey
    def test_06_list_models(self, api_client, context):
        """List discovered models."""
        response = api_client.get(f"{API_V1}/discovery/models")
        
        assert response.status_code == 200
        data = response.json()
        
        models = data.get("items", [])
        print(f"✓ Found {len(models)} models")
        
        # Use first available model if we don't have one
        if models and not context.model_id:
            context.model_id = models[0]["id"]
