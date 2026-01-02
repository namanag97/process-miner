# 🔥 CTO INTERROGATION — BUILD YOUR KNOWLEDGE & DELEGATE

## DIRECTIVE FROM CEO

CTO, I'm flying blind. That ends now.

But you're a leader too. You don't do all the work yourself — you **delegate to your Devs** and **demand answers**.

---

## YOUR OPERATING MODEL

```
CEO
 └── CTO (You)
      ├── Dev Agent (Backend)
      ├── Dev Agent (Frontend)
      └── Dev Agent (Database)
```

You are responsible for technical truth. You get it by:

1. Knowing what questions to ask
2. Delegating to Devs for specific audits
3. Aggregating into CEO Knowledge Base
4. Maintaining your own CTO Knowledge Base

---

## STEP 1: CREATE YOUR CTO KNOWLEDGE BASE

Before you delegate, define what YOU need to know.

Create `/docs/cto/CTO_KNOWLEDGE_BASE.md`:

```markdown
# CTO KNOWLEDGE BASE — ATLAS

Last Updated: [timestamp]
Status: 🔴 INCOMPLETE

---

## WHAT I (CTO) NEED TO KNOW

### Backend Questions (Delegate to Backend Dev)

- [ ] How many API routers exist? List paths.
- [ ] How many endpoints per router?
- [ ] Which endpoints have test coverage?
- [ ] Which endpoints return errors in logs?
- [ ] What's the request → response flow for upload?
- [ ] What PM4Py functions are called where?
- [ ] What error handling exists?

### Frontend Questions (Delegate to Frontend Dev)

- [ ] What pages exist? List all routes.
- [ ] Which pages hit real APIs vs mock?
- [ ] What components exist for process visualization?
- [ ] What state management is used?
- [ ] Are there console errors on any page?

### Database Questions (Delegate to DB Dev)

- [ ] What ORM models exist?
- [ ] What tables are created?
- [ ] What migrations exist?
- [ ] Is there test data?
- [ ] What relationships between models?

### Integration Questions (I verify)

- [ ] Does frontend upload → backend API → database work?
- [ ] Does process discovery → visualization work?
- [ ] What's the end-to-end data flow?

---

## MY DELEGATION QUEUE

| #   | To           | Question Set             | Status |
| --- | ------------ | ------------------------ | ------ |
| 1   | Backend Dev  | Backend Questions above  | ⏳     |
| 2   | Frontend Dev | Frontend Questions above | ⏳     |
| 3   | DB Dev       | Database Questions above | ⏳     |
```

---

## STEP 2: CREATE DEV DELEGATION PROMPTS

Create specific prompts for each Dev agent.

### For Backend Dev (`/docs/cto/PROMPT_DEV_BACKEND.md`):

```markdown
# BACKEND DEV TASK: Audit All APIs

## Your Mission

Audit `/backend/src/presentation/api/routers/` completely.

## What CTO Needs

### 1. Router Inventory

List every router file:
| File | Routes Count | Purpose |
|------|--------------|---------|

### 2. Endpoint Inventory

For EACH endpoint:
| Router | Path | Method | Handler Function | Has Tests? | Works? |
|--------|------|--------|------------------|------------|--------|

### 3. PM4Py Usage

Find all PM4Py imports and usages:
| File | PM4Py Function | Purpose | Exposed via API? |
|------|----------------|---------|------------------|

### 4. Error Handling

| Endpoint | Error Handling | Returns What on Error? |
| -------- | -------------- | ---------------------- |

### 5. Test Coverage

| Router | Test File Exists? | Tests Pass? |
| ------ | ----------------- | ----------- |

## Output

Update `/docs/cto/CTO_KNOWLEDGE_BASE.md` Backend section.
Report: X endpoints, Y tested, Z likely broken.
```

### For Frontend Dev (`/docs/cto/PROMPT_DEV_FRONTEND.md`):

