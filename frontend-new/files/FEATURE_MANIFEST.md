# Feature Manifest: Process Mining Platform

> Version: 1.0.0 | Last Updated: 2024-12-30
> Status: Planning Complete — Development Ready

---

## Overview

This document tracks all features across development phases. Use this to:
- Understand what to build in each phase
- Track dependencies between features
- Monitor implementation status
- Provide context to AI coders

---

## Phase Summary

| Phase | Name | Focus | Duration | Status |
|-------|------|-------|----------|--------|
| **0** | Foundation | Shell, routing, design system | Week 1-2 | 🟡 In Progress |
| **1** | Base Platform | Settings, notifications, help | Week 3-4 | ⚪ Not Started |
| **2** | Data Foundation | Upload, logs, statistics | Week 5-6 | ⚪ Not Started |
| **3** | Process Discovery | Visualization, variants, filters | Week 7-9 | ⚪ Not Started |
| **4** | Analytics | Performance, conformance, rework | Week 10-12 | ⚪ Not Started |
| **5** | AI & Advanced | Predictions, insights, KG | Week 13+ | ⚪ Not Started |

**Status Legend:**
- ⚪ Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔴 Blocked

---

## Phase 0: Foundation

**Goal:** Establish the shell everything slots into

### Features

#### F0.1: App Shell
**Priority:** Critical
**Status:** ⚪ Not Started

**Description:** 
Core application layout with sidebar navigation, header area, and content region.

**Components Used:**
- Sidebar Navigation
- App Shell layout

**Acceptance Criteria:**
- [ ] Sidebar renders with all nav items (linked to placeholder pages)
- [ ] Active nav item highlights correctly
- [ ] Sidebar can collapse/expand
- [ ] Content area scrolls independently
- [ ] Responsive: sidebar collapses on mobile

**Dependencies:** None

---

#### F0.2: Routing Setup
**Priority:** Critical
**Status:** ⚪ Not Started

**Description:**
All routes defined with proper URL structure. Unimplemented pages show placeholder.

**Technical:**
- React Router (or equivalent)
- Route guards for auth
- 404 handling

**Acceptance Criteria:**
- [ ] All routes from IA document are defined
- [ ] Unimplemented routes show "Coming Soon" placeholder
- [ ] URL parameters work (`:id`, query strings)
- [ ] Browser back/forward works correctly
- [ ] Deep linking works

**Dependencies:** F0.1 (App Shell)

---

#### F0.3: Mock Authentication
**Priority:** High
**Status:** ⚪ Not Started

**Description:**
Simple login page that simulates authentication without real backend.

**Components Used:**
- Input
- Button
- Card
- Logo

**Acceptance Criteria:**
- [ ] Login page renders at `/login`
- [ ] Any email/password accepted
- [ ] Session stored (localStorage or memory)
- [ ] Protected routes redirect to login
- [ ] "Continue as Guest" bypasses login (dev mode)
- [ ] Logout clears session

**Dependencies:** F0.2 (Routing)

---

#### F0.4: Theme Infrastructure
**Priority:** Medium
**Status:** ⚪ Not Started

**Description:**
CSS custom properties for design tokens, with optional dark mode support.

**Technical:**
- CSS variables from Design System
- Light theme default
- Dark theme toggle (optional, can be Phase 1)

**Acceptance Criteria:**
- [ ] All design tokens available as CSS variables
- [ ] Colors, spacing, typography consistent across app
- [ ] Theme can be switched (if dark mode included)
- [ ] Tokens match Design System document

**Dependencies:** None

---

#### F0.5: Placeholder Page Component
**Priority:** High
**Status:** ⚪ Not Started

**Description:**
Reusable component for unimplemented pages.

**Components Used:**
- Empty State pattern
- Button

**Acceptance Criteria:**
- [ ] Shows "Coming Soon" message
- [ ] Indicates which phase the feature is in
- [ ] Has "Back to Home" button
- [ ] Visually consistent with design system

**Dependencies:** F0.4 (Theme)

---

