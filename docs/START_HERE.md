# CLAUDE CODE: START HERE

## Your Mission
Fix the Process Mining MVP so the complete pipeline works:
```
Upload → Ingest → Discover → Visualize → Analyze
```

## Quick Start

### 1. Start Backend
```bash
cd /Users/namanagarwal/system/backend/src
../.venv/bin/python -m uvicorn api.main:app --reload --port 8001
```

### 2. Run This Test Script
```bash
cd /Users/namanagarwal/system/backend
cat > /tmp/test_mvp.sh << 'EOF'
#!/bin/bash
BASE="http://localhost:8001/api/v1"

# Auth
TOKEN=$(curl -s -X POST "$BASE/auth/login" -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token')
[ -z "$TOKEN" ] && echo "❌ AUTH FAILED" && exit 1
echo "✅ Auth: OK"

# Upload
DATASET_ID=$(curl -s -X POST "$BASE/datasets/" -H "Authorization: Bearer $TOKEN" \
  -F "file=@tests/data/insurance_small.csv" -F "name=Test" -F "project_id=mvp-proj-001" | jq -r '.id')
[ -z "$DATASET_ID" ] && echo "❌ UPLOAD FAILED" && exit 1
echo "✅ Upload: $DATASET_ID"

# Map + Ingest
curl -s -X POST "$BASE/datasets/$DATASET_ID/mapping" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"case_id_column":"case_id","activity_column":"activity","timestamp_column":"timestamp"}' > /dev/null
curl -s -X POST "$BASE/datasets/$DATASET_ID/ingest" -H "Authorization: Bearer $TOKEN" > /dev/null

for i in {1..20}; do
  STATUS=$(curl -s "$BASE/datasets/$DATASET_ID" -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  [ "$STATUS" = "ready" ] && break
  [ "$STATUS" = "failed" ] && echo "❌ INGEST FAILED" && exit 1
  sleep 1
done
[ "$STATUS" != "ready" ] && echo "❌ INGEST TIMEOUT" && exit 1
echo "✅ Ingest: ready"

# Discovery
MODEL_ID=$(curl -s -X POST "$BASE/discovery/discover" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d "{\"dataset_id\":\"$DATASET_ID\",\"algorithm\":\"inductive\"}" | jq -r '.model_id // .id')
[ -z "$MODEL_ID" ] && echo "❌ DISCOVERY FAILED" && exit 1
echo "✅ Discovery: $MODEL_ID"

# Visualization
NODES=$(curl -s "$BASE/visualization/$DATASET_ID/dfg" -H "Authorization: Bearer $TOKEN" | jq '.nodes | length')
[ "$NODES" -lt 1 ] && echo "❌ VIZ FAILED" && exit 1
echo "✅ Visualization: $NODES nodes"

# Analytics
VARIANTS=$(curl -s "$BASE/analytics/datasets/$DATASET_ID/variants" -H "Authorization: Bearer $TOKEN" | jq '.variants | length')
[ "$VARIANTS" -lt 1 ] && echo "❌ ANALYTICS FAILED" && exit 1
echo "✅ Analytics: $VARIANTS variants"

echo ""; echo "🎉 MVP WORKING!"
EOF
chmod +x /tmp/test_mvp.sh
/tmp/test_mvp.sh
```

### 3. Fix What Fails
When a step fails:
1. Check the backend terminal for Python traceback
2. Find the file:line causing the error
3. Fix the code
4. Re-run the test script
5. Repeat until all ✅

## Key Directories
```
src/api/routes/          # API endpoints
src/services/            # Business logic
src/domain/              # Core domain (PM4Py wrappers)
src/infrastructure/      # Database, storage
```

## Full Documentation
See `MVP_COMPLETE_FIX.md` for:
- Detailed test commands for each component
- PM4Py code examples
- Common fix patterns
- Complete verification script
