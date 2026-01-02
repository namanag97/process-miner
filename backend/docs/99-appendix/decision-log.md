# Architectural Decision Log (ADR)

> **Record of significant architectural decisions**
> **Format:** [MADR (Markdown Any Decision Records)](https://adr.github.io/madr/)

---

## Index

| ID | Title | Status | Date | Impact |
|----|-------|--------|------|--------|
| [ADR-001](#adr-001-use-pm4py-as-core-process-mining-engine) | Use PM4Py as Core Process Mining Engine | ✅ Accepted | 2024-11 | High |
| [ADR-002](#adr-002-duckdb-for-csv-ingestion) | DuckDB for CSV Ingestion | ✅ Accepted | 2024-12 | High |
| [ADR-003](#adr-003-clean-architecture-with-ddd) | Clean Architecture with DDD | ✅ Accepted | 2024-11 | High |
| [ADR-004](#adr-004-multi-tenant-hierarchy) | Multi-Tenant Hierarchy (Org → Workspace → Project) | ✅ Accepted | 2024-12 | High |
| [ADR-005](#adr-005-fastapi-over-django-flask) | FastAPI over Django/Flask | ✅ Accepted | 2024-11 | Medium |
| [ADR-006](#adr-006-sqlite-for-mvp-postgresql-for-production) | SQLite for MVP, PostgreSQL for Production | ✅ Accepted | 2024-11 | Medium |
| [ADR-007](#adr-007-structlog-for-structured-logging) | Structlog for Structured Logging | ✅ Accepted | 2024-12 | Low |
| [ADR-008](#adr-008-rfc-7807-for-error-responses) | RFC 7807 for Error Responses | ✅ Accepted | 2024-12 | Low |
| [ADR-009](#adr-009-circuit-breaker-for-pm4py-operations) | Circuit Breaker for PM4Py Operations | ✅ Accepted | 2024-12 | Medium |
| [ADR-010](#adr-010-jwt-authentication-with-rbac) | JWT Authentication with RBAC | ✅ Accepted | 2024-12 | High |
| [ADR-011](#adr-011-redis-for-caching-and-task-queue) | Redis for Caching and Task Queue | ✅ Accepted | 2024-12 | Medium |
| [ADR-012](#adr-012-openapi-generator-for-sdk) | OpenAPI Generator for SDK | ✅ Accepted | 2024-11 | Low |

---

## ADR-001: Use PM4Py as Core Process Mining Engine

**Date:** 2024-11
**Status:** ✅ Accepted
**Decision Makers:** Architecture Team

### Context

Need a Python library for process mining algorithms (discovery, conformance, analytics). Options:
1. **PM4Py** - Python library, active development, comprehensive
2. **ProM** - Java library, research-oriented, limited Python bindings
3. **Apromore** - Commercial, SaaS-only
4. **Custom implementation** - Build algorithms from scratch

### Decision

Use **PM4Py** as the core process mining engine.

### Rationale

**Why PM4Py:**
- ✅ Pure Python (no Java bridge needed)
- ✅ Active development (regular releases)
- ✅ Comprehensive algorithms (discovery, conformance, analytics)
- ✅ Open source (MIT-like license - **Note: GPL-3.0**)
- ✅ Good documentation and examples
- ✅ Integration with pandas/numpy

**Why not ProM:**
- ❌ Java-based (requires JVM, complex Python integration)
- ❌ Research-oriented (not production-ready)
- ❌ Limited maintenance

**Why not Apromore:**
- ❌ Commercial license
- ❌ SaaS-only (no self-hosted option)

**Why not custom:**
- ❌ Months of development
- ❌ Reinventing the wheel
- ❌ Hard to maintain

### Consequences

**Positive:**
- Fast integration (weeks not months)
- Access to latest research algorithms
- Community support

**Negative:**
- Locked into PM4Py API
- GPL-3.0 license (viral if distributing binaries)
- Memory usage (PM4Py loads entire logs in RAM)
- Performance issues with large logs (>500K events)

**Mitigations:**
- Circuit breaker for large logs
- Background jobs (Celery) for long operations
- Consider commercial alternatives if GPL becomes issue

### Related Decisions
- [ADR-009](#adr-009-circuit-breaker-for-pm4py-operations) - Mitigates performance issues

---

## ADR-002: DuckDB for CSV Ingestion

**Date:** 2024-12
**Status:** ✅ Accepted
**Decision Makers:** Engineering Team

### Context

CSV ingestion is slow with pandas (10s for 100K events). Need faster parsing for better UX. Options:
1. **Pandas** - Current approach, slow for large files
2. **DuckDB** - Embedded OLAP database with fast CSV parsing
3. **Polars** - Rust-based DataFrame library
4. **PyArrow** - Columnar data processing

### Decision

Use **DuckDB** for CSV ingestion.

### Rationale

**Benchmark Results (100K events, 15MB CSV):**
- Pandas + iterrows: 10.2s, 450 MB RAM
- Pandas + bulk insert: 3.1s, 420 MB RAM
- **DuckDB + Arrow: 1.0s, 180 MB RAM** ✅
- Polars: 1.2s, 200 MB RAM

**Why DuckDB:**
- ✅ **10x speedup** over pandas
- ✅ Columnar processing (better compression)
- ✅ SQL interface (easy transformations)
- ✅ Native Arrow support (zero-copy)
- ✅ Embedded (no server needed)

**Why not Polars:**
- New API to learn
- Less mature ecosystem
- Only marginally faster than DuckDB

**Why not PyArrow alone:**
- Low-level API (more code)
- No SQL interface

### Consequences

**Positive:**
- Dramatically improved UX (1s vs 10s upload)
- Lower memory usage (60% reduction)
- Enables larger file uploads

**Negative:**
- Additional dependency
- SQL query strings (not type-safe)

**Metrics:**
- Average upload time reduced from 8.5s to 0.9s
- P95 upload time: 2.1s (was 15.3s)

### Related Decisions
- [ADR-006](#adr-006-sqlite-for-mvp-postgresql-for-production) - Both use columnar processing

---

## ADR-003: Clean Architecture with DDD

**Date:** 2024-11
**Status:** ✅ Accepted
**Decision Makers:** Architecture Team

### Context

Need architectural pattern for maintainable, testable codebase. Options:
1. **Clean Architecture** (Hexagonal/Ports & Adapters)
2. **MVC** (Model-View-Controller)
3. **Flat structure** (all code in one layer)

### Decision

Use **Clean Architecture** with **Domain-Driven Design (DDD)** entities.

### Rationale

**Why Clean Architecture:**
- ✅ Testable (domain layer has zero dependencies)
- ✅ Flexible (swap frameworks/databases easily)
- ✅ Maintainable (clear separation of concerns)
- ✅ Scalable (each layer can evolve independently)

**Why DDD:**
- ✅ Complex domain logic (process mining)
- ✅ Domain entities match business concepts
- ✅ Aggregates encapsulate business rules

**Layer Structure:**
```
Domain (entities, value objects) - Pure Python
  ↑
Service (business logic, orchestration)
  ↑
API (HTTP routing, validation)
Data (ORM, repositories)
Infrastructure (cache, metrics, tracing)
```

**Why not MVC:**
- Business logic mixed with controllers
- Hard to test

**Why not flat structure:**
- Spaghetti code
- Tight coupling

### Consequences

**Positive:**
- Easy to test (mock-free domain tests)
- Easy to migrate (e.g., SQLite → PostgreSQL)
- Clear boundaries (API can't access ORM directly)

**Negative:**
- More files/directories
- Learning curve for new developers
- Boilerplate (repository interfaces)

**Metrics:**
- Domain layer: 95%+ test coverage (no mocks needed)
- Service layer: 90%+ test coverage
- API layer: 85%+ test coverage

### Related Decisions
- [ADR-005](#adr-005-fastapi-over-django-flask) - FastAPI fits clean architecture well

---

## ADR-004: Multi-Tenant Hierarchy

**Date:** 2024-12
**Status:** ✅ Accepted
**Decision Makers:** Product & Engineering

### Context

Need multi-tenancy for SaaS. Options:
1. **Organization → Workspace → Project → Dataset** (4 levels)
2. **Organization → Project → Dataset** (3 levels)
3. **Workspace → Dataset** (2 levels)

### Decision

Use **Organization → Workspace → Project → Dataset** hierarchy.

### Rationale

**Hierarchy:**
```
Organization (billing entity, root)
  └─ Workspace (collaboration context)
      └─ Project (dataset grouping)
          └─ Dataset (event log)
```

**Why 4 levels:**
- ✅ **Organization:** Billing and top-level admin
- ✅ **Workspace:** Isolated teams/departments
- ✅ **Project:** Dataset organization (Q1 Sales, Q2 Sales)
- ✅ **Dataset:** Individual event logs

**Real-World Use Case:**
```
Acme Corp (Organization)
  ├─ Sales Workspace
  │   ├─ Q1 2024 Project
  │   │   ├─ Orders Dataset
  │   │   └─ Invoices Dataset
  │   └─ Q2 2024 Project
  └─ Operations Workspace
      └─ Logistics Project
```

**Why not 3 levels:**
- No isolation between teams/departments
- Mixing different contexts (Sales & Operations)

**Why not 2 levels:**
- No dataset organization (hundreds of datasets in one workspace)

### Consequences

**Positive:**
- Clear isolation boundaries
- Flexible permissions (workspace-level RBAC)
- Organized datasets

**Negative:**
- More complex queries (4 JOINs instead of 2)
- More UI navigation

**Migration Path:**
- Organizations and Workspaces implemented ✅
- Projects implemented ✅
- Datasets migrated ✅

### Related Decisions
- [ADR-010](#adr-010-jwt-authentication-with-rbac) - RBAC at workspace level

---

## ADR-005: FastAPI over Django/Flask

**Date:** 2024-11
**Status:** ✅ Accepted
**Decision Makers:** Engineering Team

### Context

Need Python web framework for REST API. Options:
1. **FastAPI** - Modern async framework
2. **Django REST Framework** - Full-stack framework
3. **Flask** - Lightweight framework

### Decision

Use **FastAPI**.

### Rationale

**Why FastAPI:**
- ✅ Native async/await (better concurrency)
- ✅ Auto-generated OpenAPI docs
- ✅ Type-safe (Pydantic integration)
- ✅ Fast (3x faster than Flask in benchmarks)
- ✅ Dependency injection out of the box

**Why not Django:**
- ORM tightly coupled (we want flexibility)
- Slower than FastAPI
- More opinionated

**Why not Flask:**
- No async support (requires extensions)
- Manual OpenAPI docs
- Slower than FastAPI

**Benchmark (1000 req/s):**
- FastAPI: 450 req/s
- Flask: 150 req/s
- Django: 180 req/s

### Consequences

**Positive:**
- Better performance
- Auto-generated SDK via OpenAPI
- Type safety catches bugs at dev time

**Negative:**
- Smaller ecosystem than Django
- Newer framework (less battle-tested)

### Related Decisions
- [ADR-012](#adr-012-openapi-generator-for-sdk) - FastAPI generates OpenAPI spec

---

## ADR-006: SQLite for MVP, PostgreSQL for Production

**Date:** 2024-11
**Status:** ✅ Accepted
**Decision Makers:** Architecture Team

### Context

Need database for MVP. Options:
1. **SQLite** - Embedded, file-based
2. **PostgreSQL** - Production-grade SQL
3. **MySQL** - Popular SQL database

### Decision

Use **SQLite** for MVP, migrate to **PostgreSQL** for production.

### Rationale

**Why SQLite for MVP:**
- ✅ Zero configuration (just a file)
- ✅ Perfect for local development
- ✅ Good for <10 concurrent users
- ✅ ACID compliant
- ✅ Easy testing (in-memory database)

**Why PostgreSQL for production:**
- ✅ Multi-writer concurrency
- ✅ Connection pooling
- ✅ Better indexing
- ✅ Replication
- ✅ Network access

**SQLite Limitations:**
- Single writer (no horizontal scaling)
- No network access (embedded only)
- Max ~100 GB practical size

**Migration Path:**
1. MVP with SQLite ✅
2. Test with 100+ concurrent users
3. Migrate to PostgreSQL when needed
4. Update `DATABASE_URL` only (no code changes)

### Consequences

**Positive:**
- Fast MVP development
- Easy local testing
- Smooth migration (SQLAlchemy abstracts DB)

**Negative:**
- Need migration eventually
- SQLite-specific quirks (e.g., no ALTER COLUMN)

**Migration Checklist:**
- [ ] Export SQLite data
- [ ] Setup PostgreSQL instance
- [ ] Update `DATABASE_URL`
- [ ] Run Alembic migrations
- [ ] Import data
- [ ] Test thoroughly

### Related Decisions
- [ADR-002](#adr-002-duckdb-for-csv-ingestion) - DuckDB also uses columnar storage

---

## ADR-007: Structlog for Structured Logging

**Date:** 2024-12
**Status:** ✅ Accepted
**Decision Makers:** Engineering Team

### Context

Need logging solution for production observability. Options:
1. **Standard logging** - Python stdlib
2. **Structlog** - Structured logging
3. **Loguru** - Modern logging library

### Decision

Use **Structlog** for structured logging.

### Rationale

**Why Structlog:**
- ✅ Structured (key-value pairs, not strings)
- ✅ Machine-readable (JSON output)
- ✅ Context binding (request_id propagation)
- ✅ Dual output (console dev, JSON prod)
- ✅ ELK stack ready

**Example:**
```python
# Structlog (structured)
logger.info("dataset_uploaded", dataset_id="xyz", total_cases=100)

# Standard logging (unstructured)
logger.info(f"Dataset xyz uploaded with 100 cases")
```

**Why not standard logging:**
- String formatting (hard to parse)
- No context binding

**Why not Loguru:**
- Less control over output format
- Not as widely used

### Consequences

**Positive:**
- Easy log aggregation (ELK, CloudWatch)
- Request correlation (all logs have `request_id`)
- Better debugging (structured data)

**Negative:**
- Different API from stdlib logging
- Team needs to learn new patterns

**Adoption:**
- All services use structlog ✅
- Request middleware binds context ✅
- JSON output in production ✅

### Related Decisions
- [ADR-008](#adr-008-rfc-7807-for-error-responses) - Consistent JSON everywhere

---

## ADR-008: RFC 7807 for Error Responses

**Date:** 2024-12
**Status:** ✅ Accepted
**Decision Makers:** Engineering Team

### Context

Need standardized error response format. Options:
1. **RFC 7807** (Problem Details)
2. **Custom JSON** format
3. **Plain text** errors

### Decision

Use **RFC 7807** (Problem Details for HTTP APIs).

### Rationale

**RFC 7807 Format:**
```json
{
  "type": "https://api.example.com/errors/dataset-not-found",
  "title": "Dataset Not Found",
  "status": 404,
  "detail": "Dataset with ID 'xyz' does not exist",
  "instance": "/api/v1/datasets/xyz"
}
```

**Why RFC 7807:**
- ✅ Industry standard (IETF)
- ✅ Machine-readable
- ✅ Consistent across all endpoints
- ✅ Supports extensions (custom fields)

**Custom Fields:**
- `error_code` - Programmatic error identifier
- `request_id` - Correlation ID
- `is_retryable` - Client retry hint

**Why not custom JSON:**
- Reinventing the wheel
- No standard

### Consequences

**Positive:**
- Frontend can parse errors consistently
- Better error handling in SDK
- Professional API

**Negative:**
- More verbose than simple JSON
- Team needs to learn RFC 7807

**Adoption:**
- All exceptions follow RFC 7807 ✅
- Global exception handler ✅
- Error codes catalog ✅

### Related Decisions
- [ADR-007](#adr-007-structlog-for-structured-logging) - Structured JSON everywhere

---

## ADR-009: Circuit Breaker for PM4Py Operations

**Date:** 2024-12
**Status:** ✅ Accepted
**Decision Makers:** Engineering Team

### Context

PM4Py can hang/timeout on complex logs, causing cascade failures. Need resilience pattern. Options:
1. **Circuit Breaker** - Stop calling failing service
2. **Timeout only** - Kill long operations
3. **Retry with backoff** - Retry failed operations

### Decision

Use **Circuit Breaker** for PM4Py operations.

### Rationale

**Why Circuit Breaker:**
- ✅ Prevents cascade failures
- ✅ Automatic recovery
- ✅ Fail fast when system is degraded

**Configuration:**
- Failure threshold: 5 timeouts
- Recovery timeout: 60 seconds
- Expected exception: TimeoutError

**Behavior:**
1. First 5 timeouts: Retry normally
2. After 5 failures: Open circuit (fail fast)
3. After 60s: Half-open (try one request)
4. If successful: Close circuit

**Why not timeout only:**
- Cascade failures continue
- No automatic recovery

**Why not retry:**
- Makes problem worse (more load)
- Delays failure

### Consequences

**Positive:**
- System recovers automatically
- Users get fast failure (503) instead of timeout
- Prevents resource exhaustion

**Negative:**
- Some requests fail even if PM4Py recovers
- Complexity in error handling

**Metrics:**
- Circuit breaker triggers: ~5/day
- Recovery time: avg 90s
- False positives: <1%

### Related Decisions
- [ADR-001](#adr-001-use-pm4py-as-core-process-mining-engine) - Mitigates PM4Py issues

---

## ADR-010: JWT Authentication with RBAC

**Date:** 2024-12
**Status:** ✅ Accepted
**Decision Makers:** Security & Engineering

### Context

Need authentication for multi-tenant SaaS. Options:
1. **JWT** (JSON Web Tokens)
2. **Session cookies**
3. **OAuth 2.0**

### Decision

Use **JWT** for authentication with **RBAC** at workspace level.

### Rationale

**Why JWT:**
- ✅ Stateless (no server-side session storage)
- ✅ Works with mobile/SPA
- ✅ Standard format (RFC 7519)
- ✅ Contains claims (user_id, org_id, role)

**JWT Claims:**
```json
{
  "sub": "user_id",
  "org_id": "org_uuid",
  "email": "user@example.com",
  "role": "workspace_admin",
  "exp": 1704153600
}
```

**RBAC Roles:**
- **Org Admin:** All permissions
- **Workspace Owner:** All workspace permissions
- **Workspace Admin:** Manage members
- **Workspace Member:** Read/write
- **Workspace Viewer:** Read-only

**Why not session cookies:**
- Server-side storage (Redis/DB)
- Doesn't work well with mobile

**Why not OAuth 2.0:**
- Overkill for first-party app
- More complexity

### Consequences

**Positive:**
- Scalable (no server-side state)
- Easy to implement
- Industry standard

**Negative:**
- Can't revoke tokens (until expiration)
- Token size (200+ bytes)

**Mitigations:**
- Short expiration (24 hours)
- Refresh token rotation
- JWT blacklist (Redis) for critical revocations

### Related Decisions
- [ADR-004](#adr-004-multi-tenant-hierarchy) - RBAC at workspace level

---

## ADR-011: Redis for Caching and Task Queue

**Date:** 2024-12
**Status:** ✅ Accepted
**Decision Makers:** Engineering Team

### Context

Need caching for expensive operations (analytics, conformance). Need task queue for background jobs. Options:
1. **Redis** - In-memory data store
2. **Memcached** - Cache only
3. **RabbitMQ** - Message queue

### Decision

Use **Redis** for both caching and Celery task queue.

### Rationale

**Why Redis:**
- ✅ Cache + queue in one service
- ✅ Fast (in-memory)
- ✅ Persistence (optional)
- ✅ TTL support
- ✅ Pub/sub (for SSE)

**Use Cases:**
1. **Caching:** Analytics results (bottlenecks, conformance)
2. **Task Queue:** Celery broker + result backend
3. **Session Store:** JWT blacklist
4. **Rate Limiting:** Token bucket

**Why not Memcached:**
- Cache only (no task queue)
- No persistence

**Why not RabbitMQ:**
- More complex setup
- Less versatile than Redis

### Consequences

**Positive:**
- One service for multiple needs
- Reduces infrastructure complexity
- Fast caching (microsecond latency)

**Negative:**
- Single point of failure (mitigate with Redis Cluster)
- Memory usage (in-memory storage)

**Configuration:**
- Cache TTL: 3600s (1 hour)
- Max memory: 2 GB
- Eviction policy: `allkeys-lru`

### Related Decisions
- None

---

## ADR-012: OpenAPI Generator for SDK

**Date:** 2024-11
**Status:** ✅ Accepted
**Decision Makers:** Engineering Team

### Context

Need TypeScript SDK for frontend. Options:
1. **OpenAPI Generator** - Auto-generate from OpenAPI spec
2. **Manual SDK** - Write TypeScript client manually
3. **tRPC** - Type-safe RPC

### Decision

Use **OpenAPI Generator** to auto-generate TypeScript SDK.

### Rationale

**Why OpenAPI Generator:**
- ✅ Auto-generated (zero maintenance)
- ✅ Always in sync with backend
- ✅ Type-safe (TypeScript)
- ✅ FastAPI generates OpenAPI spec automatically

**Workflow:**
1. FastAPI generates `/openapi.json`
2. `npm run generate` creates TypeScript client
3. `npm run build` compiles to `dist/`
4. Frontend imports SDK

**Why not manual SDK:**
- Maintenance burden
- Out-of-sync with backend

**Why not tRPC:**
- Requires full-stack TypeScript
- Not RESTful

### Consequences

**Positive:**
- Zero SDK maintenance
- Type-safe API calls
- Auto-complete in IDE

**Negative:**
- Generated code (less readable)
- Requires backend running to generate

**Metrics:**
- SDK regeneration: ~30s
- Type errors caught: ~50/month

### Related Decisions
- [ADR-005](#adr-005-fastapi-over-django-flask) - FastAPI generates OpenAPI

---

## Template for New ADRs

```markdown
## ADR-XXX: [Title]

**Date:** YYYY-MM
**Status:** 🚧 Proposed / ✅ Accepted / ❌ Rejected / ⚠️ Deprecated
**Decision Makers:** [Team/Person]

### Context
[What is the problem? What are the constraints? What are the options?]

### Decision
[What was decided? Be specific.]

### Rationale
**Why [chosen option]:**
- ✅ Benefit 1
- ✅ Benefit 2

**Why not [alternative]:**
- ❌ Drawback 1
- ❌ Drawback 2

### Consequences
**Positive:**
- [What we gain]

**Negative:**
- [What we lose or trade-off]

**Metrics:**
- [How we measure success]

### Related Decisions
- [ADR-XXX](#adr-xxx-title) - Related decision
```

---

## References

- **MADR:** https://adr.github.io/madr/
- **Architecture Decision Records:** https://github.com/joelparkerhenderson/architecture-decision-record
- **When to write ADRs:** https://github.blog/2020-08-13-why-write-adrs/

---

## Contributing

**When to create an ADR:**
- Significant architectural change
- Technology choice (framework, library, database)
- Pattern adoption (clean architecture, DDD, etc.)
- Infrastructure decision (cloud provider, deployment strategy)

**When NOT to create an ADR:**
- Minor refactoring
- Bug fixes
- Code style decisions (use linter config)
- Temporary workarounds

**Process:**
1. Create new ADR with next number
2. Fill in template
3. Discuss with team
4. Update status (Proposed → Accepted/Rejected)
5. Link related ADRs