### Phase 0 Completion Checklist
- [ ] F0.1: App Shell
- [ ] F0.2: Routing Setup
- [ ] F0.3: Mock Authentication
- [ ] F0.4: Theme Infrastructure
- [ ] F0.5: Placeholder Page Component
- [ ] All pages accessible (even if placeholder)
- [ ] Navigation works end-to-end
- [ ] Design tokens applied

---

## Phase 1: Base Platform

**Goal:** Generic SaaS infrastructure unrelated to process mining

### Features

#### F1.1: Home Dashboard
**Priority:** High
**Status:** ⚪ Not Started

**Description:**
Landing page after login. Shows overview stats, recent items, quick actions.

**Layout:** Dashboard Page pattern

**Components Used:**
- Page Header
- Stat Card (×3-4)
- Card
- List/Table
- Empty State

**Acceptance Criteria:**
- [ ] Shows welcome message with user name
- [ ] Displays stat cards (placeholder data OK)
- [ ] Shows recent event logs list (or empty state)
- [ ] Quick action cards navigate to correct pages
- [ ] Empty state shown when no data exists

**Dependencies:** F0.1, F0.3

**Mock Data Needed:**
- User name
- Stats: log count, case count, last activity
- Recent logs list

---

#### F1.2: Settings - Profile
**Priority:** High
**Status:** ⚪ Not Started

**Description:**
User profile editing: name, avatar.

**Layout:** Settings Page pattern

**Components Used:**
- Page Header
- Tabs
- Card
- Input
- Avatar (with upload)
- Button

**Acceptance Criteria:**
- [ ] Tab navigation works (Profile/Preferences/Notifications)
- [ ] Profile form displays current values
- [ ] Name field is editable
- [ ] Email field is read-only
- [ ] Avatar can be changed (mock upload OK)
- [ ] Cancel reverts changes
- [ ] Save shows success toast
- [ ] Form validation on required fields

**Dependencies:** F0.1, F1.6 (Toast)

---

#### F1.3: Settings - Preferences
**Priority:** Medium
**Status:** ⚪ Not Started

**Description:**
App preferences: theme, date format, timezone.

**Layout:** Settings Page pattern

**Components Used:**
- Card
- Select/Dropdown
- Toggle
- Button

**Acceptance Criteria:**
- [ ] Theme selector (Light/Dark/System)
- [ ] Date format selector
- [ ] Timezone selector
- [ ] Toggle switches for privacy settings
- [ ] Settings persist (localStorage OK)
- [ ] Cancel/Save behavior

**Dependencies:** F1.2

---

#### F1.4: Settings - Notification Preferences
**Priority:** Medium
**Status:** ⚪ Not Started

**Description:**
Configure which notifications user receives.

**Layout:** Settings Page pattern

**Components Used:**
- Card
- Toggle
- Button

**Acceptance Criteria:**
- [ ] Email notification toggles
- [ ] In-app notification toggles
- [ ] Settings persist
- [ ] Cancel/Save behavior

**Dependencies:** F1.2

---

#### F1.5: Notification Center
**Priority:** High
**Status:** ⚪ Not Started

**Description:**
View all notifications, mark as read, filter.

**Layout:** Standard Page pattern

**Components Used:**
- Page Header
- Tabs (All/Unread)
- Notification list items
- Badge
- Empty State

**Acceptance Criteria:**
- [ ] Bell icon in nav shows unread count
- [ ] Clicking bell navigates to notification center
- [ ] Notifications list with read/unread status
- [ ] Click notification marks as read
- [ ] "Mark all as read" button
- [ ] Tab filtering works
- [ ] Empty state when no notifications

**Dependencies:** F0.1

**Mock Data Needed:**
- Sample notifications (3-5)
- Mix of read/unread

---

#### F1.6: Toast Notification System
**Priority:** Critical
**Status:** ⚪ Not Started

**Description:**
Global toast notification system for action feedback.

**Components Used:**
- Toast component

