# ATLAS Flow Specifications
## Detailed User Flows & Wireframes

**Prepared by: Fictive Kin Design Studio**
**Version: 1.0**

---

# Flow 1: Event Log Upload (P0 - Critical Path)

## Overview
The upload flow is the entry point for all process mining. It must be flawless—this is our "Seinfeld App" foundation.

## User Journey

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   USER GOAL: "I want to upload my event log and start analyzing"         │
│                                                                          │
│   Step 1        Step 2         Step 3          Step 4        Step 5      │
│   ┌─────┐      ┌─────┐        ┌─────┐         ┌─────┐       ┌─────┐     │
│   │ 1   │ ──▶  │ 2   │  ──▶   │ 3   │  ──▶    │ 4   │ ──▶   │ 5   │     │
│   │     │      │     │        │     │         │     │       │     │     │
│   │File │      │Auto │        │Map  │         │Wait │       │Done │     │
│   │Pick │      │Detect│       │Cols │         │Proc │       │!    │     │
│   └─────┘      └─────┘        └─────┘         └─────┘       └─────┘     │
│                                                                          │
│   ~5 sec       ~3 sec         ~30 sec         ~10-60 sec    Instant     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: File Selection

### Wireframe
```
┌─────────────────────────────────────────────────────────────────────────┐
│ ← Back    Upload Event Log                                     Step 1/5 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │                         📁                                      │   │
│  │                                                                 │   │
│  │              Drag and drop your event log here                  │   │
│  │                                                                 │   │
│  │                   ─── or ───                                    │   │
│  │                                                                 │   │
│  │                  [ Browse Files ]                               │   │
│  │                                                                 │   │
│  │     ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                     │   │
│  │     │ CSV  │  │ XES  │  │ XLSX │  │Parquet│                    │   │
│  │     └──────┘  └──────┘  └──────┘  └──────┘                     │   │
│  │                                                                 │   │
│  │              Maximum file size: 500 MB                          │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ℹ️  Need help? Check our guide on preparing event logs          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│                                                          [ Cancel ]     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Behavior
- Drag-over: Border turns primary blue, background lightens
- Invalid file type: Error toast "Unsupported format. Please use CSV, XES, XLSX, or Parquet"
- File too large: Error toast "File exceeds 500 MB limit"
- Valid file: Immediately transitions to Step 2

---

## Step 2: Upload Progress

### Wireframe
```
┌─────────────────────────────────────────────────────────────────────────┐
│       Upload Event Log                                         Step 2/5 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                                                                         │
│                              📄                                         │
│                       sales_data.csv                                    │
│                          24.5 MB                                        │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │████████████████████████████░░░░░░░░░░░░░░░░░░░░░░│  68%          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│                     Uploading... 16.7 MB of 24.5 MB                    │
│                                                                         │
│                                                                         │
│                            [ Cancel Upload ]                            │
│                                                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Behavior
- Progress updates every 500ms
- Cancel: Confirmation dialog, then returns to Step 1
- Network error: Retry button with "Resume upload" option
- Complete: Auto-transitions to Step 3

---

## Step 3: Column Mapping

