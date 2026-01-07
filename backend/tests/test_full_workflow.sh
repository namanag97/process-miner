#!/bin/bash
# =============================================================================
# Full E2E Workflow Test - Upload, Map, Ingest, Discover
# =============================================================================
# Tests the complete process mining workflow:
# 1. Login and get auth token
# 2. Upload a CSV event log
# 3. Get detected columns
# 4. Submit column mapping
# 5. Trigger data ingestion
# 6. Poll until dataset is READY
# 7. Run process discovery
# 8. Display discovered process model
# =============================================================================

set -e

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8001}"
API_PREFIX="/api/v1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test data
TEST_USER_EMAIL="analyst@example.com"
TEST_USER_PASSWORD="password123"
TEST_PROJECT_ID="mvp-proj-001"

# Variables to store state
ACCESS_TOKEN=""
DATASET_ID=""
DISCOVERY_RESULT=""

# =============================================================================
# Utility Functions
# =============================================================================

log() {
    local level="$1"
    shift
    local msg="$*"

    case "$level" in
        "INFO")   echo -e "${BLUE}[INFO]${NC} $msg" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} $msg" ;;
        "ERROR")  echo -e "${RED}[ERROR]${NC} $msg" ;;
        "WARN")   echo -e "${YELLOW}[WARN]${NC} $msg" ;;
        "STEP")   echo -e "${CYAN}[STEP]${NC} $msg" ;;
        "DATA")   echo -e "${CYAN}$msg${NC}" ;;
    esac
}

api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"

    local url="${BASE_URL}${API_PREFIX}${endpoint}"
    local headers=(-H "Content-Type: application/json")

    if [[ -n "$ACCESS_TOKEN" ]]; then
        headers+=(-H "Authorization: Bearer $ACCESS_TOKEN")
    fi

    local cmd=(curl -s -w '\n%{http_code}' -X "$method" "$url" "${headers[@]}")

    if [[ -n "$data" ]]; then
        cmd+=(-d "$data")
    fi

    local response
    response=$("${cmd[@]}" 2>/dev/null)

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    echo "$http_code|$body"
}

check_status() {
    local expected="$1"
    local actual="$2"
    local step="$3"

    if [[ "$actual" == "$expected" ]]; then
        log "SUCCESS" "$step (HTTP $actual)"
        return 0
    else
        log "ERROR" "$step - Expected: $expected, Got: $actual"
        return 1
    fi
}

# =============================================================================
# Step 1: Login
# =============================================================================

step_login() {
    log "STEP" "========== STEP 1: LOGIN =========="

    local login_data='{"email":"'"$TEST_USER_EMAIL"'","password":"'"$TEST_USER_PASSWORD"'"}'
    local response=$(api_call "POST" "/auth/login" "$login_data")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    check_status "200" "$code" "Login"

    ACCESS_TOKEN=$(echo "$body" | jq -r '.access_token')
    log "INFO" "Got access token: ${ACCESS_TOKEN:0:20}..."
}

# =============================================================================
# Step 2: Upload Dataset
# =============================================================================

