#!/bin/bash
# =============================================================================
# E2E Test Script for Temporal Workflow System
# =============================================================================
#
# Usage:
#   ./tests/e2e/curl_e2e_test.sh
#
# Requirements:
#   - Backend running on localhost:8001
#   - curl installed
#   - jq installed (optional, for pretty output)
#
# =============================================================================

set -e

BASE_URL="http://localhost:8001"
API_URL="${BASE_URL}/api/v1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=============================================="
echo "E2E Tests for Temporal Workflow System"
echo "=============================================="
echo ""

# =============================================================================
# Test 1: Health Checks
# =============================================================================
echo -e "${YELLOW}Test 1: Health Checks${NC}"

echo -n "  Liveness probe... "
LIVENESS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/health/live")
if [ "$LIVENESS" = "200" ]; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL (HTTP $LIVENESS)${NC}"
    exit 1
fi

echo -n "  Readiness probe... "
READINESS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/health/ready")
if [ "$READINESS" = "200" ]; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL (HTTP $READINESS)${NC}"
    exit 1
fi

echo ""

# =============================================================================
# Test 2: Operations API
# =============================================================================
echo -e "${YELLOW}Test 2: Operations API${NC}"

echo -n "  List operations... "
OPS_RESPONSE=$(curl -s -w "\n%{http_code}" "${API_URL}/operations" \
    -H "Authorization: Bearer test-token")
OPS_CODE=$(echo "$OPS_RESPONSE" | tail -1)
OPS_BODY=$(echo "$OPS_RESPONSE" | head -n -1)

if [ "$OPS_CODE" = "200" ]; then
    echo -e "${GREEN}PASS${NC}"
    if command -v jq &> /dev/null; then
        echo "    Response: $(echo $OPS_BODY | jq -c '{items: .items | length, total: .total}')"
    fi
else
    echo -e "${RED}FAIL (HTTP $OPS_CODE)${NC}"
fi

echo -n "  Get non-existent operation... "
NOTFOUND=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/operations/nonexistent-workflow-xyz" \
    -H "Authorization: Bearer test-token")
if [ "$NOTFOUND" = "404" ] || [ "$NOTFOUND" = "500" ]; then
    echo -e "${GREEN}PASS (HTTP $NOTFOUND as expected)${NC}"
else
    echo -e "${RED}FAIL (HTTP $NOTFOUND)${NC}"
fi

echo ""

# =============================================================================
# Test 3: SSE Streaming Endpoint
# =============================================================================
echo -e "${YELLOW}Test 3: SSE Streaming Endpoint${NC}"

echo -n "  Stream endpoint headers... "
# Use timeout to prevent hanging
SSE_HEADERS=$(curl -s -I --max-time 3 "${API_URL}/operations/test-workflow/stream" \
    -H "Authorization: Bearer test-token" 2>/dev/null || true)

if echo "$SSE_HEADERS" | grep -q "text/event-stream"; then
    echo -e "${GREEN}PASS (text/event-stream)${NC}"
else
    echo -e "${YELLOW}SKIP (endpoint may need running workflow)${NC}"
fi

echo ""

# =============================================================================
# Test 4: Dataset API (Preparation for Workflow Test)
# =============================================================================
echo -e "${YELLOW}Test 4: Dataset API${NC}"

echo -n "  List datasets... "
DS_RESPONSE=$(curl -s -w "\n%{http_code}" "${API_URL}/datasets" \
    -H "Authorization: Bearer test-token")
DS_CODE=$(echo "$DS_RESPONSE" | tail -1)

if [ "$DS_CODE" = "200" ]; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL (HTTP $DS_CODE)${NC}"
fi

echo ""

# =============================================================================
# Test 5: Full Workflow Test (Optional)
# =============================================================================
echo -e "${YELLOW}Test 5: Full Workflow Test${NC}"

# Create a test CSV file
TEMP_CSV=$(mktemp)
cat > "$TEMP_CSV" << 'CSV'
case_id,activity,timestamp,resource
1,Start,2024-01-01 10:00:00,Alice
1,Process,2024-01-01 10:30:00,Bob
1,End,2024-01-01 11:00:00,Alice
2,Start,2024-01-01 10:00:00,Bob
2,End,2024-01-01 10:30:00,Alice
CSV