### Wireframe
```
┌─────────────────────────────────────────────────────────────────────────┐
│ ← Back    Map Columns                                          Step 3/5 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  We detected 12 columns. Map them to standard event log fields.         │
│                                                                         │
│  ┌──────────────────────────────┬──────────────────────────────────┐   │
│  │     REQUIRED FIELDS          │      YOUR COLUMNS                │   │
│  ├──────────────────────────────┼──────────────────────────────────┤   │
│  │                              │                                  │   │
│  │  Case ID *                   │  [ order_id        ▼ ] ✓ Auto   │   │
│  │  Unique identifier for       │  Sample: ORD-001, ORD-002        │   │
│  │  each process instance       │                                  │   │
│  │                              │                                  │   │
│  ├──────────────────────────────┼──────────────────────────────────┤   │
│  │                              │                                  │   │
│  │  Activity *                  │  [ activity_name   ▼ ] ✓ Auto   │   │
│  │  The action or step          │  Sample: Submit, Review, Approve │   │
│  │  that occurred               │                                  │   │
│  │                              │                                  │   │
│  ├──────────────────────────────┼──────────────────────────────────┤   │
│  │                              │                                  │   │
│  │  Timestamp *                 │  [ event_timestamp ▼ ] ✓ Auto   │   │
│  │  When the activity           │  Sample: 2024-01-15 14:30:00     │   │
│  │  occurred                    │  Format: [ YYYY-MM-DD HH:mm:ss ▼]│   │
│  │                              │                                  │   │
│  ├──────────────────────────────┼──────────────────────────────────┤   │
│  │     OPTIONAL FIELDS          │                                  │   │
│  ├──────────────────────────────┼──────────────────────────────────┤   │
│  │                              │                                  │   │
│  │  Resource                    │  [ assignee        ▼ ]          │   │
│  │  Who performed the action    │  Sample: John, Mary, System      │   │
│  │                              │                                  │   │
│  ├──────────────────────────────┼──────────────────────────────────┤   │
│  │                              │                                  │   │
│  │  Cost                        │  [ — Not mapped —  ▼ ]          │   │
│  │  Cost of the activity        │                                  │   │
│  │                              │                                  │   │
│  └──────────────────────────────┴──────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  + Add custom attribute mapping                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Preview (first 5 rows)                                          │   │
│  ├───────────┬────────────────┬─────────────────────┬──────────────┤   │
│  │  Case ID  │  Activity      │  Timestamp          │  Resource    │   │
│  ├───────────┼────────────────┼─────────────────────┼──────────────┤   │
│  │  ORD-001  │  Submit        │  2024-01-15 14:30   │  John        │   │
│  │  ORD-001  │  Review        │  2024-01-15 15:45   │  Mary        │   │
│  │  ORD-002  │  Submit        │  2024-01-15 16:00   │  Alice       │   │
│  │  ORD-001  │  Approve       │  2024-01-16 09:00   │  Manager     │   │
│  │  ORD-002  │  Review        │  2024-01-16 10:30   │  Bob         │   │
│  └───────────┴────────────────┴─────────────────────┴──────────────┘   │
│                                                                         │
│  [ Cancel ]                                   [ Confirm & Process → ]   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Behavior
- Auto-detected columns show "✓ Auto" badge
- Dropdown shows column names with sample values
- Timestamp format auto-detected but editable
- Required fields must be mapped before proceeding
- "Confirm & Process" validates and transitions to Step 4

---

## Step 4: Processing

### Wireframe
```
┌─────────────────────────────────────────────────────────────────────────┐
│       Processing Event Log                                     Step 4/5 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                                                                         │
│                              ⏳                                         │
│                                                                         │
│                     Processing your event log...                        │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  ✓ File validated                                               │   │
│  │  ✓ Columns mapped                                               │   │
│  │  ● Extracting events...  (156,320 / ~200,000)                   │   │
│  │  ○ Computing statistics                                         │   │
│  │  ○ Discovering variants                                         │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │████████████████████████████████████████░░░░░░░░░│  78%            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│                    Estimated time remaining: ~15 seconds               │
│                                                                         │
│                                                                         │
│                            [ Cancel ]                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Behavior
- Checklist updates in real-time via WebSocket/polling
- Progress bar shows overall progress
- ETA updates based on processing speed
- Cancel: Confirmation, deletes partial data

---

## Step 5: Complete

