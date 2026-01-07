---
description: Design and run E2E tests for the Temporal workflow system
---

# Temporal Workflow E2E Testing

You are a Senior QA Engineer tasked with designing and executing end-to-end tests for a Temporal-based workflow system. The system has been refactored to use Temporal as the single source of truth for all job states.

## System Context

### Architecture Overview
```
Frontend → API → Temporal Server → Workers → Database
           ↓
    /operations/{workflow_id}  ← Single source of truth
```

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/datasets/{id}/ingest` | POST | Start dataset ingestion workflow |
| `/api/v1/datasets/{id}/reingest` | POST | Re-ingest with updated mapping |
| `/api/v1/datasets/{id}/uploaded` | POST | Confirm S3 upload, trigger validation |
| `/api/v1/discovery/discover` | POST | Start process discovery workflow |
| `/api/v1/operations/{workflow_id}` | GET | Get workflow status (poll this!) |
| `/api/v1/operations/{workflow_id}/cancel` | POST | Cancel running workflow |
| `/api/v1/operations/{workflow_id}/result` | GET | Get final result |
| `/api/v1/operations` | GET | List all operations |

### Workflow Types
1. **DatasetIngestionWorkflowV2** - Parse CSV/XES files, insert events into database
2. **DatasetValidationWorkflowV2** - Validate uploaded file format
3. **ProcessDiscoveryWorkflowV2** - Discover process model from event log
4. **ConformanceCheckWorkflowV2** - Check log conformance against model

### Response Format (v2)
```json
{
  "id": "ingest-dataset-{uuid}",
  "workflow_id": "ingest-dataset-{uuid}",
  "poll_endpoint": "/api/v1/operations/ingest-dataset-{uuid}",
  "status": "pending"
}
```

### Operations Status Response
```json
{
  "workflow_id": "ingest-dataset-abc123",
  "status": "RUNNING",  // RUNNING, COMPLETED, FAILED, CANCELLED
  "progress": 45,
  "current_step": "processing_chunk_5_of_10",
  "started_at": "2026-01-07T10:00:00Z",
  "entity_type": "dataset",
  "entity_id": "abc123"
}
```

---

## Test Design Requirements

### 1. Curl-Based API Tests

Design curl commands to test each workflow end-to-end:

#### Test 1: Dataset Ingestion Flow
```bash
# Step 1: Upload a CSV file
curl -X POST http://localhost:8000/api/v1/datasets/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_data.csv" \
  -F "name=Test Dataset" \
  -F "project_id=$PROJECT_ID"

# Step 2: Submit column mapping
curl -X POST http://localhost:8000/api/v1/datasets/$DATASET_ID/mapping \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_id": "case_id", "activity": "activity", "timestamp": "timestamp"}'

# Step 3: Trigger ingestion
curl -X POST http://localhost:8000/api/v1/datasets/$DATASET_ID/ingest \
  -H "Authorization: Bearer $TOKEN"
# → Returns {"workflow_id": "ingest-dataset-xxx", "poll_endpoint": "..."}

# Step 4: Poll for completion
while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/operations/$WORKFLOW_ID \
    -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  echo "Status: $STATUS"
  [[ "$STATUS" == "COMPLETED" || "$STATUS" == "FAILED" ]] && break
  sleep 2
done

# Step 5: Verify dataset is READY
curl http://localhost:8000/api/v1/datasets/$DATASET_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.status'
# → Should be "ready"
```

#### Test 2: Discovery Flow
```bash
# Trigger discovery (async)
curl -X POST http://localhost:8000/api/v1/discovery/discover \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": "'$DATASET_ID'", "miner_type": "inductive", "model_name": "test_model"}'
# → Returns {"workflow_id": "discover-xxx-inductive", "poll_endpoint": "..."}

# Poll until complete
curl http://localhost:8000/api/v1/operations/$WORKFLOW_ID \
  -H "Authorization: Bearer $TOKEN"
