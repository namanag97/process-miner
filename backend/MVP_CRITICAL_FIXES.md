# MVP Critical Fixes - Implementation Guide

**Target:** Production-Ready MVP Release
**Estimated Time:** 6 hours
**Priority:** CRITICAL - Must complete before deployment

---

## Fix #1: Remove OAuth/Social Auth Endpoints (2 hours)

### Why This is Critical
- **Security:** OAuth increases attack surface unnecessarily for MVP
- **Simplicity:** Email/password auth is sufficient for initial release
- **Dependencies:** Remove unused OAuth client libraries
- **Maintenance:** Fewer endpoints to secure and monitor

### Files to Modify

#### 1. Remove OAuth Routes from Auth Router

**File:** `backend/src/platform/users/api/auth.py`

**Remove these route handlers (search and delete):**
```python
@router.get("/oauth/google")
async def oauth_google():
    ...

@router.get("/oauth/google/callback")
async def oauth_google_callback():
    ...

@router.get("/oauth/github")
async def oauth_github():
    ...

@router.get("/oauth/github/callback")
async def oauth_github_callback():
    ...
```

**Location:** Lines ~350-450 (approximate, search for "oauth" in the file)

#### 2. Remove OAuth Configuration

**File:** `backend/src/platform/core/config.py`

**Remove these settings:**
```python
# OAuth Settings
GOOGLE_CLIENT_ID: str | None = None
GOOGLE_CLIENT_SECRET: str | None = None
GITHUB_CLIENT_ID: str | None = None
GITHUB_CLIENT_SECRET: str | None = None
```

#### 3. Update Frontend (Remove OAuth UI)

**Files to check:**
```bash
# Find OAuth-related components
cd frontend-new
grep -r "oauth" src/domains/auth/
grep -r "Sign in with Google" src/
grep -r "Sign in with GitHub" src/
```

**Remove:**
- OAuth login buttons from login page
- OAuth callback handling routes
- OAuth-related constants/configs

### Testing
```bash
# 1. Verify OAuth endpoints return 404
curl http://localhost:8001/api/v1/auth/oauth/google
# Expected: 404 Not Found

# 2. Verify email/password auth still works
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "analyst@example.com", "password": "test123"}'
# Expected: 200 with access_token

# 3. Regenerate OpenAPI spec
curl http://localhost:8001/openapi.json > openapi_new.json
# Verify oauth endpoints are gone
grep -c "oauth" openapi_new.json  # Should be 0
```

---

## Fix #2: Secure Dev/Debug Endpoints (2 hours)

### Why This is Critical
- **Security:** `/dev/data/*` endpoints expose direct DB access
- **Production Safety:** Debug endpoints should NEVER be in production
- **Data Leakage:** Potential for sensitive data exposure

### Current Vulnerable Endpoints
```
POST   /api/v1/dev/log                          - Frontend log submission
GET    /api/v1/dev/logs                         - Query logs
GET    /api/v1/dev/logs/stream                  - SSE log streaming
GET    /api/v1/dev/logs/metrics                 - Log metrics
GET    /api/v1/dev/logs/recent                  - Recent logs
DELETE /api/v1/dev/logs/clear                   - Clear logs
GET    /api/v1/dev/data/tables                  - ⚠️ CRITICAL: Direct DB access
GET    /api/v1/dev/data/records/{table}         - ⚠️ CRITICAL: Query any table
GET    /api/v1/dev/data/record/{table}/{id}     - ⚠️ CRITICAL: Get any record
```

### Implementation

#### 1. Conditional Router Registration

**File:** `backend/src/api/main.py`

**Find the router registration section (~line 270-340):**
```python
# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(organizations_router, prefix="/api/v1")
# ... other routers ...
app.include_router(dev_log_router, prefix="/api/v1")  # ← FIND THIS
app.include_router(dev_data_router, prefix="/api/v1")  # ← AND THIS
app.include_router(dev_logs_stream_router, prefix="/api/v1")  # ← AND THIS
```

**Replace with:**
```python
# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(organizations_router, prefix="/api/v1")
# ... other routers ...

# Dev/Debug endpoints - ONLY in development/staging
if settings.ENVIRONMENT in ["development", "staging"]:
    logger.warning(
        "dev_endpoints_enabled",
        environment=settings.ENVIRONMENT,
        message="Dev/debug endpoints are ENABLED. Disable in production!",
    )
    app.include_router(dev_log_router, prefix="/api/v1")
    app.include_router(dev_data_router, prefix="/api/v1")
    app.include_router(dev_logs_stream_router, prefix="/api/v1")
else:
    logger.info(
        "dev_endpoints_disabled",
        environment=settings.ENVIRONMENT,
        message="Dev/debug endpoints are disabled for production safety.",
    )
```

#### 2. Add Environment Variable

**File:** `backend/.env`

**Add:**
```bash
# Environment: development, staging, production
ENVIRONMENT=development
```

**File:** `backend/.env.production` (create this)

