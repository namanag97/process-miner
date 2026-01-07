"""
User Journey 04: Process Analytics

Tests the analytics exploration flow:
1. View bottlenecks
2. Analyze rework
3. Get service times
4. Check cycle time
5. View throughput
6. Get performance dashboard
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import API_V1


class TestAnalyticsJourney:
    """Process analytics journey - explore performance and bottlenecks."""
    
    @pytest.mark.journey
    def test_01_verify_dataset(self, api_client, context):
        """Verify dataset is ready for analytics."""
        if not context.dataset_id:
            pytest.skip("No dataset available")
        
        url = f"{API_V1}/datasets/{context.dataset_id}"
        response = api_client.get(url)
        
        if response.status_code != 200:
            pytest.skip("Dataset not accessible")
        
        status = response.json().get("status", "").lower()
        if status != "ready":
            pytest.skip(f"Dataset not ready: {status}")
    
    @pytest.mark.journey
    def test_02_get_bottlenecks(self, api_client, context):
        """Identify process bottlenecks."""
        url = f"{API_V1}/analytics/datasets/{context.dataset_id}/bottlenecks"
        response = api_client.get(url)
        
        assert response.status_code == 200, f"Bottlenecks failed: {response.text}"
        
        data = response.json()
        bottlenecks = data.get("bottlenecks", [])
        print(f"✓ Bottlenecks: {len(bottlenecks)} detected")
    
    @pytest.mark.journey
    def test_03_get_rework(self, api_client, context):
        """Analyze rework patterns."""
        url = f"{API_V1}/analytics/datasets/{context.dataset_id}/rework"
        response = api_client.get(url)
        
        assert response.status_code == 200, f"Rework analysis failed: {response.text}"
        
        data = response.json()
        rework_items = data.get("rework", data.get("items", []))
        print(f"✓ Rework analysis: {len(rework_items)} items")
    
    @pytest.mark.journey
    def test_04_get_service_times(self, api_client, context):
        """Get service time statistics."""
        url = f"{API_V1}/analytics/datasets/{context.dataset_id}/service-times"
        response = api_client.get(url)
        
        assert response.status_code == 200, f"Service times failed: {response.text}"
        
        data = response.json()
        if isinstance(data, list):
            print(f"✓ Service times: {len(data)} activities")
        else:
            print(f"✓ Service times retrieved")
    
    @pytest.mark.journey
    def test_05_get_cycle_time(self, api_client, context):
        """Get overall cycle time statistics."""
        url = f"{API_V1}/analytics/datasets/{context.dataset_id}/cycle-time"
        response = api_client.get(url)
        
        assert response.status_code == 200, f"Cycle time failed: {response.text}"
        
        data = response.json()
        avg = data.get("average_seconds", data.get("avg"))
        print(f"✓ Cycle time: avg={avg}")
    
    @pytest.mark.journey
    def test_06_get_throughput(self, api_client, context):
        """Get throughput metrics."""
        url = f"{API_V1}/analytics/datasets/{context.dataset_id}/throughput"
        response = api_client.get(url)
        
        assert response.status_code == 200, f"Throughput failed: {response.text}"
        
        data = response.json()
        print(f"✓ Throughput metrics retrieved")
    
    @pytest.mark.journey
    def test_07_get_performance_dashboard(self, api_client, context):
        """Get comprehensive performance dashboard."""
        url = f"{API_V1}/analytics/datasets/{context.dataset_id}/performance"
        response = api_client.get(url)
        
        assert response.status_code == 200, f"Performance dashboard failed: {response.text}"
        
        data = response.json()
        print(f"✓ Performance dashboard retrieved")
