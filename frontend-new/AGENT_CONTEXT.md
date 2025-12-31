Plan Summary:

- 6 Phases covering all migrations and cleanup
- 4 Features to migrate: Explorer, Analytics, KPI, AI
- Pattern: Each feature gets index.ts, types.ts, routes.tsx, hooks/, pages/, components/
- Route Cleanup: Remove all legacy /projects, /home, top-level /explorer, /analytics, /ai routes
- Navigation: Update AppShell label from "Home" to "Workspace"

Key Files to Modify:

- frontend-new/src/App.tsx - Route cleanup
- frontend-new/libs/shared/design-system/src/components/AppShell.tsx - Nav label
- frontend-new/src/features/ - 4 new feature directories

Files to Delete After Migration:

- src/pages/explorer/, src/pages/kpi/, src/pages/analytics/, src/pages/ai/
- Legacy src/pages/projects/, src/pages/home/WorkspaceTab.tsx

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Ready to code?

Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
Frontend Feature Migration & Route Cleanup Plan

Decisions Made

- ✅ Migrate all 4 features in order: Explorer → Analytics → KPI → AI
- ✅ Remove legacy routes completely (no redirects)
- ✅ Rename navigation "Home" → "Workspace"

Overview

Complete migration of remaining pages to the feature module pattern established in projects, plus route cleanup and navigation improvements.

---

Phase 1: Explorer Feature Migration

1.1 Create Feature Structure

src/features/explorer/
├── index.ts # Feature entry + FeatureRegistry
├── types.ts # DFG, Variant, Activity types
├── routes.tsx # Route config with lazy loading
├── hooks/
│ └── index.ts # useDFG, useVariants, useActivities
├── pages/
│ ├── index.ts
│ ├── ExplorerIndexPage.tsx # Process selection list
│ └── ExplorerDetailPage.tsx # Main DFG canvas view
├── components/
│ ├── index.ts
│ ├── ProcessCanvas.tsx # React Flow DFG (move from pages)
│ ├── ProcessKPIBar.tsx
│ ├── VariantPanel.tsx
│ ├── ActivityDetailsPanel.tsx
│ ├── EdgeDetailsPanel.tsx
│ ├── FilterPanel.tsx
│ └── EnhancedActivityNode.tsx
└── utils/
├── layoutAlgorithms.ts # Dagre layout
└── colorScales.ts # Performance colors

1.2 Files to Move/Refactor

| Source                                      | Destination                                    | Action          |
| ------------------------------------------- | ---------------------------------------------- | --------------- |
| pages/explorer/ProcessExplorerIndexPage.tsx | features/explorer/pages/ExplorerIndexPage.tsx  | Move + refactor |
| pages/explorer/ProcessExplorerPage.tsx      | features/explorer/pages/ExplorerDetailPage.tsx | Move + refactor |
| pages/explorer/components/\*                | features/explorer/components/\*                | Move            |
| pages/explorer/utils/\*                     | features/explorer/utils/\*                     | Move            |

1.3 New Hooks to Create (using createQueryHook factory)

// hooks/index.ts
export const useDFG = createQueryHook({
queryKey: (logId) => ['explorer', 'dfg', logId],
queryFn: (sdk, logId) => sdk.discovery.buildDFG(logId),
staleTime: 5 _ 60 _ 1000,
});

export const useVariants = createQueryHook({
queryKey: (logId) => ['explorer', 'variants', logId],
queryFn: (sdk, logId) => sdk.discovery.getVariants(logId),
});

export const useActivities = createQueryHook({
queryKey: (logId) => ['explorer', 'activities', logId],
queryFn: (sdk, logId) => sdk.discovery.getActivities(logId),
});

1.4 Feature Registration

// index.ts
FeatureRegistry.register({
id: 'explorer',
name: 'Process Explorer',
version: '1.0.0',
icon: 'BranchesOutlined',
navPath: '/explorer',
navOrder: 3,
routes: explorerRouteConfig,
});

---

Phase 2: KPI Feature Migration

2.1 Create Feature Structure

src/features/kpi/
├── index.ts
├── types.ts # Performance, CycleTime types
├── routes.tsx
├── hooks/
│ └── index.ts # usePerformance, useCycleTime, etc.
├── pages/
│ ├── index.ts
│ └── KPIPage.tsx # Main KPI page with tabs
└── components/
├── index.ts
├── PerformanceTab.tsx
├── DeadlinesTab.tsx
├── UnwantedActivitiesTab.tsx
└── AutomationTab.tsx

2.2 Files to Move/Refactor

| Source                | Destination                    | Action                   |
| --------------------- | ------------------------------ | ------------------------ |
| pages/kpi/KPIPage.tsx | features/kpi/pages/KPIPage.tsx | Move + refactor          |
| pages/kpi/tabs/\*     | features/kpi/components/\*     | Move (tabs → components) |

2.3 Feature Registration

FeatureRegistry.register({
id: 'kpi',
name: 'KPI Dashboard',
version: '1.0.0',
icon: 'DashboardOutlined',
navPath: '/workspace/:projectId/data/:logId/kpi',
navOrder: 4,
routes: kpiRouteConfig,
});

---

Phase 3: Analytics Feature Migration

3.1 Create Feature Structure

src/features/analytics/
├── index.ts
├── types.ts # PerformanceData, Conformance, Rework types
├── routes.tsx
├── hooks/
│ └── index.ts # useAnalyticsPerformance, useRework, etc.
├── pages/
│ ├── index.ts
│ └── AnalyticsPage.tsx # Main analytics with tabs
└── components/
├── index.ts
├── PerformanceTab.tsx
├── ConformanceTab.tsx
├── ReworkTab.tsx
└── ResourcesTab.tsx

