# Frontend API Refactor - Handoff Document

## What Was Done

### Phase 1: Bug Fixes (COMPLETE)
- [x] Fixed auth token key: `'token'` → `'auth_token'` in `src/api/client.ts:22`
- [x] Fixed API base URL: Now uses `env.API_BASE_URL` (port 8001) in:
  - `src/api/client.ts`
  - `src/shared/design-system.ts`

### Phase 2: SDK Infrastructure (COMPLETE)
- [x] Created `src/api/sdk.ts` - Comprehensive SDK covering all BE endpoints
- [x] Created `src/api/hooks/` directory with:
  - `queryKeys.ts` - Centralized query keys
  - `useDatasets.ts` - Dataset CRUD hooks
  - `useDiscovery.ts` - Discovery & DFG hooks
  - `useAnalytics.ts` - Bottlenecks, cycle time, KPI hooks
  - `useJobs.ts` - Job polling hooks
  - `useProjects.ts` - Project CRUD hooks
  - `useWorkspaces.ts` - Workspace CRUD hooks
  - `index.ts` - Re-exports everything

### Phase 3: Migration (PARTIAL)
- [x] Migrated `features/discovery/hooks/useDiscovery.ts` → re-exports SDK hooks
- [x] Migrated `features/analytics/hooks/index.ts` → re-exports SDK hooks

## What Remains

### Files Still Using Raw fetch() - Need Migration:
```
features/platform/projects/hooks/useUploadDataset.ts
features/platform/projects/hooks/useAnalyzeDataset.ts
features/platform/upload-wizard/hooks/useJobStream.ts
features/platform/upload-wizard/hooks/useUploadWizard.ts
features/kpi/pages/KPIPage.tsx
features/kpi/components/UnwantedActivitiesTab.tsx
features/kpi/components/AutomationTab.tsx
features/kpi/components/DeadlinesTab.tsx
features/explorer/pages/ExplorerIndexPage.tsx
features/explorer/pages/ExploreProcessesPage.tsx
features/explorer/components/AnalysisModeSelector.tsx
features/platform/pages/ProcessQuestionsPage.tsx
features/platform/pages/AuditLogsPage.tsx
features/platform/projects/pages/ProjectDetailPage.tsx
```

### Migration Pattern:
Replace:
```typescript
// OLD
const response = await fetch(`/api/v1/datasets/${id}`);
const data = await response.json();
```

With:
```typescript
// NEW - import from SDK hooks
import { useDataset } from '@/src/api/hooks';

// In component
const { data, isLoading } = useDataset(datasetId);
```

Or for mutations:
```typescript
import { useUploadDataset } from '@/src/api/hooks';

const uploadMutation = useUploadDataset();
uploadMutation.mutate({ projectId, file, name });
```

### Cleanup Tasks:
1. Remove stub hooks from `src/shared/design-system.ts` (lines ~520-590):
   - useAutomation, useDeadlines, useUnwantedActivities
   - useKPIPerformance, usePerformance, useCycleTime, useThroughput
   - useProcess, useRework, useAuditLogs

2. Update `src/shared/design-system.ts` SDK creation to use the new SDK singleton:
   - Remove `createSDKInstance()` function
   - Import and use `sdk` from `@/src/api/sdk` instead

3. Update `src/features/explorer/hooks/index.ts` to use SDK hooks

4. Verify build: `cd frontend-new && npm run build`

## Key Files Created

| File | Purpose |
|------|---------|
| `src/api/sdk.ts` | Main SDK with all BE endpoints |
| `src/api/hooks/index.ts` | All TanStack Query hooks |
| `src/api/hooks/queryKeys.ts` | Centralized query keys |

## Import Pattern (Use This Going Forward)

```typescript
// For SDK hooks (recommended)
import { useDatasets, useUploadDataset, useDiscoveryMutation } from '@/src/api/hooks';

// For direct SDK access (rare)
import { sdk } from '@/src/api/sdk';

// For query keys
import { queryKeys } from '@/src/api/hooks';
```

## Known Build Errors to Fix

1. **Type export from design-system.ts** (line 936):
   - `ProcessMiningSdk` type isn't exported from `./components`
   - Fix: Move type to `src/api/sdk.ts` or create dedicated types file

2. **AnalyticsPage.tsx** (line 237):
   - Uses `logItem.totalCases` but type doesn't include it
   - Fix: Update type or change component to use correct property

3. **JobStatusPanel.tsx** (line 27):
   - Job type mismatch between old types and SDK types
   - Fix: Update import to use SDK Job type

## Quick Fixes Needed

```bash
# 1. Fix design-system.ts line 936 - remove ProcessMiningSdk from re-export
# 2. Update features/discovery/components/JobStatusPanel.tsx to import Job from SDK
# 3. Fix any remaining type mismatches
```

## Plan File
Full plan at: `/Users/namanagarwal/.claude/plans/cozy-soaring-treasure.md`
