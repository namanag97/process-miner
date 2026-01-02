# Glossary

> **Process Mining & Architecture Terms**
> **Last Updated:** 2026-01-02

---

## Process Mining Terms

### A

**Activity**
A single step or task in a business process. Example: "Create Order", "Approve Invoice", "Ship Product".

**Alignment**
A conformance checking technique that maps event log traces to model paths by finding optimal correspondence. More accurate but slower than token replay.

**Alpha Miner**
A classic process discovery algorithm that creates simple process models. Fast but doesn't handle noise well. Not recommended for real-world logs.

---

### C

**Case**
A single instance or execution of a business process. Also called "trace" or "process instance". Example: Order #12345 from creation to completion.

**Case ID**
Unique identifier for a case. Required column in event logs. Example: `order_id`, `patient_id`, `claim_number`.

**Conformance Checking**
Comparing actual process executions (event log) against a process model to measure how well they match.

**Cycle Time**
Total duration from case start to case end. Also called "throughput time" or "case duration".

---

### D

**Directly-Follows Graph (DFG)**
Simple process visualization showing which activities directly follow each other, with frequencies and timing.

**Discovery**
Automatically creating a process model from an event log. Main algorithms: Alpha, Inductive, Heuristics, ILP.

---

### E

**Event**
A single occurrence of an activity for a specific case. Example: "Order #12345 was approved at 2024-01-15 10:30:00 by Alice".

**Event Log**
Collection of events recording business process executions. Minimum required fields: Case ID, Activity, Timestamp.

---

### F

**Fitness**
Conformance metric: What percentage of traces can be replayed on the model? Range: 0.0 (nothing fits) to 1.0 (perfect fit).

---

### G

**Generalization**
Conformance metric: Can the model handle unseen cases? Measures overfitting.

---

### H

**Heuristics Miner**
Process discovery algorithm that uses frequency and dependency thresholds. Robust to noise, good for real-world logs.

---

### I

**Inductive Miner**
Process discovery algorithm that guarantees sound models (no deadlocks). Recommended for most use cases.

**ILP Miner (Integer Linear Programming)**
Process discovery algorithm that finds optimal models by solving optimization problems. Very slow but highest quality.

---

### O

**Object-Centric Event Log (OCEL)**
Event log with multiple object types (e.g., orders, items, deliveries) instead of single case ID. OCEL 2.0 is the latest standard.

**Object-Centric Process Mining (OCPM)**
Process mining with multiple interacting objects. Example: Order-to-cash process involving orders, items, invoices, payments.

---

### P

**Petri Net**
Mathematical model for representing concurrent processes. Used in process mining for formal analysis.

**PM4Py**
Python library for process mining. Core dependency of this backend.

**Precision**
Conformance metric: Does the model allow too much behavior? Range: 0.0 (allows everything) to 1.0 (very precise).

**Process Model**
Formal representation of a business process. Formats: Petri net, BPMN, Process tree, DFG.

**Process Tree**
Hierarchical process model representation. Easier to understand than Petri nets.

---

### R

**Resource**
Person or system executing an activity. Example: "Alice", "Approval Bot", "Warehouse System".

**Rework**
Repeating an activity in the same case. Indicates inefficiency or quality issues.

---

### S

**Service Time**
Time spent actively working on an activity (excluding waiting time).

**Simplicity**
Conformance metric: How complex is the model? Simpler models are easier to understand.

**Soundness**
Property of process models: Every case can complete without deadlocks or orphan activities.

---

### T

**Timestamp**
When an event occurred. Required column in event logs. Must be parseable as datetime.

**Token Replay**
Conformance checking technique that simulates process execution. Fast but less accurate than alignments.

**Trace**
Synonym for "case". Sequence of events for a single process instance.

---

### V

**Variant**
Unique sequence of activities in a process. Example: "Create → Approve → Ship → Complete" is one variant.