3.2 Files to Move/Refactor

| Source                            | Destination                                | Action          |
| --------------------------------- | ------------------------------------------ | --------------- |
| pages/analytics/AnalyticsPage.tsx | features/analytics/pages/AnalyticsPage.tsx | Move + refactor |
| pages/analytics/\*Tab.tsx         | features/analytics/components/\*Tab.tsx    | Move            |

3.3 Feature Registration

FeatureRegistry.register({
id: 'analytics',
name: 'Analytics',
version: '1.0.0',
icon: 'BarChartOutlined',
navPath: '/analytics',
navOrder: 5,
routes: analyticsRouteConfig,
});

---

Phase 4: AI Feature Migration

4.1 Create Feature Structure

src/features/ai/
├── index.ts
├── types.ts # ChatMessage, ProcessInsight, etc. (from pages/ai/types/)
├── routes.tsx
├── hooks/
│ └── index.ts # useProcessSummary, useChat
├── pages/
│ ├── index.ts
│ ├── AIIndexPage.tsx # AI feature hub
│ ├── AIAssistantPage.tsx # Chat interface
│ ├── AIInsightsPage.tsx # Automated insights
│ ├── PredictionsPage.tsx # ML predictions list
│ └── PredictorDetailPage.tsx # Single predictor
├── components/
│ ├── index.ts
│ ├── ProcessSelector.tsx
│ ├── ChatMessage.tsx
│ └── InsightCard.tsx
└── utils/
└── processContextBuilder.ts

4.2 Files to Move/Refactor

| Source                    | Destination               | Action             |
| ------------------------- | ------------------------- | ------------------ |
| pages/ai/\*.tsx (5 pages) | features/ai/pages/\*.tsx  | Move + refactor    |
| pages/ai/types/ai.ts      | features/ai/types.ts      | Move + consolidate |
| pages/ai/components/\*    | features/ai/components/\* | Move               |
| pages/ai/utils/\*         | features/ai/utils/\*      | Move               |

4.3 Feature Registration

FeatureRegistry.register({
id: 'ai',
name: 'AI & Predictions',
version: '1.0.0',
icon: 'RobotOutlined',
navPath: '/ai',
navOrder: 6,
routes: aiRouteConfig,
});

---

Phase 5: Route Cleanup (Remove Legacy Routes)

5.1 Remove Legacy Routes from App.tsx

Delete the following route definitions entirely:

- /projects and /projects/\* routes
- /home route
- Top-level /explorer (will be replaced by feature route)
- Top-level /analytics (will be replaced by feature route)
- Top-level /ai/\* routes (will be replaced by feature route)

Keep only workspace-centric routes:
// Primary routes after cleanup
{ path: '/workspace', element: <ProjectsListPage /> },
{ path: '/workspace/:projectId', element: <ProjectDetailPage /> },
{ path: '/workspace/:projectId/data/:logId/_', /_ nested feature routes \*/ },

5.2 Component Navigation Fixes

| File                                                | Current                                     | Fix To                                       |
| --------------------------------------------------- | ------------------------------------------- | -------------------------------------------- |
| features/projects/components/ProjectCard.tsx:26     | /projects/${id}                             | /workspace/${id}                             |
| features/projects/components/DataSourcesList.tsx:29 | /projects/${projectId}/data/${id}/questions | /workspace/${projectId}/data/${id}/questions |
| pages/home/WorkspaceTab.tsx                         | /projects/{id}                              | /workspace/{id}                              |
| pages/projects/ProjectDetailPage.tsx                | navigate('/home?tab=workspace')             | navigate('/workspace')                       |

5.3 Clean Up Duplicates

- Remove legacy pages/projects/ProjectDetailPage.tsx (replaced by features/projects/pages/ProjectDetailPage.tsx)
- Remove legacy pages/home/WorkspaceTab.tsx (replaced by features/projects/pages/ProjectsListPage.tsx)

---

Phase 6: Navigation Updates (Home → Workspace)

6.1 AppShell Navigation Changes

File: libs/shared/design-system/src/components/AppShell.tsx

Update default nav items array (~line 47):
// Before
{ id: 'home', label: 'Home', icon: 'home' }

// After
{ id: 'workspace', label: 'Workspace', icon: 'folder' }

6.2 App.tsx Navigation Mapping Updates

File: src/App.tsx

Update getActiveId() function (~line 117):

- Remove 'home' case
- Keep 'workspace' for /workspace paths

Update handleNavigate() function (~line 136):

- Remove 'home' → '/workspace' mapping (use 'workspace' only)

  6.3 Remove HomePage References

- Delete or update any remaining /home path references
- Update breadcrumbs that reference "Home" to "Workspace"

---

Implementation Order (Recommended)

1.  Explorer - Most isolated, good for validating pattern
2.  Analytics - Similar tab structure, standalone
3.  KPI - Depends on project context (workspace routes)
4.  AI - Multiple pages, test full feature pattern
5.  Route Cleanup - After all features migrated
6.  Navigation Updates - Final polish

---

Files to Delete After Migration

src/pages/explorer/ # Entire directory
src/pages/kpi/ # Entire directory
src/pages/analytics/ # Entire directory
src/pages/ai/ # Entire directory
src/pages/projects/ # Legacy duplicate
src/pages/home/WorkspaceTab.tsx # Replaced

---

Verification Checklist

Per Feature:

- Feature structure created
- Types extracted to types.ts
- Hooks converted to factory pattern
- Pages wrapped with FeaturePage
- Routes configured with lazy loading
- Feature registered with FeatureRegistry
- Old files deleted
- App.tsx routes updated
- Navigation working

Final:

- All legacy routes redirect correctly
- No broken navigation links
- Build passes with no errors
- All features accessible from sidebar
