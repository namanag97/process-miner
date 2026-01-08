# Part 3: Technical Audit

**Feature-by-Feature Deep Dive**
**Date:** January 8, 2026

---

## Audit Methodology

- Traced every frontend component to backend endpoint
- Verified API request/response contracts
- Identified schema mismatches
- Tested data flow end-to-end
- Documented all issues with severity

---

## 1. Upload & Ingestion Pipeline

### Overview
Multi-step wizard for uploading event logs (CSV, Excel, XES) and preparing them for process mining.

### Flow Diagram

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Upload     │ → │   Sheets     │ → │  Configure   │ → │   Mapping    │ → │  Finalize    │
│   (P0-08)    │   │   (P0-01)    │   │   (P0-07)    │   │     ✅       │   │     ✅       │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

### Component Status

| Component | File | Status | Issue |
|-----------|------|--------|-------|
| UploadStep | `upload-wizard/components/steps/UploadStep.tsx` | ✅ Works | - |
| SheetsStep | Auto-skip logic | ❌ Broken | P0-01: Missing endpoint |
| ConfigureStep | `ConfigureStep.tsx` | ❌ Broken | P0-07: Wrong response |
| MapDataStep | `MapDataStep.tsx` | ✅ Works | - |
| FinalizeStep | `FinalizeStep.tsx` | ✅ Works | - |

### API Endpoints

| Endpoint | Method | Exists | Issue |
|----------|--------|--------|-------|
| `/datasets/` | POST | ✅ | Works for direct upload |
| `/datasets/presign` | POST | ✅ | Works |
| `/datasets/{id}/validate` | POST | ✅ | Doesn't trigger for direct |
| `/datasets/{id}/sheets` | GET | ❌ | **MISSING** |
| `/datasets/{id}/preview` | POST | ✅ | Wrong response format |
| `/datasets/{id}/mapping` | POST | ✅ | Works |
| `/datasets/{id}/ingest` | POST | ✅ | Works |

### Critical Issues

#### P0-01: Missing `/sheets` Endpoint
```
Frontend expects: GET /api/v1/datasets/{id}/sheets
Response needed: { dataset_id, filename, sheets: [{ name, index, row_count }] }
Backend status: NOT IMPLEMENTED
Impact: Excel file uploads fail completely
Fix: Create endpoint in upload.py
```

#### P0-07: Preview API Wrong Format
```
Frontend expects:
  { columns: [...], rows: [...], encoding, total_rows }

Backend returns:
  { sample_events: [...], parse_errors: [...], total_rows }

Impact: Configure step can't render
Fix: Update PreviewResponse schema
```

#### P0-08: Column Detection Not Triggered
```
Issue: dispatch_workflow("validate_uploaded_file") only called for presigned
Location: upload.py:286-297
Impact: Direct uploads never detect columns
Fix: Call validation for all upload paths
```

---

## 2. Process Discovery

### Overview
Runs PM4Py algorithms to discover process models from event logs.

### Flow Diagram

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Algorithm   │ → │   Request    │ → │  Job Exec    │ → │  Visualize   │
│   Selector   │   │   (P0-03)    │   │     ✅       │   │     ✅       │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

### Component Status

| Component | File | Status | Issue |
|-----------|------|--------|-------|
| DiscoveryPage | `discovery/pages/DiscoveryPage.tsx` | ✅ Works | - |
| AnalysisModeSelector | `AnalysisModeSelector.tsx` | ⚠️ Partial | P1-10: Bypasses SDK |
| ModelList | `ModelList.tsx` | ✅ Works | - |
| GraphViewer | `GraphViewer.tsx` | ✅ Works | - |
| JobStatusPanel | `JobStatusPanel.tsx` | ✅ Works | - |

### API Endpoints

| Endpoint | Method | Exists | Issue |
|----------|--------|--------|-------|
| `/discovery/miners` | GET | ✅ | P1-07: Bare array response |
| `/discovery/discover` | POST | ✅ | P0-03: Schema mismatch |
| `/discovery/models` | GET | ✅ | Works |
| `/discovery/models/{id}` | GET | ✅ | P1-06: Response format |
| `/analyses/metadata` | GET | ✅ | Works |

