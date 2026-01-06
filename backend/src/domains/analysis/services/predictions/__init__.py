"""Predictions Services.

ML-based prediction services.
"""

from src.domains.analysis.services.predictions.service import PredictionService

prediction_service = PredictionService()

__all__ = [
    "PredictionService",
    "prediction_service",
]
