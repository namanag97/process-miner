# Patterns & Recipes: Process Mining Platform

> Version: 1.0.0 | Last Updated: 2024-12-30
> Status: Living Document — Updated with Each Feature

---

## Table of Contents

1. [Page Layout Patterns](#1-page-layout-patterns)
2. [Composition Patterns](#2-composition-patterns)
3. [Interaction Patterns](#3-interaction-patterns)
4. [State Patterns](#4-state-patterns)
5. [Recipes](#5-recipes)
6. [Decision Log](#6-decision-log)

---

## 1. Page Layout Patterns

### 1.1 Standard Page

The default layout for most pages. Simple, focused content area.

```
┌─────────────────────────────────────────────────────────────┐
│ [Sidebar]│ Page Header                                      │
│          │ ─────────────────────────────────────────────── │
│          │                                                  │
│          │ Content Area                                     │
│          │                                                  │
│          │                                                  │
└─────────────────────────────────────────────────────────────┘
```

**When to use:**
- Settings pages
- List pages
- Form pages
- Any single-purpose page

**Specs:**
- Content max-width: 960px (optional, for readability)
- Content padding: 24px
- No secondary panels

---

### 1.2 Dashboard Page

Multi-panel layout for data-rich overview pages.

```
┌─────────────────────────────────────────────────────────────┐
│ [Sidebar]│ Page Header                                      │
│          │ ─────────────────────────────────────────────── │
│          │ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│          │ │ KPI Card│ │ KPI Card│ │ KPI Card│            │ ← KPI Row
│          │ └─────────┘ └─────────┘ └─────────┘            │
│          │ ┌────────────────────────────────────┐          │
│          │ │                                    │          │ ← Main Chart
│          │ │         Chart / Visualization      │          │
│          │ │                                    │          │
│          │ └────────────────────────────────────┘          │
│          │ ┌────────────────────────────────────┐          │
│          │ │ Data Table / Secondary Content     │          │ ← Breakdown
│          │ └────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

**When to use:**
- Home/overview pages
- Analytics dashboards
- Summary views

**Specs:**
- KPI cards: 3-4 columns, equal width
- Charts: Full width or 2-column
- Vertical gap between sections: 24px
- No max-width (uses full content area)

---

### 1.3 Explorer Page (Master-Detail)

Two-panel layout with visualization/list and detail panel.

```
┌─────────────────────────────────────────────────────────────┐
│ [Sidebar]│ Page Header                                      │
│          │ ─────────────────────────────────────────────── │
│          │ ┌──────────────────────┐ ┌─────────────────────┐│
│          │ │                      │ │                     ││
│          │ │                      │ │   Detail Panel      ││
│          │ │   Main Content       │ │   (filters, info,   ││
│          │ │   (process map,      │ │    or details)      ││
│          │ │    visualization,    │ │                     ││
│          │ │    or list)          │ │                     ││
│          │ │                      │ │                     ││
│          │ └──────────────────────┘ └─────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

**When to use:**
- Process explorer
- Data browser with detail view
- Any master-detail pattern

**Specs:**
- Main content: Flexible width (flex-grow)
- Detail panel: 320-400px fixed width
- Detail panel position: Right side
- Gap between panels: 16px
- Panel can be collapsible

---

### 1.4 Full-Canvas Page

Edge-to-edge content for visualizations that need maximum space.

```
┌─────────────────────────────────────────────────────────────┐
│ [Sidebar]│ ┌─────────────────────────────────────────────┐ │
│          │ │ Toolbar / Mini Header                       │ │
│          │ ├─────────────────────────────────────────────┤ │
│          │ │                                             │ │
│          │ │                                             │ │
│          │ │        Full Canvas Content                  │ │
│          │ │        (Graph, Map, Diagram)                │ │
│          │ │                                             │ │
│          │ │                                             │ │
│          │ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**When to use:**
- Process map visualization
- Graph editors
- Any content needing maximum canvas

**Specs:**
- No page padding
- Toolbar: 48px height, sticky
- Canvas: 100% of remaining height
- Floating controls (zoom, etc.) positioned over canvas

---

### 1.5 Wizard Page

Step-by-step flow with progress indication.

```
┌─────────────────────────────────────────────────────────────┐
│ [Sidebar]│ ┌─────────────────────────────────────────────┐ │
│          │ │ ① ──── ② ──── ③ ──── ④    Progress Steps   │ │
│          │ └─────────────────────────────────────────────┘ │
│          │ ┌─────────────────────────────────────────────┐ │
│          │ │                                             │ │
│          │ │              Step Content                   │ │
│          │ │              (centered)                     │ │
│          │ │                                             │ │
│          │ └─────────────────────────────────────────────┘ │
│          │ ┌─────────────────────────────────────────────┐ │
│          │ │          [Back]              [Next →]       │ │
│          │ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**When to use:**
- Onboarding flows
- Multi-step forms
- Upload and configuration flows

**Specs:**
- Progress indicator: Top, centered or left-aligned
- Content: Centered, max-width 560px
- Navigation: Bottom, sticky or inline
- Back button: Left (secondary style)
- Next button: Right (primary style)

---

### 1.6 Settings Page

Vertical sections with save actions.

```
┌─────────────────────────────────────────────────────────────┐
│ [Sidebar]│ Page Header                                      │
│          │ ─────────────────────────────────────────────── │
│          │ ┌─────────────────────────────────────────────┐ │
│          │ │ Section 1 Title                             │ │
│          │ │ Description text                            │ │
│          │ │ ┌─────────────────────────────────────────┐ │ │
│          │ │ │ Form Fields                             │ │ │
│          │ │ └─────────────────────────────────────────┘ │ │
│          │ │              [Cancel] [Save]                │ │
│          │ └─────────────────────────────────────────────┘ │
│          │                                                  │
│          │ ┌─────────────────────────────────────────────┐ │
│          │ │ Section 2 Title                             │ │
│          │ │ ...                                         │ │
│          │ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**When to use:**
- User settings
- Workspace settings
- Preferences

**Specs:**
- Sections as cards
- Each section can have independent save
- Vertical gap between sections: 24px
- Max-width: 720px (readable forms)

---

## 2. Composition Patterns

### 2.1 Page Header Compositions

#### Minimal Header
```
Page Title
```
- Just the title
- Use when page purpose is obvious from context

#### Standard Header
```
Page Title                                    [Primary CTA]
Description or subtitle
```
- Title + single CTA
- Most common pattern

#### Full Header
```
Breadcrumb > Path > Current
← Back   Page Title                   [Secondary] [Primary]
         Description or context
```
- All elements present
- Use for nested/detail pages

#### Header with Tabs
```
Page Title
Description

[Tab 1]  [Tab 2]  [Tab 3]
─────────────────────────────────────────────────────────
```
- Tabs below title, content changes
- Use when page has distinct sub-views

---

### 2.2 Card Compositions

#### Stat Card
```
┌───────────────────────┐
│ Label            [?]  │
│ 1,234                 │  ← Large value
│ ↑ 12% vs last week    │  ← Trend (optional)
└───────────────────────┘
```

#### Content Card
```
┌───────────────────────┐
│ Title           [•••] │
│ Description text      │
│                       │
│ Content here          │
│                       │
└───────────────────────┘
```

#### Action Card (CTA Card)
```
┌───────────────────────┐
│                       │
│      [Icon]           │
│      Title            │
│      Description      │
│                       │
│   [Action Button]     │
│                       │
└───────────────────────┘
```

#### List Item Card
```
┌───────────────────────────────────────────────┐
│ [Avatar/Icon]  Title                    [•••] │
│                Subtitle / metadata            │
└───────────────────────────────────────────────┘
```

---

### 2.3 Filter Compositions

#### Inline Filters
```
┌──────────────────────────────────────────────────────────┐
│ [Search...        ] [Dropdown ▼] [Dropdown ▼] [+ Filter] │
└──────────────────────────────────────────────────────────┘
│ Results area below                                        │
```
- Filters inline above content
- Good for simple filtering (2-4 options)

#### Filter Panel (Right Sidebar)
```
┌────────────────────────────────┐│┌─────────────────┐
│                                │││ Filters         │
│   Main Content                 │││ ───────────     │
│   (list, visualization)        │││ [+ Add filter]  │
│                                │││                 │
│                                │││ Applied:        │
│                                │││ [Filter 1 ×]   │
│                                │││ [Filter 2 ×]   │
│                                │││                 │
│                                │││ [Clear all]     │
└────────────────────────────────┘│└─────────────────┘
```
- Complex filtering with many options
- Used in process explorer, data views

#### Filter Bar with Applied Tags
```
┌──────────────────────────────────────────────────────────┐
│ Applied: [Date: Last 7d ×] [Status: Active ×]  [Clear]   │
├──────────────────────────────────────────────────────────┤
│ Results area                                              │
```
- Show active filters as removable tags
- Quick overview of current filter state

---

### 2.4 Table Compositions

#### Simple Table
```
┌─────────────────────────────────────────────────────────┐
│ Column A        Column B         Column C               │
├─────────────────────────────────────────────────────────┤
│ Data            Data             Data                   │
│ Data            Data             Data                   │
│ Data            Data             Data                   │
└─────────────────────────────────────────────────────────┘
```

#### Table with Toolbar
```
┌─────────────────────────────────────────────────────────┐
│ [Search...    ] [Filter ▼]    Showing 1-20   [Export]   │
├─────────────────────────────────────────────────────────┤
│ □  Column A ↕    Column B       Column C       Actions  │
├─────────────────────────────────────────────────────────┤
│ □  Data          Data           Data           [•••]    │
│ □  Data          Data           Data           [•••]    │
├─────────────────────────────────────────────────────────┤
│            [◀ Prev]  Page 1 of 5  [Next ▶]              │
└─────────────────────────────────────────────────────────┘
```

#### Table with Selection Actions
```
┌─────────────────────────────────────────────────────────┐
│ 3 selected    [Delete]  [Export]  [Assign]    [Cancel]  │ ← Appears when selected
├─────────────────────────────────────────────────────────┤
│ ☑  Data...                                              │
│ □  Data...                                              │
│ ☑  Data...                                              │
│ ☑  Data...                                              │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Interaction Patterns

### 3.1 Loading States

#### Initial Load
- Show skeleton screens matching expected layout
- Skeletons: Animated shimmer, neutral-200 on neutral-100
- Preserve layout to prevent layout shift

#### Action Loading
- Button: Show spinner, disable, maintain width
- Form: Disable all inputs, show spinner on submit button
- Page transition: Keep current content, show top progress bar

#### Data Refresh
- Don't clear current data while loading
- Show subtle indicator (spinner in corner, progress bar)
- Update data in place

---

### 3.2 Error States

#### Inline Error (Forms)
```
┌─────────────────────────────────┐
│ Input value                     │  ← border-error-500
└─────────────────────────────────┘
  ⚠ Error message here              ← text-error-500
```

#### Section Error
```
┌─────────────────────────────────────────────────────────┐
│ ⚠ Unable to load data                          [Retry]  │
│   Something went wrong. Please try again.               │
└─────────────────────────────────────────────────────────┘
```

#### Page Error
- Use Empty State pattern with error variant
- Icon: Warning or error icon
- Message: What happened
- Action: Retry or navigate away

---

### 3.3 Empty States by Context

| Context | Primary Message | Secondary Message | CTA |
|---------|-----------------|-------------------|-----|
| **First visit** | "No X yet" | "Create your first X to..." | "Create X" |
| **No results** | "No results found" | "Try adjusting..." | "Clear filters" |
| **Deleted all** | "No X" | "You haven't created..." | "Create X" |
| **Search empty** | "No matches for 'query'" | "Try a different..." | "Clear search" |

---

### 3.4 Confirmation Patterns

#### Low-risk actions
- No confirmation needed
- Show toast on completion

#### Medium-risk actions
- Toast with undo option (e.g., "Deleted. [Undo]")
- 5-second window to undo

#### High-risk actions (destructive)
```
┌──────────────────────────────────────────────┐
│ Delete "Item Name"?                   [×]    │
├──────────────────────────────────────────────┤
│                                              │
│ This action cannot be undone. This will      │
│ permanently delete this item and all         │
│ associated data.                             │
│                                              │
├──────────────────────────────────────────────┤
│                    [Cancel]  [Delete]        │
└──────────────────────────────────────────────┘
```
- Modal confirmation required
- Destructive CTA is danger button
- Cancel is left, destructive action is right

---

### 3.5 Progressive Disclosure

#### Expandable Sections
```
▶ Section Title (collapsed)

▼ Section Title (expanded)
  └── Content revealed
```

#### "Show more" Pattern
```
Item 1
Item 2
Item 3
─────────────
[Show 5 more]
```

#### Advanced Options
```
┌─────────────────────────────────────────────┐
│ Basic options (always visible)              │
│                                             │
│ ▶ Advanced options                          │
└─────────────────────────────────────────────┘
```

---

### 3.6 Notification Patterns

#### When to use Toast
- Action feedback ("Saved", "Deleted", "Sent")
- Background task completion
- Non-critical information

#### When to use Inline Alert
- Form validation summary
- Section-specific warnings
- Persistent information (doesn't auto-dismiss)

#### When to use Modal
- Critical errors requiring acknowledgment
- Confirmations before destructive actions
- Information requiring immediate attention

---

## 4. State Patterns

### 4.1 Data Loading State Machine

Every data-driven view goes through these states:

```
┌─────────┐    load()    ┌─────────┐
│  IDLE   │ ──────────▶  │ LOADING │
└─────────┘              └────┬────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌─────────┐     ┌─────────┐     ┌─────────┐
        │ SUCCESS │     │  EMPTY  │     │  ERROR  │
        └────┬────┘     └────┬────┘     └────┬────┘
             │               │               │
             └───────────────┴───────────────┘
                              │
                          refresh()
                              │
                              ▼
                        ┌─────────┐
                        │REFRESHING│ (show current data + indicator)
                        └─────────┘
```

**Component must handle ALL states:**
- IDLE: Initial state before first load
- LOADING: Skeleton screens
- SUCCESS: Render data
- EMPTY: Empty state component
- ERROR: Error state component
- REFRESHING: Current data + loading indicator

---

### 4.2 Form State Pattern

```
┌─────────┐   edit    ┌─────────┐   submit   ┌────────────┐
│ PRISTINE│ ───────▶  │  DIRTY  │ ─────────▶ │ SUBMITTING │
└─────────┘           └────┬────┘            └──────┬─────┘
                           │                        │
                       reset()           ┌──────────┴──────────┐
                           │             ▼                     ▼
                           │       ┌─────────┐           ┌─────────┐
                           └─────▶ │ SUCCESS │           │  ERROR  │
                                   └─────────┘           └─────────┘
```

**UI Implications:**
- PRISTINE: Save button disabled
- DIRTY: Save button enabled, show unsaved indicator
- SUBMITTING: Form disabled, save shows spinner
- SUCCESS: Toast confirmation, form resets to PRISTINE
- ERROR: Form enabled, show error message

---

### 4.3 Selection State Pattern

```
NONE ────────────────▶ SINGLE ────────────────▶ MULTIPLE
      select(item)            select(item)

MULTIPLE ─────────────▶ SINGLE ─────────────▶ NONE
         deselect(item)       deselect(item)
```

**UI Implications:**
- NONE: No selection UI visible
- SINGLE: Show detail panel or highlight
- MULTIPLE: Show bulk action bar, count selected

---

## 5. Recipes

### 5.1 Recipe: Settings Page

**When to use:** User or workspace configuration

**Components needed:**
- Page Header (minimal)
- Card (for sections)
- Form inputs
- Button (save/cancel)
- Toast (save confirmation)
- Tabs (optional, if multiple categories)

**Layout pattern:** Settings Page (1.6)

**Structure:**
```
Page Header: "Settings"

Tab Bar (optional):
  [Profile] [Preferences] [Notifications] [Security]

Section Card: "Profile"
  Form fields...
  [Cancel] [Save]

Section Card: "Preferences"
  Form fields...
  [Cancel] [Save]
```

**States to handle:**
- Loading settings: Skeleton cards
- Save in progress: Disabled form, spinner on Save button
- Save success: Toast "Settings saved"
- Save error: Toast "Failed to save. Try again."
- Unsaved changes: Browser beforeunload warning

**Behavior:**
- Each section saves independently
- Cancel reverts to last saved state
- No auto-save (explicit save action)

---

### 5.2 Recipe: Notification Center

**When to use:** System notifications for user

**Components needed:**
- Button (bell icon trigger)
- Dropdown/Popover (notification list)
- Badge (unread count)
- List Item Card (each notification)
- Empty State

**Trigger anatomy:**
```
┌────────────────────────────┐
│ 🔔                         │  ← Bell icon
│ ●3                         │  ← Badge with count (if unread)
└────────────────────────────┘
```

**Dropdown anatomy:**
```
┌─────────────────────────────────────────┐
│ Notifications                [Mark all] │
├─────────────────────────────────────────┤
│ ●  Title of notification        2m ago  │  ← Unread (dot indicator)
│    Description text preview             │
├─────────────────────────────────────────┤
│    Title of notification       1h ago   │  ← Read
│    Description text preview             │
├─────────────────────────────────────────┤
│             [View all →]                │
└─────────────────────────────────────────┘
```

**States to handle:**
- No notifications: Empty state in dropdown
- All read: No badge on trigger
- New notification: Update count, animate badge

**Notification page (View All):**
- Standard Page layout
- Table or List of all notifications
- Filter by read/unread
- Bulk mark as read

---

### 5.3 Recipe: Activity Log

**When to use:** History of user or system actions

**Components needed:**
- Page Header
- Table (with pagination)
- Badge (action type)
- Filter (date range, action type)

**Table columns:**
| Action | Details | User | Date |
|--------|---------|------|------|
| Badge | Description | Avatar + name | Relative time |

**Filters:**
- Date range picker
- Action type dropdown
- User filter (if showing team activity)

**Empty state:**
- "No activity yet"
- "Your actions will appear here"

---

### 5.4 Recipe: File Upload Flow

**When to use:** Uploading event log data

**Layout pattern:** Wizard Page (1.5) or Modal

**Steps:**
1. **Select file** - Drag-drop zone or file picker
2. **Validate** - Show validation results, column detection
3. **Configure** - Column mapping, settings
4. **Process** - Progress indicator, success

**Step 1: Select File**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              ┌─────────────────────┐                   │
│              │     📁 Upload       │                   │
│              │                     │                   │
│              │  Drag & drop file   │                   │
│              │        or           │                   │
│              │  [Browse files]     │                   │
│              │                     │                   │
│              │  CSV, XES up to     │                   │
│              │  100MB              │                   │
│              └─────────────────────┘                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Step 2: Validate**
```
┌─────────────────────────────────────────────────────────┐
│ ✓ File uploaded: events.csv (2.4 MB)                   │
├─────────────────────────────────────────────────────────┤
│ Detected columns:                                       │
│ • case_id (123 unique values)                          │
│ • activity (45 unique values)                          │
│ • timestamp (date format: YYYY-MM-DD)                  │
│ • resource (12 unique values)                          │
├─────────────────────────────────────────────────────────┤
│ ⚠ 3 rows have missing timestamps (will be skipped)     │
└─────────────────────────────────────────────────────────┘
            [← Back]                    [Continue →]
```

**Step 3: Configure**
```
Map your columns:

Case ID:      [case_id        ▼]    ← Required
Activity:     [activity       ▼]    ← Required  
Timestamp:    [timestamp      ▼]    ← Required
Resource:     [resource       ▼]    ← Optional
```

**Step 4: Process**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              Processing your data...                    │
│                                                         │
│              [████████████░░░░░░] 67%                  │
│                                                         │
│              • Validating rows ✓                        │
│              • Creating event log ✓                     │
│              • Generating statistics...                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Success:**
- Modal or redirect to log detail page
- Toast: "File uploaded successfully"

**Error handling:**
- Invalid file type: Inline error on drop zone
- File too large: Inline error with size limit
- Validation errors: Summary with option to proceed or cancel

---

### 5.5 Recipe: Dashboard Home

**When to use:** Entry point / overview page

**Layout pattern:** Dashboard Page (1.2)

**Composition:**
```
Page Header: "Welcome back, [Name]"

Row 1 - Quick Stats (3-4 KPI cards):
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Event Logs │ │ Total Cases│ │ Last Upload│
│     3      │ │   45,230   │ │  2 days ago│
└────────────┘ └────────────┘ └────────────┘

Row 2 - Recent Activity:
┌─────────────────────────────────────────────────────────┐
│ Recent Event Logs                        [View all →]   │
├─────────────────────────────────────────────────────────┤
│ 📄 Orders_Q4.csv          12,345 cases    2 hours ago  │
│ 📄 Support_tickets.xes     8,901 cases    Yesterday    │
│ 📄 Invoice_process.csv    23,456 cases    3 days ago   │
└─────────────────────────────────────────────────────────┘

Row 3 - Quick Actions (optional):
┌─────────────────────────────────────────────────────────┐
│ Quick Actions                                           │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ 📤 Upload   │ │ 📊 Explore  │ │ ⚙️ Settings │        │
│ │ New File    │ │ Process Map │ │ Configure   │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
└─────────────────────────────────────────────────────────┘
```

**Empty state (new user):**
- Hide stats row
- Show prominent upload CTA
- Show getting started guide

---

### 5.6 Recipe: Data Table with Actions

**When to use:** Lists of items with CRUD operations

**Components:**
- Page Header (with "Create new" CTA)
- Search input
- Filter dropdown(s)
- Table
- Pagination
- Row actions menu
- Confirmation modal (delete)
- Toast (action feedback)

**Full composition:**
```
Page Header: "Event Logs"                   [Upload New]

┌─────────────────────────────────────────────────────────┐
│ [Search logs...        ]  [Status ▼]  [Date range ▼]    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ □  Name ↕        Cases    Events    Uploaded    Actions │
├─────────────────────────────────────────────────────────┤
│ □  Orders.csv    12,345   89,012    2 hours ago  [•••]  │
│ □  Support.xes    8,901   45,678    Yesterday    [•••]  │
│ □  Invoice.csv   23,456  156,789    3 days ago   [•••]  │
├─────────────────────────────────────────────────────────┤
│                  [◀]  1  2  3  ...  10  [▶]             │
└─────────────────────────────────────────────────────────┘
```

**Row action menu:**
```
[•••] →  ┌─────────────┐
         │ View        │
         │ Download    │
         │ ──────────  │
         │ Delete      │  ← Danger style
         └─────────────┘
```

**States:**
- Loading: Table skeleton
- Empty: Empty state with Upload CTA
- No results: Empty state with Clear filters CTA
- Delete confirmation: Modal

---

## 6. Decision Log

Document key design decisions for future reference.

### Decision 001: Sidebar vs Top Navigation
**Date:** 2024-12-30
**Decision:** Left sidebar navigation
**Rationale:** 
- Process mining apps are data-dense; sidebar preserves vertical space
- Consistent with competitor patterns (Celonis)
- Better for hierarchical navigation as features grow
**Alternatives considered:** Top nav (rejected: wastes vertical space)

### Decision 002: Cards vs Tables for Lists
**Date:** 2024-12-30
**Decision:** Tables for data lists, cards for object selection
**Rationale:**
- Tables: Better for comparing attributes, sorting, bulk operations
- Cards: Better for visual objects, thumbnails, grid layouts
**Examples:**
- Event log list → Table
- Process template selection → Cards

### Decision 003: Filter Panel Position
**Date:** 2024-12-30
**Decision:** Right sidebar for complex filtering, inline for simple
**Rationale:**
- Right panel keeps filters visible without scrolling
- Inline filters for quick 2-3 option filtering
- Matches Celonis pattern for process explorer
**Threshold:** >3 filter options → panel, ≤3 → inline

---

## Appendix: Recipe Template

When adding new recipes, use this template:

```markdown
### 5.X Recipe: [Name]

**When to use:** [Scenario description]

**Components needed:**
- Component 1
- Component 2

**Layout pattern:** [Reference to Section 1]

**Composition:**
[ASCII diagram of layout]

**States to handle:**
- State 1: [UI behavior]
- State 2: [UI behavior]

**Behavior:**
- [Interaction 1]
- [Interaction 2]

**Edge cases:**
- [Edge case]: [How to handle]
```

---

*End of Patterns & Recipes Document*