**Acceptance Criteria:**
- [ ] Toasts appear in top-right
- [ ] Support all variants (info, success, warning, error)
- [ ] Auto-dismiss after 5s (configurable)
- [ ] Manual dismiss with X button
- [ ] Multiple toasts stack
- [ ] Can be triggered from anywhere in app

**Dependencies:** F0.4 (Theme)

---

#### F1.7: Activity Log
**Priority:** Medium
**Status:** ⚪ Not Started

**Description:**
View history of user actions in the platform.

**Layout:** Standard Page pattern

**Components Used:**
- Page Header
- Filters (date range, action type)
- Table
- Badge
- Pagination

**Acceptance Criteria:**
- [ ] Table displays action history
- [ ] Date range filter works
- [ ] Action type filter works
- [ ] Pagination for long lists
- [ ] Export button (can be placeholder)
- [ ] Empty state

**Dependencies:** F0.1

**Mock Data Needed:**
- Sample activity entries (10-20)

---

#### F1.8: Help Center
**Priority:** Low
**Status:** ⚪ Not Started

**Description:**
Static help content and links to documentation.

**Layout:** Standard Page pattern

**Components Used:**
- Page Header
- Search Input
- Card grid
- Link list

**Acceptance Criteria:**
- [ ] Search input (can be non-functional initially)
- [ ] Getting started cards link to placeholder articles
- [ ] FAQ section with expandable items
- [ ] Contact support link

**Dependencies:** F0.1

---

### Phase 1 Completion Checklist
- [ ] F1.1: Home Dashboard
- [ ] F1.2: Settings - Profile
- [ ] F1.3: Settings - Preferences
- [ ] F1.4: Settings - Notification Preferences
- [ ] F1.5: Notification Center
- [ ] F1.6: Toast Notification System
- [ ] F1.7: Activity Log
- [ ] F1.8: Help Center
- [ ] All settings save and persist
- [ ] Toast notifications work globally
- [ ] App feels like complete SaaS (even without domain features)

---

## Phase 2: Data Foundation

**Goal:** Get data into the system

### Features

#### F2.1: Event Logs List
**Priority:** Critical
**Status:** ⚪ Not Started

**Description:**
List all uploaded event logs with search, filter, and actions.

**Layout:** Standard Page with table

**SDK Integration:** `sdk.logs.list()`

**Components Used:**
- Page Header (with Upload CTA)
- Search Input
- Table
- Row actions menu
- Pagination
- Empty State

**Acceptance Criteria:**
- [ ] Table displays all logs
- [ ] Columns: Name, Cases, Events, Uploaded date, Actions
- [ ] Search filters by name
- [ ] Sortable columns
- [ ] Row actions: View, Download, Delete
- [ ] Delete shows confirmation modal
- [ ] Empty state with Upload CTA
- [ ] "Upload File" button navigates to upload flow

**Dependencies:** F0.1, F1.6

---

#### F2.2: File Upload Flow
**Priority:** Critical
**Status:** ⚪ Not Started

**Description:**
Multi-step wizard to upload and configure event log files.

**Layout:** Wizard Page pattern

**SDK Integration:** 
- `sdk.logs.ingest(file)`
- `sdk.logs.detectColumns(file)`

**Components Used:**
- Progress indicator
- Drag-drop upload zone
- File preview
- Column mapping form
- Progress bar

**Steps:**
1. Select File (drag-drop or browse)
2. Validate & Preview (show detected columns, sample rows)
3. Configure (map columns to case_id, activity, timestamp)
4. Process (progress indicator, success)

**Acceptance Criteria:**
- [ ] Drag-drop file upload works
- [ ] File type validation (CSV, XES)
- [ ] File size limit check
- [ ] Column auto-detection
- [ ] Sample data preview (first 10 rows)
- [ ] Column mapping with required fields
- [ ] Processing progress indicator
- [ ] Success state with navigation to log detail
- [ ] Error handling at each step

**Dependencies:** F2.1

---

#### F2.3: Log Detail Page
**Priority:** High
**Status:** ⚪ Not Started

