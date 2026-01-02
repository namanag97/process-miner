# CTO TASK: Provide Sample Test Datasets

## CONTEXT

You are the CTO of ATLAS. Sprint 1 is a **Verification Sprint** — we're testing that Ingestion and Discovery flows work E2E.

**Your State Doc:** `/docs/cto/CTO_STATE.md`

**CEO Decision:** Sample datasets are required for QA testing.

---

## YOUR TASK

Provide or create sample CSV/XES files that QA can use to test:

1. **Ingestion Flow** — Upload a file, see it in project
2. **Discovery Flow** — Mine uploaded data, see process graph

---

## REQUIREMENTS

### Sample CSV File

Create a simple process mining event log CSV with these columns:

- `case_id` — Unique case identifier
- `activity` — Activity name
- `timestamp` — ISO timestamp
- `resource` (optional) — Who performed the activity

**Content:** A simple purchase order process with ~50-100 events across 10-20 cases

Example activities:

- Create Purchase Order
- Approve Purchase Order
- Send to Vendor
- Receive Goods
- Process Invoice
- Make Payment

Include some variation (different paths, some rework) to make the process graph interesting.

### Sample XES File (Optional)

If time permits, provide an XES format file as well.

---

## OUTPUT

1. Create sample CSV at `/demo/sample_purchase_order.csv`
2. Verify the file format matches what the upload expects
3. Document any format requirements in your report

---

## REPORT FORMAT

```markdown
## CTO REPORT: Sample Datasets

**Status:** Complete

**Files Created:**

- `/demo/sample_purchase_order.csv` — [X] cases, [Y] events

**Format Notes:**

- [Any requirements for column names, date formats, etc.]

**Ready for QA:** Yes/No
```

---

## CONSTRAINTS

- Keep files simple — goal is testing, not production data
- Use realistic activity names for demo value
- Include enough variety to produce interesting process graph