```bash
# Production environment configuration
ENVIRONMENT=production
```

#### 3. Update Config Validation

**File:** `backend/src/platform/core/config.py`

**Add to Settings class:**
```python
from typing import Literal

class Settings(BaseSettings):
    # ... existing fields ...

    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # ... rest of settings ...

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be development, staging, or production")
        return v
```

### Testing

```bash
# 1. Test with ENVIRONMENT=development (should work)
export ENVIRONMENT=development
cd backend/src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

curl http://localhost:8001/api/v1/dev/data/tables
# Expected: 200 OK with table list

# 2. Test with ENVIRONMENT=production (should fail)
export ENVIRONMENT=production
cd backend/src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001

curl http://localhost:8001/api/v1/dev/data/tables
# Expected: 404 Not Found

# 3. Check startup logs
# Should see: "dev_endpoints_disabled" in production mode
# Should see: "dev_endpoints_enabled" (with WARNING) in dev mode
```

---

## Fix #3: Fix Parameter Type Validation (2 hours)

### Why This is Critical
- **API Consistency:** All ID parameters should have proper type validation
- **Security:** Prevents injection attacks through malformed IDs
- **Error Messages:** Better validation errors for clients
- **OpenAPI Spec:** Generates correct TypeScript types

### Affected Parameters

| Parameter | Issue | Endpoints Affected |
|-----------|-------|-------------------|
| `dataset_id` | 3 endpoints missing type | 67 total uses |
| `model_id` | 1 endpoint missing type | 18 total uses |
| `org_id` | 1 endpoint missing type | 11 total uses |
| `project_id` | 1 endpoint missing type | 11 total uses |
| `user_id` | 1 endpoint missing type | 6 total uses |
| `workspace_id` | 1 endpoint missing type | 11 total uses |
| `definition_id` | 1 endpoint missing type | 2 total uses |

### Implementation Strategy

#### 1. Find Endpoints with Missing Types

**Run this command to find all affected files:**
```bash
cd backend/src

# Find dataset_id parameters without Path() annotation
grep -rn "dataset_id" --include="*.py" | grep "async def" | grep -v "Path("

# Repeat for other parameters
grep -rn "model_id" --include="*.py" | grep "async def" | grep -v "Path("
grep -rn "org_id" --include="*.py" | grep "async def" | grep -v "Path("
# etc.
```

#### 2. Fix Pattern - Before and After

**❌ BEFORE (Bad - No type validation):**
```python
@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id, db: DBSession):
    # dataset_id has no type, no validation
    ...
```

**✅ AFTER (Good - Proper validation):**
```python
from fastapi import Path

@router.get("/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: str = Path(..., description="Dataset UUID", min_length=36, max_length=36),
    db: DBSession,
):
    # dataset_id is validated as string with length checks
    ...
```

**✅ EVEN BETTER (UUID validation):**
```python
from fastapi import Path
from pydantic import UUID4

@router.get("/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: UUID4 = Path(..., description="Dataset UUID"),
    db: DBSession,
):
    # dataset_id is validated as proper UUID format
    ...
```

#### 3. Systematic Fix Script

**Create:** `backend/fix_param_validation.py`

```python
"""Find and report parameter validation issues."""
import re
from pathlib import Path

# Patterns to find
id_params = [
    'dataset_id', 'model_id', 'org_id', 'project_id',
    'user_id', 'workspace_id', 'definition_id'
]

issues = []

for py_file in Path('src').rglob('*.py'):
    if 'router' in str(py_file) or 'api' in str(py_file):
        content = py_file.read_text()

        for param in id_params:
            # Find function signatures with this parameter
            pattern = rf'async def \w+\([^)]*{param}(?![:\w])'
            matches = re.finditer(pattern, content)

            for match in matches:
                # Check if Path() is used
                sig_start = match.start()
                sig_end = content.find(':', sig_start)
                sig_text = content[sig_start:sig_end + 100]

                if 'Path(' not in sig_text and f'{param}:' not in sig_text:
                    line_num = content[:sig_start].count('\n') + 1
                    issues.append({
                        'file': str(py_file),
                        'line': line_num,
                        'param': param,
                        'signature': sig_text[:80],
                    })

print(f"Found {len(issues)} parameter validation issues:\n")
for issue in issues:
    print(f"{issue['file']}:{issue['line']}")
    print(f"  Parameter: {issue['param']}")
    print(f"  Context: {issue['signature']}")
    print()
```

**Run:**
```bash
cd backend
python fix_param_validation.py
```

#### 4. Manual Fix Each File

For each reported issue:
1. Open the file
2. Find the function signature
3. Add `from fastapi import Path` import
4. Change parameter signature

**Example Fix:**

**File:** `src/features/process_mining/discovery/router.py:45`
```python
# BEFORE
@router.get("/models/{model_id}")
async def get_model(model_id, db: DBSession):
    ...

# AFTER
from fastapi import Path

@router.get("/models/{model_id}")
async def get_model(
    model_id: str = Path(..., description="Process model UUID"),
    db: DBSession,
):
    ...
```

