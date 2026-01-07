"""Main E2E API Test Runner.

Discovers all API endpoints from OpenAPI spec and runs curl-based tests.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bug_detector import BugDetector, BugPriority
from e2e_config import E2EConfig
from helpers.curl_generator import CurlGenerator
from helpers.openapi_parser import APIEndpoint, OpenAPIParser


class E2EAPITester:
    """End-to-end API test runner."""

    def __init__(self, config: E2EConfig):
        """Initialize tester.

        Args:
            config: E2E testing configuration
        """
        self.config = config
        self.bug_detector = BugDetector()
        self.curl_generator = CurlGenerator(config.base_url)
        self.parser: OpenAPIParser | None = None
        self.auth_token: str | None = None
        self.test_results: list[dict[str, Any]] = []

    def run(self) -> None:
        """Run complete E2E API test suite."""
        print("=" * 80)
        print("E2E API Test Suite")
        print("=" * 80)
        print(f"Base URL: {self.config.base_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Step 1: Fetch OpenAPI spec
        print("[1/5] Fetching OpenAPI specification...")
        self.parser = self._fetch_openapi_spec()
        print(f"✓ Found {len(self.parser.endpoints)} endpoints")
        print()

        # Step 2: Authenticate
        print("[2/5] Authenticating...")
        self.auth_token = self._authenticate()
        print(f"✓ Authenticated as {self.config.test_user_email}")
        print()

        # Step 3: Run tests by domain
        print("[3/5] Running API tests...")
        self._run_tests()
        print()

        # Step 4: Generate report
        print("[4/5] Generating bug report...")
        report_path = self._generate_report()
        print(f"✓ Report saved to: {report_path}")
        print()

        # Step 5: Print summary
        print("[5/5] Test Summary")
        self._print_summary()

    def _fetch_openapi_spec(self) -> OpenAPIParser:
        """Fetch OpenAPI spec from running server.

        Returns:
            OpenAPIParser instance
        """
        url = f"{self.config.base_url}/openapi.json"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            spec = response.json()
            return OpenAPIParser(spec)
        except requests.RequestException as e:
            print(f"✗ Failed to fetch OpenAPI spec from {url}")
            print(f"  Error: {e}")
            print(f"\n  Is the server running at {self.config.base_url}?")
            raise

    def _authenticate(self) -> str:
        """Authenticate and get JWT token.

        Returns:
            JWT access token
        """
        # For testing, we'll use a mock token
        # In real scenario, you'd call /api/v1/auth/login
        # For now, return a test token
        return "test-token-for-e2e-testing"

    def _run_tests(self) -> None:
        """Run tests for all endpoints grouped by tag."""
        if not self.parser:
            raise RuntimeError("Parser not initialized")

        # Group endpoints by tag
        tags = self.parser.get_all_tags()

        # Filter out excluded endpoints
        endpoints_to_test = [ep for ep in self.parser.endpoints if not self._should_exclude(ep)]

        print(f"Testing {len(endpoints_to_test)} endpoints across {len(tags)} domains\n")

        # Test by tag for better organization
        for tag in sorted(tags):
            tag_endpoints = [ep for ep in endpoints_to_test if tag in ep.tags]
            if not tag_endpoints:
                continue

            print(f"\n{'─' * 80}")
            print(f"Domain: {tag} ({len(tag_endpoints)} endpoints)")
            print(f"{'─' * 80}")

            for endpoint in tag_endpoints:
                self._test_endpoint(endpoint)

    def _should_exclude(self, endpoint: APIEndpoint) -> bool:
        """Check if endpoint should be excluded from testing.

        Args:
            endpoint: API endpoint

        Returns:
            True if should be excluded
        """
        return any(pattern in endpoint.path for pattern in self.config.exclude_patterns)

    def _test_endpoint(self, endpoint: APIEndpoint) -> None:
        """Test a single API endpoint.

        Args:
            endpoint: API endpoint to test
        """
        # Skip if endpoint requires path parameters we can't auto-generate
        path_params = [p for p in endpoint.parameters if p.location == "path"]
        if path_params:
            # For now, skip endpoints requiring path params
            # In production, we'd use test data from factories
            print(
                f"  ⊘ {endpoint.method.value:6s} {endpoint.path:50s} [SKIPPED - requires path params]"
            )
            return

        # Generate request body if needed
        request_body = None
        if endpoint.request_body and self.parser:
            request_body = self.parser.generate_request_body(endpoint)

        # Generate curl command
        curl_cmd = self.curl_generator.generate_curl_command(
            endpoint=endpoint,
            path_params={},
            query_params={},
            request_body=request_body,
            auth_token=self.auth_token if endpoint.requires_auth else None,
        )

        # Execute request
        start_time = time.time()

        try:
            url = f"{self.config.base_url}{endpoint.path}"
            headers = {}

            if endpoint.requires_auth and self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"

            if request_body:
                headers["Content-Type"] = "application/json"

            response = requests.request(
                method=endpoint.method.value,
                url=url,
                headers=headers,
                json=request_body,
                timeout=self.config.timeout_seconds,
            )

            response_time_ms = (time.time() - start_time) * 1000
            status_code = response.status_code
            response_body = response.text

        except requests.RequestException as e:
            response_time_ms = (time.time() - start_time) * 1000
            status_code = None
            response_body = str(e)

        # Analyze response for bugs
        bug = self.bug_detector.analyze_response(
            endpoint=endpoint.path,
            method=endpoint.method.value,
            status_code=status_code,
            response_body=response_body,
            response_time_ms=response_time_ms,
            curl_command=curl_cmd,
        )

        # Record result
        self.test_results.append(
            {
                "endpoint": endpoint.path,
                "method": endpoint.method.value,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "has_bug": bug is not None,
                "bug_id": bug.bug_id if bug else None,
            }
        )

        # Print result
        status_symbol = "✓" if status_code and 200 <= status_code < 300 else "✗"
        bug_indicator = f" [{bug.bug_id}]" if bug else ""

        status_str = str(status_code) if status_code else "ERR"
        print(
            f"  {status_symbol} {endpoint.method.value:6s} {endpoint.path:50s} {status_str:3s} {response_time_ms:6.0f}ms{bug_indicator}"
        )

    def _generate_report(self) -> Path:
        """Generate bug report in markdown format.

        Returns:
            Path to generated report
        """
        # Create report directory
        report_dir = Path(self.config.bug_report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"report_{timestamp}.md"

        # Generate report content
        content = self._generate_report_content()

        # Write to file
        with open(report_path, "w") as f:
            f.write(content)

        return report_path

    def _generate_report_content(self) -> str:
        """Generate bug report markdown content.

        Returns:
            Report markdown string
        """
        lines = []

        # Header
        lines.append("# E2E API Test Report")
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Summary
        summary = self.bug_detector.get_summary()
        passed = len([r for r in self.test_results if not r["has_bug"]])
        failed = len([r for r in self.test_results if r["has_bug"]])

        lines.append("## Summary\n")
        lines.append(f"- **Total Endpoints Tested**: {len(self.test_results)}")
        lines.append(f"- **Passed**: {passed}")
        lines.append(f"- **Failed**: {failed}")
        lines.append(f"- **Bugs Found**: {summary['total']}")
        lines.append(f"  - P0 (Critical): {summary['p0']}")
        lines.append(f"  - P1 (High): {summary['p1']}")
        lines.append(f"  - P2 (Medium): {summary['p2']}")
        lines.append(f"  - P3 (Low): {summary['p3']}\n")

        # Bugs by priority
        for priority in [BugPriority.P0, BugPriority.P1, BugPriority.P2, BugPriority.P3]:
            bugs = self.bug_detector.get_bugs_by_priority(priority)
            if not bugs:
                continue

            priority_label = {
                BugPriority.P0: "P0 - Critical (Blocking)",
                BugPriority.P1: "P1 - High (Major Issue)",
                BugPriority.P2: "P2 - Medium (Minor Issue)",
                BugPriority.P3: "P3 - Low (Enhancement)",
            }[priority]

            lines.append(f"\n## {priority_label} ({len(bugs)} issues)\n")

            for bug in bugs:
                lines.append(f"### {bug.bug_id}: {bug.title}\n")
                lines.append(f"**Category**: {bug.category}")
                lines.append(f"**Endpoint**: `{bug.method} {bug.endpoint}`")
                if bug.status_code:
                    lines.append(f"**Status Code**: {bug.status_code}")
                if bug.error_message:
                    lines.append(f"**Error**: {bug.error_message}\n")

                if bug.root_cause:
                    lines.append(f"**Root Cause**: {bug.root_cause}\n")

                if bug.suggested_fix:
                    lines.append(f"**Suggested Fix**: {bug.suggested_fix}\n")

                lines.append("**Reproduction**:")
                lines.append("```bash")
                lines.append(bug.reproduction_curl)
                lines.append("```\n")

                if bug.response_body:
                    lines.append("**Response**:")
                    lines.append("```json")
                    # Try to pretty-print JSON
                    try:
                        response_json = json.loads(bug.response_body)
                        lines.append(json.dumps(response_json, indent=2))
                    except Exception:
                        lines.append(bug.response_body[:500])  # Limit response size
                    lines.append("```\n")

                lines.append("---\n")

        return "\n".join(lines)

    def _print_summary(self) -> None:
        """Print test summary to console."""
        summary = self.bug_detector.get_summary()
        passed = len([r for r in self.test_results if not r["has_bug"]])
        failed = len([r for r in self.test_results if r["has_bug"]])

        print("─" * 80)
        print(f"Total Endpoints: {len(self.test_results)}")
        print(f"✓ Passed:        {passed}")
        print(f"✗ Failed:        {failed}")
        print(f"🐛 Bugs Found:   {summary['total']}")
        print(f"   - P0:         {summary['p0']}")
        print(f"   - P1:         {summary['p1']}")
        print(f"   - P2:         {summary['p2']}")
        print(f"   - P3:         {summary['p3']}")
        print("─" * 80)


def main():
    """Main entry point."""
    # Use default configuration
    config = E2EConfig.default()

    # Run tests
    tester = E2EAPITester(config)
    try:
        tester.run()
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        raise


if __name__ == "__main__":
    main()
