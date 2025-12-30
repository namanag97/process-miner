# Information Architecture: Process Mining Platform

> Version: 1.0.0 | Last Updated: 2024-12-30
> Status: Foundation — All routes defined, phased implementation

---

## Overview

This document defines the complete navigation structure, URL patterns, and page inventory for the platform. All routes exist from Phase 0, but render placeholder content until their implementation phase.

---

## Navigation Structure

### Primary Navigation (Sidebar)

```
┌─────────────────────────────────────────┐
│ [Logo] Process Miner                    │
├─────────────────────────────────────────┤
│                                         │
│ MAIN                                    │
│   🏠  Home                              │  → Phase 1
│   📁  Event Logs                        │  → Phase 2
│   🔍  Process Explorer                  │  → Phase 3
│   📊  Analytics                         │  → Phase 4
│                                         │
│ AI & ADVANCED                           │
│   🤖  AI Insights                       │  → Phase 5
│   🔮  Predictions                       │  → Phase 5
│                                         │
├─────────────────────────────────────────┤
│                                         │
│ SYSTEM                                  │
│   ⚙️  Settings                          │  → Phase 1
│   ❓  Help                              │  → Phase 1
│                                         │
├─────────────────────────────────────────┤
│   🔔  Notifications              [3]    │  → Phase 1
│   👤  User Name                         │
│       user@email.com                    │
└─────────────────────────────────────────┘
```

---

## Route Definitions

### Phase 0: Foundation Shell

| Route | Page | Purpose | Notes |
|-------|------|---------|-------|
| `/` | Redirect | Redirect to `/home` | — |
| `/login` | Login | Mock auth | Bypass-able in dev |
| `/logout` | Logout | Clear session | Redirect to login |

### Phase 1: Base Platform

| Route | Page | Purpose | Status |
|-------|------|---------|--------|
| `/home` | Dashboard Home | Entry point, quick stats | Phase 1 |
| `/settings` | Settings Index | Redirect to profile | — |
| `/settings/profile` | Profile Settings | User profile form | Phase 1 |
| `/settings/preferences` | Preferences | App preferences | Phase 1 |
| `/settings/notifications` | Notification Settings | Notification preferences | Phase 1 |
| `/notifications` | Notification Center | All notifications | Phase 1 |
| `/activity` | Activity Log | User action history | Phase 1 |
| `/help` | Help Center | Help & support | Phase 1 |

### Phase 2: Data Foundation
logs have renamed into processes - find
| Route | Page | Purpose | Status |
|-------|------|---------|--------|
| `/logs` | Event Logs List | All uploaded logs | Phase 2 |
| `/logs/upload` | Upload Flow | File upload wizard | Phase 2 |
| `/logs/:id` | Log Detail | Single log overview | Phase 2 |
| `/logs/:id/preview` | Data Preview | Sample data view | Phase 2 |
| `/logs/:id/columns` | Column Mapping | Configure columns | Phase 2 |
| `/logs/:id/statistics` | Log Statistics | Case/event stats | Phase 2 |

### Phase 3: Process Discovery

| Route | Page | Purpose | Status |
|-------|------|---------|--------|
| `/explorer` | Explorer Index | Log selector | Phase 3 |
| `/explorer/:logId` | Process Explorer | Main visualization | Phase 3 |
| `/explorer/:logId/variants` | Variants List | All variants | Phase 3 |
| `/explorer/:logId/activities` | Activities List | Activity details | Phase 3 |

### Phase 4: Analytics

| Route | Page | Purpose | Status |
|-------|------|---------|--------|
| `/analytics` | Analytics Index | Analytics dashboard | Phase 4 |
| `/analytics/performance` | Performance | Bottlenecks, cycle time | Phase 4 |
| `/analytics/conformance` | Conformance | Model fitness | Phase 4 |
| `/analytics/rework` | Rework Analysis | Loop detection | Phase 4 |

### Phase 5: AI & Advanced

| Route | Page | Purpose | Status |
|-------|------|---------|--------|
| `/ai` | AI Index | AI features hub | Phase 5 |
| `/ai/insights` | AI Insights | Auto-generated insights | Phase 5 |
| `/ai/predictions` | Predictions | Predictive models | Phase 5 |
| `/ai/predictions/:id` | Predictor Detail | Single predictor | Phase 5 |

---

## Page Specifications

### Phase 0 Pages

#### Login (`/login`)
**Layout:** Centered card, no sidebar
**Components:** Card, Input, Button, Logo
**Content:**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                    [Logo]                               │
│              Process Mining Platform                    │
│                                                         │
│         ┌─────────────────────────────┐                │
│         │ Email                       │                │
│         └─────────────────────────────┘                │
│         ┌─────────────────────────────┐                │
│         │ Password                    │                │
│         └─────────────────────────────┘                │
│                                                         │
│              [Sign In]                                  │
│                                                         │
│         ─────── or ───────                             │
│                                                         │
│              [Continue as Guest]  ← Dev mode           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Behavior:**
- Mock auth: Accept any email/password
- Store user in session
- Redirect to `/home` on success
- "Continue as Guest" for dev mode

