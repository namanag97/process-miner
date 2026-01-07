# Senior Frontend Developer - UI Cleanup & Preparation Brief

**Project:** Process Mining SaaS Platform - Frontend Modernization
**Date:** January 7, 2026
**Priority:** High
**Timeline:** 1-2 weeks (before backend API integration)

---

## 🎯 Mission

**Refactor and solidify the frontend codebase** while preserving the current design system and UI/UX. Prepare the application for seamless backend integration by improving code organization, removing technical debt, and establishing best practices for a production-grade SaaS application.

**Key Constraint:** **DO NOT change the visual design or user experience.** Keep the current look and feel 100% intact.

---

## 📋 Current State

### What's Working
✅ Design system is solid (@lumina/design-system)
✅ Visual UI is approved and looks professional
✅ Nx monorepo structure is in place
✅ TypeScript strict mode enabled
✅ Ant Design 5.x + custom components
✅ TanStack Query for server state
✅ Rspack for fast builds
✅ Storybook configured

### What Needs Improvement
⚠️ Code organization inconsistencies
⚠️ TypeScript errors in unused/legacy files
⚠️ Mixed import patterns (@lumina vs direct imports)
⚠️ Some components tightly coupled to mock data
⚠️ Incomplete migration from old architecture
⚠️ Missing error boundaries in some features
⚠️ Inconsistent loading states
⚠️ No clear API integration patterns
⚠️ Limited test coverage

### Tech Stack
```
Frontend:
- React 19 + TypeScript (strict mode)
- Ant Design 5.x (UI components)
- @lumina/design-system (custom design system)
- TanStack Query v5 (server state management)
- React Router v6 (client-side routing)
- Rspack (bundler)
- Nx (monorepo tooling)
- Storybook (component documentation)
- Jest + React Testing Library (testing)

Backend API:
- FastAPI (Python)
- OpenAPI 3.0 spec at http://localhost:8001/openapi.json
- RESTful endpoints at /api/v1/*
- JWT authentication (being refactored)
```

---

## 🎯 Primary Goals

### 1. **Code Organization & Architecture** (Priority: Critical)

**Objective:** Establish clear architectural patterns that scale for a SaaS product.

**Tasks:**
- [ ] **Audit and document current architecture**
  - Map out all features and their dependencies
  - Document component hierarchy
  - Identify circular dependencies or coupling issues

- [ ] **Standardize feature structure** (Feature-Sliced Design)
  ```
  src/features/{feature-name}/
  ├── api/              # API calls (React Query hooks)
  ├── components/       # Feature-specific components
  ├── hooks/            # Feature-specific hooks
  ├── pages/            # Route components
  ├── types.ts          # TypeScript interfaces
  ├── routes.tsx        # Route definitions
  └── index.ts          # Public exports
  ```

- [ ] **Consolidate import patterns**
  - Enforce @lumina/design-system for all design system imports
  - Document when to use direct Ant Design vs @lumina wrappers
  - Update all components to use consistent imports

- [ ] **Remove dead code**
  - Delete unused hooks (useAuth.ts.bak, useWorkflowPolling.ts.bak, etc.)
  - Remove legacy shim files
  - Clean up commented-out code
  - Remove unused dependencies

### 2. **API Integration Readiness** (Priority: Critical)

**Objective:** Prepare clean, type-safe patterns for backend integration.

**Tasks:**
- [ ] **Create API integration layer**
  ```typescript
  src/features/{feature}/api/
  ├── queries.ts        # React Query queries (GET requests)
  ├── mutations.ts      # React Query mutations (POST/PUT/DELETE)
  ├── types.ts          # Request/response types
  └── endpoints.ts      # Endpoint URL constants
  ```

- [ ] **Establish data fetching patterns**
  - Standardize React Query hook naming (`useGetX`, `useCreateX`, `useUpdateX`)
  - Define error handling strategy (toast notifications, error boundaries)
  - Define loading state patterns (skeletons vs spinners)
  - Set up query invalidation strategies

- [ ] **Type safety for API**
  - Ensure all API calls use TypeScript interfaces
  - Generate types from OpenAPI spec (libs/openapi-sdk/)
  - Create type guards for runtime validation

- [ ] **Mock data strategy**
  - Move all mock data to dedicated `/mocks` folders
  - Add feature flags to toggle between mock/real data
  - Document how to switch between modes

### 3. **Error Handling & Loading States** (Priority: High)

**Objective:** Provide excellent UX during async operations and failures.

**Tasks:**
- [ ] **Implement error boundaries**
  - Add top-level error boundary in App.tsx (already exists - verify)
  - Add feature-level error boundaries
  - Create fallback UI components

