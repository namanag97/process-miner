# Invariants — Never Break These Rules

> These constraints MUST survive any AI modification. Violating them causes silent production failures.

---

## 📊 Data Integrity

| Invariant                             | Enforcement                           | Violation Effect              |
| ------------------------------------- | ------------------------------------- | ----------------------------- |
| All `id` fields are UUIDs             | `default=lambda: str(uuid4())` in ORM | Foreign key failures          |
| `timestamp` fields are always **UTC** | `datetime.utcnow()`                   | Analytics calculations wrong  |
| **Soft deletes only** for user data   | No `DELETE` in production code        | Data loss, audit trail broken |
| All JSON fields are valid JSON        | `Text` column, validated before save  | Parser crashes                |

### Never Do This:

```python
# ❌ Local time
created_at = datetime.now()

# ❌ Hard delete
await db.delete(event_log)

# ❌ Non-UUID id
id = "my-custom-id"
```

---

## 🔌 API Contracts

| Invariant                                | Enforcement                 | Violation Effect               |
| ---------------------------------------- | --------------------------- | ------------------------------ |
| All endpoints return Pydantic models     | `response_model=` in router | SDK breaks                     |
| Error responses follow RFC 7807          | `AppException.to_dict()`    | Frontend error handling breaks |
| No breaking changes without version bump | `/v1/` → `/v2/`             | Production clients break       |
| List endpoints always paginated          | `PaginatedResponse` base    | Memory exhaustion              |

### API Response Shape:

```python
# ✅ All success responses match schemas.py models
# ✅ All error responses: { "error": {...}, "status_code": int }
# ✅ List responses: { "items": [...], "total": int, "page": int }
```

---

## ⚡ Performance

| Invariant                      | Enforcement                   | Violation Effect        |
| ------------------------------ | ----------------------------- | ----------------------- |
| All DB calls are `async`       | `AsyncSession`, `await`       | Blocking event loop     |
| No N+1 queries                 | Use `selectin` loading in ORM | 10x slower endpoints    |
| Expensive operations cached    | `cache_service` with TTL      | Repeated 30s operations |
| PM4Py logs copied, not mutated | `.copy()` before modification | Cross-request pollution |

### Never Do This:

```python
# ❌ Sync database call
result = db.execute(query).all()

# ❌ N+1 query
for case in event_log.cases:
    for event in case.events:  # Each triggers a query
        ...

# ❌ Mutating shared PM4Py log
pm4py_log['new_column'] = 'value'  # Affects other requests!
```

---

## 🔒 Security (Even in MVP)

| Invariant                          | Enforcement                 | Violation Effect         |
| ---------------------------------- | --------------------------- | ------------------------ |
| No secrets in code                 | `config.py` → env vars only | Leaked credentials       |
| No raw SQL                         | ORM query builder only      | SQL injection            |
| Sanitize user input before logging | Filter PII                  | GDPR violation           |
| File uploads validated             | Extension + content check   | Malicious file execution |

### Never Do This:

```python
# ❌ Secret in code
API_KEY = "sk-12345..."

# ❌ Raw SQL
await db.execute(f"SELECT * FROM logs WHERE id = '{user_input}'")

# ❌ Logging user data unsanitized
logger.info("User uploaded", filename=user_file.filename, content=user_data)
```

---

## 🧪 Testing

| Invariant                        | Enforcement             | Violation Effect         |
| -------------------------------- | ----------------------- | ------------------------ |
| All routers have test files      | `test_{router_name}.py` | Untested endpoints       |
| Tests use fixtures, not prod DB  | `conftest.py` fixtures  | Production data modified |
| Async tests use `pytest-asyncio` | `@pytest.mark.asyncio`  | Tests hang or fail       |

---

## 📐 Code Organization

| Invariant                               | Enforcement        | Violation Effect      |
| --------------------------------------- | ------------------ | --------------------- |
| Routers don't import from other routers | Layer boundaries   | Circular imports      |
| Services don't import from routers      | Layer boundaries   | Circular imports      |
| No PM4Py imports in routers             | Service layer only | Mixed concerns        |
| ORM models in `orm.py` only             | Single file        | Scattered definitions |
| Pydantic schemas in `schemas.py` only   | Single file        | SDK generation breaks |
