# ATLAS Bug Report & Improvement List
## Audit Results from Fictive Kin Design Studio

**Date:** December 2024
**Auditor:** Fictive Kin

---

# Existing Feature Inventory (Well Implemented)

## What's Already Built ✅

| Feature | File | Lines | Quality |
|---------|------|-------|---------|
| **Upload Wizard** | `pages/logs/UploadWizardPage.tsx` | 785 | Excellent - 4 steps, column detection, validation |
| **Process Explorer** | `features/explorer/pages/ExplorerDetailPage.tsx` | 753 | Excellent - DFG, variants, filtering, export |
| **Project Detail** | `features/projects/pages/ProjectDetailPage.tsx` | 172 | Good - upload + depot options |
| **Explorer Index** | `features/explorer/pages/ExplorerIndexPage.tsx` | 145 | Good - grid of logs |
| **Filter Panel** | `features/explorer/components/FilterPanel.tsx` | Exists | Good |
| **Variant Panel** | `features/explorer/components/VariantPanel.tsx` | Exists | Good |
| **Activity Details** | `features/explorer/components/ActivityDetailsPanel.tsx` | Exists | Good |
| **Process KPI Bar** | `features/explorer/components/ProcessKPIBar.tsx` | Exists | Good |
| **AI Assistant** | `features/ai/pages/AIAssistantPage.tsx` | 547 | Good - uses proper hooks |
| **Analytics Page** | `features/analytics/pages/AnalyticsPage.tsx` | 301 | OK - needs hook refactor |

---

# Critical Bugs (P0)

## BUG-001: PredictionsPage Uses Hardcoded Mock Data
**File:** `frontend-new/src/features/ai/pages/PredictionsPage.tsx`
**Lines:** 21-69

**Issue:** The entire page uses hardcoded mock data instead of real SDK calls:
```typescript
// Lines 21-69 - MOCK DATA, NOT CONNECTED TO BACKEND
const mockLogs = [
  { id: '1', name: 'Orders_2024.csv' },
  // ...
];
const mockPredictors = [
  {
    id: '1',
    name: 'Order Next Step',
    // ...
  },
];
```

**Impact:** Users cannot train or use real predictors. All data shown is fake.

**Fix Required:**
1. Replace `mockLogs` with `useProcesses()` hook
2. Replace `mockPredictors` with `useAIPredictors(selectedLogId)` hook
3. Wire up `handleTrain` to actual SDK `predictions.train()` call
4. Wire up `handleDelete` to actual SDK `predictions.delete()` call

---

## BUG-002: ConformanceTab Uses Hardcoded Model ID
**File:** `frontend-new/src/features/analytics/components/ConformanceTab.tsx`
**Line:** 71

**Issue:**
```typescript
// Line 71 - 'default' modelId doesn't exist
const result = await sdk.conformance.check({
  logId,
  modelId: 'default', // BUG: This won't work
  method: 'token_replay',
});
```

**Impact:** Conformance checking always fails because there's no model with ID 'default'.

**Fix Required:**
1. Fetch available models for the log using `sdk.discovery.listModels(logId)`
2. Let user select a model or auto-select the most recent one
3. Show proper error state when no models exist

---

## BUG-003: AnalyticsPage Inconsistent Hook Pattern
**File:** `frontend-new/src/features/analytics/pages/AnalyticsPage.tsx`
**Lines:** 38-68

**Issue:** Uses raw `useQuery` instead of feature hook factory:
```typescript
// Inconsistent with codebase pattern
const { data: logsData, isLoading: logsLoading, error: logsError } = useQuery({
  queryKey: ['processes'],
  queryFn: () => sdk.processes.list({ pageSize: 50 }),
});
```

**Impact:**
- Inconsistent query key management
- No automatic cache invalidation
- Harder to maintain

**Fix Required:**
Create `useAnalyticsProcesses`, `useAnalyticsPerformance`, `useAnalyticsRework` hooks in `src/features/analytics/hooks/index.ts`.

---

# High Priority Issues (P1)

## ~~BUG-004: Missing Upload Flow~~
**Status:** ✅ RESOLVED - Exists at `pages/logs/UploadWizardPage.tsx` (785 lines)

The upload wizard already has:
- File drag & drop with validation
- Column auto-detection
- Column mapping with suggestions
- Real upload progress tracking
- Processing stages indicator
- Timeout warnings

---

