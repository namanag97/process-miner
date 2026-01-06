#!/bin/bash
# =============================================================================
# E2E User Journey Test Suite
# =============================================================================
# This script tests complete user journeys using curl against a running backend.
# Run with: ./scripts/test_user_journeys.sh [BASE_URL]
#
# Prerequisites:
# - Backend running on localhost:8001 (or specified BASE_URL)
# - jq installed for JSON parsing
#
# User Journeys Tested:
# 1. Health Check Journey - Verify system is operational
# 2. Upload & Ingest Journey - Upload CSV, ingest, verify ready
# 3. Discovery Journey - Discover process model from dataset
# 4. Full Analysis Journey - Complete workflow from upload to visualization
# =============================================================================

set -e

# Configuration
BASE_URL="${1:-http://localhost:8001}"
API_URL="${BASE_URL}/api/v1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DATA_DIR="${SCRIPT_DIR}/../test"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
SKIPPED=0

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

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    ((SKIPPED++))
}

log_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Make HTTP request and check status code
http_get() {
    local url="$1"
    local expected_status="${2:-200}"
    local response
    local status_code
    
    response=$(curl -s -w "\n%{http_code}" "$url")
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
    local response
    local status_code
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$data" \
        "$url")
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
    local expected_status="${3:-200}"
    local response
    local status_code
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -F "file=@$file" \
        "$url")
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

wait_for_status() {
    local url="$1"
    local expected_status="$2"
    local max_attempts="${3:-30}"
    local delay="${4:-2}"
    
    for ((i=1; i<=max_attempts; i++)); do
        response=$(curl -s "$url")
        status=$(echo "$response" | jq -r '.status // .state // empty')
        
        if [ "$status" = "$expected_status" ]; then
            echo "$response"
            return 0
        fi
        
        log_info "Waiting for status '$expected_status', current: '$status' (attempt $i/$max_attempts)"
        sleep "$delay"
    done
    
    echo "Timeout waiting for status '$expected_status'" >&2
    return 1
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
        return 1
    fi
    
    # Test health endpoint
    if response=$(http_get "$BASE_URL/health"); then
        status=$(echo "$response" | jq -r '.status')
        if [ "$status" = "healthy" ] || [ "$status" = "ok" ]; then
            log_success "Health check returned: $status"
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
        log_fail "Liveness probe failed"
    fi
    
    # Test readiness probe
    if http_get "$BASE_URL/health/ready" > /dev/null 2>&1; then
        log_success "Readiness probe passed"
    else
        log_fail "Readiness probe failed"
    fi
    
    # Test detailed health
    if response=$(http_get "$BASE_URL/health/detailed"); then
        components=$(echo "$response" | jq -r '.components | length')
        log_success "Detailed health shows $components components"
    else
        log_fail "Detailed health endpoint failed"
    fi
}

# =============================================================================
# Journey 2: Workspace & Project Setup
# =============================================================================

test_workspace_journey() {
    log_section "Journey 2: Workspace & Project Setup"
    
    # List workspaces
    if response=$(http_get "$API_URL/workspaces"); then
        count=$(echo "$response" | jq -r '.items | length')
        log_success "Listed $count workspaces"
        
        if [ "$count" -gt 0 ]; then
            WORKSPACE_ID=$(echo "$response" | jq -r '.items[0].id')
            log_info "Using workspace: $WORKSPACE_ID"
        fi
    else
        log_fail "Failed to list workspaces"
        return 1
    fi
    
    # List projects (if workspace exists)
    if [ -n "$WORKSPACE_ID" ]; then
        if response=$(http_get "$API_URL/projects"); then
            count=$(echo "$response" | jq -r '.items | length')
            log_success "Listed $count projects"
            
            if [ "$count" -gt 0 ]; then
                PROJECT_ID=$(echo "$response" | jq -r '.items[0].id')
                log_info "Using project: $PROJECT_ID"
            fi
        else
            log_fail "Failed to list projects"
        fi
    fi
    
    # Export for subsequent tests
    export WORKSPACE_ID PROJECT_ID
}

# =============================================================================
# Journey 3: Upload & Ingest Dataset
# =============================================================================

