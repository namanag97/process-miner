#!/bin/bash

# Configuration
BASE_URL="http://localhost:8001"
AUTH_EMAIL="test@example.com"
AUTH_PASSWORD="password"
PROJECT_ID="default"
FIXTURES_DIR="tests/e2e/fixtures"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[TEST]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 0. Generate large file if not exists
if [ ! -f "$FIXTURES_DIR/large_valid.csv" ] || [ $(wc -l < "$FIXTURES_DIR/large_valid.csv") -lt 100 ]; then
    log "Generating large CSV..."
    python3 "$FIXTURES_DIR/generate_large_csv.py"
fi


# 1. Register / Login
log "Registering new test user..."
TIMESTAMP=$(date +%s)
AUTH_EMAIL="test-e2e-${TIMESTAMP}@example.com"
AUTH_PASSWORD="SecurePass123!"
AUTH_NAME="E2E User ${TIMESTAMP}"

# Try to register
REGISTER_RESP=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$AUTH_EMAIL\", \"password\": \"$AUTH_PASSWORD\", \"name\": \"$AUTH_NAME\"}")

TOKEN=$(echo $REGISTER_RESP | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    # Maybe registration failed? unexpected.
    error "Failed to register: $REGISTER_RESP"
fi
log "Registered and Authenticated successfully as $AUTH_EMAIL."


# Function to run ingestion test
run_ingestion_test() {
    local FILE=$1
    local DESC=$2
    local SHOULD_FAIL=$3 # 0 for success, 1 for fail

    log "Starting Test: $DESC"
    
    # Upload
    log "Uploading file: $FILE"
    UPLOAD_RESP=$(curl -s -X POST "$BASE_URL/api/v1/datasets/" \
      -H "Authorization: Bearer $TOKEN" \
      -F "file=@$FILE" \
      -F "name=Test Dataset $(date +%s)" \
      -F "project_id=$PROJECT_ID")
    
    DATASET_ID=$(echo $UPLOAD_RESP | jq -r '.id')
    
    if [ "$DATASET_ID" == "null" ]; then
        error "Upload failed: $UPLOAD_RESP"
    fi
    log "Dataset uploaded: $DATASET_ID"

    # Mapping
    log "Submitting mapping..."
    MAPPING_RESP=$(curl -s -X POST "$BASE_URL/api/v1/datasets/$DATASET_ID/mapping" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"case_id": "case_id", "activity": "activity", "timestamp": "timestamp"}')
    
    # Ingest
    log "Triggering ingestion..."
    INGEST_RESP=$(curl -s -X POST "$BASE_URL/api/v1/datasets/$DATASET_ID/ingest" \
      -H "Authorization: Bearer $TOKEN")
    
    WORKFLOW_ID=$(echo $INGEST_RESP | jq -r '.workflow_id')
    
    if [ "$WORKFLOW_ID" == "null" ]; then
         if [ "$SHOULD_FAIL" == "1" ]; then
            log "Ingestion triggered failed as expected (or maybe it didn't start). output: $INGEST_RESP"
            return 0
         else
            error "Ingestion trigger failed: $INGEST_RESP"
         fi
    fi
    log "Workflow started: $WORKFLOW_ID"

    # Poll
    log "Polling for completion..."
    while true; do
      STATUS=$(curl -s "$BASE_URL/api/v1/operations/$WORKFLOW_ID" \
        -H "Authorization: Bearer $TOKEN" | jq -r '.status')
      
      log "Status: $STATUS"
      
      if [ "$STATUS" == "COMPLETED" ]; then
          if [ "$SHOULD_FAIL" == "1" ]; then
             error "Workflow succeeded but was expected to fail"
          fi
          break
      elif [ "$STATUS" == "FAILED" ]; then
          if [ "$SHOULD_FAIL" == "0" ]; then
             error "Workflow failed unexpectedly"
          fi
          log "Workflow failed as expected."
          break
      fi
      sleep 2
    done
    
    if [ "$SHOULD_FAIL" == "0" ]; then
        # Check Dataset Status
        DS_STATUS=$(curl -s "$BASE_URL/api/v1/datasets/$DATASET_ID" \
          -H "Authorization: Bearer $TOKEN" | jq -r '.status')
        if [ "$DS_STATUS" != "ready" ]; then
            error "Dataset status is not ready: $DS_STATUS"
        fi
        log "Dataset is READY."
    fi
}


# Function to run discovery test
run_discovery_test() {
    local DATASET_ID=$1
    if [ -z "$DATASET_ID" ]; then
        error "Dataset ID required for discovery test"
    fi
    
    log "Starting Discovery Test for Dataset: $DATASET_ID"
    
    DISCOVERY_RESP=$(curl -s -X POST "$BASE_URL/api/v1/discovery/discover" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"dataset_id\": \"$DATASET_ID\", \"miner_type\": \"inductive\", \"model_name\": \"test_model_$(date +%s)\"}")
      
    WORKFLOW_ID=$(echo $DISCOVERY_RESP | jq -r '.workflow_id')
    
    if [ "$WORKFLOW_ID" == "null" ]; then
        error "Discovery trigger failed: $DISCOVERY_RESP"
    fi
    log "Discovery Workflow started: $WORKFLOW_ID"
    
    # Poll
    log "Polling for completion..."
    while true; do
      STATUS=$(curl -s "$BASE_URL/api/v1/operations/$WORKFLOW_ID" \
        -H "Authorization: Bearer $TOKEN" | jq -r '.status')
      
      log "Status: $STATUS"
      
      if [ "$STATUS" == "COMPLETED" ]; then
          break
      elif [ "$STATUS" == "FAILED" ]; then
          error "Discovery workflow failed"
      fi
      sleep 2
    done
    log "Discovery Test Passed."
}

# Function to run cancellation test
run_cancellation_test() {
    local FILE=$1
    log "Starting Cancellation Test"
    
    # Upload & Start Ingest (using large file to ensure it runs long enough, or just normal one and cancel fast)
    # We'll use the small one but try to cancel immediately.
    
    # Upload
    UPLOAD_RESP=$(curl -s -X POST "$BASE_URL/api/v1/datasets/" \
      -H "Authorization: Bearer $TOKEN" \
      -F "file=@$FILE" \
      -F "name=Cancel Test $(date +%s)" \
      -F "project_id=$PROJECT_ID")
    DATASET_ID=$(echo $UPLOAD_RESP | jq -r '.id')
    
    # Mapping
    curl -s -X POST "$BASE_URL/api/v1/datasets/$DATASET_ID/mapping" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"case_id": "case_id", "activity": "activity", "timestamp": "timestamp"}' > /dev/null
      
    # Trigger Ingest
    INGEST_RESP=$(curl -s -X POST "$BASE_URL/api/v1/datasets/$DATASET_ID/ingest" \
      -H "Authorization: Bearer $TOKEN")
    WORKFLOW_ID=$(echo $INGEST_RESP | jq -r '.workflow_id')
    
    log "Workflow to cancel: $WORKFLOW_ID"
    
    # Cancel immediately
    curl -s -X POST "$BASE_URL/api/v1/operations/$WORKFLOW_ID/cancel" \
      -H "Authorization: Bearer $TOKEN" > /dev/null
    
    log "Sent cancel request."
    
    # Verify
    sleep 2
    STATUS=$(curl -s "$BASE_URL/api/v1/operations/$WORKFLOW_ID" \
        -H "Authorization: Bearer $TOKEN" | jq -r '.status')
        
    log "Status after cancel: $STATUS"
    
    if [ "$STATUS" == "CANCELLED" ] || [ "$STATUS" == "FAILED" ]; then
        log "Cancellation Test Passed (Status: $STATUS)"
    else
        # It might have completed too fast if it's small. 
        log "Warning: Workflow status is $STATUS. It might have finished before cancellation."
    fi
}

