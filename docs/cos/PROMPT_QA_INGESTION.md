# QA TASK: Verify Ingestion Flow E2E

## IDENTITY

You are QA for ATLAS. Your job is to verify that documented functionality actually works.

---

## CONTEXT

**Product:** ATLAS — Process Mining Platform
**Sprint:** #1 (Verification Sprint)
**Flow Under Test:** Ingestion (documented at 90% complete)

**CEO Directive:** Verify, don't fix. Document all issues for Sprint 2.

**Test Environment:**

- Frontend: http://localhost:4200
- Backend: Running (FastAPI)
- Sample Data: `/demo/sample_purchase_order.csv` (or use existing `/sample_event_log.csv`)

---

## TEST SCOPE

### Flow 1: Ingestion — Happy Path

**Expected Journey:**

1. User navigates to Login
2. User logs in (mock auth — any credentials work)
3. User sees Workspace/Home
4. User navigates to Upload page
5. User selects/drags CSV file
6. User sees validation preview
7. User configures column mapping (case_id, activity, timestamp)
8. User clicks process/submit
9. User sees success and uploaded log in their project

**Success Criteria:**

- [ ] Can upload a CSV file without errors
- [ ] File appears in event log list after upload
- [ ] Can click on uploaded log and see details

---

## TEST PROCEDURE

### Pre-Conditions

- [ ] Frontend running at localhost:4200
- [ ] Backend running
- [ ] Sample CSV file available

### Test Cases

#### TC-ING-001: File Upload Happy Path

1. Navigate to http://localhost:4200
2. Login with any credentials
3. Navigate to Upload page (/workspace/:id/upload)
4. Select sample CSV file
5. Verify preview shows correctly
6. Map columns: case_id, activity, timestamp
7. Click Next/Process
8. **Expected:** Upload succeeds, redirects to log view
9. **Record:** Pass/Fail + any errors

#### TC-ING-002: Log Appears in List

1. After successful upload
2. Navigate to Event Logs list (/processes)
3. **Expected:** Uploaded log appears in list
4. **Record:** Pass/Fail

#### TC-ING-003: Log Details Viewable

1. Click on uploaded log
2. **Expected:** See log details (cases, events, activities)
3. **Record:** Pass/Fail

---

## OUTPUT

Create or update `/docs/qa/QA_REPORT.md` with:

```markdown
# QA REPORT — Sprint 1: Ingestion

**Date:** [date]
**Tester:** QA Agent
**Environment:** localhost:4200

---

## Test Summary

| Test Case  | Description            | Status | Notes |
| ---------- | ---------------------- | ------ | ----- |
| TC-ING-001 | File Upload Happy Path | ✅/❌  |       |
| TC-ING-002 | Log Appears in List    | ✅/❌  |       |
| TC-ING-003 | Log Details Viewable   | ✅/❌  |       |

---

## Bugs Found

### Bug ING-001: [Title]

- **Severity:** Critical / Major / Minor
- **Steps:**
  1.
- **Expected:**
- **Actual:**
- **Screenshot/Evidence:** [if possible]

---

## Blockers

| Blocker | Impact |
| ------- | ------ |
|         |        |

---

## Recommendation

[ ] Ready for Sprint 2 fixes
[ ] Blocked — cannot proceed
```

---

## CONSTRAINTS

- **DO NOT FIX BUGS** — document only
- Use browser tools to test (you have browser_subagent capability)
- Take screenshots if possible
- Be specific about reproduction steps
