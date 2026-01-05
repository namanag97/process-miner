# API Testing & Fixing Agent - Handover Prompt

## Objective
Continuously test, identify bugs, fix them, and update documentation until all critical and major bugs are resolved.

## System Context
- **Test Framework**: `/Users/namanagarwal/system/test/ai_api_tester.py`
- **OpenAPI Spec**: `/Users/namanagarwal/system/backend/docs/openapi.json`
- **Backend Code**: `/Users/namanagarwal/system/backend/src/`
- **Base URL**: `http://localhost:8001`

## Execution Loop

Repeat the following cycle until Critical bugs = 0 and Major bugs < 5:

### 1. RUN TESTS
```bash
cd /Users/namanagarwal/system
python test/ai_api_tester.py
```

### 2. ANALYZE BUGS
Read the generated bug report:
```
test/bugs_identified.md
```

Prioritize by severity:
- **CRITICAL** (500 errors, crashes) → Fix immediately
- **MAJOR** (Schema violations, undefined variables, 404s on valid paths) → Fix next
- **MINOR** (Optional field issues) → Fix if time permits

### 3. ROOT CAUSE ANALYSIS

For each bug, determine:
- **Is it a code bug?** (undefined variables, wrong Pydantic methods, missing fields)
- **Is it a test data issue?** (missing resources, invalid IDs)
- **Is it a schema mismatch?** (OpenAPI spec doesn't match code)

### 4. FIX BUGS

**For code bugs:**
- Locate the file using `grep` or `Glob`
- Read the file
- Fix the bug (undefined vars, wrong method calls, missing error handling)
- Common fixes:
  - `from_orm()` → `model_validate()` (Pydantic v2)
  - Undefined `log_id` → use correct parameter name `dataset_id`
  - Missing fields in response schemas
  - Missing imports

**For schema mismatches:**
- Update Pydantic models to match OpenAPI spec
- Add missing fields marked as required
- Fix field types (str | None for nullable)

**Skip test data issues** (404s for non-existent resources are expected in automated tests)

### 5. UPDATE OPENAPI DOCS

After fixing code, regenerate OpenAPI spec:
```bash
cd /Users/namanagarwal/system/backend
source .venv/bin/activate
python -c "from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > docs/openapi.json
```

### 6. VERIFY & REPEAT

Re-run tests (go to step 1) and compare results:
- Did Critical bugs decrease?
- Did Passing tests increase?
- Are there new bugs introduced?

## Success Criteria

Stop when:
- **Critical bugs** = 0
- **Major bugs** < 5
- **Passing tests** > 90%
- All remaining failures are expected (404s for missing test data, 401s for invalid credentials)

## Quick Reference: Common Bugs

| Bug Pattern | Root Cause | Fix |
|-------------|------------|-----|
| `NameError: log_id` | Variable name mismatch | Change to `dataset_id` |
| `AttributeError: from_orm` | Pydantic v2 | Use `model_validate()` |
| 500 on `/jobs` endpoint | Missing field in schema | Add `stage: str \| None` |
| Schema validation: "Expected non-null" | OpenAPI anyOf pattern | Already fixed in tester |
| 401 on auth endpoints | Invalid test credentials | Expected - skip |
| 404 on resource endpoints | Missing test data | Expected - skip |

## Agent Prompt Template

```
I need you to continuously improve API quality by:

1. Run: python test/ai_api_tester.py
2. Read: test/bugs_identified.md
3. For each CRITICAL bug:
   - Find the code causing it (grep/glob)
   - Read the relevant files
   - Determine root cause
   - Fix the bug
4. For each MAJOR bug (up to 5 per iteration):
   - Same process as CRITICAL
5. Regenerate OpenAPI docs
6. Re-run tests
7. Report progress: "Fixed X bugs, Y critical remaining, Z% tests passing"
8. REPEAT until success criteria met

Focus on real code bugs, not test data issues.
```

## Current State

**Last Run**: 2026-01-05 17:36
**Results**:
- Total Tests: 146
- Passing: 36 (24%)
- Critical Bugs: 8
- Major Bugs: 102

**Already Fixed**:
- ✅ Job endpoints (from_orm → model_validate)
- ✅ Analyses endpoint (log_id → dataset_id)
- ✅ Conformance results (log_id → dataset_id)
- ✅ Schema validator (anyOf nullable handling)

**Remaining Work**:
- Auth refresh endpoint (likely test data issue)
- Business process comparison endpoints
- Various 404s (test data issues)
- Various 422s (validation - may be expected)

## Example Iteration

```
Iteration 1:
- Found 10 CRITICAL bugs
- RCA: 5 are code bugs (undefined vars), 5 are test data
- Fixed 5 code bugs
- Regenerated OpenAPI
- Re-tested: 8 CRITICAL remaining (all test data)
- Progress: 19% → 24% passing ✅

Iteration 2:
- Found 8 CRITICAL, 102 MAJOR
- RCA: Most MAJOR are 404/422 (expected for empty DB)
- Fixed 3 MAJOR schema mismatches
- Regenerated OpenAPI
- Re-tested: 5 CRITICAL, 95 MAJOR
- Progress: 24% → 32% passing ✅

Continue until Critical = 0...
```
