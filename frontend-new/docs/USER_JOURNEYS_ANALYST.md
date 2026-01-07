# Process Analyst User Journeys

## Persona: Process Analyst / Business Analyst

**Goal:** Discover, analyze, and improve business processes using event log data.

**Key Jobs to Be Done:**
- Upload and prepare data for analysis
- Discover how processes actually run
- Find bottlenecks and inefficiencies
- Ensure compliance with expected process flows
- Communicate findings to stakeholders

---

## Journey 1: First-Time Data Upload & Process Discovery

**Trigger:** Analyst has event log data and wants to see the process.

```
[Entry Point]
    --> Login / Sign Up
    --> Select Workspace
    --> Create New Project (name, description)

[Data Upload]
    --> Click "Upload Dataset"
    --> Drag & drop CSV/XES file (or browse)
    --> Wait for upload progress bar
    --> System detects columns automatically

[Column Mapping]
    --> Review detected columns
    --> Map required fields:
        --> Case ID (which column identifies a case?)
        --> Activity (which column is the activity name?)
        --> Timestamp (which column is the event time?)
    --> Map optional fields:
        --> Resource (who performed it?)
        --> Cost (how much did it cost?)
        --> Additional attributes
    --> Click "Validate Mapping"

[Data Validation]
    --> System runs quality checks
    --> Review validation report:
        --> Total cases / events
        --> Date range
        --> Missing values
        --> Duplicate events
    --> Fix issues or proceed
    --> Click "Start Ingestion"

[Process Discovery]
    --> Wait for ingestion to complete
    --> Click "Discover Process"
    --> Select algorithm (default: Auto)
    --> Wait for discovery to complete

[Explore Process Map]
    --> View generated DFG/BPMN
    --> Zoom / Pan / Fit to screen
    --> Hover on nodes --> See activity stats
    --> Hover on edges --> See transition stats
    --> Click variant list --> Highlight path
    --> Adjust complexity slider

[Save & Share]
    --> Save view as bookmark
    --> Copy shareable link
    --> Export as PNG/SVG
```

**Success Metrics:**
- Time to first process map < 5 minutes
- Zero mapping errors on common formats
- User completes flow without help docs

---

## Journey 2: Bottleneck Investigation

**Trigger:** Process is slow; analyst needs to find where and why.

```
[Entry Point]
    --> Open existing project
    --> Navigate to process map

[Switch to Performance View]
    --> Click "Performance" toggle
    --> Map updates with time-based heatmap:
        --> Red = slow transitions
        --> Green = fast transitions
    --> Legend shows time scale

[Identify Bottleneck]
    --> Visually spot red areas
    --> Click on slow transition/activity
    --> Side panel opens with details:
        --> Avg duration
        --> Median duration
        --> Min / Max
        --> Case count

[Drill Down]
    --> Click "View Affected Cases"
    --> See list of cases with this bottleneck
    --> Filter by:
        --> Time period
        --> Resource
        --> Region / Business Unit
        --> Case attributes
    --> Sort by duration (worst first)

[Root Cause Analysis]
    --> Click "Analyze Root Cause"
    --> System shows correlated factors:
        --> "Cases with Resource=John are 3x slower"
        --> "Cases on Mondays have 2x wait time"
        --> "Cases with Amount > $10K take longer"
    --> View statistical significance

[Document Findings]
    --> Add annotation on process map
    --> Write comment explaining issue
    --> Assign action item to process owner
    --> Export PDF report

[Set Up Monitoring]
    --> Create alert: "Notify if avg time > threshold"
    --> Configure recipients
    --> Save and activate
```

**Success Metrics:**
- Bottleneck identified in < 3 clicks
- Root cause suggestions are actionable
- Alert setup < 1 minute

---

## Journey 3: Variant Analysis

**Trigger:** Analyst wants to understand process variations.

