#!/usr/bin/env python3
"""Schema Validation Script.

Validates that SQLAlchemy models align with the DBML schema.
Run as part of CI to detect schema drift.

Usage:
    python scripts/validate_schema.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shared.database import Base

# Import all models to ensure they're registered
from src.infra.models import *  # noqa
from src.infra.workflows.models import *  # noqa
from src.infra.system.models import *  # noqa
from src.features.process_mining.models import *  # noqa


def get_all_tables() -> list[str]:
    """Get all table names from SQLAlchemy metadata."""
    return sorted(Base.metadata.tables.keys())


def get_table_columns(table_name: str) -> dict:
    """Get column info for a table."""
    table = Base.metadata.tables.get(table_name)
    if table is None:
        return {}
    
    columns = {}
    for col in table.columns:
        columns[col.name] = {
            "type": str(col.type),
            "nullable": col.nullable,
            "primary_key": col.primary_key,
            "foreign_keys": [str(fk.target_fullname) for fk in col.foreign_keys],
        }
    return columns


def validate_schema() -> bool:
    """Validate schema and print report."""
    print("=" * 60)
    print("SCHEMA VALIDATION REPORT")
    print("=" * 60)
    
    tables = get_all_tables()
    print(f"\n✓ Found {len(tables)} tables in SQLAlchemy metadata")
    
    # Group by prefix
    platform_tables = [t for t in tables if not t.startswith(("process_", "ocel", "lookup_", "datasets", "prediction", "recommendation", "social", "activity", "hierarchical", "analyses", "conformance", "analytics", "graph_"))]
    feature_tables = [t for t in tables if t not in platform_tables]
    
    print(f"\nPlatform Tables ({len(platform_tables)}):")
    for t in sorted(platform_tables):
        cols = len(get_table_columns(t))
        print(f"  - {t} ({cols} columns)")
    
    print(f"\nFeature Tables ({len(feature_tables)}):")
    for t in sorted(feature_tables):
        cols = len(get_table_columns(t))
        print(f"  - {t} ({cols} columns)")
    
    # Check for expected DBML tables
    expected_tables = {
        # Platform
        "organizations", "users", "workspaces", "workspace_members", "projects",
        "workflows", "workflow_tasks", "error_logs", "feature_flags", "api_usage",
        # Features
        "datasets", "dataset_columns", "dataset_column_mappings", "dataset_metadata",
        "process_cases", "process_events", "process_variants",
        "lookup_activities", "lookup_resources",
        "process_models", "process_model_metrics", "graph_cache",
        "analyses", "conformance_results", "analytics_cache",
        "prediction_models", "predictions", "recommendations",
        "social_networks", "activity_mappings", "hierarchical_process_models",
        # OCEL
        "ocel2_event_types", "ocel2_object_types", "ocel2_events", "ocel2_objects",
        "ocel2_e2o_relations", "ocel2_o2o_relations",
    }
    
    missing = expected_tables - set(tables)
    if missing:
        print(f"\n⚠ Missing expected tables: {missing}")
    else:
        print("\n✓ All expected DBML tables present")
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    
    return len(missing) == 0


if __name__ == "__main__":
    success = validate_schema()
    sys.exit(0 if success else 1)
