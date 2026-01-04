# Process Discovery Platform Migration - Documentation Index

**Location:** `/Users/namanagarwal/system/docs/migration/`  
**Created:** 2026-01-04  
**Purpose:** Comprehensive planning docs for AI agent-driven migration

---

## Quick Start for Agents

1. **Read `memory.md` FIRST** - Contains all project context, invariants, and conventions
2. **Check `task.md`** - See current progress and what's next
3. **Find your phase in `master_checklist.md`** - Get granular task list
4. **Reference `edge_cases.md`** - Know what can go wrong
5. **Execute according to `implementation_plan.md`** - Follow step-by-step instructions
6. **Verify using `quality_plan.md`** - Ensure quality gates pass

---

## Document Inventory

| File | Size | Purpose |
|------|------|---------|
| [README.md](file:///Users/namanagarwal/system/docs/migration/README.md) | 3KB | **This file** - Index and quick start guide |
| [memory.md](file:///Users/namanagarwal/system/docs/migration/memory.md) | 16KB | **AI Agent Memory** - Persistent context, invariants, naming conventions |
| [implementation_plan.md](file:///Users/namanagarwal/system/docs/migration/implementation_plan.md) | 34KB | **Technical Plan** - Current state audit, target state, code snippets |
| [master_checklist.md](file:///Users/namanagarwal/system/docs/migration/master_checklist.md) | 22KB | **Project Checklist** - 150+ granular tasks across 14 phases |
| [sequencing.md](file:///Users/namanagarwal/system/docs/migration/sequencing.md) | 7KB | **Phase Dependencies** - Execution order, parallelization, scheduling |
| [edge_cases.md](file:///Users/namanagarwal/system/docs/migration/edge_cases.md) | 17KB | **Risk Registry** - 100+ edge cases and failure scenarios |
| [cleanup_tracker.md](file:///Users/namanagarwal/system/docs/migration/cleanup_tracker.md) | 12KB | **Technical Debt** - 80+ items organized by priority |
| [quality_plan.md](file:///Users/namanagarwal/system/docs/migration/quality_plan.md) | 14KB | **Quality Gates** - Testing, benchmarks, rollback procedures |
| [task.md](file:///Users/namanagarwal/system/docs/migration/task.md) | 4KB | **Progress Tracker** - Current phase status and metrics |

**Total:** 9 documents, ~130KB of planning documentation

---

## Project Overview

**Goal:** Transform Process Mining MVP into enterprise-grade Process Discovery Platform

**Key Migrations:**
1. Pickle storage → PNML/BPMN/JSON (Phase 1)
2. ReactFlow → Cytoscape.js (Phase 2)
3. Mock auth → Auth0/RLS (Phase 6)
4. Sync processing → Event-driven (Phase 5)

**Current Stats:**
- 21 API routers, 128 endpoints
- 27 ORM models, 122 Pydantic schemas
- 17 mining algorithms implemented
- 8 pickle serialization points to eliminate

---

## How to Update These Docs

When completing work:
1. Update `task.md` with completed tasks
2. Update `memory.md` Section VI (Progress Tracking)
3. Mark items in `master_checklist.md` as `[x]`
4. Add any new issues to `edge_cases.md`
5. Track cleanup in `cleanup_tracker.md`

---

## Workflow Reference

There's also a workflow file for slash command access:

```
/Users/namanagarwal/system/.agent/workflows/migration-plan.md
```

---

**This documentation is the single source of truth for the migration project.**