- [ ] **Standardize loading states**
  - Audit all async operations
  - Use @lumina/design-system loading components
  - Implement skeleton screens for list/detail views
  - Add loading indicators for mutations

- [ ] **Error notification strategy**
  - Use toast notifications for transient errors
  - Use error pages for critical failures
  - Display validation errors inline on forms
  - Provide retry mechanisms where appropriate

### 4. **TypeScript & Code Quality** (Priority: High)

**Objective:** Achieve 100% type safety and eliminate compilation errors.

**Tasks:**
- [ ] **Fix all TypeScript errors**
  - Current count: 7 errors (WorkflowProgressCard, EdgeFrequencySlider, etc.)
  - Enable strict null checks if not already enabled
  - Fix any implicit any types

- [ ] **Improve type definitions**
  - Add proper types to all component props
  - Use discriminated unions for variant props
  - Avoid `any` - use `unknown` with type guards if needed

- [ ] **Code linting & formatting**
  - Ensure ESLint passes with no warnings
  - Configure Prettier (if not already)
  - Set up pre-commit hooks (Husky + lint-staged)

### 5. **Component Organization** (Priority: Medium)

**Objective:** Make components reusable, testable, and maintainable.

**Tasks:**
- [ ] **Component composition patterns**
  - Break down large components (>300 lines) into smaller pieces
  - Extract business logic into custom hooks
  - Separate presentational from container components

- [ ] **Shared component library**
  - Move reusable components to @lumina/design-system
  - Document component APIs in Storybook
  - Add prop validation

- [ ] **Form handling**
  - Standardize form library (React Hook Form recommended)
  - Create reusable form components (FormInput, FormSelect, etc.)
  - Consistent validation patterns

### 6. **State Management Clarity** (Priority: Medium)

**Objective:** Clear separation of client state vs server state.

**Tasks:**
- [ ] **Server state (TanStack Query)**
  - All API data should use React Query
  - Document query key naming conventions
  - Set up query devtools for debugging

- [ ] **Client state (React Context or Zustand)**
  - Identify what needs to be in client state
  - Minimize use of global state
  - Consider Zustand for complex client state (if needed)

- [ ] **URL state (React Router)**
  - Use URL params for filterable/shareable state
  - Implement search params for pagination/sorting

### 7. **Testing Infrastructure** (Priority: Medium)

**Objective:** Establish testing patterns for confidence in refactoring.

**Tasks:**
- [ ] **Unit tests for utilities**
  - Test pure functions
  - Test custom hooks (React Hooks Testing Library)
  - Aim for >80% coverage on utils

- [ ] **Component tests**
  - Test user interactions
  - Test error states
  - Test loading states

- [ ] **Integration tests**
  - Test critical user flows (upload, analyze, explore)
  - Mock API calls with MSW (Mock Service Worker)

---

## 📐 Architectural Principles to Follow

### 1. **Single Responsibility Principle**
Each component/hook/module should do ONE thing well.

### 2. **Separation of Concerns**
```
Component (UI)
  ↓ uses
Hook (Business Logic)
  ↓ uses
API Module (Data Fetching)
  ↓ calls
Backend API
```

### 3. **Don't Repeat Yourself (DRY)**
Extract common patterns into reusable hooks/components.

### 4. **Progressive Enhancement**
Start with basic functionality, add polish incrementally.

### 5. **Type Safety First**
No `any` types. Everything should be typed.

---

## 🚫 What NOT to Change

### Preserve These:
❌ **DO NOT** change the visual design (colors, spacing, layout)
❌ **DO NOT** replace @lumina/design-system with another UI library
❌ **DO NOT** change the Nx monorepo structure
❌ **DO NOT** replace TanStack Query with Redux/MobX/etc.
❌ **DO NOT** modify the AppShell component's UI (sidebar, navigation)
❌ **DO NOT** change the Ant Design theme configuration
❌ **DO NOT** remove Storybook
❌ **DO NOT** switch bundlers (keep Rspack)

### You CAN:
✅ Refactor internal component structure (same UI output)
✅ Reorganize files/folders
✅ Rename poorly named components/files
✅ Add new utilities/hooks
✅ Improve TypeScript types
✅ Add tests
✅ Fix bugs
✅ Improve performance
✅ Update documentation

---

## 📊 Success Criteria

### Must Have (Week 1)
- [ ] Zero TypeScript compilation errors
- [ ] All ESLint warnings resolved
- [ ] Consistent import patterns (100% using @lumina where applicable)
- [ ] Clear API integration layer structure established
- [ ] Error boundaries in all feature modules
- [ ] Loading states for all async operations
- [ ] Dead code removed (0 .bak files, 0 unused imports)