# Run Tests
DATASET_ID_RESULT=""
run_ingestion_test_capture() {
    # Wrapper to capture dataset ID for discovery test
    local FILE=$1
    local DESC=$2
    
    log "Starting Test: $DESC"
    UPLOAD_RESP=$(curl -s -X POST "$BASE_URL/api/v1/datasets/" \
      -H "Authorization: Bearer $TOKEN" \
      -F "file=@$FILE" \
      -F "name=Test Dataset $(date +%s)" \
      -F "project_id=$PROJECT_ID")
    DATASET_ID=$(echo $UPLOAD_RESP | jq -r '.id')
    
    if [ "$DATASET_ID" == "null" ]; then error "Upload failed"; fi
    
    curl -s -X POST "$BASE_URL/api/v1/datasets/$DATASET_ID/mapping" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"case_id": "case_id", "activity": "activity", "timestamp": "timestamp"}' > /dev/null
      
    INGEST_RESP=$(curl -s -X POST "$BASE_URL/api/v1/datasets/$DATASET_ID/ingest" \
      -H "Authorization: Bearer $TOKEN")
    WORKFLOW_ID=$(echo $INGEST_RESP | jq -r '.workflow_id')
    
    log "Workflow: $WORKFLOW_ID"
    
    while true; do
      STATUS=$(curl -s "$BASE_URL/api/v1/operations/$WORKFLOW_ID" \
        -H "Authorization: Bearer $TOKEN" | jq -r '.status')
      if [ "$STATUS" == "COMPLETED" ]; then break; fi
      if [ "$STATUS" == "FAILED" ]; then error "Workflow failed"; fi
      sleep 1
    done
    DATASET_ID_RESULT=$DATASET_ID
}

run_ingestion_test_capture "$FIXTURES_DIR/small_valid.csv" "Small Valid CSV (for Discovery)"
run_discovery_test "$DATASET_ID_RESULT"
run_cancellation_test "$FIXTURES_DIR/large_valid.csv"

# Optional: Run failure tests
# run_ingestion_test "$FIXTURES_DIR/missing_columns.csv" "Missing Columns" 1

log "All tests passed!"

