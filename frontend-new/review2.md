Process Mining Platform UAT Review
Reviewer: Expert Product Manager & UI/UX Designer with Process Mining Domain Expertise
Date: 2025-12-30
Version: Frontend-New (18 pages, 100% mock data)

Executive Summary
The Process Mining Platform demonstrates solid foundational architecture with proper design system integration, comprehensive logging, and well-structured routing. However, as a pre-production mock, it lacks the depth of process mining domain features that would distinguish it as a professional tool. The visual design is enterprise-grade, but the UX flows miss opportunities to leverage van der Aalst's process mining principles for actionable insights.

Overall Assessment: Ready for UI structure validation, but requires significant feature enrichment before real-world deployment.

Score Card
Dimension Score (1-10) Notes
Business Value 6/10 Core workflows present, but insights lack actionability
UX Quality 7/10 Clean flows, but process mining-specific interactions missing
UI Polish 8/10 Consistent Ant Design usage, good visual hierarchy
PM Domain Accuracy 5/10 Surface-level PM concepts; lacks depth
Accessibility 6/10 Basic ARIA via Ant Design, no explicit focus management
Information Architecture 8/10 Logical groupings, clear navigation
Critical Issues (P0-P1)
[P1] Process Map Lacks Academic Rigor
Category: PM Domain | Location:
ProcessCanvas.tsx
,
ProcessExplorerPage.tsx

Current Behavior: The DFG displays nodes and edges with frequency counts, but lacks essential process mining elements.

Problem: Per Wil van der Aalst's principles, a proper DFG should show:

Toggle between Frequency View and Performance View (time-based)
Edge width proportional to frequency, edge color to avg duration
Visual distinction for rework loops (self-loops, back-edges)
Start/End activity markers are heuristic-based (includes('start')) rather than data-driven
Steve Jobs Test: ❌ Would not ship. The map shows structure but doesn't tell a story. Where are the bottlenecks? Where is time being wasted?

van der Aalst Alignment: ❌ "The goal is not to have a beautiful process map, but to understand the process and improve it."

Recommendation:

// Add view toggle
type ViewMode = 'frequency' | 'performance';
const [viewMode, setViewMode] = useState<ViewMode>('frequency');
// Color edges based on mode
const getEdgeColor = (edge: DFGEdge, mode: ViewMode) => {
if (mode === 'performance') {
const avgTime = edge.performance || 0;
return avgTime > threshold ? tokens.colors.error[500] : tokens.colors.success[500];
}
return tokens.colors.neutral[400];
};
Add a toggle in the toolbar for frequency/performance view.

Priority: P1 (Critical)

[P1] Conformance Deviations Not Traceable
Category: PM Domain | Location:
ConformanceTab.tsx

Current Behavior: Shows deviation table with case IDs but clicking them does nothing.

Problem: Users can't trace from deviation → case → events → timeline. This breaks the fundamental "drill-down" capability that makes conformance checking actionable.

van der Aalst Alignment: ❌ Violations should lead to root cause investigation, not dead ends.

Recommendation:

// Make case IDs clickable
render: (caseId: string) => (
<Button type="link" onClick={() => navigate(`/logs/${logId}/cases/${caseId}`)}>
<Text code>{caseId}</Text>
</Button>
)
Priority: P1 (Critical)

[P1] Variant Explorer Hides the "So What?"
Category: Business Value | Location:
VariantPanel.tsx

Current Behavior: Shows variants with frequency % and avg duration, but no comparative insight.

Problem: Missing:

Variant comparison (how does V2 differ from Happy Path?)
Cost/time impact of each variant
Deviation count per variant
Visual diff when selecting a variant on the map
Steve Jobs Test: ❌ "Why should I care about Variant 2?" — this question goes unanswered.

Recommendation: Add a "Compare to Happy Path" feature:

// Add comparison metrics
interface VariantComparison {
deltaDuration: number; // vs happy path
additionalSteps: string[];
missingSteps: string[];
reworkRate: number;
}
Priority: P1 (Critical)

Major Issues (P2)
[P2] Upload Wizard Missing Event Log Quality Indicators
Category: PM Domain | Location:
UploadWizardPage.tsx

Current Behavior: Shows row count and estimated case count during validation.

