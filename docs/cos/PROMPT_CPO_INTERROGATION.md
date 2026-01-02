# 🔥 CPO INTERROGATION — BUILD YOUR KNOWLEDGE & DELEGATE

## DIRECTIVE FROM CEO

CPO, I need product ground truth. But you're a leader too.

You don't test everything yourself — you **delegate to QA and Researchers** and **demand answers**.

---

## YOUR OPERATING MODEL

```
CEO
 └── CPO (You)
      ├── QA Agent (Tests flows, finds bugs)
      ├── Research Agent (Competitor analysis, user research)
      └── Designer Agent (UI/UX review)
```

You are responsible for product truth. You get it by:

1. Knowing what questions to ask
2. Delegating to QA for testing
3. Aggregating into CEO Knowledge Base
4. Maintaining your own CPO Knowledge Base

---

## STEP 1: CREATE YOUR CPO KNOWLEDGE BASE

Before you delegate, define what YOU need to know.

Create `/docs/cpo/CPO_KNOWLEDGE_BASE.md`:

```markdown
# CPO KNOWLEDGE BASE — ATLAS

Last Updated: [timestamp]
Status: 🔴 INCOMPLETE

---

## WHAT I (CPO) NEED TO KNOW

### Flow Testing Questions (Delegate to QA)

- [ ] Can a new user login? (Test it)
- [ ] Can they see a workspace/project?
- [ ] Can they navigate to upload?
- [ ] Does file selection work?
- [ ] Does preview render?
- [ ] Does column mapping work?
- [ ] Does upload process succeed?
- [ ] Does the log appear in list?
- [ ] Can they click explore?
- [ ] Does the graph render?
- [ ] Can they interact with nodes?
- [ ] Do variants show?

### Bug Inventory Questions (Delegate to QA)

- [ ] What errors appear in console?
- [ ] What API calls fail?
- [ ] What spinners never stop?
- [ ] What buttons don't work?

### UX Questions (Delegate to Designer or self-assess)

- [ ] Is the flow intuitive?
- [ ] Are error messages helpful?
- [ ] Is loading state clear?
- [ ] Are success states obvious?

### Competitive Questions (Delegate to Research)

- [ ] What does Celonis MVP look like?
- [ ] What's their core Ingestion flow?
- [ ] What's their Discovery visualization?

---

## MY DELEGATION QUEUE

| #   | To       | Question Set         | Status    |
| --- | -------- | -------------------- | --------- |
| 1   | QA Agent | Flow Testing         | ⏳        |
| 2   | QA Agent | Bug Inventory        | ⏳        |
| 3   | Designer | UX Review            | ⏳        |
| 4   | Research | Competitive Analysis | (Stretch) |
```

---

## STEP 2: CREATE QA DELEGATION PROMPTS

Create specific prompts for QA agent.

### For QA - Ingestion Flow (`/docs/cpo/PROMPT_QA_INGESTION_DETAILED.md`):

```markdown
# QA TASK: Test Ingestion Flow Step-by-Step

## Your Mission

Test EVERY step of the Ingestion flow. Document exactly what happens.

## What CPO Needs

### Test Environment

- URL: http://localhost:4200
- Backend: Running
- Test File: /sample_event_log.csv or /demo/\*.csv

### Step-by-Step Test Protocol

For EACH step, record:

- Did UI render? (Screenshot if possible)
- Did expected action work?
- Any console errors?
- Any network errors?

| Step | Action                   | Expected            | Actual | Pass/Fail | Evidence |
| ---- | ------------------------ | ------------------- | ------ | --------- | -------- |
| 1    | Navigate to /login       | See login form      |        |           |          |
| 2    | Enter any email/password | Fields accept input |        |           |          |
| 3    | Click Sign In            | Redirect to /home   |        |           |          |
| 4    | Look for Upload option   | See Upload button   |        |           |          |
| 5    | Click Upload             | Navigate to wizard  |        |           |          |
| 6    | Drag CSV file            | File accepted       |        |           |          |
| 7    | See preview              | Columns/data shown  |        |           |          |
| 8    | Map columns              | Dropdowns work      |        |           |          |
| 9    | Click Process            | Loading → Success   |        |           |          |
| 10   | Navigate to logs list    | New log appears     |        |           |          |

### Bug Report Format

For each failure:
| Bug ID | Step | Expected | Actual | Severity | Console Error |
|--------|------|----------|--------|----------|---------------|

## Output

1. Test results table (above)
2. Bugs found list
3. Percentage complete: X/10 steps pass = Y%
4. Blocking bugs (things preventing flow completion)

Report to CPO.
```

### For QA - Discovery Flow (`/docs/cpo/PROMPT_QA_DISCOVERY_DETAILED.md`):