## BUG-005: Missing State Indicators in List Views
**Files:** `ExplorerIndexPage.tsx`, `ProjectsListPage.tsx`

**Issue:** While EventLog has `status` field in ORM, the list views don't show visual state indicators (UPLOADING, VALIDATING, READY, ERROR, ARCHIVED).

**Fix Required:**
Create `StateIndicator` component and add to log cards in list views.

---

## BUG-006: Variants Not Parseable from Backend
**File:** `frontend-new/src/features/explorer/` (implied from AGENT_CONTEXT.md)

**Issue:** Backend sends `activity_trace` as string "A → B → C", but frontend needs parsed array for visualization.

**From AGENT_CONTEXT.md:**
> "Variant activities parsing: Backend fix - Add activities: list[str] to VariantResponse"

**Impact:** Frontend must fragile-parse strings instead of using clean data.

**Fix Required:**
1. Add `activities: list[str]` field to `VariantResponse` in `backend/src/models/schemas.py`
2. Populate it in `backend/src/api/routers/processes.py` `get_variants` function

---

## BUG-007: FilterBuilder Component Missing
**Files:** None exist

**Issue:** The ontological model defines `FilterPreset` with complex `FilterCondition[]`, but there's no UI to build filters.

Current filtering is limited to search text box only.

**Fix Required:**
Create `FilterBuilder` component supporting:
- Time range filter
- Activity include/exclude
- Variant selection
- Case duration range
- Resource filter

---

# Medium Priority Issues (P2)

## BUG-008: AIInsightsPage Status Unknown
**File:** `frontend-new/src/features/ai/pages/AIInsightsPage.tsx`

**Issue:** Need to verify if this page uses proper hooks or has similar mock data issues.

**Action:** Review and update to use proper SDK hooks.

---

## BUG-009: Missing Organizational Mining UI
**Files:** ResourcesTab exists but minimal

**Issue:** The ontological model defines:
- `OrganizationalRole` - Discovered role clusters
- `HandoverNetwork` - Resource handover graph

But UI only has placeholder ResourcesTab.

**Fix Required:**
1. Create `HandoverNetwork` visualization component
2. Create `OrganizationalRole` list/cards
3. Connect to `/organizational/{logId}/social-network` endpoint

---

## BUG-010: Missing Root Cause Analysis
**Files:** None exist

**Issue:** Ontological model defines `RootCauseAnalysisResult` with `RootCauseFactor[]`, but no UI exists.

**Fix Required:**
1. Create backend endpoint for root cause analysis
2. Create `RootCauseTree` visualization component
3. Create analysis trigger flow

---

## BUG-011: Missing Simulation Support
**Files:** None exist

**Issue:** Ontological model defines:
- `SimulationModel` - Parameterized process model
- `SimulationRun` - Single simulation execution

But no UI or complete backend flow exists.

---

## BUG-012: OCEL Support Incomplete
**Files:** Partial backend support

**Issue:** Backend has OCPM router but frontend has no OCEL-specific pages.

**Fix Required:**
1. Create OCEL upload page
2. Create OCEL explorer with object-type selection
3. Create object relationship visualization

---

# Low Priority Issues (P3)

## BUG-013: Missing Dashboard Builder
**Files:** None exist

**Issue:** Ontological model defines `Dashboard` with `Widget[]` for custom dashboards, but no builder UI exists.

---

## BUG-014: Missing Alerting System
**Files:** None exist

**Issue:** Ontological model defines:
- `Alert` - Triggered notifications
- `ActionDefinition` - Automated responses
- `Trigger` - Condition triggers

But no UI exists.

---

## BUG-015: Missing Work Queue
**Files:** None exist

**Issue:** Ontological model defines `WorkQueue` and `WorkQueueItem` for case prioritization, but no UI exists.

---

# Code Quality Issues

## CQ-001: Duplicate formatDuration Function
**Files:**
- `frontend-new/src/features/ai/pages/AIAssistantPage.tsx:44-49`
- `libs/shared/design-system/src/utils/index.ts`

**Issue:** Local `formatDuration` function duplicates design system utility.

**Fix:** Remove local function, import from `@lumina/design-system`.

---

## CQ-002: Inconsistent Query Key Management
**Files:** Various

**Issue:** Some pages use:
- `['processes']` - flat key
- `['ai', 'processes', options]` - nested key
- `queryKeys.conformance.check(...)` - centralized keys

