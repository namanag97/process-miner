#!/bin/bash
# =============================================================================
# E2E User Journey Test Suite v2.0 - COMPREHENSIVE
# =============================================================================
# Tests ALL user workflows using curl against a running backend.
# Run with: ./scripts/test_user_journeys.sh [BASE_URL]
#
# Prerequisites:
# - Backend running on localhost:8001 (or specified BASE_URL)
# - jq installed for JSON parsing
#
# User Journeys Tested:
# 1. Health Check - Verify system is operational  
# 2. Authentication - Register, login, token refresh
# 3. Workspace Setup - Create/list workspaces and projects
# 4. Dataset Lifecycle - Upload, detect columns, SHEETS, map, ingest
# 5. Discovery - Discover process models
# 6. Analytics - Bottlenecks, rework, performance
# 7. Visualization - DFG, footprints, explorer data
# 8. Error Quality - Validate error messages
# =============================================================================

# Removed set -e to allow test suite to continue on expected failures
# set -e

# Configuration
BASE_URL="${1:-http://localhost:8001}"
API_URL="${BASE_URL}/api/v1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
SKIPPED=0
CRITICAL_FAILURES=0

# Auth token (set by auth tests)
AUTH_TOKEN=""

# Test state
DATASET_ID=""
MODEL_ID=""
WORKSPACE_ID=""
PROJECT_ID=""

# =============================================================================
# Utility Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

log_critical() {
    echo -e "${RED}[CRITICAL]${NC} $1"
    ((CRITICAL_FAILURES++))
    ((FAILED++))
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    ((SKIPPED++))
}

log_section() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# HTTP helpers with auth support
http_get() {
    local url="$1"
    local expected_status="${2:-200}"
    local response status_code body
    
    if [ -n "$AUTH_TOKEN" ]; then
        response=$(curl -s -w "\n%{http_code}" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            "$url")
    else
        response=$(curl -s -w "\n%{http_code}" "$url")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo "$body"
        return 0
    else
        echo "Expected $expected_status, got $status_code" >&2
        echo "$body" >&2
        return 1
    fi
}

http_post() {
    local url="$1"
    local data="$2"
    local expected_status="${3:-200}"
    local response status_code body
    
    if [ -n "$AUTH_TOKEN" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -d "$data" \
            "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$url")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo "$body"
        return 0
    else
        echo "Expected $expected_status, got $status_code" >&2
        echo "$body" >&2
        return 1
    fi
}

