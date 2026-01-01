# Current State — Where We Are

> Last updated: 2026-01-01

---

## Current Sprint Focus

- **Organizational mining features** — PM4Py social network analysis
- **PM4Py integration completion** — Filtering, statistics, simulation
- **Documentation maintenance** — API_REFERENCE.md, DATA_CONTRACTS.md

---

## Known Issues (Don't Fix Unless Asked)

These are known and intentionally deferred:

| Issue                      | Status       | Reason                       |
| -------------------------- | ------------ | ---------------------------- |
| SQLite concurrency limits  | Deferred     | PostgreSQL migration planned |
| Frontend responsive issues | Deferred     | Design not finalized         |
| Some test coverage gaps    | Acknowledged | MVP focus                    |

---

## Work in Progress (Coordinate Before Touching)

| Area                         | Status           | Notes                            |
| ---------------------------- | ---------------- | -------------------------------- |
| `services/organizational.py` | Active           | Social network analysis          |
| `models/schemas.py`          | Frequent changes | Check for conflicts              |
| `backend/docs/*`             | Active           | Being updated with new endpoints |

---

## Recent Decisions

| Date       | Decision                    | Rationale                            |
| ---------- | --------------------------- | ------------------------------------ |
| 2026-01-01 | Use PM4Py for all mining    | Stable, academically validated       |
| 2026-01-01 | TanStack Query for frontend | Simpler than Redux for data fetching |
| 2026-01-01 | DuckDB for large ingestion  | 10x faster than row-by-row           |
| 2025-12-31 | OCEL 2.0 for object-centric | Industry standard, PM4Py support     |

---

## Technical Debt (Acknowledged)

- [ ] EventLog model mixes concerns — split planned
- [ ] Frontend has duplicate API handling — SDK migration ongoing
- [ ] Some services need better error handling coverage

---

## Architecture Reviews Completed

- DDD review (2025-12-31): Identified anemic domain model
- Production readiness review (2026-01-01): Infrastructure gaps flagged
- Frontend TanStack review (2025-12-31): Query key factory pattern adopted
