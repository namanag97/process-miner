"""Business Domains.

This package contains well-bounded business domains:
- admin: User, organization, workspace, project management
- datasets: Data upload, ingestion, storage, connectors
- analysis: Process mining, analytics, visualization

Each domain follows Domain-Driven Design principles with:
- Clear boundaries and responsibilities
- Domain-specific models, schemas, services
- Minimal cross-domain dependencies
"""

from src.domains import admin, analysis, datasets

__all__ = ["admin", "datasets", "analysis"]
