# OpenAPI Specification Audit Report
**Process Mining SaaS Platform API**
**Generated:** 2026-01-07
**Total Endpoints:** 157
**Total Schemas:** 156

---

## Executive Summary

This audit analyzed the complete OpenAPI specification of the Process Mining SaaS Platform API. The analysis covers:
- MVP release readiness (identifying features to remove/disable)
- Error handling consistency
- Security and authentication patterns
- Documentation completeness
- Request/response validation
- Code quality patterns

### Overall Status: 🟡 GOOD with Action Items

**Strengths:**
- ✅ Comprehensive documentation (all endpoints have summaries and descriptions)
- ✅ Consistent tagging and organization (27 tags, no untagged endpoints)
- ✅ Good logging practices in implementation code
- ✅ Structured error handling with custom exceptions
- ✅ No deprecated endpoints

**Critical Issues:**
- 🔴 OAuth endpoints need removal for MVP
- 🔴 Dev/debug endpoints need production safeguards
- 🟡 Inconsistent error response documentation
- 🟡 Parameter type inconsistencies
- 🟡 Missing response schemas for some endpoints

---

## 1. MVP RELEASE: ENDPOINTS TO REMOVE/DISABLE

### 🔴 HIGH PRIORITY - Remove OAuth/Social Auth

**4 endpoints to remove before MVP:**

```
DELETE: /api/v1/auth/oauth/google
DELETE: /api/v1/auth/oauth/google/callback
DELETE: /api/v1/auth/oauth/github
DELETE: /api/v1/auth/oauth/github/callback
```

**Recommendation:**
- Remove OAuth routers from `src/platform/users/api/auth.py:82` (router registration)
- Remove OAuth dependencies from backend (google-auth, github oauth libs)
- Update frontend to remove OAuth login buttons
- Document that MVP uses email/password authentication only

**Files to Modify:**
- `backend/src/platform/users/api/auth.py` - Remove OAuth route handlers
- `backend/src/api/main.py` - Ensure OAuth router not registered
- `frontend-new/src/domains/auth/` - Remove OAuth UI components

### ⚠️  MEDIUM PRIORITY - Disable Dev/Debug Endpoints in Production

**9 debug endpoints currently exposed:**

```
/api/v1/dev/log                          - Frontend log submission
/api/v1/dev/logs                         - Query logs
/api/v1/dev/logs/stream                  - SSE log streaming
/api/v1/dev/logs/metrics                 - Log metrics
/api/v1/dev/logs/recent                  - Recent logs
/api/v1/dev/logs/clear                   - Clear logs
/api/v1/dev/data/tables                  - Direct DB table access
/api/v1/dev/data/records/{table}         - Query DB records
/api/v1/dev/data/record/{table}/{record_id} - Get DB record by ID
```

**Recommendation:**
- Add environment check: only register `/dev/*` routes when `ENVIRONMENT != production`
- Add strong authentication: require admin role for dev endpoints
- Consider removing `/dev/data/*` entirely (direct DB access is security risk)
- Keep `/dev/log` if needed for production error reporting, but rate limit heavily

**Implementation:**
```python
# In src/api/main.py
from src.platform.core.config import get_settings

settings = get_settings()

# Only register dev routes in non-production
if settings.ENVIRONMENT != "production":
    from src.platform.devtools.router import router as dev_router
    app.include_router(dev_router)
```

---

## 2. ERROR HANDLING ANALYSIS

### 🟡 Issue: Inconsistent Error Response Documentation

**Finding:** Most endpoints (137 out of 157) are missing standard error response schemas in their OpenAPI spec.

**Current State:**
- Only 20 endpoints document error responses (400/401/404/422/500)
- 166 endpoints use 422 (validation errors) - properly documented
- Only HTTPValidationError schema is consistently used
- Missing standardized error schema for 400/401/404/500 responses

**Examples of Affected Endpoints:**
```
❌ GET /api/v1/datasets/ - Missing: 400, 401, 404, 500
❌ POST /api/v1/discovery/discover - Missing: 400, 401, 404, 500
❌ GET /api/v1/analytics/datasets/{dataset_id}/bottlenecks - Missing: 400, 401, 404, 500
```

**Actual Implementation Status:**
The code DOES implement proper error handling using:
- `AppException` (RFC 7807 Problem Details)
- Custom exceptions: `AuthenticationError`, `ConflictError`, `NotFoundError`
- Proper logging with structlog

**Issue:** The OpenAPI spec doesn't reflect this. FastAPI's automatic OpenAPI generation isn't capturing exception handler responses.

**Recommendation:**

