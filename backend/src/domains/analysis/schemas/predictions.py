"""Prediction schemas - ML-based process predictions.

Contains schemas for:
- Predictor training requests and responses
- Prediction requests and results
- Batch predictions
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TrainPredictorRequest(BaseModel):
    """Request to train a prediction model."""

    target_type: str = Field(
        ...,
        description="Prediction target: 'next_activity', 'remaining_time', 'outcome'",
    )
    algorithm: str = Field(
        default="random_forest",
        description="ML algorithm: 'random_forest', 'xgboost', 'gradient_boosting'",
    )
    outcome_attribute: str | None = Field(
        None,
        description="Attribute to predict for outcome models",
    )


class PredictorResponse(BaseModel):
    """Prediction model response."""

    id: str
    dataset_id: str = ""
    target_type: str
    algorithm: str
    metrics: dict[str, Any] = {}
    trained_at: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse metrics_json."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "dataset_id",
                    "target_type",
                    "algorithm",
                    "metrics_json",
                    "trained_at",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("metrics_json"):
                try:
                    data["metrics"] = json.loads(data["metrics_json"])
                except (json.JSONDecodeError, TypeError):
                    data["metrics"] = {}
            elif "metrics" not in data:
                data["metrics"] = {}
        return data

    model_config = ConfigDict(from_attributes=True)


class PredictorListResponse(BaseModel):
    """List of prediction models."""

    dataset_id: str
    predictors: list[PredictorResponse]
    total: int


class PredictionRequest(BaseModel):
    """Request for a single prediction."""

    case_prefix: list[str] = Field(..., description="Activity sequence so far")
    case_attributes: dict[str, Any] | None = None


class PredictionResponse(BaseModel):
    """Prediction result."""

    predictor_id: str
    case_prefix: list[str]
    prediction: Any
    confidence: float | None
    alternatives: list[dict[str, Any]] | None = None


class BatchPredictionRequest(BaseModel):
    """Request for batch predictions."""

    cases: list[PredictionRequest]


class BatchPredictionResponse(BaseModel):
    """Batch prediction results."""

    predictor_id: str
    predictions: list[PredictionResponse]