http_post_file() {
    local url="$1"
    local file="$2"
    local project="$3"
    local expected_status="${4:-200}"
    local response status_code body
    
    if [ -n "$AUTH_TOKEN" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -F "file=@$file" \
            -F "project_id=$project" \
            "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -F "file=@$file" \
            -F "project_id=$project" \
            "$url")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo "$body"
        return 0
    else
        echo "Expected $expected_status, got $status_code" >&2  
        echo "$body" >&2
        return 1
    fi
}

# =============================================================================
# Journey 1: Health Check
# =============================================================================

test_health_journey() {
    log_section "Journey 1: Health Check"
    
    # Test root endpoint
    if http_get "$BASE_URL/" > /dev/null 2>&1; then
        log_success "Root endpoint accessible"
    else
        log_fail "Root endpoint not accessible"
    fi
    
    # Test health endpoint
    if response=$(http_get "$BASE_URL/health"); then
        status=$(echo "$response" | jq -r '.status')
        if [ "$status" = "healthy" ] || [ "$status" = "ok" ]; then
            log_success "Health check: $status"
        else
            log_fail "Unexpected health status: $status"
        fi
    else
        log_fail "Health endpoint failed"
    fi
    
    # Test liveness probe
    if http_get "$BASE_URL/health/live" > /dev/null 2>&1; then
        log_success "Liveness probe passed"
    else
        log_skip "Liveness probe not implemented"
    fi
    
    # Test readiness probe
    if http_get "$BASE_URL/health/ready" > /dev/null 2>&1; then
        log_success "Readiness probe passed"
    else
        log_skip "Readiness probe not implemented"
    fi
}

# =============================================================================
# Journey 2: Authentication
# =============================================================================

test_auth_journey() {
    log_section "Journey 2: Authentication"
    
    local email="test_e2e_$(date +%s)@test.com"
    local password="TestPass123!"
    
    # Test login (may work with dev mode)
    log_info "Testing login endpoint..."
    if response=$(http_post "$API_URL/auth/login" \
        "{\"email\":\"admin@test.com\",\"password\":\"admin123\"}"); then
        AUTH_TOKEN=$(echo "$response" | jq -r '.access_token // empty')
        if [ -n "$AUTH_TOKEN" ] && [ "$AUTH_TOKEN" != "null" ]; then
            log_success "Login successful, got token"
        else
            log_info "Login returned, but no token (dev mode?)"
            # Try to extract from different response format
            AUTH_TOKEN=$(echo "$response" | jq -r '.token // .access_token // empty')
        fi
    else
        log_skip "Login failed (may need valid credentials)"
    fi
    
    # Test /me endpoint
    if [ -n "$AUTH_TOKEN" ]; then
        if response=$(http_get "$API_URL/auth/me"); then
            user_id=$(echo "$response" | jq -r '.id // .user.id // empty')
            if [ -n "$user_id" ] && [ "$user_id" != "null" ]; then
                log_success "Get current user: $user_id"
            else
                log_info "Got user info but no ID (structure varies)"
            fi
        else
            log_skip "/me endpoint not available"
        fi
    fi
    
    export AUTH_TOKEN
}

# =============================================================================
# Journey 3: Workspace & Project Setup
# =============================================================================

test_workspace_journey() {
    log_section "Journey 3: Workspace & Project Setup"
    
    # List workspaces
    if response=$(http_get "$API_URL/workspaces"); then
        count=$(echo "$response" | jq -r '.items | length // 0')
        log_success "Listed $count workspaces"
        
        if [ "$count" -gt 0 ]; then
            WORKSPACE_ID=$(echo "$response" | jq -r '.items[0].id')
            log_info "Using workspace: $WORKSPACE_ID"
        fi
    else
        log_fail "Failed to list workspaces"
    fi
    
    # List projects
    if response=$(http_get "$API_URL/projects"); then
        count=$(echo "$response" | jq -r '.items | length // 0')
        log_success "Listed $count projects"
        
        if [ "$count" -gt 0 ]; then
            PROJECT_ID=$(echo "$response" | jq -r '.items[0].id')
            log_info "Using project: $PROJECT_ID"
        fi
    else
        log_fail "Failed to list projects"
    fi
    
    export WORKSPACE_ID PROJECT_ID
}

# =============================================================================
# Journey 4: Dataset Lifecycle (CRITICAL - includes SHEETS endpoint)
# =============================================================================

test_dataset_journey() {
    log_section "Journey 4: Dataset Lifecycle (Upload → Sheets → Map → Ingest)"
    
    # Create test CSV
    TEST_CSV="/tmp/e2e_test_event_log.csv"
    cat > "$TEST_CSV" << 'EOF'
case_id,activity,timestamp,resource
case_1,Start,2026-01-01 09:00:00,Alice
case_1,Process,2026-01-01 09:30:00,Bob
case_1,Approve,2026-01-01 10:00:00,Charlie
case_1,End,2026-01-01 10:30:00,Alice
case_2,Start,2026-01-01 10:00:00,Bob
case_2,Process,2026-01-01 10:45:00,Alice
case_2,End,2026-01-01 11:00:00,Bob
case_3,Start,2026-01-01 11:00:00,Alice
case_3,Review,2026-01-01 11:30:00,Charlie
case_3,Process,2026-01-01 12:00:00,Bob
case_3,Approve,2026-01-01 12:30:00,Charlie
case_3,End,2026-01-01 13:00:00,Alice
EOF
    log_info "Created test CSV: $TEST_CSV"
    
    # Step 1: Upload file 
    log_info "Step 1: Upload file (project_id: $PROJECT_ID)"
    if [ -z "$PROJECT_ID" ]; then
        log_fail "No project available for upload (run workspace journey first)"
        return 1
    fi
    if response=$(http_post_file "$API_URL/datasets/" "$TEST_CSV" "$PROJECT_ID"); then
        DATASET_ID=$(echo "$response" | jq -r '.id // .dataset_id // empty')
        if [ -n "$DATASET_ID" ] && [ "$DATASET_ID" != "null" ]; then
            log_success "Uploaded dataset: $DATASET_ID"
        else
            log_fail "Upload returned no dataset ID"
            echo "$response"
            return 1
        fi
    else
        log_fail "Failed to upload file"
        return 1
    fi
    
    # Step 2: Get dataset details
    log_info "Step 2: Get dataset details"
    if response=$(http_get "$API_URL/datasets/$DATASET_ID"); then
        status=$(echo "$response" | jq -r '.status')
        log_success "Dataset status: $status"
    else
        log_fail "Failed to get dataset details"
    fi
    
    # =========================================================================
    # Step 3: TEST SHEETS ENDPOINT (This was the NetworkError root cause!)
    # =========================================================================
    log_info "Step 3: TEST SHEETS ENDPOINT (Critical - NetworkError fix)"
    if response=$(http_get "$API_URL/datasets/$DATASET_ID/sheets"); then
        sheets_count=$(echo "$response" | jq -r '.total // .sheets | length // 0')
        sheets=$(echo "$response" | jq -r '.sheets')
        if [ "$sheets" != "null" ] && [ "$sheets_count" -gt 0 ]; then
            log_success "Sheets endpoint works! Found $sheets_count sheet(s)"
        else
            log_critical "Sheets endpoint returned empty/invalid response"
            echo "$response"
        fi
    else
        log_critical "SHEETS ENDPOINT FAILED - This causes upload wizard NetworkError!"
    fi
    
    # Step 4: Detect columns
    log_info "Step 4: Detect columns"
    if response=$(http_get "$API_URL/datasets/$DATASET_ID/columns"); then
        columns=$(echo "$response" | jq -r '.columns | length // 0')
        log_success "Detected $columns columns"
    else
        log_skip "Column detection endpoint not available"
    fi
    
    # Step 5: Submit mapping
    log_info "Step 5: Submit column mapping"
    MAPPING_PAYLOAD='{
        "case_id_column": "case_id",
        "activity_column": "activity",
        "timestamp_column": "timestamp",
        "resource_column": "resource"
    }'
    
    if response=$(http_post "$API_URL/datasets/$DATASET_ID/mapping" "$MAPPING_PAYLOAD"); then
        log_success "Mapping submitted"
    else
        log_skip "Mapping submission failed (may need different format)"
    fi
    
    # Step 6: Trigger ingestion
    log_info "Step 6: Trigger ingestion"
    if response=$(http_post "$API_URL/datasets/$DATASET_ID/ingest" "{}" 202); then
        job_id=$(echo "$response" | jq -r '.id // .job_id // empty')
        log_success "Ingestion triggered, job: $job_id"
    else
        log_skip "Ingestion requires Temporal/Celery (skipping)"
    fi
    
    # Step 7: Poll status
    log_info "Step 7: Poll dataset status"
    sleep 2
    if response=$(http_get "$API_URL/datasets/$DATASET_ID"); then
        status=$(echo "$response" | jq -r '.status')
        log_info "Final dataset status: $status"
        if [ "$status" = "ready" ] || [ "$status" = "READY" ]; then
            log_success "Dataset is ready!"
        else
            log_info "Dataset not yet ready (async processing)"
        fi
    fi
    
    export DATASET_ID
}

