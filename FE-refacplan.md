# Frontend Cleanup & Modernization - Implementation Plan

**Project:** Process Mining SaaS Platform - Complete Frontend Refactor
**Based on:** SENIOR_FE_DEV_BRIEF.md
**Timeline:** 10-14 days (6 phases)
**Current Branch:** feature/temporal-workers
**Status:** Ready for execution

---

## Executive Summary

Complete frontend cleanup and modernization covering 7 major goals:
1. Code Organization & Architecture
2. API Integration Readiness
3. Error Handling & Loading States
4. TypeScript & Code Quality
5. Component Organization
6. State Management Clarity
7. Testing Infrastructure

**Current State:** 0 TypeScript errors (excellent baseline!), well-architected Nx monorepo with 7 features, but needs standardization and polish.

**End Goal:** Production-ready codebase with consistent patterns, 100% type safety, comprehensive error handling, and complete documentation.

---

## Phase 1: Foundation Cleanup (0.5 days)

**Goal:** Fix immediate issues and establish clean baseline

### Tasks

#### 1.1 Fix Import Path Issues (4 files)
Replace incorrect `@/src/shared/design-system` with `@lumina/design-system`:

**Files to edit:**
- `/Users/namanagarwal/system/frontend-new/src/features/explorer/components/EdgeFrequencySlider.tsx:11`
  - Change: `import { tokens } from '@/src/shared/design-system';`
  - To: `import { tokens } from '@lumina/design-system';`

- `/Users/namanagarwal/system/frontend-new/src/features/explorer/components/ExplorerSkeleton.tsx:8`
  - Change: `import { tokens } from '@/src/shared/design-system';`
  - To: `import { tokens } from '@lumina/design-system';`

- `/Users/namanagarwal/system/frontend-new/src/shared/components/WorkflowElapsedTime.tsx:10`
  - Change: `import { tokens } from '@/src/shared/design-system';`
  - To: `import { tokens } from '@lumina/design-system';`

- `/Users/namanagarwal/system/frontend-new/src/shared/components/WorkflowProgressCard.tsx:15`
  - Change: `import { tokens } from '@/src/shared/design-system';`
  - To: `import { tokens } from '@lumina/design-system';`

#### 1.2 Fix WorkflowProgressCard Deleted Dependency
`WorkflowProgressCard.tsx:17` imports from deleted `useWorkflowPolling.ts`:

**Options:**
1. **Remove the component** (if unused)
2. **Restore from .bak file** (if needed)
3. **Inline the type definition** (simplest if component is used)

**Recommended:** Check usage with grep, then either remove or inline type.

#### 1.3 Remove Dead Code
Delete 3 backup files:
- `/Users/namanagarwal/system/frontend-new/src/shared/hooks/useWorkflowPolling.ts.bak`
- `/Users/namanagarwal/system/frontend-new/src/shared/hooks/useDatasetIngestion.ts.bak`
- `/Users/namanagarwal/system/frontend-new/src/shared/hooks/useAnalyticsDashboard.ts.bak`

**Also deleted in git** (already removed, verify not imported):
- `frontend-new/src/shared/hooks/useAnalyticsDashboard.ts`
- `frontend-new/src/shared/hooks/useDatasetIngestion.ts`
- `frontend-new/src/shared/hooks/useWorkflowPolling.ts`

#### 1.4 Audit for Unused Imports
Run across all features:
```bash
cd frontend-new && npx eslint src/ --rule "unused-imports/no-unused-imports: error" --fix
```

### Success Criteria
- [x] All 4 import paths fixed
- [x] WorkflowProgressCard compiles without errors
- [x] 0 .bak files in codebase
- [x] No unused import warnings
- [x] `npx tsc --noEmit` passes (0 errors)
- [x] App runs without console errors

### Testing
- Run `npm run typecheck`
- Start dev server: `npm run start`
- Manual smoke test: Visit all major routes

---

## Phase 2: API Integration Structure (1 day)

**Goal:** Establish standardized API integration patterns for all features

