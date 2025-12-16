"""
Analysis endpoint tests.

These tests require a processed dataset, which is complex to set up in unit tests.
For now, we test the error cases and basic validation.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_dfg_not_found(client: AsyncClient):
    """Test getting DFG for non-existent dataset."""
    response = await client.get("/api/datasets/nonexistent-id/dfg")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_variants_not_found(client: AsyncClient):
    """Test getting variants for non-existent dataset."""
    response = await client.get("/api/datasets/nonexistent-id/variants")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_summary_not_found(client: AsyncClient):
    """Test getting summary for non-existent dataset."""
    response = await client.get("/api/datasets/nonexistent-id/summary")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_activities_not_found(client: AsyncClient):
    """Test getting activities for non-existent dataset."""
    response = await client.get("/api/datasets/nonexistent-id/activities")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_deviations_not_found(client: AsyncClient):
    """Test getting deviations for non-existent dataset."""
    response = await client.get("/api/datasets/nonexistent-id/deviations")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_full_analysis_not_found(client: AsyncClient):
    """Test getting full analysis for non-existent dataset."""
    response = await client.get("/api/datasets/nonexistent-id/full")
    assert response.status_code == 404
