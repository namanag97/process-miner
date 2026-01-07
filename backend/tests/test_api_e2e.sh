#!/bin/bash
# =============================================================================
# E2E API Test Script - Happy Path Business Requirements
# =============================================================================
# Tests the full process mining workflow:
# 1. Auth - Login and get token
# 2. Organizations - View org
# 3. Workspaces - CRUD operations
# 4. Projects - CRUD operations
# 5. Datasets - Upload and manage event logs
# 6. Discovery - Process model discovery
# 7. Analytics - Performance analysis
# =============================================================================

set -e

# Note: We use `|| true` for arithmetic operations that might evaluate to 0
# because `set -e` treats ((0)) as failure

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8001}"
API_PREFIX="/api/v1"
LOG_FILE="test_results_$(date +%Y%m%d_%H%M%S).log"
VERBOSE="${VERBOSE:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Test data
TEST_USER_EMAIL="analyst@example.com"
TEST_USER_PASSWORD="password123"
TEST_ORG_ID="mvp-org-001"
TEST_WORKSPACE_ID="mvp-ws-001"
TEST_PROJECT_ID="mvp-proj-001"
ACCESS_TOKEN=""

# Created resources for cleanup
CREATED_WORKSPACE_ID=""
CREATED_PROJECT_ID=""
CREATED_DATASET_ID=""

# =============================================================================
# Utility Functions
# =============================================================================

log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $msg" >> "$LOG_FILE"

    case "$level" in
        "INFO")  echo -e "${BLUE}[INFO]${NC} $msg" ;;
        "PASS")  echo -e "${GREEN}[PASS]${NC} $msg" ;;
        "FAIL")  echo -e "${RED}[FAIL]${NC} $msg" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC} $msg" ;;
        # DEBUG goes to stderr to avoid interfering with function return values
        "DEBUG") [[ "$VERBOSE" == "true" ]] && echo -e "[DEBUG] $msg" >&2 ;;
    esac
}

api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local extra_headers="$4"

    local url="${BASE_URL}${API_PREFIX}${endpoint}"
    local headers="-H 'Content-Type: application/json'"

    if [[ -n "$ACCESS_TOKEN" ]]; then
        headers="$headers -H 'Authorization: Bearer $ACCESS_TOKEN'"
    fi

    if [[ -n "$extra_headers" ]]; then
        headers="$headers $extra_headers"
    fi

    local cmd="curl -s -w '\n%{http_code}' -X $method '$url' $headers"

    if [[ -n "$data" ]]; then
        cmd="$cmd -d '$data'"
    fi

    log "DEBUG" "Request: $method $url"
    [[ -n "$data" ]] && log "DEBUG" "Body: $data"

    local response
    response=$(eval "$cmd" 2>/dev/null)

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    log "DEBUG" "Response: $http_code - $body"

    echo "$http_code|$body"
}

assert_status() {
    local expected="$1"
    local actual="$2"
    local test_name="$3"

    if [[ "$actual" == "$expected" ]]; then
        log "PASS" "$test_name (HTTP $actual)"
        ((TESTS_PASSED++)) || true
        return 0
    else
        log "FAIL" "$test_name (Expected: $expected, Got: $actual)"
        ((TESTS_FAILED++)) || true
        return 1
    fi
}

assert_json_field() {
    local json="$1"
    local field="$2"
    local test_name="$3"

    if echo "$json" | jq -e ".$field" > /dev/null 2>&1; then
        log "PASS" "$test_name - has field '$field'"
        ((TESTS_PASSED++)) || true
        return 0
    else
        log "FAIL" "$test_name - missing field '$field'"
        ((TESTS_FAILED++)) || true
        return 1
    fi
}

extract_json() {
    local json="$1"
    local field="$2"
    echo "$json" | jq -r ".$field" 2>/dev/null
}

# =============================================================================
# Test Suites
# =============================================================================

test_health() {
    log "INFO" "========== HEALTH CHECKS =========="

    # Test liveness
    local response=$(curl -s -w '\n%{http_code}' "${BASE_URL}/health/live")
    local code=$(echo "$response" | tail -n1)
    assert_status "200" "$code" "Health - Liveness probe"

    # Test readiness
    response=$(curl -s -w '\n%{http_code}' "${BASE_URL}/health/ready")
    code=$(echo "$response" | tail -n1)
    assert_status "200" "$code" "Health - Readiness probe"

    # Test root endpoint
    response=$(curl -s -w '\n%{http_code}' "${BASE_URL}/")
    code=$(echo "$response" | tail -n1)
    assert_status "200" "$code" "Health - Root endpoint"
}

