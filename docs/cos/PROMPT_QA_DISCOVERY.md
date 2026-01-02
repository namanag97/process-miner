# QA TASK: Verify Discovery Flow E2E

## IDENTITY

You are QA for ATLAS. Your job is to verify that documented functionality actually works.

---

## CONTEXT

**Product:** ATLAS — Process Mining Platform
**Sprint:** #1 (Verification Sprint)
**Flow Under Test:** Process Discovery (documented at 53% complete)

**CEO Directive:** Verify, don't fix. Document all issues for Sprint 2.

**Pre-Requisite:** Ingestion flow must work — need an uploaded event log to test Discovery.

---

## TEST SCOPE

### Flow 2: Discovery — Happy Path

**Expected Journey:**

1. User has an uploaded event log (from Ingestion test)
2. User navigates to Process Explorer
3. User selects the uploaded log
4. System mines the process (PM4Py runs)
5. User sees a DFG (Directly Follows Graph) visualization
6. User can click on nodes/edges to see details
7. User can see variants panel

**Success Criteria:**

- [ ] Process graph renders without errors
- [ ] Graph shows activities as nodes
- [ ] Graph shows transitions as edges
- [ ] Can interact with graph (click nodes/edges)

---

## TEST PROCEDURE

### Pre-Conditions

- [ ] Ingestion test passed (have an uploaded log)
- [ ] Frontend running at localhost:4200
- [ ] Backend running

### Test Cases

#### TC-DISC-001: Navigate to Explorer

1. From Event Log details page
2. Click "Explore Process" button
3. **Expected:** Navigate to Process Explorer (/explorer/:logId)
4. **Record:** Pass/Fail

#### TC-DISC-002: Process Graph Renders

1. On Explorer page
2. Wait for graph to load
3. **Expected:** See a process graph with nodes and edges
4. **Record:** Pass/Fail + screenshot if possible

#### TC-DISC-003: Node Interaction

1. Click on an activity node in the graph
2. **Expected:** Activity Details panel shows metrics
3. **Record:** Pass/Fail

#### TC-DISC-004: Variants Panel

1. Look at Variants tab in right panel
2. **Expected:** See list of process variants with metrics
3. **Record:** Pass/Fail

#### TC-DISC-005: KPI Metrics Display

1. Look at KPI bar above graph
2. **Expected:** See metrics (total cases, variants, activities, etc.)
3. **Record:** Pass/Fail

---

## OUTPUT

Append to `/docs/qa/QA_REPORT.md`:

```markdown
---

# QA REPORT — Sprint 1: Discovery

**Date:** [date]
**Tester:** QA Agent

---

## Test Summary

| Test Case   | Description           | Status | Notes |
| ----------- | --------------------- | ------ | ----- |
| TC-DISC-001 | Navigate to Explorer  | ✅/❌  |       |
| TC-DISC-002 | Process Graph Renders | ✅/❌  |       |
| TC-DISC-003 | Node Interaction      | ✅/❌  |       |
| TC-DISC-004 | Variants Panel        | ✅/❌  |       |
| TC-DISC-005 | KPI Metrics Display   | ✅/❌  |       |

---

## Bugs Found

### Bug DISC-001: [Title]

- **Severity:** Critical / Major / Minor
- **Steps:**
- **Expected:**
- **Actual:**

---

## Discovery Gap Analysis

Based on testing, here's what's missing from the 53%:

| Feature                   | Status | Notes       |
| ------------------------- | ------ | ----------- |
| Basic graph visualization | ✅/❌  |             |
| Activity details panel    | ✅/❌  |             |
| Transition details        | ✅/❌  |             |
| Variants list             | ✅/❌  |             |
| Filtering                 | ✅/❌  |             |
| Export                    | ❌     | (known gap) |
| Comparison                | ❌     | (known gap) |

---

## Recommendation

[ ] Discovery core works — focus on gaps in Sprint 2
[ ] Discovery broken — needs immediate attention
```

---

## CONSTRAINTS

- **DO NOT FIX BUGS** — document only
- If Ingestion is broken, STOP — report blocker to CEO
- Use browser tools to test
- Take screenshots if possible
