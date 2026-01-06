# Frontend Improvement Checklist

> Based on current codebase analysis and MVP gaps. **Focus on impact, not perfection.**

---

## Stack Status ✅

| Component | Status | Version |
|-----------|--------|---------|
| React | ✅ | 19.0.0 |
| State | ✅ TanStack Query | 5.90.15 |
| Graph Viz | ✅ Cytoscape.js | 3.33.1 |
| UI | ✅ Ant Design | 5.29.3 |
| Build | ✅ RSPack/NX | - |

---

## 1. Upload & Ingestion UX

### 1.1 Upload Flow Polish
- [ ] Add drag-and-drop visual feedback (border pulse on dragover)
- [ ] Show file validation inline (size, type) before upload
- [ ] Add upload progress with bytes transferred/total
- [ ] Cancel upload button during transfer

### 1.2 Column Mapping UX
- [ ] Highlight auto-detected column suggestions
- [ ] Show sample values preview per column (5 rows)
- [ ] Warn if timestamp column looks non-parseable
- [ ] Save mapping as template for future uploads

### 1.3 Ingestion Tracking
- [ ] Show granular step progress (Parsing → Validating → Ingesting)
- [ ] Display ETA based on file size/events
- [ ] Background ingestion with toast notification on complete
- [ ] Auto-navigate to Explorer when ready

---

## 2. Real-Time Workflow Status

### 2.1 Progress Polling ✅ (Completed)
- [x] Merge database + Temporal status in `useWorkflowPolling`
- [x] Expose `currentStep` in `useDatasetIngestion`
- [x] Normalize Temporal status codes (RUNNING → running)

### 2.2 Polish
- [ ] Add skeleton loader during initial workflow fetch
- [ ] Show elapsed time counter during active workflows
- [ ] Pulse animation on active workflow card
- [ ] Add retry button on transient failures

---

## 3. Explorer Visualization

### 3.1 Graph Controls
- [ ] Edge frequency slider (filter low-frequency edges client-side)
- [ ] Color mode toggle (Frequency / Performance / Plain)
- [ ] Node size toggle (Uniform / By Frequency)
- [ ] Mini-map for large graphs

### 3.2 Tooltips & Interactions
- [ ] Rich node tooltip (frequency, avg duration, case %)
- [ ] Rich edge tooltip (frequency, wait time)
- [ ] Click node → highlight incoming/outgoing edges
- [ ] Double-click node → filter to cases containing activity

### 3.3 Export
- [ ] Export graph as PNG (current view)
- [ ] Export graph as SVG (full graph)
- [ ] Export process data as CSV
- [ ] Share link with current view state (zoom, filters)

### 3.4 Variant Panel
- [ ] Search/filter variants by activity
- [ ] Sort variants by frequency/duration/complexity
- [ ] Click variant → highlight path on graph
- [ ] Compare 2 variants side-by-side

---

## 4. Algorithm Selection UX

### 4.1 Recommendations
- [ ] Show algorithm recommendation based on profile
- [ ] Display reason: "High variant explosion → Inductive Infrequent"
- [ ] Gray out unsuitable algorithms with reason

### 4.2 Complexity Slider
- [ ] Simple ↔ Detailed slider for noise filtering
- [ ] Map slider to algorithm-specific params
- [ ] Show preview of expected node count

### 4.3 Advanced Parameters (Collapsible)
- [ ] Show advanced params per algorithm
- [ ] Slider inputs with min/max validation
- [ ] Reset to defaults button

---

## 5. Performance Optimizations

### 5.1 Graph Performance
- [ ] Virtual rendering for 500+ nodes (level-of-detail)
- [ ] Debounce edge filter slider (100ms)
- [ ] Web Worker for layout computation
- [ ] Progressive edge rendering

### 5.2 Data Loading
- [ ] React Query cache invalidation on new analysis
- [ ] Prefetch explorer data on dataset ready
- [ ] Lazy load visualization page chunk
- [ ] Image/asset optimization

### 5.3 Bundle Size
- [ ] Analyze bundle with `source-map-explorer`
- [ ] Lazy load Cytoscape on route
- [ ] Tree-shake unused Ant Design icons

---

## 6. Error Handling & Recovery

### 6.1 User-Facing Errors
- [ ] Toast notifications for API errors
- [ ] Friendly error messages (not raw exceptions)
- [ ] Retry CTA on transient failures
- [ ] Error codes for support tickets

### 6.2 Error Boundaries
- [ ] Wrap ExplorerDetailPage in ErrorBoundary
- [ ] Wrap VariantPanel in ErrorBoundary
- [ ] Fallback UI with "Reload" button
- [ ] Log errors to backend (DevConsole)

### 6.3 Offline Resilience
- [ ] Show offline banner when API unreachable
- [ ] Queue actions for retry on reconnect
- [ ] Cache last successful graph render

---

## 7. Testing Coverage

### 7.1 Unit Tests
- [ ] `useWorkflowPolling` hook tests
- [ ] `useDatasetIngestion` hook tests
- [ ] Column mapping validation logic
- [ ] Edge filter logic

### 7.2 Integration Tests
- [ ] Upload → Column mapping → Ingest flow
- [ ] Discovery → Progress → Visualization flow
- [ ] Error state display

### 7.3 Visual Regression
- [ ] Storybook stories for all Explorer components
- [ ] Snapshot tests for graph rendering
- [ ] Responsive layout tests

---

## 8. Developer Experience

### 8.1 SDK Generation
- [ ] Auto-regenerate SDK on OpenAPI spec change
- [ ] Type-safe API client with Zod validation
- [ ] Mock server for offline development

### 8.2 Documentation
- [ ] Component usage docs in Storybook
- [ ] Hook API documentation
- [ ] Frontend architecture diagram

---

## Priority Matrix

| Priority | Items | Est. Effort |
|----------|-------|-------------|
| 🔴 P0 | Ingestion tracking, Error toasts, Edge filter | 2-3 days |
| 🟠 P1 | Tooltips, Recommendations, Export | 3-4 days |
| 🟡 P2 | Graph performance, Testing | 4-5 days |
| 🟢 P3 | Offline resilience, DX improvements | 2-3 days |

---

## Quick Wins (< 1 hour each)

1. [x] Add skeleton loader to Explorer page (`ExplorerSkeleton.tsx`)
2. [x] Debounce edge filter slider (`EdgeFrequencySlider.tsx`)
3. [ ] Add export CSV button
4. [x] Add elapsed time to workflow progress (`WorkflowElapsedTime.tsx`)
5. [x] Wrap VariantPanel in ErrorBoundary (already done in ExplorerDetailPage.tsx:608-627)

---

*Checklist based on current codebase with 255 TypeScript files, 15 Explorer components, and existing TanStack Query + Cytoscape.js stack.*
