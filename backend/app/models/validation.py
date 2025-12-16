from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class ValidationError(SQLModel):
    """A validation error for a specific field."""
    field: str
    message: str
    sample_bad_values: list[str] = Field(default_factory=list)


class ValidationWarning(SQLModel):
    """A validation warning (non-blocking)."""
    field: str
    message: str
    suggestion: Optional[str] = None


class ValidationStats(SQLModel):
    """Statistics from validation."""
    total_rows: int
    valid_rows: int
    case_count: int
    activity_count: int
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None


class ValidationResult(SQLModel):
    """Result of mapping validation."""
    is_valid: bool
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[ValidationWarning] = Field(default_factory=list)
    stats: Optional[ValidationStats] = None
