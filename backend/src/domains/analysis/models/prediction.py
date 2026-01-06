"""Prediction Models.

ML prediction models, individual predictions, and recommendations.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.database import Base


class PredictionModel(Base):
    """ML prediction model."""

    __tablename__ = "prediction_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False)
    model_binary: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    trained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    """Individual prediction record."""

    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    model_id: Mapped[str] = mapped_column(
        ForeignKey("prediction_models.id", ondelete="CASCADE"), nullable=False
    )
    case_prefix_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    prediction_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    """Prescriptive recommendation for a process case."""

    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    signal_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_params_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    state: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
