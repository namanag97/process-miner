# DATABASE DEV TASK: Audit Schema & Models

## Your Mission

Audit `/backend/src/models/` and database schema.

## What CTO Needs

### 1. ORM Models

List every SQLAlchemy model:

| Model Name | File | Table Name | Key Fields |
| ---------- | ---- | ---------- | ---------- |

### 2. Relationships

Map all foreign keys and relationships:

| Model A | Relationship | Model B | Foreign Key |
| ------- | ------------ | ------- | ----------- |

### 3. Migrations

Check for Alembic migrations:

| Migration | What It Does | Applied? |
| --------- | ------------ | -------- |

Look in:

- `/backend/alembic/versions/` (if exists)
- Check if migrations are used at all

### 4. Test Data

Check if any seed data exists:

| Table | Has Seed Data? | Count |
| ----- | -------------- | ----- |

### 5. Schema Verification

Compare ORM models to actual database:

```bash
# Check what tables exist in SQLite
sqlite3 backend/src/process_mining.db ".tables"

# Check table schemas
sqlite3 backend/src/process_mining.db ".schema datasets"
```

## Files to Examine

- `/backend/src/models/orm.py` — Main ORM models
- `/backend/src/models/database.py` — Database connection
- `/backend/src/models/schemas.py` — Pydantic schemas (API DTOs)
- `/docs/database_schema.dbml` — Intended schema

## Output

Update `/docs/cto/CTO_KNOWLEDGE_BASE.md` Database section.

Report format:

```
Database Audit Complete:
- X ORM models
- Y tables in SQLite
- Z relationships mapped
- Migrations: [status]
- Top issues: [list]
```