### Wireframe
```
┌─────────────────────────────────────────────────────────────────────────┐
│       Upload Complete                                          Step 5/5 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                              ✓                                          │
│                                                                         │
│                     Your event log is ready!                            │
│                                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │          │  │          │  │          │  │          │               │
│  │  12,450  │  │ 156,320  │  │    23    │  │   847    │               │
│  │          │  │          │  │          │  │          │               │
│  │  Cases   │  │  Events  │  │Activities│  │ Variants │               │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘               │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  Date Range:     Jan 1, 2024 — Dec 15, 2024                     │   │
│  │  Avg Duration:   4d 6h 32m                                      │   │
│  │  Resources:      45 unique                                       │   │
│  │  Data Quality:   ██████████░░  87% (3 warnings)                 │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ⚠️  3 data quality warnings detected                           │   │
│  │      • 12 events with missing timestamp                         │   │
│  │      • 5 cases with single event                                │   │
│  │      • 2 duplicate events removed                               │   │
│  │                                                                 │   │
│  │                                        [ View Details ]         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  [ Upload Another ]                            [ Explore Process → ]   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Behavior
- "Explore Process" navigates to Explorer with this log
- "Upload Another" returns to Step 1
- Quality warnings are expandable
- Stats animate in with count-up effect

---

# Flow 2: Process Discovery (P0)

## Overview
Users discover process models from their event logs using various algorithms.

## User Journey
```
Select Log → Choose Algorithm → Configure Parameters → Discover → View Model
```

---

## Step 1: Select Log & Algorithm

### Wireframe
```
┌─────────────────────────────────────────────────────────────────────────┐
│ ← Back    Discover Process Model                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Select Event Log                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  📊 Sales Process                          12,450 cases ✓       │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  📊 Customer Support                        8,320 cases         │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  📊 Order Fulfillment                      45,200 cases         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Choose Discovery Algorithm                                             │
│  ┌──────────────────────────┐  ┌──────────────────────────┐           │
│  │                          │  │                          │           │
│  │  🔄 Inductive Miner      │  │  📈 Heuristics Miner     │           │
│  │                          │  │                          │           │
│  │  Best for structured     │  │  Best for noisy data    │           │
│  │  processes. Guarantees   │  │  with complex behavior. │           │
│  │  sound models.           │  │  Handles exceptions.    │           │
│  │                          │  │                          │           │
│  │  ✓ Recommended           │  │                          │           │
│  └──────────────────────────┘  └──────────────────────────┘           │
│                                                                         │
│  ┌──────────────────────────┐  ┌──────────────────────────┐           │
│  │                          │  │                          │           │
│  │  ⚡ DFG (Fast)           │  │  🎯 Alpha Miner          │           │
│  │                          │  │                          │           │
│  │  Visual directly-follows │  │  Classic algorithm for  │           │
│  │  graph. Quick overview.  │  │  simple processes.      │           │
│  │                          │  │                          │           │
│  └──────────────────────────┘  └──────────────────────────┘           │
│                                                                         │
│  [ Cancel ]                                        [ Configure → ]     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Step 2: Configure & Discover

