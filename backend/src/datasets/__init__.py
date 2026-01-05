"""Datasets Layer - Data Foundation.

This layer handles everything related to data management:
- Upload and ingestion (XES, CSV, OCEL)
- Storage (DuckDB, file management)
- Serving data to the Analysis layer

The Datasets layer:
- CAN depend on: Platform layer
- CANNOT depend on: Analysis layer
"""

from src.datasets.enums import SourceFormat

__all__ = [
    "SourceFormat",
]
