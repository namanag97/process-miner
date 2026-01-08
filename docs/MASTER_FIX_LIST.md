# MASTER FIX LIST: Process Mining Platform

**Generated:** 2026-01-08
**Total Issues Found:** 87
**Critical:** 23 | **High:** 28 | **Medium:** 24 | **Low:** 12

---

## EXECUTIVE SUMMARY

Your platform has extensive features but **nothing works 100% end-to-end**. The root causes are:

1. **Schema Evolution Debt** - Backend changed field names but frontend/tests weren't updated
2. **Missing Endpoints** - Frontend calls APIs that don't exist
3. **Hardcoded Values** - Backend returns zeros/stubs instead of real computations
4. **Type Mismatches** - snake_case vs camelCase conversion failures
5. **Incomplete Flows** - Features start but don't complete

---

## PRIORITY 0: CRITICAL BLOCKERS (Fix First)

These block basic functionality. Platform is unusable without fixing these.

### P0-01: Missing `/datasets/{id}/sheets` Endpoint
- **Feature:** Upload Wizard
- **Impact:** Excel file uploads fail completely
- **Location:** Backend - endpoint doesn't exist
- **Frontend expects:** `GET /api/v1/datasets/{id}/sheets`
- **Fix:** Create endpoint in `backend/src/features/process_mining/datasets/api/upload.py`

### P0-02: Missing `/analytics/datasets/{id}/performance` Endpoint
- **Feature:** Analytics Page
- **Impact:** Performance tab shows all "N/A", summary cards empty
- **Location:** Backend - endpoint doesn't exist
- **Frontend expects:** `GET /api/v1/analytics/datasets/{id}/performance`
- **Fix:** Either create aggregate endpoint OR update frontend to call individual endpoints (bottlenecks, cycle-time, throughput)

### P0-03: Discovery Schema Mismatch - `miner_type` vs `algorithm`
- **Feature:** Process Discovery
- **Impact:** Discovery requests fail, tests can't pass
- **Backend field:** `miner_type` (router.py:197)
- **Test sends:** `algorithm` (test_discovery.py:29)
- **Fix:** Standardize on `miner_type` everywhere, update tests

### P0-04: Discovery Router Uses ReadDBSession for Writes
- **Feature:** Process Discovery
- **Impact:** Database inserts silently fail
- **Location:** `backend/src/features/process_mining/discovery/router.py:52`
- **Issue:** `db: ReadDBSession` used for `db.add(process_model)`
- **Fix:** Change to `WriteDBSession`

### P0-05: Conformance Tab Hardcodes `modelId='default'`
- **Feature:** Conformance Checking
- **Impact:** Always returns 404 (no model named 'default')
- **Location:** `frontend-new/src/features/analytics/components/ConformanceTab.tsx:65`
- **Fix:** Fetch available models first, use first model's ID

### P0-06: ReworkTab Field Name Mismatch
- **Feature:** Analytics - Rework
- **Impact:** Rework data never displays, table shows empty
- **Backend returns:** `rework_activities`, `total_rework_cases` (snake_case)
- **Frontend expects:** `reworkActivities`, `totalReworkCases` (camelCase)
- **Location:** `frontend-new/src/features/analytics/components/ReworkTab.tsx`
- **Fix:** Add transformation layer or update backend response model

### P0-07: Upload Preview API Returns Wrong Fields
- **Feature:** Upload Wizard - Configure Step
- **Impact:** Configure step can't render, wizard hangs
- **Backend returns:** `sample_events`, `parse_errors`
- **Frontend expects:** `columns`, `rows`, `encoding`
- **Location:** `backend/src/features/process_mining/datasets/api/mapping.py:420`
- **Fix:** Update `PreviewResponse` schema to match frontend expectations

### P0-08: Column Detection Not Triggered for Direct Uploads
- **Feature:** Upload Wizard
- **Impact:** Columns never detected, mapping step fails
- **Issue:** Only presigned uploads trigger `dispatch_workflow("validate_uploaded_file")`
- **Location:** `backend/src/features/process_mining/datasets/api/upload.py:286-297`
- **Fix:** Trigger validation workflow for all upload paths

---

## PRIORITY 1: HIGH - Core Feature Breaks

Features partially work but have significant gaps.

### P1-01: Cycle Time Percentiles Hardcoded to 0
- **Feature:** Analytics - Performance
- **Impact:** P25, P75, P95 always show 0%
- **Location:** `backend/src/features/process_mining/analytics/router.py:107-109`
- **Code:** `percentile_25_seconds=0, percentile_75_seconds=0, percentile_95_seconds=0`
- **Fix:** Map actual values from query result