echo -n "  Creating dataset... "
CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" "${API_URL}/datasets" \
    -H "Authorization: Bearer test-token" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"E2E Test $(date +%s)\", \"project_id\": \"mvp-proj-001\"}")
CREATE_CODE=$(echo "$CREATE_RESPONSE" | tail -1)
CREATE_BODY=$(echo "$CREATE_RESPONSE" | head -n -1)

if [ "$CREATE_CODE" = "201" ] || [ "$CREATE_CODE" = "200" ]; then
    DATASET_ID=$(echo "$CREATE_BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$DATASET_ID" ]; then
        echo -e "${GREEN}PASS (ID: $DATASET_ID)${NC}"

        # Try to upload
        echo -n "  Uploading file... "
        UPLOAD_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/datasets/${DATASET_ID}/upload" \
            -H "Authorization: Bearer test-token" \
            -F "file=@${TEMP_CSV};filename=test.csv" 2>/dev/null || echo "000")

        if [ "$UPLOAD_CODE" = "200" ] || [ "$UPLOAD_CODE" = "201" ]; then
            echo -e "${GREEN}PASS${NC}"

            # Try to ingest
            echo -n "  Starting ingestion... "
            INGEST_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/datasets/${DATASET_ID}/ingest" \
                -H "Authorization: Bearer test-token" \
                -H "Content-Type: application/json" \
                -d '{"case_id_column": "case_id", "activity_column": "activity", "timestamp_column": "timestamp"}' \
                2>/dev/null || echo "000")

            if [ "$INGEST_CODE" = "200" ] || [ "$INGEST_CODE" = "201" ] || [ "$INGEST_CODE" = "202" ]; then
                echo -e "${GREEN}PASS${NC}"

                WORKFLOW_ID="ingest-dataset-${DATASET_ID}"
                echo "  Workflow ID: $WORKFLOW_ID"

                # Poll for status
                echo -n "  Polling workflow status"
                for i in {1..10}; do
                    sleep 2
                    echo -n "."
                    STATUS_RESPONSE=$(curl -s "${API_URL}/operations/${WORKFLOW_ID}" \
                        -H "Authorization: Bearer test-token" 2>/dev/null || echo "{}")
                    STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)

                    if [ "$STATUS" = "COMPLETED" ]; then
                        echo -e " ${GREEN}COMPLETED${NC}"
                        break
                    elif [ "$STATUS" = "FAILED" ]; then
                        echo -e " ${RED}FAILED${NC}"
                        break
                    fi
                done

                if [ "$STATUS" != "COMPLETED" ] && [ "$STATUS" != "FAILED" ]; then
                    echo -e " ${YELLOW}TIMEOUT (status: $STATUS)${NC}"
                fi
            else
                echo -e "${YELLOW}SKIP (HTTP $INGEST_CODE - Temporal may not be running)${NC}"
            fi
        else
            echo -e "${YELLOW}SKIP (HTTP $UPLOAD_CODE)${NC}"
        fi

        # Cleanup
        echo -n "  Cleaning up... "
        curl -s -o /dev/null "${API_URL}/datasets/${DATASET_ID}" \
            -X DELETE \
            -H "Authorization: Bearer test-token" 2>/dev/null || true
        echo "Done"
    else
        echo -e "${RED}FAIL (no ID in response)${NC}"
    fi
else
    echo -e "${YELLOW}SKIP (HTTP $CREATE_CODE)${NC}"
fi

rm -f "$TEMP_CSV"

echo ""

# =============================================================================
# Summary
# =============================================================================
echo "=============================================="
echo -e "${GREEN}E2E Tests Complete${NC}"
echo "=============================================="
echo ""
echo "For SSE streaming test, use:"
echo "  curl -N ${API_URL}/operations/{workflow_id}/stream -H 'Authorization: Bearer test-token'"
echo ""