1. **Define Standard Error Response Model:**
```python
# In src/platform/schemas/errors.py (create this)
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Standard RFC 7807 Problem Details error response."""
    error_code: str
    message: str
    details: dict | None = None
    timestamp: str
    request_id: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "RESOURCE_NOT_FOUND",
                "message": "Dataset not found",
                "details": {"dataset_id": "abc-123"},
                "timestamp": "2026-01-07T10:30:00Z",
                "request_id": "req-xyz"
            }
        }
```

2. **Add to All Protected Endpoints:**
```python
from src.platform.schemas.errors import ErrorResponse

@router.get(
    "/datasets/{dataset_id}",
    response_model=DatasetResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Dataset not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
```

3. **Priority Endpoints to Fix First:**
   - All dataset endpoints (16 endpoints)
   - All auth endpoints except OAuth (9 endpoints)
   - All discovery/analytics endpoints (13 endpoints)

### ✅ Positive Finding: Good Logging Implementation

**Evidence from code review:**
- All routers import and use structured logger: `logger = get_logger(__name__)`
- Logging at appropriate levels: info, warning, error, debug
- Contextual logging with structured fields
- Privacy-aware logging (email masking in auth.py:251)

**Example from auth.py:249-252:**
```python
logger.warning(
    "registration_email_exists",
    email=request.email[:3] + "***",  # Privacy: mask email
)
```

**Example from crud.py:78-86:**
```python
logger.info(
    "list_datasets_request",
    user_id=user.id,
    page=page,
    page_size=page_size,
    project_id=project_id,
    source_format=source_format,
    status_filter=status,
)
```

---

## 3. AUTHENTICATION & SECURITY

### 🟡 Issue: Many Endpoints Missing Security Declaration

**Finding:** 57 endpoints don't declare security requirements in OpenAPI spec (excluding health/auth endpoints that should be public).

**Potentially Unsecured Endpoints:**
```
GET /                                    - Root endpoint
POST /api/v1/auth/refresh                - Should require refresh token
POST /api/v1/auth/logout                 - Should require access token
GET /api/v1/analyses/metadata            - Likely should be protected
POST /api/v1/analyses                    - Likely should be protected
... and 52 more
```

**Actual Implementation:**
The code DOES use authentication via dependency injection:
```python
from src.api.dependencies import CurrentUser

async def endpoint(user: CurrentUser):
    # user is injected, requires valid JWT
```

**Issue:** FastAPI isn't auto-generating security requirements in OpenAPI because the dependency isn't explicitly declared with `Security()`.

**Recommendation:**

1. **Update dependency to explicitly declare security:**
```python
# In src/api/dependencies.py
from fastapi import Depends, Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(
    token: str = Security(security),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    # ... existing implementation
```

2. **Alternative: Add security globally in main.py:**
```python
# In src/api/main.py
app = FastAPI(
    # ... existing config
    security=[{"HTTPBearer": []}]  # Apply to all endpoints by default
)
```

### Security Schemes Defined

```yaml
securitySchemes:
  HTTPBearer:
    type: http
    scheme: bearer
```

✅ Good: Using industry-standard Bearer token authentication

---

## 4. PARAMETER VALIDATION INCONSISTENCIES

### 🔴 CRITICAL: Inconsistent ID Parameter Types

Several ID parameters have inconsistent type declarations across endpoints:

| Parameter | Inconsistency | Impact |
|-----------|---------------|--------|
| `dataset_id` | string: 64 uses, unknown: 3 uses | 3 endpoints missing type validation |
| `model_id` | string: 17 uses, unknown: 1 use | 1 endpoint missing type validation |
| `org_id` | string: 10 uses, unknown: 1 use | 1 endpoint missing type validation |
| `project_id` | string: 10 uses, unknown: 1 use | 1 endpoint missing type validation |
| `user_id` | string: 5 uses, unknown: 1 use | 1 endpoint missing type validation |
| `workspace_id` | string: 10 uses, unknown: 1 use | 1 endpoint missing type validation |
| `definition_id` | string: 1 use, unknown: 1 use | 1 endpoint missing type validation |

**All other ID parameters are consistent** ✅

**Root Cause:**
Likely missing FastAPI `Path()` parameter annotation:
```python
# ❌ Bad (generates "unknown" type)
async def get_dataset(dataset_id):
    ...

# ✅ Good (generates "string" type with validation)
from fastapi import Path
async def get_dataset(dataset_id: str = Path(..., description="Dataset UUID")):
    ...
```