step_upload_dataset() {
    log "STEP" "========== STEP 2: UPLOAD DATASET =========="

    # Create a realistic test event log
    local test_csv_file="/tmp/process_mining_test_$$.csv"
    cat > "$test_csv_file" << 'EOF'
case_id,activity,timestamp,resource,cost
CASE-001,Register Request,2024-01-01 09:00:00,Alice,50
CASE-001,Check Documents,2024-01-01 09:30:00,Bob,100
CASE-001,Approve Request,2024-01-01 10:00:00,Charlie,75
CASE-001,Process Payment,2024-01-01 11:00:00,Alice,200
CASE-001,Close Case,2024-01-01 12:00:00,Bob,25
CASE-002,Register Request,2024-01-01 09:15:00,Bob,50
CASE-002,Check Documents,2024-01-01 09:45:00,Alice,100
CASE-002,Reject Request,2024-01-01 10:30:00,Charlie,50
CASE-002,Close Case,2024-01-01 11:00:00,Alice,25
CASE-003,Register Request,2024-01-01 10:00:00,Alice,50
CASE-003,Check Documents,2024-01-01 10:30:00,Charlie,100
CASE-003,Request More Info,2024-01-01 11:00:00,Bob,75
CASE-003,Check Documents,2024-01-01 14:00:00,Charlie,100
CASE-003,Approve Request,2024-01-01 15:00:00,Alice,75
CASE-003,Process Payment,2024-01-01 16:00:00,Bob,200
CASE-003,Close Case,2024-01-01 17:00:00,Charlie,25
CASE-004,Register Request,2024-01-02 08:00:00,Charlie,50
CASE-004,Check Documents,2024-01-02 08:30:00,Alice,100
CASE-004,Approve Request,2024-01-02 09:00:00,Bob,75
CASE-004,Process Payment,2024-01-02 10:00:00,Charlie,200
CASE-004,Close Case,2024-01-02 11:00:00,Alice,25
CASE-005,Register Request,2024-01-02 09:00:00,Bob,50
CASE-005,Check Documents,2024-01-02 09:30:00,Charlie,100
CASE-005,Reject Request,2024-01-02 10:00:00,Alice,50
CASE-005,Close Case,2024-01-02 10:30:00,Bob,25
EOF

    log "INFO" "Created test CSV with 5 cases and 25 events"

    # Upload the file
    local upload_url="${BASE_URL}${API_PREFIX}/datasets/"
    local response=$(curl -s -w '\n%{http_code}' -X POST "$upload_url" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -F "file=@$test_csv_file" \
        -F "project_id=$TEST_PROJECT_ID" \
        -F "name=E2E Full Workflow Test")

    local code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    check_status "200" "$code" "Upload dataset"

    DATASET_ID=$(echo "$body" | jq -r '.id')
    local status=$(echo "$body" | jq -r '.status')

    log "INFO" "Dataset ID: $DATASET_ID"
    log "INFO" "Initial status: $status"

    # Cleanup
    rm -f "$test_csv_file"
}

# =============================================================================
# Step 3: Get Detected Columns
# =============================================================================

step_get_columns() {
    log "STEP" "========== STEP 3: GET DETECTED COLUMNS =========="

    # Wait a moment for column detection
    sleep 2

    local response=$(api_call "GET" "/datasets/$DATASET_ID/columns")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    check_status "200" "$code" "Get columns"

    log "INFO" "Detected columns:"
    echo "$body" | jq -r '.columns[] | "  - \(.name) (\(.dtype))"' 2>/dev/null || echo "$body" | jq '.'
}

# =============================================================================
# Step 4: Submit Column Mapping
# =============================================================================

step_submit_mapping() {
    log "STEP" "========== STEP 4: SUBMIT COLUMN MAPPING =========="

    local mapping_data='{
        "case_id_column": "case_id",
        "activity_column": "activity",
        "timestamp_column": "timestamp",
        "resource_column": "resource",
        "additional_columns": ["cost"]
    }'

    log "INFO" "Submitting mapping:"
    log "DATA" "  - case_id_column: case_id"
    log "DATA" "  - activity_column: activity"
    log "DATA" "  - timestamp_column: timestamp"
    log "DATA" "  - resource_column: resource"
    log "DATA" "  - additional_columns: [cost]"

    local response=$(api_call "POST" "/datasets/$DATASET_ID/mapping" "$mapping_data")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    check_status "200" "$code" "Submit mapping"

    local new_status=$(echo "$body" | jq -r '.status // .dataset_status // "unknown"')
    log "INFO" "Dataset status after mapping: $new_status"
}

# =============================================================================
# Step 5: Trigger Ingestion
# =============================================================================

