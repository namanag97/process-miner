# AI Testing Playbook

**Purpose:** This document enables any AI agent to autonomously test, identify issues, and fix the Process Mining platform until it meets MVP specifications.

**How to Use:** Follow sections in order. Check boxes as you complete them. When you find a bug, fix it immediately before moving on.

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Quick Health Check](#2-quick-health-check)
3. [Automated Test Suites](#3-automated-test-suites)
4. [Manual Feature Testing](#4-manual-feature-testing)
5. [API Contract Testing](#5-api-contract-testing)
6. [Frontend Testing](#6-frontend-testing)
7. [E2E User Journey Testing](#7-e2e-user-journey-testing)
8. [Bug Triage & Fix Protocol](#8-bug-triage--fix-protocol)
9. [MVP Completion Checklist](#9-mvp-completion-checklist)
10. [Common Issues & Fixes](#10-common-issues--fixes)

---

## 1. Environment Setup

### 1.1 Prerequisites Check

Run these commands to verify the environment is ready:

```bash
# Check Python version (need 3.10+)
cd /Users/namanagarwal/system/backend
.venv/bin/python --version

# Check Node version (need 18+)
node --version

# Check if backend venv exists
ls -la /Users/namanagarwal/system/backend/.venv/bin/python

# Check if frontend node_modules exists
ls -d /Users/namanagarwal/system/frontend-new/node_modules
```

**If missing, run:**
```bash
# Backend setup
cd /Users/namanagarwal/system/backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/alembic upgrade head

# Frontend setup
cd /Users/namanagarwal/system/frontend-new
npm install
```

### 1.2 Start Servers

**Terminal 1 - Backend:**
```bash
cd /Users/namanagarwal/system/backend/src
../.venv/bin/python -m uvicorn api.main:app --reload --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd /Users/namanagarwal/system/frontend-new
npm run start
```

### 1.3 Verify Servers Running

```bash
# Backend health check
curl -s http://localhost:8001/health/live | jq .

# Expected: {"status": "healthy", ...}

# Frontend check
curl -s -o /dev/null -w "%{http_code}" http://localhost:4200

# Expected: 200
```

---

## 2. Quick Health Check

Run this first to catch obvious issues:

```bash
cd /Users/namanagarwal/system/backend

# 1. Linting (should pass with no errors)
.venv/bin/python -m ruff check src/ --fix

# 2. Type checking (may have warnings, no errors)
.venv/bin/python -m mypy src/ --ignore-missing-imports

# 3. Security scan
.venv/bin/python -m bandit -r src/ -ll

# 4. Import architecture check
.venv/bin/lint-imports
```

**Success Criteria:**
- [ ] Ruff: 0 errors
- [ ] mypy: 0 errors (warnings OK)
- [ ] Bandit: 0 high/medium severity issues
- [ ] lint-imports: All contracts passed

---

## 3. Automated Test Suites

### 3.1 Backend Unit Tests

```bash
cd /Users/namanagarwal/system/backend

# Run all tests
.venv/bin/python -m pytest tests/ -v --tb=short

# Run with coverage
.venv/bin/python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test categories
.venv/bin/python -m pytest tests/unit/ -v          # Unit tests only
.venv/bin/python -m pytest tests/api/ -v           # API tests only
.venv/bin/python -m pytest tests/integration/ -v   # Integration tests
.venv/bin/python -m pytest tests/e2e/ -v           # E2E tests
```

**Interpret Results:**
- `PASSED` - Test working correctly
- `FAILED` - Bug found, needs fixing
- `ERROR` - Test setup issue, fix test or code
- `SKIPPED` - Intentionally skipped (OK)
- `XFAIL` - Expected failure (OK)

### 3.2 Frontend Tests

```bash
cd /Users/namanagarwal/system/frontend-new

# Run all tests
npm run test

# Run with coverage
npm run test -- --coverage

# Run specific test file
npm run test -- --testPathPattern=userStore
```

### 3.3 Record Test Results

After running tests, document:

```
## Test Run: [DATE]

### Backend Tests
- Total: X
- Passed: X
- Failed: X
- Errors: X

### Failed Tests:
1. test_file.py::test_name - Error message
2. ...

### Frontend Tests
- Total: X
- Passed: X
- Failed: X
```

---

## 4. Manual Feature Testing

Test each feature manually by calling APIs. Use this systematic approach.

### 4.1 Authentication Flow

```bash
BASE_URL="http://localhost:8001/api/v1"

# 1. Register new user
curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }' | jq .

# Expected: 201 with user object

# 2. Login
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"

# 3. Get current user
curl -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected: 200 with user details
```

**Checklist:**
- [ ] Registration creates user
- [ ] Login returns valid JWT
- [ ] /me returns user info with valid token
- [ ] Invalid credentials return 401
- [ ] Expired token returns 401

### 4.2 Project & Workspace Management

```bash
# Using MVP seeded data
ORG_ID="mvp-org-001"
WORKSPACE_ID="mvp-ws-001"
USER_ID="mvp-user-001"

# 1. List workspaces
curl -X GET "$BASE_URL/workspaces/" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 2. List projects in workspace
curl -X GET "$BASE_URL/projects/?workspace_id=$WORKSPACE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Create project
PROJECT_ID=$(curl -s -X POST "$BASE_URL/projects/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test Project $(date +%s)\",
    \"workspace_id\": \"$WORKSPACE_ID\"
  }" | jq -r '.id')

echo "Project ID: $PROJECT_ID"

# 4. Get project details
curl -X GET "$BASE_URL/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

**Checklist:**
- [ ] Can list workspaces
- [ ] Can list projects
- [ ] Can create project
- [ ] Can get project by ID
- [ ] Can update project
- [ ] Can delete project

### 4.3 Dataset Upload & Ingestion

```bash
# 1. Upload CSV file
DATASET_ID=$(curl -s -X POST "$BASE_URL/datasets/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/Users/namanagarwal/system/backend/tests/data/insurance_small.csv" \
  -F "name=Test Dataset" \
  -F "project_id=$PROJECT_ID" | jq -r '.id')

echo "Dataset ID: $DATASET_ID"

# 2. Check dataset status
curl -X GET "$BASE_URL/datasets/$DATASET_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.status'

# Expected: "uploaded" or "pending"

# 3. Get detected columns
curl -X GET "$BASE_URL/datasets/$DATASET_ID/columns" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 4. Submit column mapping
curl -X POST "$BASE_URL/datasets/$DATASET_ID/mapping" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id_column": "case_id",
    "activity_column": "activity",
    "timestamp_column": "timestamp"
  }' | jq .

# 5. Trigger ingestion
curl -X POST "$BASE_URL/datasets/$DATASET_ID/ingest" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 6. Poll status until READY
for i in {1..30}; do
  STATUS=$(curl -s -X GET "$BASE_URL/datasets/$DATASET_ID" \
    -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "ready" ]; then
    echo "Dataset ready!"
    break
  fi
  sleep 2
done
```

**Checklist:**
- [ ] CSV upload works
- [ ] XES upload works
- [ ] Column detection returns columns
- [ ] Column mapping saves correctly
- [ ] Ingestion completes to READY status
- [ ] Dataset metadata (case count, event count) populated

### 4.4 Process Discovery

```bash
# Use a dataset that's in READY status
# DATASET_ID should be set from previous step or use seeded data

# 1. List available miners
curl -X GET "$BASE_URL/discovery/miners" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | .name'

# 2. Discover DFG
curl -X POST "$BASE_URL/discovery/discover" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dataset_id\": \"$DATASET_ID\",
    \"algorithm\": \"dfg_frequency\"
  }" | jq .

# 3. Discover with Inductive Miner
curl -X POST "$BASE_URL/discovery/discover" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dataset_id\": \"$DATASET_ID\",
    \"algorithm\": \"inductive\",
    \"parameters\": {
      \"noise_threshold\": 0.2
    }
  }" | jq .

# 4. Get Petri Net visualization
curl -X POST "$BASE_URL/visualization/petri-net" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dataset_id\": \"$DATASET_ID\"
  }" | jq '.svg' | head -c 500
```

**Checklist:**
- [ ] DFG discovery works
- [ ] Inductive Miner works
- [ ] Heuristics Miner works
- [ ] Alpha Miner works
- [ ] Petri Net visualization returns SVG
- [ ] Process Tree conversion works
- [ ] BPMN generation works

### 4.5 Analytics

```bash
# 1. Bottleneck analysis
curl -X GET "$BASE_URL/analytics/$DATASET_ID/bottlenecks" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 2. Rework analysis
curl -X GET "$BASE_URL/analytics/$DATASET_ID/rework" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Variant analysis
curl -X GET "$BASE_URL/analytics/$DATASET_ID/variants" \
  -H "Authorization: Bearer $TOKEN" | jq '.variants[:3]'

# 4. Service times
curl -X GET "$BASE_URL/analytics/$DATASET_ID/service-times" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 5. Cycle times
curl -X GET "$BASE_URL/analytics/$DATASET_ID/cycle-times" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 6. Throughput
curl -X GET "$BASE_URL/analytics/$DATASET_ID/throughput" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

**Checklist:**
- [ ] Bottleneck detection returns results
- [ ] Rework detection works
- [ ] Variant extraction works
- [ ] Service time calculation works
- [ ] Cycle time calculation works
- [ ] Throughput metrics work

### 4.6 Conformance Checking

```bash
# 1. Basic conformance check
curl -X POST "$BASE_URL/conformance/check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dataset_id\": \"$DATASET_ID\"
  }" | jq .

# 2. Fitness calculation
curl -X POST "$BASE_URL/conformance/fitness" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dataset_id\": \"$DATASET_ID\"
  }" | jq .

# 3. Precision calculation
curl -X POST "$BASE_URL/conformance/precision" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"dataset_id\": \"$DATASET_ID\"
  }" | jq .
```

**Checklist:**
- [ ] Token replay conformance works
- [ ] Fitness score returned (0-1)
- [ ] Precision score returned (0-1)
- [ ] Alignment-based conformance works
- [ ] Diagnostics show deviating cases

---

## 5. API Contract Testing

### 5.1 Validate OpenAPI Spec

```bash
# Get OpenAPI spec
curl -s http://localhost:8001/openapi.json > /tmp/openapi.json

# Check it's valid JSON
jq . /tmp/openapi.json > /dev/null && echo "Valid JSON"

# Count endpoints
jq '.paths | keys | length' /tmp/openapi.json
```

### 5.2 Check Response Schemas

For each endpoint, verify:
1. Response matches documented schema
2. Error responses follow RFC 7807 format
3. All required fields present

```bash
# Example: Check error format
curl -s -X GET "$BASE_URL/datasets/nonexistent-id" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Should return:
# {
#   "type": "...",
#   "title": "...",
#   "status": 404,
#   "detail": "...",
#   "instance": "..."
# }
```

### 5.3 Automated API Discovery Test

```bash
cd /Users/namanagarwal/system/backend
.venv/bin/python tests/e2e/e2e_api_tester.py
```

This script:
- Fetches OpenAPI spec
- Tests each endpoint
- Reports failures and errors

---

## 6. Frontend Testing

### 6.1 Component Rendering

Start the frontend and manually verify each page loads:

| Page | URL | Check |
|------|-----|-------|
| Login | http://localhost:4200/login | [ ] Renders login form |
| Workspace | http://localhost:4200/workspace | [ ] Shows project list |
| Upload Wizard | http://localhost:4200/workspace/{id}/upload | [ ] Multi-step wizard works |
| Explorer | http://localhost:4200/workspace/{id}/data/{id}/explorer | [ ] Graph renders |
| Discovery | http://localhost:4200/workspace/{id}/data/{id}/discovery | [ ] Algorithm selector works |
| Analytics | http://localhost:4200/workspace/{id}/data/{id}/analytics | [ ] Charts render |
| KPI | http://localhost:4200/workspace/{id}/data/{id}/kpi | [ ] Metrics display |

### 6.2 Console Error Check

Open browser DevTools (F12) and check for:
- [ ] No JavaScript errors in console
- [ ] No failed network requests (4xx/5xx)
- [ ] No React warnings about keys, hooks, etc.

### 6.3 Responsive Design

Test at these breakpoints:
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)

---

## 7. E2E User Journey Testing

### 7.1 Happy Path: First-Time User

Test the complete flow a new user would experience:

```bash
# Run the comprehensive user journey test
cd /Users/namanagarwal/system/backend
bash scripts/test_user_journeys.sh
```

**Manual Steps:**
1. [ ] Open http://localhost:4200
2. [ ] Click "Get Started" or "Login"
3. [ ] Register with new email
4. [ ] See welcome/onboarding
5. [ ] Create new project
6. [ ] Upload CSV file
7. [ ] Map columns
8. [ ] Wait for ingestion
9. [ ] View process map
10. [ ] Click on bottlenecks
11. [ ] View variants
12. [ ] Export/save results

### 7.2 Error Scenarios

Test error handling:

```bash
# 1. Upload invalid file
curl -X POST "$BASE_URL/datasets/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/etc/hosts" \
  -F "name=Invalid" \
  -F "project_id=$PROJECT_ID"

# Expected: 400 or 422 with clear error message

# 2. Access without auth
curl -X GET "$BASE_URL/datasets/"

# Expected: 401 Unauthorized

# 3. Access other user's data
curl -X GET "$BASE_URL/datasets/other-user-dataset-id" \
  -H "Authorization: Bearer $TOKEN"

# Expected: 403 or 404

# 4. Invalid parameters
curl -X POST "$BASE_URL/discovery/discover" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": "invalid", "algorithm": "nonexistent"}'

# Expected: 400 or 422 with validation error
```

**Checklist:**
- [ ] Invalid file upload shows helpful error
- [ ] Unauthenticated requests return 401
- [ ] Unauthorized access returns 403/404
- [ ] Invalid parameters return 422 with field errors
- [ ] Server errors (500) are rare and logged

---

## 8. Bug Triage & Fix Protocol

### 8.1 When You Find a Bug

1. **Document it:**
```markdown
## Bug: [Short description]

**Severity:** P0/P1/P2/P3
**Location:** [file:line]
**Steps to reproduce:**
1. ...
2. ...

**Expected:** ...
**Actual:** ...
**Error message:** ...
```

2. **Severity Guide:**
   - **P0 (Critical):** App crashes, data loss, security issue
   - **P1 (High):** Feature broken, blocking user
   - **P2 (Medium):** Feature partially broken, workaround exists
   - **P3 (Low):** Cosmetic, minor inconvenience

3. **Fix immediately if P0/P1, note for later if P2/P3**

### 8.2 Fix Protocol

```bash
# 1. Create a branch (optional for small fixes)
git checkout -b fix/bug-description

# 2. Write a failing test first
# Add test to tests/api/test_xxx.py or tests/unit/xxx.py

# 3. Fix the bug
# Edit the source file

# 4. Run tests to verify
.venv/bin/python -m pytest tests/path/to/test.py -v

# 5. Run full test suite
.venv/bin/python -m pytest tests/ -v

# 6. Commit
git add .
git commit -m "fix: [description]

- What was wrong
- How it was fixed
- Test added

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 8.3 Common Fix Patterns

**Missing import:**
```python
# Error: NameError: name 'X' is not defined
# Fix: Add import at top of file
from module import X
```

**Async/await issue:**
```python
# Error: coroutine was never awaited
# Fix: Add await
result = await async_function()
```

**Type error:**
```python
# Error: expected str, got int
# Fix: Convert type
value = str(int_value)
```

**Database session issue:**
```python
# Error: Session closed
# Fix: Ensure session passed correctly
async def func(db: AsyncSession):
    # use db here
```

---

## 9. MVP Completion Checklist

Use this as the final verification before declaring MVP complete.

### 9.1 Core Features (Must Pass)

**Data Ingestion:**
- [ ] CSV upload (< 100MB)
- [ ] Column auto-detection
- [ ] Column mapping wizard
- [ ] Ingestion to READY status
- [ ] Error handling for bad files

**Process Discovery:**
- [ ] DFG generation
- [ ] Inductive Miner
- [ ] Petri Net visualization
- [ ] Interactive graph (zoom, pan)

**Analytics:**
- [ ] Bottleneck detection
- [ ] Variant analysis
- [ ] Basic statistics (cases, events, duration)

**Platform:**
- [ ] User registration
- [ ] User login
- [ ] Project creation
- [ ] Multi-user workspaces

### 9.2 Quality Gates (Must Pass)

**Tests:**
- [ ] All backend tests pass
- [ ] All frontend tests pass
- [ ] No P0/P1 bugs open

**Code Quality:**
- [ ] Ruff linting passes
- [ ] mypy type check passes
- [ ] Bandit security scan clean
- [ ] import-linter passes

**Performance:**
- [ ] Page load < 3 seconds
- [ ] Discovery < 30 seconds (100K events)
- [ ] No memory leaks in 1-hour session

**Security:**
- [ ] No OAuth endpoints exposed
- [ ] Dev endpoints protected
- [ ] Rate limiting enabled
- [ ] CORS configured correctly

### 9.3 Documentation (Should Have)

- [ ] API documented in OpenAPI
- [ ] README updated
- [ ] CLAUDE.md current
- [ ] Error messages helpful

---

## 10. Common Issues & Fixes

### 10.1 Backend Won't Start

**Symptom:** `ModuleNotFoundError`
```bash
# Fix: Reinstall dependencies
cd /Users/namanagarwal/system/backend
.venv/bin/pip install -e ".[dev]"
```

**Symptom:** `Database error`
```bash
# Fix: Run migrations
cd /Users/namanagarwal/system/backend
.venv/bin/alembic upgrade head
```

**Symptom:** Port already in use
```bash
# Fix: Kill existing process
lsof -ti:8001 | xargs kill -9
```

### 10.2 Frontend Won't Start

**Symptom:** `ENOENT node_modules`
```bash
cd /Users/namanagarwal/system/frontend-new
npm install
```

**Symptom:** Build errors
```bash
# Fix: Clear cache and rebuild
rm -rf node_modules/.cache
npm run start
```

### 10.3 Tests Failing

**Symptom:** Database fixture errors
```bash
# Fix: Check conftest.py fixtures are correct
# Ensure async session handling
```

**Symptom:** Import errors in tests
```bash
# Fix: Run from correct directory
cd /Users/namanagarwal/system/backend
.venv/bin/python -m pytest tests/ -v
```

### 10.4 CORS Errors

**Symptom:** Frontend can't reach backend
```python
# Fix: Check CORS in api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 10.5 Authentication Issues

**Symptom:** 401 on all requests
```bash
# Fix: Check token format
# Header should be: Authorization: Bearer <token>
# Not: Authorization: <token>
```

**Symptom:** Token expired
```bash
# Fix: Refresh token or re-login
curl -X POST "$BASE_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "..."}'
```

---

## Appendix A: Quick Reference Commands

```bash
# === SETUP ===
cd /Users/namanagarwal/system/backend && .venv/bin/pip install -e ".[dev]"
cd /Users/namanagarwal/system/frontend-new && npm install

# === START SERVERS ===
cd /Users/namanagarwal/system/backend/src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001
cd /Users/namanagarwal/system/frontend-new && npm run start

# === RUN TESTS ===
cd /Users/namanagarwal/system/backend && .venv/bin/python -m pytest tests/ -v
cd /Users/namanagarwal/system/frontend-new && npm run test

# === CODE QUALITY ===
cd /Users/namanagarwal/system/backend && .venv/bin/python -m ruff check src/ --fix
cd /Users/namanagarwal/system/backend && .venv/bin/python -m mypy src/
cd /Users/namanagarwal/system/backend && .venv/bin/lint-imports

# === HEALTH CHECK ===
curl http://localhost:8001/health/live
curl http://localhost:8001/health/ready

# === DATABASE ===
cd /Users/namanagarwal/system/backend && .venv/bin/alembic upgrade head
cd /Users/namanagarwal/system/backend && .venv/bin/alembic current
```

---

## Appendix B: Test Data Locations

```
/Users/namanagarwal/system/backend/tests/data/
├── insurance_small.csv      # Small test dataset (~100 cases)
├── insurance_medium.csv     # Medium test dataset (~1000 cases)
├── bottleneck_cases.csv     # Dataset with obvious bottlenecks
├── rework_cases.csv         # Dataset with rework patterns
└── order_management_*.jsonocel  # OCEL 2.0 test data
```

---

## Appendix C: Success Criteria Summary

**MVP is COMPLETE when:**

1. ✅ All Tier 0 features working (see MVP_TARGET_SPECIFICATION.md)
2. ✅ All automated tests passing
3. ✅ No P0/P1 bugs
4. ✅ Code quality gates passing
5. ✅ Full user journey works end-to-end
6. ✅ Security checklist complete

**Estimated time for AI agent to verify:** 2-4 hours of autonomous testing

---

*This playbook should be updated as new features are added or issues discovered.*
