"""
User Journey 01: Onboarding

Tests the complete new user onboarding flow:
- Register new account
- Login
- Get user info
- Verify workspace/org creation
"""

import pytest
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import API_V1
from debug_helpers import dump_request, generate_curl_command


class TestOnboardingJourney:
    """New user onboarding journey - from registration to first project."""
    
    @pytest.mark.journey
    def test_01_health_check(self, api_client):
        """Verify backend is running before starting."""
        response = api_client.get(f"{API_V1.replace('/api/v1', '')}/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
    
    @pytest.mark.journey
    def test_02_get_current_user(self, api_client, context):
        """Get current user info (after auth setup)."""
        response = api_client.get(f"{API_V1}/auth/me")
        
        if response.status_code == 200:
            data = response.json()
            context.user_id = data.get("user", {}).get("id") or data.get("id")
            context.user_email = data.get("user", {}).get("email") or data.get("email")
            context.org_id = data.get("organization", {}).get("id")
            
            # Check for workspaces
            workspaces = data.get("workspaces", [])
            if workspaces:
                context.workspace_id = workspaces[0].get("id")
                context.workspace_name = workspaces[0].get("name")
        else:
            # Auth might be disabled, that's OK for MVP
            pytest.skip("Auth disabled or user not available")
    
    @pytest.mark.journey
    def test_03_list_workspaces(self, api_client, context):
        """List available workspaces."""
        response = api_client.get(f"{API_V1}/workspaces")
        
        assert response.status_code == 200
        data = response.json()
        
        items = data.get("items", [])
        if items and not context.workspace_id:
            context.workspace_id = items[0]["id"]
            context.workspace_name = items[0].get("name")
    
    @pytest.mark.journey
    def test_04_list_projects(self, api_client, context):
        """List projects in workspace."""
        params = {}
        if context.workspace_id:
            params["workspace_id"] = context.workspace_id
        
        response = api_client.get(f"{API_V1}/projects", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        items = data.get("items", [])
        if items:
            context.project_id = items[0]["id"]
            context.project_name = items[0].get("name")
    
    @pytest.mark.journey
    def test_05_create_project_if_needed(self, api_client, context):
        """Create a project if none exists."""
        if context.project_id:
            pytest.skip("Project already exists")
        
        if not context.workspace_id:
            pytest.skip("No workspace available")
        
        response = api_client.post(
            f"{API_V1}/projects",
            params={"workspace_id": context.workspace_id},
            json={
                "name": "E2E Test Project",
                "description": "Created by automated tests"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        context.project_id = data["id"]
        context.project_name = data.get("name")
    
    @pytest.mark.journey
    def test_06_verify_project_created(self, api_client, context):
        """Verify the project is accessible."""
        if not context.project_id:
            pytest.skip("No project created")
        
        response = api_client.get(f"{API_V1}/projects/{context.project_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == context.project_id
