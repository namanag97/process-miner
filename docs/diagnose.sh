#!/bin/bash
# DIAGNOSTIC SCRIPT - Find what's actually broken
# Run this to identify exactly where the visualization pipeline fails

echo "=========================================="
echo "  PROCESS MINING MVP DIAGNOSTIC"
echo "=========================================="
echo ""

BASE="http://localhost:8001/api/v1"
FRONTEND_DIR="/Users/namanagarwal/system/frontend-new"
BACKEND_DIR="/Users/namanagarwal/system/backend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}✓ $1${NC}"; }
fail() { echo -e "${RED}✗ $1${NC}"; }
warn() { echo -e "${YELLOW}! $1${NC}"; }

echo "--- PHASE 1: INFRASTRUCTURE ---"
echo ""

# Check backend
if curl -s "http://localhost:8001/health/live" | grep -q "healthy"; then
    pass "Backend running on port 8001"
else
    fail "Backend NOT running"
    echo "  → Start: cd $BACKEND_DIR/src && ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001"
    exit 1
fi

# Check frontend
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:4200" | grep -q "200"; then
    pass "Frontend running on port 4200"
else
    warn "Frontend may not be running (or returns non-200)"
    echo "  → Start: cd $FRONTEND_DIR && npm start"
fi

echo ""
echo "--- PHASE 2: AUTHENTICATION ---"
echo ""

# Get token
TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' 2>/dev/null | jq -r '.access_token // empty')

if [ -n "$TOKEN" ]; then
    pass "Auth working - got token"
else
    fail "Auth BROKEN - cannot get token"
    echo "  → Check: src/api/routes/auth.py"
    echo "  → Check: Database has seeded users"
    exit 1
fi

echo ""
echo "--- PHASE 3: DATA ---"
echo ""

# Find a ready dataset
DATASETS=$(curl -s "$BASE/datasets/" -H "Authorization: Bearer $TOKEN" 2>/dev/null)
READY_DATASET=$(echo "$DATASETS" | jq -r '.items[] | select(.status=="ready") | .id' | head -1)
ANY_DATASET=$(echo "$DATASETS" | jq -r '.items[0].id // empty')
DATASET_COUNT=$(echo "$DATASETS" | jq '.items | length')

echo "  Found $DATASET_COUNT datasets"

if [ -n "$READY_DATASET" ]; then
    pass "Found READY dataset: $READY_DATASET"
    DATASET_ID="$READY_DATASET"
elif [ -n "$ANY_DATASET" ]; then
    warn "No READY datasets, using: $ANY_DATASET"
    STATUS=$(echo "$DATASETS" | jq -r '.items[0].status')
    echo "  → Dataset status: $STATUS"
    echo "  → May need to complete ingestion first"
    DATASET_ID="$ANY_DATASET"
else
    fail "No datasets found"
    echo "  → Upload a CSV first via the UI or API"
    exit 1
fi

echo ""
echo "--- PHASE 4: VISUALIZATION ENDPOINT ---"
echo ""

# Test visualization endpoint
VIZ_RESPONSE=$(curl -s "$BASE/visualization/$DATASET_ID/dfg" \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null)

# Check if it's valid JSON
if echo "$VIZ_RESPONSE" | jq . > /dev/null 2>&1; then
    # Check for error
    if echo "$VIZ_RESPONSE" | jq -e '.detail' > /dev/null 2>&1; then
        fail "Visualization endpoint returned error"
        echo "  Error: $(echo "$VIZ_RESPONSE" | jq -r '.detail')"
        echo "  → Fix: src/api/routes/visualization.py"
    else
        NODE_COUNT=$(echo "$VIZ_RESPONSE" | jq '.nodes | length // 0')
        EDGE_COUNT=$(echo "$VIZ_RESPONSE" | jq '.edges | length // 0')
        
        if [ "$NODE_COUNT" -gt 0 ]; then
            pass "Visualization endpoint returns data: $NODE_COUNT nodes, $EDGE_COUNT edges"
            echo ""
            echo "  Sample node: $(echo "$VIZ_RESPONSE" | jq '.nodes[0]')"
            echo "  Sample edge: $(echo "$VIZ_RESPONSE" | jq '.edges[0]')"
        else
            fail "Visualization endpoint returns EMPTY data"
            echo "  → Check dataset has events"
            echo "  → Check PM4Py is discovering properly"
        fi
    fi
else
    fail "Visualization endpoint returned invalid response"
    echo "  Response: $VIZ_RESPONSE"
    echo "  → Check: src/api/routes/visualization.py"
fi

echo ""
echo "--- PHASE 5: BACKEND CODE CHECK ---"
echo ""

