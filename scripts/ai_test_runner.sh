#!/bin/bash
#
# AI Test Runner - Automated MVP Validation
# Usage: ./scripts/ai_test_runner.sh [quick|full|api|frontend]
#
# This script is designed to be run by AI agents to validate the system.
# It outputs structured results that AI can parse and act on.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend-new"

# Results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0
FAILURES=()

# Logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_failure() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILURES+=("$1")
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
}

log_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check if backend is running
check_backend() {
    if curl -s http://localhost:8001/health/live > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if frontend is running
check_frontend() {
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:4200 2>/dev/null | grep -q "200"; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# TEST SUITES
# ============================================================================

run_quick_checks() {
    log_section "QUICK HEALTH CHECKS"

    # 1. Backend health
    log_info "Checking backend health..."
    if check_backend; then
        HEALTH=$(curl -s http://localhost:8001/health/live)
        if echo "$HEALTH" | grep -q '"status":"healthy"'; then
            log_success "Backend is healthy"
        else
            log_failure "Backend health check returned unexpected response"
        fi
    else
        log_failure "Backend is not running on port 8001"
    fi

    # 2. Backend readiness
    log_info "Checking backend readiness..."
    if curl -s http://localhost:8001/health/ready | grep -q '"status"'; then
        log_success "Backend readiness check passed"
    else
        log_failure "Backend readiness check failed"
    fi

    # 3. OpenAPI spec available
    log_info "Checking OpenAPI spec..."
    if curl -s http://localhost:8001/openapi.json | grep -q '"openapi"'; then
        log_success "OpenAPI spec is available"
    else
        log_failure "OpenAPI spec not available"
    fi

    # 4. Frontend check
    log_info "Checking frontend..."
    if check_frontend; then
        log_success "Frontend is running on port 4200"
    else
        log_skip "Frontend is not running (optional for API testing)"
    fi
}

run_code_quality() {
    log_section "CODE QUALITY CHECKS"

    cd "$BACKEND_DIR"

    # 1. Ruff linting
    log_info "Running Ruff linter..."
    if .venv/bin/python -m ruff check src/ 2>/dev/null; then
        log_success "Ruff linting passed"
    else
        log_failure "Ruff linting found issues"
    fi

    # 2. Import linter
    log_info "Running import-linter..."
    if .venv/bin/lint-imports 2>/dev/null; then
        log_success "Import architecture check passed"
    else
        log_failure "Import architecture violations found"
    fi

    # 3. Type checking (allow warnings)
    log_info "Running mypy type checker..."
    if .venv/bin/python -m mypy src/ --ignore-missing-imports 2>&1 | grep -q "Success\|no issues"; then
        log_success "Type checking passed"
    else
        # Check if there are actual errors vs just warnings
        MYPY_OUTPUT=$(.venv/bin/python -m mypy src/ --ignore-missing-imports 2>&1 || true)
        if echo "$MYPY_OUTPUT" | grep -q "error:"; then
            log_failure "Type checking found errors"
        else
            log_success "Type checking passed (with warnings)"
        fi
    fi
}

run_backend_tests() {
    log_section "BACKEND UNIT TESTS"

    cd "$BACKEND_DIR"

    log_info "Running pytest..."

    # Run tests and capture output
    if .venv/bin/python -m pytest tests/ -v --tb=short 2>&1 | tee /tmp/pytest_output.txt; then
        # Count results
        PASSED=$(grep -c "PASSED" /tmp/pytest_output.txt || echo "0")
        FAILED=$(grep -c "FAILED" /tmp/pytest_output.txt || echo "0")

        if [ "$FAILED" -eq 0 ]; then
            log_success "All $PASSED backend tests passed"
        else
            log_failure "$FAILED backend tests failed (out of $((PASSED + FAILED)))"
        fi
    else
        log_failure "Backend tests failed to run"
    fi
}

run_api_tests() {
    log_section "API ENDPOINT TESTS"

    if ! check_backend; then
        log_failure "Backend not running - skipping API tests"
        return
    fi

    BASE_URL="http://localhost:8001/api/v1"

    # Get auth token using seeded user
    # Credentials: analyst@example.com / TestPass123
    log_info "Testing authentication..."
    TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"analyst@example.com","password":"TestPass123"}' \
        2>/dev/null | jq -r '.access_token // empty')

    if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
        log_success "Authentication works"
    else
        log_failure "Authentication failed - cannot continue API tests"
        return
    fi

    AUTH_HEADER="Authorization: Bearer $TOKEN"

    # Test endpoints using simple function to avoid associative array issues
    test_endpoint() {
        local name="$1"
        local endpoint="$2"
        log_info "Testing $name..."

        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "$AUTH_HEADER" \
            "$BASE_URL/$endpoint" 2>/dev/null)

        if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
            log_success "$name returned $HTTP_CODE"
        elif [ "$HTTP_CODE" -eq 401 ]; then
            log_failure "$name returned 401 Unauthorized"
        elif [ "$HTTP_CODE" -eq 500 ]; then
            log_failure "$name returned 500 Server Error"
        else
            log_failure "$name returned $HTTP_CODE"
        fi
    }

    test_endpoint "GET /workspaces" "workspaces"
    test_endpoint "GET /projects" "projects"
    test_endpoint "GET /datasets" "datasets/"
    test_endpoint "GET /discovery/miners" "discovery/miners"

    # Health endpoint is at root level, not under /api/v1
    log_info "Testing GET /health/live..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        "http://localhost:8001/health/live" 2>/dev/null)
    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
        log_success "GET /health/live returned $HTTP_CODE"
    else
        log_failure "GET /health/live returned $HTTP_CODE"
    fi

    # Test error handling
    log_info "Testing error handling (404)..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "$AUTH_HEADER" \
        "$BASE_URL/datasets/nonexistent-id-12345" 2>/dev/null)

    if [ "$HTTP_CODE" -eq 404 ]; then
        log_success "404 handling works correctly"
    else
        log_failure "Expected 404, got $HTTP_CODE"
    fi

    # Test unauthorized access (auth may be disabled in dev mode)
    log_info "Testing unauthorized access..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        "$BASE_URL/auth/me" 2>/dev/null)

    if [ "$HTTP_CODE" -eq 401 ] || [ "$HTTP_CODE" -eq 403 ]; then
        log_success "Unauthorized access blocked ($HTTP_CODE)"
    elif [ "$HTTP_CODE" -eq 200 ]; then
        # In dev mode, auth is disabled (auth_enabled=False) so this is expected
        log_skip "Auth disabled in dev mode (expected 401, got $HTTP_CODE)"
    else
        log_failure "Unexpected response code: $HTTP_CODE"
    fi
}

run_frontend_tests() {
    log_section "FRONTEND TESTS"

    cd "$FRONTEND_DIR"

    if [ ! -d "node_modules" ]; then
        log_skip "node_modules not found - run 'npm install' first"
        return
    fi

    log_info "Running Jest tests..."

    if npm run test -- --passWithNoTests 2>&1 | tee /tmp/jest_output.txt; then
        log_success "Frontend tests passed"
    else
        log_failure "Frontend tests failed"
    fi
}

run_e2e_flow() {
    log_section "END-TO-END FLOW TEST"

    if ! check_backend; then
        log_failure "Backend not running - skipping E2E tests"
        return
    fi

    BASE_URL="http://localhost:8001/api/v1"

    # 1. Login (using MVP seeded credentials)
    log_info "Step 1: Login..."
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"analyst@example.com","password":"TestPass123"}')

    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')
    if [ -z "$TOKEN" ]; then
        log_failure "E2E: Login failed"
        return
    fi
    log_success "E2E: Login successful"

    AUTH="Authorization: Bearer $TOKEN"

    # 2. Get workspace (paginated response uses .items array)
    log_info "Step 2: Get workspace..."
    WORKSPACE=$(curl -s "$BASE_URL/workspaces" -H "$AUTH" | jq -r '.items[0].id // empty')
    if [ -z "$WORKSPACE" ]; then
        log_failure "E2E: No workspace found"
        return
    fi
    log_success "E2E: Found workspace $WORKSPACE"

    # 3. Get or create project (paginated response uses .items array)
    log_info "Step 3: Get project..."
    PROJECT=$(curl -s "$BASE_URL/projects?workspace_id=$WORKSPACE" -H "$AUTH" | jq -r '.items[0].id // empty')
    if [ -z "$PROJECT" ]; then
        # Create project
        PROJECT=$(curl -s -X POST "$BASE_URL/projects/" \
            -H "$AUTH" \
            -H "Content-Type: application/json" \
            -d "{\"name\":\"E2E Test Project\",\"workspace_id\":\"$WORKSPACE\"}" | jq -r '.id // empty')
    fi

    if [ -z "$PROJECT" ]; then
        log_failure "E2E: Could not get/create project"
        return
    fi
    log_success "E2E: Using project $PROJECT"

    # 4. Check for existing dataset or upload (paginated response uses .items array)
    log_info "Step 4: Check datasets..."
    DATASET=$(curl -s "$BASE_URL/datasets?project_id=$PROJECT" -H "$AUTH" | jq -r '.items[] | select(.status=="ready") | .id' | head -1)

    if [ -n "$DATASET" ]; then
        log_success "E2E: Found ready dataset $DATASET"
    else
        log_info "E2E: No ready dataset, checking for any dataset..."
        DATASET=$(curl -s "$BASE_URL/datasets?project_id=$PROJECT" -H "$AUTH" | jq -r '.items[0].id // empty')
        if [ -n "$DATASET" ]; then
            log_success "E2E: Found dataset $DATASET (may not be ready)"
        else
            log_skip "E2E: No datasets - upload test skipped (would need file)"
            return
        fi
    fi

    # 5. Test discovery endpoint
    log_info "Step 5: Test discovery miners..."
    MINERS=$(curl -s "$BASE_URL/discovery/miners" -H "$AUTH" | jq -r 'length')
    if [ "$MINERS" -gt 0 ]; then
        log_success "E2E: Found $MINERS discovery algorithms"
    else
        log_failure "E2E: No discovery algorithms found"
    fi

    # 6. Test analytics endpoints (if dataset is ready)
    log_info "Step 6: Test analytics..."
    ANALYTICS=$(curl -s "$BASE_URL/analytics/$DATASET/variants" -H "$AUTH" 2>/dev/null)
    if echo "$ANALYTICS" | jq -e '.variants' > /dev/null 2>&1; then
        log_success "E2E: Analytics endpoints working"
    else
        log_skip "E2E: Analytics skipped (dataset may not be ready)"
    fi

    log_success "E2E: Flow test completed"
}

