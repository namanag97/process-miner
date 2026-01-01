# ADR-005: Enterprise Error Handling

## Status

Accepted

## Context

Enterprise applications require:

- Consistent error responses for client applications
- Machine-readable error codes for automation
- Actionable error details for debugging
- Retry guidance for transient failures
- Audit trail via correlation IDs

The initial implementation had 4 basic exceptions. This was insufficient for production use.

## Decision

Implement enterprise-grade error handling with:

1. **Typed Error Codes** - Machine-readable codes (ERR_100-599)
2. **RFC 7807 Problem Details** - Standard error response format
3. **Exception Hierarchy** - 20+ exception types for specific cases
4. **Correlation IDs** - Request tracing across services
5. **Retry Hints** - Retry-After headers for rate limits

### Error Code Categories

| Range   | Category         | Example                          |
| ------- | ---------------- | -------------------------------- |
| ERR_1xx | Validation       | ERR_100 (VALIDATION_FAILED)      |
| ERR_2xx | Resource         | ERR_200 (RESOURCE_NOT_FOUND)     |
| ERR_3xx | Processing       | ERR_300 (PROCESSING_FAILED)      |
| ERR_4xx | External Service | ERR_400 (EXTERNAL_SERVICE_ERROR) |
| ERR_5xx | System           | ERR_500 (INTERNAL_ERROR)         |

### RFC 7807 Response Format

```json
{
  "type": "https://api.processmining.io/errors/ERR_200",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "Process not found: abc-123",
  "error_code": "ERR_200",
  "instance": "/api/v1/processes/abc-123",
  "correlation_id": "req-xyz-456",
  "timestamp": "2026-01-01T12:00:00Z"
}
```

### Exception Hierarchy

```
AppException
├── ValidationError
│   ├── InvalidInputError
│   └── InvalidFileError
├── NotFoundError
│   ├── ProjectNotFoundError
│   ├── ProcessNotFoundError
│   └── ModelNotFoundError
├── ConflictError
│   └── ConcurrencyError
├── ProcessingError
│   ├── DiscoveryError
│   ├── ConformanceError
│   └── TimeoutError
├── ExternalServiceError
│   ├── PM4PyError
│   └── DatabaseError
└── RateLimitError
```

## Consequences

### Positive

- **Client integration** - Standard format for error handling
- **Debugging** - Correlation IDs trace requests
- **Automation** - Error codes enable programmatic handling
- **Resilience** - Retry hints reduce failed retries

### Negative

- **Complexity** - More exception types to manage
- **Migration** - Existing code needs updates
- **Documentation** - Error catalog must be maintained

### Files Added

- `src/core/error_codes.py` - Error code catalog
- `src/core/exceptions.py` - Exception hierarchy
- Updated `src/api/main.py` - RFC 7807 responses