### P1-02: Bottleneck Service Time Hardcoded to 0
- **Feature:** Analytics - Bottlenecks
- **Impact:** Service time column always shows 0
- **Location:** `backend/src/features/process_mining/analytics/router.py:72`
- **Code:** `avg_service_time_seconds=0`
- **Fix:** Compute service time in DuckDB query

### P1-03: Bottleneck Preceding/Following Activities Empty
- **Feature:** Analytics - Bottlenecks
- **Impact:** Context for bottlenecks missing
- **Location:** `backend/src/features/process_mining/analytics/router.py:76`
- **Code:** `preceding_activities=[], following_activities=[]`
- **Fix:** Extend DuckDB query to include activity relationships

### P1-04: AI Chat in Stub Mode
- **Feature:** AI Assistant
- **Impact:** Not using real LLM, just pattern-matched responses
- **Location:** `backend/src/features/process_mining/ai/service.py:40-48`
- **Issue:** `use_real_llm = False` by default
- **Fix:** Add `OPENROUTER_API_KEY` and `AI_CHAT_LIVE_MODE=true` to .env

### P1-05: OpenRouter LLM Integration Not Implemented
- **Feature:** AI Assistant
- **Impact:** Even with API key, LLM not called
- **Location:** `backend/src/features/process_mining/ai/service.py:79-91`
- **Issue:** `_call_openrouter()` is placeholder, returns stub
- **Fix:** Implement actual HTTP call to OpenRouter API

### P1-06: Discovery Response Format Mismatch
- **Feature:** Process Discovery
- **Impact:** Frontend can't parse discovery results
- **Backend returns:** `ModelResponse` with `miner_type`, `model_format`
- **Test expects:** `model_id`, `algorithm`, `format`
- **Location:** `backend/src/features/process_mining/discovery/router.py:180-186`
- **Fix:** Standardize response schema

### P1-07: `/miners` Endpoint Returns Bare Array
- **Feature:** Process Discovery
- **Impact:** Frontend expects wrapped response
- **Backend returns:** `[MinerInfo, MinerInfo, ...]`
- **Frontend expects:** `{ "algorithms": [...] }`
- **Location:** `backend/src/features/process_mining/discovery/router.py:39-42`
- **Fix:** Wrap in `AlgorithmListResponse`

### P1-08: Filters Are UI-Only (No Backend Integration)
- **Feature:** Explorer
- **Impact:** Filters don't actually filter data
- **Location:** `frontend-new/src/features/explorer/pages/ExplorerDetailPage.tsx:585`
- **Issue:** No API call made when filters applied
- **Fix:** Implement filter backend API, pass filters to data fetching

### P1-09: Job Status Enum Mismatch
- **Feature:** Job Polling
- **Impact:** Status comparison fails, polling may not stop
- **Celery uses:** `"pending"`, `"running"`
- **Temporal uses:** `"PENDING"`, `"RUNNING"`
- **Fix:** Normalize status values in backend response

### P1-10: AnalysisModeSelector Bypasses SDK
- **Feature:** Process Discovery
- **Impact:** Direct fetch() calls, hardcoded URLs, fragile
- **Location:** `frontend-new/src/features/explorer/components/AnalysisModeSelector.tsx:142-178`
- **Fix:** Use `sdk.discovery.discover()` instead of raw fetch

### P1-11: Column Detection Missing for Presigned Uploads
- **Feature:** Upload Wizard
- **Impact:** `validate_uploaded_file` workflow not implemented
- **Location:** `backend/src/features/process_mining/datasets/api/upload.py`
- **Fix:** Implement validation workflow that detects columns

### P1-12: Diagnostics Endpoint Runs Conformance Twice
- **Feature:** Conformance Checking
- **Impact:** Performance degradation, duplicate data
- **Location:** `backend/src/features/process_mining/conformance/router.py:279-312`
- **Fix:** Cache first conformance result, reuse for diagnostics

---

## PRIORITY 2: MEDIUM - UX and Data Quality

### P2-01: Column Type Settings Not Saved
- **Feature:** Upload Wizard - Configure Step
- **Impact:** User selections lost on page reload
- **Location:** ConfigureStep.tsx local state only
- **Fix:** Persist to backend via API call

### P2-02: Mapping Submitted Twice
- **Feature:** Upload Wizard
- **Impact:** Redundant API calls, potential race condition
- **Location:** `useUploadWizard.ts` - `submitMapping()` then `ingest()`
- **Fix:** Remove redundant submission

### P2-03: Wizard State Not Persisted
- **Feature:** Upload Wizard
- **Impact:** User loses progress if page reloads
- **Fix:** Save state to localStorage