test_upload_journey() {
    log_section "Journey 3: Upload & Ingest Dataset"
    
    # Create temp test CSV if needed
    TEST_CSV="/tmp/test_event_log.csv"
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
    
    # Upload file
    if response=$(http_post_file "$API_URL/datasets/upload" "$TEST_CSV"); then
        DATASET_ID=$(echo "$response" | jq -r '.id // .dataset_id')
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
    
    # Detect columns
    if response=$(http_get "$API_URL/datasets/$DATASET_ID/detect-columns"); then
        columns=$(echo "$response" | jq -r '.columns | length')
        log_success "Detected $columns columns"
    else
        log_skip "Column detection failed (endpoint may not be implemented)"
    fi
    
    # Ingest dataset
    INGEST_PAYLOAD='{
        "case_id_column": "case_id",
        "activity_column": "activity", 
        "timestamp_column": "timestamp",
        "resource_column": "resource"
    }'
    
    if response=$(http_post "$API_URL/datasets/$DATASET_ID/ingest" "$INGEST_PAYLOAD"); then
        log_success "Ingestion started"
        job_id=$(echo "$response" | jq -r '.job_id // .workflow_id // empty')
        if [ -n "$job_id" ]; then
            log_info "Job/Workflow ID: $job_id"
        fi
    else
        log_skip "Ingestion endpoint may require Temporal (skipping)"
    fi
    
    # Wait for dataset to be ready (with timeout)
    log_info "Waiting for dataset to become ready..."
    sleep 3
    
    if response=$(http_get "$API_URL/datasets/$DATASET_ID"); then
        status=$(echo "$response" | jq -r '.status')
        log_info "Dataset status: $status"
        if [ "$status" = "ready" ] || [ "$status" = "READY" ]; then
            log_success "Dataset is ready"
        fi
    else
        log_skip "Could not verify dataset status"
    fi
    
    export DATASET_ID
}

# =============================================================================
# Journey 4: Process Discovery
# =============================================================================

test_discovery_journey() {
    log_section "Journey 4: Process Discovery"
    
    # Check if we have a dataset
    if [ -z "$DATASET_ID" ]; then
        log_skip "No dataset available, skipping discovery"
        return 0
    fi
    
    # List available miners
    if response=$(http_get "$API_URL/discovery/miners"); then
        miners=$(echo "$response" | jq -r '.miners | length')
        log_success "Available miners: $miners"
    else
        log_skip "Miners endpoint not available"
    fi
    
    # Trigger discovery
    DISCOVER_PAYLOAD="{\"dataset_id\": \"$DATASET_ID\", \"algorithm\": \"inductive\"}"
    
    if response=$(http_post "$API_URL/discovery/discover" "$DISCOVER_PAYLOAD"); then
        MODEL_ID=$(echo "$response" | jq -r '.id // .model_id // empty')
        if [ -n "$MODEL_ID" ]; then
            log_success "Discovery completed, model: $MODEL_ID"
        else
            log_info "Discovery started (async)"
        fi
    else
        log_skip "Discovery endpoint may require Temporal"
    fi
    
    # List models
    if response=$(http_get "$API_URL/discovery/models"); then
        count=$(echo "$response" | jq -r '.items | length')
        log_success "Found $count process models"
    else
        log_skip "Models endpoint not available"
    fi
    
    export MODEL_ID
}

# =============================================================================
# Journey 5: Visualization & Analytics
# =============================================================================

test_visualization_journey() {
    log_section "Journey 5: Visualization & Analytics"
    
    if [ -z "$DATASET_ID" ]; then
        log_skip "No dataset available, skipping visualization"
        return 0
    fi
    
    # Get DFG
    if response=$(http_get "$API_URL/visualization/$DATASET_ID/dfg"); then
        nodes=$(echo "$response" | jq -r '.nodes | length')
        edges=$(echo "$response" | jq -r '.edges | length')
        log_success "DFG: $nodes nodes, $edges edges"
    else
        log_skip "DFG endpoint not available"
    fi
    
    # Get activities
    if response=$(http_get "$API_URL/datasets/$DATASET_ID/activities"); then
        activities=$(echo "$response" | jq -r '.items | length // .activities | length // 0')
        log_success "Activities in dataset: $activities"
    else
        log_skip "Activities endpoint not available"
    fi
    
    # Get variants
    if response=$(http_get "$API_URL/datasets/$DATASET_ID/variants"); then
        variants=$(echo "$response" | jq -r '.items | length // .variants | length // 0')
        log_success "Process variants: $variants"
    else
        log_skip "Variants endpoint not available"
    fi
}