**Fix:** Standardize all query keys to use `queryKeys` from design system.

---

## CQ-003: Mixed State Management Patterns
**Files:** Various

**Issue:** Some pages use:
- `useState` + `useEffect` (old pattern)
- Raw `useQuery` (medium pattern)
- `createQueryHook` (new pattern)

**Fix:** Migrate all to `createQueryHook` pattern per FEATURE_BLUEPRINT.md.

---

## CQ-004: Missing Error Boundaries in Feature Pages
**Files:** Most feature pages

**Issue:** While `FeaturePage` handles loading/error states, individual sections within pages lack error boundaries.

**Fix:** Wrap complex sections in `ErrorBoundary` components.

---

# UI/UX Issues

## UX-001: No Loading Feedback for Long Operations
**Issue:** Training predictors, discovering models, conformance checking can take 10-60 seconds, but no progress indicators show.

**Fix:** Add `AsyncJobProgress` component that polls `/jobs/{id}` and shows progress.

---

## UX-002: Empty State Inconsistency
**Issue:** Empty states vary in messaging and actions across pages.

**Fix:** Standardize empty state messages per context:
- No logs: "Upload your first event log to get started"
- No models: "Discover a process model to unlock analytics"
- No predictions: "Train a predictor to enable forecasting"

---

## UX-003: No Breadcrumb on Some Pages
**Issue:** Some pages lack proper breadcrumb navigation.

**Fix:** Ensure all pages use `FeaturePage` with proper `breadcrumb` prop.

---

## UX-004: Responsive Layout Issues
**Issue:** Some pages (AIAssistantPage, AnalyticsPage) may have layout issues on tablet/mobile.

**Fix:** Test and fix responsive breakpoints per design system specs.

---

# Backend Issues

## BE-001: Missing EventLog Status Endpoints
**File:** `backend/src/api/routers/processes.py`

**Issue:** EventLog has `status` field in ORM but no endpoints to:
- Update status
- Trigger validation
- Transition states

**Fix Required:**
```python
@router.patch("/{log_id}/status")
async def update_log_status(log_id: str, status: LogStatus, db):
    ...

@router.post("/{log_id}/validate")
async def validate_log(log_id: str, db):
    ...
```

---

## BE-002: Missing Deviation Pagination
**File:** `backend/src/api/routers/conformance.py`

**Issue:** Conformance results can have thousands of deviations, but no paginated endpoint exists.

**Fix Required:**
```python
@router.get("/{result_id}/deviations")
async def list_deviations(result_id: str, page: int, page_size: int, db):
    ...
```

---

## BE-003: Missing Organizational Mining Endpoints
**File:** `backend/src/api/routers/organizational.py`

**Issue:** Missing endpoints for:
- `/roles` - Discovered organizational roles
- `/handovers` - Handover network data

---

## BE-004: Variant Response Missing activities Array
**File:** `backend/src/models/schemas.py`

**Issue:** `VariantResponse` only has `activity_trace: str`, needs:
```python
activities: list[str]  # Pre-parsed for frontend
```

---

# Summary

| Priority | Count | Status |
|----------|-------|--------|
| P0 Critical | 3 | Must fix before release |
| P1 High | 4 | Should fix for MVP |
| P2 Medium | 5 | Nice to have for MVP |
| P3 Low | 3 | Future roadmap |
| Code Quality | 4 | Technical debt |
| UX | 4 | Polish items |
| Backend | 4 | API gaps |
| **Total** | **27** | |

---

# Recommended Fix Order

## Sprint 1 (Critical Path)
1. **BUG-001**: Fix PredictionsPage mock data
2. **BUG-002**: Fix ConformanceTab model selection
3. **BUG-003**: Standardize AnalyticsPage hooks

## Sprint 2 (Upload Flow)
4. **BUG-004**: Create upload wizard
5. **BUG-005**: Add state indicators
6. **BE-001**: Add status endpoints

## Sprint 3 (Data Quality)
7. **BUG-006**: Fix variant activities parsing
8. **BE-004**: Add activities to VariantResponse
9. **CQ-001-004**: Code quality fixes

## Sprint 4 (Filtering)
10. **BUG-007**: Create filter builder
11. Connect to filtering endpoints

## Sprint 5+ (P2/P3)
12-27. Remaining features per roadmap

---

**Report Prepared By:** Fictive Kin Design Studio
**Version:** 1.0