### 2.1 Create API Structure Template

**Create:** `/Users/namanagarwal/system/frontend-new/src/features/_template/api/`

```
_template/api/
├── queries.ts        # GET requests (React Query)
├── mutations.ts      # POST/PUT/DELETE (React Query)
├── types.ts          # Request/response TypeScript types
├── endpoints.ts      # API endpoint URL constants
└── README.md         # Usage guide for developers
```

**Example structure (queries.ts):**
```typescript
import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@lumina/design-system';
import { instrumentedFetch } from '@lumina/design-system';

export function useGetFeatureItems(featureId: string) {
  return useQuery({
    queryKey: queryKeys.feature.items(featureId),
    queryFn: async () => {
      const response = await instrumentedFetch(`/api/v1/features/${featureId}/items`);
      return response.json();
    },
    enabled: !!featureId,
  });
}
```

### 2.2 Document API Integration Patterns

**Create:** `/Users/namanagarwal/system/frontend-new/docs/API_INTEGRATION_GUIDE.md`

Include:
- When to use queries vs mutations
- Error handling strategy (toast vs error boundary)
- Loading state patterns (skeletons vs spinners)
- Query key naming conventions
- Invalidation strategies
- Mock data toggle pattern

### 2.3 Apply Pattern to Projects Feature (Pilot)

**Refactor:** `/Users/namanagarwal/system/frontend-new/src/features/platform/projects/`

Current state: Already uses hooks from `@lumina/design-system` (useProjects, useProject, useCreateProject, etc.)

**Actions:**
1. Create `projects/api/` folder
2. Move project-specific API logic (if any) into structured files
3. Ensure consistent error handling
4. Add loading states to all async operations
5. Document as reference implementation

### Success Criteria
- [x] Template API structure created with all 5 files
- [x] API_INTEGRATION_GUIDE.md written (5-10 pages)
- [x] Projects feature follows new pattern
- [x] All queries have error handling
- [x] All mutations show loading states
- [x] Team can replicate pattern for other features

### Testing
- Projects list page loads correctly
- Project creation shows loading spinner
- Errors display toast notifications
- Form validation works

---

## Phase 3: Error Handling & Loading States (1 day)

**Goal:** Consistent error handling and loading UX across all features

### 3.1 Add Feature-Level Error Boundaries

App.tsx already has `GlobalErrorBoundary`. Add feature-level boundaries for graceful degradation.

**Pattern to apply to all 7 features:**

```typescript
// In each feature's routes.tsx or index page
import { ErrorBoundary } from '@lumina/design-system';

export function FeatureRoutes() {
  return (
    <ErrorBoundary
      fallback={<FeatureErrorFallback />}
      onError={(error) => console.error('[Feature] Error:', error)}
    >
      <Routes>
        {/* feature routes */}
      </Routes>
    </ErrorBoundary>
  );
}
```

**Features to update:**
1. `src/features/explorer/routes.tsx` - Explorer
2. `src/features/discovery/routes.tsx` - Discovery
3. `src/features/analytics/routes.tsx` - Analytics
4. `src/features/ai/routes.tsx` - AI
5. `src/features/kpi/routes.tsx` - KPI
6. `src/features/platform/projects/routes.tsx` - Projects
7. `src/features/platform/upload-wizard/` - Upload Wizard

### 3.2 Create Reusable Error Fallback Components

**Create:** `/Users/namanagarwal/system/frontend-new/src/shared/ui/FeatureErrorFallback.tsx`

Component should:
- Show friendly error message
- Provide "Retry" button
- Option to "Go to Home"
- Display error details in dev mode
- Log to error tracking service

### 3.3 Standardize Loading States

**Audit all features** for loading states, ensure using `@lumina/design-system` components:

- **Lists/Tables:** `<TableLoadingState rows={5} />`
- **Detail Pages:** `<DetailLoadingState />`
- **Metrics:** `<MetricsLoadingState />`
- **Full Page:** `<PageLoadingState message="Loading..." />`
- **Inline:** `<LoadingState type="inline" />`