# Check visualization route exists
if [ -f "$BACKEND_DIR/src/api/routes/visualization.py" ]; then
    pass "visualization.py exists"
    
    # Check for dfg endpoint
    if grep -q "def.*dfg\|/dfg" "$BACKEND_DIR/src/api/routes/visualization.py"; then
        pass "DFG endpoint defined in visualization.py"
    else
        fail "DFG endpoint NOT found in visualization.py"
        echo "  → Need to add GET /{dataset_id}/dfg endpoint"
    fi
else
    fail "visualization.py NOT FOUND"
    echo "  → Create: src/api/routes/visualization.py"
fi

# Check if router is registered
if grep -q "visualization" "$BACKEND_DIR/src/api/main.py"; then
    pass "Visualization router registered in main.py"
else
    warn "Visualization router may not be registered in main.py"
    echo "  → Add: app.include_router(visualization.router)"
fi

echo ""
echo "--- PHASE 6: FRONTEND CODE CHECK ---"
echo ""

# Check Explorer component exists
EXPLORER_FILE=$(find "$FRONTEND_DIR/src" -name "*[Ee]xplorer*.tsx" -o -name "*[Ee]xplorer*.jsx" 2>/dev/null | head -1)

if [ -n "$EXPLORER_FILE" ]; then
    pass "Explorer component found: $EXPLORER_FILE"
    
    # Check if it fetches visualization data
    if grep -q "visualization\|dfg" "$EXPLORER_FILE"; then
        pass "Explorer references visualization/dfg endpoint"
    else
        warn "Explorer may not be fetching visualization data"
        echo "  → Check useEffect and API calls in: $EXPLORER_FILE"
    fi
    
    # Check for cytoscape
    if grep -q "cytoscape\|Cytoscape" "$EXPLORER_FILE"; then
        pass "Explorer uses Cytoscape"
    else
        warn "Explorer may not use Cytoscape"
        echo "  → Check rendering library"
    fi
else
    fail "Explorer component NOT FOUND"
    echo "  → Create: src/pages/Explorer/Explorer.tsx"
fi

# Check ProcessMap component
PROCESSMAP_FILE=$(find "$FRONTEND_DIR/src" -name "*[Pp]rocess*[Mm]ap*.tsx" 2>/dev/null | head -1)

if [ -n "$PROCESSMAP_FILE" ]; then
    pass "ProcessMap component found: $PROCESSMAP_FILE"
else
    warn "ProcessMap component not found"
    echo "  → May be inline in Explorer or named differently"
fi

# Check cytoscape installed
if grep -q '"cytoscape"' "$FRONTEND_DIR/package.json"; then
    pass "Cytoscape is in package.json"
else
    fail "Cytoscape NOT in package.json"
    echo "  → Run: cd $FRONTEND_DIR && npm install cytoscape cytoscape-dagre"
fi

echo ""
echo "--- PHASE 7: FRONTEND API CONFIG ---"
echo ""

# Check API service
API_FILE=$(find "$FRONTEND_DIR/src" -name "api.ts" -o -name "api.js" 2>/dev/null | head -1)

if [ -n "$API_FILE" ]; then
    pass "API service found: $API_FILE"
    
    if grep -q "localhost:8001" "$API_FILE"; then
        pass "API URL points to localhost:8001"
    else
        warn "API URL may not point to localhost:8001"
        echo "  → Check baseURL in: $API_FILE"
    fi
else
    warn "Could not find api.ts/js"
fi

# Check .env
if [ -f "$FRONTEND_DIR/.env" ]; then
    pass ".env file exists"
    cat "$FRONTEND_DIR/.env"
else
    warn ".env file not found"
    echo "  → Create $FRONTEND_DIR/.env with:"
    echo "  VITE_API_URL=http://localhost:8001/api/v1"
fi

echo ""
echo "=========================================="
echo "  SUMMARY"
echo "=========================================="
echo ""
echo "Dataset ID for testing: $DATASET_ID"
echo ""
echo "Test visualization endpoint:"
echo "  curl -s '$BASE/visualization/$DATASET_ID/dfg' -H 'Authorization: Bearer $TOKEN' | jq ."
echo ""

if [ "$NODE_COUNT" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}BACKEND IS WORKING${NC} - Problem is likely in frontend rendering"
    echo ""
    echo "Next steps:"
    echo "1. Open http://localhost:4200"
    echo "2. Navigate to Explorer for dataset: $DATASET_ID"
    echo "3. Open browser console (F12)"
    echo "4. Look for errors or missing API calls"
    echo "5. Check ProcessMap container has height"
else
    echo -e "${RED}BACKEND IS NOT RETURNING DATA${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Check src/api/routes/visualization.py has DFG endpoint"
    echo "2. Check PM4Py is installed and working"
    echo "3. Check event log can be loaded from dataset"
    echo "4. Add debug prints to trace the issue"
fi

echo ""
echo "=========================================="