### Critical Issues

#### P0-03: Discovery Schema Mismatch
```
Backend field: miner_type
Test sends: algorithm
Response has: miner_type, model_format
Test expects: model_id, algorithm, format

Impact: Discovery requests fail
Fix: Standardize on miner_type everywhere
```

#### P0-04: Wrong DB Session
```
Location: discovery/router.py:52
Code: db: ReadDBSession
Used for: db.add(process_model)
Impact: Database inserts silently fail
Fix: Change to WriteDBSession
```

#### P1-07: Bare Array Response
```
Backend returns: [MinerInfo, MinerInfo, ...]
Frontend expects: { "algorithms": [...] }
Impact: Frontend may not parse correctly
Fix: Wrap in AlgorithmListResponse
```

---

## 3. Analytics

### Overview
Performance analytics: bottlenecks, cycle times, throughput, rework detection.

### Component Status

| Tab | Component | Status | Issue |
|-----|-----------|--------|-------|
| Performance | PerformanceTab.tsx | ❌ Broken | P0-02, P1-01, P1-02 |
| Conformance | ConformanceTab.tsx | ❌ Broken | P0-05 |
| Rework | ReworkTab.tsx | ❌ Broken | P0-06 |
| Resources | ResourcesTab.tsx | ✅ Works | - |
| Variants | (in explorer) | ✅ Works | - |

### API Endpoints

| Endpoint | Method | Exists | Issue |
|----------|--------|--------|-------|
| `/analytics/.../performance` | GET | ❌ | **MISSING** |
| `/analytics/.../bottlenecks` | GET | ✅ | P1-02: Service time = 0 |
| `/analytics/.../cycle-time` | GET | ✅ | P1-01: Percentiles = 0 |
| `/analytics/.../throughput` | GET | ✅ | Works |
| `/analytics/.../rework` | GET | ✅ | P0-06: Field names |
| `/analytics/.../variants` | GET | ✅ | Works |

### Critical Issues

#### P0-02: Missing Performance Endpoint
```
Frontend calls: GET /api/v1/analytics/datasets/{id}/performance
Backend status: NOT IMPLEMENTED

Individual endpoints exist but not aggregated:
  - /bottlenecks ✅
  - /cycle-time ✅
  - /throughput ✅

Options:
  A) Create aggregate endpoint (recommended)
  B) Update frontend to call individual endpoints
```

#### P0-06: ReworkTab Field Name Mismatch
```
Backend returns (snake_case):
  {
    "rework_activities": [...],
    "total_rework_cases": 100,
    "rework_percentage": 15.5
  }

Frontend expects (camelCase):
  {
    "reworkActivities": [...],
    "totalReworkCases": 100,
    "reworkPercentage": 15.5
  }

Impact: Rework tab shows empty
Fix: Add transformation layer
```

#### P1-01: Percentiles Hardcoded to 0
```
Location: analytics/router.py:107-109
Code:
  percentile_25_seconds=0,
  percentile_75_seconds=0,
  percentile_95_seconds=0

Impact: P25, P75, P95 always show 0%
Fix: Map actual values from query result
```

---

## 4. Conformance Checking

### Overview
Compares process execution against discovered models.

### Component Status

| Component | File | Status | Issue |
|-----------|------|--------|-------|
| ConformanceTab | `ConformanceTab.tsx` | ❌ Broken | P0-05 |
| Conformance API | `conformance/router.py` | ✅ Works | - |
| Conformance Service | `conformance/service.py` | ✅ Works | - |

### API Endpoints

| Endpoint | Method | Exists | Works |
|----------|--------|--------|-------|
| `/conformance/check` | POST | ✅ | ✅ |
| `/conformance/methods` | GET | ✅ | ✅ |
| `/conformance/diagnostics/{ds}/{model}` | GET | ✅ | ⚠️ Runs twice |
| `/conformance/quality/{ds}/{model}` | GET | ✅ | ⚠️ Null handling |

### Critical Issue

#### P0-05: Hardcoded Model ID
```
Location: ConformanceTab.tsx:65
Code: modelId: 'default'

Impact: Always returns 404 (no model named 'default')
User never sees conformance results

Fix:
  1. Fetch available models first
  2. Use models[0].id or let user select
  3. Show "No model" message if none found
```

