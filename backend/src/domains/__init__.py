"""Business Domains.

This package contains well-bounded business domains:
- admin: User, organization, workspace, project management
- datasets: Data upload, ingestion, storage, connectors
- analysis: Process mining, analytics, visualization

Each domain follows Domain-Driven Design principles with:
- Clear boundaries and responsibilities
- Domain-specific models, schemas, services
- Minimal cross-domain dependencies

Domain Structure:
- api/: FastAPI routers for the domain
- models/: SQLAlchemy ORM models
- schemas/: Pydantic request/response schemas
- services/: Business logic services
- tasks/: Background tasks (Celery/async)
- README.md: Domain boundary documentation
"""

from src.domains import admin, analysis, datasets

__all__ = ["admin", "datasets", "analysis"]