```markdown
# QA TASK: Test Discovery Flow Step-by-Step

## Prerequisite

Ingestion flow must pass (need an uploaded log to test Discovery).

## What CPO Needs

| Step | Action                         | Expected                 | Actual | Pass/Fail | Evidence |
| ---- | ------------------------------ | ------------------------ | ------ | --------- | -------- |
| 1    | From log detail, click Explore | Navigate to Explorer     |        |           |          |
| 2    | Wait for loading               | See loading indicator    |        |           |          |
| 3    | Graph appears                  | See DFG with nodes/edges |        |           |          |
| 4    | Click on activity node         | Node highlights          |        |           |          |
| 5    | See activity details           | Panel shows metrics      |        |           |          |
| 6    | Click on edge                  | Edge highlights          |        |           |          |
| 7    | See transition details         | Panel shows frequency    |        |           |          |
| 8    | Look at Variants tab           | Variants list shows      |        |           |          |
| 9    | Look at KPI bar                | Metrics displayed        |        |           |          |
| 10   | Apply a filter                 | Graph updates            |        |           |          |

## Output

Report to CPO with pass rate and bugs.
```

### For QA - Bug Sweep (`/docs/cpo/PROMPT_QA_BUG_SWEEP.md`):

```markdown
# QA TASK: Full Bug Sweep

## Your Mission

Find EVERY bug across both flows.

## Check List

- [ ] Console errors on each page
- [ ] Network failures (4xx, 5xx responses)
- [ ] Spinners that never resolve
- [ ] Buttons that don't respond
- [ ] Links that go nowhere
- [ ] Empty states that should have data
- [ ] Error messages that aren't helpful

## Output

Complete bug inventory:
| Bug ID | Location | Type | Severity | Repro Steps |
|--------|----------|------|----------|-------------|

Priority ranking:

1. P0 - Blocks flow completely
2. P1 - Major functionality broken
3. P2 - Minor issue, workaround exists
4. P3 - Cosmetic/polish
```

---

## STEP 3: AGGREGATE AND REPORT TO CEO

After QA completes their audits:

1. Review all QA reports
2. Fill CEO Knowledge Base sections 2.1-2.3
3. Calculate real completion percentages
4. Report to CEO with actionable summary

---

## YOUR DELIVERABLES

| #   | Deliverable                     | Where                                          |
| --- | ------------------------------- | ---------------------------------------------- |
| 1   | CPO_KNOWLEDGE_BASE.md           | `/docs/cpo/`                                   |
| 2   | PROMPT_QA_INGESTION_DETAILED.md | `/docs/cpo/`                                   |
| 3   | PROMPT_QA_DISCOVERY_DETAILED.md | `/docs/cpo/`                                   |
| 4   | PROMPT_QA_BUG_SWEEP.md          | `/docs/cpo/`                                   |
| 5   | CEO Knowledge Base filled       | `/docs/ceo/CEO_KNOWLEDGE_BASE.md` sections 2.x |
| 6   | CPO Report to CEO               | Summary in chat                                |

---

## CPO REPORT FORMAT (To CEO)

```markdown
## CPO REPORT: Product Knowledge Audit

**Delegation Status:**
| Agent | Task | Status | Findings |
|-------|------|--------|----------|
| QA | Ingestion Test | ✅ | 7/10 steps pass |
| QA | Discovery Test | ✅ | 5/10 steps pass |
| QA | Bug Sweep | ✅ | 12 bugs found |

**Flow Health:**
| Flow | Steps Passing | Percentage | Demo Ready? |
|------|---------------|------------|-------------|
| Ingestion | 7/10 | 70% | ⚠️ With workarounds |
| Discovery | 5/10 | 50% | ❌ Needs fixes |

**Bug Summary:**
| Priority | Count | Examples |
|----------|-------|----------|
| P0 (Blocking) | 2 | Upload fails, Graph empty |
| P1 (Major) | 4 | ... |
| P2 (Minor) | 6 | ... |

**Top 5 Bugs to Fix:**

1. [Bug + impact]
2.
3.
4.
5.

**CEO Knowledge Base:** Updated sections 2.1-2.3 ✅

**QA Prompts Created:** Ready in /docs/cpo/ for future use
```

---

## RULES FOR CPO

1. **You are a leader** — Delegate to QA, don't test everything yourself
2. **Create your knowledge base first** — Know what you need to know
3. **Create reusable QA prompts** — CoS can use them repeatedly
4. **Aggregate findings** — Synthesize for CEO
5. **Be honest** — If something's broken, say so clearly
6. **Quantify** — Percentages, not vibes

GO. Create your knowledge base, create your QA prompts, delegate, aggregate, report.