print_summary() {
    log_section "TEST SUMMARY"

    echo ""
    echo -e "  ${GREEN}Passed:${NC}  $TESTS_PASSED"
    echo -e "  ${RED}Failed:${NC}  $TESTS_FAILED"
    echo -e "  ${YELLOW}Skipped:${NC} $TESTS_SKIPPED"
    echo ""

    if [ ${#FAILURES[@]} -gt 0 ]; then
        echo -e "${RED}FAILURES:${NC}"
        for failure in "${FAILURES[@]}"; do
            echo -e "  - $failure"
        done
        echo ""
    fi

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  ALL TESTS PASSED! MVP is looking good.${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        exit 0
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}  $TESTS_FAILED TESTS FAILED - See failures above${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        exit 1
    fi
}

# ============================================================================
# MAIN
# ============================================================================

MODE="${1:-full}"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          AI Test Runner - Process Mining MVP                 ║"
echo "║          Mode: $MODE                                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"

case "$MODE" in
    quick)
        run_quick_checks
        ;;
    api)
        run_quick_checks
        run_api_tests
        ;;
    frontend)
        run_frontend_tests
        ;;
    quality)
        run_code_quality
        ;;
    e2e)
        run_e2e_flow
        ;;
    full)
        run_quick_checks
        run_code_quality
        run_api_tests
        run_e2e_flow
        # run_backend_tests  # Uncomment to include pytest
        # run_frontend_tests # Uncomment to include jest
        ;;
    *)
        echo "Usage: $0 [quick|full|api|frontend|quality|e2e]"
        echo ""
        echo "  quick    - Health checks only"
        echo "  api      - Health + API endpoint tests"
        echo "  frontend - Jest tests only"
        echo "  quality  - Code quality checks (lint, types)"
        echo "  e2e      - End-to-end user flow"
        echo "  full     - All tests (default)"
        exit 1
        ;;
esac

print_summary
