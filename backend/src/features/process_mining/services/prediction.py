"""Prediction Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.predictions.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.prediction import prediction_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.predictions import prediction_service
"""

from src.features.process_mining.predictions import (
    PredictionService,
    prediction_service,
)

__all__ = [
    "PredictionService",
    "prediction_service",
]