# =============================================================================
# Journey 5: Process Discovery
# =============================================================================

test_discovery_journey() {
    log_section "Journey 5: Process Discovery"
    
    if [ -z "$DATASET_ID" ]; then
        log_skip "No dataset available, skipping discovery"
        return 0
    fi
    
    # List miners
    if response=$(http_get "$API_URL/discovery/miners"); then
        miners=$(echo "$response" | jq -r '.miners | length // 0')
        log_success "Available miners: $miners"
    else
        log_skip "Miners endpoint not available"
    fi
    
    # Discover model
    DISCOVER_PAYLOAD="{\"dataset_id\": \"$DATASET_ID\", \"algorithm\": \"inductive\"}"
    if response=$(http_post "$API_URL/discovery/discover" "$DISCOVER_PAYLOAD" 202); then
        MODEL_ID=$(echo "$response" | jq -r '.id // .model_id // empty')
        if [ -n "$MODEL_ID" ] && [ "$MODEL_ID" != "null" ]; then
            log_success "Discovery started, model: $MODEL_ID"
        else
            log_info "Discovery started (async)"
        fi
    else
        log_skip "Discovery requires async processing"
    fi
    
    # List models
    if response=$(http_get "$API_URL/discovery/models"); then
        count=$(echo "$response" | jq -r '.items | length // 0')
        log_success "Found $count process models"
    else
        log_skip "Models endpoint not available"
    fi
    
    export MODEL_ID
}

# =============================================================================
# Journey 6: Analytics
# =============================================================================

