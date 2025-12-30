# HANDOFF.md - Frontend Development Status

> **Last Updated**: 2024-12-30T13:00:00+05:30
> **Project**: Process Mining Platform Frontend
> **Location**: `/Users/namanagarwal/system/frontend-new`

---

## Quick Start

```bash
cd /Users/namanagarwal/system/frontend-new
npx nx serve frontend-new --port=4300
# Opens at http://localhost:4300
```

---

## Current State (DO NOT HALLUCINATE)

### ✅ COMPLETED - Phase 0

| Item                      | Status  | Files                                    |
| ------------------------- | ------- | ---------------------------------------- |
| Nx + Rsbuild setup        | ✅ Done | `package.json`, `rspack.config.js`       |
| Design tokens             | ✅ Done | `libs/shared/design-system/src/theme.ts` |
| AppShell + Sidebar        | ✅ Done | `.../components/AppShell.tsx`            |
| Mock Auth                 | ✅ Done | `src/context/AuthContext.tsx`            |
| All Routes (placeholders) | ✅ Done | `src/App.tsx`                            |
| Home Dashboard            | ✅ Done | `src/pages/HomePage.tsx`                 |
| Login Page                | ✅ Done | `src/pages/LoginPage.tsx`                |

### 🔄 IN PROGRESS - Nothing

### ⏳ NOT STARTED

| Phase | Feature             | Priority |
| ----- | ------------------- | -------- |
| 1     | Settings Pages      | High     |
| 1     | Notification Center | High     |
| 2     | Event Logs List     | Critical |
| 2     | Upload Wizard       | Critical |
| 3     | Process Explorer    | Critical |
| 4     | Analytics Dashboard | Medium   |

---

## Available Imports

```typescript
// Design System (verified working)
import {
  AppShell,
  MetricCard,
  EmptyState,
  PageHeader,
  tokens,
  luminaTheme,
  toast,
  notify,
  SDKProvider,
  useSDK,
  formatDuration,
  formatCompactNumber,
} from '@lumina/design-system';

// Auth Context
import { useAuth, AuthProvider } from './context/AuthContext';
```

---

## Mandatory Documentation

Before implementing ANY feature, read these files:

| Doc               | Path                                            | Purpose                            |
| ----------------- | ----------------------------------------------- | ---------------------------------- |
| Feature Manifest  | `../frontend/files/FEATURE_MANIFEST.md`         | Feature specs, acceptance criteria |
| Design System     | `../frontend/files/DESIGN_SYSTEM.md`            | Component specs, tokens            |
| Info Architecture | `../frontend/files/INFORMATION_ARCHITECTURE.md` | Routes, page layouts               |
| Patterns          | `../frontend/files/PATTERNS_AND_RECIPES.md`     | Layout patterns                    |
| Design Tokens     | `../docs/Design System Doc.md`                  | Extracted tokens from Celonis      |

---

## Anti-Hallucination Rules

1. **Check before assuming**: Verify files exist before importing
2. **Use ONLY documented tokens**: No magic numbers for colors/spacing
3. **Follow naming conventions**: `use{Resource}`, `use{Action}{Resource}`
4. **Implement ALL states**: loading, error, empty, success

---

## Update Instructions

When completing work, update this file:

1. Move items from "NOT STARTED" → "COMPLETED"
2. Update "Last Updated" timestamp
3. Add new files to the "Files" column
4. Keep entries concise (1 line per item)

---

## SDK Status

- **Linked**: `process-mining-sdk@file:../sdk`
- **Mock Mode**: SDKContext returns mock data
- **Real Backend**: Start on port 8001, regenerate SDK

---

## Known Issues

_None currently_

---

## Agent Changelog

| Date       | Agent/Session | Changes Made                      |
| ---------- | ------------- | --------------------------------- |
| 2024-12-30 | Initial       | Created project, Phase 0 complete |
