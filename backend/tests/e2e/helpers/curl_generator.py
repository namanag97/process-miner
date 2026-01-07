"""Curl Command Generator for E2E API Testing.

Generates curl commands from OpenAPI endpoint definitions.
"""

import json
from typing import Any

from .openapi_parser import APIEndpoint, HTTPMethod


class CurlGenerator:
    """Generate curl commands for API testing."""

    def __init__(self, base_url: str):
        """Initialize curl generator.

        Args:
            base_url: Base URL for API (e.g., http://localhost:8001)
        """
        self.base_url = base_url.rstrip("/")

    def generate_curl_command(
        self,
        endpoint: APIEndpoint,
        path_params: dict[str, str] | None = None,
        query_params: dict[str, str] | None = None,
        request_body: Any = None,
        auth_token: str | None = None,
        additional_headers: dict[str, str] | None = None,
    ) -> str:
        """Generate a curl command for an API endpoint.

        Args:
            endpoint: API endpoint definition
            path_params: Path parameter values
            query_params: Query parameter values
            request_body: Request body data
            auth_token: JWT auth token
            additional_headers: Additional HTTP headers

        Returns:
            Formatted curl command string
        """
        path_params = path_params or {}
        query_params = query_params or {}
        additional_headers = additional_headers or {}

        # Build URL
        url = self._build_url(endpoint, path_params, query_params)

        # Build curl command parts
        parts = ["curl", "-X", endpoint.method.value]

        # Add URL
        parts.append(f"'{url}'")

        # Add headers
        headers = {}

        # Auth header
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        # Content-Type for POST/PUT/PATCH with body
        if endpoint.method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
            if request_body is not None:
                headers["Content-Type"] = "application/json"

        # Additional headers
        headers.update(additional_headers)

        # Add header flags
        for key, value in headers.items():
            parts.append("-H")
            parts.append(f"'{key}: {value}'")

        # Add request body
        if request_body is not None:
            if isinstance(request_body, (dict, list)):
                body_json = json.dumps(request_body, indent=2)
                parts.append("-d")
                parts.append(f"'{body_json}'")
            else:
                parts.append("-d")
                parts.append(f"'{request_body}'")

        # Join with newlines and backslashes for readability
        return " \\\n  ".join(parts)

    def _build_url(
        self,
        endpoint: APIEndpoint,
        path_params: dict[str, str],
        query_params: dict[str, str],
    ) -> str:
        """Build complete URL with path and query parameters.

        Args:
            endpoint: API endpoint
            path_params: Path parameter values
            query_params: Query parameter values

        Returns:
            Complete URL string
        """
        # Replace path parameters
        url_path = endpoint.path
        for param_name, param_value in path_params.items():
            url_path = url_path.replace(f"{{{param_name}}}", str(param_value))

        # Build full URL
        full_url = f"{self.base_url}{url_path}"

        # Add query parameters
        if query_params:
            query_string = "&".join(f"{key}={value}" for key, value in query_params.items())
            full_url = f"{full_url}?{query_string}"

        return full_url

    def generate_simple_curl(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: Any = None,
    ) -> str:
        """Generate a simple curl command.

        Args:
            method: HTTP method
            url: Full URL
            headers: HTTP headers
            body: Request body

        Returns:
            Formatted curl command
        """
        headers = headers or {}

        parts = ["curl", "-X", method.upper(), f"'{url}'"]

        for key, value in headers.items():
            parts.append("-H")
            parts.append(f"'{key}: {value}'")

        if body is not None:
            if isinstance(body, (dict, list)):
                body_json = json.dumps(body, indent=2)
                parts.append("-d")
                parts.append(f"'{body_json}'")
            else:
                parts.append("-d")
                parts.append(f"'{body}'")

        return " \\\n  ".join(parts)
