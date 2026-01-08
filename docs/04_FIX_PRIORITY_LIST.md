# Part 4: Fix Priority List

**All Issues Ranked by Severity**
**Date:** January 8, 2026

---

## P0: Critical Blockers

**Total: 8 issues | Estimated Fix Time: ~15 hours**

These must be fixed first. Platform is unusable without them.

---

### P0-01: Missing `/datasets/{id}/sheets` Endpoint

**Feature:** Upload Wizard
**Impact:** Excel file uploads completely fail
**Time to Fix:** 2 hours

**Current State:**
- Frontend calls: `GET /api/v1/datasets/{id}/sheets`
- Backend: Endpoint does not exist
- Result: Wizard hangs on Sheets step for Excel files

**Fix:**
```python
# backend/src/features/process_mining/datasets/api/upload.py

@router.get("/{dataset_id}/sheets", response_model=SheetsResponse)
async def get_sheets(
    dataset_id: UUID,
    db: ReadDBSession,
) -> SheetsResponse:
    """Get sheets for multi-sheet files (Excel)."""
    dataset = await get_dataset_or_404(db, dataset_id)

    # Load file and detect sheets
    storage = get_storage()
    file_path = await storage.get_file(dataset.storage_key)

    sheets = detect_sheets(file_path, dataset.source_format)

    return SheetsResponse(
        dataset_id=dataset_id,
        filename=dataset.source_file,
        sheets=sheets
    )
```

---

### P0-02: Missing `/analytics/datasets/{id}/performance` Endpoint

**Feature:** Analytics Page
**Impact:** Performance tab shows all "N/A", summary cards empty
**Time to Fix:** 4 hours

**Current State:**
- Frontend calls: `GET /api/v1/analytics/datasets/{id}/performance`
- Backend: Endpoint does not exist
- Individual endpoints exist: `/bottlenecks`, `/cycle-time`, `/throughput`

**Option A: Create Aggregate Endpoint (Recommended)**
```python
# backend/src/features/process_mining/analytics/router.py

@router.get("/datasets/{dataset_id}/performance")
async def get_performance(dataset_id: UUID) -> PerformanceResponse:
    """Aggregated performance metrics."""
    bottlenecks = await get_bottlenecks(dataset_id)
    cycle_time = await get_cycle_time(dataset_id)
    throughput = await get_throughput(dataset_id)

    return PerformanceResponse(
        dataset_id=dataset_id,
        cycle_time=cycle_time,
        throughput=throughput,
        top_bottlenecks=bottlenecks[:5]
    )
```

**Option B: Update Frontend**
```typescript
// frontend-new/src/features/analytics/pages/AnalyticsPage.tsx

// Instead of:
const perfData = await sdk.analytics.getPerformance(datasetId);

// Do:
const [bottlenecks, cycleTime, throughput] = await Promise.all([
  sdk.analytics.getBottlenecks(datasetId),
  sdk.analytics.getCycleTime(datasetId),
  sdk.analytics.getThroughput(datasetId),
]);
```

---

### P0-03: Discovery Schema Mismatch (`miner_type` vs `algorithm`)

**Feature:** Process Discovery
**Impact:** Discovery requests fail, tests can't pass
**Time to Fix:** 1 hour

**Current State:**
- Backend expects: `miner_type` field
- Tests send: `algorithm` field
- Response has: `miner_type`, `model_format`
- Tests expect: `model_id`, `algorithm`, `format`

**Fix:**
```python
# 1. Update test to use correct field name
# backend/tests/api/test_discovery.py

response = client.post("/api/v1/discovery/discover", json={
    "dataset_id": str(seeded_dataset_ready.id),
    "miner_type": "inductive",  # Changed from "algorithm"
})

# 2. Verify response schema matches
assert "id" in data  # Changed from "model_id"
assert "miner_type" in data  # Changed from "algorithm"
```

---

### P0-04: Discovery Router Uses ReadDBSession for Writes

**Feature:** Process Discovery
**Impact:** Database inserts silently fail - models not saved
**Time to Fix:** 30 minutes

**Location:** `backend/src/features/process_mining/discovery/router.py:52`

