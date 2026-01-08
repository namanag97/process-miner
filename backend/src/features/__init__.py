"""Features Layer - Domain-specific business logic.

This layer contains code specific to the product vertical.
Currently: Process Mining SaaS.

Modules:
- process_mining/
  - models/          - SQLAlchemy models (Dataset, etc.)
  - schemas/         - Pydantic schemas for API
  - datasets/        - Dataset upload, ingestion
  - ingestion/       - DuckDB-based data ingestion
  - discovery/       - Process discovery (Alpha, Inductive, Heuristics)
  - conformance/     - Conformance checking
  - analytics/       - Performance analytics
  - visualization/   - DFG, Petri net graphs
  - predictions/     - ML predictions
  - organizational/  - Organizational mining
  - simulation/      - What-if analysis
  - ocpm/            - Object-Centric PM (OCEL)
  - ai/              - AI chat assistant
  - statistics/      - Dataset statistics

Import Rules:
- Features CAN import from src.infra.*
- Features CANNOT import from src.api.*
- Platform (infra) CANNOT import from features
"""

from src.features import process_mining

__all__ = ["process_mining"]
