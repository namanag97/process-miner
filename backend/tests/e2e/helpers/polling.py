"""
Smart polling helpers for async workflows.

Provides wait_for_state() to poll API endpoints until target state is reached.
"""

import asyncio
from typing import List, Optional, Callable, Any, Dict
from httpx import AsyncClient


async def wait_for_state(
    client: AsyncClient,
    endpoint: str,
    target_states: List[str],
    timeout_seconds: int = 60,
    poll_interval: float = 1.0,
    state_extractor: Optional[Callable[[Dict], str]] = None,
    on_state_change: Optional[Callable[[Optional[str], str], None]] = None,
) -> str:
    """
    Poll an endpoint until target state is reached.
    
    Args:
        client: HTTP client
        endpoint: API endpoint to poll (e.g., /api/v1/datasets/{id})
        target_states: List of acceptable target states (e.g., ["ready", "READY"])
        timeout_seconds: Max time to wait
        poll_interval: Seconds between polls
        state_extractor: Function to extract state from response (default: response["status"])
        on_state_change: Callback when state changes (receives prev_state, current_state)
    
    Returns:
        Final state reached
    
    Raises:
        TimeoutError: If target state not reached in time
        AssertionError: If state transitions to ERROR/FAILED
    """
    if state_extractor is None:
        state_extractor = lambda r: r.get("status", "UNKNOWN")
    
    prev_state: Optional[str] = None
    start_time = asyncio.get_event_loop().time()
    max_attempts = int(timeout_seconds / poll_interval)
    
    for attempt in range(max_attempts):
        await asyncio.sleep(poll_interval)
        
        response = await client.get(endpoint)
        assert response.status_code == 200, (
            f"Failed to poll {endpoint}: HTTP {response.status_code}\n{response.text}"
        )
        
        data = response.json()
        current_state = state_extractor(data)
        
        # State changed - notify callback
        if current_state != prev_state and on_state_change:
            on_state_change(prev_state, current_state)
        
        # Check for failure states
        if current_state.upper() in ["FAILED", "ERROR"]:
            error_msg = data.get("error_message", "Unknown error")
            raise AssertionError(
                f"State transitioned to {current_state}: {error_msg}\n"
                f"Full response: {data}"
            )
        
        # Check for target state (case-insensitive)
        if current_state.lower() in [s.lower() for s in target_states]:
            elapsed = asyncio.get_event_loop().time() - start_time
            print(f"✓ Reached state '{current_state}' in {elapsed:.2f}s after {attempt + 1} polls")
            return current_state
        
        prev_state = current_state
    
    elapsed = asyncio.get_event_loop().time() - start_time
    raise TimeoutError(
        f"Timeout waiting for states {target_states} after {elapsed:.2f}s. "
        f"Last state: {prev_state}"
    )


async def wait_for_job_completion(
    client: AsyncClient,
    job_id: str,
    timeout_seconds: int = 120,
    poll_interval: float = 2.0,
) -> Dict[str, Any]:
    """
    Poll a job until it completes.
    
    Args:
        client: HTTP client
        job_id: Job ID to poll
        timeout_seconds: Max time to wait
        poll_interval: Seconds between polls
    
    Returns:
        Final job response
    
    Raises:
        TimeoutError: If job doesn't complete in time
        AssertionError: If job fails
    """
    endpoint = f"/api/v1/jobs/{job_id}"
    
    def extract_status(response: Dict) -> str:
        return response.get("status", "UNKNOWN")
    
    def on_change(prev: Optional[str], current: str):
        progress = response.get("progress", 0)
        print(f"  Job {job_id}: {prev} → {current} (progress: {progress}%)")
    
    # Poll for completion
    start_time = asyncio.get_event_loop().time()
    max_attempts = int(timeout_seconds / poll_interval)
    
    for attempt in range(max_attempts):
        await asyncio.sleep(poll_interval)
        
        response_obj = await client.get(endpoint)
        assert response_obj.status_code == 200
        
        response = response_obj.json()
        status = extract_status(response)
        
        if status.upper() == "COMPLETED":
            elapsed = asyncio.get_event_loop().time() - start_time
            print(f"✓ Job {job_id} completed in {elapsed:.2f}s")
            return response
        
        if status.upper() in ["FAILED", "CANCELLED"]:
            error = response.get("error", "Unknown error")
            raise AssertionError(f"Job {job_id} failed: {error}")
    
    raise TimeoutError(f"Job {job_id} did not complete in {timeout_seconds}s")
