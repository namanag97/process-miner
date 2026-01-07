"""Bug Detector for E2E API Testing.

Automatically detects and categorizes bugs from API test responses.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class BugPriority(str, Enum):
    """Bug priority levels."""
    P0 = "P0"  # Critical - Blocks functionality
    P1 = "P1"  # High - Major functionality issue
    P2 = "P2"  # Medium - Minor issue or performance problem
    P3 = "P3"  # Low - Nice to have


@dataclass
class Bug:
    """Detected bug information."""
    bug_id: str
    priority: BugPriority
    title: str
    endpoint: str
    method: str
    status_code: int | None
    error_message: str | None
    reproduction_curl: str
    response_body: str | None
    root_cause: str | None = None
    suggested_fix: str | None = None
    category: str = "General"


class BugDetector:
    """Detect bugs from API test responses."""
    
    def __init__(self):
        """Initialize bug detector."""
        self.bugs: list[Bug] = []
        self.bug_counter = 0
    
    def analyze_response(
        self,
        endpoint: str,
        method: str,
        status_code: int | None,
        response_body: str | None,
        response_time_ms: float,
        curl_command: str,
        expected_status: int = 200,
    ) -> Bug | None:
        """Analyze API response and detect bugs.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            status_code: Response status code (None if request failed)
            response_body: Response body as string
            response_time_ms: Response time in milliseconds
            curl_command: Curl command for reproduction
            expected_status: Expected status code
            
        Returns:
            Bug object if issue detected, None otherwise
        """
        bug = None
        
        # No response - connection error
        if status_code is None:
            bug = self._create_bug(
                priority=BugPriority.P0,
                title=f"Connection Error on {method} {endpoint}",
                endpoint=endpoint,
                method=method,
                status_code=None,
                error_message="Failed to connect to server",
                reproduction_curl=curl_command,
                response_body=response_body,
                root_cause="Server not responding or connection refused",
                suggested_fix="Check if server is running and accessible",
                category="Connection",
            )
        
        # HTTP 500 - Internal Server Error
        elif status_code == 500:
            error_detail = self._extract_error_message(response_body)
            
            # Detect specific error patterns
            root_cause = "Internal server error"
            suggested_fix = "Check server logs for stack trace"
            
            if response_body:
                if "blocking" in response_body.lower() and "async" in response_body.lower():
                    root_cause = "Blocking I/O operation in async context"
                    suggested_fix = "Use async-compatible file/network operations"
                    category = "Async/Sync Mixing"
                elif "database" in response_body.lower():
                    root_cause = "Database operation failed"
                    suggested_fix = "Check database connection and query syntax"
                    category = "Database"
                else:
                    category = "Internal Server Error"
            else:
                category = "Internal Server Error"
            
            bug = self._create_bug(
                priority=BugPriority.P0,
                title=f"Internal Server Error on {method} {endpoint}",
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                error_message=error_detail,
                reproduction_curl=curl_command,
                response_body=response_body,
                root_cause=root_cause,
                suggested_fix=suggested_fix,
                category=category,
            )
        
        # HTTP 422 - Validation Error
        elif status_code == 422:
            error_detail = self._extract_error_message(response_body)
            
            bug = self._create_bug(
                priority=BugPriority.P1,
                title=f"Validation Error on {method} {endpoint}",
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                error_message=error_detail,
                reproduction_curl=curl_command,
                response_body=response_body,
                root_cause="Request validation failed",
                suggested_fix="Check request schema and required fields",
                category="Validation",
            )
        
        # HTTP 401/403 - Auth errors
        elif status_code in [401, 403]:
            # Only flag as bug if endpoint should be accessible
            if self._should_be_public(endpoint):
                bug = self._create_bug(
                    priority=BugPriority.P1,
                    title=f"Authentication Error on Public Endpoint {method} {endpoint}",
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                    error_message=self._extract_error_message(response_body),
                    reproduction_curl=curl_command,
                    response_body=response_body,
                    root_cause="Public endpoint requires authentication",
                    suggested_fix="Review endpoint security configuration",
                    category="Authentication",
                )
        
        # HTTP 404 - Not Found
        elif status_code == 404 and expected_status != 404:
            bug = self._create_bug(
                priority=BugPriority.P2,
                title=f"Not Found Error on {method} {endpoint}",
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                error_message=self._extract_error_message(response_body),
                reproduction_curl=curl_command,
                response_body=response_body,
                root_cause="Endpoint or resource not found",
                suggested_fix="Check if endpoint is registered and resource exists",
                category="Not Found",
            )
        
        # Slow response
        elif response_time_ms > 5000:  # > 5 seconds
            bug = self._create_bug(
                priority=BugPriority.P2,
                title=f"Slow Response on {method} {endpoint} ({response_time_ms:.0f}ms)",
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                error_message=f"Response time: {response_time_ms:.0f}ms (threshold: 5000ms)",
                reproduction_curl=curl_command,
                response_body=None,  # Don't include body for performance issues
                root_cause="Slow endpoint performance",
                suggested_fix="Profile endpoint and optimize database queries or algorithms",
                category="Performance",
            )
        
        # Success but check for warnings
        elif 200 <= status_code < 300:
            # Could add more checks here for response schema validation
            pass
        
        if bug:
            self.bugs.append(bug)
        
        return bug
    
    def _create_bug(
        self,
        priority: BugPriority,
        title: str,
        endpoint: str,
        method: str,
        status_code: int | None,
        error_message: str | None,
        reproduction_curl: str,
        response_body: str | None,
        root_cause: str | None = None,
        suggested_fix: str | None = None,
        category: str = "General",
    ) -> Bug:
        """Create a bug object with unique ID.
        
        Args:
            priority: Bug priority
            title: Bug title
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            error_message: Error message
            reproduction_curl: Curl command to reproduce
            response_body: Response body
            root_cause: Root cause analysis
            suggested_fix: Suggested fix
            category: Bug category
            
        Returns:
            Bug object
        """
        self.bug_counter += 1
        bug_id = f"BUG-E2E-{self.bug_counter:03d}"
        
        return Bug(
            bug_id=bug_id,
            priority=priority,
            title=title,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            error_message=error_message,
            reproduction_curl=reproduction_curl,
            response_body=response_body,
            root_cause=root_cause,
            suggested_fix=suggested_fix,
            category=category,
        )
    
    def _extract_error_message(self, response_body: str | None) -> str | None:
        """Extract error message from response body.
        
        Args:
            response_body: Response body as string
            
        Returns:
            Extracted error message or None
        """
        if not response_body:
            return None
        
        try:
            import json
            data = json.loads(response_body)
            
            # Try common error fields
            if "detail" in data:
                return str(data["detail"])
            elif "message" in data:
                return str(data["message"])
            elif "error" in data:
                return str(data["error"])
            
            return response_body[:200]  # First 200 chars
        except:
            return response_body[:200]
    
    def _should_be_public(self, endpoint: str) -> bool:
        """Check if endpoint should be publicly accessible.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            True if endpoint should be public
        """
        public_endpoints = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]
        
        return endpoint in public_endpoints
    
    def get_bugs_by_priority(self, priority: BugPriority) -> list[Bug]:
        """Get all bugs with specific priority.
        
        Args:
            priority: Bug priority
            
        Returns:
            List of bugs with the priority
        """
        return [bug for bug in self.bugs if bug.priority == priority]
    
    def get_summary(self) -> dict[str, int]:
        """Get bug summary statistics.
        
        Returns:
            Dictionary with bug counts by priority
        """
        return {
            "total": len(self.bugs),
            "p0": len(self.get_bugs_by_priority(BugPriority.P0)),
            "p1": len(self.get_bugs_by_priority(BugPriority.P1)),
            "p2": len(self.get_bugs_by_priority(BugPriority.P2)),
            "p3": len(self.get_bugs_by_priority(BugPriority.P3)),
        }