**Current Code:**
```python
async def discover(
    request: DiscoverRequest,
    db: ReadDBSession,  # ❌ Wrong session type
):
    ...
    db.add(process_model)  # This silently fails
    await db.flush()
```

**Fix:**
```python
async def discover(
    request: DiscoverRequest,
    db: WriteDBSession,  # ✅ Correct session type
):
    ...
    db.add(process_model)
    await db.commit()  # Use commit, not just flush
```

---

### P0-05: Conformance Tab Hardcodes `modelId='default'`

**Feature:** Conformance Checking
**Impact:** Always returns 404 (no model named 'default')
**Time to Fix:** 1 hour

**Location:** `frontend-new/src/features/analytics/components/ConformanceTab.tsx:65`

**Current Code:**
```typescript
await sdk.conformance.check({
  datasetId,
  modelId: 'default',  // ❌ This model doesn't exist
  method: 'token_replay',
});
```

**Fix:**
```typescript
// 1. Fetch available models
const models = await sdk.discovery.listModels(datasetId);

// 2. Handle no models case
if (models.length === 0) {
  setNoModelsMessage("Discover a model first");
  return null;
}

// 3. Use first (or best) model
const modelId = models[0].id;

const result = await sdk.conformance.check({
  datasetId,
  modelId,
  method: 'token_replay',
});
```

---

### P0-06: ReworkTab Field Name Mismatch

**Feature:** Analytics - Rework
**Impact:** Rework data never displays, table shows empty
**Time to Fix:** 1 hour

**Current State:**
- Backend returns: `rework_activities`, `total_rework_cases` (snake_case)
- Frontend expects: `reworkActivities`, `totalReworkCases` (camelCase)

**Location:** `frontend-new/src/features/analytics/components/ReworkTab.tsx`

**Fix Option A: Transform in Frontend**
```typescript
// Add transformation when receiving data
const transformedData = {
  reworkActivities: data.rework_activities?.map(a => ({
    activity: a.activity,
    reworkCount: a.rework_count,
    casesWithRework: a.cases_with_rework,
    reworkPercentage: a.rework_percentage,
  })),
  totalReworkCases: data.total_rework_cases,
  reworkPercentage: data.rework_percentage,
};
```

**Fix Option B: Update Backend Response**
```python
# Use Pydantic alias
class ReworkResponse(BaseModel):
    activity: str
    rework_count: int = Field(alias="reworkCount")
    cases_with_rework: int = Field(alias="casesWithRework")

    class Config:
        populate_by_name = True
```

---

### P0-07: Upload Preview API Returns Wrong Fields

**Feature:** Upload Wizard - Configure Step
**Impact:** Configure step can't render, wizard hangs
**Time to Fix:** 2 hours

**Current State:**
- Backend returns: `sample_events`, `parse_errors`
- Frontend expects: `columns`, `rows`, `encoding`, `total_rows`

**Location:** `backend/src/features/process_mining/datasets/api/mapping.py:420`

**Fix:**
```python
@router.post("/{dataset_id}/preview", response_model=PreviewResponse)
async def get_preview(...):
    # Current response
    # return PreviewResponse(
    #     sample_events=sample_events,
    #     parse_errors=parse_errors,
    # )

    # Fixed response
    return PreviewResponse(
        dataset_id=dataset_id,
        columns=[
            {"name": col, "dtype": detect_dtype(col, df)}
            for col in df.columns
        ],
        rows=df.head(limit).to_dict('records'),
        total_rows=len(df),
        encoding="utf-8",
        has_header=True,
    )
```

---

### P0-08: Column Detection Not Triggered for Direct Uploads

**Feature:** Upload Wizard
**Impact:** Columns never detected, mapping step fails
**Time to Fix:** 3 hours

**Current State:**
- Presigned uploads call: `dispatch_workflow("validate_uploaded_file")`
- Direct uploads: Don't trigger validation

**Location:** `backend/src/features/process_mining/datasets/api/upload.py`

**Fix:**
```python
@router.post("/", response_model=DatasetResponse)
async def upload_dataset(file: UploadFile, ...):
    # ... existing upload code ...

    # Add validation trigger
    await dispatch_workflow(
        workflow_type="validate_uploaded_file",
        args={"dataset_id": str(dataset.id)},
    )

    return DatasetResponse(...)
```

