#!/usr/bin/env python3
"""
AI-Driven API Testing System

Automatically generates and executes API tests based on OpenAPI/Swagger specification.
Validates responses against schemas and generates comprehensive bug reports.
"""

import json
import sys
import time
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path
from uuid import uuid4


class OpenAPIParser:
    """Parse OpenAPI specification and extract endpoint information."""

    def __init__(self, spec_path: str):
        self.spec_path = spec_path
        self.spec = self._load_spec()
        self.paths = self.spec.get("paths", {})
        self.components = self.spec.get("components", {})
        self.schemas = self.components.get("schemas", {})

    def _load_spec(self) -> Dict:
        """Load OpenAPI spec from file."""
        try:
            with open(self.spec_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading OpenAPI spec: {e}")
            sys.exit(1)

    def get_all_endpoints(self) -> List[Dict]:
        """Extract all endpoint definitions."""
        endpoints = []
        for path, methods in self.paths.items():
            for method, spec in methods.items():
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch']:
                    continue

                endpoints.append({
                    'path': path,
                    'method': method.upper(),
                    'operation_id': spec.get('operationId', ''),
                    'summary': spec.get('summary', ''),
                    'description': spec.get('description', ''),
                    'tags': spec.get('tags', []),
                    'parameters': spec.get('parameters', []),
                    'request_body': spec.get('requestBody', {}),
                    'responses': spec.get('responses', {}),
                    'security': spec.get('security', [])
                })
        return endpoints

    def get_schema(self, ref: str) -> Optional[Dict]:
        """Resolve schema reference."""
        if not ref or not ref.startswith('#/components/schemas/'):
            return None
        schema_name = ref.replace('#/components/schemas/', '')
        return self.schemas.get(schema_name)

    def resolve_schema(self, schema: Dict) -> Dict:
        """Recursively resolve schema references."""
        if not schema:
            return {}

        if '$ref' in schema:
            resolved = self.get_schema(schema['$ref'])
            return self.resolve_schema(resolved) if resolved else {}

        # Resolve nested properties
        if 'properties' in schema:
            for prop, prop_schema in schema['properties'].items():
                if '$ref' in prop_schema:
                    schema['properties'][prop] = self.resolve_schema(prop_schema)

        # Resolve array items
        if 'items' in schema and '$ref' in schema['items']:
            schema['items'] = self.resolve_schema(schema['items'])

        return schema


class DataGenerator:
    """Generate realistic test data based on OpenAPI schemas."""

    def __init__(self, parser: OpenAPIParser):
        self.parser = parser
        self.counter = 0

    def generate_value(self, schema: Dict, field_name: str = "") -> Any:
        """Generate a value based on schema type."""
        schema = self.parser.resolve_schema(schema)

        # Handle enum
        if 'enum' in schema:
            return schema['enum'][0]

        # Handle const
        if 'const' in schema:
            return schema['const']

        # Handle examples
        if 'example' in schema:
            return schema['example']

        schema_type = schema.get('type', 'string')
        schema_format = schema.get('format', '')

        # String types
        if schema_type == 'string':
            if schema_format == 'uuid':
                return str(uuid4())
            elif schema_format == 'email':
                return f"test{self.counter}@example.com"
            elif schema_format == 'date-time':
                return datetime.utcnow().isoformat() + 'Z'
            elif schema_format == 'date':
                return datetime.utcnow().date().isoformat()
            elif schema_format == 'uri':
                return "https://example.com/test"
            elif 'id' in field_name.lower():
                return str(uuid4())
            else:
                pattern = schema.get('pattern', '')
                if pattern:
                    # Simple pattern matching
                    if pattern == '^[a-zA-Z0-9_-]+$':
                        return f"test_value_{self.counter}"
                return f"test_{field_name}_{self.counter}"

        # Numeric types
        elif schema_type == 'integer':
            minimum = schema.get('minimum', 0)
            maximum = schema.get('maximum', 100)
            return max(minimum, min(maximum, self.counter % 100))

        elif schema_type == 'number':
            minimum = schema.get('minimum', 0.0)
            maximum = schema.get('maximum', 100.0)
            return float(max(minimum, min(maximum, self.counter % 100)))

        # Boolean
        elif schema_type == 'boolean':
            return True

        # Array
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            min_items = schema.get('minItems', 0)
            max_items = schema.get('maxItems', 2)
            count = max(min_items, min(max_items, 1))
            return [self.generate_value(items_schema, field_name) for _ in range(count)]

        # Object
        elif schema_type == 'object':
            return self.generate_object(schema)

        # Fallback
        return f"value_{self.counter}"

    def generate_object(self, schema: Dict) -> Dict:
        """Generate an object from schema."""
        schema = self.parser.resolve_schema(schema)
        obj = {}
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        self.counter += 1

        # Generate required fields
        for field in required:
            if field in properties:
                obj[field] = self.generate_value(properties[field], field)

        # Optionally add some optional fields
        for field, field_schema in properties.items():
            if field not in obj and self.counter % 3 == 0:  # Add some optional fields
                obj[field] = self.generate_value(field_schema, field)

        return obj

    def generate_request_body(self, request_body_spec: Dict) -> Optional[Dict]:
        """Generate request body from OpenAPI spec."""
        if not request_body_spec:
            return None

        content = request_body_spec.get('content', {})
        json_content = content.get('application/json', {})
        schema = json_content.get('schema', {})

        if not schema:
            return None

        return self.generate_object(schema)


class SchemaValidator:
    """Validate API responses against OpenAPI schemas."""

    def __init__(self, parser: OpenAPIParser):
        self.parser = parser
        self.errors = []

    def validate(self, response_data: Any, schema: Dict, path: str = "root") -> List[str]:
        """Validate data against schema and return list of errors."""
        self.errors = []
        self._validate_recursive(response_data, schema, path)
        return self.errors

    def _validate_recursive(self, data: Any, schema: Dict, path: str):
        """Recursively validate data against schema."""
        schema = self.parser.resolve_schema(schema)

        # Handle null - check for OpenAPI 3.1 anyOf pattern
        if data is None:
            # Check if nullable via old 'nullable' property
            if schema.get('nullable', False):
                return
            # Check if nullable via anyOf pattern (OpenAPI 3.1)
            if 'anyOf' in schema:
                for sub_schema in schema['anyOf']:
                    if sub_schema.get('type') == 'null':
                        return  # Null is allowed
            # Null not allowed
            self.errors.append(f"{path}: Expected non-null value")
            return

        # Handle anyOf schemas - validate against the non-null schema
        if 'anyOf' in schema and data is not None:
            # Find the first non-null schema that matches
            for sub_schema in schema['anyOf']:
                if sub_schema.get('type') != 'null':
                    schema = sub_schema
                    break

        schema_type = schema.get('type')

        # Validate type
        if schema_type == 'string':
            if not isinstance(data, str):
                self.errors.append(f"{path}: Expected string, got {type(data).__name__}")
                return
            self._validate_string(data, schema, path)

        elif schema_type == 'integer':
            if not isinstance(data, int) or isinstance(data, bool):
                self.errors.append(f"{path}: Expected integer, got {type(data).__name__}")
                return
            self._validate_number(data, schema, path)

        elif schema_type == 'number':
            if not isinstance(data, (int, float)) or isinstance(data, bool):
                self.errors.append(f"{path}: Expected number, got {type(data).__name__}")
                return
            self._validate_number(data, schema, path)

        elif schema_type == 'boolean':
            if not isinstance(data, bool):
                self.errors.append(f"{path}: Expected boolean, got {type(data).__name__}")

        elif schema_type == 'array':
            if not isinstance(data, list):
                self.errors.append(f"{path}: Expected array, got {type(data).__name__}")
                return
            self._validate_array(data, schema, path)

        elif schema_type == 'object':
            if not isinstance(data, dict):
                self.errors.append(f"{path}: Expected object, got {type(data).__name__}")
                return
            self._validate_object(data, schema, path)

    def _validate_string(self, data: str, schema: Dict, path: str):
        """Validate string constraints."""
        if 'enum' in schema and data not in schema['enum']:
            self.errors.append(f"{path}: Value '{data}' not in enum {schema['enum']}")

        if 'pattern' in schema:
            pattern = schema['pattern']
            if not re.match(pattern, data):
                self.errors.append(f"{path}: Value '{data}' doesn't match pattern '{pattern}'")

        min_length = schema.get('minLength')
        if min_length is not None and len(data) < min_length:
            self.errors.append(f"{path}: String length {len(data)} < minimum {min_length}")

        max_length = schema.get('maxLength')
        if max_length is not None and len(data) > max_length:
            self.errors.append(f"{path}: String length {len(data)} > maximum {max_length}")

    def _validate_number(self, data: float, schema: Dict, path: str):
        """Validate number constraints."""
        minimum = schema.get('minimum')
        if minimum is not None and data < minimum:
            self.errors.append(f"{path}: Value {data} < minimum {minimum}")

        maximum = schema.get('maximum')
        if maximum is not None and data > maximum:
            self.errors.append(f"{path}: Value {data} > maximum {maximum}")

    def _validate_array(self, data: List, schema: Dict, path: str):
        """Validate array constraints."""
        min_items = schema.get('minItems')
        if min_items is not None and len(data) < min_items:
            self.errors.append(f"{path}: Array length {len(data)} < minimum {min_items}")

        max_items = schema.get('maxItems')
        if max_items is not None and len(data) > max_items:
            self.errors.append(f"{path}: Array length {len(data)} > maximum {max_items}")

        items_schema = schema.get('items', {})
        if items_schema:
            for i, item in enumerate(data):
                self._validate_recursive(item, items_schema, f"{path}[{i}]")

    def _validate_object(self, data: Dict, schema: Dict, path: str):
        """Validate object constraints."""
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        # Check required fields
        for field in required:
            if field not in data:
                self.errors.append(f"{path}: Missing required field '{field}'")

        # Validate present fields
        for field, value in data.items():
            if field in properties:
                self._validate_recursive(value, properties[field], f"{path}.{field}")


class TestExecutor:
    """Execute HTTP requests to test API endpoints."""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.state = {}  # Track created resources

    def execute(self, method: str, path: str, body: Optional[Dict] = None,
                query_params: Optional[Dict] = None) -> Tuple[int, Any, str, float]:
        """
        Execute HTTP request.
        Returns: (status_code, response_body, error_message, duration)
        """
        # Substitute path parameters from state
        resolved_path = self._resolve_path_params(path)

        # Build URL with query parameters
        url = f"{self.base_url}{resolved_path}"
        if query_params:
            query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
            url = f"{url}?{query_string}"

        # Prepare request
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        data = None
        if body:
            data = json.dumps(body).encode('utf-8')

        req = Request(url, headers=headers, method=method, data=data)

        # Execute request
        start_time = time.time()
        try:
            with urlopen(req, timeout=self.timeout) as response:
                duration = time.time() - start_time
                response_body = None
                try:
                    content = response.read().decode('utf-8')
                    if content:
                        response_body = json.loads(content)
                except Exception:
                    pass

                # Update state with created resources
                self._update_state(response_body)

                return (response.status, response_body, "", duration)

        except HTTPError as e:
            duration = time.time() - start_time
            error_body = None
            try:
                content = e.read().decode('utf-8')
                if content:
                    error_body = json.loads(content)
            except Exception:
                pass
            return (e.code, error_body, str(e.reason), duration)

        except URLError as e:
            duration = time.time() - start_time
            return (0, None, f"Network error: {e.reason}", duration)

        except Exception as e:
            duration = time.time() - start_time
            return (0, None, f"Error: {str(e)}", duration)

    def _resolve_path_params(self, path: str) -> str:
        """Resolve path parameters from state."""
        resolved = path

        # Find all path parameters {param_name}
        params = re.findall(r'\{([^}]+)\}', path)
        for param in params:
            # Try to get from state
            if param in self.state:
                resolved = resolved.replace(f"{{{param}}}", str(self.state[param]))
            else:
                # Generate a placeholder UUID for missing params
                placeholder = str(uuid4())
                self.state[param] = placeholder
                resolved = resolved.replace(f"{{{param}}}", placeholder)

        return resolved

    def _update_state(self, response_body: Any):
        """Extract and store resource IDs from response."""
        if not isinstance(response_body, dict):
            return

        # Common ID fields to track
        id_fields = ['id', 'workspace_id', 'project_id', 'user_id', 'organization_id',
                     'event_log_id', 'model_id', 'analysis_id', 'job_id']

        for field in id_fields:
            if field in response_body:
                self.state[field] = response_body[field]

        # Also check nested workspace/project objects
        if 'workspace' in response_body and isinstance(response_body['workspace'], dict):
            if 'id' in response_body['workspace']:
                self.state['workspace_id'] = response_body['workspace']['id']

        if 'project' in response_body and isinstance(response_body['project'], dict):
            if 'id' in response_body['project']:
                self.state['project_id'] = response_body['project']['id']


class BugDetector:
    """Detect and classify bugs from test results."""

    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"

    @staticmethod
    def classify_bug(test_result: Dict) -> Optional[Dict]:
        """Classify a test failure as a bug with severity."""
        status_code = test_result.get('status_code', 0)
        error_message = test_result.get('error_message', '')
        validation_errors = test_result.get('validation_errors', [])

        if status_code == 0:
            # Network error or timeout
            return {
                'severity': BugDetector.CRITICAL,
                'title': 'Network Error or Timeout',
                'description': error_message,
                'impact': 'Endpoint completely unreachable'
            }

        if status_code >= 500:
            # Server error
            return {
                'severity': BugDetector.CRITICAL,
                'title': f'Server Crash ({status_code})',
                'description': error_message or 'Internal Server Error',
                'impact': 'Complete endpoint failure, server-side crash'
            }

        if status_code == 404:
            # Not found (could be valid or bug depending on context)
            return {
                'severity': BugDetector.MAJOR,
                'title': '404 Not Found',
                'description': 'Endpoint or resource not found',
                'impact': 'Endpoint may not be implemented or resource doesn\'t exist'
            }

        if status_code >= 400 and status_code < 500:
            # Client error on what should be a valid request
            return {
                'severity': BugDetector.MAJOR,
                'title': f'Client Error on Valid Request ({status_code})',
                'description': error_message or 'Request rejected',
                'impact': 'Valid request rejected by server, possible validation issue'
            }

        if validation_errors:
            # Schema validation failed
            has_missing_required = any('Missing required' in err for err in validation_errors)
            has_type_mismatch = any('Expected' in err and 'got' in err for err in validation_errors)

            if has_missing_required:
                severity = BugDetector.MAJOR
                title = 'Schema Violation - Missing Required Fields'
            elif has_type_mismatch:
                severity = BugDetector.MAJOR
                title = 'Schema Violation - Type Mismatch'
            else:
                severity = BugDetector.MINOR
                title = 'Schema Validation Issues'

            return {
                'severity': severity,
                'title': title,
                'description': '; '.join(validation_errors[:3]),
                'impact': 'API response doesn\'t match documented schema'
            }

        return None


class ReportGenerator:
    """Generate comprehensive test reports."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_test_plan(self, endpoints: List[Dict]):
        """Generate test plan markdown."""
        content = f"# API Test Plan\n\n"
        content += f"Generated: {datetime.now().isoformat()}\n\n"
        content += f"## Summary\n\n"
        content += f"- Total Endpoints: {len(endpoints)}\n"

        # Group by tags
        by_tag = {}
        for ep in endpoints:
            tags = ep.get('tags', ['Untagged'])
            tag = tags[0] if tags else 'Untagged'
            if tag not in by_tag:
                by_tag[tag] = []
            by_tag[tag].append(ep)

        content += f"- Categories: {len(by_tag)}\n\n"

        content += f"## Test Strategy\n\n"
        content += "For each endpoint, we will:\n"
        content += "1. Execute happy path test with valid data\n"
        content += "2. Validate response status code (expect 200-299)\n"
        content += "3. Validate response body against OpenAPI schema\n"
        content += "4. Check for required fields\n"
        content += "5. Verify data types\n\n"

        content += f"## Endpoints by Category\n\n"
        for tag, eps in sorted(by_tag.items()):
            content += f"### {tag} ({len(eps)} endpoints)\n\n"
            for ep in eps:
                method = ep['method']
                path = ep['path']
                summary = ep.get('summary', 'No description')
                content += f"- **{method} {path}**: {summary}\n"
            content += "\n"

        plan_file = self.output_dir / "test_plan.md"
        with open(plan_file, 'w') as f:
            f.write(content)

        print(f"Test plan written to: {plan_file}")

    def generate_results(self, test_results: List[Dict], start_time: float):
        """Generate test results JSON."""
        end_time = time.time()
        duration = end_time - start_time

        passed = [r for r in test_results if r['status'] == 'PASS']
        failed = [r for r in test_results if r['status'] == 'FAIL']
        skipped = [r for r in test_results if r['status'] == 'SKIP']

        results = {
            'summary': {
                'total_tests': len(test_results),
                'passed': len(passed),
                'failed': len(failed),
                'skipped': len(skipped),
                'execution_time': f"{duration:.2f}s",
                'timestamp': datetime.now().isoformat()
            },
            'tests': test_results
        }

        results_file = self.output_dir / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Test results written to: {results_file}")
        return results

    def generate_summary(self, test_results: List[Dict]):
        """Generate human-readable summary."""
        passed = [r for r in test_results if r['status'] == 'PASS']
        failed = [r for r in test_results if r['status'] == 'FAIL']
        skipped = [r for r in test_results if r['status'] == 'SKIP']

        content = f"# API Test Summary\n\n"
        content += f"Generated: {datetime.now().isoformat()}\n\n"
        content += f"## Executive Summary\n\n"
        content += f"- **Total Tests**: {len(test_results)}\n"
        content += f"- **Passed**: {len(passed)} ({len(passed)*100//len(test_results) if test_results else 0}%)\n"
        content += f"- **Failed**: {len(failed)} ({len(failed)*100//len(test_results) if test_results else 0}%)\n"
        content += f"- **Skipped**: {len(skipped)}\n\n"

        if failed:
            content += f"## Failed Tests ({len(failed)})\n\n"
            for result in failed:
                endpoint = f"{result['method']} {result['path']}"
                content += f"### {endpoint}\n\n"
                content += f"- **Status Code**: {result['status_code']}\n"
                if result.get('error_message'):
                    content += f"- **Error**: {result['error_message']}\n"
                if result.get('validation_errors'):
                    content += f"- **Validation Errors**:\n"
                    for err in result['validation_errors'][:5]:
                        content += f"  - {err}\n"
                content += f"- **What was tested**: {result.get('summary', 'Happy path request')}\n"
                content += "\n"

        if passed:
            content += f"## Passed Tests ({len(passed)})\n\n"
            # Group by category
            by_tag = {}
            for result in passed:
                tag = result.get('tag', 'Other')
                if tag not in by_tag:
                    by_tag[tag] = []
                by_tag[tag].append(result)

            for tag, results in sorted(by_tag.items()):
                content += f"### {tag} ({len(results)} tests)\n\n"
                for result in results:
                    endpoint = f"{result['method']} {result['path']}"
                    summary = result.get('summary', 'Happy path successful')
                    content += f"- **{endpoint}**: {summary}\n"
                content += "\n"

        summary_file = self.output_dir / "test_summary.md"
        with open(summary_file, 'w') as f:
            f.write(content)

        print(f"Test summary written to: {summary_file}")

    def generate_bug_report(self, test_results: List[Dict]):
        """Generate bug report with severity classification."""
        bugs_by_severity = {
            BugDetector.CRITICAL: [],
            BugDetector.MAJOR: [],
            BugDetector.MINOR: []
        }

        for result in test_results:
            if result['status'] == 'FAIL':
                bug = BugDetector.classify_bug(result)
                if bug:
                    bug['endpoint'] = f"{result['method']} {result['path']}"
                    bug['status_code'] = result['status_code']
                    bug['details'] = result
                    bugs_by_severity[bug['severity']].append(bug)

        total_bugs = sum(len(bugs) for bugs in bugs_by_severity.values())

        content = f"# API Bugs Identified\n\n"
        content += f"Generated: {datetime.now().isoformat()}\n\n"
        content += f"## Summary\n\n"
        content += f"- **Total Issues**: {total_bugs}\n"
        content += f"- **Critical**: {len(bugs_by_severity[BugDetector.CRITICAL])}\n"
        content += f"- **Major**: {len(bugs_by_severity[BugDetector.MAJOR])}\n"
        content += f"- **Minor**: {len(bugs_by_severity[BugDetector.MINOR])}\n\n"

        for severity in [BugDetector.CRITICAL, BugDetector.MAJOR, BugDetector.MINOR]:
            bugs = bugs_by_severity[severity]
            if not bugs:
                continue

            content += f"## {severity} ({len(bugs)})\n\n"
            for i, bug in enumerate(bugs, 1):
                content += f"{i}. **{bug['endpoint']} - {bug['title']}**\n"
                content += f"   - Status Code: {bug['status_code']}\n"
                content += f"   - Description: {bug['description']}\n"
                content += f"   - Impact: {bug['impact']}\n"

                # Add business logic insights
                endpoint = bug['endpoint']
                if 'jobs' in endpoint.lower():
                    content += f"   - Business Impact: Job monitoring and background task management unavailable\n"
                elif 'analyses' in endpoint.lower():
                    content += f"   - Business Impact: Process analysis features cannot be accessed\n"
                elif 'workspace' in endpoint.lower():
                    content += f"   - Business Impact: Workspace management functionality broken\n"
                elif 'project' in endpoint.lower():
                    content += f"   - Business Impact: Project operations unavailable\n"
                elif 'auth' in endpoint.lower():
                    content += f"   - Business Impact: Authentication flow broken, users cannot log in\n"

                content += "\n"

        if total_bugs == 0:
            content += "## No Issues Found\n\n"
            content += "All tested endpoints returned valid responses matching their schemas.\n"

        bugs_file = self.output_dir / "bugs_identified.md"
        with open(bugs_file, 'w') as f:
            f.write(content)

        print(f"Bug report written to: {bugs_file}")


class AIAPITester:
    """Main orchestrator for AI-driven API testing."""

    def __init__(self, base_url: str, spec_path: str, output_dir: str):
        self.base_url = base_url
        self.spec_path = spec_path
        self.output_dir = output_dir

        print(f"Initializing AI API Tester...")
        print(f"Base URL: {base_url}")
        print(f"OpenAPI Spec: {spec_path}")
        print(f"Output Dir: {output_dir}\n")

        self.parser = OpenAPIParser(spec_path)
        self.data_gen = DataGenerator(self.parser)
        self.executor = TestExecutor(base_url)
        self.validator = SchemaValidator(self.parser)
        self.reporter = ReportGenerator(output_dir)

        self.test_results = []

    def run(self):
        """Main execution flow."""
        print("=" * 80)
        print("STARTING API TEST SUITE")
        print("=" * 80)

        start_time = time.time()

        # Step 1: Get all endpoints
        print("\n[1/5] Parsing OpenAPI specification...")
        endpoints = self.parser.get_all_endpoints()
        print(f"Found {len(endpoints)} endpoints to test\n")

        # Step 2: Generate test plan
        print("[2/5] Generating test plan...")
        self.reporter.generate_test_plan(endpoints)

        # Step 3: Execute tests
        print(f"\n[3/5] Executing tests...")
        self._execute_tests(endpoints)

        # Step 4: Generate reports
        print(f"\n[4/5] Generating reports...")
        self.reporter.generate_results(self.test_results, start_time)
        self.reporter.generate_summary(self.test_results)
        self.reporter.generate_bug_report(self.test_results)

        # Step 5: Print summary
        print(f"\n[5/5] Test Execution Complete!")
        self._print_summary()

    def _execute_tests(self, endpoints: List[Dict]):
        """Execute tests for all endpoints."""
        for i, endpoint in enumerate(endpoints, 1):
            method = endpoint['method']
            path = endpoint['path']
            tag = endpoint['tags'][0] if endpoint['tags'] else 'Other'

            print(f"\n[{i}/{len(endpoints)}] Testing {method} {path}")

            # Generate test data
            body = None
            if endpoint['request_body']:
                body = self.data_gen.generate_request_body(endpoint['request_body'])

            # Extract query parameters
            query_params = {}
            for param in endpoint.get('parameters', []):
                if param.get('in') == 'query' and param.get('required'):
                    param_schema = param.get('schema', {})
                    query_params[param['name']] = self.data_gen.generate_value(param_schema)

            # Execute request
            status_code, response_body, error_msg, duration = self.executor.execute(
                method, path, body, query_params
            )

            print(f"  Status: {status_code}, Duration: {duration:.2f}s")

            # Determine expected success status
            responses = endpoint.get('responses', {})
            success_codes = [code for code in responses.keys() if code.startswith('2')]
            expected_code = int(success_codes[0]) if success_codes else 200

            # Validate response
            validation_errors = []
            if status_code >= 200 and status_code < 300 and response_body:
                # Get response schema
                response_spec = responses.get(str(status_code), responses.get('200', {}))
                content = response_spec.get('content', {})
                json_content = content.get('application/json', {})
                schema = json_content.get('schema', {})

                if schema:
                    validation_errors = self.validator.validate(response_body, schema)
                    if validation_errors:
                        print(f"  Schema validation failed: {len(validation_errors)} errors")

            # Determine test status
            if status_code == 0:
                test_status = 'FAIL'
                summary = "Network error or timeout"
            elif status_code >= 200 and status_code < 300:
                if validation_errors:
                    test_status = 'FAIL'
                    summary = f"Response received but schema validation failed"
                else:
                    test_status = 'PASS'
                    summary = f"Successful {method} request, schema validated"
            else:
                test_status = 'FAIL'
                summary = f"Request failed with {status_code}"

            # Record result
            result = {
                'endpoint': f"{method} {path}",
                'method': method,
                'path': path,
                'tag': tag,
                'status': test_status,
                'status_code': status_code,
                'error_message': error_msg,
                'validation_errors': validation_errors,
                'duration': f"{duration:.2f}s",
                'summary': summary
            }

            self.test_results.append(result)

            # Small delay to avoid overwhelming the server
            time.sleep(0.1)

    def _print_summary(self):
        """Print execution summary to console."""
        passed = [r for r in self.test_results if r['status'] == 'PASS']
        failed = [r for r in self.test_results if r['status'] == 'FAIL']

        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests:  {len(self.test_results)}")
        print(f"Passed:       {len(passed)} ({len(passed)*100//len(self.test_results) if self.test_results else 0}%)")
        print(f"Failed:       {len(failed)} ({len(failed)*100//len(self.test_results) if self.test_results else 0}%)")
        print("=" * 80)

        if failed:
            print("\nFailed Tests:")
            for result in failed[:10]:  # Show first 10
                print(f"  - {result['endpoint']} ({result['status_code']}): {result['summary']}")
            if len(failed) > 10:
                print(f"  ... and {len(failed) - 10} more")

        print(f"\nDetailed reports available in: {self.output_dir}")
        print("  - test_plan.md")
        print("  - test_results.json")
        print("  - test_summary.md")
        print("  - bugs_identified.md")
        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='AI-Driven API Testing System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--base-url',
        default='http://localhost:8001',
        help='Base URL of the API (default: http://localhost:8001)'
    )
    parser.add_argument(
        '--spec',
        default='backend/docs/openapi.json',
        help='Path to OpenAPI spec (default: backend/docs/openapi.json)'
    )
    parser.add_argument(
        '--output',
        default='test',
        help='Output directory for reports (default: test)'
    )

    args = parser.parse_args()

    tester = AIAPITester(args.base_url, args.spec, args.output)
    tester.run()


if __name__ == '__main__':
    main()
