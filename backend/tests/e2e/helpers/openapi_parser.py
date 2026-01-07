"""OpenAPI Specification Parser for E2E API Testing.

Extracts endpoints, schemas, and generates test data from OpenAPI spec.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class HTTPMethod(str, Enum):
    """HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class Parameter:
    """Request parameter definition."""

    name: str
    location: str  # path, query, header, cookie
    required: bool
    schema: dict[str, Any]
    description: str | None = None


@dataclass
class APIEndpoint:
    """Parsed API endpoint information."""

    path: str
    method: HTTPMethod
    operation_id: str | None
    summary: str | None
    description: str | None
    tags: list[str]
    parameters: list[Parameter]
    request_body: dict[str, Any] | None
    responses: dict[str, dict[str, Any]]
    security: list[dict[str, list[str]]] | None

    @property
    def requires_auth(self) -> bool:
        """Check if endpoint requires authentication."""
        return self.security is not None and len(self.security) > 0

    @property
    def primary_tag(self) -> str:
        """Get primary tag for grouping."""
        return self.tags[0] if self.tags else "Untagged"


class OpenAPIParser:
    """Parse OpenAPI specification and extract endpoint information."""

    def __init__(self, spec: dict[str, Any]):
        """Initialize parser with OpenAPI spec dictionary.

        Args:
            spec: OpenAPI specification as dictionary
        """
        self.spec = spec
        self.endpoints: list[APIEndpoint] = []
        self._parse()

    def _parse(self) -> None:
        """Parse the OpenAPI spec and extract all endpoints."""
        paths = self.spec.get("paths", {})

        for path, path_item in paths.items():
            # Skip non-method keys like 'parameters', 'summary', etc.
            for method in ["get", "post", "put", "patch", "delete"]:
                if method not in path_item:
                    continue

                operation = path_item[method]

                # Parse parameters
                parameters = self._parse_parameters(
                    operation.get("parameters", []), path_item.get("parameters", [])
                )

                # Parse request body
                request_body = None
                if "requestBody" in operation:
                    request_body = operation["requestBody"]

                # Parse responses
                responses = operation.get("responses", {})

                # Parse security
                security = operation.get("security")

                endpoint = APIEndpoint(
                    path=path,
                    method=HTTPMethod(method.upper()),
                    operation_id=operation.get("operationId"),
                    summary=operation.get("summary"),
                    description=operation.get("description"),
                    tags=operation.get("tags", []),
                    parameters=parameters,
                    request_body=request_body,
                    responses=responses,
                    security=security,
                )

                self.endpoints.append(endpoint)

    def _parse_parameters(
        self, operation_params: list[dict[str, Any]], path_params: list[dict[str, Any]]
    ) -> list[Parameter]:
        """Parse parameters from operation and path level.

        Args:
            operation_params: Parameters defined at operation level
            path_params: Parameters defined at path level

        Returns:
            List of Parameter objects
        """
        all_params = path_params + operation_params
        parameters = []

        for param_def in all_params:
            # Handle $ref references
            if "$ref" in param_def:
                param_def = self._resolve_ref(param_def["$ref"])

            param = Parameter(
                name=param_def.get("name", ""),
                location=param_def.get("in", "query"),
                required=param_def.get("required", False),
                schema=param_def.get("schema", {}),
                description=param_def.get("description"),
            )
            parameters.append(param)

        return parameters

    def _resolve_ref(self, ref: str) -> dict[str, Any]:
        """Resolve a $ref reference in the spec.

        Args:
            ref: Reference string like "#/components/schemas/User"

        Returns:
            Resolved schema object
        """
        parts = ref.lstrip("#/").split("/")
        current = self.spec

        for part in parts:
            current = current.get(part, {})

        return current

    def get_endpoints_by_tag(self, tag: str) -> list[APIEndpoint]:
        """Get all endpoints with a specific tag.

        Args:
            tag: Tag name to filter by

        Returns:
            List of endpoints with the tag
        """
        return [ep for ep in self.endpoints if tag in ep.tags]

    def get_all_tags(self) -> list[str]:
        """Get all unique tags from endpoints.

        Returns:
            Sorted list of unique tags
        """
        tags = set()
        for endpoint in self.endpoints:
            tags.update(endpoint.tags)
        return sorted(tags)

    def generate_test_data(self, schema: dict[str, Any]) -> Any:
        """Generate test data from JSON schema.

        Args:
            schema: JSON schema definition

        Returns:
            Generated test data matching schema
        """
        schema_type = schema.get("type")

        if schema_type == "string":
            # Check for format
            format_type = schema.get("format")
            if format_type == "date-time":
                return "2024-01-01T10:00:00Z"
            if format_type == "uuid":
                return "00000000-0000-0000-0000-000000000001"
            if format_type == "email":
                return "test@example.com"

            # Check for enum
            if "enum" in schema:
                return schema["enum"][0]

            return "test_string"

        if schema_type == "integer":
            return schema.get("minimum", 1)

        if schema_type == "number":
            return schema.get("minimum", 1.0)

        if schema_type == "boolean":
            return True

        if schema_type == "array":
            items_schema = schema.get("items", {})
            return [self.generate_test_data(items_schema)]

        if schema_type == "object":
            properties = schema.get("properties", {})
            required = schema.get("required", [])

            obj = {}
            for prop_name, prop_schema in properties.items():
                # Only generate required properties for now
                if prop_name in required:
                    obj[prop_name] = self.generate_test_data(prop_schema)

            return obj

        # Handle $ref
        if "$ref" in schema:
            resolved = self._resolve_ref(schema["$ref"])
            return self.generate_test_data(resolved)

        # Default
        return None

    def get_request_body_schema(self, endpoint: APIEndpoint) -> dict[str, Any] | None:
        """Get the request body JSON schema for an endpoint.

        Args:
            endpoint: API endpoint

        Returns:
            JSON schema for request body or None
        """
        if not endpoint.request_body:
            return None

        content = endpoint.request_body.get("content", {})

        # Try application/json first
        if "application/json" in content:
            return content["application/json"].get("schema")

        # Try multipart/form-data (for file uploads)
        if "multipart/form-data" in content:
            return content["multipart/form-data"].get("schema")

        return None

    def generate_request_body(self, endpoint: APIEndpoint) -> Any:
        """Generate test request body for an endpoint.

        Args:
            endpoint: API endpoint

        Returns:
            Generated request body data
        """
        schema = self.get_request_body_schema(endpoint)
        if not schema:
            return None

        return self.generate_test_data(schema)