**Variant Analysis**
Analyzing which process paths are most common. Used for process understanding and filtering.

---

### W

**Waiting Time**
Time between activities (excluding service time). Main source of process inefficiency.

**XES (eXtensible Event Stream)**
Standard XML format for event logs. Alternative to CSV.

---

## Architecture Terms

### A

**Aggregate (DDD)**
Domain-Driven Design pattern: Cluster of entities treated as a single unit. Example: `DatasetAggregate` contains cases and events.

**API Layer**
Outermost layer in clean architecture. Contains HTTP routers, request validation, response formatting.

**Async/Await**
Python pattern for non-blocking I/O. All database queries and external calls use async.

---

### C

**Cache-Aside**
Caching pattern: Check cache first, load from DB on miss, write to cache.

**Circuit Breaker**
Resilience pattern: Stop calling failing service temporarily to allow recovery. Used for PM4Py operations.

**Clean Architecture**
Software architecture pattern with dependency rule: inner layers never depend on outer layers.

**CORS (Cross-Origin Resource Sharing)**
HTTP headers allowing frontend (different domain) to call backend API.

---

### D

**Data Layer**
Layer containing SQLAlchemy ORM models, repositories, database session management.

**Dependency Injection**
Pattern for providing dependencies to functions. FastAPI uses this extensively.

**Domain Event**
Event representing something that happened in the domain. Example: "DatasetUploaded", "ModelDiscovered".

**Domain Layer**
Core layer with pure business logic. No external dependencies (no FastAPI, no SQLAlchemy, no PM4Py).

**DTO (Data Transfer Object)**
Object for transferring data between layers. Pydantic models serve as DTOs.

**DuckDB**
Embedded OLAP database. Used for 10x faster CSV ingestion via columnar processing.

---

### E

**Entity (DDD)**
Domain object with identity. Example: `Dataset`, `ProcessCase`, `ProcessEvent`.

---

### I

**Idempotency**
Property where operation produces same result if repeated. POST requests use idempotency keys.

**Infrastructure Layer**
Layer for external services: Redis, Prometheus, OpenTelemetry, Celery.

---

### J

**JWT (JSON Web Token)**
Standard for authentication tokens. Contains claims (user_id, org_id, expiration).

---

### M

**Middleware**
Code that runs before/after HTTP requests. Examples: logging, authentication, CORS.

**Multi-Tenancy**
Architecture supporting multiple customers (organizations) in one system. Hierarchy: Org → Workspace → Project → Dataset.

---

### O

**ORM (Object-Relational Mapping)**
SQLAlchemy pattern for mapping database tables to Python classes.

---

### P

**Pydantic**
Python library for data validation and serialization. Used for request/response schemas.

---

### R

**Repository Pattern**
Abstraction for data access. Example: `DatasetRepository` hides SQLAlchemy details from services.

**RFC 7807**
Standard for HTTP error responses ("Problem Details"). Defines JSON error format.

**RBAC (Role-Based Access Control)**
Authorization model: users have roles (owner, admin, member, viewer) with different permissions.

---

### S

**Service Layer**
Layer containing business logic, orchestration, PM4Py wrappers. Calls domain and data layers.

**SSE (Server-Sent Events)**
One-way real-time communication from server to client. Used for live log streaming.

**Structlog**
Python library for structured logging (key-value pairs instead of strings).

---

### V

**Value Object (DDD)**
Domain object without identity, defined by its attributes. Example: `TimeRange`, `ActivitySequence`.

---

## File Formats

**CSV (Comma-Separated Values)**
Text file format for tabular data. Most common event log format.

**XES (eXtensible Event Stream)**
XML standard for event logs. More expressive than CSV but larger files.

**OCEL (Object-Centric Event Log)**
JSON/SQLite format for multi-object event logs. OCEL 2.0 is current standard.

**BPMN (Business Process Model and Notation)**
Graphical notation for process models. Industry standard.