### Should Have (Week 2)
- [ ] Storybook stories for all shared components
- [ ] Unit tests for critical business logic (>50% coverage)
- [ ] Feature-level integration tests for main flows
- [ ] Performance audit (Lighthouse score >90)
- [ ] Bundle size optimization (code splitting)
- [ ] Documentation updated (README, ARCHITECTURE.md)

### Nice to Have (If Time Permits)
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] E2E tests with Playwright/Cypress
- [ ] Performance monitoring setup (Sentry, LogRocket)
- [ ] CI/CD pipeline improvements

---

## 📚 Key Files to Review

### Start Here:
1. **`frontend-new/UI_ARCHITECTURE_REPORT.md`** - Understand current architecture
2. **`frontend-new/src/App.tsx`** - Application entry point
3. **`frontend-new/libs/shared/design-system/src/index.ts`** - Design system exports
4. **`frontend-new/tsconfig.json`** - TypeScript configuration
5. **`frontend-new/rspack.config.js`** - Build configuration

### Critical Features to Focus On:
```
src/features/
├── explorer/          # Process mining visualization (CORE FEATURE)
├── platform/          # Projects, upload wizard (CRITICAL PATH)
│   ├── projects/      # Project management
│   └── upload-wizard/ # Dataset upload flow
├── analytics/         # Performance dashboards
└── ai/                # AI insights, predictions
```

### Design System Components:
```
libs/shared/design-system/src/
├── components/        # UI components (AppShell, MetricCard, etc.)
├── theme.ts           # Design tokens & Ant theme
├── api/               # API client & React Query setup
└── hooks/             # Reusable hooks
```

---

## 🔧 Development Workflow

### Setup
```bash
cd frontend-new
npm install
npm run start    # Dev server on :4200
npm run test     # Run Jest tests
npm run lint     # ESLint
npm run typecheck # TypeScript validation
npm run storybook # Storybook on :6006
```

### Environment
```bash
# .env file
VITE_API_BASE_URL=http://localhost:8001  # Backend API
VITE_ENABLE_DEV_TOOLS=true               # Dev console
VITE_ENABLE_MOCK_DATA=false              # Use real API (when ready)
```

### Git Workflow
```bash
# Current branch: feature/temporal-workers
# DO NOT merge to main without approval

git checkout -b feat/fe-cleanup
# Make changes
git add .
git commit -m "refactor: improve component organization"
# Push and create PR
```

---

## 🐛 Known Issues to Address

### TypeScript Errors (7 total)
1. `EdgeFrequencySlider.tsx` - Missing design-system import
2. `ExplorerSkeleton.tsx` - Missing design-system import
3. `WorkflowElapsedTime.tsx` - Missing design-system import
4. `WorkflowProgressCard.tsx` - Missing design-system import + missing useWorkflowPolling
5. `useAuth.ts` - Missing @/src/api/generated import

### Architectural Issues
1. Some components import from `@/src/shared/design-system` (old path) instead of `@lumina/design-system`
2. Unused `.bak` files in `src/shared/hooks/`
3. Mixed API client usage (some use instrumentedFetch, some use axios directly)
4. Inconsistent error handling across features

---

## 📖 Process Mining SaaS Context

### What This App Does
Users can:
1. **Upload event logs** (CSV/OCEL files)
2. **Map columns** to process semantics (case ID, activity, timestamp)
3. **Discover process models** (DFG, Petri nets, BPMN)
4. **Analyze performance** (bottlenecks, cycle time, throughput)
5. **Explore variants** and deviations
6. **Train ML models** for predictions
7. **Run simulations** for what-if analysis

### Critical User Flows
```
1. Upload Flow:
   Upload → Detect Columns → Map Columns → Ingest → Ready

2. Analysis Flow:
   Select Dataset → Choose Algorithm → Run Analysis → View Results

3. Exploration Flow:
   Select Dataset → Apply Filters → Explore DFG → Drill Down
```

### UX Priorities
- **Fast feedback** - Users should see progress immediately
- **Error recovery** - Clear error messages with retry options
- **Progressive disclosure** - Don't overwhelm with options
- **Professional** - Enterprise SaaS feel, not toy demo

---

## 💡 Recommended Patterns & Libraries

### API Integration
```typescript
// ✅ GOOD: Using React Query
const { data, isLoading, error } = useGetDatasets();

if (isLoading) return <LoadingState type="table" />;
if (error) return <QueryError error={error} />;

return <DataTable data={data.items} />;
```

