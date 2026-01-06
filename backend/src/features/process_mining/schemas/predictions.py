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
    name: str = Field("", description="Human-readable model name")
    target_type: str
    algorithm: str
    status: str = Field("ready", description="training, ready, deprecated, failed")
    storage_path: str | None = Field(None, description="Path to serialized model file")
    metrics: dict[str, Any] = {}
    training_config: dict[str, Any] | None = Field(None, description="Hyperparameters and feature settings")
    workflow_id: str | None = Field(None, description="Temporal workflow that trained this model")
    trained_at: datetime | None = None
    training_duration_seconds: int | None = None
    created_at: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse metrics_json and training_config_json."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "dataset_id",
                    "name",
                    "target_type",
                    "algorithm",
                    "status",
                    "storage_path",
                    "metrics_json",
                    "training_config_json",
                    "workflow_id",
                    "trained_at",
                    "training_duration_seconds",
                    "created_at",
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
            if data.get("training_config_json"):
                try:
                    data["training_config"] = json.loads(data["training_config_json"])
                except (json.JSONDecodeError, TypeError):
                    data["training_config"] = None
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
