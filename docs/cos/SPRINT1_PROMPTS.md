# SPRINT 1 PROMPTS — Ready to Activate

## Overview

Sprint 1 is a **VERIFICATION SPRINT**. We test, don't build.

**Goal:** Verify that documented progress (90% Ingestion, 53% Discovery) actually works E2E

---

## Prompt Queue

| #   | Agent | Task                         | Priority | File                         |
| --- | ----- | ---------------------------- | -------- | ---------------------------- |
| 1   | CTO   | Provide sample test datasets | P1       | PROMPT_CTO_SAMPLE_DATA.md    |
| 2   | QA    | Verify Ingestion Flow E2E    | P1       | PROMPT_QA_INGESTION.md       |
| 3   | QA    | Verify Discovery Flow E2E    | P1       | PROMPT_QA_DISCOVERY.md       |
| 4   | CTO   | Quantify Discovery gaps      | P2       | PROMPT_CTO_DISCOVERY_GAPS.md |

---

## Current Status

- [x] CTO_STATE.md created
- [x] CPO_STATE.md created
- [x] SPRINT_PLAN.md created
- [x] CEO decisions locked
- [ ] Sample datasets provided
- [ ] Ingestion verified
- [ ] Discovery verified
- [ ] QA_REPORT.md created

---

## Session Workflow

### Step 1: Get Sample Data from CTO

Copy `PROMPT_CTO_SAMPLE_DATA.md` → New session → CTO provides test files

### Step 2: Activate QA for Ingestion Test

Copy `PROMPT_QA_INGESTION.md` → New session → QA tests upload flow

### Step 3: Activate QA for Discovery Test

Copy `PROMPT_QA_DISCOVERY.md` → New session → QA tests process mining

### Step 4: Return to CEO

Paste QA reports → CEO reviews → Sprint 2 planning

---

## Restartability Protocol

To restart any agent mid-session:

1. Copy their state doc (e.g., `/docs/cto/CTO_STATE.md`)
2. Start fresh agent session
3. Paste: "You are [ROLE]. Here is your state: [paste state doc]. Continue with: [task]"
4. Agent resumes with context

This keeps context length manageable over a month-long project.