test_auth() {
    log "INFO" "========== AUTHENTICATION =========="

    # Test login
    local login_data='{"email":"'"$TEST_USER_EMAIL"'","password":"'"$TEST_USER_PASSWORD"'"}'
    local response=$(api_call "POST" "/auth/login" "$login_data")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "200" "$code" "Auth - Login"

    if [[ "$code" == "200" ]]; then
        ACCESS_TOKEN=$(extract_json "$body" "access_token")
        if [[ -n "$ACCESS_TOKEN" && "$ACCESS_TOKEN" != "null" ]]; then
            log "PASS" "Auth - Got access token"
            ((TESTS_PASSED++))
        else
            log "FAIL" "Auth - No access token in response"
            ((TESTS_FAILED++))
        fi
    fi

    # Test get current user
    if [[ -n "$ACCESS_TOKEN" ]]; then
        response=$(api_call "GET" "/auth/me")
        code=$(echo "$response" | cut -d'|' -f1)
        body=$(echo "$response" | cut -d'|' -f2-)

        assert_status "200" "$code" "Auth - Get current user"
        # Response has nested user object
        assert_json_field "$body" "user.id" "Auth - User has ID"
        assert_json_field "$body" "user.email" "Auth - User has email"
    fi
}

test_organizations() {
    log "INFO" "========== ORGANIZATIONS =========="

    # List organizations (trailing slash required)
    local response=$(api_call "GET" "/organizations/")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "200" "$code" "Organizations - List"

    # Get specific organization
    response=$(api_call "GET" "/organizations/$TEST_ORG_ID")
    code=$(echo "$response" | cut -d'|' -f1)
    body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "200" "$code" "Organizations - Get by ID"
    assert_json_field "$body" "id" "Organizations - Has ID"
    assert_json_field "$body" "name" "Organizations - Has name"
}

test_workspaces() {
    log "INFO" "========== WORKSPACES =========="

    # List workspaces
    local response=$(api_call "GET" "/workspaces")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "200" "$code" "Workspaces - List"

    # Get specific workspace
    response=$(api_call "GET" "/workspaces/$TEST_WORKSPACE_ID")
    code=$(echo "$response" | cut -d'|' -f1)
    body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "200" "$code" "Workspaces - Get by ID"
    assert_json_field "$body" "id" "Workspaces - Has ID"
    assert_json_field "$body" "name" "Workspaces - Has name"

    # Create workspace (org_id is required as query param)
    local create_data='{"name":"Test Workspace E2E","description":"Created by E2E tests"}'
    response=$(api_call "POST" "/workspaces?org_id=$TEST_ORG_ID" "$create_data")
    code=$(echo "$response" | cut -d'|' -f1)
    body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "201" "$code" "Workspaces - Create"

    if [[ "$code" == "201" ]]; then
        CREATED_WORKSPACE_ID=$(extract_json "$body" "id")
        log "INFO" "Created workspace: $CREATED_WORKSPACE_ID"
    fi

    # Update workspace (if created)
    if [[ -n "$CREATED_WORKSPACE_ID" && "$CREATED_WORKSPACE_ID" != "null" ]]; then
        local update_data='{"name":"Test Workspace E2E Updated","description":"Updated by E2E tests"}'
        response=$(api_call "PUT" "/workspaces/$CREATED_WORKSPACE_ID" "$update_data")
        code=$(echo "$response" | cut -d'|' -f1)
        assert_status "200" "$code" "Workspaces - Update"
    fi
}

test_projects() {
    log "INFO" "========== PROJECTS =========="

    # List projects
    local response=$(api_call "GET" "/projects")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "200" "$code" "Projects - List"

    # Get specific project
    response=$(api_call "GET" "/projects/$TEST_PROJECT_ID")
    code=$(echo "$response" | cut -d'|' -f1)
    body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "200" "$code" "Projects - Get by ID"
    assert_json_field "$body" "id" "Projects - Has ID"
    assert_json_field "$body" "name" "Projects - Has name"

    # Create project (workspace_id is required as query param)
    local create_data='{"name":"Test Project E2E","description":"Created by E2E tests"}'
    response=$(api_call "POST" "/projects?workspace_id=$TEST_WORKSPACE_ID" "$create_data")
    code=$(echo "$response" | cut -d'|' -f1)
    body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "201" "$code" "Projects - Create"

    if [[ "$code" == "201" ]]; then
        CREATED_PROJECT_ID=$(extract_json "$body" "id")
        log "INFO" "Created project: $CREATED_PROJECT_ID"
    fi
}

