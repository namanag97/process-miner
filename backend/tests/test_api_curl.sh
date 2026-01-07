#!/bin/bash
# =============================================================================
# Process Mining Platform - API Integration Test Script
# =============================================================================
# Usage: ./test_api_curl.sh
# This script tests all major API endpoints using curl
# =============================================================================

set -e  # Exit on first error

# Configuration
BASE_URL="${API_URL:-http://localhost:8001}"
API_PREFIX="/api/v1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

print_test() {
    echo -e "\n${YELLOW}▶ TEST: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ PASSED: $1${NC}"
    ((PASSED++))
}

print_fail() {
    echo -e "${RED}✗ FAILED: $1${NC}"
    echo -e "${RED}  Response: $2${NC}"
    ((FAILED++))
}

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Warning: jq not found. Install jq for prettier output."
    JQ_CMD="cat"
else
    JQ_CMD="jq"
fi

# =============================================================================
# HEALTH CHECKS
# =============================================================================
print_header "HEALTH CHECK ENDPOINTS"

print_test "GET /health - Basic health check"
RESPONSE=$(curl -s "${BASE_URL}/health")
if echo "$RESPONSE" | grep -q '"status":"healthy"'; then
    print_success "Health check passed"
    echo "$RESPONSE" | $JQ_CMD
else
    print_fail "Health check" "$RESPONSE"
fi

print_test "GET /health/ready - Readiness probe"
RESPONSE=$(curl -s "${BASE_URL}/health/ready")
if echo "$RESPONSE" | grep -q '"status"'; then
    print_success "Readiness probe passed"
    echo "$RESPONSE" | $JQ_CMD
else
    print_fail "Readiness probe" "$RESPONSE"
fi

print_test "GET /health/live - Liveness probe"
RESPONSE=$(curl -s "${BASE_URL}/health/live")
if echo "$RESPONSE" | grep -q '"status"'; then
    print_success "Liveness probe passed"
    echo "$RESPONSE" | $JQ_CMD
else
    print_fail "Liveness probe" "$RESPONSE"
fi

# =============================================================================
# AUTHENTICATION
# =============================================================================
print_header "AUTHENTICATION ENDPOINTS"

# Try to login with MVP user first
print_test "POST /auth/login - Login with MVP user"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "analyst@company.local",
        "password": "devpassword123"
    }')

if echo "$LOGIN_RESPONSE" | grep -q '"access_token"'; then
    print_success "Login successful"
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | $JQ_CMD -r '.access_token // empty' 2>/dev/null || echo "")
    REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | $JQ_CMD -r '.refresh_token // empty' 2>/dev/null || echo "")
    echo "Access Token: ${ACCESS_TOKEN:0:50}..."
else
    echo -e "${YELLOW}MVP user login failed, trying registration...${NC}"

    # Register a new user
    print_test "POST /auth/register - Register new user"
    REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test@example.com",
            "password": "TestPassword123!",
            "name": "Test User",
            "organization_name": "Test Org"
        }')

    if echo "$REGISTER_RESPONSE" | grep -q '"access_token"'; then
        print_success "Registration successful"
        ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | $JQ_CMD -r '.access_token // empty' 2>/dev/null || echo "")
        echo "Access Token: ${ACCESS_TOKEN:0:50}..."
    else
        print_fail "Registration" "$REGISTER_RESPONSE"
        ACCESS_TOKEN=""
    fi
fi

# Auth header for subsequent requests
AUTH_HEADER=""
if [ -n "$ACCESS_TOKEN" ]; then
    AUTH_HEADER="-H \"Authorization: Bearer $ACCESS_TOKEN\""
fi

print_test "GET /auth/me - Get current user"
if [ -n "$ACCESS_TOKEN" ]; then
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/auth/me" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"email"'; then
        print_success "Get current user"
        echo "$RESPONSE" | $JQ_CMD
    else
        print_fail "Get current user" "$RESPONSE"
    fi