### Wireframe
```
┌─────────────────────────────────────────────────────────────────────────┐
│ ← Back    Configure Inductive Miner                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Noise Threshold                                                        │
│  Filter out infrequent behavior                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  0% ━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50%    │   │
│  │              20%                                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  Higher values filter more noise but may miss valid paths              │
│                                                                         │
│  Model Output Format                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │
│  │ ● Petri Net │  │ ○ BPMN      │  │ ○ Process   │                     │
│  │             │  │             │  │   Tree      │                     │
│  └─────────────┘  └─────────────┘  └─────────────┘                     │
│                                                                         │
│  ☐ Include frequency statistics                                        │
│  ☐ Include performance metrics (may take longer)                       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Estimated discovery time: ~15 seconds                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  [ Cancel ]                                      [ Discover → ]        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# Flow 3: Conformance Checking (P1)

## Overview
Users check how well their event log conforms to a reference model.

---

## Step 1: Select Model & Log

### Wireframe
```
┌─────────────────────────────────────────────────────────────────────────┐
│ ← Back    Conformance Checking                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Reference Model                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  📐 Sales Process - Inductive Miner                  Selected   │   │
│  │     Created: Dec 10, 2024  |  23 activities  |  Fitness: 0.94  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  [ Change Model ]                                                       │
│                                                                         │
│  Event Log                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  📊 Sales Process - December 2024                    Selected   │   │
│  │     12,450 cases  |  156,320 events  |  847 variants           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  [ Change Log ]                                                         │
│                                                                         │
│  Conformance Method                                                     │
│  ┌──────────────────────────┐  ┌──────────────────────────┐           │
│  │                          │  │                          │           │
│  │  ⚡ Token Replay         │  │  🎯 Alignments           │           │
│  │                          │  │                          │           │
│  │  Fast approximate        │  │  Precise but slower      │           │
│  │  conformance check       │  │  Optimal alignment       │           │
│  │                          │  │                          │           │
│  │  ✓ Recommended           │  │                          │           │
│  └──────────────────────────┘  └──────────────────────────┘           │
│                                                                         │
│  [ Cancel ]                                    [ Check Conformance → ] │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Step 2: Results

### Wireframe
```
┌─────────────────────────────────────────────────────────────────────────┐
│ ← Back    Conformance Results                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │  │
│  │   │         │    │         │    │         │    │         │     │  │
│  │   │  0.94   │    │  0.87   │    │  0.91   │    │ 11,234  │     │  │
│  │   │         │    │         │    │         │    │         │     │  │
│  │   │ Fitness │    │Precision│    │  F1     │    │Conforming│     │  │
│  │   └─────────┘    └─────────┘    └─────────┘    └─────────┘     │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Deviations Summary                                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │   🔴 1,216 cases with deviations (9.8%)                         │  │
│  │                                                                  │  │
│  │   ┌─────────────────────────────────────────────────────────┐   │  │
│  │   │  Missing Activity    ████████████████░░  847 (69.6%)    │   │  │
│  │   │  Unexpected Activity ██████░░░░░░░░░░░░  298 (24.5%)    │   │  │
│  │   │  Wrong Order         ██░░░░░░░░░░░░░░░░   71  (5.8%)    │   │  │
│  │   └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Top Deviations                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Type       │  Activity         │  Expected       │  Cases       │  │
│  ├─────────────┼───────────────────┼─────────────────┼──────────────┤  │
│  │  Missing    │  Quality Check    │  After Review   │  423         │  │
│  │  Unexpected │  Rush Processing  │  —              │  187         │  │
│  │  Missing    │  Final Approval   │  Before Ship    │  156         │  │
│  │  Wrong Order│  Pack → Label     │  Label → Pack   │   71         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  [ Export Report ]                          [ View All Deviations → ] │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# Flow 4: Performance Analytics (P0/P1)

## Overview
Users analyze process performance, identify bottlenecks, and understand timing.

---

## Analytics Dashboard

### Wireframe
```
┌─────────────────────────────────────────────────────────────────────────┐
│ Sales Process - Analytics                                               │
│ Breadcrumb: Home > Explorer > Sales Process > Analytics                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Tabs: [Overview] [Performance] [Throughput] [Conformance] [Resources] │
│                                                                         │
│  ═══════════════════════════════════════════════════════════════════   │
│                                                                         │
│  Key Metrics                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  4d 6h   │  │  2d 3h   │  │  87.3%   │  │    5     │               │
│  │          │  │          │  │          │  │          │               │
│  │ Avg Cycle│  │ Median   │  │ On-Time  │  │Bottleneck│               │
│  │   ↑ 12%  │  │   ↓ 5%   │  │   ↓ 3%   │  │          │               │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘               │
│                                                                         │
│  Bottlenecks                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 🔴 CRITICAL                                                      │  │
│  │ ┌────────────────────────────────────────────────────────────┐  │  │
│  │ │  Manager Approval                                         │  │  │
│  │ │  Avg wait: 18h 32m  |  Affects 67% of cases              │  │  │
│  │ │  ▸ Consider adding parallel approval path                 │  │  │
│  │ └────────────────────────────────────────────────────────────┘  │  │
│  │                                                                  │  │
│  │ 🟡 HIGH                                                          │  │
│  │ ┌────────────────────────────────────────────────────────────┐  │  │
│  │ │  Quality Check                                            │  │  │
│  │ │  Avg wait: 4h 15m  |  Affects 45% of cases               │  │  │
│  │ │  ▸ Bottleneck during peak hours (10am-2pm)                │  │  │
│  │ └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Activity Duration Heatmap                                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Submit    ██  2m                                               │  │
│  │  Review    ████████  45m                                        │  │
│  │  Approve   ████████████████████  2h 15m                         │  │
│  │  Quality   ██████████████  1h 30m                               │  │
│  │  Pack      ████  15m                                            │  │
│  │  Ship      ██  5m                                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# Navigation Architecture

