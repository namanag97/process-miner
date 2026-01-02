# SPRINT PLAN — Sprint 1

**Duration:** Week 1 (Jan 2 - Jan 9, 2026)
**Goal:** Stabilize Ingestion Flow to 100% and verify Discovery baseline works E2E
**Status:** 📋 Planning

---

## 🎯 SPRINT OBJECTIVE

> Complete the Ingestion Flow (90% → 100%) and verify Discovery Flow works end-to-end. By end of Sprint 1, a user should be able to upload a CSV file AND see a basic process graph.

---

## 📋 SPRINT BACKLOG

### Priority 1 — Must Complete

| #      | Task                                                | Type  | Owner | Business Activity | Status         |
| ------ | --------------------------------------------------- | ----- | ----- | ----------------- | -------------- |
| S1-001 | Verify CSV upload E2E flow works                    | QA    | QA    | DIS-001           | ⬜ Not Started |
| S1-002 | Verify XES upload E2E flow works                    | QA    | QA    | DIS-001           | ⬜ Not Started |
| S1-003 | Fix any blocking bugs in upload flow                | Bug   | CTO   | DIS-001, DIS-002  | ⬜ Pending QA  |
| S1-004 | Improve error messaging for invalid files           | UX    | CTO   | DIS-003           | ⬜ Not Started |
| S1-005 | Verify column mapping wizard works correctly        | QA    | QA    | DIS-002           | ⬜ Not Started |
| S1-006 | Verify data preview shows correct sample            | QA    | QA    | DIS-004           | ⬜ Not Started |
| S1-007 | Verify quality report displays after upload         | QA    | QA    | DIS-003           | ⬜ Not Started |
| S1-008 | Run Alpha Miner on test data → verify graph renders | QA    | QA    | DIS-007, DIS-008  | ⬜ Not Started |
| S1-009 | Document any Discovery bugs found                   | Bug   | QA    | —                 | ⬜ Not Started |
| S1-010 | Create sample test data files (CSV, XES)            | Setup | CPO   | —                 | ⬜ Not Started |

### Priority 2 — Should Complete

| #      | Task                                            | Type     | Owner | Business Activity  | Status         |
| ------ | ----------------------------------------------- | -------- | ----- | ------------------ | -------------- |
| S1-011 | Write acceptance test script for Ingestion Flow | QA       | QA    | —                  | ⬜ Not Started |
| S1-012 | Assess gaps in Discovery Flow (detailed list)   | Analysis | CTO   | DIS-005 to DIS-015 | ⬜ Not Started |
| S1-013 | Prioritize Discovery gaps for Sprint 2          | Planning | CPO   | —                  | ⬜ Not Started |
| S1-014 | Verify Heuristic Miner works                    | QA       | QA    | DIS-007            | ⬜ Not Started |
| S1-015 | Verify Inductive Miner works                    | QA       | QA    | DIS-007            | ⬜ Not Started |

### Priority 3 — Nice to Have

| #      | Task                               | Type | Owner | Business Activity | Status         |
| ------ | ---------------------------------- | ---- | ----- | ----------------- | -------------- |
| S1-016 | Test frequency annotation on DFG   | QA   | QA    | DIS-010           | ⬜ Not Started |
| S1-017 | Test performance annotation on DFG | QA   | QA    | DIS-011           | ⬜ Not Started |

---

## 📊 SPRINT METRICS

| Metric              | Target | Current |
| ------------------- | ------ | ------- |
| Must Complete Tasks | 10/10  | 0/10    |
| Ingestion Coverage  | 100%   | 90%     |
| Blocking Bugs Fixed | All    | TBD     |
| E2E Test Pass Rate  | 100%   | TBD     |

---

## 🚧 BLOCKERS

| Blocker                                        | Impact                         | Owner | Status              |
| ---------------------------------------------- | ------------------------------ | ----- | ------------------- |
| Unknown if frontend-backend integration stable | Can't start E2E testing        | CTO   | 🔴 Needs assessment |
| No standardized test data files                | Can't execute repeatable tests | CPO   | 🟡 S1-010 addresses |
| Discovery gaps not detailed                    | Can't plan Sprint 2 accurately | CTO   | 🟡 S1-012 addresses |

---

## 📝 DEPENDENCIES

### Need from CTO:

- [ ] Confirm frontend-backend integration is running and accessible
- [ ] Provide list of known bugs in upload flow
- [ ] Assess Discovery Flow gaps (what specifically is missing at 53%)
- [ ] Identify any infrastructure blockers

### Need from CEO:

- [ ] Confirm MVP scope (Cognitive in/out)
- [ ] Confirm sprint 1 priorities are aligned with business goals
- [ ] Approve sprint kickoff

---

## ✅ DEFINITION OF DONE (Sprint 1)

Sprint 1 is complete when:

1. **Ingestion Flow verified at 100%:**

   - [ ] CSV upload works without errors
   - [ ] XES upload works without errors
   - [ ] Column mapping saves correctly
   - [ ] Quality report displays
   - [ ] Dataset appears in project dashboard

2. **Discovery baseline verified:**

   - [ ] Alpha Miner produces visible graph
   - [ ] No JavaScript errors in console
   - [ ] Graph is interactive (zoom/pan works)

3. **Documentation complete:**
   - [ ] Bug list from testing documented
   - [ ] Discovery gaps documented for Sprint 2
   - [ ] Sprint 1 retrospective completed

---

## 📅 SPRINT SCHEDULE

| Day     | Focus             | Key Activities                                |
| ------- | ----------------- | --------------------------------------------- |
| Day 1   | Setup             | Create test data, verify environment, kickoff |
| Day 2-3 | Ingestion Testing | Execute S1-001 through S1-007                 |
| Day 4   | Bug Fixes         | Fix any blockers found (S1-003, S1-004)       |
| Day 5   | Discovery Testing | Execute S1-008, S1-014, S1-015                |
| Day 6   | Gap Analysis      | Complete S1-012, S1-013                       |
| Day 7   | Wrap-up           | Retrospective, Sprint 2 planning prep         |

---

## 📝 NOTES

- **Sprint 1 is primarily a VERIFICATION sprint** — we're validating what's documented as working actually works
- Keep scope tight — don't expand into feature development until baseline is verified
- Any bugs found should be documented and triaged; only **blocking bugs** fixed in Sprint 1
- Non-blocking bugs queued for Sprint 2 or later

---

_Sprint Owner: CPO_
_Last Updated: 2026-01-02T20:10:00+05:30_
