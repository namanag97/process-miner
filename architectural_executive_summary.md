# EXECUTIVE ARCHITECTURAL SUMMARY (ARIA PHASE 2)

A synthesized summary of critical architectural, ontological, and performance gaps identified in the current codebase.

## 1. Core Domain & Semantics (Ontology)

- **Object-Centricity Gap**: The system treats Object-Centric (OCEL) data as a bolted-on feature rather than the core event representation. This forces a "Flattening Tax" where rich M:N relationships (Order -> Items -> Shipments) are crushed into simple linear cases, losing convergence patterns.
- **Semantic Anemia**: Activities are currently simple string labels. The domain model fails to represent Activities as rich objects (with SLA, Cost, Owner), making the system "domain blind."
- **Conformance Honesty**: The conformance service silently falls back to heuristic "Token Replay" when rigorous "Alignments" fail, presenting users with "Fake Fitness" scores rather than admitting analytical uncertainty.
- **Process Semantics**: The system lacks a Lifecycle Model (Start/Complete), making it impossible to distinguish "Working Time" from "Waiting Time" accurately.

## 2. System Architecture & Data Engineering

- **Transaction Script Pattern**: Business logic leaks into API Routers (`processes.py`) instead of residing in a unified Service Layer. This leads to code duplication and thin "Anemic Models" that are merely data containers.
- **Database Coupling**: Services run raw SQLAlchemy queries, creating a hard coupling to the relational schema. Transitioning to a Graph DB or NoSQL store would require rewriting every service.
- **Batch-Only Pipeline**: The architecture is strictly batch-based (upload -> wait -> analyze) with no "Streaming" capability. It is a "History Book," not a "Cockpit" for real-time management.
- **Missing Data Lineage**: "Filtered Logs" are new database rows with no link to their source. There is no audit trail or "Recipe" to prove how an insight was derived.
- **State Drift Risks**: Key metrics (like `event_count`) are denormalized without transactional safeguards, risking situations where the log header contradicts the actual row count.

## 3. Performance & Efficiency

- **The "Object Tax"**: Data is converted 4 times for every operation (SQL -> Dict -> ORM -> PM4Py). 90% of CPU time is spent on data marshalling, not actual mining.
- **Serialization Suicide**: Models are stored as Python `pickle` blobs in the DB. This is slow, insecure, version-fragile, and opaque to SQL queries.
- **Parsing Bottleneck**: Ingestion iterates over millions of rows in native Python loops. A Vectorized/Columnar approach (Arrow/DuckDB) is needed to respect hardware limits.
- **Bloated Stack**: The system deploys heavy distributed tools (Celery, Redis) for a workload that is currently sequential, adding "Premature Scaling" complexity without the benefits.

## 4. AI, Analytics & Simulation

- **Prescriptive Void**: The AI predicts delays (Predictive) but offers no fixes (Prescriptive). It is a "Passive Observer" that warns of failure but provides no steering wheel.
- **Concept Drift Ignorance**: Models are trained once on static history. The system lacks "Drift Detection," meaning it will confidently apply outdated logic to new process behaviors.
- **Simulation Fallacy**: The simulation engine assumes linear human scaling (10 people = 2x output of 5), ignoring "Queuing Theory" and burnout, creating a "Mirage of Certainty" for decision makers.
- **Resume AI**: The predictive layer uses basic XGBoost on CSVs without deep feature learning (Embeddings/RNNs), failing to capture the complex sequential nature of process data.

## 5. UX & Organizational Social

- **Organizational Echo Chamber**: Social mining blindly maps system handovers (User->Bot) as human collaboration, failing to filter "System Noise" to reveal the true human network.
- **Actionless Workflows**: The system detects problems but has no "Webhook" or "Trigger" capability to fix them automatically.
- **Metric Confusion**: The UI uses color for "Vibe" rather than "Meaning." Critical DFG paths rely on Red/Green scales, ignoring accessibility standards for color-blind executives.
- **The 13" Economy**: The UI is optimized for large monitors. Fixed sidebars and "Fat Headers" make the tool unusable on standard enterprise laptops.

## 6. Privacy, Security & Ethics

- **The Panopticon Effect**: Employee data is stored and analyzed with real names and exact timestamps. There is no anonymization layer, turning the tool into potential "Spyware" and risking GDPR violations.
- **Identity Void**: The system relies on a hardcoded "Process Analyst" stub user. The lack of an abstract Identity Provider makes implementing "Row-Level Security" or "Tenant Isolation" impossible without a rewrite.
- **The Export Lie**: Data export buttons only download the "Visible Page" of the table, not the full dataset, creating a false sense of completeness for compliance auditors.

## 7. Frontend/Backend Coupling

- **Interface Segregation Violation**: The "Design System" library imports the entire Business SDK. A simple Button component now carries the weight of the entire Mining engine.
- **Contract Drift**: API types are manually duplicated in TypeScript and Python. There is no "Single Source of Truth" (OpenAPI codegen), guaranteeing that the frontend will eventually break due to a backend change.
- **Leaky Ingestion Logic**: File validation rules (extensions, mime-types) live in the Web Router, making them inaccessible to future CLI or Bulk Ingestion tools.
