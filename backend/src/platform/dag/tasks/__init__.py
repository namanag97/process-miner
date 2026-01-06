"""DAG Tasks Package.

Contains DAG-compatible task functions organized by domain:
- dataset: File validation, column detection, ingestion
- analysis: Process discovery, conformance, statistics
- prediction: ML model training
"""

from src.platform.dag.tasks.dataset import (
    validate_file,
    detect_columns,
    ingest_dataset,
)
from src.platform.dag.tasks.analysis import (
    discover_model,
    check_conformance,
    compute_statistics,
)
from src.platform.dag.tasks.prediction import (
    train_predictor,
)

__all__ = [
    # Dataset
    "validate_file",
    "detect_columns",
    "ingest_dataset",
    # Analysis
    "discover_model",
    "check_conformance",
    "compute_statistics",
    # Prediction
    "train_predictor",
]
