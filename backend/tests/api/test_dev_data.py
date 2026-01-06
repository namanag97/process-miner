"""Tests for Dev Data API endpoints.

CRITICAL: These endpoints were returning 500 errors in the API audit.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_tables(auth_client: AsyncClient):
    """Test listing database tables.
    
    CRITICAL: This was returning 500 before the fix.
    """
    response = await auth_client.get("/api/v1/dev/data/tables")
    # Should return 200 with table list, not 500
    assert response.status_code == 200
    data = response.json()
    
    # Should return a list of tables
    assert "tables" in data or isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.integration  
async def test_get_records_invalid_table(auth_client: AsyncClient):
    """Test getting records from non-existent table.
    
    Should return 400/404, not 500.
    """
    response = await auth_client.get("/api/v1/dev/data/records/nonexistent_table")
    # Should be 400 Bad Request or 404 Not Found
    assert response.status_code in (400, 404, 422)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_records_valid_table(auth_client: AsyncClient):
    """Test getting records from a valid table."""
    # First get available tables
    tables_response = await auth_client.get("/api/v1/dev/data/tables")
    
    if tables_response.status_code != 200:
        pytest.skip("Tables endpoint not available")
    
    tables_data = tables_response.json()
    tables = tables_data.get("tables", tables_data if isinstance(tables_data, list) else [])
    
    if not tables:
        pytest.skip("No tables available")
    
    # Try to get records from first table
    table_name = tables[0] if isinstance(tables[0], str) else tables[0].get("name", tables[0])
    response = await auth_client.get(f"/api/v1/dev/data/records/{table_name}")
    
    # Should return 200 with records or empty list
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_record_not_found(auth_client: AsyncClient):
    """Test getting a specific record that doesn't exist.
    
    Should return 400/404, not 500.
    """
    response = await auth_client.get("/api/v1/dev/data/record/users/nonexistent-id")
    assert response.status_code in (400, 404, 422)