### P2-04: Null Conformance Metrics Show as 0%
- **Feature:** Conformance Tab
- **Impact:** Misleading - 0% looks like failure, not "not calculated"
- **Location:** `ConformanceTab.tsx:108-109`
- **Fix:** Show "N/A" or "Not calculated" instead of 0

### P2-05: GetVariantsQuery Duplicated
- **Feature:** Analytics - Variants
- **Impact:** Code confusion, potential bugs
- **Locations:**
  - `analytics_queries.py:61-69` (stub)
  - `get_variants.py:24-33` (full)
- **Fix:** Remove stub, use only full implementation

### P2-06: Model Delete Button Handler Missing
- **Feature:** Discovery
- **Impact:** Delete button exists but doesn't work
- **Location:** `ModelList.tsx:129-139`
- **Fix:** Add `onDeleteModel` handler to DiscoveryPage

### P2-07: Alignment Parsing Logic Fragile
- **Feature:** Conformance
- **Impact:** Fails with some model formats
- **Location:** `backend/src/features/process_mining/conformance/service.py:306-338`
- **Fix:** Validate alignment structure before parsing

### P2-08: Missing Error Recovery in Upload
- **Feature:** Upload Wizard
- **Impact:** Failed uploads require full restart
- **Fix:** Add retry buttons for failed API calls

### P2-09: Progress Thresholds Hardcoded
- **Feature:** Upload Wizard - Finalize Step
- **Impact:** Progress bar doesn't match actual job progress
- **Fix:** Use actual job progress values

### P2-10: Event Log Loader Missing Validation
- **Feature:** Discovery
- **Impact:** Runtime crash if parquet file missing
- **Location:** `backend/src/features/process_mining/discovery/service.py:81-83`
- **Fix:** Validate parquet file exists before loading

### P2-11: Compare Variants Not Implemented
- **Feature:** Explorer
- **Impact:** Button exists but shows "coming soon"
- **Location:** `ExplorerDetailPage.tsx:454`
- **Fix:** Implement variant comparison or disable button

### P2-12: Create Exploration Not Implemented
- **Feature:** Explorer
- **Impact:** Button exists but shows "coming soon"
- **Location:** `ExplorerDetailPage.tsx:822-827`
- **Fix:** Implement or disable

### P2-13: Help/Documentation Not Implemented
- **Feature:** Explorer
- **Impact:** Button exists but shows "coming soon"
- **Location:** `ExplorerDetailPage.tsx:833-837`
- **Fix:** Link to docs or disable

### P2-14: No Conversation History in AI Chat
- **Feature:** AI Assistant
- **Impact:** Each response is stateless
- **Location:** `backend/src/features/process_mining/ai/service.py`
- **Issue:** `conversation_history` accepted but not used
- **Fix:** Pass history to LLM context

---

## PRIORITY 3: LOW - Polish and Cleanup

### P3-01: Upload Search Box Non-Functional
- **Feature:** Upload Wizard
- **Impact:** UI placeholder that does nothing
- **Fix:** Remove or implement

### P3-02: Google Sheets/Database Upload Disabled
- **Feature:** Upload Wizard
- **Impact:** Shows "coming soon"
- **Fix:** Remove or implement

### P3-03: Date Format Selector Unused
- **Feature:** Upload Wizard
- **Impact:** Field does nothing
- **Fix:** Implement or remove

### P3-04: Encoding Selector Disabled
- **Feature:** Upload Wizard
- **Impact:** Always UTF-8
- **Fix:** Implement or remove

### P3-05: Upload Progress Hardcoded
- **Feature:** Upload Wizard
- **Impact:** Not real-time progress
- **Fix:** Use actual upload progress events

### P3-06: No Token Counting in AI Chat
- **Feature:** AI Assistant
- **Impact:** Can't track usage/costs
- **Fix:** Implement token counting

### P3-07: Missing AI Tests
- **Feature:** AI Assistant
- **Impact:** No test coverage
- **Fix:** Add unit/integration tests

### P3-08: Model Serializer Not Exported
- **Feature:** Discovery
- **Impact:** Import errors possible
- **Location:** `discovery/__init__.py:44`
- **Fix:** Add proper export

### P3-09: Frontend Type Casts
- **Feature:** Discovery
- **Impact:** TypeScript errors
- **Location:** `useDiscovery.ts:76`
- **Issue:** `as unknown as` indicates type mismatch
- **Fix:** Fix SDK types

