"""Datasets layer enums.

Enums related to data formats and ingestion.
"""

from enum import Enum


class SourceFormat(str, Enum):
    """Event log source formats."""

    CSV = "csv"
    XES = "xes"
    OCEL_JSON = "ocel_json"
    OCEL_SQLITE = "ocel_sqlite"
