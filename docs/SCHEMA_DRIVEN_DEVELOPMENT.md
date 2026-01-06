# Schema-Driven Development Guide

## Overview

This document describes the schema-driven development workflow for the Process Mining SaaS backend.

## Source of Truth

The **DBML schema** at `docs/process_mining_schema.dbml` is the canonical source of truth for the database schema.

## Workflow

```
┌──────────────────┐
│  Edit DBML       │
│  (schema design) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Update Models   │
│  (SQLAlchemy)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Generate        │
│  Alembic         │
│  Migration       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Run Tests       │
│  + Validation    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Deploy          │
└──────────────────┘
```

## Commands

### Validate Schema
```bash
cd backend
python scripts/validate_schema.py
```

### Generate DBML from Models
```bash
cd backend
python scripts/generate_dbml.py
```

### Generate Migration
```bash
cd backend
alembic revision --autogenerate -m "description"
```

### Apply Migrations
```bash
cd backend
alembic upgrade head
```

## Model Locations

| Domain | Location |
|--------|----------|
| Platform Core | `src/platform/users/models.py` |
| Workflows | `src/platform/workflows/models.py` |
| System | `src/platform/system/models.py` |
| Datasets | `src/features/process_mining/models/dataset.py` |
| Events | `src/features/process_mining/models/events_models.py` |
| Variants | `src/features/process_mining/models/variants.py` |
| Process Models | `src/features/process_mining/models/process_model_models.py` |
| Analysis | `src/features/process_mining/models/analysis_models.py` |
| Prediction | `src/features/process_mining/models/prediction.py` |
| OCEL 2.0 | `src/features/process_mining/models/ocel2.py` |

## CI Integration

Add to CI pipeline:
```yaml
- name: Validate Schema
  run: python scripts/validate_schema.py
```
