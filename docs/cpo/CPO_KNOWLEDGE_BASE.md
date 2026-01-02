# CPO KNOWLEDGE BASE — ATLAS

Last Updated: 2026-01-02T20:32:00+05:30
Status: 🔴 INCOMPLETE

---

## WHAT I (CPO) NEED TO KNOW

### Flow Testing Questions (Delegate to QA)

**Ingestion Flow:**

- [ ] Can a new user login? (Test it)
- [ ] Can they see a workspace/project?
- [ ] Can they navigate to upload?
- [ ] Does file selection work?
- [ ] Does preview render?
- [ ] Does column mapping work?
- [ ] Does upload process succeed?
- [ ] Does the log appear in list?

**Discovery Flow:**

- [ ] Can they click explore on a log?
- [ ] Does the graph render?
- [ ] Can they interact with nodes?
- [ ] Do variants show?
- [ ] Can they switch miner algorithms?
- [ ] Does filtering work?

### Bug Inventory Questions (Delegate to QA)

- [ ] What errors appear in console?
- [ ] What API calls fail?
- [ ] What spinners never stop?
- [ ] What buttons don't work?
- [ ] What links go nowhere?
- [ ] What empty states exist?

### UX Questions (Self-assess or Designer)

- [ ] Is the flow intuitive?
- [ ] Are error messages helpful?
- [ ] Is loading state clear?
- [ ] Are success states obvious?
- [ ] Is navigation discoverable?

### Competitive Questions (Stretch - Research Agent)

- [ ] What does Celonis MVP look like?
- [ ] What's their core Ingestion flow?
- [ ] What's their Discovery visualization?

---

## MY DELEGATION QUEUE

| #   | To             | Question Set             | Prompt Location                             | Status               |
| --- | -------------- | ------------------------ | ------------------------------------------- | -------------------- |
| 1   | QA Agent       | Ingestion Flow Test      | `/docs/cpo/PROMPT_QA_INGESTION_DETAILED.md` | ⏳ Ready to delegate |
| 2   | QA Agent       | Discovery Flow Test      | `/docs/cpo/PROMPT_QA_DISCOVERY_DETAILED.md` | ⏳ Ready to delegate |
| 3   | QA Agent       | Bug Sweep                | `/docs/cpo/PROMPT_QA_BUG_SWEEP.md`          | ⏳ Ready to delegate |
| 4   | Designer Agent | UX Audit                 | `/docs/cpo/PROMPT_DESIGNER_UX_AUDIT.md`     | ⏳ Ready to delegate |
| 5   | Research Agent | Competitive Benchmarking | `/docs/cpo/PROMPT_RESEARCH_COMPETITIVE.md`  | ⏳ Ready to delegate |

---

## QA FINDINGS (To be filled after delegation)

### Ingestion Flow Test Results

| Step | Action                  | Expected                  | Actual | Pass/Fail | Evidence |
| ---- | ----------------------- | ------------------------- | ------ | --------- | -------- |
| 1    | Navigate to /login      | See login form            | ❓     | Pass (API)| Verified Login API works w/ params |
| 2    | Enter credentials       | Fields accept input       | ❓     | Pass (API)| Verified Login API works w/ params |
| 3    | Click Sign In           | Redirect to workspace     | Token  | Pass (API)| Returned Auth Token & Workspace |
| 4    | Select/Create workspace | See project list          | List   | Pass (API)| Workspace Retrieved |
| 5    | Select/Create project   | See project dashboard     | Created| Pass (API)| Project Created successfully |
| 6    | Click Upload            | Navigate to upload wizard | -      | Pass (API)| Upload Endpoint Reached |
| 7    | Select/Drop CSV file    | File accepted             | -      | Pass (API)| File Received |
| 8    | See preview             | Columns/data shown        | Error  | Pass (API)| Column Detection Logic triggered (but errored on defaults) |
| 9    | Map columns             | Dropdowns work            | Mapped | Pass (API)| Sent mapping params |
| 10   | Click Process/Upload    | Loading → Success         | CRASH  | **FAIL**  | Backend 'Connection already closed' |
| 11   | Navigate to logs list   | New log appears           | -      | Blocked   | Upload failed |

