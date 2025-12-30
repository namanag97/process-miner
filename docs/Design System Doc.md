# Design System Documentation

> Last Updated: 2025-12-30
> Screenshots Analyzed: Celonis Studio/Automations, Business Miner Workspace, Quickstarts Grid, Analytics Dashboard (KPIs), Throughput Time Report

---

## 1. Design Tokens

### Colors

#### Primary Palette

```css
--color-primary-50: #ebf5ff; /* Lightest blue - hover backgrounds */
--color-primary-100: #d6ebff; /* Light blue - selected states backgrounds */
--color-primary-200: #b3d7ff; /* Soft blue - focus rings, subtle highlights */
--color-primary-400: #4d9fff; /* Medium blue - secondary actions */
--color-primary-500: #2563eb; /* Primary brand blue - main CTAs, active nav items */
--color-primary-600: #1d4ed8; /* Darker blue - hover states on primary buttons */
--color-primary-700: #1e40af; /* Deep blue - active/pressed states */
```

#### Semantic Colors

```css
/* Success */
--color-success-50: #ecfdf5; /* Success background */
--color-success-100: #d1fae5; /* Success light */
--color-success-500: #10b981; /* Success primary - "Data available" indicators */
--color-success-600: #059669; /* Success dark */

/* Warning */
--color-warning-50: #fffbeb; /* Warning background */
--color-warning-100: #fef3c7; /* Warning light */
--color-warning-500: #f59e0b; /* Warning primary - percentages below target */
--color-warning-600: #d97706; /* Warning dark */

/* Error */
--color-error-50: #fef2f2; /* Error background */
--color-error-100: #fee2e2; /* Error light */
--color-error-500: #ef4444; /* Error primary - below target rates (e.g., 50%, 51%) */
--color-error-600: #dc2626; /* Error dark */

/* Info */
--color-info-50: #eff6ff; /* Info background */
--color-info-500: #3b82f6; /* Info primary */
```

#### Neutral Scale

```css
--color-neutral-0: #ffffff; /* Pure white - page backgrounds, cards */
--color-neutral-50: #f9fafb; /* Near white - alternate row backgrounds */
--color-neutral-100: #f3f4f6; /* Light gray - sidebar background, input backgrounds */
--color-neutral-200: #e5e7eb; /* Border gray - dividers, inactive borders */
--color-neutral-300: #d1d5db; /* Medium gray - placeholder text, disabled borders */
--color-neutral-400: #9ca3af; /* Gray - secondary text, muted icons */
--color-neutral-500: #6b7280; /* Dark gray - secondary labels */
--color-neutral-600: #4b5563; /* Darker gray - body text */
--color-neutral-700: #374151; /* Deep gray - emphasized body text */
--color-neutral-800: #1f2937; /* Near black - primary text, headings */
--color-neutral-900: #111827; /* Darkest gray - darkest text */
--color-neutral-950: #030712; /* Black - high contrast elements */
```

#### Surface Colors

```css
--color-surface-page: #ffffff; /* Main page background */
--color-surface-sidebar: #f3f4f6; /* Sidebar/navigation background */
--color-surface-card: #ffffff; /* Card backgrounds */
--color-surface-card-hover: #f9fafb; /* Card hover state */
--color-surface-modal: #ffffff; /* Modal backgrounds */
--color-surface-overlay: rgba(0, 0, 0, 0.5); /* Modal overlays */
--color-surface-elevated: #ffffff; /* Elevated surfaces (dropdowns) */
--color-surface-dark: #1a1a2e; /* Dark cards (e.g., Quickstart tiles) */
```

#### Border Colors

```css
--color-border-default: #e5e7eb; /* Default borders */
--color-border-subtle: #f3f4f6; /* Subtle dividers */
--color-border-strong: #d1d5db; /* Strong borders, input borders */
--color-border-focus: #2563eb; /* Focus ring color */
--color-border-active: #2563eb; /* Active/selected borders */
```

#### Text Colors

```css
--color-text-primary: #1f2937; /* Primary text - headings, important content */
--color-text-secondary: #6b7280; /* Secondary text - labels, descriptions */
--color-text-muted: #9ca3af; /* Muted text - placeholders, timestamps */
--color-text-disabled: #d1d5db; /* Disabled text */
--color-text-inverse: #ffffff; /* Inverse text - on dark backgrounds */
--color-text-link: #2563eb; /* Link text - clickable elements */
--color-text-link-hover: #1d4ed8; /* Link hover state */
```

