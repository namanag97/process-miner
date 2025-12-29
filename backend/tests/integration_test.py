#!/usr/bin/env python3
"""Integration Test with Focused Logging.

Runs against a live backend server and tests key API flows.
Saves focused, content-centric logs with timestamps.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")
API_PREFIX = "/api/v1"
LOG_DIR = Path(__file__).parent.parent.parent / "logs"


class FocusedLogger:
    """Logger that produces focused, content-centric output."""

    def __init__(self, log_path: Path):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.log_path = log_path
        self.results: list[str] = []
        self.passed = 0
        self.failed = 0

    def log(self, status: str, endpoint: str, summary: str):
        """Log a test result with focused format."""
        icon = "✓" if status == "PASS" else "✗"
        line = f"[{status}] {icon} {endpoint}: {summary}"
        self.results.append(line)
        print(line)
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1

    def section(self, title: str):
        """Log a section header."""
        line = f"\n{'='*60}\n  {title}\n{'='*60}"
        self.results.append(line)
        print(line)

    def save(self):
        """Save results to file."""
        header = [
            f"Integration Test Report",
            f"Timestamp: {datetime.now().isoformat()}",
            f"Backend URL: {BASE_URL}",
            f"Results: {self.passed} passed, {self.failed} failed",
            "",
        ]
        content = "\n".join(header + self.results)
        self.log_path.write_text(content)
        print(f"\n📝 Log saved: {self.log_path}")


class IntegrationTest:
    """Integration test runner."""

    def __init__(self, logger: FocusedLogger):
        self.logger = logger
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.log_id: str | None = None
        self.model_id: str | None = None

    async def close(self):
        await self.client.aclose()

    async def run_all(self):
        """Run all integration tests."""
        self.logger.section("HEALTH CHECKS")
        await self.test_health()

        self.logger.section("AUTHENTICATION")
        await self.test_auth()

        self.logger.section("EVENT LOGS")
        await self.test_logs()

        self.logger.section("PROCESS DISCOVERY")
        await self.test_discovery()

        self.logger.section("CONFORMANCE CHECKING")
        await self.test_conformance()

        self.logger.section("PERFORMANCE ANALYSIS")
        await self.test_performance()

        self.logger.section("SUMMARY")
        self.logger.save()

    async def test_health(self):
        """Test health endpoints."""
        # Root
        try:
            r = await self.client.get("/")
            if r.status_code == 200 and r.json().get("status") == "healthy":
                self.logger.log("PASS", "GET /", f"status={r.json()['status']}")
            else:
                self.logger.log("FAIL", "GET /", f"status_code={r.status_code}")
        except Exception as e:
            self.logger.log("FAIL", "GET /", str(e))

        # Health detail
        try:
            r = await self.client.get("/health")
            if r.status_code == 200:
                data = r.json()
                self.logger.log("PASS", "GET /health", f"db={data.get('database', 'n/a')}")
            else:
                self.logger.log("FAIL", "GET /health", f"status_code={r.status_code}")
        except Exception as e:
            self.logger.log("FAIL", "GET /health", str(e))

    async def test_auth(self):
        """Test auth endpoints."""
        # Login
        try:
            r = await self.client.post(
                f"{API_PREFIX}/auth/login",
                json={"email": "test@example.com", "password": "test"},
            )
            if r.status_code == 200 and "access_token" in r.json():
                self.logger.log("PASS", "POST /auth/login", "token_received=true")
            else:
                self.logger.log("FAIL", "POST /auth/login", f"status_code={r.status_code}")
        except Exception as e:
            self.logger.log("FAIL", "POST /auth/login", str(e))

        # Get me
        try:
            r = await self.client.get(f"{API_PREFIX}/auth/me")
            if r.status_code == 200:
                email = r.json().get("email", "n/a")
                self.logger.log("PASS", "GET /auth/me", f"email={email}")
            else:
                self.logger.log("FAIL", "GET /auth/me", f"status_code={r.status_code}")
        except Exception as e:
            self.logger.log("FAIL", "GET /auth/me", str(e))

    async def test_logs(self):
        """Test event log endpoints."""
        # List logs
        try:
            r = await self.client.get(f"{API_PREFIX}/logs/")
            if r.status_code == 200:
                data = r.json()
                self.logger.log("PASS", "GET /logs/", f"total={data.get('total', 0)}")
            else:
                self.logger.log("FAIL", "GET /logs/", f"status_code={r.status_code}")
        except Exception as e:
            self.logger.log("FAIL", "GET /logs/", str(e))

        # Upload log
        sample_csv = b"""case_id,activity,timestamp,resource