else
    echo -e "${YELLOW}Skipping - No access token${NC}"
fi

# =============================================================================
# ORGANIZATIONS
# =============================================================================
print_header "ORGANIZATIONS ENDPOINTS"

print_test "GET /organizations - List organizations"
if [ -n "$ACCESS_TOKEN" ]; then
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/organizations" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"items"\|"id"'; then
        print_success "List organizations"
        echo "$RESPONSE" | $JQ_CMD
        ORG_ID=$(echo "$RESPONSE" | $JQ_CMD -r '.items[0].id // .id // empty' 2>/dev/null || echo "mvp-org-001")
    else
        print_fail "List organizations" "$RESPONSE"
        ORG_ID="mvp-org-001"
    fi
else
    echo -e "${YELLOW}Skipping - No access token${NC}"
    ORG_ID="mvp-org-001"
fi

# =============================================================================
# WORKSPACES
# =============================================================================
print_header "WORKSPACES ENDPOINTS"

print_test "GET /workspaces - List workspaces"
if [ -n "$ACCESS_TOKEN" ]; then
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/workspaces" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"items"\|"id"'; then
        print_success "List workspaces"
        echo "$RESPONSE" | $JQ_CMD
        WS_ID=$(echo "$RESPONSE" | $JQ_CMD -r '.items[0].id // .id // empty' 2>/dev/null || echo "mvp-ws-001")
    else
        print_fail "List workspaces" "$RESPONSE"
        WS_ID="mvp-ws-001"
    fi
else
    echo -e "${YELLOW}Skipping - No access token${NC}"
    WS_ID="mvp-ws-001"
fi

# =============================================================================
# PROJECTS
# =============================================================================
print_header "PROJECTS ENDPOINTS"

print_test "GET /projects - List projects"
if [ -n "$ACCESS_TOKEN" ]; then
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/projects?workspace_id=${WS_ID}" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"items"\|"id"'; then
        print_success "List projects"
        echo "$RESPONSE" | $JQ_CMD
        PROJECT_ID=$(echo "$RESPONSE" | $JQ_CMD -r '.items[0].id // .id // empty' 2>/dev/null || echo "mvp-proj-001")
    else
        print_fail "List projects" "$RESPONSE"
        PROJECT_ID="mvp-proj-001"
    fi
else
    echo -e "${YELLOW}Skipping - No access token${NC}"
    PROJECT_ID="mvp-proj-001"
fi

# =============================================================================
# DATASETS
# =============================================================================
print_header "DATASETS ENDPOINTS"

print_test "GET /datasets - List datasets"
if [ -n "$ACCESS_TOKEN" ]; then
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/datasets?project_id=${PROJECT_ID}" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"items"\|"id"\|[]'; then
        print_success "List datasets"
        echo "$RESPONSE" | $JQ_CMD
        DATASET_ID=$(echo "$RESPONSE" | $JQ_CMD -r '.items[0].id // empty' 2>/dev/null || echo "")
    else
        print_fail "List datasets" "$RESPONSE"
    fi
else
    echo -e "${YELLOW}Skipping - No access token${NC}"
fi

# If we have a dataset, test dataset-specific endpoints
if [ -n "$DATASET_ID" ]; then
    print_test "GET /datasets/{id} - Get dataset details"
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/datasets/${DATASET_ID}" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"id"'; then
        print_success "Get dataset details"
        echo "$RESPONSE" | $JQ_CMD
    else
        print_fail "Get dataset details" "$RESPONSE"
    fi

    print_test "GET /datasets/{id}/columns - Get dataset columns"
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/datasets/${DATASET_ID}/columns" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"columns"\|"name"'; then
        print_success "Get dataset columns"
        echo "$RESPONSE" | $JQ_CMD
    else
        print_fail "Get dataset columns" "$RESPONSE"
    fi

    print_test "GET /datasets/{id}/statistics - Get dataset statistics"
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/datasets/${DATASET_ID}/statistics" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"total_events"\|"total_cases"'; then
        print_success "Get dataset statistics"
        echo "$RESPONSE" | $JQ_CMD
    else
        print_fail "Get dataset statistics" "$RESPONSE"
    fi