**Files likely needing updates:**
- Explorer components (FilterPanel, ActivitiesPanel, etc.)
- Analytics dashboards
- AI insights pages
- Project detail pages

### 3.4 Implement Error Notification Strategy

**Update:** Error handling utilities to distinguish:

1. **Transient errors** (network timeout) → Toast notification with retry
2. **Validation errors** (bad input) → Inline form errors
3. **Critical errors** (500, auth failure) → Error boundary fallback
4. **Not found** (404) → Empty state component

**Enhance:** `@lumina/design-system` QueryError component if needed

### Success Criteria
- [x] 7 feature-level error boundaries added
- [x] FeatureErrorFallback component created
- [x] All async operations show loading states
- [x] Error notification strategy documented
- [x] No blank screens during loading
- [x] Network errors show retry option

### Testing
- Simulate network failure (Chrome DevTools offline)
- Test invalid API responses
- Verify error boundaries catch component errors
- Check loading states appear/disappear correctly

---

## Phase 4: TypeScript Quality & Component Organization (2 days)

**Goal:** 100% type safety, eliminate `any` types, refactor large components

### 4.1 TypeScript Quality Pass

**Tasks:**
1. Search for all `any` types: `grep -r ": any" src/`
2. Replace with proper types or `unknown` + type guards
3. Ensure all function parameters are typed
4. Add return types to all functions (esp. async)
5. Use discriminated unions for variant props

**Example refinement:**
```typescript
// Before
function handleData(data: any) { ... }

// After
function handleData(data: ProcessData | null): ProcessResult {
  if (!data) return { success: false };
  // ...
}
```

### 4.2 Refactor Large Components

**Target:** Components >300 lines or >20KB file size

**Identified large files:**
- `FilterPanel.tsx` (~21KB, explorer feature)
- Check for others with: `find src/features -name "*.tsx" -size +15k`

**Refactoring strategy:**
1. Extract business logic to custom hooks
2. Split UI into smaller sub-components
3. Move pure functions to utils
4. Create compound component patterns

**Example for FilterPanel:**
```
FilterPanel.tsx (main)
├── useFilterState.ts (hook)
├── FilterHeader.tsx (sub-component)
├── FilterOptions.tsx (sub-component)
├── FilterActions.tsx (sub-component)
└── filterUtils.ts (pure functions)
```

### 4.3 Extract Business Logic to Hooks

**Pattern:**
- Component should only handle rendering
- Hooks handle data fetching, state management, side effects
- Utils handle pure transformations

**Example refactor:**
```typescript
// Before: logic in component
function DatasetPage() {
  const [data, setData] = useState(null);
  useEffect(() => { /* fetch logic */ }, []);
  // ... 200 lines of logic
  return <div>{/* UI */}</div>;
}

// After: logic in hook
function useDatasetData(id: string) {
  const query = useQuery(...);
  const computed = useMemo(() => transform(query.data), [query.data]);
  return { data: computed, ...query };
}

function DatasetPage() {
  const { data, isLoading } = useDatasetData(datasetId);
  if (isLoading) return <LoadingState />;
  return <DatasetView data={data} />;
}
```

### 4.4 Move Reusable Components to Design System

**Candidates** (find with usage grep):
- Components used in 3+ features
- Generic UI components (not feature-specific)

**Process:**
1. Identify reusable components
2. Move to `libs/shared/design-system/src/components/`
3. Add to design system exports
4. Create Storybook story
5. Update imports in features

### Success Criteria
- [x] 0 `any` types (search returns nothing)
- [x] All functions have return types
- [x] Large components refactored (<300 lines each)
- [x] Business logic extracted to hooks
- [x] 5+ reusable components moved to design system
- [x] TypeScript strict mode passes

### Testing
- Run `npx tsc --noEmit --strict`
- Manual test refactored components
- Verify no visual regressions

---

## Phase 5: State Management Clarity & Testing Foundation (2 days)

**Goal:** Clear state management strategy and testing infrastructure