step_trigger_ingestion() {
    log "STEP" "========== STEP 5: TRIGGER INGESTION =========="

    local response=$(api_call "POST" "/datasets/$DATASET_ID/ingest" '{}')
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    # Accept 200 (sync) or 202 (async) or 409 (already ingesting)
    if [[ "$code" == "200" || "$code" == "202" ]]; then
        log "SUCCESS" "Ingestion triggered (HTTP $code)"
        local job_id=$(echo "$body" | jq -r '.job_id // .workflow_id // "N/A"')
        log "INFO" "Ingestion job ID: $job_id"
    elif [[ "$code" == "409" ]]; then
        log "WARN" "Ingestion already in progress or completed"
    else
        log "ERROR" "Ingestion trigger failed (HTTP $code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    fi
}

# =============================================================================
# Step 6: Wait for Dataset to be READY
# =============================================================================

step_wait_for_ready() {
    log "STEP" "========== STEP 6: WAIT FOR INGESTION =========="

    local max_polls=60
    local poll_interval=2
    local current_status=""

    for ((i=1; i<=max_polls; i++)); do
        local response=$(api_call "GET" "/datasets/$DATASET_ID")
        local code=$(echo "$response" | cut -d'|' -f1)
        local body=$(echo "$response" | cut -d'|' -f2-)

        if [[ "$code" != "200" ]]; then
            log "ERROR" "Failed to get dataset status"
            return 1
        fi

        current_status=$(echo "$body" | jq -r '.status')
        local total_cases=$(echo "$body" | jq -r '.total_cases // 0')
        local total_events=$(echo "$body" | jq -r '.total_events // 0')

        printf "\r${BLUE}[INFO]${NC} Poll %d/%d: Status = %-12s Cases = %-5s Events = %-5s" \
            "$i" "$max_polls" "$current_status" "$total_cases" "$total_events"

        if [[ "$current_status" == "ready" || "$current_status" == "READY" ]]; then
            echo ""  # New line after progress
            log "SUCCESS" "Dataset is READY!"
            log "INFO" "Total cases: $total_cases"
            log "INFO" "Total events: $total_events"

            # Get activities
            local activities=$(echo "$body" | jq -r '.activities // [] | join(", ")')
            if [[ -n "$activities" && "$activities" != "" ]]; then
                log "INFO" "Activities: $activities"
            fi
            return 0
        elif [[ "$current_status" == "failed" || "$current_status" == "FAILED" || "$current_status" == "error" || "$current_status" == "ERROR" ]]; then
            echo ""  # New line after progress
            local error_msg=$(echo "$body" | jq -r '.error_message // "Unknown error"')
            log "ERROR" "Dataset ingestion failed: $error_msg"
            return 1
        fi

        sleep "$poll_interval"
    done

    echo ""  # New line after progress
    log "ERROR" "Timeout waiting for dataset to be ready (status: $current_status)"
    return 1
}

# =============================================================================
# Step 7: Run Process Discovery
# =============================================================================