## Sidebar Structure (HUD Navigation)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ┌─────────────────────┐                                               │
│  │  ATLAS              │   ← Logo (64x64)                              │
│  │  Process Mining     │                                               │
│  └─────────────────────┘                                               │
│                                                                         │
│  ─────────────────────────  (Main Navigation)                          │
│                                                                         │
│  📁  Workspace              ← /workspace                               │
│                                 └── /workspace/:projectId              │
│                                                                         │
│  🔍  Explorer               ← /explorer                                │
│                                 └── /explorer/:logId                   │
│                                 └── /explorer/:logId/variants          │
│                                                                         │
│  📊  Analytics              ← /analytics                               │
│                                 └── /analytics/:logId                  │
│                                 └── /analytics/:logId/conformance      │
│                                                                         │
│  ⏱️  KPI Dashboard          ← /kpi                                     │
│                                                                         │
│  ─────────────────────────  (AI & Advanced)                            │
│                                                                         │
│  🤖  AI Assistant           ← /ai                                      │
│                                 └── /ai/insights                       │
│                                 └── /ai/predictions                    │
│                                                                         │
│  📈  Predictions            ← /predictions                             │
│                                 └── /predictions/:modelId              │
│                                                                         │
│  ─────────────────────────  (Footer)                                   │
│                                                                         │
│  ⚙️  Settings               ← /settings                                │
│                                                                         │
│  👤  Naman Agarwal                                                     │
│      naman@company.com                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# Responsive Breakpoints

| Breakpoint | Width | Sidebar | Layout Changes |
|------------|-------|---------|----------------|
| Desktop XL | ≥1440px | 240px | Full experience |
| Desktop | ≥1280px | 240px | Standard layout |
| Laptop | ≥1024px | 64px (collapsed) | Compact sidebar |
| Tablet | ≥768px | Hidden (hamburger) | Stack layout |
| Mobile | <768px | Hidden (hamburger) | Single column |

---

# Error States

## Empty States by Context

| Context | Icon | Title | Description | Action |
|---------|------|-------|-------------|--------|
| No logs | 📁 | No Event Logs | Upload your first event log to start mining | Upload Log |
| No models | 🔄 | No Process Models | Discover a model from your event log | Discover Model |
| No results | 🔍 | No Results | Try adjusting your filters | Clear Filters |
| No deviations | ✓ | Perfect Conformance | All cases conform to the model | — |

## Error States

| Error Type | Display | Actions |
|------------|---------|---------|
| Network | Card with retry | Retry, Go Back |
| 404 | Full page | Go Home, Contact Support |
| 500 | Full page | Retry, Contact Support |
| Validation | Inline | Fix Input |
| Timeout | Card | Retry with simplified query |

---

**Document Version:** 1.0
**Last Updated:** December 2024
**Maintainer:** Fictive Kin Design Studio