```
[Entry Point]
    --> Open project
    --> Navigate to "Variants" tab

[View Variant List]
    --> See all unique process paths
    --> Default sort: by frequency (most common first)
    --> Each row shows:
        --> Variant ID
        --> Activity sequence preview
        --> Case count
        --> % of total
        --> Avg duration

[Sort & Filter Variants]
    --> Sort by:
        --> Frequency
        --> Duration (slowest first)
        --> Cost (most expensive first)
    --> Filter by:
        --> Contains activity X
        --> Excludes activity Y
        --> Duration > threshold

[Inspect Single Variant]
    --> Click variant row
    --> Process map highlights this path
    --> See variant-specific stats:
        --> Avg cycle time
        --> Avg cost
        --> Conformance score
    --> View sample cases

[Compare Variants]
    --> Select "Happy Path" (most common)
    --> Ctrl+Click second variant
    --> Click "Compare"
    --> Side-by-side view:
        --> Left: Happy Path
        --> Right: Selected variant
    --> Differences highlighted:
        --> Extra activities (red)
        --> Missing activities (gray)
        --> Different order (yellow)

[Analyze Deviation]
    --> Click on deviation
    --> See:
        --> How many cases affected
        --> Impact on duration
        --> Impact on cost
    --> Drill into specific cases

[Take Action]
    --> Tag variant as "Needs Review"
    --> Create alert for this variant
    --> Export comparison report
    --> Share with stakeholders
```

**Success Metrics:**
- Compare any two variants in 2 clicks
- Deviation impact quantified automatically
- Variant alerts prevent future issues

---

## Journey 4: Custom Dashboard Creation

**Trigger:** Analyst needs to monitor KPIs and share with team.

```
[Entry Point]
    --> Navigate to "Dashboards"
    --> Click "Create New Dashboard"
    --> Enter name and description

[Add Widgets]
    --> Click "Add Widget"
    --> Select widget type:
        --> KPI Card
        --> Process Map (mini)
        --> Line Chart
        --> Bar Chart
        --> Table
        --> Pie Chart

[Configure KPI Card]
    --> Select metric:
        --> Cycle Time (Avg/Median/P95)
        --> Throughput (cases/day)
        --> Cost (total/avg)
        --> Rework Rate
        --> Conformance Score
    --> Set comparison:
        --> vs Previous Period
        --> vs Target
    --> Choose color thresholds

[Configure Chart]
    --> Select X-axis (time, activity, resource)
    --> Select Y-axis (metric)
    --> Set aggregation (sum, avg, count)
    --> Apply grouping (by variant, region, etc.)
    --> Set date range

[Add Process Map Widget]
    --> Select dataset
    --> Choose view type (DFG, BPMN)
    --> Set default filters
    --> Enable/disable interactions

[Add Filters]
    --> Add global filter controls:
        --> Date Range Picker
        --> Activity Multi-select
        --> Resource Dropdown
    --> Link filters to widgets

[Layout & Design]
    --> Drag widgets to arrange
    --> Resize widgets
    --> Set refresh interval (5min, 15min, 1hr)

[Save & Share]
    --> Click "Save"
    --> Set as project default (optional)
    --> Share with:
        --> Specific users
        --> Entire workspace
        --> Public link (view-only)
    --> Schedule email delivery:
        --> Recipients
        --> Frequency (daily, weekly)
        --> Time
```

**Success Metrics:**
- Dashboard created in < 10 minutes
- Widgets load in < 2 seconds
- Scheduled reports delivered on time

---

## Journey 5: Conformance Checking

**Trigger:** Analyst needs to verify process follows expected flow.

```
[Entry Point]
    --> Open project
    --> Navigate to "Conformance" tab

[Define Reference Model]
    --> Option A: Upload BPMN file
        --> Click "Upload Reference"
        --> Select .bpmn file
        --> Preview model
    --> Option B: Create from scratch
        --> Click "Create Reference"
        --> Use BPMN editor
        --> Add activities, gateways, flows
        --> Save model
    --> Option C: Use discovered model
        --> Click "Use Current Model"
        --> Optionally simplify

[Run Conformance Check]
    --> Select algorithm:
        --> Token Replay (fast, approximate)
        --> Alignments (slow, precise)
    --> Click "Run Check"
    --> Wait for analysis

[Review Results]
    --> View overall scores:
        --> Fitness (0-100%)
        --> Precision (0-100%)
        --> Generalization (0-100%)
    --> View deviation summary:
        --> Missing activities
        --> Extra activities
        --> Wrong order
        --> Skipped activities

[Explore Deviations]
    --> Click deviation type
    --> See affected cases
    --> Process map highlights:
        --> Green = conforming
        --> Red = deviating
    --> Click specific deviation
    --> See case details

[Filter by Conformance]
    --> Toggle "Show only deviations"
    --> Filter by deviation type
    --> Filter by severity
    --> Export non-conforming cases

[Create Compliance Report]
    --> Click "Generate Report"
    --> Select sections to include
    --> Add executive summary
    --> Export as PDF
    --> Schedule recurring report
```

