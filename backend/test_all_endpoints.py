#!/usr/bin/env python3
"""
Final Comprehensive Endpoint Test Script v3

Tests all API endpoints with verified correct paths and enum values.
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api/v1"

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

results = {"passed": 0, "failed": 0}


def log_success(msg):
    results["passed"] += 1
    print(f"{GREEN}✓ {msg}{RESET}")


def log_error(msg):
    results["failed"] += 1
    print(f"{RED}✗ {msg}{RESET}")


def log_info(msg):
    print(f"{BLUE}ℹ {msg}{RESET}")


def log_section(msg):
    print(f"\n{YELLOW}{'='*60}\n{msg}\n{'='*60}{RESET}")


def test_endpoint(method: str, path: str, label: str = None, json_data=None, files=None, data=None, base=None):
    """Generic endpoint tester"""
    label = label or f"{method} {path}"
    url = (base or API_URL) + path
    try:
        if method == "GET":
            r = requests.get(url)
        elif method == "POST":
            r = requests.post(url, json=json_data, files=files, data=data)
        elif method == "DELETE":
            r = requests.delete(url)
        else:
            r = requests.get(url)

        if r.status_code in [200, 201]:
            log_success(f"{label} - {r.status_code}")
            return True, r.json() if r.text else None
        else:
            log_error(f"{label} - {r.status_code}")
            return False, None
    except Exception as e:
        log_error(f"{label} - {e}")
        return False, None


def main():
    print(f"\n{BLUE}{'='*60}")
    print(f"  Process Mining API - Full Endpoint Test v3")
    print(f"{'='*60}{RESET}")

    # ========== HEALTH ==========
    log_section("1. Health Endpoints")
    test_endpoint("GET", "/", label="Root /", base=BASE_URL)
    test_endpoint("GET", "/health", label="Health Check", base=BASE_URL)
    test_endpoint("GET", "/health/live", label="Liveness", base=BASE_URL)

    # ========== PROJECTS ==========
    log_section("2. Projects")
    test_endpoint("GET", "/projects", label="List Projects")
    ok, data = test_endpoint(
        "POST", "/projects", "Create Project",
        json_data={"name": "Test Project", "description": "E2E test"}
    )
    project_id = data.get("id") if data else None
    if project_id:
        log_info(f"Created project: {project_id}")

    # ========== PROCESS UPLOAD ==========
    log_section("3. Process Upload")
    csv_path = Path(__file__).parent / "sample_log.csv"
    log_info(f"Using: {csv_path}")

    process_id = None
    if csv_path.exists():
        with open(csv_path, "rb") as f:
            files = {"file": ("sample_log.csv", f, "text/csv")}
            data = {
                "name": "E2E Test Log",
                "case_id_column": "case:concept:name",
                "activity_column": "concept:name",
                "timestamp_column": "time:timestamp",
                "resource_column": "org:resource"
            }
            ok, resp = test_endpoint("POST", "/processes/upload", "Upload CSV", files=files, data=data)
            if ok and resp:
                process_id = resp.get("id")
                log_info(f"Process ID: {process_id}")

    # ========== PROCESS ENDPOINTS ==========
    if process_id:
        log_section("4. Process CRUD & Statistics")
        test_endpoint("GET", "/processes", "List Processes")
        test_endpoint("GET", f"/processes/{process_id}", "Get Process")
        test_endpoint("GET", f"/processes/{process_id}/statistics", "Get Statistics")
        test_endpoint("GET", f"/processes/{process_id}/cases", "List Cases")
        test_endpoint("GET", f"/processes/{process_id}/variants", "Get Variants")
        test_endpoint("GET", f"/processes/{process_id}/activities", "Get Activities")

        # ========== DISCOVERY ==========
        log_section("5. Discovery Endpoints")
        test_endpoint("GET", "/discovery/miners", "List Miners")

        model_id = None
        # Use correct enum values
        for algo in ["alpha", "heuristics", "inductive"]:
            ok, model_data = test_endpoint(
                "POST", "/discovery/discover", f"Discover ({algo})",
                json_data={"log_id": process_id, "miner_type": algo}
            )
            if ok and model_data:
                model_id = model_data.get("id")
                log_info(f"Model ID ({algo}): {model_id}")

        test_endpoint("GET", "/discovery/models", "List Models")

        # ========== CONFORMANCE ==========
        if model_id:
            log_section("6. Conformance Checking")
            test_endpoint("GET", "/conformance/methods", "List Methods")
            test_endpoint(
                "POST", "/conformance/check", "Check Conformance",
                json_data={"log_id": process_id, "model_id": model_id, "method": "token_replay"}
            )
            test_endpoint("GET", f"/conformance/results", "List Results")

        # ========== ANALYTICS ==========
        log_section("7. Analytics Endpoints")
        test_endpoint("GET", f"/analytics/logs/{process_id}/bottlenecks", "Bottlenecks")
        test_endpoint("GET", f"/analytics/logs/{process_id}/rework", "Rework Analysis")
        test_endpoint("GET", f"/analytics/logs/{process_id}/service-times", "Service Times")
        test_endpoint("GET", f"/analytics/logs/{process_id}/cycle-time", "Cycle Time")
        test_endpoint("GET", f"/analytics/logs/{process_id}/throughput", "Throughput")
        test_endpoint("GET", f"/analytics/logs/{process_id}/performance", "Performance Dashboard")
        test_endpoint("GET", f"/analytics/logs/{process_id}/rework-chains", "Rework Chains")
        test_endpoint("GET", f"/analytics/logs/{process_id}/patterns", "Patterns")

        # ========== VISUALIZATION ==========
        log_section("8. Visualization Endpoints")
        test_endpoint("GET", f"/visualization/{process_id}/dfg", "DFG")

    # ========== STORAGE CHECK ==========
    log_section("9. Local Storage Verification")
    storage_path = Path(__file__).parent / "data" / "uploads"
    if storage_path.exists():
        files = list(storage_path.glob("**/*"))
        file_count = len([f for f in files if f.is_file()])
        log_success(f"Found {file_count} files in storage")
        for f in list(files)[:3]:
            if f.is_file():
                print(f"   - {f.relative_to(storage_path)} ({f.stat().st_size:,} bytes)")

    # ========== SUMMARY ==========
    total = results["passed"] + results["failed"]
    print(f"\n{GREEN}{'='*60}")
    print(f"  RESULTS: {results['passed']}/{total} passed ({results['passed']*100//total}%)")
    print(f"{'='*60}{RESET}\n")


if __name__ == "__main__":
    main()