#### Chart Colors

```css
--color-chart-blue-500: #3b82f6; /* Primary chart bars */
--color-chart-blue-600: #2563eb; /* Darker chart elements */
--color-chart-blue-700: #1d4ed8; /* Darkest chart fills */
--color-chart-blue-200: #bfdbfe; /* Light chart fills - area charts */
--color-chart-target: #10b981; /* Target line indicators */
--color-chart-axis: #9ca3af; /* Axis lines and labels */
--color-chart-grid: #e5e7eb; /* Grid lines */
```

---

### Typography

#### Font Families

```css
--font-family-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
  sans-serif;
--font-family-mono: "JetBrains Mono", "Fira Code", "SF Mono", Consolas,
  monospace;
```

#### Font Weights

```css
--font-weight-regular: 400; /* Body text, labels */
--font-weight-medium: 500; /* Emphasized body, buttons, nav items */
--font-weight-semibold: 600; /* Subheadings, card titles */
--font-weight-bold: 700; /* Headings, KPI values */
```

#### Font Size Scale

```css
--font-size-xs: 11px; /* 0.6875rem - Badges, micro labels */
--font-size-sm: 12px; /* 0.75rem - Table cells, metadata, timestamps */
--font-size-base: 14px; /* 0.875rem - Body text, form labels */
--font-size-md: 15px; /* ~0.9375rem - Slightly emphasized body */
--font-size-lg: 16px; /* 1rem - Section headers, large body */
--font-size-xl: 18px; /* 1.125rem - Card titles */
--font-size-2xl: 20px; /* 1.25rem - Page subtitles */
--font-size-3xl: 24px; /* 1.5rem - Page titles */
--font-size-4xl: 32px; /* 2rem - Large KPI values */
--font-size-5xl: 40px; /* 2.5rem - Hero KPIs (e.g., "4.3%", "37 days") */
```

#### Line Heights

```css
--line-height-tight: 1.2; /* Headings, KPIs */
--line-height-snug: 1.35; /* Subheadings */
--line-height-normal: 1.5; /* Body text */
--line-height-relaxed: 1.625; /* Long-form content */
```

#### Letter Spacing

```css
--letter-spacing-tight: -0.02em; /* Large headings, KPIs */
--letter-spacing-normal: 0; /* Body text */
--letter-spacing-wide: 0.02em; /* Labels, section headers */
--letter-spacing-wider: 0.05em; /* Uppercase labels, badges */
```

#### Typography Styles

| Style         | Weight | Size | Line Height | Usage                            |
| ------------- | ------ | ---- | ----------- | -------------------------------- |
| Hero KPI      | 700    | 40px | 1.2         | Large statistics (4.3%, 37 days) |
| Page Title    | 600    | 24px | 1.35        | Main page headings (Connections) |
| Section Title | 600    | 18px | 1.35        | Card headers, section heads      |
| Card Title    | 500    | 16px | 1.5         | Card titles, list items          |
| Body          | 400    | 14px | 1.5         | Default body text                |
| Body Small    | 400    | 12px | 1.5         | Secondary text, metadata         |
| Label         | 500    | 12px | 1.5         | Form labels, table headers       |
| Caption       | 400    | 11px | 1.4         | Timestamps, helper text          |

---

### Spacing

#### Base Unit

```css
--spacing-unit: 4px;
```

#### Spacing Scale

```css
--spacing-0: 0;
--spacing-0.5: 2px; /* Micro spacing - between inline elements */
--spacing-1: 4px; /* Tight spacing - icon-to-text */
--spacing-1.5: 6px; /* Small spacing */
--spacing-2: 8px; /* Default compact spacing - button padding-y */
--spacing-2.5: 10px; /* Between related items */
--spacing-3: 12px; /* Common padding - input padding */
--spacing-4: 16px; /* Default section padding - card padding */
--spacing-5: 20px; /* Medium spacing */
--spacing-6: 24px; /* Large spacing - between sections */
--spacing-8: 32px; /* Extra large spacing */
--spacing-10: 40px; /* Section gaps */
--spacing-12: 48px; /* Large section gaps */
--spacing-16: 64px; /* Page margins */
--spacing-20: 80px; /* Major section separators */
--spacing-24: 96px; /* Page-level spacing */
```

