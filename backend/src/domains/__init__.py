"""Business Domains.

This package contains well-bounded business domains:
- admin: User, organization, workspace, project management
- datasets: Data upload, ingestion, storage, connectors
- analysis: Process mining, analytics, visualization

Note: Admin routers and some infrastructure have been migrated to:
- src.platform.users (models, schemas, routers)
"""

from src.domains import admin, analysis, datasets

__all__ = ["admin", "datasets", "analysis"]