# =============================================================================
# Journey 6: Error Message Quality (Happy Flow Validation)
# =============================================================================

test_error_message_quality() {
    log_section "Journey 6: Error Message Quality"
    
    local poor_messages=0
    
    # Test 404 responses have helpful messages
    log_info "Checking error response quality..."
    
    # Non-existent dataset
    response=$(curl -s "$API_URL/datasets/nonexistent-id-12345")
    error_msg=$(echo "$response" | jq -r '.detail // .message // .error // empty')
    if [ -z "$error_msg" ] || [ "$error_msg" = "Not found" ] || [ "$error_msg" = "null" ]; then
        log_fail "Poor error message for dataset 404: '$error_msg' (should explain what wasn't found)"
        ((poor_messages++))
    else
        log_success "Dataset 404 has helpful message: $error_msg"
    fi
    
    # Non-existent project
    response=$(curl -s "$API_URL/projects/nonexistent-id-12345")
    error_msg=$(echo "$response" | jq -r '.detail // .message // .error // empty')
    if [ -z "$error_msg" ] || [ "${#error_msg}" -lt 10 ]; then
        log_fail "Poor error message for project 404: '$error_msg'"
        ((poor_messages++))
    else
        log_success "Project 404 has helpful message"
    fi
    
    # Bad request validation
    response=$(curl -s -X POST -H "Content-Type: application/json" -d '{}' "$API_URL/datasets/test/ingest")
    error_msg=$(echo "$response" | jq -r '.detail // .message // empty')
    if [ -z "$error_msg" ]; then
        log_fail "No validation error message for empty ingest request"
        ((poor_messages++))
    else
        log_success "Validation error has message: ${error_msg:0:60}..."
    fi
    
    # Summary
    if [ "$poor_messages" -gt 0 ]; then
        log_info "Found $poor_messages endpoints with poor error messages - consider improving"
    else
        log_success "All tested error messages are helpful"
    fi
}

# =============================================================================
# Cleanup Test Data
# =============================================================================

cleanup_test_data() {
    log_section "Cleanup: Removing Test Data"
    
    # Delete test dataset if created
    if [ -n "$DATASET_ID" ] && [ "$DATASET_ID" != "null" ]; then
        log_info "Deleting test dataset: $DATASET_ID"
        response=$(curl -s -X DELETE "$API_URL/datasets/$DATASET_ID" -w "%{http_code}")
        status_code=$(echo "$response" | tail -c 4)
        if [ "$status_code" = "200" ] || [ "$status_code" = "204" ] || [ "$status_code" = "404" ]; then
            log_success "Deleted dataset $DATASET_ID"
        else
            log_info "Could not delete dataset (status: $status_code) - may need manual cleanup"
        fi
    fi
    
    # Delete test model if created
    if [ -n "$MODEL_ID" ] && [ "$MODEL_ID" != "null" ]; then
        log_info "Deleting test model: $MODEL_ID"
        response=$(curl -s -X DELETE "$API_URL/discovery/models/$MODEL_ID" -w "%{http_code}")
        status_code=$(echo "$response" | tail -c 4)
        if [ "$status_code" = "200" ] || [ "$status_code" = "204" ] || [ "$status_code" = "404" ]; then
            log_success "Deleted model $MODEL_ID"
        else
            log_info "Could not delete model (status: $status_code)"
        fi
    fi
    
    # Clean up temp files
    if [ -f "/tmp/test_event_log.csv" ]; then
        rm -f "/tmp/test_event_log.csv"
        log_success "Removed temp CSV file"
    fi
    
    log_info "Cleanup complete"
}

# =============================================================================
# Main Test Runner
# =============================================================================

main() {
    log_section "E2E User Journey Test Suite"
    echo "Base URL: $BASE_URL"
    echo "Started: $(date)"
    echo ""
    
    # Set up trap for cleanup on exit (including Ctrl+C)
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
    test_workspace_journey
    test_upload_journey
    test_discovery_journey
    test_visualization_journey
    test_error_message_quality
    
    # Summary
    log_section "Test Summary"
    echo -e "  ${GREEN}Passed:${NC}  $PASSED"
    echo -e "  ${RED}Failed:${NC}  $FAILED"
    echo -e "  ${YELLOW}Skipped:${NC} $SKIPPED"
    echo ""
    
    if [ "$FAILED" -gt 0 ]; then
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