#### Component Spacing Patterns

```css
/* Cards */
--card-padding: 16px; /* Internal card padding */
--card-padding-compact: 12px; /* Compact card variant */
--card-gap: 16px; /* Gap between cards in grid */

/* Buttons */
--button-padding-x: 16px; /* Horizontal padding */
--button-padding-y: 8px; /* Vertical padding */
--button-padding-x-sm: 12px; /* Small button horizontal */
--button-padding-y-sm: 6px; /* Small button vertical */

/* Inputs */
--input-padding-x: 12px; /* Input horizontal padding */
--input-padding-y: 8px; /* Input vertical padding */

/* Navigation */
--nav-item-padding-x: 12px; /* Nav item horizontal padding */
--nav-item-padding-y: 8px; /* Nav item vertical padding */
--sidebar-padding: 8px; /* Sidebar internal padding */

/* Tables */
--table-cell-padding-x: 16px; /* Table cell horizontal */
--table-cell-padding-y: 12px; /* Table cell vertical */
--table-header-padding-y: 8px; /* Table header vertical */
```

---

### Shadows (Elevation)

```css
--shadow-none: none;
--shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04); /* Subtle depth - cards */
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08); /* Light elevation - buttons */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1); /* Medium elevation - dropdowns */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1); /* High elevation - modals */
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.15); /* Highest elevation - dialogs */

/* Focus shadow */
--shadow-focus: 0 0 0 3px rgba(37, 99, 235, 0.2); /* Focus ring shadow */
```

---

### Borders & Radius

#### Border Widths

```css
--border-width-none: 0;
--border-width-hairline: 0.5px; /* Subtle dividers */
--border-width-thin: 1px; /* Default borders */
--border-width-medium: 2px; /* Emphasized borders, active states */
--border-width-thick: 3px; /* Strong emphasis */
```

#### Border Radius Scale

```css
--radius-none: 0;
--radius-sm: 4px; /* Subtle rounding - badges, tags */
--radius-md: 6px; /* Default rounding - inputs, buttons */
--radius-lg: 8px; /* Medium rounding - cards, modals */
--radius-xl: 12px; /* Large rounding - large cards */
--radius-2xl: 16px; /* Extra large rounding */
--radius-full: 9999px; /* Pill shape - avatars, badges, toggles */
```

---

### Animation & Motion

#### Transition Durations

```css
--duration-instant: 50ms; /* Instant feedback */
--duration-fast: 100ms; /* Quick transitions - hover states */
--duration-normal: 150ms; /* Default transitions */
--duration-moderate: 200ms; /* Noticeable transitions */
--duration-slow: 300ms; /* Deliberate animations */
--duration-slower: 500ms; /* Page transitions */
```

#### Easing Curves

```css
--easing-default: cubic-bezier(0.4, 0, 0.2, 1); /* Standard ease */
--easing-in: cubic-bezier(0.4, 0, 1, 1); /* Accelerate */
--easing-out: cubic-bezier(0, 0, 0.2, 1); /* Decelerate */
--easing-in-out: cubic-bezier(0.4, 0, 0.2, 1); /* Smooth */
--easing-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55); /* Playful */
```

---

### Iconography

#### Icon Sizes

```css
--icon-size-xs: 12px; /* Inline indicators */
--icon-size-sm: 16px; /* Small icons - nav items, buttons */
--icon-size-md: 20px; /* Default icon size */
--icon-size-lg: 24px; /* Larger icons - section headers */
--icon-size-xl: 32px; /* Feature icons */
--icon-size-2xl: 48px; /* Empty state icons */
```

#### Icon Style

- **Style**: Outlined with 1.5px stroke weight
- **Corners**: Rounded (matching border-radius system)
- **Fill**: None by default, solid for selected/active states

---

## 2. Components

### Sidebar Navigation

#### Anatomy

