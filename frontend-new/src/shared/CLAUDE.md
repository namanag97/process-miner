# Frontend Shared CLAUDE.md

## Overview
Shared utilities, components, and hooks used across all features. This is the common foundation layer.

## Directory Structure

```
shared/
├── components/      # Reusable UI components
├── context/         # React contexts
├── core/            # Core utilities and plugins
├── hooks/           # Shared React hooks
├── lib/             # Utility libraries
├── ui/              # Base UI primitives (Ant Design wrappers)
├── config/          # Shared configuration
└── index.ts         # Public exports
```

## Key Directories

### components/
Reusable UI components that are feature-agnostic:
- Layout components
- Form components
- Data display components

### hooks/
Shared React hooks:
- `useDebounce`
- `useLocalStorage`
- `useMediaQuery`
- API-related hooks

### lib/
Utility functions:
- Date formatting
- Number formatting
- Validation helpers

### ui/
Base UI primitives wrapping Ant Design:
- Custom themed components
- Extended Ant Design components

### context/
React context providers:
- Theme context
- Auth context
- Toast/notification context

## Import Pattern

```typescript
// From features, import via alias
import { Button, Card } from '@/shared/components';
import { useDebounce } from '@/shared/hooks';
import { formatDate } from '@/shared/lib';
```

## Guidelines

- Keep shared code truly generic
- No feature-specific logic
- Document complex utilities
- Prefer composition over configuration