C001,Create Order,2024-01-01 09:00:00,Alice
C001,Review Order,2024-01-01 10:00:00,Bob
C001,Approve Order,2024-01-01 11:00:00,Charlie
C001,Ship Order,2024-01-01 14:00:00,Dave
C002,Create Order,2024-01-01 09:30:00,Alice
C002,Review Order,2024-01-01 10:30:00,Bob
C002,Reject Order,2024-01-01 11:30:00,Charlie
C003,Create Order,2024-01-01 10:00:00,Eve
C003,Review Order,2024-01-01 11:00:00,Frank
C003,Approve Order,2024-01-01 12:00:00,Charlie
C003,Ship Order,2024-01-01 15:00:00,Dave
"""
        try:
            r = await self.client.post(
                f"{API_PREFIX}/logs/upload",
                files={"file": ("test.csv", sample_csv, "text/csv")},
            )
            if r.status_code == 200:
                data = r.json()
                self.log_id = data.get("id")
                self.logger.log(
                    "PASS",
                    "POST /logs/upload",
                    f"id={self.log_id[:8]}... cases={data.get('total_cases')} events={data.get('total_events')}",
                )
            else:
                self.logger.log("FAIL", "POST /logs/upload", f"status_code={r.status_code}")
        except Exception as e:
            self.logger.log("FAIL", "POST /logs/upload", str(e))

        # Get log statistics
        if self.log_id:
            try:
                r = await self.client.get(f"{API_PREFIX}/logs/{self.log_id}/statistics")
                if r.status_code == 200:
                    data = r.json()
                    self.logger.log(
                        "PASS",
                        f"GET /logs/{{id}}/statistics",
                        f"unique_activities={data.get('unique_activities', 0)}",
                    )
                else:
                    self.logger.log("FAIL", f"GET /logs/{{id}}/statistics", f"status_code={r.status_code}")
            except Exception as e:
                self.logger.log("FAIL", f"GET /logs/{{id}}/statistics", str(e))

    async def test_discovery(self):
        """Test process discovery endpoints."""
        # List miners
        try:
            r = await self.client.get(f"{API_PREFIX}/discovery/miners")
            if r.status_code == 200:
                miners = r.json()
                self.logger.log("PASS", "GET /discovery/miners", f"count={len(miners)}")
            else:
                self.logger.log("FAIL", "GET /discovery/miners", f"status_code={r.status_code}")
        except Exception as e:
            self.logger.log("FAIL", "GET /discovery/miners", str(e))

        # Discover model
        if self.log_id:
            try:
                r = await self.client.post(
                    f"{API_PREFIX}/discovery/discover",
                    json={"log_id": self.log_id, "miner_type": "inductive"},
                )
                if r.status_code == 200:
                    data = r.json()
                    self.model_id = data.get("model_id")
                    self.logger.log(
                        "PASS",
                        "POST /discovery/discover",
                        f"model_id={self.model_id[:8] if self.model_id else 'n/a'}... miner=inductive",
                    )
                else:
                    self.logger.log("FAIL", "POST /discovery/discover", f"status_code={r.status_code}")
            except Exception as e:
                self.logger.log("FAIL", "POST /discovery/discover", str(e))

            # DFG
            try:
                r = await self.client.get(f"{API_PREFIX}/discovery/dfg/{self.log_id}")
                if r.status_code == 200:
                    data = r.json()
                    nodes = len(data.get("nodes", []))
                    edges = len(data.get("edges", []))
                    self.logger.log("PASS", "GET /discovery/dfg/{id}", f"nodes={nodes} edges={edges}")
                else:
                    self.logger.log("FAIL", "GET /discovery/dfg/{id}", f"status_code={r.status_code}")
            except Exception as e:
                self.logger.log("FAIL", "GET /discovery/dfg/{id}", str(e))

    async def test_conformance(self):
        """Test conformance checking endpoints."""
        if self.log_id and self.model_id:
            try:
                r = await self.client.post(
                    f"{API_PREFIX}/conformance/check",
                    json={"log_id": self.log_id, "model_id": self.model_id},
                )
                if r.status_code == 200:
                    data = r.json()
                    fitness = data.get("fitness", 0)
                    self.logger.log("PASS", "POST /conformance/check", f"fitness={fitness:.2%}")
                else:
                    self.logger.log("FAIL", "POST /conformance/check", f"status_code={r.status_code}")
            except Exception as e:
                self.logger.log("FAIL", "POST /conformance/check", str(e))
        else:
            self.logger.log("SKIP", "POST /conformance/check", "no log_id or model_id")

    async def test_performance(self):
        """Test performance analysis endpoints."""
        if self.log_id:
            try:
                r = await self.client.get(f"{API_PREFIX}/performance/analyze/{self.log_id}")
                if r.status_code == 200:
                    data = r.json()
                    bottlenecks = len(data.get("bottlenecks", []))
                    self.logger.log("PASS", "GET /performance/analyze/{id}", f"bottlenecks={bottlenecks}")
                else:
                    self.logger.log("FAIL", "GET /performance/analyze/{id}", f"status_code={r.status_code}")
            except Exception as e:
                self.logger.log("FAIL", "GET /performance/analyze/{id}", str(e))
        else:
            self.logger.log("SKIP", "GET /performance/analyze/{id}", "no log_id")


async def main():
    """Main entry point."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_path = LOG_DIR / f"integration_test_{timestamp}.log"

    print(f"🚀 Starting Integration Tests against {BASE_URL}")
    print(f"📁 Log output: {log_path}")

    logger = FocusedLogger(log_path)
    test = IntegrationTest(logger)

    try:
        await test.run_all()
    finally:
        await test.close()

    # Exit with error code if any tests failed
    if logger.failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
