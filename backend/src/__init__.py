"""Process Mining SaaS Backend.

A FastAPI-based backend for process mining analytics.

Architecture:
- api/          - FastAPI application and routers
- features/     - Process mining feature modules
- infra/        - Infrastructure layer (auth, db, temporal)
- application/  - CQRS application layer
- shared/       - Shared utilities

Key Technologies:
- FastAPI       - Async REST API
- PM4Py         - Process mining algorithms
- SQLAlchemy    - Async ORM with SQLite
- DuckDB        - High-performance data ingestion
- Temporal      - Workflow orchestration
"""

__version__ = "1.0.0"