---

## 5. AI Assistant

### Overview
Chat interface for natural language process analysis queries.

### Component Status

| Component | Status | Issue |
|-----------|--------|-------|
| Chat UI | ✅ Works | Clean interface |
| Send Message | ✅ Works | API connected |
| Context Injection | ✅ Works | Analytics data passed |
| LLM Response | ❌ Stub | P1-04, P1-05 |

### API Endpoints

| Endpoint | Method | Exists | Works |
|----------|--------|--------|-------|
| `/ai/chat` | POST | ✅ | Returns stub responses |
| `/ai/capabilities` | GET | ✅ | Works |

### Issues

#### P1-04: AI Chat in Stub Mode
```
Location: ai/service.py:40-48
Code: use_real_llm = False (effectively)

Condition for real LLM:
  - OPENROUTER_API_KEY set AND
  - AI_CHAT_LIVE_MODE=true

Impact: Returns pattern-matched responses, not real AI
```

#### P1-05: OpenRouter Not Implemented
```
Location: ai/service.py:79-91
Method: _call_openrouter()

Current code:
  logger.info("openrouter_call_placeholder")
  return self._generate_stub_response(...)

Impact: Even with API key, LLM not actually called
Fix: Implement HTTP call to OpenRouter API
```

---

## 6. Explorer

### Overview
Interactive process visualization with DFG, variants, and filtering.

### Component Status

| Component | Status | Issue |
|-----------|--------|-------|
| CytoscapeCanvas | ✅ Works | Graph renders correctly |
| ActivitiesPanel | ✅ Works | - |
| VariantPanel | ✅ Works | - |
| FilterPanel | ⚠️ UI Only | P1-08: No backend |
| Export PNG | ✅ Works | - |
| Export CSV | ✅ Works | - |

### Issues

#### P1-08: Filters Are UI-Only
```
Location: ExplorerDetailPage.tsx:585

Current behavior:
  - User applies filter
  - UI shows filter tags
  - Data NOT actually filtered (no API call)

Impact: Filters are cosmetic only
Fix: Implement filter parameters in backend API
```

---

## 7. Navigation & Routing

### Route Coverage

| Route | Component | Status |
|-------|-----------|--------|
| `/` | LandingPage | ✅ |
| `/login` | LoginPage | ✅ |
| `/workspace` | ProjectsListPage | ✅ |
| `/workspace/:projectId` | ProjectDetailPage | ✅ |
| `/workspace/:projectId/upload` | UploadWizardPage | ⚠️ |
| `/workspace/:projectId/data/:id/explorer` | ExplorerDetailPage | ✅ |
| `/workspace/:projectId/data/:id/discovery` | DiscoveryPage | ⚠️ |
| `/analytics` | AnalyticsPage | ⚠️ |
| `/ai/assistant` | AIAssistantPage | ⚠️ |

### Auth Status

```
Current: MVP mode - NO authentication guards
All routes accessible without login
User: Hardcoded as mvp-user-001
```

---

## Summary: Issues by Severity

### P0 - Critical (8 issues)
Platform unusable without fixing these.

| ID | Feature | Issue |
|----|---------|-------|
| P0-01 | Upload | Missing `/sheets` endpoint |
| P0-02 | Analytics | Missing `/performance` endpoint |
| P0-03 | Discovery | Schema mismatch |
| P0-04 | Discovery | Wrong DB session |
| P0-05 | Conformance | Hardcoded model ID |
| P0-06 | Analytics | Field name mismatch |
| P0-07 | Upload | Wrong preview format |
| P0-08 | Upload | Column detection missing |

### P1 - High (12 issues)
Core features broken or significantly degraded.

### P2 - Medium (14 issues)
UX issues and data quality problems.

### P3 - Low (10 issues)
Polish and cleanup items.

---

**Previous:** [02_COMPETITIVE_ANALYSIS.md](./02_COMPETITIVE_ANALYSIS.md)
**Next:** [04_FIX_PRIORITY_LIST.md](./04_FIX_PRIORITY_LIST.md)
