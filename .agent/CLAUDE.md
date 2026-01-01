# CLAUDE.md — AI Collaboration Guide

> **Read this first before making any changes to this codebase.**

This is a **Process Mining SaaS** backend wrapping PM4Py with FastAPI + SQLAlchemy (async) + SQLite.

---

## 🚨 Critical Rules

| Rule                                                    | Reason                                                 |
| ------------------------------------------------------- | ------------------------------------------------------ |
| **NEVER** modify `orm.py` without updating `schemas.py` | 23+ files depend on ORM models                         |
| **NEVER** use raw `try/except Exception`                | Use `AppException` hierarchy from `core/exceptions.py` |
| **ALWAYS** run `make check` before claiming done        | Runs lint + typecheck + security                       |
| **ALWAYS** regenerate SDK after schema changes          | `cd backend/sdk && npm run generate && npm run build`  |
| **NEVER** hardcode secrets                              | Use `core/config.py` → environment variables only      |

---

## Architecture Quick Reference

```
backend/src/
├── api/routers/     → HTTP endpoints (thin, validation only)
├── services/        → Business logic + PM4Py operations
├── models/orm.py    → SQLAlchemy (10 tables)
├── models/schemas.py → Pydantic (137 models)
├── core/            → Config, exceptions, logging
└── infrastructure/  → Cache, workers, circuit breakers
```

**Data Flow**: Router → Pydantic Validation → Service → PM4Py → ORM → Response

---

## Common Pitfalls

| If you're tempted to...       | Instead, do this...                                            |
| ----------------------------- | -------------------------------------------------------------- |
| Create a new utility function | Check `core/` and `services/` first                            |
| Add generic `try/except`      | Use `AppException` subclass (see [PATTERNS.md](./PATTERNS.md)) |
| Return plain dict from router | Return Pydantic model from `schemas.py`                        |
| Use print() for debugging     | Use `structlog.get_logger(__name__)`                           |
| Add DB query in router        | Put it in service layer                                        |
| Modify PM4Py log directly     | Copy or use service wrapper                                    |

---

## Related Documentation

| Doc                                                             | Purpose                           |
| --------------------------------------------------------------- | --------------------------------- |
| [DEPENDENCY_MAP.md](./DEPENDENCY_MAP.md)                        | What breaks when you touch X      |
| [PATTERNS.md](./PATTERNS.md)                                    | DO/DON'T code examples            |
| [INVARIANTS.md](./INVARIANTS.md)                                | Never-break rules                 |
| [TESTING_CONTRACTS.md](./TESTING_CONTRACTS.md)                  | What to test for each change type |
| [CURRENT_STATE.md](./CURRENT_STATE.md)                          | Work in progress, don't touch     |
| [RECOVERY_PLAYBOOK.md](./RECOVERY_PLAYBOOK.md)                  | How to fix when things break      |
| [backend/docs/ARCHITECTURE.md](../backend/docs/ARCHITECTURE.md) | Full architecture details         |
| [backend/CLAUDE.md](../backend/CLAUDE.md)                       | Backend-specific quick start      |

---

## Quick Commands

```bash
# Backend
cd backend
make check          # lint + typecheck + security
make test           # run all tests
make run            # start dev server (port 8001)

# SDK (requires backend running)
cd backend/sdk && npm run generate && npm run build

# Full CI
make all            # check + test (from root)
```