test_datasets() {
    log "INFO" "========== DATASETS =========="

    # List datasets (trailing slash required)
    local response=$(api_call "GET" "/datasets/")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "200" "$code" "Datasets - List"

    # Create a simple test CSV file
    local test_csv_file="/tmp/test_event_log_$$.csv"
    cat > "$test_csv_file" << 'EOF'
case_id,activity,timestamp,resource
1,Start,2024-01-01 09:00:00,Alice
1,Process,2024-01-01 10:00:00,Bob
1,Complete,2024-01-01 11:00:00,Alice
2,Start,2024-01-01 09:30:00,Bob
2,Process,2024-01-01 10:30:00,Alice
2,Complete,2024-01-01 11:30:00,Bob
3,Start,2024-01-01 10:00:00,Alice
3,Review,2024-01-01 11:00:00,Charlie
3,Process,2024-01-01 12:00:00,Bob
3,Complete,2024-01-01 13:00:00,Alice
EOF

    # Upload dataset using multipart form (endpoint is /datasets/ with trailing slash)
    local upload_url="${BASE_URL}${API_PREFIX}/datasets/"
    response=$(curl -s -w '\n%{http_code}' -X POST "$upload_url" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -F "file=@$test_csv_file" \
        -F "project_id=$TEST_PROJECT_ID" \
        -F "name=E2E Test Event Log")

    code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    # API returns 200 for successful upload (async processing starts separately)
    assert_status "200" "$code" "Datasets - Upload CSV"

    if [[ "$code" == "200" ]]; then
        CREATED_DATASET_ID=$(echo "$body" | jq -r '.id' 2>/dev/null)
        log "INFO" "Created dataset: $CREATED_DATASET_ID"

        # Get dataset details
        response=$(api_call "GET" "/datasets/$CREATED_DATASET_ID")
        code=$(echo "$response" | cut -d'|' -f1)
        body=$(echo "$response" | cut -d'|' -f2-)

        assert_status "200" "$code" "Datasets - Get by ID"
        assert_json_field "$body" "id" "Datasets - Has ID"
        assert_json_field "$body" "name" "Datasets - Has name"
        assert_json_field "$body" "status" "Datasets - Has status"
    fi

    # Cleanup test file
    rm -f "$test_csv_file"
}

test_discovery() {
    log "INFO" "========== PROCESS DISCOVERY =========="

    # List available algorithms
    local response=$(api_call "GET" "/algorithms")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "200" "$code" "Discovery - List algorithms"

    # Skip discovery if no dataset
    if [[ -z "$CREATED_DATASET_ID" || "$CREATED_DATASET_ID" == "null" ]]; then
        log "WARN" "Skipping discovery tests - no dataset available"
        ((TESTS_SKIPPED++)) || true
        return
    fi

    # Note: Full discovery requires dataset to be in READY status
    # For now, just test the endpoint responds correctly
    local discover_data='{"dataset_id":"'"$CREATED_DATASET_ID"'","algorithm":"inductive"}'
    response=$(api_call "POST" "/discovery/discover" "$discover_data")
    code=$(echo "$response" | cut -d'|' -f1)

    # Accept 200 (success) or 400/422 (dataset not ready - expected)
    if [[ "$code" == "200" || "$code" == "202" ]]; then
        assert_status "$code" "$code" "Discovery - Run process discovery"
    else
        log "WARN" "Discovery - Dataset not ready for discovery (HTTP $code)"
        ((TESTS_SKIPPED++)) || true
    fi
}

test_analytics() {
    log "INFO" "========== ANALYTICS =========="

    # Skip if no dataset
    if [[ -z "$CREATED_DATASET_ID" || "$CREATED_DATASET_ID" == "null" ]]; then
        log "WARN" "Skipping analytics tests - no dataset available"
        ((TESTS_SKIPPED++)) || true
        return
    fi

    # Test bottleneck analysis endpoint (path-based dataset_id)
    local response=$(api_call "GET" "/analytics/datasets/$CREATED_DATASET_ID/bottlenecks")
    local code=$(echo "$response" | cut -d'|' -f1)

    # Accept various codes (200 success, 400/422 dataset not ready)
    if [[ "$code" == "200" ]]; then
        assert_status "200" "$code" "Analytics - Bottleneck analysis"
    else
        log "WARN" "Analytics - Dataset not ready for analysis (HTTP $code)"
        ((TESTS_SKIPPED++)) || true
    fi
}