- **Width**: 220px (expanded), 56px (collapsed)
- **Background**: `--color-surface-sidebar` (#F3F4F6)
- **Border-right**: 1px solid `--color-border-subtle`

#### Navigation Items

**Default State:**

- Background: Transparent
- Text: `--color-text-secondary` (#6B7280)
- Icon: `--color-neutral-500`
- Padding: 8px 12px
- Border-radius: 6px
- Font: 500 14px/20px Inter

**Hover State:**

- Background: `--color-neutral-200` (#E5E7EB)
- Text: `--color-text-primary`

**Active/Selected State:**

- Background: `--color-primary-100` (#D6EBFF)
- Text: `--color-primary-600` (#1D4ED8)
- Icon: `--color-primary-600`
- Left border: 3px solid `--color-primary-500`

#### Section Headers

- Text: `--color-text-muted` (#9CA3AF)
- Font: 500 11px/16px Inter
- Letter-spacing: 0.05em
- Text-transform: uppercase
- Padding: 16px 12px 4px

_Source: uploaded_image_0, uploaded_image_2_

---

### Button

#### Primary Button

- **Background**: `--color-primary-500` (#2563EB)
- **Text**: `--color-text-inverse` (#FFFFFF)
- **Font**: 500 14px/20px Inter
- **Padding**: 8px 16px
- **Border-radius**: 6px
- **Height**: 36px
- **Shadow**: `--shadow-xs`

**Hover State:**

- Background: `--color-primary-600` (#1D4ED8)
- Transition: 150ms ease-out

**Active State:**

- Background: `--color-primary-700` (#1E40AF)

_Source: uploaded_image_1 (Create Process Workspace), uploaded_image_3 (Create new Exploration)_

#### Secondary Button

- **Background**: `--color-neutral-0` (#FFFFFF)
- **Text**: `--color-text-primary` (#1F2937)
- **Border**: 1px solid `--color-border-strong` (#D1D5DB)
- **Font**: 500 14px/20px Inter
- **Padding**: 8px 16px
- **Border-radius**: 6px
- **Height**: 36px

**Hover State:**

- Background: `--color-neutral-50` (#F9FAFB)
- Border-color: `--color-neutral-400`

_Source: uploaded_image_1 (Share button)_

#### Ghost/Text Button

- **Background**: Transparent
- **Text**: `--color-text-link` (#2563EB)
- **Font**: 500 14px/20px Inter
- **Padding**: 4px 8px
- **Border-radius**: 4px

**Hover State:**

- Background: `--color-primary-50` (#EBF5FF)

_Source: uploaded_image_3 (Add filter), uploaded_image_4 (Add Question)_

---

### Input Field

#### Default State

- **Background**: `--color-neutral-0` (#FFFFFF)
- **Border**: 1px solid `--color-border-strong` (#D1D5DB)
- **Border-radius**: 6px
- **Padding**: 8px 12px
- **Height**: 36px
- **Font**: 400 14px/20px Inter
- **Placeholder color**: `--color-text-muted` (#9CA3AF)

#### Focus State

- **Border**: 2px solid `--color-border-focus` (#2563EB)
- **Shadow**: `--shadow-focus`
- **Outline**: none

_Source: uploaded_image_0 (Search input)_

---

### Dropdown/Select

#### Default State

- **Background**: `--color-neutral-0` (#FFFFFF)
- **Border**: 1px solid `--color-border-strong` (#D1D5DB)
- **Border-radius**: 6px
- **Padding**: 8px 12px
- **Height**: 36px
- **Font**: 400 14px/20px Inter
- **Chevron icon**: Right-aligned, 16px

_Source: uploaded_image_0 (Select Package dropdown)_

---

### Card

#### Standard Card

- **Background**: `--color-surface-card` (#FFFFFF)
- **Border**: 1px solid `--color-border-default` (#E5E7EB)
- **Border-radius**: 8px
- **Padding**: 16px
- **Shadow**: `--shadow-xs`

**Hover State:**

- Shadow: `--shadow-sm`
- Border-color: `--color-neutral-300`

_Source: uploaded_image_1 (Process Exploration cards)_

#### Dark Card (Quickstart Tiles)

- **Background**: `--color-surface-dark` (#1A1A2E)
- **Text**: `--color-text-inverse` (#FFFFFF)
- **Border-radius**: 8px
- **Padding**: 20px
- **Aspect ratio**: ~16:9

**Content:**

- Logo: Bottom-right, grayscale or white
- Title: 500 16px/24px Inter
- Subtitle: 400 14px/20px Inter (muted)

_Source: uploaded_image_2 (Oracle, SAP tiles)_

---

### KPI Card

#### Large KPI Display

- **Value**: 700 40px/48px Inter, `--color-text-primary`
- **Label**: 400 14px/20px Inter, `--color-text-secondary`
- **Trend indicator**: Inline, small badge
  - Positive: Green with up arrow
  - Negative: Red with down arrow
  - Format: "↓ -0.11 pp"

_Source: uploaded_image_3 (4.3% Unwanted activity rate), uploaded_image_4 (37 days Throughput Time)_

---

### Data Table

#### Table Structure

- **Header row**:

  - Background: `--color-neutral-50` (#F9FAFB)
  - Text: 500 12px/16px Inter, `--color-text-secondary`
  - Padding: 8px 16px
  - Border-bottom: 1px solid `--color-border-default`

- **Body rows**:

  - Background: `--color-neutral-0`
  - Text: 400 14px/20px Inter, `--color-text-primary`
  - Padding: 12px 16px
  - Border-bottom: 1px solid `--color-border-subtle`

- **Hover state**:

  - Background: `--color-neutral-50`

- **Sortable columns**:
  - Cursor: pointer
  - Sort icon: 12px, appears on hover

_Source: uploaded_image_4 (Throughput Time breakdown table)_

---

### Chart Components

#### Bar Chart

- **Bar fill**: `--color-chart-blue-600` (#2563EB)
- **Bar radius**: 2px (top corners only)
- **Hover fill**: `--color-chart-blue-700`
- **Tooltip**:
  - Background: `--color-neutral-800`
  - Text: `--color-text-inverse`
  - Border-radius: 4px
  - Padding: 8px 12px
  - Shadow: `--shadow-md`

_Source: uploaded_image_3 (Activity frequency chart, # of cases chart)_

#### Area Chart

- **Fill**: `--color-chart-blue-200` with 0.3 opacity
- **Stroke**: `--color-chart-blue-500`, 2px
- **Axis**: `--color-chart-axis` (#9CA3AF)
- **Grid lines**: `--color-chart-grid` (#E5E7EB), dashed

_Source: uploaded_image_3 (Unwanted activities over time)_

#### Histogram/Distribution Chart

- **Fill**: `--color-chart-blue-500`
- **Target line**: `--color-success-500`, 2px dashed
- **Label**: "Target Throughput Time"

_Source: uploaded_image_4 (Throughput Time distribution)_

---

### Status Indicators

#### Data Status Badge

- **Available (Green):**
  - Background: `--color-success-50`
  - Text: `--color-success-600`
  - Dot indicator: `--color-success-500`
  - Format: "● Data available"

_Source: uploaded_image_1 (Data Model status)_

#### Target Rate Indicator

- **Above Target (Green):**

  - Text: `--color-success-500`
  - Example: "59%", "67%"

- **Below Target (Red/Orange):**
  - Text: `--color-error-500`
  - Example: "50%", "51%", "40%"

_Source: uploaded_image_4 (Target Hit rate column)_

---

### Tabs

#### Tab Group

- **Container**: No background, border-bottom 1px `--color-border-default`
- **Tab item**:
  - Padding: 12px 16px
  - Font: 500 14px/20px Inter
  - Default: `--color-text-secondary`
  - Active: `--color-text-primary`, border-bottom 2px `--color-primary-500`

_Source: uploaded_image_1 (Process Explorations tabs), uploaded_image_3 (Related KPIs / Trends tabs)_

---

### Filter Panel

#### Right Sidebar Filter

- **Width**: ~280px
- **Background**: `--color-surface-card`
- **Border-left**: 1px solid `--color-border-default`
- **Padding**: 16px

#### Filter Elements

- **Section header**: 500 14px Inter, `--color-text-primary`
- **Add filter link**: 500 14px Inter, `--color-text-link`, with + icon
- **Filter chips**:
  - Background: `--color-neutral-100`
  - Border-radius: 16px (pill)
  - Padding: 4px 12px
  - Remove icon: 12px, right side

_Source: uploaded_image_3, uploaded_image_4 (Filter panel)_

---

### Progress/Percentage Indicator

#### Circular Progress Ring

- **Size**: 40px diameter
- **Stroke width**: 4px
- **Track**: `--color-neutral-200`
- **Fill**: `--color-primary-500`
- **Text inside**: 600 12px Inter

_Source: uploaded_image_3 (100% of cases indicator)_

---

### Breadcrumb

#### Standard Breadcrumb

- **Separator**: ">" or "›"
- **Text**: 400 14px Inter
- **Non-active items**: `--color-text-link`
- **Active item**: `--color-text-primary`, font-weight 500
- **Separator color**: `--color-text-muted`

_Source: uploaded_image_3 (Business Miner > [Quickstarts] Oracle AP...)_

---

## 3. Patterns

### Layout Patterns

#### App Shell

- **Sidebar**: Left-aligned, fixed, 220px width
- **Main content**: Fluid, margin-left: 220px
- **Top header**: Fixed, 56px height (within main content area)
- **Content area**: Scrollable, padding: 24px

#### Dashboard Grid

- **KPI row**: Multi-column flex (2-3 cards), gap: 16px
- **Chart row**: Full-width or 2-column, gap: 16px
- **Table section**: Full-width below charts

#### Card Grid

- **Columns**: 3-column responsive grid
- **Gap**: 16px
- **Card min-width**: ~280px

_Source: uploaded_image_1 (Process Exploration cards), uploaded_image_2 (Quickstart tiles)_

---

### Interaction Patterns

#### Empty States

- **Centered layout**: Vertically and horizontally centered
- **Icon**: 48px, `--color-neutral-400`
- **Message**: 400 14px Inter, `--color-text-secondary`
- **CTA**: Optional primary or text button below

_Source: uploaded_image_0 ("You haven't created any connections yet.")_

#### Hover Cards

- **Trigger**: Mouse hover on card
- **Effect**: Elevated shadow, subtle border color change
- **Timing**: 150ms ease-out

#### Action Menus

- **Trigger**: Three-dot menu icon (⋮)
- **Position**: Top-right of cards
- **Dropdown**: Shadow-md, 8px radius

_Source: uploaded_image_1 (Card action menus)_

---

## 4. Usage Guidelines

### Do's and Don'ts

#### ✅ Do's

1. Use the primary blue (#2563EB) sparingly for main CTAs and active states
2. Maintain consistent 16px padding within cards
3. Use the shadow scale progressively (xs for cards, md for dropdowns, lg for modals)
4. Apply the 8-point grid system for all spacing decisions
5. Use semantic colors for status indicators (green=success, red=error)
6. Keep typography hierarchy clear: max 3-4 levels per view

#### ❌ Don'ts

1. Don't use multiple primary buttons in the same view section
2. Don't mix border-radius values within the same component
3. Don't use shadows heavier than necessary for the elevation context
4. Don't override the neutral scale with arbitrary gray values
5. Don't use color alone to convey meaning (add icons/text for accessibility)

---

### Accessibility Notes

- Text color on `--color-primary-500` background must be white for 4.5:1 contrast
- Minimum touch target: 44x44px for mobile, 36x36px for desktop
- Focus states must be visible with 3px outline ring
- Charts should include text labels, not color alone

---

## Appendix: Screenshot Analysis Log

| Screenshot       | Elements Extracted                                                                                                            | Date       |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------- | ---------- |
| uploaded_image_0 | Sidebar navigation, Search input, Select dropdown, Empty state pattern, Section headers                                       | 2025-12-30 |
| uploaded_image_1 | Workspace cards, Tab component, Share button, Status badges, Action menus, Card grid layout, Breadcrumb                       | 2025-12-30 |
| uploaded_image_2 | Dark content tiles, Logo placement patterns, Quickstart grid, Expanded sidebar with icons                                     | 2025-12-30 |
| uploaded_image_3 | Large KPI display, Bar charts, Area charts, Tooltip, Filter panel, Progress ring, Trend indicators, Related KPIs tabs         | 2025-12-30 |
| uploaded_image_4 | Data table with sorting, Target rate indicators (color coded), Histogram chart, Question suggestion cards, Throughput metrics | 2025-12-30 |

---

## Version History

| Version | Date       | Changes                                                                                            |
| ------- | ---------- | -------------------------------------------------------------------------------------------------- |
| 1.0     | 2025-12-30 | Initial extraction from 5 Celonis screenshots covering Studio, Business Miner, Analytics Dashboard |