**Recommendation:**
1. Search for path parameters without type hints or Path() annotation
2. Add explicit type hints and Path() validators
3. Consider adding UUID format validation:
```python
from pydantic import UUID4
async def get_dataset(dataset_id: UUID4 = Path(...)):
    ...
```

---

## 5. RESPONSE SCHEMA COMPLETENESS

### 🟡 Issue: 37 Success Responses Missing Schemas

**Affected Endpoints:**
```
POST /api/v1/discovery/discover (200) - No response schema
DELETE /api/v1/discovery/models/{model_id} (200) - No response schema
DELETE /api/v1/conformance/results/{result_id} (200) - No response schema
GET /api/v1/conformance/methods (200) - No response schema
POST /api/v1/conformance/import-model (200) - No response schema
... and 32 more
```

**Impact:**
- Auto-generated TypeScript SDK may have `unknown` types
- API consumers don't know response structure
- No validation of response data

**Recommendation:**
1. Add explicit `response_model` to all endpoints
2. For DELETE operations returning 204, use `status.HTTP_204_NO_CONTENT` and `response_model=None`
3. For operations returning success messages, create a standard schema:

```python
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: dict | None = None

@router.delete("/{model_id}", response_model=SuccessResponse)
async def delete_model(model_id: str):
    ...
    return SuccessResponse(message="Model deleted successfully")
```

---

## 6. HTTP STATUS CODE USAGE

### ✅ Good: Appropriate Status Code Distribution

```
200 (OK):           171 endpoints - Standard success responses
201 (Created):        6 endpoints - POST creating resources
202 (Accepted):       6 endpoints - Async operations
204 (No Content):     8 endpoints - DELETE operations
400 (Bad Request):    8 endpoints - Validation errors
404 (Not Found):     11 endpoints - Resource not found
413 (Payload Large):  1 endpoint  - File upload size limit
422 (Validation):   166 endpoints - Pydantic validation errors
429 (Rate Limit):     1 endpoint  - Rate limiting
```

**Observations:**
- ✅ Correct use of 201 for resource creation
- ✅ Correct use of 202 for async operations (Celery jobs)
- ✅ Correct use of 204 for deletes
- ⚠️  Only 1 endpoint documents rate limiting (429) - likely more should

---

## 7. API ORGANIZATION

### ✅ Excellent: Well-Organized with 27 Tags

**Top API Groups:**
```
Datasets (16)                    - Event log management
Conformance (14)                 - Conformance checking
Object-Centric Process Mining (14) - OCPM/OCEL support
Auth (13)                        - Authentication
Organizations (11)               - Multi-tenant management
Workspaces (11)                  - Collaboration contexts
Workflows (11)                   - Workflow/DAG orchestration
Projects (9)                     - Project management
Analytics (8)                    - Performance analytics
DAGs (8)                         - DAG definitions
Health (6)                       - Health checks
```

**✅ All 157 endpoints are properly tagged** - No untagged endpoints

---

## 8. FILE UPLOAD ENDPOINTS

### ✅ Good: 2 File Upload Endpoints Identified

```
POST /api/v1/datasets/              - Standard event log upload (CSV/XES)
POST /api/v1/ocpm/upload            - OCEL upload (JSON/XML)
```

**Security Considerations:**
- ✅ Max file size limit (413 response documented)
- ⚠️  Verify: File type validation (CSV/XES/JSON/XML only)
- ⚠️  Verify: Virus scanning integration
- ⚠️  Verify: Temp file cleanup on errors
- ⚠️  Verify: Rate limiting on upload endpoints

**Recommendation:**
Document in OpenAPI spec:
- Maximum file sizes
- Allowed MIME types
- Upload rate limits

---

## 9. RATE LIMITING

### 🟡 Issue: Minimal Rate Limiting Documentation

**Finding:** Only 3 endpoints document rate limiting:
```
POST /api/v1/datasets/presign
POST /api/v1/simulation/models/{model_id}/play-out
GET /api/v1/business/p2p/audit-report/{dataset_id}/{reference_model_id}
```

**Expected Rate Limits (from code patterns):**
- Upload endpoints: 10 req/min
- Standard endpoints: 100 req/min
- Health checks: No limit

**Recommendation:**
1. Document rate limits in OpenAPI spec for all endpoints:
```python
@router.post(
    "/datasets/",
    description="Upload event log. **Rate Limit:** 10 requests/minute",
    responses={
        429: {"description": "Rate limit exceeded. Retry after X seconds."}
    }
)
```

2. Ensure all endpoints return proper 429 responses with Retry-After header

---

## 10. DEPRECATION & MIGRATION

### ✅ Good: No Deprecated Endpoints

**Finding:** No endpoints marked as deprecated in OpenAPI spec