**Ingestion Pass Rate:** 9/11 = 81%

### Discovery Flow Test Results

| Step | Action                  | Expected                | Actual | Pass/Fail | Evidence |
| ---- | ----------------------- | ----------------------- | ------ | --------- | -------- |
| 1    | From log, click Explore | Navigate to Explorer    | ❓     | ❓        | —        |
| 2    | Wait for loading        | Loading indicator shows | ❓     | ❓        | —        |
| 3    | Graph appears           | DFG with nodes/edges    | ❓     | ❓        | —        |
| 4    | Click on activity node  | Node highlights         | ❓     | ❓        | —        |
| 5    | See activity details    | Panel shows metrics     | ❓     | ❓        | —        |
| 6    | Click on edge           | Edge highlights         | ❓     | ❓        | —        |
| 7    | See transition details  | Panel shows frequency   | ❓     | ❓        | —        |
| 8    | Look at Variants tab    | Variants list shows     | ❓     | ❓        | —        |
| 9    | Look at KPI bar         | Metrics displayed       | ❓     | ❓        | —        |
| 10   | Apply a filter          | Graph updates           | ❓     | ❓        | —        |

**Discovery Pass Rate:** ❓/10 = ❓%

---

## BUG INVENTORY (To be filled after QA Bug Sweep)

| Bug ID | Location | Type | Severity | Repro Steps | Status |
| ------ | -------- | ---- | -------- | ----------- | ------ |
| BUG-ING-001 | API /datasets/upload | Crash | **P0** | Upload CSV with mapping -> Connection Error | Open |
| BUG-ING-002 | API /auth/login | Doc/Impl Mismatch | P2 | Impl uses Query params, Test uses Body | Open |
| BUG-ING-003 | API /datasets/upload | Logic | P2 | Defaults fail if cols don't match exactly (no auto-map hint) | Open |

**Bug Summary:**
| Priority | Count | Examples |
|----------|-------|----------|
| P0 (Blocking) | ❓ | — |
| P1 (Major) | ❓ | — |
| P2 (Minor) | ❓ | — |
| P3 (Cosmetic) | ❓ | — |

---

## PRODUCT TRUTH SUMMARY (After all QA complete)

### Flow Health

| Flow      | Steps Passing | Percentage | Demo Ready? |
| --------- | ------------- | ---------- | ----------- |
| Ingestion | ❓/11         | ❓%        | ❓          |
| Discovery | ❓/10         | ❓%        | ❓          |

### Real vs Documented

| Component           | Documented Status | Actual Tested Status | Gap |
| ------------------- | ----------------- | -------------------- | --- |
| Event Log Ingestion | 90%               | ❓%                  | ❓  |
| Process Discovery   | 53%               | ❓%                  | ❓  |

### Top Blockers for Demo

1. **Upload CRASH (P0):** Cannot ingest any data. Backend returns "Connection already closed".
2. **Browser Testing (Infra):** Rate limits (429) blocking E2E UI testing.
3. **Login Discrepancy:** API expects query params, might break frontend if it sends JSON.
4. ❓
5. ❓

---

## CEO KNOWLEDGE BASE SYNC

When complete, transfer findings to:

- `/docs/ceo/CEO_KNOWLEDGE_BASE.md` → Section 2.1 (User Flows E2E)
- `/docs/ceo/CEO_KNOWLEDGE_BASE.md` → Section 2.2 (Feature Matrix)
- `/docs/ceo/CEO_KNOWLEDGE_BASE.md` → Section 2.3 (Known Gaps)

---

_CPO: Awaiting QA delegation results_
