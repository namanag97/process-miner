# FRONTEND DEV TASK: Audit All Pages & Components

## Your Mission

Audit `/frontend-new/src/` completely.

## What CTO Needs

### 1. Routes Inventory

Find routing config in `App.tsx` and feature routes, list ALL routes:

| Route Path | Component | Purpose | Protected? |
| ---------- | --------- | ------- | ---------- |

### 2. API Integration

For each page, what API does it call?

| Page | API Endpoint Called | Hook/Service Used | Works? |
| ---- | ------------------- | ----------------- | ------ |

### 3. Process Visualization Components

| Component | Location | Purpose | Dependencies |
| --------- | -------- | ------- | ------------ |

Look in:

- `/frontend-new/src/features/explorer/components/`
- Any graph/visualization components

### 4. State Management

| Store/Context | Purpose | What Data? |
| ------------- | ------- | ---------- |

Look for:

- React Context providers
- State management libraries
- API hooks

### 5. Console Errors

Navigate each route in browser, report any console errors:

| Route | Error? | Error Message |
| ----- | ------ | ------------- |

## Files to Examine

- `/frontend-new/src/App.tsx` — Main routes
- `/frontend-new/src/features/*/routes.tsx` — Feature routes
- `/frontend-new/src/features/*/hooks/` — API hooks
- `/frontend-new/src/context/` — Global state

## Output

Update `/docs/cto/CTO_KNOWLEDGE_BASE.md` Frontend section.

Report format:

```
Frontend Audit Complete:
- X total routes
- Y routes connected to real APIs
- Z routes use mock data
- Top issues: [list]
```
