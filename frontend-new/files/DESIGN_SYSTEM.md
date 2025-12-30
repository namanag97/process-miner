# Design System: Process Mining Platform

> Version: 1.0.0 | Last Updated: 2024-12-30
> Status: Foundation — Phase 0-1 Components

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Design Tokens](#2-design-tokens)
3. [Core Components](#3-core-components)
4. [App Shell](#4-app-shell)

---

## 1. Design Principles

These principles guide every design decision. When facing ambiguity, refer back to these.

### P1: Compose from Common Parts

> "Same components, different arrangements"

Every UI is built from the same component library. A button is a button everywhere. A card is a card everywhere. Complexity comes from composition, not component proliferation.

**Applied:**
- Don't create "special" one-off components
- If a pattern appears twice, extract it
- New features should feel familiar because they use familiar parts

**Anti-pattern:** Creating a "ProcessUploadButton" when a standard Button + Icon works.

---

### P2: One Thing Per View

> "Each screen has one job"

Users should immediately understand what they can do on any screen. If a page tries to do two things, split it into two pages or use clear progressive disclosure.

**Applied:**
- Page titles describe the action/content clearly
- Primary CTA is obvious and singular
- Related actions are grouped, secondary actions are subdued
- Settings are separated from workflows

**Anti-pattern:** A page that lets you upload files AND configure settings AND view results.

---

### P3: Show the Process, Don't Describe It

> "Visualization over explanation"

Process mining is inherently visual. Prefer diagrams, charts, and flows over text descriptions. When text is necessary, keep it scannable.

**Applied:**
- Process maps are the hero, not supporting content
- Statistics appear as visual indicators (charts, badges) not paragraphs
- Empty states show what WILL appear, not just what's missing
- Progressive complexity: simple view first, details on demand

**Anti-pattern:** A paragraph explaining "Your process has 1,234 variants with an average cycle time of 5.2 days" instead of showing it.

---

### P4: Respect the User's Time

> "No unnecessary clicks, no unnecessary waits"

Every interaction should feel purposeful. Eliminate friction. Show progress. Never leave users wondering "did that work?"

**Applied:**
- Destructive actions need confirmation; routine actions don't
- Loading states are informative (skeleton > spinner > nothing)
- Batch operations where possible
- Smart defaults reduce configuration
- Recent/frequent items surface automatically

**Anti-pattern:** A 5-step wizard for something that could be 2 steps.

---

### P5: Context is King

> "Users should always know where they are and how they got here"

Navigation, breadcrumbs, and state indicators aren't decoration — they're essential wayfinding.

**Applied:**
- Breadcrumbs on all nested pages
- Active nav items clearly highlighted
- Page headers include parent context
- Filters and selections are always visible
- "Back" behavior is predictable

**Anti-pattern:** Opening a detail view in a modal with no indication of what list item it came from.

---

### P6: Progressive Disclosure

> "Simple by default, powerful when needed"

Start with the essential view. Reveal complexity through intentional user action. Advanced features exist but don't overwhelm beginners.

**Applied:**
- Default views show the "happy path"
- Advanced options behind expandable sections or secondary tabs
- Filters start collapsed
- Settings have sensible defaults
- Tooltips provide depth without cluttering the surface

**Anti-pattern:** A 30-field form when 5 fields would handle 90% of cases.

---

### P7: Data Density When Analyzing, Simplicity When Acting

> "Match information density to the task"

Analysis screens can be dense — users are exploring. Action screens should be focused — users are deciding.

**Applied:**
- Dashboards: Dense, multi-panel, many data points
- Upload flows: Sparse, step-by-step, clear CTAs
- Process explorer: Dense visualization + focused detail panel
- Settings: One section at a time, clear save/cancel

**Anti-pattern:** A cluttered upload page or an oversimplified dashboard.

---

## 2. Design Tokens

### 2.1 Color System

#### Brand Colors

```
primary-50:   #EBF5FF   /* Hover backgrounds, selected row */
primary-100:  #D6EBFF   /* Active nav background, light highlight */
primary-200:  #B3D7FF   /* Focus rings */
primary-500:  #2563EB   /* Primary buttons, links, active states */
primary-600:  #1D4ED8   /* Primary button hover */
primary-700:  #1E40AF   /* Primary button active/pressed */
```

#### Semantic Colors

```
/* Success - Confirmations, positive metrics, "data available" */
success-50:   #ECFDF5   /* Success background */
success-500:  #10B981   /* Success text, icons */
success-600:  #059669   /* Success dark */

/* Warning - Caution states, approaching thresholds */
warning-50:   #FFFBEB   /* Warning background */
warning-500:  #F59E0B   /* Warning text, icons */
warning-600:  #D97706   /* Warning dark */

/* Error - Failures, blocked states, below target */
error-50:     #FEF2F2   /* Error background */
error-500:    #EF4444   /* Error text, icons */
error-600:    #DC2626   /* Error dark */

/* Info - Neutral information callouts */
info-50:      #EFF6FF   /* Info background */
info-500:     #3B82F6   /* Info text, icons */
```

#### Neutral Scale

```
neutral-0:    #FFFFFF   /* Page background, cards */
neutral-50:   #F9FAFB   /* Subtle backgrounds, hover rows */
neutral-100:  #F3F4F6   /* Sidebar background, input backgrounds */
neutral-200:  #E5E7EB   /* Borders, dividers */
neutral-300:  #D1D5DB   /* Stronger borders, disabled state */
neutral-400:  #9CA3AF   /* Placeholder text, muted icons */
neutral-500:  #6B7280   /* Secondary text */
neutral-600:  #4B5563   /* Body text */
neutral-700:  #374151   /* Emphasized body text */
neutral-800:  #1F2937   /* Headings, primary text */
neutral-900:  #111827   /* High contrast text */
```

#### Semantic Aliases (Use These in Components)

```
/* Backgrounds */
bg-page:          neutral-0
bg-sidebar:       neutral-100
bg-card:          neutral-0
bg-card-hover:    neutral-50
bg-input:         neutral-0
bg-input-disabled: neutral-100
bg-overlay:       rgba(0,0,0,0.5)

/* Text */
text-primary:     neutral-800
text-secondary:   neutral-500
text-muted:       neutral-400
text-disabled:    neutral-300
text-inverse:     neutral-0
text-link:        primary-500
text-link-hover:  primary-600

/* Borders */
border-default:   neutral-200
border-strong:    neutral-300
border-focus:     primary-500
border-error:     error-500

/* Actions */
action-primary:       primary-500
action-primary-hover: primary-600
action-danger:        error-500
action-danger-hover:  error-600
```

---

### 2.2 Typography

#### Font Stack

```
font-sans:  "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
font-mono:  "JetBrains Mono", "Fira Code", Consolas, monospace
```

#### Type Scale

| Name | Size | Line Height | Weight | Usage |
|------|------|-------------|--------|-------|
| `text-xs` | 11px | 16px | 400 | Badges, micro labels, timestamps |
| `text-sm` | 12px | 16px | 400/500 | Table cells, metadata, captions |
| `text-base` | 14px | 20px | 400 | Body text, inputs, buttons |
| `text-lg` | 16px | 24px | 500 | Card titles, nav items |
| `text-xl` | 18px | 28px | 600 | Section headers |
| `text-2xl` | 20px | 28px | 600 | Page subtitles |
| `text-3xl` | 24px | 32px | 600 | Page titles |
| `text-4xl` | 32px | 40px | 700 | Large KPIs |
| `text-5xl` | 40px | 48px | 700 | Hero KPIs |

#### Font Weights

```
font-regular:   400   /* Body text, descriptions */
font-medium:    500   /* Labels, buttons, nav items */
font-semibold:  600   /* Headings, emphasis */
font-bold:      700   /* KPIs, strong emphasis */
```

---

### 2.3 Spacing

#### Base Unit: 4px

| Token | Value | Usage |
|-------|-------|-------|
| `space-0` | 0 | — |
| `space-1` | 4px | Icon-to-text gap, tight grouping |
| `space-2` | 8px | Button padding-y, compact gaps |
| `space-3` | 12px | Input padding, nav item padding |
| `space-4` | 16px | Card padding, standard gap |
| `space-5` | 20px | Section gaps (small) |
| `space-6` | 24px | Section gaps (medium) |
| `space-8` | 32px | Large section gaps |
| `space-10` | 40px | Page section separators |
| `space-12` | 48px | Major separators |
| `space-16` | 64px | Page margins |

#### Component-Specific Spacing

```
/* Buttons */
button-padding-x:     16px
button-padding-y:     8px
button-padding-x-sm:  12px
button-padding-y-sm:  6px

/* Inputs */
input-padding-x:      12px
input-padding-y:      8px

/* Cards */
card-padding:         16px
card-gap:             16px

/* Tables */
table-cell-padding-x: 16px
table-cell-padding-y: 12px

/* Navigation */
nav-item-padding-x:   12px
nav-item-padding-y:   8px
sidebar-width:        240px
sidebar-width-collapsed: 64px
```

---

### 2.4 Borders & Radius

#### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-sm` | 4px | Badges, tags, small elements |
| `radius-md` | 6px | Buttons, inputs, dropdowns |
| `radius-lg` | 8px | Cards, modals |
| `radius-xl` | 12px | Large cards, panels |
| `radius-full` | 9999px | Avatars, pills, toggles |

#### Border Widths

```
border-thin:    1px    /* Default borders */
border-medium:  2px    /* Focus rings, active states */
border-thick:   3px    /* Heavy emphasis (rare) */
```

---

### 2.5 Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-xs` | 0 1px 2px rgba(0,0,0,0.05) | Cards, subtle elevation |
| `shadow-sm` | 0 1px 3px rgba(0,0,0,0.08) | Buttons, raised elements |
| `shadow-md` | 0 4px 6px rgba(0,0,0,0.1) | Dropdowns, popovers |
| `shadow-lg` | 0 10px 15px rgba(0,0,0,0.1) | Modals, dialogs |
| `shadow-xl` | 0 20px 25px rgba(0,0,0,0.15) | Highest elevation |
| `shadow-focus` | 0 0 0 3px rgba(37,99,235,0.2) | Focus ring shadow |

---

### 2.6 Motion

#### Durations

```
duration-fast:     100ms   /* Hover states, micro-interactions */
duration-normal:   150ms   /* Standard transitions */
duration-moderate: 200ms   /* Panel slides, dropdowns */
duration-slow:     300ms   /* Page transitions, modals */
```

#### Easing

```
ease-default:  cubic-bezier(0.4, 0, 0.2, 1)   /* Standard */
ease-in:       cubic-bezier(0.4, 0, 1, 1)     /* Accelerate */
ease-out:      cubic-bezier(0, 0, 0.2, 1)     /* Decelerate */
```

---

### 2.7 Breakpoints

```
sm:   640px    /* Small tablets */
md:   768px    /* Tablets */
lg:   1024px   /* Small laptops */
xl:   1280px   /* Desktops */
2xl:  1536px   /* Large screens */
```

---

### 2.8 Z-Index Scale

```
z-base:       0      /* Default layer */
z-dropdown:   100    /* Dropdowns, select menus */
z-sticky:     200    /* Sticky headers */
z-overlay:    300    /* Backdrop overlays */
z-modal:      400    /* Modals, dialogs */
z-popover:    500    /* Popovers, tooltips */
z-toast:      600    /* Toast notifications */
```

---

## 3. Core Components

### 3.1 Button

#### Variants

| Variant | Background | Text | Border | Usage |
|---------|------------|------|--------|-------|
| **Primary** | primary-500 | white | none | Main CTA, one per section max |
| **Secondary** | white | neutral-800 | neutral-300 | Secondary actions |
| **Ghost** | transparent | primary-500 | none | Tertiary, inline actions |
| **Danger** | error-500 | white | none | Destructive actions |
| **Danger Ghost** | transparent | error-500 | none | Destructive inline |

#### Sizes

| Size | Height | Padding X | Font Size | Icon Size |
|------|--------|-----------|-----------|-----------|
| **sm** | 32px | 12px | 13px | 16px |
| **md** (default) | 36px | 16px | 14px | 18px |
| **lg** | 40px | 20px | 15px | 20px |

#### States

| State | Changes |
|-------|---------|
| **Default** | As specified per variant |
| **Hover** | Background darkens one step (500→600) |
| **Active** | Background darkens two steps (500→700) |
| **Focus** | Add focus ring: 2px primary-500 + shadow-focus |
| **Disabled** | opacity: 0.5, cursor: not-allowed |
| **Loading** | Show spinner, disable click, maintain width |

#### Anatomy

```
┌─────────────────────────────────┐
│  [Icon]  Label  [Icon]          │
│    ↑              ↑             │
│  Optional      Optional         │
│  (leading)     (trailing)       │
└─────────────────────────────────┘

Spacing: 8px gap between icon and label
Icons: 16-20px depending on button size
Min-width: None (hug content), but consider 80px+ for primary CTAs
```

#### Behavior

- **Ripple effect**: None (keep it clean)
- **Loading state**: Replace leading icon with spinner, keep label
- **Icon-only**: Square aspect ratio, tooltip required

---

### 3.2 Input

#### Variants

| Variant | Usage |
|---------|-------|
| **Text** | Single-line text entry |
| **Password** | With visibility toggle |
| **Search** | With search icon, optional clear button |
| **Textarea** | Multi-line, resizable |

#### Anatomy

```
┌─────────────────────────────────────────┐
│ Label (optional)                         │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ [Icon]  Placeholder/Value  [Action] │ │
│ └─────────────────────────────────────┘ │
│ Helper text or error message            │
└─────────────────────────────────────────┘

Spacing:
- Label to input: 6px
- Input to helper: 4px
```

#### States

| State | Border | Background | Label Color |
|-------|--------|------------|-------------|
| **Default** | neutral-300 | white | neutral-500 |
| **Hover** | neutral-400 | white | neutral-500 |
| **Focus** | primary-500 (2px) | white | primary-500 |
| **Error** | error-500 | error-50 | error-500 |
| **Disabled** | neutral-200 | neutral-100 | neutral-400 |

#### Specs

```
Height: 36px (single-line)
Padding: 12px horizontal, 8px vertical
Border-radius: radius-md (6px)
Font: text-base (14px)
Placeholder: neutral-400
```

#### Behavior

- **Focus**: Auto-select all text on focus (for inputs expecting replacement)
- **Error**: Show error icon (trailing), error message below
- **Clear button**: Appears when value exists (search variant)
- **Character count**: Optional, shown in helper text position

---

### 3.3 Card

#### Variants

| Variant | Usage |
|---------|-------|
| **Default** | Standard content container |
| **Interactive** | Clickable, hover state, cursor pointer |
| **Selected** | Active/selected state with primary border |

#### Anatomy

```
┌─────────────────────────────────────────┐
│ ┌─────────────────────────────────────┐ │
│ │ Header (optional)        [Actions]  │ │
│ ├─────────────────────────────────────┤ │
│ │                                     │ │
│ │ Body Content                        │ │
│ │                                     │ │
│ ├─────────────────────────────────────┤ │
│ │ Footer (optional)                   │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘

Padding: 16px all sides
Header-body gap: 12px
Body-footer gap: 12px
```

#### States

| State | Border | Shadow | Background |
|-------|--------|--------|------------|
| **Default** | neutral-200 | shadow-xs | white |
| **Hover** (interactive) | neutral-300 | shadow-sm | white |
| **Selected** | primary-500 | shadow-xs | primary-50 |

#### Specs

```
Border-radius: radius-lg (8px)
Border: 1px solid border-default
Min-width: 240px (recommended)
```

---

### 3.4 Sidebar Navigation

#### Anatomy

```
┌──────────────────────────────┐
│ ┌──────────────────────────┐ │
│ │ Logo / Brand             │ │ ← 48px height, 16px padding
│ └──────────────────────────┘ │
├──────────────────────────────┤
│ Section Label (optional)     │ ← 11px, uppercase, muted
│ ┌──────────────────────────┐ │
│ │ [Icon]  Nav Item Label   │ │ ← Nav Item
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ [Icon]  Nav Item Label   │ │
│ └──────────────────────────┘ │
│                              │
│ ... more items ...           │
│                              │
├──────────────────────────────┤ ← Spacer (flex-grow)
│ ┌──────────────────────────┐ │
│ │ [Icon]  Settings         │ │ ← Bottom-pinned items
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ [Avatar] User Name       │ │ ← User section
│ │          Role            │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘

Width: 240px (expanded), 64px (collapsed)
Background: neutral-100
```

#### Nav Item States

| State | Background | Text | Icon | Left Border |
|-------|------------|------|------|-------------|
| **Default** | transparent | neutral-600 | neutral-500 | none |
| **Hover** | neutral-200 | neutral-800 | neutral-600 | none |
| **Active** | primary-100 | primary-700 | primary-600 | 3px primary-500 |
| **Disabled** | transparent | neutral-400 | neutral-400 | none |

#### Nav Item Specs

```
Height: 40px
Padding: 8px 12px
Border-radius: radius-md (6px)
Icon size: 20px
Icon-to-text gap: 12px
Font: text-base (14px), font-medium (500)
```

#### Section Label Specs

```
Font: 11px, font-medium, uppercase
Color: neutral-400
Letter-spacing: 0.05em
Padding: 16px 12px 8px
```

#### Behavior

- **Collapse**: Icon-only mode, tooltips on hover
- **Expand on hover**: Optional — can expand collapsed sidebar on hover
- **Active indication**: Left border + background change
- **Nested items**: Indent 24px, no left border until active

---

### 3.5 Page Header

#### Anatomy

```
┌─────────────────────────────────────────────────────────────┐
│ Breadcrumb (optional)                                       │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────┐  ┌───────────────────┐ │
│ │ [Back] Page Title               │  │ [Secondary] [CTA] │ │
│ │        Description (optional)   │  │                   │ │
│ └─────────────────────────────────┘  └───────────────────┘ │
└─────────────────────────────────────────────────────────────┘

Layout: Flex, space-between
Left: Title group
Right: Actions group
```

#### Specs

```
Breadcrumb:
- Font: text-sm (12px)
- Color: text-link for links, text-secondary for separator
- Separator: "›" or "/"
- Margin-bottom: 8px

Page Title:
- Font: text-3xl (24px), font-semibold
- Color: text-primary

Description:
- Font: text-base (14px)
- Color: text-secondary
- Margin-top: 4px

Back Button:
- Icon-only or icon + "Back"
- Margin-right: 8px from title

Actions:
- Gap between buttons: 8px
- Primary CTA rightmost
```

#### Variations

| Variation | Elements |
|-----------|----------|
| **Minimal** | Title only |
| **Standard** | Title + Description + Primary CTA |
| **Full** | Breadcrumb + Back + Title + Description + Multiple Actions |

---

### 3.6 Empty State

#### Anatomy

```
┌─────────────────────────────────────────┐
│              ┌─────────┐                │
│              │  Icon   │                │ ← 48px, neutral-400
│              │  or     │                │
│              │ Illustr │                │
│              └─────────┘                │
│                                         │
│         Primary Message                 │ ← text-lg, semibold
│                                         │
│   Secondary message explaining          │ ← text-base, neutral-500
│   what to do or why it's empty          │
│                                         │
│          ┌─────────────┐                │
│          │  Action CTA │                │ ← Primary button
│          └─────────────┘                │
└─────────────────────────────────────────┘

Alignment: Center (both axes)
Max-width: 400px for text
```

#### Content Guidelines

| Element | Guidelines |
|---------|------------|
| **Icon** | Relevant to the content type (folder for files, chart for data, etc.) |
| **Primary message** | What's empty, stated positively ("No projects yet" not "Error: No projects") |
| **Secondary message** | How to fill it, or why it might be empty |
| **CTA** | Action to resolve the empty state |

#### Examples

```
Files empty state:
- Icon: Upload cloud icon
- Primary: "No files uploaded"
- Secondary: "Upload a CSV or XES file to start analyzing your process"
- CTA: "Upload File"

Search empty state:
- Icon: Search icon
- Primary: "No results found"
- Secondary: "Try adjusting your search or filter criteria"
- CTA: "Clear filters"
```

---

### 3.7 Badge / Status Indicator

#### Variants

| Variant | Background | Text | Usage |
|---------|------------|------|-------|
| **Default** | neutral-100 | neutral-700 | Neutral labels, counts |
| **Primary** | primary-100 | primary-700 | Selected, featured |
| **Success** | success-50 | success-700 | Positive status, completed |
| **Warning** | warning-50 | warning-700 | Attention needed |
| **Error** | error-50 | error-700 | Failed, critical |
| **Info** | info-50 | info-700 | Informational |

#### Sizes

| Size | Height | Padding X | Font Size |
|------|--------|-----------|-----------|
| **sm** | 20px | 6px | 11px |
| **md** | 24px | 8px | 12px |

#### Specs

```
Border-radius: radius-full (pill shape)
Font-weight: font-medium (500)
```

#### Status Dot Variant

```
For inline status indicators:
┌─────────────────────────┐
│ ● Status Label          │
└─────────────────────────┘

Dot: 8px circle, color matches variant
Gap: 6px between dot and label
```

---

### 3.8 Toast / Notification

#### Anatomy

```
┌─────────────────────────────────────────────────┐
│ [Icon]  Message text goes here        [Close ×] │
│         Optional secondary line                 │
└─────────────────────────────────────────────────┘
```

#### Variants

| Variant | Icon | Left Border | Background |
|---------|------|-------------|------------|
| **Info** | Info circle | info-500 | white |
| **Success** | Check circle | success-500 | white |
| **Warning** | Warning triangle | warning-500 | white |
| **Error** | X circle | error-500 | white |

#### Specs

```
Position: Fixed, top-right (16px from edges)
Width: 360px max
Padding: 12px 16px
Border-radius: radius-lg (8px)
Shadow: shadow-lg
Left border: 4px solid (variant color)
Z-index: z-toast (600)

Icon: 20px
Gap: 12px (icon to text)
Close button: 16px, neutral-400, hover neutral-600
```

#### Behavior

- **Duration**: 5s default, configurable
- **Dismiss**: Click close button or swipe (mobile)
- **Stack**: New toasts push older ones down
- **Max visible**: 3 toasts, older ones fade
- **Persistence**: Error toasts don't auto-dismiss

---

### 3.9 Modal / Dialog

#### Anatomy

```
┌───────────────────────────────────────────────────────┐
│ ┌───────────────────────────────────────────────────┐ │
│ │ Title                                     [Close] │ │ ← Header
│ ├───────────────────────────────────────────────────┤ │
│ │                                                   │ │
│ │ Body content goes here                            │ │ ← Body (scrollable)
│ │                                                   │ │
│ ├───────────────────────────────────────────────────┤ │
│ │                        [Secondary]  [Primary]     │ │ ← Footer (optional)
│ └───────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────┘

Overlay: bg-overlay (rgba(0,0,0,0.5))
```

#### Sizes

| Size | Width | Use Case |
|------|-------|----------|
| **sm** | 400px | Confirmations, simple forms |
| **md** | 560px | Standard forms, content |
| **lg** | 720px | Complex content, tables |
| **xl** | 900px | Rich content, side-by-side |
| **full** | 100% - 48px | Near full-screen |

#### Specs

```
Border-radius: radius-xl (12px)
Shadow: shadow-xl
Max-height: 90vh
Padding:
  - Header: 16px 24px
  - Body: 24px
  - Footer: 16px 24px
  
Header border-bottom: 1px solid neutral-200
Footer border-top: 1px solid neutral-200
Footer button gap: 8px
```

#### Behavior

- **Open animation**: Fade in + scale from 95% to 100% (duration-moderate)
- **Close triggers**: Close button, overlay click (optional), Escape key
- **Focus trap**: Tab cycles within modal
- **Scroll**: Body scrolls, header/footer fixed
- **Stacking**: Avoid; if necessary, dim previous modal

---

### 3.10 Dropdown / Select

#### Anatomy

```
Trigger (closed):
┌─────────────────────────────────┐
│ Selected value             [▼]  │
└─────────────────────────────────┘

Menu (open):
┌─────────────────────────────────┐
│ Search input (optional)         │
├─────────────────────────────────┤
│ Option 1                        │ ← hover: neutral-50
│ Option 2 (selected)         [✓] │ ← selected: primary bg
│ Option 3                        │
│ ...                             │
└─────────────────────────────────┘
```

#### Specs

```
Trigger:
- Same specs as Input component
- Chevron icon: 16px, right-aligned

Menu:
- Background: white
- Border: 1px solid neutral-200
- Border-radius: radius-md (6px)
- Shadow: shadow-md
- Max-height: 280px (scrollable)
- Z-index: z-dropdown (100)

Option:
- Padding: 8px 12px
- Font: text-base (14px)
- Hover: neutral-50 background
- Selected: primary-50 background, primary-600 text, checkmark icon
- Disabled: neutral-400 text, no hover
```

#### Behavior

- **Open**: Click trigger or focus + Enter/Space
- **Navigation**: Arrow keys move highlight
- **Select**: Enter/click selects and closes
- **Close**: Click outside, Escape, or select
- **Search**: Filters options as you type

---

### 3.11 Tabs

#### Anatomy

```
┌─────────────────────────────────────────────────────┐
│ Tab 1        Tab 2 (active)        Tab 3            │
│ ─────────────███████████████───────────────         │ ← bottom border on active
├─────────────────────────────────────────────────────┤
│                                                     │
│ Tab Panel Content                                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### Specs

```
Tab List:
- Border-bottom: 1px solid neutral-200
- Gap between tabs: 0 (tabs touch)

Tab Item:
- Padding: 12px 16px
- Font: text-base (14px), font-medium
- Default: neutral-500
- Hover: neutral-700
- Active: primary-600, border-bottom 2px primary-500

Tab Panel:
- Padding-top: 16px
```

#### Behavior

- **Activation**: Click or keyboard (arrow keys when focused)
- **Lazy loading**: Panels can render on first activation
- **Scrollable tabs**: For many tabs, add horizontal scroll with fade indicators

---

### 3.12 Table

#### Anatomy

```
┌─────────────────────────────────────────────────────────────┐
│ Column A ↕    Column B ↕    Column C         Actions        │ ← Header
├─────────────────────────────────────────────────────────────┤
│ Cell A1        Cell B1       Cell C1         [•••]          │ ← Row
├─────────────────────────────────────────────────────────────┤
│ Cell A2        Cell B2       Cell C2         [•••]          │
├─────────────────────────────────────────────────────────────┤
│ Cell A3        Cell B3       Cell C3         [•••]          │
└─────────────────────────────────────────────────────────────┘
```

#### Specs

```
Header:
- Background: neutral-50
- Font: text-sm (12px), font-medium, neutral-500
- Padding: 8px 16px
- Border-bottom: 1px solid neutral-200
- Sortable: cursor pointer, sort icon on hover

Row:
- Background: white (odd), white (even) — no zebra by default
- Hover: neutral-50
- Font: text-base (14px), neutral-800
- Padding: 12px 16px
- Border-bottom: 1px solid neutral-100

Selected Row:
- Background: primary-50
- Left border: 3px solid primary-500
```

#### Behavior

- **Sorting**: Click header to sort, show direction indicator (↑↓)
- **Selection**: Checkbox column (optional), row click (optional)
- **Actions**: Three-dot menu or inline icon buttons
- **Empty**: Show empty state component in table body

---

### 3.13 Avatar

#### Sizes

| Size | Dimensions | Font Size | Usage |
|------|------------|-----------|-------|
| **xs** | 24px | 10px | Inline mentions, tight spaces |
| **sm** | 32px | 12px | Comments, lists |
| **md** | 40px | 14px | Default, nav user |
| **lg** | 48px | 16px | Profile headers |
| **xl** | 64px | 20px | Account pages |

#### Variants

| Variant | Display |
|---------|---------|
| **Image** | User photo, object-fit: cover |
| **Initials** | First letter(s), background color derived from name |
| **Icon** | Placeholder user icon |

#### Specs

```
Border-radius: radius-full (circle)
Fallback order: Image → Initials → Icon
Initial colors: Deterministic from name string (pick from a palette)
Initial font-weight: font-medium
```

---

### 3.14 Tooltip

#### Specs

```
Background: neutral-800
Text: white
Font: text-sm (12px)
Padding: 6px 10px
Border-radius: radius-sm (4px)
Max-width: 200px
Z-index: z-popover (500)
```

#### Behavior

- **Trigger**: Hover (desktop), long-press (mobile)
- **Delay**: 300ms before showing
- **Position**: Auto-positioned, prefer top, flip if needed
- **Arrow**: 6px triangle pointing to trigger

---

## 4. App Shell

### Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌────────┐┌───────────────────────────────────────────────────┐  │
│ │        ││ ┌───────────────────────────────────────────────┐ │  │
│ │        ││ │ Page Header                                   │ │  │
│ │        ││ └───────────────────────────────────────────────┘ │  │
│ │        ││ ┌───────────────────────────────────────────────┐ │  │
│ │Sidebar ││ │                                               │ │  │
│ │        ││ │                                               │ │  │
│ │        ││ │           Main Content Area                   │ │  │
│ │        ││ │              (scrollable)                     │ │  │
│ │        ││ │                                               │ │  │
│ │        ││ │                                               │ │  │
│ │        ││ └───────────────────────────────────────────────┘ │  │
│ └────────┘└───────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Specifications

```
Sidebar:
- Width: 240px (expanded), 64px (collapsed)
- Background: neutral-100
- Position: Fixed left
- Height: 100vh
- Border-right: 1px solid neutral-200
- Z-index: z-sticky (200)

Main Area:
- Margin-left: 240px (or 64px when collapsed)
- Min-height: 100vh
- Background: white

Page Header:
- Padding: 24px 24px 0
- Sticky: Optional (top: 0)

Content Area:
- Padding: 24px
- Max-width: 1440px (optional, centered)
- Overflow-y: auto
```

### Responsive Behavior

| Breakpoint | Sidebar | Main Content |
|------------|---------|--------------|
| **≥ 1024px** | Full width (240px) | Beside sidebar |
| **768–1023px** | Collapsed (64px) | Beside sidebar |
| **< 768px** | Hidden (overlay on trigger) | Full width |

---

## Appendix A: Component Checklist for Phase 0-1

| Component | Phase 0 | Phase 1 | Notes |
|-----------|---------|---------|-------|
| Button | ✅ | — | All variants needed |
| Input | ✅ | — | Text, password, search |
| Card | ✅ | — | Default, interactive |
| Sidebar Nav | ✅ | — | Core shell |
| Page Header | ✅ | — | Core shell |
| Empty State | ✅ | — | Needed for all features |
| Badge | ✅ | — | Status indicators |
| Toast | — | ✅ | Notifications feature |
| Modal | — | ✅ | Settings, confirmations |
| Dropdown | ✅ | — | Forms, filters |
| Tabs | — | ✅ | Settings sections |
| Table | — | ✅ | Activity log |
| Avatar | ✅ | — | User nav, settings |
| Tooltip | ✅ | — | Collapsed nav, icons |

---

## Appendix B: Color Usage Quick Reference

| Use Case | Token |
|----------|-------|
| Primary CTA background | primary-500 |
| Primary CTA hover | primary-600 |
| Link text | primary-500 |
| Active nav item | primary-100 bg, primary-700 text |
| Success status | success-500 |
| Error status | error-500 |
| Default border | neutral-200 |
| Input border | neutral-300 |
| Focus border | primary-500 |
| Body text | neutral-800 |
| Secondary text | neutral-500 |
| Muted text | neutral-400 |
| Page background | white |
| Sidebar background | neutral-100 |
| Card background | white |
| Hover background | neutral-50 |

---

## Appendix C: Spacing Quick Reference

| Use Case | Value |
|----------|-------|
| Icon to label | 8px |
| Button padding | 8px 16px |
| Input padding | 8px 12px |
| Card padding | 16px |
| Card grid gap | 16px |
| Section gap | 24px |
| Page padding | 24px |
| Nav item padding | 8px 12px |
| Table cell padding | 12px 16px |
| Modal body padding | 24px |

---

*End of Design System Foundation Document*
