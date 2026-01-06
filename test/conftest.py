
import pytest
import requests
from test_config import BASE_URL

@pytest.fixture(scope="session")
def api_client():
    """
    Returns a requests session configured with the base URL.
    """
    session = requests.Session()
    # verify=False is useful for local dev with self-signed certs (if any)
    # but for localhost http it's fine.
    session.verify = False 
    return session

def pytest_configure(config):
    """
    Configure pytest.
    """
    # Register markers if needed
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