Problem: Process mining experts need to assess log quality before analysis:

Timestamp format consistency
Missing values count
Unique activities vs expected
Case completeness (% with start/end)
Potential noise indicators
van der Aalst Alignment: "Event logs are the starting point; garbage in, garbage out."

Recommendation: Add a "Log Quality Score" card in Step 2:

const logQualityMetrics = {
completeness: 94.5, // % cases with start+end
timestampValidity: 99.8, // % valid timestamps
missingValues: 0.2, // % cells with nulls
uniqueActivities: 12,
potentialNoise: ['Manual Override', 'System Error'] // low-freq activities
};
Priority: P2 (Major)

[P2] AI Insights Lack Actionable CTAs
Category: Business Value | Location:
AIInsightsPage.tsx

Current Behavior: Shows insights with recommendations as plain text.

Problem: Recommendations like "Consider adding parallel approval paths" are vague. Enterprise users need:

Take Action button that links to relevant page
Impact estimation (ROI if fixed)
Affected cases count with drilldown
Root cause drill-through
Steve Jobs Test: ❌ Insights without action buttons are just FYI emails. Useless.

Recommendation:

// Add action buttons to InsightCard
<Space>
<Button type="primary" onClick={() => navigate(`/explorer/${logId}?highlight=approval`)}>
Analyze Bottleneck
</Button>
<Button onClick={() => navigate(`/logs/${logId}/cases?filter=delayed`)}>
View Affected Cases (125)
</Button>
</Space>
Priority: P2 (Major)

[P2] No Comparison/Benchmarking Context for Metrics
Category: Data Presentation | Location:
AnalyticsPage.tsx
, MetricCard usage

Current Behavior: Shows "Avg Cycle Time: 4.2 days" without context.

Problem: Is 4.2 days good or bad? Users need:

Trend indicator (↑12% vs last month)
Benchmark comparison (industry avg: 3.5 days)
Historical sparkline
Recommendation: Enhance MetricCard with comparative data:

<MetricCard
title="Avg Cycle Time"
value="4.2 days"
trend={{ value: 12, isPositive: false, label: 'vs last month' }}
benchmark={{ value: '3.5 days', label: 'industry avg' }}
sparkline={[3.8, 4.0, 4.1, 4.2, 4.2, 4.2]}
/>
Priority: P2 (Major)

[P2] Event Log List Missing Key PM Metadata
Category: PM Domain | Location:
EventLogsPage.tsx

Current Behavior: Shows: Name, Cases, Events, Uploaded date.

Problem: Missing critical PM context:

Date range of events in log
Unique activities count
Avg case duration
Last analysis date
Recommendation: Add columns (optionally toggleable):

{ title: 'Date Range', dataIndex: 'dateRange', render: (range) => `${range.start} - ${range.end}` },
{ title: 'Activities', dataIndex: 'uniqueActivities', width: 100 },
{ title: 'Avg Duration', dataIndex: 'avgDuration' },
Priority: P2 (Major)

[P2] Rework Loops Not Visible on Process Map
Category: PM Domain | Location:
ProcessCanvas.tsx

Current Behavior: Edges are styled uniformly regardless of whether they represent rework.

Problem: Rework (back-edges) is where most process inefficiency hides. Should be:

Visually distinct (dashed line, different color)
Labeled with rework rate %
Clickable to see cases with that rework pattern
van der Aalst Alignment: "Rework loops are the signature of process inefficiency."

Recommendation:

// In createEdges function
const isBackEdge = layerMap.get(edge.source) > layerMap.get(edge.target);
return {
...baseEdge,
style: {
...baseStyle,
strokeDasharray: isBackEdge ? '5,5' : undefined,
stroke: isBackEdge ? tokens.colors.warning[500] : tokens.colors.neutral[400],
},
label: isBackEdge ? `↺ ${edge.frequency}` : edge.frequency,
};
Priority: P2 (Major)

[P2] Filter Context Lost When Filtering
Category: UX | Location:
ProcessExplorerPage.tsx

Current Behavior: When filters are applied, original state is lost.

Problem: Users can't:

See what % of the total the filtered view represents
Compare filtered vs unfiltered
Save filter presets for common analyses
Recommendation: Add a filter summary bar:

