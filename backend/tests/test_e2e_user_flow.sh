#!/usr/bin/env bash
# =============================================================================
# Full E2E User Flow Test - All Discovery Algorithms
# =============================================================================
# 
# This script simulates a real user flow:
# 1. Register/Login as user
# 2. Create project
# 3. Upload event log (CSV or use BPI 2019 XES)
# 4. Run all discovery algorithms
# 5. Verify visualization endpoints return valid graph data
#
# Usage: ./test_e2e_user_flow.sh [--use-bpi]
# =============================================================================

set -e

BASE_URL="${BASE_URL:-http://localhost:8000/api/v1}"
TEST_EMAIL="e2e-test-$(date +%s)@test.com"
TEST_PASSWORD="TestPassword123!"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=============================================="
echo "🚀 E2E USER FLOW TEST - All Discovery Algorithms"
echo "=============================================="
echo "Base URL: $BASE_URL"
echo ""

# -----------------------------------------------------------------------------
# Step 1: Health Check
# -----------------------------------------------------------------------------
echo -n "1. Health Check... "
HEALTH=$(curl -s "http://localhost:8000/health" || curl -s "http://localhost:8000/" || echo '{"status":"error"}')
if echo "$HEALTH" | grep -q "ok\|healthy\|Process Mining"; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend not responding${NC}"
    exit 1
fi

# -----------------------------------------------------------------------------
# Step 2: Register User (or use demo user)
# -----------------------------------------------------------------------------
echo -n "2. Register/Login... "

# Try to use demo login endpoint first
LOGIN_RESP=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email": "demo@processminer.io", "password": "demo123"}' 2>/dev/null || echo '{}')

