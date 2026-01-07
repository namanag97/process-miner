# Frontend Features CLAUDE.md

## Overview
Feature modules implementing the main application functionality. Each feature is self-contained with its own pages, components, hooks, and API layer.

## Feature Modules

### ai/
AI Assistant feature for natural language interaction with process mining.
- Chat interface
- Query processing
- Insight generation

### analytics/
Analytics dashboards and visualizations.
- Performance metrics
- Bottleneck analysis
- Trend charts

### discovery/
Process discovery features.
- Model discovery algorithms
- DFG visualization
- Process map rendering

### explorer/
Data exploration and navigation.
- Dataset browsing
- Event log inspection
- Case exploration

### kpi/
KPI management and tracking.
- KPI definitions
- Target setting
- Performance monitoring

### platform/
Core platform features.
- Settings and preferences
- Project management
- Upload wizard
- User profile

## Feature Structure Pattern

```
{feature}/
├── index.ts              # Public exports
├── pages/                # Route page components
│   ├── {Feature}ListPage.tsx
│   └── {Feature}DetailPage.tsx
├── components/           # Feature-specific UI components
├── hooks/                # Feature-specific React hooks
├── api/                  # TanStack Query queries/mutations
│   ├── queries.ts
│   └── mutations.ts
└── types.ts              # TypeScript types
```

## Guidelines

- Features should NOT import from other features
- Use shared components from `@/shared/components`
- Export only public API through `index.ts`
- Keep feature-specific logic isolated
