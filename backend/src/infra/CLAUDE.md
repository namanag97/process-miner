# Backend Infrastructure CLAUDE.md

## Overview
Infrastructure layer containing all external integrations, persistence, and platform services. This layer provides the technical capabilities that features and application layer depend on.

## Directory Structure

```
infra/
├── models.py            # Shared SQLAlchemy models
├── schemas.py           # Shared Pydantic schemas
├── admin/               # Admin utilities
├── audit/               # Audit logging
├── auth/                # JWT authentication
├── core/                # Core infrastructure (DB, config)
├── dag/                 # DAG workflow management
├── devconsole/          # Developer console and debugging
├── devtools/            # Development utilities
├── health/              # Health check endpoints
├── infrastructure/      # Base infrastructure (storage, cache)
├── jobs/                # Background job management
├── organizations/       # Multi-tenant organization management
├── projects/            # Project management
├── storage/             # Object storage (S3/MinIO)
├── system/              # System utilities
├── temporal/            # Temporal workflow activities
├── users/               # User management
├── workflows/           # Workflow definitions
└── workspaces/          # Workspace management
```

## Key Modules

### core/
Core infrastructure:
- Database session management
- Configuration loading
- Middleware
- Exception handling

### infrastructure/
Base technical services:
- `object_storage.py` - S3/MinIO client
- `cache.py` - Redis caching
- `tasks.py` - Celery task submission

### temporal/
Temporal.io workflow activities:
- Data ingestion activities
- Long-running process activities

### auth/
JWT authentication:
- Token generation/validation
- Password hashing
- Session management

### organizations/ / workspaces/ / projects/
Multi-tenant hierarchy:
- Organization → Workspace → Project
- RBAC permission management

## Import Rules

- This layer should NOT import from `features/` or `application/`
- Can import from `shared/`
- Provides interfaces for upper layers