### 5.1 Document State Management Layers

**Create:** `/Users/namanagarwal/system/frontend-new/docs/STATE_MANAGEMENT_GUIDE.md`

**Cover 3 layers:**

1. **Server State (TanStack Query)**
   - All backend data
   - Automatic caching, revalidation
   - Query key conventions
   - When to invalidate

2. **Client State (React Context)**
   - UI-only state (sidebar open, theme, etc.)
   - Minimal global state
   - User preferences
   - When to use Context vs useState

3. **URL State (React Router)**
   - Filters, search, pagination
   - Makes state shareable via URL
   - Use searchParams for dynamic filters
   - Example implementation

### 5.2 Implement URL State for Filters (if not already)

**Target features:**
- Explorer (filters for process variants)
- Analytics (date ranges, metric filters)
- Projects (search, sort)

**Example pattern:**
```typescript
import { useSearchParams } from 'react-router-dom';

function useExplorerFilters() {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = {
    minFrequency: Number(searchParams.get('minFreq')) || 0,
    activities: searchParams.getAll('activity'),
  };

  const setFilters = (newFilters) => {
    setSearchParams(newFilters);
  };

  return { filters, setFilters };
}
```

### 5.3 Testing Infrastructure Setup

#### Create Test Utilities

**Create:** `/Users/namanagarwal/system/frontend-new/src/test/utils.tsx`

```typescript
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

// Test wrapper with providers
export function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {ui}
      </BrowserRouter>
    </QueryClientProvider>
  );
}
```

#### Set Up MSW (Mock Service Worker)

**Install:**
```bash
cd frontend-new && npm install -D msw
```

**Create:** `/Users/namanagarwal/system/frontend-new/src/test/mocks/handlers.ts`

```typescript
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/v1/projects', (req, res, ctx) => {
    return res(ctx.json({ items: [], total: 0 }));
  }),
];
```

**Create:** `/Users/namanagarwal/system/frontend-new/src/test/setup.ts`

Configure Jest to use MSW for all tests.

### 5.4 Write Example Test Suites

**Create 3 example test files:**

1. **Utils test:** `/Users/namanagarwal/system/frontend-new/src/shared/utils/__tests__/formatters.test.ts`
   - Test formatDuration, formatPercentage, etc.
   - Pure function tests (easy, high value)

2. **Hook test:** `/Users/namanagarwal/system/frontend-new/src/features/platform/projects/hooks/__tests__/useProjectData.test.ts`
   - Use `@testing-library/react-hooks`
   - Mock API responses with MSW

3. **Component test:** `/Users/namanagarwal/system/frontend-new/src/features/platform/projects/components/__tests__/ProjectCard.test.tsx`
   - Test user interactions
   - Test loading/error states

### 5.5 Create Testing Guide

**Create:** `/Users/namanagarwal/system/frontend-new/docs/TESTING_GUIDE.md`

Include:
- How to run tests
- How to write unit tests
- How to write component tests
- How to mock API calls with MSW
- How to test hooks
- Coverage goals (>50% utils, >30% components)

### Success Criteria
- [x] STATE_MANAGEMENT_GUIDE.md created
- [x] URL state implemented in 2+ features
- [x] Test utilities created (renderWithProviders, etc.)
- [x] MSW configured
- [x] 3 example test suites passing
- [x] TESTING_GUIDE.md written
- [x] `npm run test` executes successfully

### Testing
- Run `npm run test`
- Verify all 3 example tests pass
- Check coverage report
- Test URL state (filters persist on page refresh)

---

## Phase 6: Documentation & Polish (1-2 days)

**Goal:** Complete documentation, Storybook stories, performance audit

### 6.1 Create ARCHITECTURE.md

**Create:** `/Users/namanagarwal/system/frontend-new/ARCHITECTURE.md`

**Include:**
- High-level architecture diagram
- Feature organization structure
- Data flow (Component → Hook → API → Backend)
- Design system usage
- State management layers
- Testing strategy
- Build/deployment process

### 6.2 Update README.md

