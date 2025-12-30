# DESIGN_TOKENS.md — Visual Language Reference

> [!TIP]
> Always use tokens via the `tokens` object from `@lumina/design-system` or CSS variables. Never use hardcoded hex values.

---

## Quick Reference

| Category   | Import                       | Usage      |
| ---------- | ---------------------------- | ---------- |
| Colors     | `tokens.colors.primary[500]` | `#2563EB`  |
| Spacing    | `tokens.spacing[4]`          | `16px`     |
| Radius     | `tokens.radius.md`           | `6px`      |
| Shadow     | `tokens.shadow.xs`           | Box shadow |
| Typography | `tokens.fontSize.base`       | `14px`     |

---

## 1. Colors

**Source:** [libs/shared/design-system/src/theme.ts](file:///Users/namanagarwal/system/frontend-new/libs/shared/design-system/src/theme.ts)

### Brand Palette

| Token         | CSS Variable          | Hex       | Usage                      |
| ------------- | --------------------- | --------- | -------------------------- |
| `primary-50`  | `--color-primary-50`  | `#EBF5FF` | Backgrounds, selected rows |
| `primary-100` | `--color-primary-100` | `#D6EBFF` | Hover states               |
| `primary-500` | `--color-primary-500` | `#2563EB` | Main CTAs, links, active   |
| `primary-600` | `--color-primary-600` | `#1D4ED8` | Hover on primary           |
| `primary-700` | `--color-primary-700` | `#1E40AF` | Pressed states             |

### Semantic Palette

| Category | Token         | Hex       | Usage                      |
| -------- | ------------- | --------- | -------------------------- |
| Success  | `success-50`  | `#ECFDF5` | Success backgrounds        |
| Success  | `success-500` | `#10B981` | Completed, positive trends |
| Warning  | `warning-50`  | `#FFFBEB` | Warning backgrounds        |
| Warning  | `warning-500` | `#F59E0B` | Bottlenecks, delays        |
| Error    | `error-50`    | `#FEF2F2` | Error backgrounds          |
| Error    | `error-500`   | `#EF4444` | Violations, failures       |
| Info     | `info-500`    | `#3B82F6` | System information         |

### Neutral Palette

| Token         | Hex       | Usage                 |
| ------------- | --------- | --------------------- |
| `neutral-0`   | `#FFFFFF` | Page background       |
| `neutral-50`  | `#F9FAFB` | Card hover, subtle bg |
| `neutral-100` | `#F3F4F6` | Sidebar, dividers     |
| `neutral-200` | `#E5E7EB` | Borders               |
| `neutral-400` | `#9CA3AF` | Disabled text, icons  |
| `neutral-500` | `#6B7280` | Secondary text        |
| `neutral-700` | `#374151` | Primary text          |
| `neutral-900` | `#111827` | Headings              |

---

## 2. Typography

**Font Stack:** `"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`

| Token           | Size | Weight | Usage                    |
| --------------- | ---- | ------ | ------------------------ |
| `fontSize.xs`   | 11px | 400    | Micro-labels, timestamps |
| `fontSize.sm`   | 12px | 500    | Table cells, metadata    |
| `fontSize.base` | 14px | 400    | Body text, inputs        |
| `fontSize.md`   | 15px | 400    | Emphasized body          |
| `fontSize.lg`   | 16px | 500    | Subheadings              |
| `fontSize.xl`   | 18px | 600    | Section headers          |
| `fontSize.3xl`  | 24px | 600    | Page titles              |
| `fontSize.4xl`  | 32px | 700    | Hero text                |

### Font Weights

| Token                 | Value | Usage           |
| --------------------- | ----- | --------------- |
| `fontWeight.regular`  | 400   | Body text       |
| `fontWeight.medium`   | 500   | Labels, buttons |
| `fontWeight.semibold` | 600   | Headings        |
| `fontWeight.bold`     | 700   | Emphasis        |

---

## 3. Spacing & Radius

**Base Unit:** 4px

| Token        | Value | Usage                       |
| ------------ | ----- | --------------------------- |
| `spacing[1]` | 4px   | Tight gaps                  |
| `spacing[2]` | 8px   | Button padding-y            |
| `spacing[3]` | 12px  | Input padding               |
| `spacing[4]` | 16px  | Card padding, standard gaps |
| `spacing[6]` | 24px  | Page margins, section gaps  |
| `spacing[8]` | 32px  | Large sections              |

### Border Radius

| Token         | Value  | Usage           |
| ------------- | ------ | --------------- |
| `radius.sm`   | 4px    | Small elements  |
| `radius.md`   | 6px    | Buttons, inputs |
| `radius.lg`   | 8px    | Cards, modals   |
| `radius.xl`   | 12px   | Large cards     |
| `radius.full` | 9999px | Avatars, pills  |

---

## 4. Shadows

| Token          | Value                           | Usage               |
| -------------- | ------------------------------- | ------------------- |
| `shadow.xs`    | `0 1px 2px rgba(0,0,0,0.04)`    | Default cards       |
| `shadow.sm`    | `0 1px 3px rgba(0,0,0,0.08)`    | Raised elements     |
| `shadow.md`    | `0 4px 6px rgba(0,0,0,0.1)`     | Popovers, dropdowns |
| `shadow.lg`    | `0 10px 15px rgba(0,0,0,0.1)`   | Modals              |
| `shadow.focus` | `0 0 0 3px rgba(37,99,235,0.2)` | Input focus rings   |

---

## 5. Animation Durations

| Token               | Value | Usage                |
| ------------------- | ----- | -------------------- |
| `duration.fast`     | 100ms | Micro-interactions   |
| `duration.normal`   | 150ms | Standard transitions |
| `duration.moderate` | 200ms | Panel animations     |
| `duration.slow`     | 300ms | Page transitions     |

---

## 6. Layout Constants

| Token                    | Value      | Usage                 |
| ------------------------ | ---------- | --------------------- |
| `sidebar.width`          | 240px      | Expanded sidebar      |
| `sidebar.collapsedWidth` | 64px       | Collapsed sidebar     |
| Control Heights          | 32/36/40px | SM/Default/LG buttons |

---

## 7. Breakpoints

| Name  | Value  | Target           |
| ----- | ------ | ---------------- |
| `xs`  | 480px  | Mobile portrait  |
| `sm`  | 640px  | Mobile landscape |
| `md`  | 768px  | Tablets          |
| `lg`  | 1024px | Small laptops    |
| `xl`  | 1280px | Desktops         |
| `2xl` | 1536px | Large screens    |

---

## Usage Examples

### TypeScript (Recommended)

```tsx
import { tokens } from '@lumina/design-system';

const style = {
  backgroundColor: tokens.colors.primary[50],
  padding: tokens.spacing[4],
  borderRadius: tokens.radius.md,
  boxShadow: tokens.shadow.xs,
  transition: `all ${tokens.duration.normal}ms ease`,
};
```

### Do ✅ / Don't ❌

```css
/* ✅ Do */
.card {
  color: var(--color-neutral-700);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
}

/* ❌ Don't */
.card {
  color: #374151;
  padding: 16px;
  border-radius: 8px;
}
```
