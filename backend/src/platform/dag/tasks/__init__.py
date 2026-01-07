"""DAG Tasks Package.

Contains DAG-compatible task functions organized by domain:
- dataset: File validation, column detection, ingestion
- analysis: Process discovery, conformance, statistics
- prediction: ML model training
"""

from src.platform.dag.tasks.analysis import (
    check_conformance,
    compute_statistics,
    discover_model,
)
from src.platform.dag.tasks.dataset import (
    detect_columns,
    ingest_dataset,
    validate_file,
)
from src.platform.dag.tasks.prediction import (
    train_predictor,
)

__all__ = [
    "check_conformance",
    "compute_statistics",
    "detect_columns",
    # Analysis
    "discover_model",
    "ingest_dataset",
    # Prediction
    "train_predictor",
    # Dataset
    "validate_file",
]