**Update:** `/Users/namanagarwal/system/frontend-new/README.md`

**Add sections:**
- Quick start guide
- Development workflow
- Available scripts
- Environment variables
- Common patterns
- Troubleshooting

### 6.3 Create Storybook Stories

**Target:** 10-15 stories for shared components

**Priority components from design system:**
1. MetricCard
2. EmptyState
3. LoadingState variants
4. QueryError
5. DataTable
6. StatusBadge
7. ProcessQuestion
8. FeatureErrorFallback (new)

**Create stories:** `/Users/namanagarwal/system/frontend-new/libs/shared/design-system/src/components/**/*.stories.tsx`

### 6.4 Performance Audit

**Run Lighthouse:**
```bash
npm run build
npm run preview
# Open Chrome DevTools → Lighthouse → Run audit
```

**Target scores:**
- Performance: >90
- Accessibility: >90
- Best Practices: >90
- SEO: >80

**Optimizations if needed:**
- Code splitting (already using lazy loading)
- Image optimization
- Bundle size analysis: `npm run build -- --analyze`
- Remove unused dependencies

### 6.5 Accessibility Quick Wins

**Check:**
- All images have alt text
- Forms have proper labels
- Color contrast meets WCAG AA
- Keyboard navigation works
- Focus indicators visible
- ARIA labels on icon buttons

**Tool:**
```bash
npm install -D @axe-core/react
```

### 6.6 Create HANDOFF.md

**Create:** `/Users/namanagarwal/system/frontend-new/HANDOFF.md`

**Include:**
- What was completed (link to phases 1-6)
- What still needs work (known issues)
- Recommendations for next steps
- Technical debt items
- Performance notes
- Testing coverage summary

### Success Criteria
- [x] ARCHITECTURE.md created (10+ pages)
- [x] README.md updated
- [x] 10-15 Storybook stories created
- [x] Lighthouse score >90 (all categories)
- [x] Basic accessibility checks pass
- [x] HANDOFF.md written
- [x] All documentation reviewed and accurate

### Testing
- Read through all docs for clarity
- Run Storybook: `npm run storybook`
- Verify all stories render correctly
- Run Lighthouse audit
- Manual accessibility testing

---

## Phase Dependencies & Timeline

```
Week 1:
Day 1:     Phase 1 (0.5d) ──┐
                             ├──> Phase 2 (1d) ──┐
Day 2-3:                     │                   │
                             │                   ├──> Phase 3 (1d)
Day 4:                       │                   │
                             │                   │
Day 5:     Can start Phase 4 concurrently ──────┘

Week 2:
Day 6-7:   Phase 4 (2d) ──┐
                          ├──> Phase 5 (2d)
Day 8-9:                  │
Day 10-11: Phase 6 (1-2d) ─┘
```

**Critical path:** Phase 1 → Phase 2 → Phase 3
**Can overlap:** Phase 4 & 5 (different files)
**Final:** Phase 6 (depends on all previous)

---

## Risk Mitigation

### Risks
1. **Scope creep** - Too many "while we're here" changes
   - Mitigation: Stick to plan, track new items separately

2. **Breaking changes** - Refactoring breaks existing functionality
   - Mitigation: Manual smoke tests after each phase, Git branches

3. **Time overruns** - Phases take longer than estimated
   - Mitigation: Time-box each phase, defer nice-to-haves to Phase 6

4. **Testing gaps** - Not enough test coverage
   - Mitigation: Focus on critical paths, document testing patterns

### Rollback Plan
- Each phase on separate Git branch
- Merge to feature/temporal-workers after smoke testing
- Can cherry-pick specific commits if needed

---

## Critical Files Reference

### Phase 1 - Fix Imports
- `src/features/explorer/components/EdgeFrequencySlider.tsx:11`
- `src/features/explorer/components/ExplorerSkeleton.tsx:8`
- `src/shared/components/WorkflowElapsedTime.tsx:10`
- `src/shared/components/WorkflowProgressCard.tsx:15,17`