### Form Handling
```typescript
// Consider: React Hook Form
import { useForm } from 'react-hook-form';

const { register, handleSubmit, formState: { errors } } = useForm();
```

### File Uploads
```typescript
// Existing pattern in upload-wizard/
// Use presigned URLs for large files
// Show progress bar with percentage
// Support drag & drop
```

### Error Boundaries
```typescript
// Per-feature boundaries
<ErrorBoundary fallback={<FeatureError />}>
  <FeatureComponent />
</ErrorBoundary>
```

---

## 📞 Communication & Handoff

### Daily Updates
Please provide brief daily updates:
- What you worked on
- Blockers (if any)
- Questions for stakeholders

### Questions to Ask
- "Where is the OpenAPI spec?" → http://localhost:8001/openapi.json
- "How do I run the backend?" → See backend/README.md
- "What's the auth strategy?" → JWT (being refactored, will provide details)
- "Can I change component X?" → If visual output stays same, yes
- "Should I use Zustand/Redux?" → Prefer React Query + Context (minimal client state)

### Code Review Expectations
- Keep PRs focused (<500 lines changed)
- Include before/after screenshots for UI changes
- Write clear commit messages
- Add tests for new utilities/hooks
- Update Storybook for new components

---

## 📝 Deliverables

### End of Week 1
1. **Architecture Document** (`ARCHITECTURE.md`)
   - Component hierarchy diagram
   - Data flow documentation
   - API integration patterns

2. **Refactored Codebase**
   - Zero TypeScript errors
   - Consistent imports
   - Dead code removed

3. **Testing Foundation**
   - Jest configured properly
   - Example tests for 2-3 components
   - Testing guide for team

### End of Week 2
1. **Production-Ready Code**
   - All features tested
   - Error handling complete
   - Loading states polished

2. **Developer Documentation**
   - Component catalog (Storybook)
   - API integration guide
   - Common patterns guide

3. **Handoff Document**
   - What was changed
   - What still needs work
   - Recommendations for next steps

---

## 🎓 Resources

### Documentation
- **Nx Docs:** https://nx.dev/
- **TanStack Query:** https://tanstack.com/query/latest
- **Ant Design:** https://ant.design/
- **React Router:** https://reactrouter.com/
- **TypeScript Handbook:** https://www.typescriptlang.org/docs/

### Internal Docs
- `frontend-new/UI_ARCHITECTURE_REPORT.md` - Current architecture
- `frontend-new/README.md` - Getting started
- `backend/CLAUDE.md` - Backend architecture
- OpenAPI Spec: http://localhost:8001/docs

### Similar Projects (for inspiration)
- Linear (UI polish, performance)
- Notion (component composition)
- Vercel Dashboard (clean architecture)

---

## ✅ Definition of Done

A feature/component is considered "done" when:
- [ ] TypeScript compiles with no errors
- [ ] ESLint passes with no warnings
- [ ] Unit tests written and passing
- [ ] Storybook story created (for shared components)
- [ ] Error states handled
- [ ] Loading states implemented
- [ ] Responsive design tested
- [ ] Code reviewed and approved
- [ ] Documentation updated

---

## 🚀 Getting Started Checklist

### Day 1
- [ ] Clone repo and run `npm install`
- [ ] Start dev server and verify it works
- [ ] Read `UI_ARCHITECTURE_REPORT.md`
- [ ] Run TypeScript (`npm run typecheck`) and note all errors
- [ ] Run linter (`npm run lint`) and note all warnings
- [ ] Browse Storybook (`npm run storybook`)
- [ ] Open backend API docs (http://localhost:8001/docs)

### Day 2-3
- [ ] Fix all TypeScript errors
- [ ] Remove dead code (.bak files, unused imports)
- [ ] Standardize import patterns
- [ ] Document current architecture

### Day 4-7
- [ ] Establish API integration patterns
- [ ] Add error boundaries
- [ ] Standardize loading states
- [ ] Write first round of tests

### Day 8-14
- [ ] Polish remaining features
- [ ] Expand test coverage
- [ ] Update Storybook
- [ ] Write final documentation

---

## 🎯 Final Note

**Goal:** Make this codebase a joy to work with.

A senior developer 6 months from now should be able to:
- Understand the architecture in 30 minutes
- Add a new feature without touching existing code
- Fix a bug with confidence it won't break something else
- Write tests without fighting the framework

**Quality over speed.** Take the time to do it right. The backend integration will go 10x faster with a solid frontend foundation.

---

**Questions?** Ask before making major architectural decisions.

**Git Commit:** Current checkpoint is `0ba38a7` - "Restore beautiful UI from 06eb052 checkpoint (Naman approved)"

**Good luck! 🚀**