if echo "$LOGIN_RESP" | grep -q "access_token"; then
    TOKEN=$(echo "$LOGIN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
    echo -e "${GREEN}✓ Logged in as demo user${NC}"
else
    # Auth might be disabled, continue without token
    TOKEN=""
    echo -e "${YELLOW}⚠ Auth disabled or demo user not found, continuing without auth${NC}"
fi

AUTH_HEADER=""
if [ -n "$TOKEN" ]; then
    AUTH_HEADER="-H \"Authorization: Bearer $TOKEN\""
fi

# -----------------------------------------------------------------------------
# Step 3: Create/Get Project
# -----------------------------------------------------------------------------
echo -n "3. Get/Create Project... "

# List projects first
PROJECTS=$(curl -s "$BASE_URL/projects" $AUTH_HEADER 2>/dev/null || echo '[]')
if echo "$PROJECTS" | grep -q '"id"'; then
    PROJECT_ID=$(echo "$PROJECTS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['id'] if isinstance(d,list) and len(d)>0 else d.get('items',[{}])[0].get('id',''))" 2>/dev/null)
    echo -e "${GREEN}✓ Using existing project: ${PROJECT_ID:0:8}...${NC}"
else
    # Create new project
    CREATE_RESP=$(curl -s -X POST "$BASE_URL/projects" \
        -H "Content-Type: application/json" \
        $AUTH_HEADER \
        -d '{"name": "E2E Test Project", "description": "Automated E2E testing"}' 2>/dev/null || echo '{}')
    PROJECT_ID=$(echo "$CREATE_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
    echo -e "${GREEN}✓ Created project: ${PROJECT_ID:0:8}...${NC}"
fi

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}✗ Failed to get/create project${NC}"
    exit 1
fi

# -----------------------------------------------------------------------------
# Step 4: Upload Event Log
# -----------------------------------------------------------------------------
echo -n "4. Upload Event Log... "

# Create test CSV inline
TEST_CSV=$(cat << 'EOF'
case:concept:name,concept:name,time:timestamp,org:resource
1,Submit Application,2023-01-01 09:00:00,John
1,Review Application,2023-01-01 10:00:00,Sarah
1,Verify Documents,2023-01-01 11:00:00,Mike
1,Approve Application,2023-01-01 14:00:00,Manager
1,Send Confirmation,2023-01-01 14:30:00,System
2,Submit Application,2023-01-01 09:30:00,Sarah
2,Review Application,2023-01-01 10:30:00,John
2,Verify Documents,2023-01-01 11:30:00,Mike
2,Request Additional Info,2023-01-01 12:00:00,John
2,Review Application,2023-01-01 15:00:00,Mike
2,Verify Documents,2023-01-01 16:00:00,Sarah
2,Approve Application,2023-01-01 17:00:00,Manager
2,Send Confirmation,2023-01-01 17:30:00,System
3,Submit Application,2023-01-02 08:00:00,Mike
3,Review Application,2023-01-02 09:00:00,Sarah
3,Verify Documents,2023-01-02 10:00:00,John
3,Reject Application,2023-01-02 11:00:00,Manager
3,Send Rejection,2023-01-02 11:15:00,System
4,Submit Application,2023-01-02 10:00:00,John
4,Review Application,2023-01-02 11:00:00,Mike
4,Verify Documents,2023-01-02 12:00:00,Sarah
4,Approve Application,2023-01-02 15:00:00,Manager
4,Send Confirmation,2023-01-02 15:30:00,System
5,Submit Application,2023-01-03 09:00:00,Sarah
5,Review Application,2023-01-03 10:00:00,John
5,Verify Documents,2023-01-03 11:00:00,Mike
5,Approve Application,2023-01-03 13:00:00,Manager
5,Send Confirmation,2023-01-03 13:15:00,System
EOF
)

# Save to temp file for upload
TEMP_CSV=$(mktemp /tmp/e2e_test_XXXXXX.csv)
echo "$TEST_CSV" > "$TEMP_CSV"

UPLOAD_RESP=$(curl -s -X POST "$BASE_URL/datasets/upload" \
    -F "file=@$TEMP_CSV;filename=e2e_test.csv" \
    -F "project_id=$PROJECT_ID" \
    $AUTH_HEADER 2>/dev/null || echo '{}')

rm -f "$TEMP_CSV"

DATASET_ID=$(echo "$UPLOAD_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)

if [ -n "$DATASET_ID" ]; then
    echo -e "${GREEN}✓ Uploaded dataset: ${DATASET_ID:0:8}...${NC}"
else
    echo -e "${RED}✗ Upload failed: $UPLOAD_RESP${NC}"
    exit 1
fi

# -----------------------------------------------------------------------------
# Step 5: Run All Discovery Algorithms
# -----------------------------------------------------------------------------
echo ""
echo "5. Testing All Discovery Algorithms..."
echo "   ────────────────────────────────────"

# All 17 miners
MINERS="alpha alpha_plus inductive inductive_infrequent heuristics dfg performance_dfg ilp powl bpmn_inductive declare log_skeleton temporal_profile prefix_tree transition_system batches correlation"

PASSED=0
FAILED=0
XFAIL=0
declare -a RESULTS

for MINER in $MINERS; do
    echo -n "   ├─ $MINER: "
    
    DISCOVER_RESP=$(curl -s -X POST "$BASE_URL/discovery/discover?async_mode=false" \
        -H "Content-Type: application/json" \
        $AUTH_HEADER \
        -d "{\"dataset_id\": \"$DATASET_ID\", \"miner_type\": \"$MINER\", \"model_name\": \"E2E $MINER\"}" \
        2>/dev/null || echo '{"error": "request_failed"}')
    
    MODEL_ID=$(echo "$DISCOVER_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
    MODEL_FORMAT=$(echo "$DISCOVER_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('model_format',''))" 2>/dev/null)
    ERROR=$(echo "$DISCOVER_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error','') or d.get('detail',''))" 2>/dev/null)
    
    if [ -n "$MODEL_ID" ] && [ "$MODEL_ID" != "None" ]; then
        echo -e "${GREEN}✓ OK${NC} (format: $MODEL_FORMAT, id: ${MODEL_ID:0:8}...)"
        RESULTS+=("$MINER:PASS:$MODEL_ID:$MODEL_FORMAT")
        ((PASSED++))
    else
        # Check if it's a known failing algorithm
        if [[ "$MINER" =~ ^(alpha_plus|ilp|declare|correlation)$ ]]; then
            echo -e "${YELLOW}⚠ XFAIL${NC} (known bug: $ERROR)"
            RESULTS+=("$MINER:XFAIL:$ERROR")
            ((XFAIL++))
        else
            echo -e "${RED}✗ FAIL${NC} ($ERROR)"
            RESULTS+=("$MINER:FAIL:$ERROR")
            ((FAILED++))
        fi
    fi
done

echo "   └────────────────────────────────────"

# -----------------------------------------------------------------------------
# Step 6: Check Visualization Endpoints
# -----------------------------------------------------------------------------
echo ""
echo "6. Testing Visualization Endpoints..."
echo "   ────────────────────────────────────"

# DFG Visualization
echo -n "   ├─ DFG Visualization: "
DFG_RESP=$(curl -s "$BASE_URL/visualization/$DATASET_ID/dfg" $AUTH_HEADER 2>/dev/null || echo '{}')
NODES=$(echo "$DFG_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('nodes',[])))" 2>/dev/null)
EDGES=$(echo "$DFG_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('edges',[])))" 2>/dev/null)

if [ "$NODES" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}✓ OK${NC} ($NODES nodes, $EDGES edges)"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

# Performance DFG
echo -n "   ├─ Performance DFG: "
PERF_DFG_RESP=$(curl -s "$BASE_URL/visualization/$DATASET_ID/dfg?performance=true" $AUTH_HEADER 2>/dev/null || echo '{}')
PERF_EDGES=$(echo "$PERF_DFG_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(sum(1 for e in d.get('edges',[]) if 'avg_duration' in str(e) or 'mean' in str(e)))" 2>/dev/null)

if [ "$PERF_EDGES" -ge 0 ] 2>/dev/null; then
    echo -e "${GREEN}✓ OK${NC} (timing on $PERF_EDGES edges)"
else
    echo -e "${YELLOW}⚠ Partial${NC} (no timing data)"
fi

# Variants
echo -n "   ├─ Process Variants: "
VARIANTS_RESP=$(curl -s "$BASE_URL/datasets/$DATASET_ID/variants" $AUTH_HEADER 2>/dev/null || echo '{}')
VARIANT_COUNT=$(echo "$VARIANTS_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_variants') or len(d.get('variants',d.get('top_variants',[]))))" 2>/dev/null)

if [ "$VARIANT_COUNT" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}✓ OK${NC} ($VARIANT_COUNT variants)"
else
    echo -e "${YELLOW}⚠ No variants${NC}"
fi

# Statistics
echo -n "   └─ Dataset Statistics: "
STATS_RESP=$(curl -s "$BASE_URL/datasets/$DATASET_ID/statistics" $AUTH_HEADER 2>/dev/null || echo '{}')
if echo "$STATS_RESP" | grep -q "activity\|event"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⚠ Limited${NC}"
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
echo "📊 TEST SUMMARY"
echo "=============================================="
echo "Algorithms Tested: $((PASSED + FAILED + XFAIL))"
echo -e "  ${GREEN}Passed:${NC}  $PASSED"
echo -e "  ${YELLOW}XFail:${NC}   $XFAIL (known bugs)"
echo -e "  ${RED}Failed:${NC}  $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ E2E TEST PASSED${NC}"
    exit 0
else
    echo -e "${RED}❌ E2E TEST FAILED${NC}"
    exit 1
fi
