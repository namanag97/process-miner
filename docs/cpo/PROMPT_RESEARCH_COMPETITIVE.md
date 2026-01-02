# RESEARCH TASK: Competitive Benchmarking — Process Mining MVP

## Your Mission

Research the competitive landscape for process mining platforms. CPO needs to understand what "good" looks like so we can benchmark ATLAS MVP against industry standards.

---

## Research Questions

### 1. Celonis (Market Leader)

- [ ] What is their core Ingestion flow? (Upload → What happens?)
- [ ] What file formats do they support?
- [ ] What does their Process Discovery visualization look like?
- [ ] What's their simplest user journey for a new user?
- [ ] What features are in their "starter" vs "enterprise" tiers?

### 2. Other Competitors

| Competitor            | Website         | Focus                     | Key Differentiator        |
| --------------------- | --------------- | ------------------------- | ------------------------- |
| Celonis               | celonis.com     | Enterprise                | Market leader, AI-powered |
| Signavio              | signavio.com    | Process modeling + mining | SAP acquisition           |
| UiPath Process Mining | uipath.com      | RPA-focused               | Automation integration    |
| Apromore              | apromore.com    | Academic/Open source      | Research-grade algorithms |
| Minit                 | minit.io        | Mid-market                | Simplicity focus          |
| ProcessGold           | processgold.com | Now UiPath                | Was standalone            |

### 3. MVP Feature Comparison

For each competitor's starter/free tier:

| Feature       | Celonis | Signavio | Apromore | ATLAS (Current) |
| ------------- | ------- | -------- | -------- | --------------- |
| CSV Upload    |         |          |          | ✅              |
| XES Upload    |         |          |          | ✅              |
| Process Graph |         |          |          | 🟡              |
| Variants View |         |          |          | 🔴              |
| Conformance   |         |          |          | 🔴              |
| Export (BPMN) |         |          |          | ❌              |
| NL Queries    |         |          |          | ❌              |

### 4. UX Benchmarks

What do best-in-class process mining UIs include:

- [ ] Onboarding flow (guided tour?)
- [ ] Sample datasets included?
- [ ] Interactive tutorials?
- [ ] Help documentation inline?
- [ ] Error handling quality?

---

## Research Sources

- Product demo videos on YouTube
- Official documentation
- G2 Crowd / Gartner reviews
- Free trial experiences (if available)
- Academic papers comparing tools

---

## Output Format

### Competitive Analysis Summary

```markdown
## Competitive Landscape

### Market Leader: Celonis

**Core Flow:**
[Describe their simplest user journey]

**Key Features (Starter):**

-
-
- **UX Observations:**

-
-

### Comparison Matrix

| Feature | Celonis | Signavio | Apromore | ATLAS |
| ------- | ------- | -------- | -------- | ----- |
|         |         |          |          |       |

### Gap Analysis

**Features ATLAS is missing vs. MVP standard:**

1.
2.
3.

**Features where ATLAS matches/exceeds:**

1.
2.

### Recommended Additions for MVP

Based on competitive analysis:

1. [Feature] — Why: [Reason]
2.
3.

### Recommended Deferrals (v1.1+)

Features competitors have but not required for MVP:

1.
2.
```

---

## Deliver To

**Report to:** CPO
**Create:** `/docs/cpo/COMPETITIVE_ANALYSIS.md`
