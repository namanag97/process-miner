# CPO STATE — ATLAS Process Mining Platform

Last Updated: 2026-01-02T20:35:00+05:30
Current Sprint: #0.5 (Interrogation Sprint)
Status: 🔵 **DELEGATING — Awaiting agent reports**

---

## 🚨 CPO OPERATING MODE

**Role:** Product leader — I delegate, I don't execute.

```
CEO
 └── CPO (Me)
      ├── QA Agent → Tests flows, finds bugs
      ├── Research Agent → Competitive analysis
      └── Designer Agent → UX review
```

**My job:**

1. Know what questions to ask
2. Create specific delegation prompts
3. Aggregate findings into CEO Knowledge Base
4. Report product truth to CEO

---

## 🎯 PRODUCT DEFINITION

### User Personas

| Persona                | Description                                                                      | Primary Goal                                                                          |
| ---------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **Process Analyst**    | Technical user who imports data, runs discovery algorithms, and creates analysis | Discover actual process behavior from event data, identify optimization opportunities |
| **Compliance Officer** | Governance role ensuring processes adhere to regulations                         | Verify process conformance, document deviations, generate audit evidence              |
| **Operations Manager** | Business leader responsible for process efficiency                               | Monitor KPIs, identify bottlenecks, track improvement initiatives                     |
| **Business Manager**   | Non-technical stakeholder needing process insights                               | Understand variant distribution, view dashboards, make data-driven decisions          |

### Core Value Proposition

**ATLAS empowers enterprises to discover how their processes actually work** — not how they're documented — **by mining event logs and visualizing process flows.**

Key Differentiators:

- **Upload → Discover → Visualize** in minutes, not weeks
- **PM4Py-powered** process discovery with enterprise-grade UI
- **Actionable insights** — bottlenecks, variants, conformance issues surfaced automatically

---

## 🗺️ USER FLOWS (Detailed)

### Flow 1: Ingestion

**Goal:** User uploads process execution data and sees it available in their project for analysis.

**Trigger:** User has CSV/XES file containing event log data.

**Steps:**

1. User logs in → sees workspace selection screen
2. User selects/creates workspace → sees project list
3. User selects/creates project → sees project dashboard
4. User clicks "Upload" → sees upload wizard
5. User drags/drops or selects CSV/XES file → file uploads
6. System validates file format → shows preview of data
7. User maps columns (case_id, activity, timestamp) → system confirms mapping
8. User clicks "Import" → dataset created
9. User sees dataset listed in project dashboard with basic stats

**Success State:**

- Dataset visible in project dashboard
- Row count, case count, activity count displayed
- Quality indicators shown (valid/invalid rows)

**Current Status:** 🟢 **90% Complete** (UAT Ready)

- ✅ CSV/XES upload working
- ✅ Preview functionality
- ✅ Statistics generation
- ✅ Quality validation
- ⚠️ Minor: Column mapping UX refinements needed

---

### Flow 2: Discovery

**Goal:** User generates a visual process model (DFG/Petri net) from their uploaded event data.

**Trigger:** User has at least one dataset uploaded in their project.

**Steps:**

1. User navigates to Discovery module → sees dataset selection
2. User selects dataset → sees algorithm options
3. User selects discovery algorithm (Alpha, Heuristic, Inductive) → sees parameter options
4. User adjusts parameters (optional) or accepts defaults
5. User clicks "Discover" → system runs PM4Py miner
6. System generates process model → displays Process Explorer
7. User sees DFG/Petri net visualization with activities as nodes, transitions as edges
8. User can zoom, pan, select nodes for details
9. User can annotate model with frequency or performance data

**Success State:**

- Interactive process graph displayed without errors
- Nodes show activity names
- Edges show flow relationships
- Frequency/performance annotations visible

**Current Status:** 🟡 **53% Complete** (Partial)

- ✅ Alpha, Heuristic, Inductive miners working
- ✅ Basic DFG visualization
- ✅ Petri net generation
- ❌ Missing: Export to BPMN/PNML
- ❌ Missing: Algorithm parameter configuration UI
- ❌ Missing: Model comparison view
- ❌ Missing: Model quality metrics display

---

### Flow 3: Cognitive (AI-Powered Insights)

**Goal:** User asks natural language questions about their process and gets data-backed answers.

**Trigger:** User has discovered process model and wants deeper insights without manual analysis.

**Steps:**

1. User opens Cognitive Assistant panel
2. System shows knowledge graph built from process data
3. User types question: "Where is the biggest bottleneck?"
4. LLM processes question → queries knowledge graph → retrieves relevant data
5. System displays answer with supporting evidence (charts, numbers, highlighted nodes)
6. User can ask follow-up questions or refine scope

**Success State:**

- User receives accurate, data-backed answer to their question
- Answer includes visual evidence (highlighted bottleneck in process model)
- Response time < 10 seconds

**Current Status:** 🔴 **0% Complete** (Not Started)

- ❌ Knowledge graph construction not implemented
- ❌ LLM integration not implemented
- ❌ NL query interface not built
- **Recommendation:** Defer to v1.1

---

## 📅 MVP SCOPE PROPOSAL

### ✅ IN SCOPE (Must Ship for MVP)

**Ingestion Flow (Complete to 100%):**

- [x] CSV/XES file upload
- [x] Data preview and validation
- [x] Column mapping wizard
- [x] Quality report generation
- [ ] Error messaging improvements (10% remaining)

**Discovery Flow (Target: 80%+):**

- [x] Alpha Miner execution
- [x] Heuristic Miner execution
- [x] Inductive Miner execution
- [x] DFG visualization
- [x] Petri net visualization
- [ ] Frequency annotation on model
- [ ] Performance annotation on model
- [ ] Algorithm parameter configuration panel
- [ ] Model export (BPMN at minimum)