---

### Phase 1 Pages

#### Home Dashboard (`/home`)
**Layout:** Dashboard Page
**Components:** Page Header, Stat Card (×3-4), Card, List, Empty State
**Content:**
```
Welcome back, [User Name]

┌─────────┐ ┌─────────┐ ┌─────────┐
│ Logs: 3 │ │Cases: 45K│ │ Last: 2d│
└─────────┘ └─────────┘ └─────────┘

┌─────────────────────────────────────┐
│ Recent Event Logs        [View all] │
├─────────────────────────────────────┤
│ List of recent logs...              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Quick Actions                       │
│ [Upload] [Explore] [Settings]       │
└─────────────────────────────────────┘
```

**Empty state (no logs):**
- Hide stats
- Show getting started CTA
- Prominent "Upload your first file" action

---

#### Settings - Profile (`/settings/profile`)
**Layout:** Settings Page
**Components:** Page Header, Tabs, Card, Input, Avatar upload, Button
**Content:**
```
Settings

[Profile] [Preferences] [Notifications]

┌─────────────────────────────────────────────────────────┐
│ Profile Information                                     │
│                                                         │
│ ┌─────┐                                                │
│ │Avatar│  [Change photo]                               │
│ └─────┘                                                │
│                                                         │
│ Full Name                                              │
│ ┌─────────────────────────────────┐                   │
│ │ John Doe                        │                   │
│ └─────────────────────────────────┘                   │
│                                                         │
│ Email                                                  │
│ ┌─────────────────────────────────┐                   │
│ │ john@example.com                │  ← Read-only      │
│ └─────────────────────────────────┘                   │
│                                                         │
│                    [Cancel] [Save Changes]             │
└─────────────────────────────────────────────────────────┘
```

---

#### Settings - Preferences (`/settings/preferences`)
**Layout:** Settings Page
**Components:** Page Header, Tabs, Card, Select, Toggle, Button
**Content:**
```
Settings

[Profile] [Preferences] [Notifications]

┌─────────────────────────────────────────────────────────┐
│ Display                                                 │
│                                                         │
│ Theme                                                  │
│ ┌─────────────────────────────────┐                   │
│ │ System default              ▼   │                   │
│ └─────────────────────────────────┘                   │
│                                                         │
│ Date Format                                            │
│ ┌─────────────────────────────────┐                   │
│ │ DD/MM/YYYY                  ▼   │                   │
│ └─────────────────────────────────┘                   │
│                                                         │
│ Time Zone                                              │
│ ┌─────────────────────────────────┐                   │
│ │ UTC+0 (London)              ▼   │                   │
│ └─────────────────────────────────┘                   │
│                                                         │
│                    [Cancel] [Save Changes]             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Data & Privacy                                          │
│                                                         │
│ [Toggle] Share anonymous usage data                    │
│ [Toggle] Enable keyboard shortcuts                     │
│                                                         │
│                    [Cancel] [Save Changes]             │
└─────────────────────────────────────────────────────────┘
```

---

#### Settings - Notifications (`/settings/notifications`)
**Layout:** Settings Page
**Components:** Page Header, Tabs, Card, Toggle, Button
**Content:**
```
Settings

[Profile] [Preferences] [Notifications]

┌─────────────────────────────────────────────────────────┐
│ Email Notifications                                     │
│                                                         │
│ [Toggle] Processing complete                           │
│          Get notified when file processing finishes    │
│                                                         │
│ [Toggle] Weekly summary                                │
│          Receive a weekly digest of your activity      │
│                                                         │
│ [Toggle] Product updates                               │
│          Learn about new features and improvements     │
│                                                         │
│                    [Cancel] [Save Changes]             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ In-App Notifications                                    │
│                                                         │
│ [Toggle] Show desktop notifications                    │
│ [Toggle] Play sound for notifications                  │
│                                                         │
│                    [Cancel] [Save Changes]             │
└─────────────────────────────────────────────────────────┘
```

---

#### Notification Center (`/notifications`)
**Layout:** Standard Page
**Components:** Page Header, Tabs, Table/List, Badge, Empty State
**Content:**
```
Notifications                           [Mark all as read]

[All] [Unread (3)]

┌─────────────────────────────────────────────────────────┐
│ ●  File processing complete               2 hours ago  │
│    Orders.csv has been processed successfully          │
├─────────────────────────────────────────────────────────┤
│ ●  New feature available                  Yesterday    │
│    Check out the new variant explorer                  │
├─────────────────────────────────────────────────────────┤
│    Weekly summary                         3 days ago   │
│    Your activity summary for last week                 │
└─────────────────────────────────────────────────────────┘
```

**Empty state:**
- "No notifications"
- "You're all caught up!"

---