<Alert
type="info"
message={`Showing ${filteredCases} of ${totalCases} cases (${percentage}%)`}
action={<Button type="link" onClick={clearFilters}>Clear</Button>}
/>
Priority: P2 (Major)

Minor Issues (P3-P4)
[P3] Relative Time Formatting Uninformative After 30 Days
Location:
EventLogsPage.tsx

- formatRelativeTime

Problem: "366 days ago" is meaningless. After 7 days, switch to absolute date.

Fix:

if (diffDays > 7) {
return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}
[P3] Empty Header in Layout
Location:
AppShell.tsx
line 306-320

Problem: The <Header> component is rendered but empty, wasting 56px of vertical space.

Recommendation: Either populate with breadcrumbs/search or remove entirely.

[P3] Natural Language Query Shows Toast But Should Show Loading
Location:
AIInsightsPage.tsx

- handleNLQuery

Problem: When user submits a query, the field clears but there's no indication processing is happening (even as a preview).

Fix: Show a mock "Analyzing..." state with animated skeleton.

[P4] Missing Keyboard Shortcuts
Location: Global

Problem: Enterprise power users expect keyboard shortcuts:

Cmd+K for global search
Cmd+U for upload
Arrow keys for variant navigation
Recommendation: Add useHotkeys hook integration.

[P4] No Global Search
Location: App-wide

Problem: No way to search across logs, cases, activities, insights from one place.

Recommendation: Add Command Palette (Cmd+K spotlight search).

Process Mining Domain Gaps
Missing: Case-Level Exploration
Currently, users can see aggregated stats but cannot:

View a single case's event timeline
Compare two cases side-by-side
See where a specific case deviated from the norm
Recommendation: Add /logs/:logId/cases/:caseId page with:

Event timeline (vertical Gantt)
Variant this case follows
Deviations flagged inline
Missing: Activity Timeline Accuracy
The mock data has timestamps but no component visualizes the temporal sequence of events within a case with accurate time scaling.

Recommendation: Add Timeline view using vis-timeline or custom SVG Gantt.

Missing: Bottleneck Quantification
Bottlenecks should show:

Queue time (waiting)
Service time (processing)
Total impact on cycle time
Cases affected
Currently, insights say "bottleneck detected" but don't quantify impact in hours/days.

Missing: Export to Standard Formats
Process mining professionals expect:

Export to BPMN 2.0 for modeling tools
Export to XES for academic analysis
Export to CSV for spreadsheet analysis
Export process map as SVG/PNG/PDF
Recommendations (Prioritized)
Immediate (Before Demo/Beta)
Add frequency/performance toggle to ProcessCanvas
Make conformance violations drillable to case/event level
Add action buttons to AI insights
Show filter context when filtering
Short-Term (Next Sprint)
Add log quality score to upload wizard
Visualize rework loops distinctly on process map
Add comparison context to all metrics
Add case timeline view for single-case investigation
Medium-Term (Before GA)
Implement case explorer page
Add bottleneck quantification (time impact)
Add export to BPMN/XES/SVG/PDF
Add global search (Cmd+K)
Praise: What's Working Well ✅
Feature Why It Works
Design Token Consistency tokens.colors._, tokens.spacing._ used throughout — easy to theme
Comprehensive Logging createLogger() on every page enables debugging
Route Protection ProtectedRoute wrapper properly guards auth
Empty States EmptyState component with CTAs on all list pages
Breadcrumbs Present on key pages (Upload, Log Detail, Explorer)
Column Mapping Auto-Suggest Smart defaults in
UploadWizardPage
Variant Visual Selection Selecting a variant highlights path on the map
Collapsible Sidebar Proper collapse with icon-only mode
Conformance Gauges Fitness/Precision/Generalization/Simplicity — academically correct metrics
Summary
The Process Mining Platform has excellent foundational UI but needs deeper process mining domain integration to deliver genuine value to professionals. The distance between "showing data" and "enabling action" is where the work remains.

"Process mining should lead to action, not just visualization." — Wil van der Aalst

The recommendations above prioritize closing the action gap — ensuring every insight, every visualization, and every interaction moves users closer to process improvement.

Review conducted by Expert UAT Agent applying Steve Jobs craft standards and Wil van der Aalst process mining principles.