```

#### Test 3: Workflow Cancellation
```bash
# Start a long workflow
RESP=$(curl -X POST http://localhost:8000/api/v1/datasets/$DATASET_ID/ingest \
  -H "Authorization: Bearer $TOKEN")
WORKFLOW_ID=$(echo $RESP | jq -r '.workflow_id')

# Wait a moment, then cancel
sleep 1
curl -X POST http://localhost:8000/api/v1/operations/$WORKFLOW_ID/cancel \
  -H "Authorization: Bearer $TOKEN"

# Verify cancelled status
curl http://localhost:8000/api/v1/operations/$WORKFLOW_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.status'
# → Should be "CANCELLED"
```

---

### 2. Test Scenarios to Cover

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | Upload + Ingest small CSV | Workflow completes, status=READY |
| 2 | Upload + Ingest large CSV (>10MB) | Uses chunked processing, progress updates visible |
| 3 | Ingest invalid CSV | Workflow fails with error message |
| 4 | Re-ingest after mapping change | Old events cleared, new events inserted |
| 5 | Discovery on ready dataset | Model created and saved |
| 6 | Discovery on non-ready dataset | Returns 400 error before starting |
| 7 | Cancel running workflow | Status becomes CANCELLED |
| 8 | Poll completed workflow | Returns COMPLETED with result |
| 9 | List operations | Returns all user's workflows |
| 10 | Duplicate workflow start | Returns existing workflow ID (idempotent) |

---

### 3. Frontend Hook Tests

Test the React hooks in a browser context:

```tsx
// Test useOperationPolling hook
import { useOperationPolling } from '@/api/hooks';

function TestPolling({ workflowId }) {
  const { status, progress, currentStep, isComplete, error } = useOperationPolling(workflowId, {
    pollInterval: 1000,
    onComplete: (op) => console.log('Complete!', op),
    onError: (err) => console.error('Failed!', err),
  });

  return (
    <div>
      <p>Status: {status}</p>
      <p>Progress: {progress}%</p>
      <p>Step: {currentStep}</p>
    </div>
  );
}
```

---

### 4. Failure Mode Tests

Test these failure scenarios:

1. **Temporal Server Down**: API should return 503 with helpful error
2. **Worker Crash Mid-Activity**: Workflow should resume on worker restart
3. **Database Connection Lost**: Activity should fail, workflow should retry
4. **Cancellation During Activity**: Should cancel gracefully
5. **Timeout Exceeded**: Workflow should fail with timeout error

---

### 5. Test Data Requirements

Create test fixtures:
- `small_valid.csv` - 100 rows, valid format
- `large_valid.csv` - 100,000 rows, chunked processing
- `invalid_encoding.csv` - Binary data (should fail validation)
- `missing_columns.csv` - Missing required columns
- `xes_sample.xes` - Valid XES event log

---

## Execution Instructions

1. **Prerequisites**
   - Backend running: `make dev`
   - Temporal server running: `/start_temporal`
   - Frontend running: `npm start`
   - Auth token obtained: `POST /api/v1/auth/login`

2. **Run curl tests**
   ```bash
   # Set environment
   export TOKEN="your-jwt-token"
   export BASE_URL="http://localhost:8000"
   export PROJECT_ID="your-project-id"
   
   # Run test script
   ./tests/e2e/test_temporal_workflows.sh
   ```

3. **Run browser tests**
   - Open DevTools console
   - Navigate to upload page
   - Monitor network tab for /operations calls
   - Verify progress bar updates

4. **Verify Temporal UI**
   - Open http://localhost:8233 (Temporal Web UI)
   - Check workflow histories
   - Verify activities logged correctly

---

## Success Criteria

✅ All workflows complete within expected timeframes
✅ Progress updates visible via /operations endpoint
✅ Cancellation works at any point
✅ Failures are properly reported with actionable messages
✅ Duplicate starts are idempotent
✅ Frontend polling works smoothly without excessive requests
✅ Temporal history shows expected event sequence
