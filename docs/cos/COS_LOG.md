# CHIEF OF STAFF LOG

## Active Session

Date: 2026-01-02
Phase: **UNDERSTAND** (Knowledge Acquisition)
Sprint: #0.5 (Interrogation Sprint)

---

## 🚨 OPERATING MODEL UPGRADE

All leaders now delegate with their own knowledge checklists:

```
CEO → CTO + CPO (with interrogation)
  CTO → Dev Agents (Backend, Frontend, Database)
  CPO → QA Agents (Ingestion Tests, Discovery Tests, Bug Sweep)
```

Everyone creates prompts for their sub-agents.

---

## Complete Prompt Inventory

### CEO Level (Ready)

| Prompt                        | Activates | Creates                                |
| ----------------------------- | --------- | -------------------------------------- |
| `PROMPT_CTO_INTERROGATION.md` | CTO       | CTO_KB + Dev prompts + CEO_KB sections |
| `PROMPT_CPO_INTERROGATION.md` | CPO       | CPO_KB + QA prompts + CEO_KB sections  |

### CTO Level (CTO Creates)

| Prompt                   | Activates    | Output           |
| ------------------------ | ------------ | ---------------- |
| `PROMPT_DEV_BACKEND.md`  | Backend Dev  | API inventory    |
| `PROMPT_DEV_FRONTEND.md` | Frontend Dev | Routes inventory |
| `PROMPT_DEV_DATABASE.md` | Database Dev | Schema inventory |

### CPO Level (CPO Creates)

| Prompt                            | Activates | Output                 |
| --------------------------------- | --------- | ---------------------- |
| `PROMPT_QA_INGESTION_DETAILED.md` | QA        | 10-step test results   |
| `PROMPT_QA_DISCOVERY_DETAILED.md` | QA        | 10-step test results   |
| `PROMPT_QA_BUG_SWEEP.md`          | QA        | Complete bug inventory |

---

## Execution Sequence

### Step 1: Activate CTO ← **START HERE**

```
1. Open: /docs/cos/PROMPT_CTO_INTERROGATION.md
2. Copy → New session
3. CTO creates:
   - CTO_KNOWLEDGE_BASE.md
   - PROMPT_DEV_BACKEND.md
   - PROMPT_DEV_FRONTEND.md
   - PROMPT_DEV_DATABASE.md
4. You get back Dev prompts to activate
```

### Step 2: Activate CTO's Dev Agents

```
5. Open: /docs/cto/PROMPT_DEV_BACKEND.md → New session → Backend Dev
6. Open: /docs/cto/PROMPT_DEV_FRONTEND.md → New session → Frontend Dev
7. Open: /docs/cto/PROMPT_DEV_DATABASE.md → New session → Database Dev
8. Bring reports back to CTO (or CTO aggregates if same session)
```

### Step 3: CTO Aggregates to CEO KB

```
9. CTO fills CEO_KNOWLEDGE_BASE.md sections 1.1-1.5
10. CTO provides summary report
11. You bring to CEO
```

### Step 4: Activate CPO

```
12. Open: /docs/cos/PROMPT_CPO_INTERROGATION.md
13. Copy → New session
14. CPO creates QA prompts
```

### Step 5: Activate CPO's QA Agents

```
15. Open: /docs/cpo/PROMPT_QA_INGESTION_DETAILED.md → New session
16. Open: /docs/cpo/PROMPT_QA_DISCOVERY_DETAILED.md → New session
17. Open: /docs/cpo/PROMPT_QA_BUG_SWEEP.md → New session
18. Bring reports back to CPO
```

### Step 6: CPO Aggregates to CEO KB

```
19. CPO fills CEO_KNOWLEDGE_BASE.md sections 2.1-2.3
20. CPO provides summary report
21. You bring to CEO
```

### Step 7: CEO Reviews Complete Knowledge Base

```
22. Activate CEO
23. "Knowledge Base complete. Review and decide."
24. CEO makes informed Sprint 1 decisions
```

---

## Document Checklist

### Created ✅

- [x] CEO_STATE.md
- [x] CEO_KNOWLEDGE_BASE.md (empty template)
- [x] PROMPT_CTO_INTERROGATION.md
- [x] PROMPT_CPO_INTERROGATION.md
- [x] DELEGATION_HIERARCHY.md

### CTO Will Create

- [ ] CTO_KNOWLEDGE_BASE.md
- [ ] PROMPT_DEV_BACKEND.md
- [ ] PROMPT_DEV_FRONTEND.md
- [ ] PROMPT_DEV_DATABASE.md

### CPO Will Create

- [ ] CPO_KNOWLEDGE_BASE.md
- [ ] PROMPT_QA_INGESTION_DETAILED.md
- [ ] PROMPT_QA_DISCOVERY_DETAILED.md
- [ ] PROMPT_QA_BUG_SWEEP.md

---

## Next Action

**ACTIVATE CTO** with:

```
/docs/cos/PROMPT_CTO_INTERROGATION.md
```

CTO will create their knowledge base and Dev delegation prompts.
Then you activate each Dev agent.
Then CTO aggregates.
Then repeat for CPO.