### Phase 2 - API Structure
- `src/features/_template/api/` (CREATE)
- `docs/API_INTEGRATION_GUIDE.md` (CREATE)
- `src/features/platform/projects/api/` (CREATE)

### Phase 3 - Error Handling
- All 7 feature `routes.tsx` files
- `src/shared/ui/FeatureErrorFallback.tsx` (CREATE)

### Phase 4 - TypeScript & Components
- `src/features/explorer/components/FilterPanel.tsx` (REFACTOR)
- Any components >300 lines
- `libs/shared/design-system/src/components/` (ADDITIONS)

### Phase 5 - Testing
- `src/test/utils.tsx` (CREATE)
- `src/test/mocks/handlers.ts` (CREATE)
- `src/test/setup.ts` (CREATE)
- `docs/STATE_MANAGEMENT_GUIDE.md` (CREATE)
- `docs/TESTING_GUIDE.md` (CREATE)

### Phase 6 - Documentation
- `ARCHITECTURE.md` (CREATE)
- `README.md` (UPDATE)
- `HANDOFF.md` (CREATE)
- Storybook stories (10-15 CREATE)

---

## Success Metrics Summary

### Week 1 Must-Have
- [x] Zero TypeScript errors
- [x] All ESLint warnings resolved
- [x] Consistent import patterns (100% @lumina)
- [x] Clear API integration layer established
- [x] Error boundaries in all features
- [x] Loading states for all async operations
- [x] Dead code removed (0 .bak files)

### Week 2 Should-Have
- [x] Storybook stories for shared components (10-15)
- [x] Unit tests for critical business logic (>50% coverage on utils)
- [x] Feature-level integration tests for main flows
- [x] Performance audit (Lighthouse >90)
- [x] Bundle size optimization (code splitting verified)
- [x] Documentation complete (ARCHITECTURE.md, guides)

### Nice-to-Have
- [ ] Accessibility audit (WCAG 2.1 AA) - basic checks only
- [ ] E2E tests (defer to future sprint)
- [ ] Performance monitoring (defer to future sprint)
- [ ] CI/CD improvements (defer to DevOps)

---

## Execution Notes

### Before Starting Each Phase
1. Create feature branch: `git checkout -b phase-X-description`
2. Review phase goals and success criteria
3. Read all relevant files first
4. Make incremental commits

### After Completing Each Phase
1. Run full test suite: `npm run test`
2. Run type check: `npm run typecheck`
3. Run linter: `npm run lint`
4. Start dev server and smoke test
5. Commit with clear message
6. Optional: Merge to feature/temporal-workers or keep separate

### Communication
- Brief update after each phase (what was done, blockers, questions)
- Flag any deviations from plan
- Document new findings in HANDOFF.md

---

## Constraints (Do NOT Change)

❌ **DO NOT** change visual design (colors, spacing, layout)
❌ **DO NOT** replace @lumina/design-system
❌ **DO NOT** change Nx monorepo structure
❌ **DO NOT** replace TanStack Query
❌ **DO NOT** modify AppShell component's UI
❌ **DO NOT** change Ant Design theme
❌ **DO NOT** remove Storybook
❌ **DO NOT** switch bundlers (keep Rspack)

✅ **CAN** refactor internal component structure (same UI output)
✅ **CAN** reorganize files/folders
✅ **CAN** rename poorly named components/files
✅ **CAN** add utilities/hooks
✅ **CAN** improve TypeScript types
✅ **CAN** add tests
✅ **CAN** fix bugs
✅ **CAN** improve performance
✅ **CAN** update documentation

---

## Plan Status

**Phase 1:** Ready to execute
**Phase 2:** Ready after Phase 1
**Phase 3:** Ready after Phase 2
**Phase 4:** Ready after Phase 3 (can overlap with 5)
**Phase 5:** Ready after Phase 3 (can overlap with 4)
**Phase 6:** Ready after Phases 4 & 5

**Last Updated:** 2026-01-07
**Next Step:** Begin Phase 1 execution upon approval
