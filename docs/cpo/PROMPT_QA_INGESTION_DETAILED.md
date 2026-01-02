# QA TASK: Test Ingestion Flow Step-by-Step

## Your Mission

Test EVERY step of the Ingestion flow. Document exactly what happens. No guessing — only observed facts.

---

## Test Environment

- **Frontend URL:** http://localhost:4200
- **Backend:** Should be running (check http://localhost:8000/docs)
- **Test File:** Find a sample CSV in the repo, or use any CSV with columns: case_id, activity, timestamp

---

## Step-by-Step Test Protocol

For EACH step, record:

- Did UI render correctly?
- Did expected action work?
- Any console errors? (Open DevTools → Console)
- Any network errors? (DevTools → Network)
- Screenshot or describe what you see

---

## Test Execution Table

| Step | Action                                     | Expected Result                                     | Actual Result | Pass/Fail | Evidence/Notes |
| ---- | ------------------------------------------ | --------------------------------------------------- | ------------- | --------- | -------------- |
| 1    | Open http://localhost:4200                 | See login page or landing                           |               |           |                |
| 2    | Navigate to /login (if not auto)           | See login form with email/password fields           |               |           |                |
| 3    | Enter test credentials                     | Fields accept input                                 |               |           |                |
| 4    | Click Sign In / Login button               | Either: redirect to workspace, OR see error message |               |           |                |
| 5    | Look for workspace selection               | See list of workspaces OR create workspace option   |               |           |                |
| 6    | Select or create a workspace               | Navigate into workspace view                        |               |           |                |
| 7    | Look for project selection                 | See list of projects OR create project option       |               |           |                |
| 8    | Select or create a project                 | Navigate into project dashboard                     |               |           |                |
| 9    | Find Upload option                         | See Upload button/tab/menu item                     |               |           |                |
| 10   | Click Upload                               | Navigate to upload wizard/modal                     |               |           |                |
| 11   | Select or drag CSV file                    | File accepted, name shown                           |               |           |                |
| 12   | See preview                                | Columns and sample data rows displayed              |               |           |                |
| 13   | Map columns (case_id, activity, timestamp) | Dropdowns work, correct columns selected            |               |           |                |
| 14   | Click Process/Upload/Import                | Loading state appears                               |               |           |                |
| 15   | Wait for completion                        | Success message OR error message                    |               |           |                |
| 16   | Navigate to event logs list                | See list of uploaded logs                           |               |           |                |
| 17   | Find newly uploaded log                    | Log appears in list with correct name               |               |           |                |
| 18   | Check log metadata                         | Shows row count, case count, activity count         |               |           |                |

---

## Bug Report Format

For EACH failure, document:

| Bug ID  | Step # | Expected | Actual | Severity | Console Error? | Network Error? |
| ------- | ------ | -------- | ------ | -------- | -------------- | -------------- |
| ING-001 |        |          |        |          |                |                |
| ING-002 |        |          |        |          |                |                |

**Severity Guide:**

- **P0** - Flow completely blocked, cannot continue
- **P1** - Major feature broken, significant impact
- **P2** - Minor issue, workaround exists
- **P3** - Cosmetic, polish issue

---

## Summary Output

Fill this after completing all tests:

### Pass Rate

- Steps Passing: \_\_/18
- Percentage: \_\_%

### Blocking Issues (P0)

1.
2.

### Critical Bugs Found

| Bug ID | Summary | Severity |
| ------ | ------- | -------- |
|        |         |          |

### Can User Complete Upload Flow?

- [ ] YES - fully works
- [ ] PARTIAL - works with workarounds
- [ ] NO - blocked

### Notes for CPO

(Any observations about UX, confusing steps, suggestions)

---

## Report To

**Deliver to:** CPO
**Update:** `/docs/cpo/CPO_KNOWLEDGE_BASE.md` → Ingestion Flow Test Results section