**Success Metrics:**
- Conformance score calculated in < 30 seconds
- Deviations clearly explained
- Audit-ready reports in 1 click

---

## Journey 6: Time-Based Process Comparison

**Trigger:** Analyst wants to measure improvement over time.

```
[Entry Point]
    --> Open project
    --> Click "Compare" mode

[Define Comparison Periods]
    --> Set Period A:
        --> Start date
        --> End date
        --> Label (e.g., "Q1 2024")
    --> Set Period B:
        --> Start date
        --> End date
        --> Label (e.g., "Q1 2025")
    --> Click "Compare"

[View Side-by-Side Maps]
    --> Left panel: Period A process map
    --> Right panel: Period B process map
    --> Maps are synchronized (zoom, pan)
    --> Color coding:
        --> Blue = unchanged
        --> Green = improved
        --> Red = degraded
        --> Yellow = new path

[Review Metrics Delta]
    --> Summary card shows:
        --> Cycle Time: -15% (improved)
        --> Throughput: +20% (improved)
        --> Variants: +5 new
        --> Conformance: +8%
    --> Click metric for drill-down

[Analyze Changes]
    --> Tab: "New Paths"
        --> Paths that appear only in Period B
        --> Impact assessment
    --> Tab: "Removed Paths"
        --> Paths that disappeared
        --> Were they problematic?
    --> Tab: "Changed Performance"
        --> Activities that got faster/slower
        --> Transitions that changed

[Attribute Analysis]
    --> Break down by dimension:
        --> By Region
        --> By Product
        --> By Customer Segment
    --> Identify which segments improved/degraded

[Document & Share]
    --> Add annotations
    --> Generate comparison report
    --> Export as presentation
    --> Share with stakeholders
```

**Success Metrics:**
- Comparison generated in < 1 minute
- Changes clearly highlighted
- Quantified improvement metrics

---

## Journey 7: Process Filtering & Segmentation

**Trigger:** Analyst wants to analyze a specific subset of cases.

```
[Entry Point]
    --> Open project with process map
    --> Click "Filters" panel

[Add Filters]
    --> Time filters:
        --> Date range (start - end)
        --> Day of week
        --> Time of day
    --> Case attribute filters:
        --> Customer type = "Enterprise"
        --> Region in ["US", "EU"]
        --> Amount > 10000
    --> Activity filters:
        --> Contains activity "Manual Review"
        --> Excludes activity "Auto-Approved"
        --> Starts with "Submit"
        --> Ends with "Complete"
    --> Performance filters:
        --> Duration > 7 days
        --> Cost > $500
        --> Has rework = true

[Apply & Preview]
    --> Click "Apply Filters"
    --> See filter summary:
        --> "Showing 1,234 of 10,000 cases (12.3%)"
    --> Process map updates
    --> All metrics recalculate

[Save Filter Preset]
    --> Click "Save as Preset"
    --> Name: "High-Value Enterprise Cases"
    --> Optionally share with team

[Compare Segments]
    --> Create Segment A (filter set 1)
    --> Create Segment B (filter set 2)
    --> Click "Compare Segments"
    --> Side-by-side analysis
```

**Success Metrics:**
- Filters apply in < 2 seconds
- Complex filter combinations supported
- Saved presets sync across team

---

## Journey 8: Case-Level Investigation

**Trigger:** Analyst needs to understand what happened in specific cases.