**Note Found in Code:**
```python
# src/api/routers/workflows.py:137
# NOTE: These endpoints have been deprecated in favor of the unified
```

**Recommendation:**
- Verify if there are actually deprecated endpoints that should be marked
- If so, add `deprecated=True` to route decorator
- Document migration path in description

---

## 11. HEALTH & MONITORING ENDPOINTS

### ✅ Good: Kubernetes-Ready Health Checks

```
GET /health                - General health check
GET /health/live          - Liveness probe (k8s)
GET /health/ready         - Readiness probe (k8s)
GET /health/startup       - Startup probe (k8s)
GET /health/detailed      - Detailed health with dependencies
```

**Recommendation:**
- Health endpoints correctly don't require authentication ✅
- Consider adding `/metrics` endpoint for Prometheus scraping

---

## Priority Action Items

### 🔴 HIGH Priority (Pre-MVP Release)

1. **Remove OAuth Endpoints** (Estimated: 1 hour)
   - Remove 4 OAuth endpoints
   - Update frontend auth flows
   - Test email/password auth thoroughly

2. **Secure Dev Endpoints** (Estimated: 2 hours)
   - Add environment check to disable in production
   - Add admin-only authentication
   - Remove or heavily restrict `/dev/data/*` endpoints

3. **Fix Parameter Type Inconsistencies** (Estimated: 3 hours)
   - Add Path() annotations to 8 inconsistent ID parameters
   - Add UUID validation where appropriate

### 🟡 MEDIUM Priority (Post-MVP, Pre-GA)

4. **Standardize Error Responses** (Estimated: 8 hours)
   - Create ErrorResponse schema
   - Add to top 50 most-used endpoints
   - Update exception handlers to match schema

5. **Add Missing Response Schemas** (Estimated: 6 hours)
   - Add response_model to 37 endpoints missing schemas
   - Update TypeScript SDK generation

6. **Document Rate Limiting** (Estimated: 2 hours)
   - Add rate limit documentation to all endpoints
   - Ensure 429 responses are properly handled

### 🟢 LOW Priority (Future Enhancement)

7. **Add Security Declarations** (Estimated: 1 hour)
   - Update dependency injection to use Security()
   - Verify OpenAPI spec shows auth requirements

8. **Enhance Health Checks** (Estimated: 3 hours)
   - Add Prometheus metrics endpoint
   - Add detailed dependency health checks

---

## Files Requiring Modification

### Backend

```
HIGH PRIORITY:
- src/platform/users/api/auth.py          - Remove OAuth routes
- src/api/main.py                         - Conditional dev routes
- src/platform/devtools/router.py         - Add admin auth

MEDIUM PRIORITY:
- src/platform/schemas/errors.py          - CREATE: Standard error schema
- src/features/process_mining/api/*.py    - Add error response models
- src/platform/users/api/*.py             - Add error response models
- src/api/dependencies.py                 - Update security declaration

LOW PRIORITY:
- src/platform/health/router.py           - Add /metrics endpoint
```

### Frontend

```
HIGH PRIORITY:
- frontend-new/src/domains/auth/*         - Remove OAuth components
- frontend-new/src/api/sdk.ts             - Regenerate after API changes
```

---

## Testing Checklist

Before MVP release, verify:

- [ ] OAuth endpoints return 404
- [ ] Dev endpoints disabled in production mode
- [ ] All ID parameters properly validated (reject non-UUID values)
- [ ] File upload size limits enforced
- [ ] Rate limiting returns 429 with Retry-After header
- [ ] Error responses follow consistent schema
- [ ] Health checks respond within 1 second
- [ ] Authentication required on all non-public endpoints
- [ ] CORS properly configured for production domains
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (response sanitization)

---

## Conclusion

The API is **well-structured and production-ready** with minor improvements needed:

**Strengths:**
- Comprehensive documentation
- Excellent code organization (domain-driven design)
- Good logging and error handling in implementation
- Proper authentication infrastructure
- Kubernetes-ready health checks

**Pre-MVP Must-Fix:**
- Remove OAuth endpoints (security + simplicity)
- Secure dev/debug endpoints (security)
- Fix parameter type inconsistencies (validation)

**Post-MVP Improvements:**
- Standardize error response documentation
- Complete response schema coverage
- Enhanced rate limiting documentation

**Estimated Total Effort:**
- High Priority: 6 hours
- Medium Priority: 16 hours
- Low Priority: 4 hours
- **Total: ~26 hours** (3-4 days for one developer)

The platform demonstrates strong engineering practices and is on track for a successful MVP release after addressing the high-priority action items.
