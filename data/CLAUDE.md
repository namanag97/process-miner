# Data CLAUDE.md

## Overview
Root data directory for local development. Contains databases, uploaded files, and model artifacts.

## Directory Structure

```
data/
├── db/          # SQLite database files
├── models/      # Trained model artifacts
└── uploads/     # Uploaded event log files
```

## Important Notes

- This directory is for LOCAL DEVELOPMENT ONLY
- Do not commit data files to git (check .gitignore)
- Production uses S3/MinIO for object storage
- Database files can be recreated via migrations

## Database

The SQLite database is stored in `db/`. To reset:

```bash
cd backend
rm -f data/db/*.db
.venv/bin/alembic upgrade head
```

## Uploads

Uploaded event logs are stored in `uploads/`. Structure:
```
uploads/
└── {project_id}/
    └── {dataset_id}/
        └── {filename}
```
