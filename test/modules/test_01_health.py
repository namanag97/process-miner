
import pytest
import requests
from test_config import BASE_URL

def test_root(api_client):
    """Test root endpoint returns API info"""
    response = api_client.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data or "message" in data

def test_health_basic(api_client):
    """Test basic health check"""
    response = api_client.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json().get("status") in ["ok", "healthy"]

def test_health_live(api_client):
    """Test liveness probe"""
    response = api_client.get(f"{BASE_URL}/health/live")
    assert response.status_code == 200

def test_health_ready(api_client):
    """Test readiness probe"""
    response = api_client.get(f"{BASE_URL}/health/ready")
    assert response.status_code == 200

def test_health_detailed(api_client):
    """Test detailed health status"""
    response = api_client.get(f"{BASE_URL}/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded", "healthy"]
    assert "components" in data