#### Activity Log (`/activity`)
**Layout:** Standard Page
**Components:** Page Header, Filter (date range), Table, Badge, Pagination
**Content:**
```
Activity Log

┌─────────────────────────────────────────────────────────┐
│ [Last 7 days ▼]  [All actions ▼]           [Export]    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Action            Description         Date             │
├─────────────────────────────────────────────────────────┤
│ [Upload]          Uploaded Orders.csv  2 hours ago    │
│ [View]            Viewed process map   3 hours ago    │
│ [Settings]        Updated profile      Yesterday      │
│ [Login]           Signed in            2 days ago     │
└─────────────────────────────────────────────────────────┘
```

---

#### Help Center (`/help`)
**Layout:** Standard Page
**Components:** Page Header, Search, Card grid, Link list
**Content:**
```
Help Center

┌─────────────────────────────────────────────────────────┐
│ [Search help articles...                             ] │
└─────────────────────────────────────────────────────────┘

Getting Started
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ 📤 Upload   │ │ 🔍 Explorer │ │ 📊 Analytics│
│ your first  │ │ basics      │ │ overview    │
│ file        │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘

Common Questions
• How do I upload a file?
• What file formats are supported?
• How do I interpret the process map?

Need more help?
[Contact Support]  [Documentation →]
```

---

### Phase 2 Pages

#### Event Logs List (`/logs`)
**Layout:** Standard Page
**Components:** Page Header, Search, Table, Pagination, Empty State
**Primary CTA:** "Upload File"

---

#### Upload Flow (`/logs/upload`)
**Layout:** Wizard Page
**Steps:** 
1. Select File
2. Validate & Preview
3. Configure Columns
4. Process

---

#### Log Detail (`/logs/:id`)
**Layout:** Standard Page with tabs
**Tabs:** Overview, Preview, Statistics
**Components:** Page Header (with breadcrumb), Tabs, Stat Cards, Table

---

### Phase 3 Pages

#### Process Explorer (`/explorer/:logId`)
**Layout:** Full Canvas with right panel
**Components:** Toolbar, Canvas (process map), Filter Panel, Detail Popover
**Features:** Zoom, pan, node selection, filtering

---

### Phase 4 Pages

#### Analytics Dashboard (`/analytics`)
**Layout:** Dashboard Page
**Components:** KPI Cards, Charts, Tables
**Sub-pages:** Performance, Conformance, Rework

---

### Phase 5 Pages

#### AI Insights (`/ai/insights`)
**Layout:** Standard Page
**Components:** Insight cards, Natural language query input

---

## Placeholder Page Component

For unimplemented pages, show consistent placeholder:

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                    🚧                                   │
│                                                         │
│              Coming Soon                                │
│                                                         │
│      This feature is under development.                │
│      Expected in Phase [X].                            │
│                                                         │
│              [Back to Home]                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## URL Parameter Conventions

| Parameter | Format | Example | Usage |
|-----------|--------|---------|-------|
| `:id` | UUID or slug | `abc-123` | Resource identifier |
| `:logId` | UUID | `550e8400-e29b-41d4-a716-446655440000` | Event log ID |
| `?tab=` | string | `?tab=preview` | Active tab |
| `?page=` | number | `?page=2` | Pagination |
| `?search=` | string | `?search=orders` | Search query |
| `?filter=` | JSON | `?filter={"status":"active"}` | Encoded filters |

---

## Breadcrumb Patterns

| Page | Breadcrumb |
|------|------------|
| Home | (none) |
| Settings | Settings |
| Settings/Profile | Settings > Profile |
| Event Logs | Event Logs |
| Log Detail | Event Logs > [Log Name] |
| Log Statistics | Event Logs > [Log Name] > Statistics |
| Process Explorer | Event Logs > [Log Name] > Explorer |

---

## Navigation State

### Active States
- Current route highlights corresponding nav item
- Parent items highlight when child is active
- Breadcrumb shows full path

### Badge States
- Notification bell shows unread count
- Nav items may show status badges (e.g., "New")

### Collapsed Sidebar
- Icons only
- Tooltips on hover
- User section shows avatar only

---

## Implementation Checklist

### Phase 0: Shell
- [ ] App shell with sidebar
- [ ] Router with all routes defined
- [ ] Placeholder page component
- [ ] Login page (mock)
- [ ] Navigation state management

### Phase 1: Base
- [ ] Home dashboard
- [ ] Settings (all tabs)
- [ ] Notification center
- [ ] Activity log
- [ ] Help center
- [ ] Toast system

### Phase 2: Data
- [ ] Event logs list
- [ ] Upload wizard
- [ ] Log detail pages
- [ ] Column mapping UI

### Phase 3: Explorer
- [ ] Process visualization
- [ ] Variant explorer
- [ ] Activity details
- [ ] Filter panel

### Phase 4: Analytics
- [ ] Analytics dashboard
- [ ] Performance page
- [ ] Conformance page
- [ ] Rework page

### Phase 5: AI
- [ ] AI insights
- [ ] Prediction management
- [ ] Natural language interface

---

*End of Information Architecture Document*