**DOT (Graphviz)**
Text format for graph visualization. Used for Petri nets and DFGs.

---

## Metrics & Observability

**Prometheus**
Open-source monitoring system. Scrapes `/metrics` endpoint for time-series data.

**OpenTelemetry**
Observability framework for traces, metrics, logs. Exports to Jaeger, Zipkin.

**Request ID**
Unique identifier for each HTTP request. Propagated through logs for correlation.

**Correlation ID**
Synonym for Request ID. Used in distributed tracing.

---

## Database Terms

**Alembic**
Database migration tool for SQLAlchemy. Manages schema changes.

**SQLite**
Embedded SQL database. Used for development (production should use PostgreSQL).

**PostgreSQL**
Production-grade SQL database. Recommended for >10 concurrent users.

**Connection Pool**
Reusing database connections instead of creating new ones. Improves performance.

**Eager Loading**
Loading related data in single query instead of N+1 queries. Example: `selectinload()`.

---

## Acronyms

| Acronym | Meaning |
|---------|---------|
| **ACID** | Atomicity, Consistency, Isolation, Durability (database properties) |
| **API** | Application Programming Interface |
| **ASGI** | Asynchronous Server Gateway Interface |
| **CRUD** | Create, Read, Update, Delete |
| **DDD** | Domain-Driven Design |
| **DFG** | Directly-Follows Graph |
| **DTO** | Data Transfer Object |
| **ELK** | Elasticsearch, Logstash, Kibana (log stack) |
| **GDPR** | General Data Protection Regulation |
| **HA** | High Availability |
| **ILP** | Integer Linear Programming |
| **JSON** | JavaScript Object Notation |
| **JWT** | JSON Web Token |
| **OCPM** | Object-Centric Process Mining |
| **OCEL** | Object-Centric Event Log |
| **OLAP** | Online Analytical Processing |
| **ORM** | Object-Relational Mapping |
| **PII** | Personally Identifiable Information |
| **RBAC** | Role-Based Access Control |
| **REST** | Representational State Transfer |
| **RFC** | Request for Comments (IETF standards) |
| **RTO** | Recovery Time Objective |
| **RPO** | Recovery Point Objective |
| **SaaS** | Software as a Service |
| **SDK** | Software Development Kit |
| **SQL** | Structured Query Language |
| **SSE** | Server-Sent Events |
| **TTL** | Time To Live (cache expiration) |
| **UUID** | Universally Unique Identifier |
| **XES** | eXtensible Event Stream |

---

## External Services

**Redis**
In-memory data store. Used for caching and Celery task queue.

**Celery**
Distributed task queue. Used for background jobs (long-running PM4Py operations).

**Flower**
Web UI for monitoring Celery workers.

**Jaeger / Zipkin**
Distributed tracing backends. Receive OpenTelemetry traces.

**Grafana**
Visualization platform for Prometheus metrics.

---

## Development Tools

**pytest**
Python testing framework. Used for unit and integration tests.

**ruff**
Rust-based Python linter and formatter. 10-100x faster than Black/Flake8.

**mypy**
Static type checker for Python. Enforces type hints.

**bandit**
Security linter for Python. Detects common vulnerabilities.

**Uvicorn**
ASGI server for running FastAPI. Production uses Gunicorn with Uvicorn workers.

**Alembic**
Database migration tool. Manages schema changes.

**Poetry / pip-tools**
Python dependency management. Project uses pip with `pyproject.toml`.

---

## See Also

- [Architecture Overview](../00-overview/architecture.md) - System architecture
- [Tech Stack](../00-overview/tech-stack.md) - Technologies and dependencies
- [Decision Log](./decision-log.md) - Architectural decisions
- [API Reference](http://localhost:8001/docs) - Interactive API documentation

---

## Contributing

Missing a term? Submit a pull request or create an issue!

**Format:**
```markdown
### [Term Name]
[Definition in 1-3 sentences]

[Optional: Example or usage]
```