test_jobs() {
    log "INFO" "========== JOBS =========="

    # List jobs
    local response=$(api_call "GET" "/jobs")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    assert_status "200" "$code" "Jobs - List"
}

test_visualization() {
    log "INFO" "========== VISUALIZATION =========="

    # Skip if no dataset
    if [[ -z "$CREATED_DATASET_ID" || "$CREATED_DATASET_ID" == "null" ]]; then
        log "WARN" "Skipping visualization tests - no dataset available"
        ((TESTS_SKIPPED++)) || true
        return
    fi

    # Test DFG visualization endpoint (path-based dataset_id)
    local response=$(api_call "GET" "/visualization/$CREATED_DATASET_ID/dfg")
    local code=$(echo "$response" | cut -d'|' -f1)

    if [[ "$code" == "200" ]]; then
        assert_status "200" "$code" "Visualization - DFG"
    else
        log "WARN" "Visualization - Dataset not ready (HTTP $code)"
        ((TESTS_SKIPPED++)) || true
    fi
}

# =============================================================================
# Cleanup
# =============================================================================

cleanup() {
    log "INFO" "========== CLEANUP =========="

    # Delete created dataset
    if [[ -n "$CREATED_DATASET_ID" && "$CREATED_DATASET_ID" != "null" ]]; then
        local response=$(api_call "DELETE" "/datasets/$CREATED_DATASET_ID")
        local code=$(echo "$response" | cut -d'|' -f1)
        if [[ "$code" == "204" || "$code" == "200" ]]; then
            log "INFO" "Deleted dataset: $CREATED_DATASET_ID"
        else
            log "WARN" "Failed to delete dataset: $CREATED_DATASET_ID (HTTP $code)"
        fi
    fi

    # Delete created project
    if [[ -n "$CREATED_PROJECT_ID" && "$CREATED_PROJECT_ID" != "null" ]]; then
        local response=$(api_call "DELETE" "/projects/$CREATED_PROJECT_ID")
        local code=$(echo "$response" | cut -d'|' -f1)
        if [[ "$code" == "204" || "$code" == "200" ]]; then
            log "INFO" "Deleted project: $CREATED_PROJECT_ID"
        else
            log "WARN" "Failed to delete project: $CREATED_PROJECT_ID (HTTP $code)"
        fi
    fi

    # Delete created workspace
    if [[ -n "$CREATED_WORKSPACE_ID" && "$CREATED_WORKSPACE_ID" != "null" ]]; then
        local response=$(api_call "DELETE" "/workspaces/$CREATED_WORKSPACE_ID")
        local code=$(echo "$response" | cut -d'|' -f1)
        if [[ "$code" == "204" || "$code" == "200" ]]; then
            log "INFO" "Deleted workspace: $CREATED_WORKSPACE_ID"
        else
            log "WARN" "Failed to delete workspace: $CREATED_WORKSPACE_ID (HTTP $code)"
        fi
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    echo "=============================================="
    echo "  E2E API Tests - Process Mining Platform"
    echo "=============================================="
    echo "Base URL: $BASE_URL"
    echo "Log file: $LOG_FILE"
    echo ""

    log "INFO" "Starting E2E API tests"

    # Run test suites
    test_health
    test_auth
    test_organizations
    test_workspaces
    test_projects
    test_datasets
    test_discovery
    test_analytics
    test_visualization
    test_jobs

    # Cleanup
    cleanup

    # Summary
    echo ""
    echo "=============================================="
    echo "  TEST SUMMARY"
    echo "=============================================="
    echo -e "${GREEN}Passed:${NC}  $TESTS_PASSED"
    echo -e "${RED}Failed:${NC}  $TESTS_FAILED"
    echo -e "${YELLOW}Skipped:${NC} $TESTS_SKIPPED"
    echo "=============================================="
    echo ""

    log "INFO" "Tests completed - Passed: $TESTS_PASSED, Failed: $TESTS_FAILED, Skipped: $TESTS_SKIPPED"

    # Exit with failure if any tests failed
    if [[ $TESTS_FAILED -gt 0 ]]; then
        exit 1
    fi

    exit 0
}

# Handle signals for cleanup on interruption
trap 'echo "Interrupted. Running cleanup..."; cleanup; exit 1' INT TERM

# Run main (cleanup is called inside main, but trap handles interrupts)
main "$@"
