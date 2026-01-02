# QA TASK: Test Discovery Flow Step-by-Step

## Prerequisites

⚠️ **Required:** Ingestion flow must have succeeded. You need an uploaded event log to test Discovery.

If Ingestion is blocked, report that immediately and skip this test.

---

## Your Mission

Test EVERY step of the Discovery flow. Start from an uploaded log and verify the process mining graph renders and is interactive.

---

## Test Environment

- **Frontend URL:** http://localhost:4200
- **Starting Point:** A project with at least one uploaded event log
- **Expected Output:** Interactive process graph (DFG or Petri net)

---

## Step-by-Step Test Protocol

| Step | Action                                | Expected Result                                | Actual Result | Pass/Fail | Evidence/Notes |
| ---- | ------------------------------------- | ---------------------------------------------- | ------------- | --------- | -------------- |
| 1    | Navigate to project with uploaded log | See log in list                                |               |           |                |
| 2    | Click on the log name/row             | See log detail view or selection state         |               |           |                |
| 3    | Find "Explore" or "Discover" button   | Button visible and clickable                   |               |           |                |
| 4    | Click Explore/Discover                | Navigate to Process Explorer                   |               |           |                |
| 5    | See loading indicator                 | Spinner or "Loading..." shown                  |               |           |                |
| 6    | Wait for graph to render              | Graph appears (nodes and edges visible)        |               |           |                |
| 7    | Count nodes                           | Multiple activity nodes visible                |               |           |                |
| 8    | Count edges                           | Edges connecting nodes visible                 |               |           |                |
| 9    | Hover over a node                     | Tooltip or highlight effect                    |               |           |                |
| 10   | Click on a node                       | Node selected, details panel shows             |               |           |                |
| 11   | Check node details                    | Activity name, frequency, duration shown       |               |           |                |
| 12   | Click on an edge                      | Edge selected, details panel shows             |               |           |                |
| 13   | Check edge details                    | Transition frequency shown                     |               |           |                |
| 14   | Try zoom controls                     | Can zoom in/out                                |               |           |                |
| 15   | Try pan (drag canvas)                 | Canvas moves                                   |               |           |                |
| 16   | Look for Variants tab/panel           | Variants section visible                       |               |           |                |
| 17   | Click Variants                        | See list of variants with frequencies          |               |           |                |
| 18   | Look for algorithm selector           | Dropdown or tabs for Alpha/Heuristic/Inductive |               |           |                |
| 19   | Switch algorithm (if available)       | Graph re-renders with different structure      |               |           |                |
| 20   | Look for filter controls              | Filter by time, activity, etc.                 |               |           |                |

---

## Bug Report Format

| Bug ID  | Step # | Expected | Actual | Severity | Console Error? | Network Error? |
| ------- | ------ | -------- | ------ | -------- | -------------- | -------------- |
| DIS-001 |        |          |        |          |                |                |
| DIS-002 |        |          |        |          |                |                |

**Severity Guide:**

- **P0** - Flow completely blocked, cannot see graph at all
- **P1** - Graph shows but major interaction broken
- **P2** - Minor feature missing, graph usable
- **P3** - Cosmetic, visual polish

---

## Summary Output

### Pass Rate

- Steps Passing: \_\_/20
- Percentage: \_\_%

### Blocking Issues (P0)

1.
2.

### Critical Bugs Found

| Bug ID | Summary | Severity |
| ------ | ------- | -------- |
|        |         |          |

### Can User See Process Graph?

- [ ] YES - graph renders and is interactive
- [ ] PARTIAL - graph renders but limited interaction
- [ ] NO - blocked, no graph visible

### Graph Quality Assessment

- [ ] Nodes clearly labeled with activity names
- [ ] Edges visible and connected
- [ ] Layout is readable (not overlapping mess)
- [ ] Can identify start/end activities
- [ ] Frequency annotations visible

### Missing Features Observed

- [ ] No algorithm selector
- [ ] No export functionality
- [ ] No filtering
- [ ] No variant view
- [ ] No performance overlay
- (Add any others)

---

## Report To

**Deliver to:** CPO
**Update:** `/docs/cpo/CPO_KNOWLEDGE_BASE.md` → Discovery Flow Test Results section
