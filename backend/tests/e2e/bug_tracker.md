# E2E Test Bug Tracker

Auto-generated: 2026-01-07 13:37:20

## Test Run 1: Dataset Upload Journey

### ❌ Failing Tests (Cannot run - import error)

#### BUG-001: SQLAlchemy table already defined (P0 - BLOCKING) ✅ FIXED
**Test**: All E2E tests
**Status**: ✅ FIXED - Deleted duplicate `src/platform/users/models.py`
**Error**:
```
sqlalchemy.exc.InvalidRequestError: Table 'organizations' is already defined for this MetaData instance.
Specify 'extend_existing=True' to redefine options and columns on an existing Table object.
```

**Stack trace**:
```
src/platform/users/models.py:21: in <module>
    class Organization(Base):
```

**Root cause**: Duplicate model definitions - `Organization` is defined in both:
- `src/platform/models.py` (old location)
- `src/platform/users/models.py` (new location)

SQLAlchemy doesn't allow the same table to be defined twice in the same MetaData instance.

**Fix**: Need to consolidate model definitions to a single location.

**Priority**: P0 - Cannot run any tests until this is fixed
