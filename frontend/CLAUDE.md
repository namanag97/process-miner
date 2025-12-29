# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Lumina (new enterprise app - port 4300)
npx nx serve lumina               # Dev server
npx nx build lumina               # Production build
npx nx test lumina                # Tests
npx nx lint lumina                # Lint
npx nx typecheck lumina           # Type check

# Process Mining (legacy app - port 4200)
npx nx serve process-mining       # Dev server
npx nx build process-mining       # Production build

# Utilities
npx nx graph                      # View dependency graph
npx nx affected:test              # Test affected projects
npx nx reset                      # Clear Nx cache
```

## Architecture

**Nx monorepo** with React 19, Rsbuild (Rspack-based bundler), TanStack Query for server state.

### Applications

**`apps/lumina/`** - New enterprise process mining platform (primary development)
- Domain-driven design with vertical slice architecture
- Ant Design 6 with compact algorithm
- Pages are thin wrappers that compose domain components
- Port 4300 in development

**`apps/process-mining/`** - Legacy app (maintenance mode)
- Original SPA with mixed concerns
- Port 4200 in development

### Library Structure

**Shared Libraries:**
- `libs/shared/design-system/` (`@lumina/design-system`) - Theme, tokens, reusable components (AppShell, MetricCard, DataGrid)
- `libs/api/` (`@frontend/api`) - React Query hooks wrapping SDK (legacy)
- `libs/ui/` (`@frontend/ui`) - Legacy shared components
- `libs/process-graph/` (`@frontend/process-graph`) - ReactFlow visualization utilities
- `libs/design-tokens/` (`@frontend/design-tokens`) - Legacy design tokens

**Domain Libraries** (Vertical Slices - Feature-Complete Modules):
- `libs/domains/data-hub/` (`@lumina/data-hub`) - Event log management, upload wizard, quality reports
- `libs/domains/process-explorer/` (`@lumina/process-explorer`) - DFG visualization, discovery, filtering
- `libs/domains/variants/` (`@lumina/variants`) - Variant analysis and comparison
- `libs/domains/analytics/` (`@lumina/analytics`) - Performance metrics, bottlenecks, KPIs
- Each domain exports hooks + components for its feature area

**Key Dependencies:**
- `process-mining-sdk` - TypeScript SDK from `../sdk` (linked via `file:../sdk` in package.json)
- SDK is auto-generated from backend OpenAPI spec using openapi-typescript-codegen

## SDK Integration

**Critical:** Frontend depends on locally linked SDK from `../sdk`.

**To regenerate SDK after backend changes:**
```bash
# 1. Start backend on port 8001
cd ../backend && source .venv/bin/activate && uvicorn src.api.main:app --reload --port 8001

# 2. Generate and build SDK
cd ../sdk && npm run generate && npm run build

# 3. Restart frontend dev server
```

## Path Aliases (Import Patterns)

Domain libraries use scoped imports defined in `tsconfig.base.json`:

```typescript
// Design system
import { AppShell, MetricCard, theme } from '@lumina/design-system'

// Domain libraries
import { LogList, useLogs } from '@lumina/data-hub'
import { ProcessMap, useDFG } from '@lumina/process-explorer'
import { VariantList, useVariants } from '@lumina/variants'
import { KPIDashboard, usePerformance } from '@lumina/analytics'

// Legacy libraries (process-mining app)
import { Button } from '@frontend/ui'
import { useProcesses } from '@frontend/api'
```

## Working with Domain Libraries

Domain libraries follow a **vertical slice architecture** - each domain is self-contained with:
- **Hooks** (`hooks/use-*.ts`) - React Query wrappers for SDK calls
- **Components** (`components/*.tsx`) - UI components specific to that domain
- **Exports** (`index.ts`) - Public API of the domain

**Example: Creating a new page using domains**
```typescript
// apps/lumina/src/pages/analytics/AnalyticsPage.tsx
import { KPIDashboard, usePerformance } from '@lumina/analytics'

export default function AnalyticsPage() {
  const { data } = usePerformance(logId)
  return <KPIDashboard data={data} />
}
```

**Adding a new domain library:**
```bash
npx nx g @nx/react:library --name=my-domain --directory=libs/domains/my-domain --importPath=@lumina/my-domain
```

Then add to `tsconfig.base.json`:
```json
"@lumina/my-domain": ["libs/domains/my-domain/src/index.ts"],
"@lumina/my-domain/*": ["libs/domains/my-domain/src/*"]
```

## Authentication

**Process Mining app**: Mock auth at `apps/process-mining/src/context/AuthContext.tsx`

**Lumina app**: Mock auth at `apps/lumina/src/context/AuthContext.tsx`
- Accepts any credentials (username/password)
- Stores mock token in localStorage
- Protected routes check for token presence
- No backend integration yet

## Common Issues

**SDK changes not reflecting:**
```bash
cd ../sdk && npm run build
npx nx reset  # Clear Nx cache
```

**Type errors after SDK regeneration:** Update hooks in `libs/api/src/lib/hooks/`

## Development Workflow

### Standard Development
1. Start backend: `cd ../backend && make dev` (runs on :8001)
2. Start frontend: `npx nx serve lumina` (runs on :4300)
3. Access:
   - Lumina app: http://localhost:4300
   - Process Mining app: `npx nx serve process-mining` → http://localhost:4200
   - Backend API docs: http://localhost:8001/docs

### When Switching Between Apps
Both apps can run simultaneously on different ports, but they share the same SDK dependency. If you encounter SDK-related issues after switching apps, restart the dev server.

## Project Documentation

- `FEPLAN.md` - Comprehensive frontend implementation plan for Lumina (16 screens, 237 business activities)
- `HANDOFF.md` - Current implementation status and next steps
- `../CONTRIBUTING.md` - Git workflow (two-branch: `dev` → `main`)
- `../sdk/` - TypeScript SDK source (auto-generated from backend OpenAPI)
