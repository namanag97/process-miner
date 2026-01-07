"""Shared/Generic schemas.

Contains schemas used by multiple layers:
- Pagination
- Error responses
"""

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Base paginated response."""

    total: int
    page: int
    page_size: int
    pages: int


class ErrorResponse(BaseModel):
    """API error response (RFC 7807 inspired)."""

    type: str = "error"
    title: str
    status: int
    detail: str
    instance: str | None = None