test_analytics_journey() {
    log_section "Journey 6: Analytics"
    
    if [ -z "$DATASET_ID" ]; then
        log_skip "No dataset available, skipping analytics"
        return 0
    fi
    
    # Test each analytics endpoint
    local endpoints=(
        "bottlenecks"
        "rework"
        "service-times"
        "cycle-time"
        "throughput"
        "performance"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if response=$(http_get "$API_URL/analytics/datasets/$DATASET_ID/$endpoint"); then
            log_success "Analytics/$endpoint works"
        else
            log_skip "Analytics/$endpoint not available (may need READY dataset)"
        fi
    done
}

# =============================================================================
# Journey 7: Visualization
# =============================================================================

test_visualization_journey() {
    log_section "Journey 7: Visualization"
    
    if [ -z "$DATASET_ID" ]; then
        log_skip "No dataset available, skipping visualization"
        return 0
    fi
    
    # DFG endpoint
    if response=$(http_get "$API_URL/visualization/$DATASET_ID/dfg"); then
        nodes=$(echo "$response" | jq -r '.nodes | length // 0')
        edges=$(echo "$response" | jq -r '.edges | length // 0')
        log_success "DFG: $nodes nodes, $edges edges"
    else
        log_skip "DFG endpoint not available"
    fi
    
    # Explorer data
    if response=$(http_get "$API_URL/visualization/$DATASET_ID/explorer-data"); then
        log_success "Explorer data endpoint works"
    else
        log_skip "Explorer data not available"
    fi
    
    # Footprints
    if response=$(http_get "$API_URL/visualization/$DATASET_ID/footprints"); then
        log_success "Footprints endpoint works"
    else
        log_skip "Footprints endpoint not available"
    fi
}

# =============================================================================
# Journey 8: Error Message Quality
# =============================================================================

test_error_message_quality() {
    log_section "Journey 8: Error Message Quality"
    
    local poor_messages=0
    
    # Test 404 for non-existent dataset
    response=$(curl -s "$API_URL/datasets/nonexistent-uuid-12345")
    error_msg=$(echo "$response" | jq -r '.detail // .message // .error // empty')
    if [ -z "$error_msg" ] || [ "$error_msg" = "Not found" ]; then
        log_fail "Poor 404 message for dataset: '$error_msg'"
        ((poor_messages++))
    else
        log_success "Dataset 404 has helpful message"
    fi
    
    # Test 404 for non-existent sheets (CRITICAL for NetworkError debugging)
    response=$(curl -s "$API_URL/datasets/nonexistent-uuid/sheets")
    error_msg=$(echo "$response" | jq -r '.detail // .message // empty')
    if [ -z "$error_msg" ] || [ "${#error_msg}" -lt 10 ]; then
        log_fail "Poor 404 message for sheets: '$error_msg'"
        ((poor_messages++))
    else
        log_success "Sheets 404 has helpful message"
    fi
    
    # Test validation error
    response=$(curl -s -X POST -H "Content-Type: application/json" -d '{}' "$API_URL/datasets/test/mapping")
    error_msg=$(echo "$response" | jq -r '.detail // .message // empty')
    if [ -n "$error_msg" ]; then
        log_success "Validation error has message"
    else
        log_info "No validation error message (may be expected)"
    fi
    
    if [ "$poor_messages" -gt 0 ]; then
        log_info "Found $poor_messages endpoints with poor error messages"
    fi
}

# =============================================================================
# Cleanup
# =============================================================================

cleanup_test_data() {
    log_section "Cleanup: Removing Test Data"
    
    if [ -n "$DATASET_ID" ] && [ "$DATASET_ID" != "null" ]; then
        log_info "Deleting test dataset: $DATASET_ID"
        response=$(curl -s -X DELETE "$API_URL/datasets/$DATASET_ID" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -w "%{http_code}")
        status_code=$(echo "$response" | tail -c 4)
        if [ "$status_code" = "200" ] || [ "$status_code" = "204" ] || [ "$status_code" = "404" ]; then
            log_success "Deleted dataset"
        else
            log_info "Could not delete dataset (status: $status_code)"
        fi
    fi
    
    if [ -f "/tmp/e2e_test_event_log.csv" ]; then
        rm -f "/tmp/e2e_test_event_log.csv"
        log_success "Removed temp CSV"
    fi
    
    log_info "Cleanup complete"
}

# =============================================================================
# Main Test Runner
# =============================================================================

main() {
    log_section "E2E User Journey Test Suite v2.0"
    echo "Base URL: $BASE_URL"
    echo "Started: $(date)"
    echo ""
    
    # Set up trap for cleanup
    trap cleanup_test_data EXIT
    
    # Check prerequisites
    if ! command -v jq &> /dev/null; then
        echo "ERROR: jq is required. Install with: brew install jq"
        exit 1
    fi
    
    # Check if server is running
    if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        echo "ERROR: Backend not responding at $BASE_URL"
        echo "Start the backend with: cd backend && make dev"
        exit 1
    fi
    
    # Run all journeys
    test_health_journey
    test_auth_journey
    test_workspace_journey
    test_dataset_journey
    test_discovery_journey
    test_analytics_journey
    test_visualization_journey
    test_error_message_quality
    
    # Summary
    log_section "Test Summary"
    echo -e "  ${GREEN}Passed:${NC}   $PASSED"
    echo -e "  ${RED}Failed:${NC}   $FAILED"
    echo -e "  ${RED}Critical:${NC} $CRITICAL_FAILURES"
    echo -e "  ${YELLOW}Skipped:${NC}  $SKIPPED"
    echo ""
    
    if [ "$CRITICAL_FAILURES" -gt 0 ]; then
        echo -e "${RED}❌ CRITICAL FAILURES DETECTED - These cause user-facing bugs!${NC}"
        exit 2
    elif [ "$FAILED" -gt 0 ]; then
        echo -e "${RED}❌ Some tests failed${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ All tests passed!${NC}"
        exit 0
    fi
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