**Description:**
Overview of a single event log with statistics and actions.

**Layout:** Standard Page with tabs

**SDK Integration:**
- `sdk.logs.get(logId)`
- `sdk.logs.analyze(logId)`

**Components Used:**
- Page Header (with breadcrumb)
- Tabs (Overview, Preview, Statistics)
- Stat Cards
- Table
- Actions dropdown

**Acceptance Criteria:**
- [ ] Breadcrumb navigation works
- [ ] Overview tab shows key stats
- [ ] Preview tab shows sample data
- [ ] Statistics tab shows analysis
- [ ] Actions: Export, Delete, Open in Explorer

**Dependencies:** F2.1, F2.2

---

#### F2.4: Log Statistics
**Priority:** High
**Status:** ⚪ Not Started

**Description:**
Detailed statistics for an event log (cases, events, activities, durations).

**SDK Integration:** `sdk.logs.analyze(logId)`

**Components Used:**
- Stat Cards
- Bar charts (activity frequency)
- Timeline chart (cases over time)
- Table (top variants preview)

**Acceptance Criteria:**
- [ ] Case count, event count, activity count
- [ ] Date range of data
- [ ] Activity frequency chart
- [ ] Cases over time chart
- [ ] Average events per case
- [ ] Top 5 variants preview

**Dependencies:** F2.3

---

### Phase 2 Completion Checklist
- [ ] F2.1: Event Logs List
- [ ] F2.2: File Upload Flow
- [ ] F2.3: Log Detail Page
- [ ] F2.4: Log Statistics
- [ ] Can upload CSV/XES files
- [ ] Files are processed and statistics generated
- [ ] Files appear in list
- [ ] Can view and delete files

---

## Phase 3: Process Discovery

**Goal:** The "aha moment" — seeing your process visualized

### Features

#### F3.1: Process Visualization
**Priority:** Critical
**Status:** ⚪ Not Started

**Description:**
Interactive process map showing activities and transitions.

**Layout:** Full Canvas with panels

**SDK Integration:**
- `sdk.discovery.discover({logId, minerType})`
- `sdk.visualization.getDFG(logId)`

**Components Used:**
- Toolbar
- Canvas (graph rendering)
- Zoom controls
- Mini-map (optional)
- Node tooltips

**Acceptance Criteria:**
- [ ] Process map renders from log data
- [ ] Activities shown as nodes with counts
- [ ] Transitions shown as edges with durations
- [ ] Pan and zoom works
- [ ] Clicking node shows detail popover
- [ ] Edge labels show time
- [ ] Loading state while discovering

**Dependencies:** F2.1, F2.4

---

#### F3.2: Variant Explorer
**Priority:** High
**Status:** ⚪ Not Started

**Description:**
List and explore process variants (unique execution paths).

**SDK Integration:** `sdk.logs.listVariants(logId)`

**Components Used:**
- List/Table
- Variant path visualization
- Frequency indicators
- Selection state

**Acceptance Criteria:**
- [ ] Variants listed by frequency
- [ ] Each variant shows path and count
- [ ] Selecting variant highlights in process map
- [ ] Can filter to show only selected variant
- [ ] Variant percentage of total

**Dependencies:** F3.1

---

#### F3.3: Activity Details
**Priority:** Medium
**Status:** ⚪ Not Started

**Description:**
Detailed view when clicking an activity node.

**Components Used:**
- Popover/Panel
- Stat displays
- Filter buttons

**Acceptance Criteria:**
- [ ] Shows activity name and count
- [ ] Percentage of cases containing activity
- [ ] Average time at activity
- [ ] Filter buttons: "with this activity", "without", etc.
- [ ] Clicking filter updates view

**Dependencies:** F3.1

---

#### F3.4: Filter Panel
**Priority:** High
**Status:** ⚪ Not Started

**Description:**
Right sidebar for filtering process data.

**SDK Integration:** `sdk.filtering.applyFilter(logId, {filters})`

**Components Used:**
- Panel
- Filter controls (date range, dropdowns)
- Applied filter tags
- Clear button