### Testing

```bash
# 1. Regenerate OpenAPI spec
curl http://localhost:8001/openapi.json | python -m json.tool > openapi_fixed.json

# 2. Verify all parameters have types
cd backend
python << 'EOF'
import json
with open('openapi_fixed.json') as f:
    spec = json.load(f)

issues = []
for path, methods in spec['paths'].items():
    for method, details in methods.items():
        params = details.get('parameters', [])
        for param in params:
            if param.get('in') == 'path':
                schema = param.get('schema', {})
                if not schema.get('type'):
                    issues.append(f"{method.upper()} {path} - {param['name']}")

if issues:
    print(f"❌ Still {len(issues)} issues:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("✅ All path parameters have proper types!")
EOF

# 3. Test validation works
curl "http://localhost:8001/api/v1/datasets/not-a-uuid"
# Expected: 422 Validation Error (not 500)
```

---

## Verification Checklist

After completing all fixes:

```bash
# ✅ 1. OAuth endpoints removed
curl http://localhost:8001/api/v1/auth/oauth/google
# Expected: 404

# ✅ 2. Dev endpoints disabled in production
export ENVIRONMENT=production
# Restart server
curl http://localhost:8001/api/v1/dev/data/tables
# Expected: 404

# ✅ 3. Parameter validation working
curl "http://localhost:8001/api/v1/datasets/invalid-id"
# Expected: 422 (not 500)

# ✅ 4. OpenAPI spec updated
curl http://localhost:8001/openapi.json | python -m json.tool > openapi_final.json
diff openapi_extracted.json openapi_final.json
# Should show:
#   - 4 fewer endpoints (OAuth removed)
#   - 9 fewer endpoints in production mode (dev endpoints)
#   - Consistent parameter types

# ✅ 5. Frontend regenerate SDK
cd frontend-new
npm run generate:sdk
# Should complete without errors

# ✅ 6. Run test suite
cd backend
.venv/bin/python -m pytest tests/ -v
# All tests should pass

# ✅ 7. Check startup logs
cd backend/src
../.venv/bin/python -m uvicorn api.main:app --reload --port 8001
# Look for:
#   ✓ "dev_endpoints_disabled" (in production)
#   ✓ "application_ready"
#   ✓ No OAuth route registration messages
```

---

## Deployment Notes

### Environment Variables for Production

**Set these before deployment:**
```bash
ENVIRONMENT=production              # Critical!
DEBUG=false                         # Disable debug mode
LOG_LEVEL=INFO                      # Not DEBUG in production
```

### Rollback Plan

If issues arise after deployment:

1. **OAuth Removal Rollback:**
   ```bash
   git revert <commit-hash-of-oauth-removal>
   ```

2. **Dev Endpoints Rollback:**
   ```bash
   # Emergency: set ENVIRONMENT=development temporarily
   # Then investigate and fix properly
   ```

3. **Parameter Validation Rollback:**
   ```bash
   git revert <commit-hash-of-param-fixes>
   ```

---

## Post-Deployment Monitoring

**Monitor these for 24 hours after deployment:**

1. **Error Rate:**
   - Should NOT increase after deployment
   - Watch for 422 errors (might increase initially - this is GOOD, means validation working)
   - Watch for 500 errors (should NOT increase)

2. **Auth Success Rate:**
   - Email/password login should have >95% success rate
   - No OAuth-related errors in logs

3. **API Response Times:**
   - Should be unchanged or slightly improved (fewer routes to check)

4. **Log Volume:**
   - Should be similar or lower (no dev endpoint spam)

---

## Success Criteria

### Before Marking Complete

- [ ] All 4 OAuth endpoints return 404
- [ ] All 9 dev endpoints return 404 in production mode
- [ ] All 8 ID parameters have proper type validation
- [ ] OpenAPI spec regenerated and verified
- [ ] Frontend SDK regenerated successfully
- [ ] All backend tests passing
- [ ] Manual smoke test of auth flow completed
- [ ] Manual smoke test of dataset upload completed
- [ ] Production environment variables documented
- [ ] Deployment checklist reviewed with DevOps

### Definition of Done

**The MVP is production-ready when:**
1. Security surface reduced (OAuth removed)
2. Production safety guaranteed (dev endpoints disabled)
3. API consistency improved (parameter validation)
4. All tests passing
5. Documentation updated
6. Team trained on new configuration

**Estimated Timeline:**
- Fix #1 (OAuth removal): 2 hours
- Fix #2 (Dev endpoints): 2 hours
- Fix #3 (Parameter validation): 2 hours
- Testing & Verification: 2 hours
- **Total: 8 hours (1 working day)**

Add 50% buffer for unexpected issues: **12 hours (1.5 days)**

---

**Questions? Issues?**
Contact: Technical Lead / CTO
Priority: CRITICAL - Block MVP deployment until complete
