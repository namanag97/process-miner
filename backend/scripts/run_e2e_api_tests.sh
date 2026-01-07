#!/bin/bash
# Run E2E API Tests
# This script starts the backend server (if needed), waits for health check,
# runs the E2E API test suite, and generates a bug report.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         E2E API Test Suite Runner                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8001}"
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HEALTH_ENDPOINT="/health"
MAX_WAIT=30

echo -e "${YELLOW}[1/4] Checking server status...${NC}"

# Check if server is already running
if curl -s -f "${BASE_URL}${HEALTH_ENDPOINT}" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server is already running at ${BASE_URL}${NC}"
else
    echo -e "${YELLOW}Server not running. Please start the backend server first:${NC}"
    echo -e "${YELLOW}  cd ${BACKEND_DIR}${NC}"
    echo -e "${YELLOW}  make dev${NC}"
    echo ""
    exit 1
fi

echo ""
echo -e "${YELLOW}[2/4] Waiting for server health check...${NC}"

# Wait for health check
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s -f "${BASE_URL}${HEALTH_ENDPOINT}" | grep -q '"status":"healthy"'; then
        echo -e "${GREEN}✓ Server is healthy${NC}"
        break
    fi
    
    sleep 1
    WAITED=$((WAITED + 1))
    
    if [ $WAITED -eq $MAX_WAIT ]; then
        echo -e "${RED}✗ Server health check timed out after ${MAX_WAIT}s${NC}"
        exit 1
    fi
done

echo ""
echo -e "${YELLOW}[3/4] Running E2E API tests...${NC}"
echo ""

# Run the Python test suite
cd "${BACKEND_DIR}/tests/e2e"
python3 e2e_api_tester.py

echo ""
echo -e "${YELLOW}[4/4] Test complete!${NC}"
echo -e "${GREEN}✓ Bug report saved to: tests/e2e/bug_reports/${NC}"
echo ""

# Show latest report
LATEST_REPORT=$(ls -t "${BACKEND_DIR}/tests/e2e/bug_reports/report_"*.md 2>/dev/null | head -1)
if [ -n "$LATEST_REPORT" ]; then
    echo -e "${GREEN}Latest report: ${LATEST_REPORT}${NC}"
    echo ""
    
    # Show summary section
    echo -e "${YELLOW}Report Summary:${NC}"
    sed -n '/## Summary/,/## /p' "$LATEST_REPORT" | head -n -1
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         E2E API Test Suite Complete                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
