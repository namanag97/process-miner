"""System Models.

Feature flags and API usage tracking for operations.
"""

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.database import Base


class FeatureFlag(Base):
    """Feature flags and A/B tests."""

    __tablename__ = "feature_flags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Targeting
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    enabled_for_orgs_json: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # ["org_id_1", ...]
    enabled_for_users_json: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # ["user_id_1", ...]
    percentage_rollout: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100

    # Configuration
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class APIUsage(Base):
    """API usage tracking for billing and rate limiting."""

    __tablename__ = "api_usage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # What was used
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # 'discovery', 'conformance', 'prediction', 'storage'
    operation: Mapped[str] = mapped_column(String(50), nullable=False)

    # Quantity
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Billing period
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (Index("ix_api_usage_org_period", "org_id", "period_start", "period_end"),)
