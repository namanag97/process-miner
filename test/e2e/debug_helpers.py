"""
Debug helpers for fast issue diagnosis during E2E tests.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

import requests


# ANSI colors for terminal output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def colored_print(text: str, color: str = Colors.RESET):
    """Print colored text if in terminal."""
    if os.isatty(1):  # stdout is a terminal
        print(f"{color}{text}{Colors.RESET}")
    else:
        print(text)


def dump_request(
    method: str,
    url: str,
    response: requests.Response,
    request_body: Optional[dict] = None,
    show_headers: bool = False
):
    """
    Print a formatted request/response dump for debugging.
    
    Usage:
        response = client.post(url, json=body)
        dump_request("POST", url, response, body)
    """
    status_color = Colors.GREEN if response.status_code < 400 else Colors.RED
    
    print("\n" + "=" * 60)
    colored_print(f"{Colors.BOLD}>>> {method} {url}", Colors.CYAN)
    
    if request_body:
        print(f"Request Body: {json.dumps(request_body, indent=2)[:500]}")
    
    colored_print(f"<<< {response.status_code} ({response.elapsed.total_seconds():.2f}s)", status_color)
    
    if show_headers:
        print(f"Response Headers: {dict(response.headers)}")
    
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)[:1000]}")
    except:
        print(f"Response: {response.text[:500]}")
    
    print("=" * 60 + "\n")


def generate_curl_command(
    method: str,
    url: str,
    headers: dict = None,
    body: dict = None,
    auth_token: Optional[str] = None
) -> str:
    """
    Generate a curl command that can be copy-pasted for debugging.
    
    Returns:
        Complete curl command string
    """
    parts = [f"curl -X {method}"]
    
    # Add headers
    all_headers = {"Content-Type": "application/json"}
    if auth_token:
        all_headers["Authorization"] = f"Bearer {auth_token}"
    if headers:
        all_headers.update(headers)
    
    for key, value in all_headers.items():
        parts.append(f"-H '{key}: {value}'")
    
    # Add body
    if body:
        parts.append(f"-d '{json.dumps(body)}'")
    
    # Add URL
    parts.append(f"'{url}'")
    
    return " \\\n  ".join(parts)


def save_failed_test_state(
    context: Any,
    test_name: str,
    error: Optional[Exception] = None,
    response: Optional[requests.Response] = None
):
    """
    Save full state on test failure for RCA.
    
    Creates a debug file in test/e2e/debug_dumps/ with:
    - Test context state
    - Error information
    - Response details
    """
    debug_dir = Path(__file__).parent / "debug_dumps"
    debug_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = debug_dir / f"{test_name}_{timestamp}.json"
    
    dump = {
        "test_name": test_name,
        "timestamp": datetime.now().isoformat(),
        "context": context.to_dict() if hasattr(context, "to_dict") else str(context),
        "error": str(error) if error else None,
    }
    
    if response:
        dump["response"] = {
            "status_code": response.status_code,
            "url": str(response.url),
            "elapsed_seconds": response.elapsed.total_seconds(),
            "headers": dict(response.headers),
        }
        try:
            dump["response"]["body"] = response.json()
        except:
            dump["response"]["body"] = response.text[:2000]
    
    with open(filename, "w") as f:
        json.dump(dump, f, indent=2 ,default=str)
    
    colored_print(f"Debug dump saved: {filename}", Colors.YELLOW)
    return filename


def print_test_summary(results: list[dict]):
    """
    Print a summary table of test results.
    
    Args:
        results: List of {"name": str, "passed": bool, "duration_ms": float}
    """
    print("\n" + "=" * 70)
    print(f"{'Test Name':<40} {'Status':<10} {'Duration':<10}")
    print("-" * 70)
    
    total_passed = 0
    total_failed = 0
    total_duration = 0
    
    for result in results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        color = Colors.GREEN if result["passed"] else Colors.RED
        duration = f"{result['duration_ms']:.0f}ms"
        
        colored_print(f"{result['name']:<40} {status:<10} {duration:<10}", color)
        
        if result["passed"]:
            total_passed += 1
        else:
            total_failed += 1
        total_duration += result["duration_ms"]
    
    print("-" * 70)
    summary_color = Colors.GREEN if total_failed == 0 else Colors.RED
    colored_print(
        f"Total: {total_passed} passed, {total_failed} failed ({total_duration:.0f}ms)",
        summary_color
    )
    print("=" * 70 + "\n")