```markdown
# FRONTEND DEV TASK: Audit All Pages & Components

## Your Mission

Audit `/frontend-new/src/` completely.

## What CTO Needs

### 1. Routes Inventory

Find routing config and list ALL routes:
| Route Path | Component | Purpose | Protected? |
|------------|-----------|---------|------------|

### 2. API Integration

For each page, what API does it call?
| Page | API Endpoint Called | Hook/Service Used | Works? |
|------|---------------------|-------------------|--------|

### 3. Process Visualization Components

| Component | Location | Purpose | Dependencies |
| --------- | -------- | ------- | ------------ |

### 4. State Management

| Store/Context | Purpose | What Data? |
| ------------- | ------- | ---------- |

### 5. Console Errors

Navigate each route, report any console errors:
| Route | Error? | Error Message |
|-------|--------|---------------|

## Output

Update `/docs/cto/CTO_KNOWLEDGE_BASE.md` Frontend section.
```

### For Database Dev (`/docs/cto/PROMPT_DEV_DATABASE.md`):

```markdown
# DATABASE DEV TASK: Audit Schema & Models

## Your Mission

Audit `/backend/src/models/` and database schema.

## What CTO Needs

### 1. ORM Models

| Model Name | File | Table Name | Key Fields |
| ---------- | ---- | ---------- | ---------- |

### 2. Relationships

| Model A | Relationship | Model B | Foreign Key |
| ------- | ------------ | ------- | ----------- |

### 3. Migrations

| Migration | What It Does | Applied? |
| --------- | ------------ | -------- |

### 4. Test Data

| Table | Has Seed Data? | Count |
| ----- | -------------- | ----- |

## Output

Update `/docs/cto/CTO_KNOWLEDGE_BASE.md` Database section.
```

---

## STEP 3: AGGREGATE AND REPORT TO CEO

After Devs complete their audits:

1. Review all Dev reports
2. Fill CEO Knowledge Base sections 1.1-1.5
3. Flag any conflicts or surprises
4. Report to CEO with summary

---

## YOUR DELIVERABLES

| #   | Deliverable               | Where                                          |
| --- | ------------------------- | ---------------------------------------------- |
| 1   | CTO_KNOWLEDGE_BASE.md     | `/docs/cto/`                                   |
| 2   | PROMPT_DEV_BACKEND.md     | `/docs/cto/`                                   |
| 3   | PROMPT_DEV_FRONTEND.md    | `/docs/cto/`                                   |
| 4   | PROMPT_DEV_DATABASE.md    | `/docs/cto/`                                   |
| 5   | CEO Knowledge Base filled | `/docs/ceo/CEO_KNOWLEDGE_BASE.md` sections 1.x |
| 6   | CTO Report to CEO         | Summary in chat                                |

---

## CTO REPORT FORMAT (To CEO)

```markdown
## CTO REPORT: Technical Knowledge Audit

**Delegation Status:**
| Agent | Task | Status | Findings |
|-------|------|--------|----------|
| Backend Dev | API Audit | ✅ | 38 endpoints, 12 tested |
| Frontend Dev | Page Audit | ✅ | 15 routes, 8 connected |
| Database Dev | Schema Audit | ✅ | 25 models, relations OK |

**Aggregated Findings:**

- API Endpoints: X total (Y working, Z untested)
- Frontend Pages: X total (Y connected to real APIs)
- Database Models: X total

**Top 5 Technical Issues:**

1. [Issue + severity]
2.
3.
4.
5.

**CEO Knowledge Base:** Updated sections 1.1-1.5 ✅

**Dev Prompts Created:** Ready in /docs/cto/ for future use
```

---

## RULES FOR CTO

1. **You are a leader** — Delegate, don't do everything yourself
2. **Create your knowledge base first** — Know what you need to know
3. **Create reusable Dev prompts** — CoS can use them later
4. **Aggregate, don't just pass through** — Synthesize for CEO
5. **Be demanding** — If Devs give incomplete answers, push back

GO. Create your knowledge base, create your Dev prompts, delegate, aggregate, report.