step_run_discovery() {
    log "STEP" "========== STEP 7: RUN PROCESS DISCOVERY =========="

    # First, list available algorithms
    log "INFO" "Fetching available algorithms..."
    local alg_response=$(api_call "GET" "/algorithms")
    local alg_code=$(echo "$alg_response" | cut -d'|' -f1)
    local alg_body=$(echo "$alg_response" | cut -d'|' -f2-)

    if [[ "$alg_code" == "200" ]]; then
        log "INFO" "Available discovery algorithms:"
        echo "$alg_body" | jq -r '.algorithms[] | select(.category == "discovery") | "  - \(.id): \(.name)"' 2>/dev/null || true
    fi

    # Run discovery with inductive miner
    log "INFO" "Running process discovery with Inductive Miner..."

    local discover_data='{
        "dataset_id": "'"$DATASET_ID"'",
        "algorithm": "inductive",
        "parameters": {
            "noise_threshold": 0.0
        }
    }'

    local response=$(api_call "POST" "/discovery/discover" "$discover_data")
    local code=$(echo "$response" | cut -d'|' -f1)
    local body=$(echo "$response" | cut -d'|' -f2-)

    if [[ "$code" == "200" || "$code" == "202" ]]; then
        log "SUCCESS" "Process discovery completed (HTTP $code)"
        DISCOVERY_RESULT="$body"

        # Display the discovered model info
        log "INFO" "========== DISCOVERED PROCESS MODEL =========="

        # Try to extract model information
        local model_id=$(echo "$body" | jq -r '.model_id // .id // "N/A"')
        local model_type=$(echo "$body" | jq -r '.model_type // .type // "petri_net"')

        log "INFO" "Model ID: $model_id"
        log "INFO" "Model Type: $model_type"

        # Display model structure if available
        if echo "$body" | jq -e '.places' > /dev/null 2>&1; then
            local num_places=$(echo "$body" | jq '.places | length')
            local num_transitions=$(echo "$body" | jq '.transitions | length')
            local num_arcs=$(echo "$body" | jq '.arcs | length')

            log "INFO" "Petri Net Structure:"
            log "DATA" "  - Places: $num_places"
            log "DATA" "  - Transitions: $num_transitions"
            log "DATA" "  - Arcs: $num_arcs"

            log "INFO" "Transitions (Activities):"
            echo "$body" | jq -r '.transitions[] | "  - \(.label // .name // .id)"' 2>/dev/null || true
        fi

        # Display DFG if available
        if echo "$body" | jq -e '.nodes' > /dev/null 2>&1; then
            log "INFO" "Process Model Nodes:"
            echo "$body" | jq -r '.nodes[] | "  - \(.id): \(.label // .name) (freq: \(.frequency // "N/A"))"' 2>/dev/null || true

            log "INFO" "Process Model Edges:"
            echo "$body" | jq -r '.edges[] | "  - \(.source) → \(.target) (freq: \(.frequency // .weight // "N/A"))"' 2>/dev/null || true
        fi

        # Show full response for debugging
        log "INFO" "Full Discovery Response:"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"

    else
        log "ERROR" "Process discovery failed (HTTP $code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        return 1
    fi
}

# =============================================================================
# Step 8: Cleanup
# =============================================================================

step_cleanup() {
    log "STEP" "========== CLEANUP =========="

    if [[ -n "$DATASET_ID" && "$DATASET_ID" != "null" ]]; then
        local response=$(api_call "DELETE" "/datasets/$DATASET_ID")
        local code=$(echo "$response" | cut -d'|' -f1)

        if [[ "$code" == "200" || "$code" == "204" ]]; then
            log "INFO" "Deleted dataset: $DATASET_ID"
        else
            log "WARN" "Failed to delete dataset (HTTP $code)"
        fi
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    echo "=============================================="
    echo "  Full E2E Workflow Test"
    echo "  Upload → Map → Ingest → Discover"
    echo "=============================================="
    echo "Base URL: $BASE_URL"
    echo ""

    # Check if backend is available
    if ! curl -s "${BASE_URL}/health/live" > /dev/null 2>&1; then
        log "ERROR" "Backend server not available at $BASE_URL"
        exit 1
    fi

    # Run workflow steps
    step_login
    step_upload_dataset
    step_get_columns
    step_submit_mapping
    step_trigger_ingestion
    step_wait_for_ready
    step_run_discovery

    # Auto cleanup unless KEEP_DATA is set
    if [[ "${KEEP_DATA:-}" != "true" ]]; then
        step_cleanup
    else
        log "INFO" "Dataset kept: $DATASET_ID"
    fi

    echo ""
    log "SUCCESS" "========== WORKFLOW COMPLETE =========="
}

# Handle signals
trap 'echo ""; log "WARN" "Interrupted"; step_cleanup; exit 1' INT TERM

# Run main
main "$@"