**Core Infrastructure:**

- [x] User authentication
- [x] Workspace management
- [x] Project management
- [ ] Stable frontend-backend integration

### ⏳ STRETCH (If Time Permits)

- [ ] Variant Analysis — basic variant list with frequency (VAR-001 to VAR-003)
- [ ] Conformance Check — fitness score display (CON-006, CON-007)
- [ ] Performance Summary — case duration distribution (PER-001, PER-002)
- [ ] Model comparison view (DIS-012)

### ❌ OUT OF SCOPE (v1.1+)

- [ ] Cognitive Layer (NL questions, knowledge graph)
- [ ] Dashboards & Report Builder (DSH-\*)
- [ ] Predictive Process Monitoring (PRD-\*)
- [ ] Concept Drift Detection (DRF-\*)
- [ ] Object-Centric Process Mining (OCE-\*)
- [ ] RPA Discovery (RPA-\*)
- [ ] Simulation & What-If (SIM-\*)
- [ ] Alerting & Monitoring (ALR-\*)
- [ ] Compliance Monitoring advanced (CMP-\* beyond basic conformance)

---

## 📊 ACCEPTANCE CRITERIA (Per Flow)

| Flow          | Success Criteria                                                              | Test Method               | Status                |
| ------------- | ----------------------------------------------------------------------------- | ------------------------- | --------------------- |
| **Ingestion** | User uploads sample CSV file, sees it in project with correct row/case counts | E2E test with sample data | 🟡 Needs verification |
| **Ingestion** | User uploads XES file, column mapping auto-detected                           | E2E test with XES sample  | 🟡 Needs verification |
| **Ingestion** | Invalid file shows clear error message                                        | Negative test             | ⚠️ Unknown            |
| **Discovery** | User runs Alpha Miner on sample data, sees process graph within 30s           | E2E test                  | 🟡 Needs verification |
| **Discovery** | Discovered model shows all activities present in source data                  | Validation test           | 🟡 Needs verification |
| **Discovery** | User can export discovered model as BPMN file                                 | Feature test              | ❌ Not implemented    |
| **E2E**       | User completes full Upload → Discover flow without errors                     | Integration test          | 🟡 Needs verification |

---

## 📋 SPRINT BACKLOG (Proposed)

See: [/docs/sprints/SPRINT_PLAN.md](file:///Users/namanagarwal/system/docs/sprints/SPRINT_PLAN.md)

---

## 🎯 MVP MILESTONES

| Milestone                  | Target Date                | Success Criteria                               |
| -------------------------- | -------------------------- | ---------------------------------------------- |
| **M1: Ingestion Complete** | End of Sprint 1            | Upload CSV → see in dashboard with no bugs     |
| **M2: Discovery Complete** | End of Sprint 2            | Run miner → see process graph with annotations |
| **M3: MVP Ship**           | End of Sprint 4 (~1 month) | Full E2E flow working, deployed to staging     |

---

## 📈 METRICS TO TRACK

| Metric                          | Current      | Target (MVP) |
| ------------------------------- | ------------ | ------------ |
| Ingestion Coverage              | 90%          | 100%         |
| Discovery Coverage              | 53%          | 80%          |
| Business Activities Implemented | 61/237 (26%) | 90/237 (38%) |
| E2E Flow Success Rate           | Unknown      | 95%          |

---

## 📝 QUESTIONS FOR CEO

1. [ ] **Confirm: Cognitive Layer in or out of MVP?**

   - CPO Recommendation: **OUT** — adds significant scope with uncertain timeline. Defer to v1.1.

2. [ ] **Confirm: What's the firm ship date target?**

   - Need to know if ~1 month is hard deadline or flexible.

3. [ ] **Confirm: Any must-have features not listed?**

   - Are there customer commitments requiring specific features?

4. [ ] **Confirm: Variant Analysis priority?**

   - Currently marked as stretch. Should it be must-have for MVP?

5. [ ] **Confirm: Export format requirements?**
   - BPMN export sufficient, or need PNML, PNG, SVG as well?

---

## 📊 COVERAGE ANALYSIS (from businessusecase.md)

### Activity Implementation by Use Case

| Use Case                   | Total Activities | MVP Target | Status        |
| -------------------------- | ---------------- | ---------- | ------------- |
| Process Discovery (DIS-\*) | 15               | 10         | 🟡 ~8 working |
| Variant Analysis (VAR-\*)  | 15               | 5          | 🔴 ~3 working |
| Conformance (CON-\*)       | 22               | 4          | 🟡 Stretch    |
| Performance (PER-\*)       | 20               | 3          | 🟡 Stretch    |
| Bottleneck (BOT-\*)        | 12               | 0          | ❌ v1.1       |
| Root Cause (RCA-\*)        | 13               | 0          | ❌ v1.1       |
| Org Mining (ORG-\*)        | 15               | 0          | ❌ v1.1       |
| Predictive (PRD-\*)        | 15               | 0          | ❌ v1.1       |
| Drift (DRF-\*)             | 12               | 0          | ❌ v1.1       |
| OCEL (OCE-\*)              | 19               | 0          | ❌ v1.1       |
| RPA (RPA-\*)               | 14               | 0          | ❌ v1.1       |
| Compliance (CMP-\*)        | 17               | 0          | ❌ v1.1       |
| Simulation (SIM-\*)        | 14               | 0          | ❌ v1.1       |
| Dashboard (DSH-\*)         | 18               | 0          | ❌ v1.1       |
| Alerting (ALR-\*)          | 16               | 0          | ❌ v1.1       |

**MVP Focus:** Discovery (DIS) + Variant (VAR) core activities only.

---

_Last reviewed by: CPO Agent_
_Next update: After Sprint 1 kickoff_