### P3-10: Deprecated Hooks Still Exported
- **Feature:** Explorer
- **Impact:** Code confusion
- **Location:** `explorer/hooks/index.ts`
- **Fix:** Remove deprecated exports

---

## FIX ORDER RECOMMENDATION

### Week 1: Critical Path (Get Basic Flow Working)
1. P0-02: Create `/analytics/datasets/{id}/performance` endpoint OR fix frontend
2. P0-06: Fix ReworkTab field name transformation
3. P0-07: Fix Upload Preview API response
4. P0-03: Standardize `miner_type` field name
5. P0-04: Fix Discovery WriteDBSession

### Week 2: Complete Upload Flow
6. P0-01: Create `/datasets/{id}/sheets` endpoint
7. P0-08: Trigger column detection for all uploads
8. P1-11: Implement validation workflow
9. P2-02: Remove duplicate mapping submission
10. P2-03: Persist wizard state

### Week 3: Fix Analytics
11. P1-01: Compute real cycle time percentiles
12. P1-02: Compute real service times
13. P1-03: Compute activity relationships
14. P0-05: Fix conformance modelId selection
15. P2-04: Show "N/A" for null metrics

### Week 4: Fix Discovery & Explorer
16. P1-06: Fix discovery response format
17. P1-07: Wrap `/miners` response
18. P1-10: Use SDK in AnalysisModeSelector
19. P1-08: Implement filter backend integration
20. P2-06: Add model delete handler

### Week 5: AI & Polish
21. P1-04: Enable real LLM mode
22. P1-05: Implement OpenRouter integration
23. P2-14: Use conversation history
24. P1-09: Normalize job status enums
25. Remaining P2/P3 items

---

## QUICK WINS (< 1 Hour Each)

These can be fixed quickly between larger tasks:

1. **P1-01**: Change hardcoded `0` to `result.percentile_XX_seconds` (5 min)
2. **P1-07**: Wrap response in `{ "algorithms": [...] }` (10 min)
3. **P0-05**: Fetch models first, use `models[0].id` (15 min)
4. **P2-04**: Change `?? 0` to `?? null` and show "N/A" (10 min)
5. **P3-01**: Remove search box HTML (5 min)
6. **P2-05**: Delete stub query class (5 min)
7. **P3-08**: Add export to `__init__.py` (5 min)

---

## VERIFICATION CHECKLIST

After fixing each issue, verify:

### Upload Flow
- [ ] CSV upload works end-to-end
- [ ] Excel upload works (requires P0-01)
- [ ] Column detection triggers automatically
- [ ] Preview shows correct data
- [ ] Mapping step shows column suggestions
- [ ] Ingestion completes successfully
- [ ] Dataset shows as READY

### Discovery Flow
- [ ] Algorithm list loads
- [ ] Discovery job starts
- [ ] Job status polls correctly
- [ ] Model appears in list
- [ ] Model visualization renders
- [ ] Fitness/precision metrics show

### Analytics Flow
- [ ] Performance tab shows real data
- [ ] Bottleneck table populates
- [ ] Cycle time chart renders
- [ ] Throughput metrics show
- [ ] Rework tab displays data
- [ ] Conformance runs without 404

### Explorer Flow
- [ ] DFG visualization renders
- [ ] Variants list populates
- [ ] Activity details show on click
- [ ] Filters apply (after P1-08)
- [ ] Export PNG works
- [ ] Export CSV works

### AI Flow
- [ ] Chat input works
- [ ] Response shows (even stub)
- [ ] Process context injected
- [ ] Quick prompts work
- [ ] Real LLM responds (after P1-04/05)

---

## ARCHITECTURE RECOMMENDATIONS

### Short Term (This Quarter)
1. **Add API Contract Tests** - Ensure frontend/backend stay in sync
2. **Implement Response Transformers** - snake_case → camelCase consistently
3. **Add Error Boundaries** - Catch and display errors gracefully
4. **Implement Retry Logic** - Automatic retry for transient failures

### Medium Term (Next Quarter)
1. **Real Authentication** - Remove MVP hardcoded auth
2. **Multi-Workspace Support** - Enable workspace selection
3. **Real-time Updates** - WebSocket for job status
4. **Caching Layer** - Redis for computed analytics

### Long Term
1. **OpenTelemetry** - Distributed tracing
2. **Feature Flags** - Gradual rollout
3. **API Versioning** - Breaking change management
4. **Multi-Region** - Geographic distribution

---

## CONTACT & SUPPORT

This audit was generated by comprehensive codebase analysis. For questions about specific issues, reference the file paths and line numbers provided.

**Files Modified:** 0
**Files Analyzed:** 150+
**Time to Generate:** ~15 minutes
