"""Prediction Models.

ML prediction models, individual predictions, and recommendations.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.database import Base


class PredictionModel(Base):
    """Trained ML prediction model."""

    __tablename__ = "prediction_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Model identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # What it predicts
    target_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # 'next_activity', 'remaining_time', 'outcome', 'sla_breach', 'resource'
    
    # Algorithm used
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # 'lstm', 'transformer', 'random_forest', 'xgboost', 'markov'
    
    # Model storage (file path preferred over BLOB)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    model_binary: Mapped[bytes | None] = mapped_column(Text, nullable=True)  # Deprecated
    
    # Training configuration
    training_config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Evaluation metrics
    metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="training", index=True)
    # 'training', 'ready', 'deprecated', 'failed'
    
    workflow_id: Mapped[str | None] = mapped_column(
        ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Timing
    trained_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    training_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    """Individual prediction for a running case."""

    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    model_id: Mapped[str] = mapped_column(
        ForeignKey("prediction_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # What case/prefix this is for
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    case_prefix_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # The prediction
    prediction_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # For outcome tracking
    actual_outcome_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    was_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("ix_predictions_model_case", "model_id", "case_id"),
    )


class Recommendation(Base):
    """Actionable recommendation for a process case."""

    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Trigger
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # 'sla_risk', 'bottleneck_detected', 'deviation_predicted', 'resource_overload'
    signal_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Recommended action
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 'escalate', 'reassign', 'skip_activity', 'notify', 'investigate'
    action_params_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Prioritization
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    # 'critical', 'high', 'medium', 'low'
    expected_impact_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # State machine
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    # 'pending', 'viewed', 'accepted', 'dismissed', 'expired'
    
    # User interaction
    handled_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    handled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    __table_args__ = (
        Index("ix_recommendations_dataset_case", "dataset_id", "case_id"),
    )

