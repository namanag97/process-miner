
import os

# Base URL for the API
BASE_URL = os.getenv("API_URL", "http://localhost:8001")
API_V1 = f"{BASE_URL}/api/v1"

# Test user credentials
TEST_USER = {
    "email": "test@processmining.io",
    "password": "TestPassword123!",
    "name": "Test User"
}

# Admin user credentials (if needed)
ADMIN_USER = {
    "email": "admin@processmining.io",
    "password": "AdminPassword123!",
    "name": "Admin User"
}

# Shared state class to pass data between tests
class TestContext:
    # Auth
    access_token: str = None
    refresh_token: str = None
    user_id: str = None
    
    # Hierarchy
    org_id: str = None
    workspace_id: str = None
    project_id: str = None
    
    # Resources
    dataset_id: str = None
    dataset_uploaded: bool = False
    dataset_mapped: bool = False
    dataset_ingested: bool = False
    
    # Mining
    model_id: str = None
    job_id: str = None
    
    # Analytics
    analysis_id: str = None

    @classmethod
    def reset(cls):
        """Reset context state - useful if tests are not dependent"""
        # We might not want to reset everything if we are running a sequence
        pass

# Global instance
context = TestContext()