**Acceptance Criteria:**
- [ ] Panel toggles open/closed
- [ ] Time range filter
- [ ] Activity include/exclude filter
- [ ] Top-K variants filter
- [ ] Applied filters shown as tags
- [ ] Filters update visualization
- [ ] "Clear all" resets

**Dependencies:** F3.1

---

#### F3.5: Export Process Map
**Priority:** Low
**Status:** ⚪ Not Started

**Description:**
Export visualization as image.

**SDK Integration:** `sdk.visualization.getModelSVG(modelId)`

**Acceptance Criteria:**
- [ ] Export as SVG button
- [ ] Export as PNG button
- [ ] Downloads file to user's device

**Dependencies:** F3.1

---

### Phase 3 Completion Checklist
- [ ] F3.1: Process Visualization
- [ ] F3.2: Variant Explorer
- [ ] F3.3: Activity Details
- [ ] F3.4: Filter Panel
- [ ] F3.5: Export Process Map
- [ ] Users can see their process as a map
- [ ] Users can explore variants
- [ ] Users can filter the view
- [ ] **This is the MVP milestone**

---

## Phase 4: Analytics

**Goal:** Actionable intelligence from process data

### Features

#### F4.1: Performance Dashboard
**SDK:** `sdk.analytics.getPerformanceDashboard(logId)`
**Includes:** Bottlenecks, cycle time, throughput

#### F4.2: Conformance Checking
**SDK:** `sdk.conformance.check({logId, modelId})`
**Includes:** Fitness score, deviation highlighting

#### F4.3: Rework Analysis
**SDK:** `sdk.analytics.getRework(logId)`
**Includes:** Loop detection, rework frequency

#### F4.4: Comparative Views
**Description:** Compare two filtered views side-by-side

---

## Phase 5: AI & Advanced

### Features

#### F5.1: Predictive Analytics
**SDK:** `sdk.predictions.trainPredictor()`, `sdk.predictions.predict()`

#### F5.2: AI Insights
**Description:** Auto-generated insights from process data

#### F5.3: Natural Language Queries
**Description:** Ask questions about your process in plain English

#### F5.4: Knowledge Graph (if applicable)
**Description:** Entity relationships and process context

---

## Appendix: Feature Spec Template

When adding new features, use this template:

```markdown
#### F[Phase].[Number]: [Feature Name]
**Priority:** Critical | High | Medium | Low
**Status:** ⚪ Not Started | 🟡 In Progress | 🟢 Complete | 🔴 Blocked

**Description:**
[What this feature does]

**Layout:** [Reference to Patterns document]

**SDK Integration:** [Which SDK methods are used]

**Components Used:**
- Component 1
- Component 2

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Dependencies:** [Which features must be complete first]

**Mock Data Needed:** [What mock data is required]

**Notes:** [Any additional context]
```

---

## Appendix: SDK Method Reference

Quick reference for SDK methods used in features:

| Method | Phase | Used In |
|--------|-------|---------|
| `sdk.logs.ingest(file)` | 2 | F2.2 |
| `sdk.logs.detectColumns(file)` | 2 | F2.2 |
| `sdk.logs.analyze(logId)` | 2 | F2.3, F2.4 |
| `sdk.logs.listVariants(logId)` | 3 | F3.2 |
| `sdk.discovery.discover()` | 3 | F3.1 |
| `sdk.visualization.getDFG(logId)` | 3 | F3.1 |
| `sdk.visualization.getModelSVG()` | 3 | F3.5 |
| `sdk.filtering.applyFilter()` | 3 | F3.4 |
| `sdk.conformance.check()` | 4 | F4.2 |
| `sdk.analytics.getPerformanceDashboard()` | 4 | F4.1 |
| `sdk.analytics.getRework()` | 4 | F4.3 |
| `sdk.predictions.trainPredictor()` | 5 | F5.1 |
| `sdk.predictions.predict()` | 5 | F5.1 |

---

*End of Feature Manifest*