---

## P1: High Priority Issues

**Total: 12 issues | Estimated Fix Time: ~38 hours**

---

### P1-01: Cycle Time Percentiles Hardcoded to 0
**Location:** `analytics/router.py:107-109`
**Time:** 30 minutes
```python
# Change from:
percentile_25_seconds=0,
percentile_75_seconds=0,

# To:
percentile_25_seconds=result.percentile_25_seconds,
percentile_75_seconds=result.percentile_75_seconds,
```

### P1-02: Bottleneck Service Time Hardcoded to 0
**Location:** `analytics/router.py:72`
**Time:** 1 hour
- Add service time calculation to DuckDB query

### P1-03: Bottleneck Activity Relationships Empty
**Location:** `analytics/router.py:76`
**Time:** 2 hours
- Add preceding/following activity queries

### P1-04: AI Chat in Stub Mode
**Location:** `ai/service.py:40-48`
**Time:** 4 hours
- Add environment variables to .env
- Enable live mode flag

### P1-05: OpenRouter LLM Not Implemented
**Location:** `ai/service.py:79-91`
**Time:** 8 hours
- Implement HTTP client for OpenRouter
- Add error handling and retries

### P1-06: Discovery Response Format Mismatch
**Location:** `discovery/router.py:180-186`
**Time:** 2 hours
- Standardize response schema with frontend

### P1-07: `/miners` Endpoint Returns Bare Array
**Location:** `discovery/router.py:39-42`
**Time:** 30 minutes
```python
# Wrap in response object
return AlgorithmListResponse(algorithms=[...])
```

### P1-08: Filters Are UI-Only
**Location:** `ExplorerDetailPage.tsx:585`
**Time:** 8 hours
- Implement filter parameters in backend
- Pass filters to visualization endpoints

### P1-09: Job Status Enum Mismatch
**Time:** 2 hours
- Normalize Celery vs Temporal status values

### P1-10: AnalysisModeSelector Bypasses SDK
**Location:** `AnalysisModeSelector.tsx:142-178`
**Time:** 4 hours
- Replace raw fetch() with SDK calls

### P1-11: Validation Workflow Missing
**Time:** 4 hours
- Implement validate_uploaded_file workflow

### P1-12: Diagnostics Endpoint Runs Conformance Twice
**Location:** `conformance/router.py:279-312`
**Time:** 2 hours
- Cache first result, reuse for diagnostics

---

## Quick Wins (< 1 hour each)

These can be done between larger tasks:

| Fix | Time | Code Change |
|-----|------|-------------|
| P1-01 Percentiles | 5 min | Change `0` to `result.value` |
| P1-07 Wrap array | 10 min | Add response wrapper |
| P0-05 Fetch models | 15 min | Add model list query |
| P2-04 Show N/A | 10 min | Change `?? 0` to null check |
| P3-01 Remove search | 5 min | Delete HTML element |
| P2-05 Remove stub | 5 min | Delete duplicate class |
| P3-08 Add export | 5 min | Update `__init__.py` |

---

## Fix Order Recommendation

### Week 1: Critical Path
1. P0-02: Performance endpoint/frontend
2. P0-06: ReworkTab transformation
3. P0-07: Preview API format
4. P0-03: Schema standardization
5. P0-04: WriteDBSession

### Week 2: Upload Flow
6. P0-01: Sheets endpoint
7. P0-08: Validation trigger
8. P1-11: Validation workflow
9. P2-02: Remove duplicate mapping
10. P2-03: Persist wizard state

### Week 3: Analytics
11. P1-01: Real percentiles
12. P1-02: Service times
13. P1-03: Activity relationships
14. P0-05: Model selection
15. P2-04: Null handling

### Week 4: Discovery & AI
16. P1-06: Response format
17. P1-07: Wrap array
18. P1-10: Use SDK
19. P1-04: Enable AI
20. P1-05: OpenRouter

---

**Previous:** [03_TECHNICAL_AUDIT.md](./03_TECHNICAL_AUDIT.md)
**Next:** [05_ROADMAP.md](./05_ROADMAP.md)
