# ATLAS DELEGATION HIERARCHY

## Organization Structure

```
                              ┌─────────────┐
                              │     CEO     │
                              │   (ATLAS)   │
                              └──────┬──────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
            ▼                        ▼                        ▼
   ┌─────────────────┐     ┌─────────────────┐      ┌─────────────────┐
   │      CTO        │     │      CPO        │      │    CoS (User)   │
   │ Technical Truth │     │  Product Truth  │      │  Orchestrator   │
   └────────┬────────┘     └────────┬────────┘      └─────────────────┘
            │                       │
   ┌────────┼────────┐     ┌────────┼────────┐
   │        │        │     │        │        │
   ▼        ▼        ▼     ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ Dev  │ │ Dev  │ │ Dev  │ │  QA  │ │  QA  │ │Design│
│ BE   │ │ FE   │ │ DB   │ │ Ing  │ │ Disc │ │  UI  │
└──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
```

---

## Knowledge Flow

```
                    ┌─────────────────────────────────┐
                    │   CEO_KNOWLEDGE_BASE.md         │
                    │   (Ground Truth for Decisions)  │
                    └─────────────────────────────────┘
                                    ▲
                                    │ Aggregates
                    ┌───────────────┴───────────────┐
                    │                               │
         ┌──────────┴──────────┐         ┌─────────┴──────────┐
         │ CTO_KNOWLEDGE_BASE  │         │ CPO_KNOWLEDGE_BASE │
         │ (Technical Details) │         │ (Product Details)  │
         └──────────┬──────────┘         └─────────┬──────────┘
                    │                               │
         ┌──────────┴──────────┐         ┌─────────┴──────────┐
         │   Dev Agent Reports │         │   QA Agent Reports │
         │   - Backend Audit   │         │   - Flow Tests     │
         │   - Frontend Audit  │         │   - Bug Inventory  │
         │   - Database Audit  │         │   - UX Review      │
         └─────────────────────┘         └────────────────────┘
```

---

## Delegation Prompts by Level

### Level 1: CEO → CTO/CPO

| Prompt                        | Location   | Activates | Output                                   |
| ----------------------------- | ---------- | --------- | ---------------------------------------- |
| `PROMPT_CTO_INTERROGATION.md` | /docs/cos/ | CTO       | CTO Knowledge Base + CEO KB sections 1.x |
| `PROMPT_CPO_INTERROGATION.md` | /docs/cos/ | CPO       | CPO Knowledge Base + CEO KB sections 2.x |

### Level 2: CTO → Dev Agents

| Prompt                   | Location   | Activates    | Output                    |
| ------------------------ | ---------- | ------------ | ------------------------- |
| `PROMPT_DEV_BACKEND.md`  | /docs/cto/ | Backend Dev  | API & PM4Py audit         |
| `PROMPT_DEV_FRONTEND.md` | /docs/cto/ | Frontend Dev | Routes & components audit |
| `PROMPT_DEV_DATABASE.md` | /docs/cto/ | Database Dev | Schema & models audit     |

### Level 3: CPO → QA Agents

| Prompt                            | Location   | Activates | Output                    |
| --------------------------------- | ---------- | --------- | ------------------------- |
| `PROMPT_QA_INGESTION_DETAILED.md` | /docs/cpo/ | QA Agent  | Step-by-step test results |
| `PROMPT_QA_DISCOVERY_DETAILED.md` | /docs/cpo/ | QA Agent  | Step-by-step test results |
| `PROMPT_QA_BUG_SWEEP.md`          | /docs/cpo/ | QA Agent  | Complete bug inventory    |

---

## Activation Sequence

### Phase 1: CTO Knowledge Acquisition

```
CoS activate → CTO_INTERROGATION
  └── CTO creates knowledge base
  └── CTO creates Dev prompts
  └── CoS activate → DEV_BACKEND (new session)
  └── CoS activate → DEV_FRONTEND (new session)
  └── CoS activate → DEV_DATABASE (new session)
  └── CTO aggregates into CEO KB
```

### Phase 2: CPO Knowledge Acquisition

```
CoS activate → CPO_INTERROGATION
  └── CPO creates knowledge base
  └── CPO creates QA prompts
  └── CoS activate → QA_INGESTION (new session)
  └── CoS activate → QA_DISCOVERY (new session)
  └── CoS activate → QA_BUG_SWEEP (new session)
  └── CPO aggregates into CEO KB
```

### Phase 3: CEO Decision Making

```
CoS return to → CEO
  └── CEO reads filled knowledge base
  └── CEO makes informed decisions
  └── CEO approves Sprint 1 backlog
```

---

## Document Locations

### CEO Level

```
/docs/ceo/
  ├── CEO_STATE.md              # CEO's operating state
  └── CEO_KNOWLEDGE_BASE.md     # Ground truth (filled by CTO/CPO)
```

### CTO Level

```
/docs/cto/
  ├── CTO_STATE.md              # CTO's operating state
  ├── CTO_KNOWLEDGE_BASE.md     # Technical questions & answers
  ├── PROMPT_DEV_BACKEND.md     # For backend dev audits
  ├── PROMPT_DEV_FRONTEND.md    # For frontend dev audits
  └── PROMPT_DEV_DATABASE.md    # For database dev audits
```

### CPO Level

```
/docs/cpo/
  ├── CPO_STATE.md              # CPO's operating state
  ├── CPO_KNOWLEDGE_BASE.md     # Product questions & answers
  ├── PROMPT_QA_INGESTION_DETAILED.md
  ├── PROMPT_QA_DISCOVERY_DETAILED.md
  └── PROMPT_QA_BUG_SWEEP.md
```

### CoS Level (Orchestration)

```
/docs/cos/
  ├── COS_LOG.md                # Session tracking
  ├── PROMPT_CTO_INTERROGATION.md
  ├── PROMPT_CPO_INTERROGATION.md
  └── DELEGATION_HIERARCHY.md   # This file
```

---

## Rules for Leaders

### CEO Rules

- Never search codebase directly
- Demand facts in tables, not summaries
- Delegate to CTO and CPO only
- Maintain CEO_KNOWLEDGE_BASE as source of truth

### CTO Rules

- You are a leader, not a doer
- Delegate technical audits to Dev agents
- Create reusable Dev prompts
- Aggregate findings into your knowledge base
- Report rollups to CEO

### CPO Rules

- You are a leader, not a tester
- Delegate testing to QA agents
- Create reusable QA prompts
- Aggregate findings into your knowledge base
- Report rollups to CEO
- Quantify everything (percentages, not vibes)

### CoS Rules

- You are the only human
- You carry context between agents
- You activate prompts in fresh sessions
- You bring reports back up the chain
- You keep all logs updated