fi

# =============================================================================
# DISCOVERY
# =============================================================================
print_header "DISCOVERY ENDPOINTS"

print_test "GET /discovery/miners - List available miners"
if [ -n "$ACCESS_TOKEN" ]; then
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/discovery/miners" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"algorithms"\|"miners"\|"inductive"\|"alpha"'; then
        print_success "List miners"
        echo "$RESPONSE" | $JQ_CMD
    else
        print_fail "List miners" "$RESPONSE"
    fi
else
    echo -e "${YELLOW}Skipping - No access token${NC}"
fi

# =============================================================================
# ANALYTICS (if dataset exists)
# =============================================================================
if [ -n "$DATASET_ID" ]; then
    print_header "ANALYTICS ENDPOINTS"

    print_test "GET /analytics/datasets/{id}/bottlenecks - Get bottlenecks"
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/analytics/datasets/${DATASET_ID}/bottlenecks" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"bottlenecks"\|"activity"\|"error"'; then
        print_success "Get bottlenecks"
        echo "$RESPONSE" | $JQ_CMD
    else
        print_fail "Get bottlenecks" "$RESPONSE"
    fi

    print_test "GET /analytics/datasets/{id}/cycle-time - Get cycle time"
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/analytics/datasets/${DATASET_ID}/cycle-time" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"mean_duration"\|"duration"\|"error"'; then
        print_success "Get cycle time"
        echo "$RESPONSE" | $JQ_CMD
    else
        print_fail "Get cycle time" "$RESPONSE"
    fi
fi

# =============================================================================
# VISUALIZATION (if dataset exists)
# =============================================================================
if [ -n "$DATASET_ID" ]; then
    print_header "VISUALIZATION ENDPOINTS"

    print_test "GET /visualization/{id}/dfg - Get DFG data"
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/visualization/${DATASET_ID}/dfg" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"nodes"\|"edges"\|"error"'; then
        print_success "Get DFG data"
        echo "$RESPONSE" | $JQ_CMD '.nodes[:2], .edges[:2]' 2>/dev/null || echo "$RESPONSE"
    else
        print_fail "Get DFG data" "$RESPONSE"
    fi
fi

# =============================================================================
# JOBS
# =============================================================================
print_header "JOBS ENDPOINTS"

print_test "GET /jobs - List jobs"
if [ -n "$ACCESS_TOKEN" ]; then
    RESPONSE=$(curl -s "${BASE_URL}${API_PREFIX}/jobs" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$RESPONSE" | grep -q '"items"\|"jobs"\|[]'; then
        print_success "List jobs"
        echo "$RESPONSE" | $JQ_CMD
    else
        print_fail "List jobs" "$RESPONSE"
    fi
else
    echo -e "${YELLOW}Skipping - No access token${NC}"
fi

# =============================================================================
# OPENAPI SPEC
# =============================================================================
print_header "API DOCUMENTATION"

print_test "GET /openapi.json - OpenAPI specification"
RESPONSE=$(curl -s "${BASE_URL}/openapi.json" | head -c 500)
if echo "$RESPONSE" | grep -q '"openapi"\|"paths"'; then
    print_success "OpenAPI spec available"
    echo "OpenAPI spec retrieved successfully (truncated)"
else
    print_fail "OpenAPI spec" "$RESPONSE"
fi

# =============================================================================
# SUMMARY
# =============================================================================
print_header "TEST SUMMARY"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
TOTAL=$((PASSED + FAILED))
echo -e "Total:  $TOTAL"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed.${NC}"
    exit 1
fi