```
[Entry Point]
    --> From any view, click case ID
    --> Or navigate to "Cases" tab
    --> Search by case ID

[View Case Timeline]
    --> Horizontal timeline:
        --> Each activity as a node
        --> Time gaps visualized
        --> Duration of each activity
    --> Vertical event list:
        --> Timestamp
        --> Activity
        --> Resource
        --> Additional attributes

[Analyze Case]
    --> See case summary:
        --> Total duration
        --> Number of events
        --> Variant ID
        --> Conformance status
    --> Highlight anomalies:
        --> Unusually long waits
        --> Rework loops
        --> Skipped steps

[Compare to Average]
    --> Toggle "Show Average"
    --> Overlay typical case timeline
    --> See where this case deviates

[View Related Cases]
    --> "Similar Cases" tab
    --> Cases with same variant
    --> Cases with same attributes
    --> Cases with same outcome

[Take Action]
    --> Add note to case
    --> Flag for review
    --> Export case details
    --> Link to external ticket (Jira, ServiceNow)
```

**Success Metrics:**
- Case loads in < 1 second
- Full audit trail visible
- Easy navigation between cases

---

## Journey 9: Export & Reporting

**Trigger:** Analyst needs to share findings with stakeholders.

```
[Export Process Map]
    --> Click "Export" button
    --> Select format:
        --> PNG (image)
        --> SVG (vector)
        --> BPMN (editable model)
        --> PDF (with stats)
    --> Configure options:
        --> Include legend
        --> Include statistics
        --> High resolution
    --> Download file

[Export Data]
    --> Navigate to "Export Data"
    --> Select export type:
        --> Full event log (CSV/Parquet)
        --> Filtered cases only
        --> Aggregated statistics
        --> Variant summary
    --> Apply current filters (optional)
    --> Download or send to S3/GCS

[Generate Report]
    --> Click "Create Report"
    --> Select template:
        --> Executive Summary
        --> Detailed Analysis
        --> Compliance Report
        --> Custom
    --> Select sections:
        --> Process overview
        --> KPI summary
        --> Bottleneck analysis
        --> Variant analysis
        --> Recommendations
    --> Add custom text/annotations
    --> Preview report
    --> Export as PDF/PPTX

[Schedule Report]
    --> Click "Schedule"
    --> Set frequency (daily, weekly, monthly)
    --> Set recipients (email)
    --> Set delivery time
    --> Activate schedule
```

**Success Metrics:**
- Export completes in < 30 seconds
- Reports are presentation-ready
- Scheduled reports never fail

---

## Summary: Analyst Journey Map

```
                                    PROCESS ANALYST JOURNEY

 ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
 │  UPLOAD │-->│ DISCOVER│-->│ ANALYZE │-->│ COMPARE │-->│ MONITOR │-->│ REPORT  │
 │  DATA   │   │ PROCESS │   │ ISSUES  │   │ IMPROVE │   │ ONGOING │   │ SHARE   │
 └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
      │             │             │             │             │             │
      v             v             v             v             v             v
  - Upload      - Auto       - Bottleneck  - Before/    - Alerts     - PDF/PNG
  - Map cols    - Discovery    analysis      After      - Dashboards - Scheduled
  - Validate    - Variants   - Root cause  - Segments   - KPIs         reports
  - Ingest      - Explore    - Conformance - Simulate   - Anomalies  - Share link
```

---

## Emotional Journey

```
Stage       | Upload | Discover | Analyze | Report |
------------|--------|----------|---------|--------|
Emotion     |   😰   |    😮    |   🤔    |   😊   |
            | Anxious| Surprised| Focused | Satisfied
Pain Points | Format | Too      | Finding | Making it
            | errors | complex  | root    | look good
            |        |          | cause   |
Opportunity | Auto-  | Smart    | AI      | 1-click
            | detect | defaults | insights| templates
```

---

## Edge Cases & Error Handling

| Scenario | System Response |
|----------|-----------------|
| Invalid file format | Show supported formats, offer conversion |
| Missing required columns | Highlight missing, suggest mappings |
| Duplicate timestamps | Warn user, offer auto-resolution |
| Empty dataset after filtering | Show message, suggest relaxing filters |
| Discovery timeout | Show partial results, offer to continue |
| Export too large | Offer pagination or async download |
| Session timeout during analysis | Auto-save state, resume on login |
